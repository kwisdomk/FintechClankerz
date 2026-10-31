import json
import sys
from pathlib import Path

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "sdk/python/src"))
from fintech_ai import FintechAIClient  # noqa: E402


def test_sdk_preserves_backend_prefix_and_upload_boundary(tmp_path):
    requests = []

    def handle(request):
        requests.append(request)
        if request.url.path.endswith("/review"):
            assert json.loads(request.content)["decision"] == "needs_review"
        return httpx.Response(200, json={"success": True})

    csv = tmp_path / "sample.csv"
    csv.write_text("date,description,amount\n2026-01-01,Example,10\n")
    with FintechAIClient("https://demo.example/backend", transport=httpx.MockTransport(handle)) as client:
        client.health()
        client.transactions(limit=25, offset=10)
        client.upload_csv(csv)
        client.review(7, "needs_review", reviewer="Tester")
    assert requests[0].url.path == "/backend/api/health"
    assert requests[1].url.params["offset"] == "10"
    assert requests[2].headers["content-type"].startswith("multipart/form-data; boundary=")
    assert b"sample.csv" in requests[2].content
    assert requests[3].url.path == "/backend/api/findings/7/review"


def test_sdk_exposes_provider_unavailable_without_retry():
    calls = []

    def handle(request):
        calls.append(request)
        return httpx.Response(503, json={"detail": "Inference unavailable"})

    with FintechAIClient(transport=httpx.MockTransport(handle)) as client:
        with pytest.raises(httpx.HTTPStatusError) as error:
            client.explain(1)
    assert error.value.response.status_code == 503
    assert len(calls) == 1
