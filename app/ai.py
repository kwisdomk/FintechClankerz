import json

import httpx

from app.config import settings


class AIUnavailable(Exception):
    pass


async def explain(finding: dict, transaction: dict) -> tuple[str, dict]:
    evidence = json.loads(finding["evidence_json"])
    prompt = f"""You assist a financial auditor. Use only supplied evidence; do not invent facts.
Return ONLY JSON with keys finding, observed_evidence, possible_explanations, recommended_actions, learning (object with concept and explanation).
Observed evidence must quote or faithfully summarize supplied evidence. Label uncertainty clearly.
Transaction: {json.dumps(transaction)}
Finding: {finding['finding_type']}; evidence: {json.dumps(evidence)}"""
    url = settings.ollama_base_url.rstrip("/") + "/api/generate"
    try:
        async with httpx.AsyncClient(timeout=settings.ai_timeout_seconds) as client:
            response = await client.post(url, json={"model": settings.ollama_model, "prompt": prompt, "stream": False, "format": "json"})
            response.raise_for_status()
            raw = response.json()["response"]
        payload = json.loads(raw)
        required = {"finding", "observed_evidence", "possible_explanations", "recommended_actions", "learning"}
        if not required.issubset(payload) or not isinstance(payload["observed_evidence"], list):
            raise ValueError("Unexpected model response structure")
        # Server-owned evidence is authoritative, never model-authored.
        payload["observed_evidence"] = evidence
        return settings.ollama_model, payload
    except (httpx.HTTPError, KeyError, ValueError, json.JSONDecodeError) as exc:
        raise AIUnavailable("Local AI inference is unavailable or returned invalid output") from exc
