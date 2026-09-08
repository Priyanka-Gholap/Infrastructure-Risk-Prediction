from fastapi.testclient import TestClient
from backend.app.main import app

def test_health_endpoint():
    """GET /health should return HTTP 200 and confirm models are loaded."""
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["models_loaded"] is True


def test_model_info_endpoint():
    """GET /model-info should return HTTP 200 and expose authoritative metadata."""
    with TestClient(app) as client:
        response = client.get("/model-info")
        assert response.status_code == 200
        data = response.json()
        assert data["feature_count"] == 36
        assert "safe_mvp_features" in data
        assert len(data["safe_mvp_features"]) == 36
        assert data["operating_thresholds"]["cost_overrun_threshold"] == 0.40
        assert data["operating_thresholds"]["delay_threshold"] == 0.50
        assert "cost_overrun" in data["models"]
        assert "delay" in data["models"]
        assert "delay_regression_secondary" in data["models"]
