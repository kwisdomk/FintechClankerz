from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "fintech-ai-backend"


def test_pipeline_csv_headers_are_accepted() -> None:
    with TestClient(app) as live_client:
        csv_content = (
            "Transaction ID,Transaction date,Description,Supplier,Amount,Category,Payment reference,Payment method\n"
            "TEST-API-A,2026-01-01,Test duplicate invoice,Test Supplier,123.45,Office Supplies,TEST-API-REF,Cash\n"
            "TEST-API-B,2026-01-01,Test duplicate invoice,Test Supplier,123.45,Office Supplies,TEST-API-REF,Cash\n"
        )
        response = live_client.post("/api/upload", files={"file": ("api-test.csv", csv_content, "text/csv")})
        assert response.status_code == 200, response.text
        result = response.json()
        assert result["successful"] == 2
        assert result["findings_detected"] >= 1
