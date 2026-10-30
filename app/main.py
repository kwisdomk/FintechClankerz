import csv
import io
import json
from datetime import datetime, timezone

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app import ai
from app.config import settings
from app.database import connection, initialize
from app.schemas import ReviewRequest

app = FastAPI(title=settings.app_name, version="0.2.0", description="AURA financial audit API")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["GET", "POST"], allow_headers=["*"])


@app.on_event("startup")
def startup() -> None:
    initialize()


@app.get("/api/health", tags=["system"])
def health() -> dict:
    return {"status": "ok", "service": "aura-backend", "database": "configured"}


@app.post("/api/upload", tags=["transactions"])
async def upload(file: UploadFile = File(...)) -> dict:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(415, "Upload a .csv file")
    content = await file.read(10 * 1024 * 1024 + 1)
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(413, "CSV exceeds the 10 MB limit")
    try:
        text = content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        required = {"date", "description", "amount"}
        headers = {h.strip().lower() for h in (reader.fieldnames or []) if h}
        if not required.issubset(headers):
            raise HTTPException(422, "CSV requires date, description, amount columns")
        # Normalize header names for case-insensitive CSVs.
        rows = [{(k or "").strip().lower(): (v or "").strip() for k, v in row.items()} for row in reader]
    except UnicodeDecodeError as exc:
        raise HTTPException(422, "CSV must be UTF-8 encoded") from exc
    if not rows:
        raise HTTPException(422, "CSV contains no transaction rows")
    accepted, errors = [], []
    for number, row in enumerate(rows, 2):
        try:
            amount = float(row["amount"])
            if not row["date"] or not row["description"]:
                raise ValueError("date and description are required")
            accepted.append((row["date"], row["description"], amount, row.get("currency") or "USD", row.get("supplier"), row.get("reference"), number))
        except (ValueError, KeyError) as exc:
            errors.append(f"Row {number}: {exc}")
    if not accepted:
        raise HTTPException(422, detail={"message": "No valid transaction rows", "errors": errors})
    with connection() as db:
        db.executemany("INSERT INTO transactions(date,description,amount,currency,supplier,reference,source_row) VALUES(?,?,?,?,?,?,?)", accepted)
    return {"success": True, "message": "Transactions imported", "total_records": len(rows), "successful": len(accepted), "rejected": len(rows)-len(accepted), "findings_detected": 0, "errors": errors[:50]}


@app.get("/api/summary", tags=["transactions"])
def summary() -> dict:
    with connection() as db:
        tx = db.execute("SELECT COUNT(*) count, COALESCE(SUM(amount),0) total FROM transactions").fetchone()
        findings = db.execute("SELECT COUNT(*) FROM findings").fetchone()[0]
    return {"transaction_count": tx["count"], "total_amount": tx["total"], "finding_count": findings}


@app.get("/api/findings", tags=["findings"])
def list_findings() -> list[dict]:
    with connection() as db:
        rows = db.execute("SELECT * FROM findings ORDER BY id DESC").fetchall()
    return [{**dict(r), "evidence": json.loads(r["evidence_json"])} for r in rows]


@app.post("/api/findings/{finding_id}/explain", tags=["AI"])
async def explain_finding(finding_id: int) -> dict:
    with connection() as db:
        row = db.execute("SELECT * FROM findings WHERE id=?", (finding_id,)).fetchone()
        if not row:
            raise HTTPException(404, "Finding not found")
        finding = dict(row)
        transaction = dict(db.execute("SELECT * FROM transactions WHERE id=?", (row["transaction_id"],)).fetchone())
    try:
        model, payload = await ai.explain(finding, transaction)
    except ai.AIUnavailable as exc:
        raise HTTPException(503, str(exc)) from exc
    generated = datetime.now(timezone.utc).isoformat()
    result = {"finding_id": finding_id, "model_used": model, **payload, "generated_at": generated}
    with connection() as db:
        db.execute("INSERT INTO explanations(finding_id,model,result_json) VALUES(?,?,?)", (finding_id, model, json.dumps(result)))
    return result


@app.post("/api/findings/{finding_id}/review", tags=["findings"])
def review_finding(finding_id: int, request: ReviewRequest) -> dict:
    with connection() as db:
        if not db.execute("SELECT 1 FROM findings WHERE id=?", (finding_id,)).fetchone():
            raise HTTPException(404, "Finding not found")
        cursor = db.execute("INSERT INTO reviews(finding_id,decision,notes,reviewer) VALUES(?,?,?,?)", (finding_id, request.decision, request.notes, request.reviewer))
        db.execute("UPDATE findings SET status=? WHERE id=?", (request.decision, finding_id))
        record = db.execute("SELECT * FROM reviews WHERE id=?", (cursor.lastrowid,)).fetchone()
    return dict(record)
