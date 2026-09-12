from fastapi.testclient import TestClient

from app.main import app


def test_health_is_live() -> None:
    response = TestClient(app).get('/api/v1/health')
    assert response.status_code == 200
    body = response.json()
    assert body['status'] == 'ok'
    assert body['service'] == 'krishimitra-api'
    assert body['timestamp']


def test_readiness_without_database_is_ready() -> None:
    response = TestClient(app).get('/api/v1/readiness')
    assert response.status_code == 200
    assert response.json()['status'] == 'ready'
