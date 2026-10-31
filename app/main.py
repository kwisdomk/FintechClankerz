import csv
import io
import json
from datetime import datetime, timezone

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app import ai
from app.config import settings
from app.database import connection, initialize
from app.schemas import Explanation, Finding, Health, Review, ReviewRequest, Summary, TransactionPage, UploadResult

app = FastAPI(
    title="FINTECH AI API", version="0.4.0",
    description="CSV import, deterministic duplicate screening, optional local/cloud Gemma explanations and human review. See docs/INTEGRATION.md in the source repository. MVP: not a fraud determination service.",
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup() -> None:
    initialize()

@app.get("/api/health", tags=["system"], response_model=Health, operation_id="getHealth")
def health() -> dict:
    return {"status": "ok", "service": "fintech-ai-backend", "database": "configured"}


def canonical_row(row: dict[str, str]) -> dict[str, str]:
    # Accept the Data Engineer's pipeline CSV (Title Case headers) and simple CSVs.
    normalized = {" ".join((k or "").strip().lower().replace("_", " ").split()): (v or "").strip() for k, v in row.items()}
    aliases = {
        "date": ("date", "transaction date"), "description": ("description", "transaction description"),
        "amount": ("amount", "transaction amount"), "supplier": ("supplier", "vendor"),
        "reference": ("reference", "payment reference", "transaction id"),
        "currency": ("currency",), "category": ("category", "detected category"),
    }
    return {key: next((normalized[a] for a in names if normalized.get(a)), "") for key, names in aliases.items()}

@app.post("/api/upload", tags=["transactions"], response_model=UploadResult, operation_id="uploadTransactions",
          responses={413: {"description": "CSV exceeds 10 MB"}, 415: {"description": "Not a CSV filename"}, 422: {"description": "Invalid encoding, columns, or no accepted rows"}})
async def upload(file: UploadFile = File(...)) -> dict:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(415, "Upload a .csv file")
    content = await file.read(10 * 1024 * 1024 + 1)
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(413, "CSV exceeds the 10 MB limit")
    try:
        reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))
        rows = [canonical_row(r) for r in reader]
        headers = {" ".join((h or "").strip().lower().replace("_", " ").split()) for h in (reader.fieldnames or [])}
    except UnicodeDecodeError as exc:
        raise HTTPException(422, "CSV must be UTF-8 encoded") from exc
    if not {"date", "description", "amount"}.issubset({"date" if h == "transaction date" else "amount" if h == "transaction amount" else h for h in headers}):
        raise HTTPException(422, "CSV requires date, description, amount (or Transaction date, Description, Amount) columns")
    if not rows:
        raise HTTPException(422, "CSV contains no transaction rows")
    accepted, errors = [], []
    for number, row in enumerate(rows, 2):
        try:
            amount_text = row["amount"].replace(",", "").replace("KES", "").replace("USD", "").strip()
            amount = float(amount_text)
            if amount <= 0 or not row["date"] or not row["description"]:
                raise ValueError("date, description, and a positive amount are required")
            currency = "KES" if "KES" in row["amount"].upper() or "transaction date" in headers else "USD"
            accepted.append((row["date"], row["description"], amount, currency, row["supplier"] or None, row["reference"] or None, number))
        except (ValueError, KeyError) as exc:
            errors.append(f"Row {number}: {exc}")
    if not accepted:
        raise HTTPException(422, detail={"message": "No valid transaction rows", "errors": errors[:50]})
    with connection() as db:
        db.executemany("INSERT INTO transactions(date,description,amount,currency,supplier,reference,source_row) VALUES(?,?,?,?,?,?,?)", accepted)
        # Transparent deterministic duplicate rules; no LLM is involved in detection.
        txs = db.execute("SELECT * FROM transactions ORDER BY id").fetchall()
        groups = {}
        for tx in txs:
            supplier = (tx["supplier"] or "").strip().casefold()
            if tx["reference"]:
                groups.setdefault(("reference", tx["reference"].strip().casefold()), []).append(tx)
            if supplier:
                groups.setdefault(("supplier_amount_date", supplier, round(tx["amount"], 2), tx["date"]), []).append(tx)
        created = 0
        for key, group in groups.items():
            if len(group) < 2:
                continue
            finding_type = "possible_duplicate_payment"
            for tx in group[1:]:
                if db.execute("SELECT 1 FROM findings WHERE transaction_id=? AND finding_type=?", (tx["id"], finding_type)).fetchone():
                    continue
                evidence = [f"Matching transaction references: {', '.join(str(x['id']) for x in group)}", f"Supplier: {tx['supplier'] or 'not supplied'}", f"Amount: {tx['currency']} {tx['amount']:.2f}", f"Date: {tx['date']}"]
                db.execute("INSERT INTO findings(transaction_id,finding_type,severity,evidence_json) VALUES(?,?,?,?)", (tx["id"], finding_type, "medium", json.dumps(evidence)))
                created += 1
    return {"success": True, "message": "Transactions imported and rule checks completed", "total_records": len(rows), "successful": len(accepted), "rejected": len(rows)-len(accepted), "findings_detected": created, "errors": errors[:50]}

@app.get("/api/transactions", tags=["transactions"], response_model=TransactionPage, operation_id="listTransactions")
def list_transactions(limit: int = 100, offset: int = 0) -> dict:
    limit = max(1, min(limit, 500)); offset = max(offset, 0)
    with connection() as db:
        total = db.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
        rows = db.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT ? OFFSET ?", (limit, offset)).fetchall()
    return {"items": [dict(r) for r in rows], "total": total, "limit": limit, "offset": offset}

@app.get("/api/summary", tags=["transactions"], response_model=Summary, operation_id="getSummary")
def summary() -> dict:
    with connection() as db:
        tx = db.execute("SELECT COUNT(*) count, COALESCE(SUM(amount),0) total FROM transactions").fetchone()
        findings = db.execute("SELECT COUNT(*) FROM findings").fetchone()[0]
        open_findings = db.execute("SELECT COUNT(*) FROM findings WHERE status='open'").fetchone()[0]
    return {"transaction_count": tx["count"], "total_amount": tx["total"], "finding_count": findings, "open_finding_count": open_findings}

@app.get("/api/findings", tags=["findings"], response_model=list[Finding], operation_id="listFindings")
def list_findings() -> list[dict]:
    with connection() as db:
        rows = db.execute("SELECT f.*, t.date, t.description, t.amount, t.currency, t.supplier, t.reference FROM findings f JOIN transactions t ON t.id=f.transaction_id ORDER BY f.id DESC").fetchall()
    return [{**dict(r), "evidence": json.loads(r["evidence_json"])} for r in rows]

@app.post("/api/findings/{finding_id}/explain", tags=["AI"], response_model=Explanation, operation_id="explainFinding",
          responses={404: {"description": "Finding not found"}, 503: {"description": "Inference unavailable or invalid model output"}})
async def explain_finding(finding_id: int) -> dict:
    with connection() as db:
        row = db.execute("SELECT * FROM findings WHERE id=?", (finding_id,)).fetchone()
        if not row: raise HTTPException(404, "Finding not found")
        finding = dict(row)
        transaction = dict(db.execute("SELECT * FROM transactions WHERE id=?", (row["transaction_id"],)).fetchone())
    try:
        model, payload = await ai.explain(finding, transaction)
    except ai.AIUnavailable as exc:
        raise HTTPException(503, str(exc)) from exc
    result = {"finding_id": finding_id, "model_used": model, **payload, "generated_at": datetime.now(timezone.utc).isoformat()}
    with connection() as db:
        db.execute("INSERT INTO explanations(finding_id,model,result_json) VALUES(?,?,?)", (finding_id, model, json.dumps(result)))
    return result

@app.post("/api/findings/{finding_id}/review", tags=["findings"], response_model=Review, operation_id="reviewFinding",
          responses={404: {"description": "Finding not found"}})
def review_finding(finding_id: int, request: ReviewRequest) -> dict:
    with connection() as db:
        if not db.execute("SELECT 1 FROM findings WHERE id=?", (finding_id,)).fetchone(): raise HTTPException(404, "Finding not found")
        cursor = db.execute("INSERT INTO reviews(finding_id,decision,notes,reviewer) VALUES(?,?,?,?)", (finding_id, request.decision, request.notes, request.reviewer))
        db.execute("UPDATE findings SET status=? WHERE id=?", (request.decision, finding_id))
        record = db.execute("SELECT * FROM reviews WHERE id=?", (cursor.lastrowid,)).fetchone()
    return dict(record)
