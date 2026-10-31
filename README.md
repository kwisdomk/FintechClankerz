# FINTECH AI Backend — Member 3: API & AI Integration

FastAPI service connecting the auditor-facing API, SQLite persistence, the data engine, and Gemma inference. It is designed to expose **observed evidence** separately from AI-generated interpretation. Models do not query databases or perform financial actions.

## Open-source license and integration

Application code is released under the [MIT License](LICENSE). Third-party dependencies, model weights and hosted services retain their own licenses/terms; the MIT license does not relicense Gemma or Google AI Studio.

- **Integrator guide:** [docs/INTEGRATION.md](docs/INTEGRATION.md) — Python, JavaScript and curl examples, errors, CORS, deployment and current limitations.
- **Machine-readable API contract:** [docs/openapi.json](docs/openapi.json); live `/openapi.json`, `/docs` and `/redoc` on FastAPI.
- **Python client:** `python -m pip install ./sdk/python` from a clone (not published to PyPI).
- **Contributions:** [CONTRIBUTING.md](CONTRIBUTING.md).

```python
from fintech_ai import FintechAIClient

with FintechAIClient("http://localhost:8000") as api:
    print(api.upload_csv("demo-data/01_mixed_office_transactions.csv"))
    print(api.findings())
```

The API is pre-1.0; it is not a production-hardened financial platform. Use synthetic records for public demos.

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
| POST | `/api/upload` | Import UTF-8 CSV (max 10 MB); supports simple headers and data-engine headers such as `Transaction date,Description,Amount,Supplier,Payment reference`. Reports invalid rows and creates deterministic possible-duplicate findings. |
| GET | `/api/transactions` | Paginated records (`limit`, `offset`) |
| GET | `/api/summary` | Transaction count, total amount, finding and open-finding counts |
| GET | `/api/findings` | Findings joined to their transaction details and observed evidence |
| POST | `/api/findings/{id}/explain` | Ask the configured local Ollama or Google AI Studio model for an explanation; persist response; 503 if unavailable |
| POST | `/api/findings/{id}/review` | Validate and persist `confirmed`, `dismissed`, or `needs_review` plus reviewer/notes and timestamp |

Upload example response:
```json
{"success":true,"message":"Transactions imported and rule checks completed","total_records":2,"successful":2,"rejected":0,"findings_detected":1,"errors":[]}
```
Review request: `{"decision":"confirmed","notes":"Invoice checked","reviewer":"auditor"}`.

## Try the API with demo data

With the server running, open `/docs` and try the upload, summary, and findings endpoints. Or seed a fictional finding for the AI/review flow:

```powershell
python scripts/seed_demo.py
```

Then call `GET /api/findings`; take its `id` and use it in `POST /api/findings/{id}/review` with `{"decision":"confirmed","notes":"Demo review","reviewer":"Tester"}`. `POST /api/findings/{id}/explain` calls the provider selected by `AI_PROVIDER`; if that provider is unavailable, the endpoint returns 503 while transaction and review APIs remain usable. To test CSV import, use `demo-transactions.csv` in `POST /api/upload`; one deliberately invalid row demonstrates row validation. The seed script is idempotent and does not clear existing data.

## Current boundary / integration needed

The SQLite schema stores transactions, findings, explanations, and review history. Upload accepts both the data-engine export headers and the simpler demo format. It currently runs deterministic duplicate checks (repeated payment reference; same supplier, amount, and date) without an LLM. The broader Isolation Forest/high-amount/category pipeline on `main` is not yet called by the API; integrating that callable pipeline is the next data-engine step.

## Inference providers: Ollama and Google AI Studio

Local inference remains the default (`AI_PROVIDER=local`). Configure `OLLAMA_BASE_URL` and `OLLAMA_MODEL` to use Ollama on the same machine or a trusted private network; never expose port 11434 publicly. Google AI Studio cloud inference is also implemented and was verified with `gemma-4-26b-a4b-it` using synthetic demo evidence. Configure `AI_PROVIDER=cloud`, `CLOUD_AI_API_KEY`, `CLOUD_AI_MODEL=gemma-4-26b-a4b-it`, and optionally `GOOGLE_GENAI_BASE_URL`. `AI_PROVIDER=local_then_cloud` tries local first and calls Google only if local inference fails. Keep the key in ignored `.env` only—never commit it.

Cloud mode sends the finding's transaction and evidence to Google. Use synthetic data unless your team approves the provider's data-handling terms for real financial records. The explanation endpoint validates the model response and replaces model-authored observed evidence with server-owned evidence before persistence. AI outages do not block transaction or review APIs. Because a public unauthenticated explain route can consume your quota, do not expose cloud mode through a public tunnel without access controls and rate limits.

## Team tunnel (temporary demo)

A temporary unauthenticated Cloudflare Quick Tunnel was explicitly enabled for the team's synthetic-data demo, exposing the frontend, API and local Ollama proxy. It is scheduled to stop after its one-hour demo window; do not treat its URL as a permanent integration endpoint. Anyone with the URL can mutate demo records and consume cloud/local inference. Before persistent access, add authentication and rate limits, expose only the HTTPS frontend/API, and keep inference networks and provider credentials private.

## Security and limitations

Credentials belong only in ignored `.env`; rotate keys that have been pasted into chat or committed. Validate/limit uploaded files; never treat model output as financial truth. SQLite is the hackathon/local database; deployment hardening, authentication/authorization, migrations, rate limits, and hosted-provider approval remain follow-up work. CSV date parsing and finding payload shape should be settled with the data-engine owner.
