import json
from pathlib import Path

from fastapi.testclient import TestClient

from app import ai
from app.main import app


def test_openapi_contract_has_named_responses_and_stable_operations():
    schema = app.openapi()
    assert schema["info"]["license"]["name"] == "MIT"
    operations = []
    for item in schema["paths"].values():
        for operation in item.values():
            operations.append(operation["operationId"])
            assert "schema" in operation["responses"]["200"]["content"]["application/json"]
    assert len(operations) == len(set(operations)) == 7
    exported = json.loads((Path(__file__).resolve().parents[1] / "docs/openapi.json").read_text())
    assert exported == schema, "Run python scripts/export_openapi.py after changing the API"


def test_import_findings_explanation_and_human_review(monkeypatch):
    async def explain(finding, transaction):
        return "test-model", {
            "finding": "Possible duplicate",
            "observed_evidence": json.loads(finding["evidence_json"]),
            "possible_explanations": ["Could be a duplicate"],
            "recommended_actions": ["Compare invoice originals"],
            "learning": {"concept": "Duplicate review", "explanation": "Check references."},
        }

    monkeypatch.setattr(ai, "explain", explain)
    csv = "date,description,amount,supplier,reference\n2026-01-01,Invoice A,10,Demo Vendor,REF-A\n2026-01-01,Invoice B,10,Demo Vendor,REF-A\n2026-01-02,Bad amount,invalid,Demo Vendor,REF-B\n"
    with TestClient(app) as client:
        upload = client.post("/api/upload", files={"file": ("demo.csv", csv, "text/csv")})
        assert upload.status_code == 200
        assert upload.json()["successful"] == 2
        assert upload.json()["rejected"] == 1
        assert upload.json()["findings_detected"] == 1
        assert client.get("/api/transactions?limit=1").json()["total"] == 2
        assert client.get("/api/summary").json()["finding_count"] == 1
        finding = client.get("/api/findings").json()[0]
        result = client.post(f"/api/findings/{finding['id']}/explain")
        assert result.status_code == 200
        assert result.json()["observed_evidence"] == finding["evidence"]
        review = client.post(f"/api/findings/{finding['id']}/review", json={
            "decision": "needs_review", "reviewer": "Integration test", "notes": "Verify invoices",
        })
        assert review.status_code == 200
        assert client.get("/api/findings").json()[0]["status"] == "needs_review"
        assert client.post("/api/findings/999/review", json={"decision": "confirmed"}).status_code == 404
