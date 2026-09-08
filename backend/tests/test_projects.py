import pytest
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.project_service import DatasetUnavailableError, ProjectService


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


# ==============================================================================
# 1. PROJECT LOOKUP TESTS (GET /projects)
# ==============================================================================

def test_projects_lookup_default(client):
    """GET /projects returns 200 with default 50 items and only metadata fields."""
    response = client.get("/projects")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 50

    # Ensure each item contains ONLY lookup metadata fields, not the 36 model features
    first = data[0]
    assert "project_id" in first
    assert "project_name" in first
    assert "snapshot_month" in first
    assert "original_cost" not in first
    assert "physical_progress_pct" not in first
    assert "cumulative_expenditure" not in first


def test_projects_lookup_search_by_id(client):
    """Search by exact project ID returns that project."""
    response = client.get("/projects?search=400234")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    pids = [item["project_id"] for item in data]
    assert "400234" in pids
    matched = next(item for item in data if item["project_id"] == "400234")
    assert "Patratu" in matched["project_name"]


def test_projects_lookup_search_by_name(client):
    """Search by project title substring returns matching projects."""
    response = client.get("/projects?search=Patratu")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    for item in data:
        assert "patratu" in item["project_name"].lower() or "patratu" in item["project_id"].lower()


def test_projects_lookup_search_case_insensitive(client):
    """Search query is case-insensitive."""
    response_lower = client.get("/projects?search=railway")
    response_upper = client.get("/projects?search=RAILWAY")
    assert response_lower.status_code == 200
    assert response_upper.status_code == 200
    assert response_lower.json() == response_upper.json()


def test_projects_lookup_search_no_matches(client):
    """Search with non-matching query returns empty list with 200 OK."""
    response = client.get("/projects?search=nonexistent_project_xyz_999999")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_projects_lookup_limit(client):
    """Custom limit parameter is respected."""
    response = client.get("/projects?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5


def test_projects_lookup_offset_pagination(client):
    """Offset skips initial projects for pagination."""
    res_page1 = client.get("/projects?limit=5&offset=0")
    res_page2 = client.get("/projects?limit=5&offset=5")
    assert res_page1.status_code == 200
    assert res_page2.status_code == 200

    pids_page1 = [p["project_id"] for p in res_page1.json()]
    pids_page2 = [p["project_id"] for p in res_page2.json()]

    # Pages must be disjoint
    assert set(pids_page1).isdisjoint(set(pids_page2))


def test_projects_lookup_invalid_limit(client):
    """Limit < 1 or > 500 returns 422 Unprocessable Content."""
    res_zero = client.get("/projects?limit=0")
    assert res_zero.status_code == 422

    res_over = client.get("/projects?limit=501")
    assert res_over.status_code == 422


def test_projects_lookup_invalid_offset(client):
    """Negative offset returns 422 Unprocessable Content."""
    res_neg = client.get("/projects?offset=-5")
    assert res_neg.status_code == 422


# ==============================================================================
# 2. PROJECT PREDICTION TESTS (POST /projects/{project_id}/predict)
# ==============================================================================

def test_predict_valid_project_400234(client):
    """
    Project 400234 (Third Railway Line Patratu-Sonnagar):
    Verified Low Risk in Step 6B.
    """
    response = client.post("/projects/400234/predict")
    assert response.status_code == 200
    data = response.json()

    assert data["project_id"] == "400234"
    assert "Patratu" in data["project_name"]
    assert data["snapshot_month"] == "2025-12"
    assert data["overall_risk"] == "LOW"
    assert data["cost_overrun_risk"] == "LOW"
    assert data["schedule_delay_risk"] == "LOW"
    assert data["cost_overrun_probability"] == 0.2388
    assert data["schedule_delay_probability"] == 0.1615
    assert data["predicted_delay_months"] == -3.83


def test_predict_valid_project_400161(client):
    """
    Project 400161 (PP Project, Pata):
    Verified High Risk Budget Overrun in Step 6B.
    """
    response = client.post("/projects/400161/predict")
    assert response.status_code == 200
    data = response.json()

    assert data["project_id"] == "400161"
    assert "Pata" in data["project_name"]
    assert data["snapshot_month"] == "2026-01"
    assert data["overall_risk"] == "HIGH"
    assert data["cost_overrun_risk"] == "HIGH"
    assert data["schedule_delay_risk"] == "LOW"
    assert data["cost_overrun_probability"] == 0.7201
    assert data["schedule_delay_probability"] == 0.1608
    assert data["predicted_delay_months"] == 26.73


def test_predict_response_schema_exact_fields(client):
    """Response matches exact required schema without extraneous fields."""
    response = client.post("/projects/400234/predict")
    assert response.status_code == 200
    data = response.json()

    expected_keys = {
        "project_id",
        "project_name",
        "snapshot_month",
        "overall_risk",
        "cost_overrun_probability",
        "cost_overrun_risk",
        "schedule_delay_probability",
        "schedule_delay_risk",
        "predicted_delay_months",
    }
    assert set(data.keys()) == expected_keys


def test_predict_negative_delay_preserved(client):
    """
    Negative delay predictions from the locked regression model
    must be returned raw without clamping.
    """
    response = client.post("/projects/400234/predict")
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_delay_months"] < 0
    assert data["predicted_delay_months"] == -3.83


def test_predict_project_not_found(client):
    """Nonexistent project_id returns HTTP 404 with standard detail."""
    response = client.post("/projects/999999/predict")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Project '999999' was not found in the current inference dataset."


def test_predict_whitespace_project_id(client):
    """Whitespace-only project ID returns HTTP 422."""
    response = client.post("/projects/%20%20/predict")
    assert response.status_code == 422


def test_dataset_unavailable_returns_503(client):
    """When dataset is unavailable, endpoints return HTTP 503 without leaking paths."""
    with patch("backend.app.main.get_project_service") as mock_get_svc:
        mock_svc = mock_get_svc.return_value
        mock_svc.search_projects.side_effect = DatasetUnavailableError("Missing dataset")
        mock_svc.get_project.side_effect = DatasetUnavailableError("Missing dataset")

        res_lookup = client.get("/projects")
        assert res_lookup.status_code == 503
        assert "Current inference dataset is unavailable" in res_lookup.json()["detail"]

        with patch("backend.app.predictor.get_project_service") as mock_pred_svc:
            mock_pred_svc.return_value.get_project.side_effect = DatasetUnavailableError("Missing dataset")
            res_pred = client.post("/projects/400234/predict")
            assert res_pred.status_code == 503
            assert "Current inference dataset is unavailable" in res_pred.json()["detail"]
