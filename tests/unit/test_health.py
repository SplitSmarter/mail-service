import pytest

pytestmark = pytest.mark.unit


def test_root_health(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "Mail Service is running"


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
