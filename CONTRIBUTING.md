# Contributing

Contributions to FINTECH AI's application code are welcome under the MIT license. Only submit material you have the right to license. Model files, external datasets and provider credentials must not be committed.

1. Fork the repository and create a feature branch. The team's backend integration branch is `mbr-3`; `main` is the shared demo branch.
2. Install `requirements.txt`; copy `.env.example` to ignored `.env`. Use synthetic records and your own credentials.
3. Run `python -m pytest -q`. Tests use temporary databases, not the demo database. Inference in integration tests is mocked; no cloud calls are needed.
4. If an API changes, update response models, `docs/INTEGRATION.md`, SDK/tests, and run `python scripts/export_openapi.py`. Preserve existing routes and response fields where possible; explain breaking changes.
5. For frontend changes, run `npm ci` then `npm run build` in `frontend/`.
6. Submit a PR with the use case, test results, data-handling implications and any contract changes.

Keep observed evidence distinct from model interpretation. Never implement automatic fraud conclusions, payment actions or silent cloud transfer of real financial records. Do not commit `.env`, databases, financial records, API keys or downloaded model weights. Rotate leaked credentials immediately.

For a security issue, avoid posting credentials or private data in an issue. Contact the repository maintainers privately through an available GitHub contact; use a public issue only to request a private reporting channel if necessary.
