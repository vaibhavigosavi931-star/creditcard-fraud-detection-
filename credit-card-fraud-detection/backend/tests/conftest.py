from pathlib import Path
import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-with-at-least-32-characters")

from app import database
from app.main import app


@pytest.fixture
def isolated_database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    db_path = tmp_path / "test_fraud.db"
    monkeypatch.setattr(database, "DB_PATH", db_path)
    database.init_db()
    return db_path


@pytest.fixture
def client(isolated_database: Path) -> TestClient:
    with TestClient(app) as test_client:
        response = test_client.post(
            "/api/auth/register",
            json={
                "username": "test-analyst",
                "email": "analyst@example.com",
                "password": "analyst-password",
            },
        )
        assert response.status_code == 201
        token = test_client.post(
            "/api/auth/login",
            json={"login": "analyst@example.com", "password": "analyst-password"},
        ).json()["access_token"]
        test_client.headers.update({"Authorization": f"Bearer {token}"})
        yield test_client


@pytest.fixture
def unauthenticated_client(isolated_database: Path) -> TestClient:
    with TestClient(app) as test_client:
        yield test_client