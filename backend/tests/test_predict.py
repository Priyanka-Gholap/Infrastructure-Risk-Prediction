import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

SAMPLE_400234 = {
    "project_id": "400234",
    "project_name": "Third Railway Line between Patratu-Sonnagar [291 kms]",
    "snapshot_month": "2026-04",
    "features": {
        "original_cost": 8975.0,
        "approval_to_start_months": 21.0,
        "cumulative_expenditure": 4798.96,
        "expenditure_percent_of_original_cost": 53.4703,
        "monthly_expenditure_change": None,
        "monthly_expenditure_growth_pct": None,
        "physical_progress_pct": 90.0,
        "monthly_progress_change": None,
        "progress_growth_rate": None,
        "planned_duration_months": 91.0,
        "elapsed_months": 88.0,
        "remaining_planned_months": 3.0,
        "elapsed_duration_ratio": 0.967,
        "is_past_original_doc": 0.0,
        "efficiency_gap": 36.5297,
        "cost_physical_ratio": 0.5941,
        "expected_progress_pct": 96.7033,
        "progress_gap_pct_points": -6.7033,
        "months_since_first_observation": 0.0,
        "observation_count_to_date": 1.0,
        "physical_progress_1_month_change": None,
        "physical_progress_2_month_change": None,
        "expenditure_1_month_change": None,
        "expenditure_2_month_change": None,
        "progress_trend_slope": None,
        "expenditure_trend_slope": None,
        "negative_expenditure_flag": 0,
        "missing_previous_month_flag": 1,
        "invalid_duration_flag": 0,
        "past_original_doc_flag": 0,
        "missing_key_date_flag": 0,
        "suspicious_value_flag": 0,
        "ministry": "Ministry of Railways",
        "sector": "Railways",
        "implementing_agency": "RVNL - II",
        "state": "Multi-States\n(Bihar, Jharkhand)",
    },
}

SAMPLE_400161 = {
    "project_id": "400161",
    "project_name": "PP Project, Pata",
    "snapshot_month": "2026-04",
    "features": {
        "ministry": "Ministry of Petroleum & Natural Gas",
        "sector": "Oil & Gas",
        "implementing_agency": "Gas Authority of India Limited [GAIL]",
        "state": "Uttar Pradesh",
        "original_cost": 910.56,
        "approval_to_start_months": 0.0,
        "cumulative_expenditure": 1066.0,
        "expenditure_percent_of_original_cost": 117.0708,
        "monthly_expenditure_change": None,
        "monthly_expenditure_growth_pct": None,
        "physical_progress_pct": 99.0,
        "monthly_progress_change": None,
        "progress_growth_rate": None,
        "planned_duration_months": 58.0,
        "elapsed_months": 81.0,
        "remaining_planned_months": -23.0,
        "elapsed_duration_ratio": 1.3966,
        "is_past_original_doc": 1.0,
        "efficiency_gap": -18.0708,
        "cost_physical_ratio": 1.1825,
        "expected_progress_pct": 100.0,
        "progress_gap_pct_points": -1.0,
        "months_since_first_observation": 0.0,
        "observation_count_to_date": 1.0,
        "physical_progress_1_month_change": None,
        "physical_progress_2_month_change": None,
        "expenditure_1_month_change": None,
        "expenditure_2_month_change": None,
        "progress_trend_slope": None,
        "expenditure_trend_slope": None,
        "negative_expenditure_flag": 0,
        "missing_previous_month_flag": 1,
        "invalid_duration_flag": 0,
        "past_original_doc_flag": 1,
        "missing_key_date_flag": 0,
        "suspicious_value_flag": 0,
    },
}


def test_predict_valid_sample_400234():
    """Valid inference on Low-Risk project 400234 conforming strictly to output schema."""
    with TestClient(app) as client:
        response = client.post("/predict", json=SAMPLE_400234)
        assert response.status_code == 200
        data = response.json()

        # Schema contract assertions
        assert data["project_id"] == "400234"
        assert 0.0 <= data["cost_overrun_probability"] <= 1.0
        assert data["cost_overrun_threshold"] == 0.40
        assert data["cost_overrun_flag"] == 0

        assert 0.0 <= data["delay_probability"] <= 1.0
        assert data["delay_threshold"] == 0.50
        assert data["delay_flag"] == 0

        assert isinstance(data["predicted_delay_months"], (int, float))
        assert data["overall_risk_level"] == "LOW"

        # Exact smoke-test values alignment
        assert abs(data["cost_overrun_probability"] - 0.2388) < 1e-3
        assert abs(data["delay_probability"] - 0.1615) < 1e-3
        assert abs(data["predicted_delay_months"] - (-3.83)) < 0.1


def test_predict_high_risk_sample_400161():
    """Valid inference on High-Risk budget overrun project 400161."""
    with TestClient(app) as client:
        response = client.post("/predict", json=SAMPLE_400161)
        assert response.status_code == 200
        data = response.json()

        assert data["project_id"] == "400161"
        assert data["cost_overrun_flag"] == 1
        assert data["cost_overrun_probability"] >= 0.40
        assert data["overall_risk_level"] == "HIGH"


def test_feature_order_invariance():
    """Inference output must be invariant to the order keys are passed in the request dictionary."""
    reversed_features = dict(reversed(list(SAMPLE_400234["features"].items())))
    payload = {
        "project_id": "400234",
        "features": reversed_features,
    }
    with TestClient(app) as client:
        res1 = client.post("/predict", json=SAMPLE_400234)
        res2 = client.post("/predict", json=payload)
        assert res1.status_code == 200
        assert res2.status_code == 200
        assert res1.json() == res2.json()


def test_threshold_boundary_behavior():
    """Verify that operating decision thresholds trigger flags strictly at >= 0.40 (cost) and >= 0.50 (delay)."""
    from backend.app.model_loader import get_model_container
    container = get_model_container()

    # Cost threshold: 0.40
    assert (1 if 0.3999 >= container.cost_threshold else 0) == 0
    assert (1 if 0.4000 >= container.cost_threshold else 0) == 1
    assert (1 if 0.4001 >= container.cost_threshold else 0) == 1

    # Delay threshold: 0.50
    assert (1 if 0.4999 >= container.delay_threshold else 0) == 0
    assert (1 if 0.5000 >= container.delay_threshold else 0) == 1
    assert (1 if 0.5001 >= container.delay_threshold else 0) == 1


def test_predict_missing_required_feature():
    """Omitting a required feature must be rejected with HTTP 422."""
    payload = {
        "project_id": "400234",
        "features": {k: v for k, v in SAMPLE_400234["features"].items() if k != "original_cost"},
    }
    with TestClient(app) as client:
        response = client.post("/predict", json=payload)
        assert response.status_code == 422
        body = response.json()
        assert body["error"] == "Validation Error"
        assert any("original_cost" in d["field"] for d in body["details"])


def test_predict_missing_cumulative_expenditure():
    """Omitting cumulative_expenditure must be rejected with HTTP 422."""
    payload = {
        "project_id": "400234",
        "features": {k: v for k, v in SAMPLE_400234["features"].items() if k != "cumulative_expenditure"},
    }
    with TestClient(app) as client:
        response = client.post("/predict", json=payload)
        assert response.status_code == 422
        body = response.json()
        assert any("cumulative_expenditure" in d["field"] for d in body["details"])


def test_predict_invalid_data_type():
    """Passing a string for numerical feature original_cost must be rejected with HTTP 422."""
    corrupted_features = dict(SAMPLE_400234["features"])
    corrupted_features["original_cost"] = "non_numeric_string"
    payload = {
        "project_id": "400234",
        "features": corrupted_features,
    }
    with TestClient(app) as client:
        response = client.post("/predict", json=payload)
        assert response.status_code == 422
        body = response.json()
        assert any("original_cost" in d["field"] for d in body["details"])


def test_predict_invalid_flag_enum():
    """Passing a value outside [0, 1, null] for a flag must be rejected with HTTP 422."""
    corrupted_features = dict(SAMPLE_400234["features"])
    corrupted_features["negative_expenditure_flag"] = 42
    payload = {
        "project_id": "400234",
        "features": corrupted_features,
    }
    with TestClient(app) as client:
        response = client.post("/predict", json=payload)
        assert response.status_code == 422
        body = response.json()
        assert any("negative_expenditure_flag" in d["field"] for d in body["details"])


def test_predict_forbidden_extra_feature():
    """Passing an extra unapproved feature must be rejected with HTTP 422."""
    extra_features = dict(SAMPLE_400234["features"])
    extra_features["arbitrary_new_column"] = 123.45
    payload = {
        "project_id": "400234",
        "features": extra_features,
    }
    with TestClient(app) as client:
        response = client.post("/predict", json=payload)
        assert response.status_code == 422
        body = response.json()
        assert any("arbitrary_new_column" in d["field"] for d in body["details"])


def test_predict_missing_project_id():
    """Payload missing project_id must be rejected with HTTP 422."""
    payload = {
        "features": SAMPLE_400234["features"],
    }
    with TestClient(app) as client:
        response = client.post("/predict", json=payload)
        assert response.status_code == 422


def test_predict_empty_project_id():
    """Payload with empty string project_id must be rejected with HTTP 422."""
    payload = {
        "project_id": "",
        "features": SAMPLE_400234["features"],
    }
    with TestClient(app) as client:
        response = client.post("/predict", json=payload)
        assert response.status_code == 422


def test_predict_missing_features_object():
    """Payload missing features object must be rejected with HTTP 422."""
    payload = {
        "project_id": "400234",
    }
    with TestClient(app) as client:
        response = client.post("/predict", json=payload)
        assert response.status_code == 422
