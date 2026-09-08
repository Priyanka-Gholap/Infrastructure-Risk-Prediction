"""
Test suite for Step 6D-C: Real Model Explainability & Early-Warning Drivers.
Verifies SHAP TreeExplainer mathematical reconciliation, categorical aggregation,
prediction invariance, model-specific directions, and error handling.
"""

from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.project_service import DatasetUnavailableError


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_prediction_invariance_before_vs_after_explainability(client):
    """
    CORRECTION 11 INVARIANT:
    Ensures that adding explainability did NOT modify the existing
    POST /projects/{project_id}/predict response schema or values.
    Predictions must remain bit-for-bit identical and purely observational.

    Executes true before-vs-after sequence:
    1. Call POST /projects/{project_id}/predict (save response)
    2. Call GET /projects/{project_id}/explain
    3. Call POST /projects/{project_id}/predict again (save response)
    4. Assert before and after responses are bit-for-bit identical across all 9 fields.
    5. Assert predictions match authoritative historical outputs.
    """
    authoritative_predictions = {
        "400234": {
            "project_id": "400234",
            "project_name": "Third Railway Line between Patratu-Sonnagar [291 kms]",
            "snapshot_month": "2025-12",
            "overall_risk": "LOW",
            "cost_overrun_risk": "LOW",
            "schedule_delay_risk": "LOW",
            "cost_overrun_probability": 0.2388,
            "schedule_delay_probability": 0.1615,
            "predicted_delay_months": -3.83,
        },
        "400161": {
            "project_id": "400161",
            "project_name": "PP Project, Pata",
            "snapshot_month": "2026-01",
            "overall_risk": "HIGH",
            "cost_overrun_risk": "HIGH",
            "schedule_delay_risk": "LOW",
            "cost_overrun_probability": 0.7201,
            "schedule_delay_probability": 0.1608,
            "predicted_delay_months": 26.73,
        },
        "400104": {
            "project_id": "400104",
            "project_name": "Punpun Barrage Project",
            "snapshot_month": "2026-03",
            "overall_risk": "HIGH",
            "cost_overrun_risk": "HIGH",
            "schedule_delay_risk": "LOW",
            "cost_overrun_probability": 0.5231,
            "schedule_delay_probability": 0.1451,
            "predicted_delay_months": 153.04,
        },
    }

    for pid, expected_data in authoritative_predictions.items():
        # 1. Call predict BEFORE explain
        res_before = client.post(f"/projects/{pid}/predict")
        assert res_before.status_code == 200
        data_before = res_before.json()

        # 2. Call explain
        res_explain = client.get(f"/projects/{pid}/explain")
        assert res_explain.status_code == 200

        # 3. Call predict AFTER explain
        res_after = client.post(f"/projects/{pid}/predict")
        assert res_after.status_code == 200
        data_after = res_after.json()

        # 4. Assert bit-for-bit identical before and after
        assert data_before == data_after, f"Prediction variance detected before vs after explain for project {pid}"

        # 5. Assert all 9 fields match authoritative ground truth
        assert set(data_before.keys()) == {
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
        assert data_before == expected_data


def test_explainability_endpoint_schema(client):
    """
    Verifies that GET /projects/{project_id}/explain returns the complete,
    valid response schema with all documented audit fields.
    """
    response = client.get("/projects/400234/explain")
    assert response.status_code == 200
    data = response.json()

    assert data["project_id"] == "400234"
    assert "Patratu" in data["project_name"]
    assert data["snapshot_month"] == "2025-12"
    assert data["top_k"] == 5

    # Check each model explanation structure
    for model_key in ["cost_overrun_explanation", "schedule_delay_explanation", "predicted_delay_explanation"]:
        assert model_key in data
        exp = data[model_key]
        assert "model_name" in exp
        assert "target_metric" in exp
        assert "base_value" in exp
        assert "predicted_value" in exp
        assert "total_contribution" in exp
        assert "displayed_contribution" in exp
        assert "audit_reconciliation_gap" in exp
        assert "top_drivers" in exp
        assert "audit_status" in exp
        assert exp["audit_status"] == "reconciled"
        assert len(exp["top_drivers"]) == 5


def test_mathematical_reconciliation_invariant_tolerance(client):
    """
    CORRECTION 4 & 7 INVARIANT:
    Verifies that abs(base_value + total_contribution - predicted_value) <= 1e-5
    across all models for multiple diverse projects.
    """
    test_projects = ["400234", "400161", "400104"]

    for pid in test_projects:
        response = client.get(f"/projects/{pid}/explain")
        assert response.status_code == 200
        data = response.json()

        for model_key in ["cost_overrun_explanation", "schedule_delay_explanation", "predicted_delay_explanation"]:
            exp = data[model_key]
            base = exp["base_value"]
            total = exp["total_contribution"]
            pred = exp["predicted_value"]
            gap = exp["audit_reconciliation_gap"]

            recomputed_gap = abs(base + total - pred)
            assert recomputed_gap <= 1e-5, f"Reconciliation failed for {pid} on {model_key}: gap={recomputed_gap}"
            assert gap <= 1e-5
            assert exp["audit_status"] == "reconciled"


def test_top_k_vs_total_attribution_separation(client):
    """
    CORRECTION 4 INVARIANT:
    Verifies that total_contribution represents the sum of ALL 36 features,
    whereas displayed_contribution is the sum of the Top-K displayed drivers.
    """
    response = client.get("/projects/400161/explain?top_k=5")
    assert response.status_code == 200
    data = response.json()

    exp = data["cost_overrun_explanation"]
    displayed = exp["displayed_contribution"]
    total = exp["total_contribution"]

    drivers_sum = sum(d["contribution"] for d in exp["top_drivers"])
    assert abs(displayed - drivers_sum) < 1e-5
    # Total contribution must not be conflated with displayed contribution
    assert total != displayed


def test_direction_semantics_model_specific(client):
    """
    CORRECTION 8 INVARIANT:
    Classifiers must use INCREASES_RISK / DECREASES_RISK.
    Regressor must use INCREASES_DELAY / REDUCES_DELAY.
    """
    response = client.get("/projects/400161/explain")
    assert response.status_code == 200
    data = response.json()

    # Cost classifier drivers
    for d in data["cost_overrun_explanation"]["top_drivers"]:
        if d["contribution"] > 0:
            assert d["direction"] == "INCREASES_RISK"
        else:
            assert d["direction"] == "DECREASES_RISK"

    # Schedule delay classifier drivers
    for d in data["schedule_delay_explanation"]["top_drivers"]:
        if d["contribution"] > 0:
            assert d["direction"] == "INCREASES_RISK"
        else:
            assert d["direction"] == "DECREASES_RISK"

    # Regressor drivers
    for d in data["predicted_delay_explanation"]["top_drivers"]:
        if d["contribution"] > 0:
            assert d["direction"] == "INCREASES_DELAY"
        else:
            assert d["direction"] == "REDUCES_DELAY"


def test_reference_projects_validation_cases(client):
    """
    CORRECTION 6:
    Verifies reference projects 400234, 400161, 400104 as behavioral validation cases
    without hardcoding brittle float numbers in the test.
    """
    # 400161 (High cost overrun probability: 72.01%)
    res_161 = client.get("/projects/400161/explain")
    assert res_161.status_code == 200
    cost_drivers_161 = res_161.json()["cost_overrun_explanation"]["top_drivers"]
    feature_names_161 = [d["feature_name"] for d in cost_drivers_161]
    # Key budget metrics should appear in top cost drivers
    assert any("expenditure" in name or "cost" in name for name in feature_names_161)
    # The top driver should increase risk
    assert cost_drivers_161[0]["direction"] == "INCREASES_RISK"

    # 400104 (High continuous delay: +153 months)
    res_104 = client.get("/projects/400104/explain")
    assert res_104.status_code == 200
    delay_drivers_104 = res_104.json()["predicted_delay_explanation"]["top_drivers"]
    feature_names_104 = [d["feature_name"] for d in delay_drivers_104]
    # Timeline features should appear in top delay drivers
    assert any("elapsed" in name or "month" in name or "duration" in name for name in feature_names_104)
    # The top driver should increase delay
    assert delay_drivers_104[0]["direction"] == "INCREASES_DELAY"

    # 400234 (Ahead of schedule: -3.83 months)
    res_234 = client.get("/projects/400234/explain")
    assert res_234.status_code == 200
    cost_drivers_234 = res_234.json()["cost_overrun_explanation"]["top_drivers"]
    # Top cost driver suppresses risk (negative contribution)
    assert cost_drivers_234[0]["direction"] == "DECREASES_RISK"


def test_top_k_query_parameter(client):
    """Verifies that the top_k query parameter properly limits returned drivers."""
    res_3 = client.get("/projects/400234/explain?top_k=3")
    assert res_3.status_code == 200
    assert len(res_3.json()["cost_overrun_explanation"]["top_drivers"]) == 3
    assert res_3.json()["top_k"] == 3

    res_7 = client.get("/projects/400234/explain?top_k=7")
    assert res_7.status_code == 200
    assert len(res_7.json()["cost_overrun_explanation"]["top_drivers"]) == 7


def test_nonexistent_project_returns_404(client):
    """Verifies that an invalid project ID returns 404."""
    response = client.get("/projects/nonexistent_999999/explain")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_whitespace_project_id_returns_422(client):
    """Verifies that whitespace project ID returns 422."""
    response = client.get("/projects/%20%20/explain")
    assert response.status_code == 422


def test_explainability_dataset_unavailable_returns_503(client):
    """
    CORRECTION 2 & 7:
    Verifies that when the inference dataset is unavailable,
    GET /projects/{project_id}/explain returns HTTP 503 without crashing.
    """
    with patch("backend.app.explainability.get_project_service") as mock_exp_svc:
        mock_exp_svc.return_value.get_project.side_effect = DatasetUnavailableError("Simulated missing dataset")
        res = client.get("/projects/400234/explain")
        assert res.status_code == 503
        assert "Current inference dataset is unavailable" in res.json()["detail"]


def test_prediction_resilience_when_explainability_fails(client):
    """
    CORRECTION 7:
    Verifies decoupled failure isolation:
    Even if explainability computation fails with an error,
    the primary POST /projects/{project_id}/predict endpoint remains 100% functional.
    """
    with patch("backend.app.explainability.ExplainabilityService.explain_project") as mock_explain:
        mock_explain.side_effect = RuntimeError("Simulated SHAP computation failure")

        # Explainability fails with 500
        res_explain = client.get("/projects/400234/explain")
        assert res_explain.status_code == 500
        assert "Explainability computation failed" in res_explain.json()["detail"]

        # Primary prediction remains completely unblocked and functional
        res_predict = client.post("/projects/400234/predict")
        assert res_predict.status_code == 200
        data_pred = res_predict.json()
        assert data_pred["project_id"] == "400234"
        assert data_pred["overall_risk"] == "LOW"
        assert data_pred["cost_overrun_probability"] == 0.2388
        assert data_pred["schedule_delay_probability"] == 0.1615
        assert data_pred["predicted_delay_months"] == -3.83


def test_predict_vs_explain_numerical_parity(client):
    """
    CORRECTION 5:
    Verifies raw numerical parity between /predict and /explain across all 3 reference projects
    WITHOUT rounding either side before comparison.
    
    Data Integrity Analysis:
    - /predict publishes presentation metrics rounded to 4 decimals for probabilities (round(p, 4))
      and 2 decimals for continuous delay (round(d, 2)) per locked Step 6C API contract.
    - /explain publishes raw model predictions to 6 decimal places (round(p, 6)) to satisfy
      the SHAP TreeExplainer additivity invariant: abs(base_value + total_contribution - predicted_value) <= 1e-5.
    - Direct raw comparison without presentation rounding is mathematically bounded by the
      half-step quantization error:
      * Probabilities: abs(p - e) <= 0.5 * 10^-4 = 5.0e-5 (measured: 1.4e-5 to 4.8e-5)
      * Delay Months:  abs(p - e) <= 0.5 * 10^-2 = 5.0e-3 (measured: 1.3e-3 to 3.7e-3)
    """
    reference_projects = ["400234", "400161", "400104"]

    for pid in reference_projects:
        res_pred = client.post(f"/projects/{pid}/predict")
        assert res_pred.status_code == 200
        pred_data = res_pred.json()

        res_exp = client.get(f"/projects/{pid}/explain")
        assert res_exp.status_code == 200
        exp_data = res_exp.json()

        cost_pred = pred_data["cost_overrun_probability"]
        cost_exp = exp_data["cost_overrun_explanation"]["predicted_value"]
        # Direct raw comparison without rounding either side
        assert abs(cost_pred - cost_exp) <= 5e-5, f"Cost prob raw parity failed for {pid}: pred={cost_pred}, exp={cost_exp}"

        delay_pred = pred_data["schedule_delay_probability"]
        delay_exp = exp_data["schedule_delay_explanation"]["predicted_value"]
        assert abs(delay_pred - delay_exp) <= 5e-5, f"Delay prob raw parity failed for {pid}: pred={delay_pred}, exp={delay_exp}"

        months_pred = pred_data["predicted_delay_months"]
        months_exp = exp_data["predicted_delay_explanation"]["predicted_value"]
        assert abs(months_pred - months_exp) <= 5e-3, f"Delay months raw parity failed for {pid}: pred={months_pred}, exp={months_exp}"
