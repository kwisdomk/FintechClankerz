import pytest

from app.config import settings
from app.database import initialize


@pytest.fixture(autouse=True)
def isolated_database(tmp_path, monkeypatch):
    """Tests must never mutate the running demo's aura.db."""
    monkeypatch.setattr(settings, "database_url", f"sqlite:///{tmp_path / 'test.db'}")
    initialize()
