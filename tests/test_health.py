from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import ai
from app.config import settings
from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Every test gets a disposable database; never touch the team's configured DB.
    monkeypatch.setattr(settings, "database_url", "sqlite:///" + str(tmp_path / "test.db"))
    with TestClient(app) as test_client:
        yield test_client


def upload(client, content):
    return client.post("/api/upload", files={"file": ("records.csv", content, "text/csv")})


def duplicate_finding(client):
    response = upload(client,
        "date,description,amount,currency,supplier,reference\n"
        "2026-10-30,Invoice A,100,KES,Example Supplier,REF-A\n"
        "2026-10-30,Invoice B,100,KES,Example Supplier,REF-A\n")
    assert response.status_code == 200
    assert response.json()["findings_detected"] == 1
    return client.get("/api/findings").json()[0]["id"]


def test_health(client):
    assert client.get("/api/health").json()["service"] == "finguard-ai-backend"


def test_pipeline_csv_headers_are_accepted(client):
    content = (
        "Transaction ID,Transaction date,Description,Supplier,Amount,Category,Payment reference,Payment method\n"
        "TEST-A,2026-01-01,Test invoice,Test Supplier,123.45,Office Supplies,TEST-REF,Cash\n"
        "TEST-B,2026-01-01,Test invoice,Test Supplier,123.45,Office Supplies,TEST-REF,Cash\n"
    )
    result = upload(client, content)
    assert result.status_code == 200
    assert result.json()["findings_detected"] == 1
    assert client.get("/api/transactions").json()["items"][0]["currency"] == "KES"


def test_explicit_currency_and_separate_totals(client):
    result = upload(client,
        "date,description,amount,currency,supplier,reference\n"
        "2026-10-30,Invoice A,100,KES,Example Supplier,SAME\n"
        "2026-10-30,Invoice B,100,USD,Example Supplier,SAME\n")
    assert result.status_code == 200
    assert result.json()["findings_detected"] == 0
    assert {item["currency"] for item in client.get("/api/transactions").json()["items"]} == {"KES", "USD"}
    totals = client.get("/api/summary").json()["totals_by_currency"]
    assert [(item["currency"], item["total_amount"]) for item in totals] == [("KES", 100), ("USD", 100)]


@pytest.mark.parametrize("amount", ["NaN", "inf", "-inf", "1e999", "0", "-10", "nonsense"])
def test_invalid_amounts_are_rejected_without_server_errors(client, amount):
    response = upload(client, f"date,description,amount\n2026-10-30,Invoice,{amount}\n")
    assert response.status_code == 422
    assert client.get("/api/summary").json()["transaction_count"] == 0


@pytest.mark.parametrize("value", ["not-a-date", "2026-02-30", "20261030", "2026-10-30T12:00:00"])
def test_invalid_dates_are_rejected(client, value):
    assert upload(client, f"date,description,amount\n{value},Invoice,10\n").status_code == 422


def test_partial_import_reports_bad_rows(client):
    response = upload(client,
        "date,description,amount\n"
        "2026-10-30,Valid,10\n"
        "not-a-date,Invalid,20\n"
        "2026-10-30,Invalid,NaN\n"
        "2026-10-30,Invalid,30,EXTRA\n")
    assert response.status_code == 200
    result = response.json()
    assert (result["successful"], result["rejected"], len(result["errors"])) == (1, 3, 3)
    assert "Row 3" in result["errors"][0]
    assert client.get("/api/summary").json()["transaction_count"] == 1


def test_currency_conflicts_are_rejected(client):
    response = upload(client, "date,description,amount,currency\n2026-10-30,Invoice,KES 10,USD\n")
    assert response.status_code == 422


def test_amount_currency_markers_are_case_insensitive(client):
    response = upload(client, "date,description,amount\n2026-10-30,Invoice,kes 10\n")
    assert response.status_code == 200
    assert client.get("/api/transactions").json()["items"][0]["currency"] == "KES"


@pytest.mark.parametrize("decision, expected_open", [("needs_review", 1), ("confirmed", 0), ("dismissed", 0)])
def test_review_status_and_queue_count(client, decision, expected_open):
    finding_id = duplicate_finding(client)
    response = client.post(f"/api/findings/{finding_id}/review",
                           json={"decision": decision, "reviewer": "Test reviewer", "notes": "Synthetic evidence"})
    assert response.status_code == 200
    assert response.json()["notes"] == "Synthetic evidence"
    assert client.get("/api/findings").json()[0]["status"] == decision
    assert client.get("/api/summary").json()["open_finding_count"] == expected_open


def test_ai_outage_keeps_review_available(client, monkeypatch):
    finding_id = duplicate_finding(client)
    async def unavailable(*args):
        raise ai.AIUnavailable("Test outage")
    monkeypatch.setattr(ai, "explain", unavailable)
    assert client.post(f"/api/findings/{finding_id}/explain").status_code == 503
    assert client.post(f"/api/findings/{finding_id}/review", json={"decision": "needs_review"}).status_code == 200


def test_transaction_search_covers_all_pages(client):
    rows = ["date,description,amount,reference"]
    rows.extend(f"2026-10-30,Record {index},{index + 1},REF-{index}" for index in range(120))
    assert upload(client, "\n".join(rows)).status_code == 200
    first = client.get("/api/transactions?limit=50").json()
    last = client.get("/api/transactions?limit=50&offset=100").json()
    assert (first["total"], len(first["items"]), len(last["items"])) == (120, 50, 20)
    result = client.get("/api/transactions", params={"q": "REF-0"}).json()
    assert result["total"] == 1
    assert result["items"][0]["reference"] == "REF-0"


def test_synthetic_sample_keeps_three_duplicate_findings(client):
    sample = Path(__file__).resolve().parents[1] / "synthetic_financial_transactions.csv"
    result = upload(client, sample.read_bytes()).json()
    assert (result["successful"], result["rejected"], result["findings_detected"]) == (100, 0, 3)
