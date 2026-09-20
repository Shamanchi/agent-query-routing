"""API-тесты без сети: TestClient."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture()
def client() -> TestClient:
    return TestClient(create_app())


def test_health(client: TestClient) -> None:
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_departments(client: TestClient) -> None:
    resp = client.get("/api/v1/departments")
    assert resp.status_code == 200
    assert set(resp.json()["departments"]) == {"billing", "technical", "sales"}


def test_route(client: TestClient) -> None:
    resp = client.post("/api/v1/route", json={"text": "My invoice has a wrong charge"})
    assert resp.status_code == 200
    assert resp.json()["department"] == "billing"


def test_route_rejects_empty(client: TestClient) -> None:
    resp = client.post("/api/v1/route", json={"text": "   "})
    assert resp.status_code == 422


@pytest.mark.integration()
def test_route_general_shape(client: TestClient) -> None:
    """Интеграционный по маркеру: fallback-форма, без сети."""
    resp = client.post("/api/v1/route", json={"text": "xyzzy blorp"})
    assert resp.status_code == 200
    assert resp.json()["department"] == "general"
