from fastapi.testclient import TestClient
from passkey_server.src.main import app


def test_health_endpoint():
    with TestClient(app) as client:
        resp = client.get('/health')
        assert resp.status_code == 200
        assert resp.json() == {'status': 'ok'}
