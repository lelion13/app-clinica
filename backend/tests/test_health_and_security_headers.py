from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_returns_ok():
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_security_headers_present():
    client = TestClient(app)
    response = client.get("/health")

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert "strict-origin-when-cross-origin" in response.headers["referrer-policy"]
