# FINTECH AI Backend — Member 3: API & AI Integration

FastAPI service connecting the auditor-facing API, SQLite persistence, the data engine, and Gemma inference. It is designed to expose **observed evidence** separately from AI-generated interpretation. Models do not query databases or perform financial actions.

## Run

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

- Swagger: http://localhost:8000/docs
- Health: `GET /api/health`
- Tests: `pytest`

## Implemented API

| Method | Path | Behavior |
|---|---|---|
| GET | `/api/health` | Service health |
| POST | `/api/upload` | Import UTF-8 CSV (max 10 MB); required headers `date,description,amount`; optional `currency,supplier,reference`. Invalid rows reported, valid rows stored. |
| GET | `/api/summary` | Transaction count, amount total, finding count |
| GET | `/api/findings` | Persisted findings (empty until data-engine integration creates them) |
| POST | `/api/findings/{id}/explain` | Ask configured Ollama model for an explanation; persist response; 503 if unavailable |
| POST | `/api/findings/{id}/review` | Validate and persist `confirmed`, `dismissed`, or `needs_review` plus reviewer/notes and timestamp |

Upload example response:
```json
{"success":true,"message":"Transactions imported","total_records":1,"successful":1,"rejected":0,"findings_detected":0,"errors":[]}
```
Review request: `{"decision":"confirmed","notes":"Invoice checked","reviewer":"auditor"}`.

## Try the API with demo data

With the server running, open `/docs` and try the upload, summary, and findings endpoints. Or seed a fictional finding for the AI/review flow:

```powershell
python scripts/seed_demo.py
```

Then call `GET /api/findings`; take its `id` and use it in `POST /api/findings/{id}/review` with `{"decision":"confirmed","notes":"Demo review","reviewer":"Tester"}`. Try `POST /api/findings/{id}/explain` to exercise Ollama; if Ollama is not configured/reachable this correctly returns 503 while other endpoints stay usable. To test CSV import, use `demo-transactions.csv` in `POST /api/upload`; one deliberately invalid row demonstrates row validation. The seed script is idempotent and does not clear existing data.

## Current boundary / integration needed

The SQLite schema stores transactions, findings, explanations, and review history. CSV parsing is deliberately limited to ingestion and does **not** implement anomaly detection: findings currently remain empty. The data engine owner must agree on transaction and finding payloads and provide a callable detection interface; findings should be created only from its output, with evidence and transaction references preserved. API response contracts should then be confirmed with both frontend developers before they bind to them.

## Gemma / Ollama

Configure `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, and `AI_TIMEOUT_SECONDS` in `.env`. Start Ollama on the trusted inference machine, pull the agreed Gemma model, and verify its `/api/generate` endpoint before setting the URL. For a separate host, use a trusted private LAN/VPN and firewall-restrict access; do not expose Ollama publicly. The explanation endpoint sends the transaction and engine-provided evidence to that service, expects JSON, validates its shape, then replaces model-authored observed evidence with the server's authoritative evidence before persistence. AI failure does not prevent the finding/review APIs from working. Hosted inference is not enabled; do not send sensitive records to a hosted provider until the team explicitly approves data handling and credentials.

## Security and limitations

Credentials belong only in ignored `.env`; validate/limit uploaded files; never treat model output as financial truth. SQLite is the hackathon/local database; deployment hardening, authentication/authorization, migrations, rate limits, and hosted-provider policy remain follow-up work. CSV date parsing and finding payload shape should be settled with the data-engine owner.
