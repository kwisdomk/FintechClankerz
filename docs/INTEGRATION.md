# Integrate FINTECH AI

FINTECH AI's original application code is available under the [MIT license](../LICENSE). It is an audit investigation MVP, not a fraud determination service or production-hardened financial platform. Model weights, third-party dependencies and Google AI Studio usage remain subject to their own licenses and terms. An API credential grants no rights to redistribute a provider's model.

## 1. Start your own backend

From a clone of https://github.com/kwisdomk/FintechClankerz:

```sh
python -m venv .venv
# Activate .venv using your shell, then:
python -m pip install -r requirements.txt
# Copy .env.example to .env; configure your own credentials if using cloud inference.
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Inference defaults to `AI_PROVIDER=local`. CSV import, findings and reviews work without Ollama or cloud credentials. SQLite is created at startup. Do not commit `.env` or databases. Keep the service loopback-only until you have secured a public deployment.

## 2. Base URL and OpenAPI

| Deployment | Base URL supplied to clients |
|---|---|
| Local FastAPI | `http://localhost:8000` |
| Frontend same-origin proxy | `https://YOUR-APP-HOST` |
| Frontend explicit backend proxy | `https://YOUR-APP-HOST/backend` |

Every audit route below starts with `/api`. Do **not** put `/api` in the SDK base URL. Do not hard-code a temporary Quick Tunnel address in an integration.

- Local interactive docs: `http://localhost:8000/docs`
- Local alternative docs: `http://localhost:8000/redoc`
- Local live contract: `http://localhost:8000/openapi.json`
- Proxied live contract: `https://YOUR-APP-HOST/backend/openapi.json`
- Checked-in contract: [openapi.json](openapi.json)
- Regenerate after API changes: `python scripts/export_openapi.py`

The OpenAPI 3.1 contract has named request/response models and explicit operation IDs for generating Python, TypeScript or other clients. Configure the generated client's server/base URL for your deployment. Run tests and regenerate the contract whenever changing a response.

## 3. Python client

The SDK is included in this repository; it has **not** been published to PyPI.

```sh
python -m pip install ./sdk/python
```

```python
from fintech_ai import FintechAIClient

with FintechAIClient("http://localhost:8000", timeout=180) as api:
    print(api.health())
    report = api.upload_csv("demo-data/01_mixed_office_transactions.csv")
    print(report)
    print(api.summary())
    page = api.transactions(limit=25, offset=0)
    print(page["items"])

    # List contains all findings in newest-first order, not only this upload's.
    # Let a human select an actual finding; never auto-confirm it.
    candidates = api.findings()
    for finding in candidates:
        print(finding["id"], finding["description"], finding["evidence"])
```

Once a human has chosen a real finding ID:

```python
import httpx
from fintech_ai import FintechAIClient

with FintechAIClient("http://localhost:8000") as api:
    finding_id = 1  # Replace with an ID returned by findings().
    try:
        print(api.explain(finding_id))
    except httpx.HTTPStatusError as error:
        if error.response.status_code != 503:
            raise
        print("AI unavailable; evidence and review remain usable")
    print(api.review(finding_id, "needs_review",
                     notes="Compare invoices and payment records.",
                     reviewer="Integration demo"))
```

Errors raise `httpx.HTTPStatusError`; connection/timeouts raise `httpx.RequestError`. The SDK intentionally does not retry uploads or reviews. Use a context manager or call `close()`.

## 4. JavaScript / browser integration

For a browser served by the Next.js app, use same-origin paths:

```javascript
async function request(path, options = {}) {
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) throw new Error(JSON.stringify(data.detail ?? data));
  return data;
}

const form = new FormData();
form.append("file", fileInput.files[0]); // fileInput is your HTML <input type="file">.
const result = await request("/api/upload", { method: "POST", body: form });
// Do not set Content-Type: the browser must supply the multipart boundary.
const findings = await request("/api/findings");
console.log(result, findings);
```

A separately hosted browser app should call `https://YOUR-API-HOST/api/...` and configure `FRONTEND_ORIGINS` on the backend as a comma-separated list of exact origins, e.g. `https://audit.example.com,http://localhost:3000`. CORS is a browser policy, **not authentication**. Never put Google API credentials in browser code.

## 5. curl examples

```sh
curl http://localhost:8000/api/health
curl -F "file=@demo-data/01_mixed_office_transactions.csv" http://localhost:8000/api/upload
curl "http://localhost:8000/api/transactions?limit=25&offset=0"
curl http://localhost:8000/api/findings
# Replace 1 with a real finding ID:
curl -X POST http://localhost:8000/api/findings/1/explain
curl -X POST http://localhost:8000/api/findings/1/review \
  -H "Content-Type: application/json" \
  -d '{"decision":"needs_review","notes":"Verify invoices","reviewer":"Auditor"}'
```

## 6. Contract and CSV format

| Method | Route | Result |
|---|---|---|
| GET | `/api/health` | Service health (not an inference readiness check) |
| POST | `/api/upload` | Multipart `file`; counts, rejection messages and new-finding count |
| GET | `/api/transactions` | `{items,total,limit,offset}`; limit clamped to 1–500 |
| GET | `/api/summary` | Transaction/finding counts and sum of stored amounts |
| GET | `/api/findings` | Array of findings joined to transaction context |
| POST | `/api/findings/{id}/explain` | Validated interpretation, authoritative evidence, model and time |
| POST | `/api/findings/{id}/review` | Stored review and updated finding status |

UTF-8 CSV, maximum 10 MB, required columns: `date,description,amount`. Optional: `currency,supplier,reference`. Title-case data-engine headers such as `Transaction date,Description,Amount,Supplier,Payment reference` are also accepted. Use ISO dates and positive finite numeric amounts. Prefer the supplied USD demo files for this MVP.

Current limitations to account for:

- Imports append records; no idempotency key, rollback endpoint or automatic deduplication of imports. Re-uploading creates additional records and potentially findings. Do not retry a timed-out import blindly.
- Date strings are not strictly parsed. The current currency implementation infers KES from KES amount text / pipeline headers and otherwise USD, rather than consistently honoring `currency`. It does not convert FX; summary amounts are not a consolidated financial valuation.
- Duplicate matching is simplistic: reference, or supplier+amount+date. The current match keys do not partition by currency. Do not rely on it for multi-currency reconciliation.
- Findings are an unpaginated list; transactions are paginated.
- The separate Isolation Forest pipeline is not called by upload. Large amounts alone do not cause an API finding.
- No webhooks, background jobs, enterprise authorization, tenant isolation or immutable audit logging are implemented.
- This is a pre-1.0 contract. `/api` is the current path; no `/api/v1` route is advertised. Review changes before updating clients.

### Error handling

- `404`: unknown finding.
- `413`: upload over 10 MB.
- `415`: filename does not end in `.csv`.
- `422`: invalid request or unusable CSV. A partially valid CSV normally returns `200` with `rejected` and `errors`; inspect these even after HTTP success.
- `503`: inference unavailable or invalid model output; do not block review on this.

Errors use FastAPI's `detail` field, whose value can be a string, an object, or a validation-error array. Timeout or lost-response conditions do not prove a mutation failed.

## 7. Inference integration

- `AI_PROVIDER=local`: Ollama configured through `OLLAMA_BASE_URL` and `OLLAMA_MODEL`.
- `AI_PROVIDER=cloud`: Google AI Studio, using your own `CLOUD_AI_API_KEY` and `CLOUD_AI_MODEL` (default `gemma-4-26b-a4b-it`).
- `AI_PROVIDER=local_then_cloud`: try local, then send evidence to Google if local inference fails. Enabling this also approves that data transfer; assess provider terms before using real records.

`POST /api/findings/{id}/explain` is the recommended provider-independent integration. It persists explanations and restores authoritative server evidence. It does not grant the model database or payment-execution tools.

The demo also exposes Ollama-compatible `GET /ollama/api/tags` and `POST /ollama/api/generate` via Next.js. Those are direct model-proxy routes, **not** audit API endpoints: they bypass explanation persistence and evidence validation. Provider support for each parameter depends on the installed model. Do not expose raw Ollama or these unrestricted proxies in production.

## 8. Public deployment checklist

Before real users/data: HTTPS, authentication/authorization, rate/concurrency limits, request budgets, private inference networking, backups, secret rotation, tenant isolation, retention policy and approved cloud data processing. The current unauthenticated demo permits data modification and consumes inference resources; it is not a production configuration. Set browser origins explicitly and put access controls at your API gateway; neither CORS nor an obscure tunnel URL protects data.
