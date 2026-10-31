import json

import httpx

from app.config import settings


class AIUnavailable(Exception):
    pass


def _prompt(finding: dict, transaction: dict, evidence: list) -> str:
    return f"""You assist a financial auditor. Return one concise JSON object only, without analysis or markdown. Use only supplied evidence; do not invent facts.
Keys: finding (string), observed_evidence (array copied from supplied evidence), possible_explanations (array of 2 short strings), recommended_actions (array of 2 short strings), learning (object with concept and explanation).
Transaction: {json.dumps(transaction)}
Finding: {finding['finding_type']}
Evidence: {json.dumps(evidence)}"""


def _validate(raw: str, evidence: list) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        if raw.lower().startswith("json"):
            raw = raw[4:].strip()
    payload = json.loads(raw)
    required = {"finding", "observed_evidence", "possible_explanations", "recommended_actions", "learning"}
    if not required.issubset(payload):
        raise ValueError("Unexpected model response structure")
    if isinstance(payload["observed_evidence"], str):
        payload["observed_evidence"] = [payload["observed_evidence"]]
    if not isinstance(payload["observed_evidence"], list):
        raise ValueError("observed_evidence must be a list")
    if not isinstance(payload["possible_explanations"], list) or not isinstance(payload["recommended_actions"], list):
        raise ValueError("Explanation lists must be arrays")
    if not isinstance(payload["learning"], dict):
        raise ValueError("learning must be an object")
    # Do not persist model-created facts as observed evidence.
    payload["observed_evidence"] = evidence
    return payload


async def _local(prompt: str, evidence: list) -> tuple[str, dict]:
    url = settings.ollama_base_url.rstrip("/") + "/api/generate"
    async with httpx.AsyncClient(timeout=settings.ai_timeout_seconds) as client:
        response = await client.post(url, json={"model": settings.ollama_model, "prompt": prompt, "stream": False, "format": "json", "think": False, "options": {"num_predict": 900, "temperature": 0.2}})
        response.raise_for_status()
        raw = response.json()["response"]
    return settings.ollama_model, _validate(raw, evidence)


async def _cloud(prompt: str, evidence: list) -> tuple[str, dict]:
    if not settings.cloud_ai_api_key:
        raise AIUnavailable("Google AI Studio key is not configured")
    model = settings.cloud_ai_model
    url = f"{settings.google_genai_base_url.rstrip('/')}/models/{model}:generateContent"
    request = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.1, "maxOutputTokens": 2048},
    }
    try:
        async with httpx.AsyncClient(timeout=settings.ai_timeout_seconds) as client:
            response = await client.post(url, headers={"x-goog-api-key": settings.cloud_ai_api_key}, json=request)
            response.raise_for_status()
            parts = response.json()["candidates"][0]["content"]["parts"]
            raw = "".join(part.get("text", "") for part in parts if not part.get("thought", False))
        return f"{model} (Google AI Studio)", _validate(raw, evidence)
    except (httpx.HTTPError, KeyError, IndexError, ValueError, json.JSONDecodeError) as exc:
        # Never include provider response text or credentials in the API error.
        raise AIUnavailable("Google AI Studio inference failed or returned invalid output") from exc


async def explain(finding: dict, transaction: dict) -> tuple[str, dict]:
    evidence = json.loads(finding["evidence_json"])
    prompt = _prompt(finding, transaction, evidence)
    provider = settings.ai_provider.lower()
    if provider == "cloud":
        return await _cloud(prompt, evidence)
    if provider == "local_then_cloud":
        try:
            return await _local(prompt, evidence)
        except (httpx.HTTPError, KeyError, ValueError, json.JSONDecodeError):
            return await _cloud(prompt, evidence)
    if provider != "local":
        raise AIUnavailable("AI_PROVIDER must be local, cloud, or local_then_cloud")
    try:
        model, payload = await _local(prompt, evidence)
        return model, payload
    except (httpx.HTTPError, KeyError, ValueError, json.JSONDecodeError) as exc:
        raise AIUnavailable("Local AI inference is unavailable or returned invalid output") from exc
