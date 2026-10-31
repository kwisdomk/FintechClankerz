# FinGuard AI frontend

A small review workspace: import CSV records, inspect possible duplicate payments, request an optional AI explanation, and save a human review decision.

## Local setup

Start FastAPI from the repository root using the root README. In a second terminal:

```powershell
cd frontend
npm ci
Copy-Item .env.example .env.local
npm run dev
```

Before starting, replace the example TEAM_ACCESS_PASSWORD in .env.local with your own team secret. Open http://localhost:3000 and sign in with username team and that password.

Browser API calls use the authenticated same-origin /api proxy. FINGUARD_BACKEND_URL configures the server-side backend address (default http://127.0.0.1:8000). Keep FastAPI and Ollama on loopback when sharing the frontend through the team tunnel.

## Current scope

- Upload accepts the simple CSV format and the data-engine sample format.
- Duplicate checks run on import. The separate statistical/category pipeline is not called by the API.
- Amounts are shown per currency. Review decisions are confirmed, dismissed, and needs_review.
- Transactions have pagination and search across all stored records.
- Importing the same CSV again adds its records again.
- AI failure does not block a human review.

Run npm run lint and npm run build to check the frontend.
