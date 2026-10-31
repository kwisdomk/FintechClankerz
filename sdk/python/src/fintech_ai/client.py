from pathlib import Path
from typing import Any, Literal

import httpx


class FintechAIClient:
    """Synchronous audit API client; errors raise httpx.HTTPStatusError.

    base_url excludes /api, e.g. http://localhost:8000 or https://host/backend.
    No automatic retries: uploads and reviews are not idempotent.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        *,
        timeout: float = 180,
        headers: dict[str, str] | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._client = httpx.Client(
            base_url=base_url.rstrip("/") + "/",
            timeout=timeout,
            headers=headers,
            transport=transport,
        )

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        response = self._client.request(method, path, **kwargs)
        response.raise_for_status()
        return response.json()

    def health(self) -> dict[str, Any]:
        return self._request("GET", "api/health")

    def summary(self) -> dict[str, Any]:
        return self._request("GET", "api/summary")

    def transactions(self, *, limit: int = 100, offset: int = 0) -> dict[str, Any]:
        return self._request("GET", "api/transactions", params={"limit": limit, "offset": offset})

    def findings(self) -> list[dict[str, Any]]:
        return self._request("GET", "api/findings")

    def upload_csv(self, path: str | Path) -> dict[str, Any]:
        path = Path(path)
        with path.open("rb") as file:
            return self._request("POST", "api/upload", files={"file": (path.name, file, "text/csv")})

    def explain(self, finding_id: int) -> dict[str, Any]:
        return self._request("POST", f"api/findings/{finding_id}/explain")

    def review(
        self,
        finding_id: int,
        decision: Literal["confirmed", "dismissed", "needs_review"],
        *,
        notes: str | None = None,
        reviewer: str | None = None,
    ) -> dict[str, Any]:
        return self._request("POST", f"api/findings/{finding_id}/review", json={
            "decision": decision, "notes": notes, "reviewer": reviewer,
        })

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "FintechAIClient":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()
