"""
Step 6C.1 Automated Audit Test Suite.

Verifies that the entire 2,131 project snapshot cohort in current_inference_dataset.csv
can be processed end-to-end through the production inference pipeline without failure,
producing mathematically bounded probabilities, valid risk tiers, and no missing or
duplicate project records.
"""

import math
import pandas as pd
import numpy as np
import pytest

from backend.app.config import settings
from backend.app.model_loader import load_models
from backend.app.project_service import get_project_service
from backend.app.predictor import PredictorService
from backend.app.risk_policy import compute_overall_risk


@pytest.fixture(scope="module")
def model_container():
    return load_models()


@pytest.fixture(scope="module")
def project_service():
    ps = get_project_service()
    ps.load_dataset()
    return ps


def test_full_dataset_inference_audit(model_container, project_service):
    """
    Validates complete production inference across all 2,131 projects:
    - Exactly 2,131 projects loaded
    - Zero duplicate project IDs
    - No NaN / infinite outputs across all 3 estimators
    - Valid probability ranges [0.0, 1.0]
    - Valid risk labels adhering strictly to the authoritative risk policy
    """
    dataset_path = project_service.dataset_path
    assert dataset_path.exists(), f"Dataset file missing at {dataset_path}"

    df = pd.read_csv(dataset_path, dtype={"project_id": str})
    
    # 1. Project cardinality & uniqueness
    total_projects = len(df)
    assert total_projects == 2131, f"Expected 2,131 projects, found {total_projects}"
    assert df["project_id"].nunique() == 2131, "Duplicate project IDs detected in dataset"

    # 2. Extract production feature matrix
    feature_names = model_container.feature_names
    assert len(feature_names) == 36, f"Expected 36 production features, found {len(feature_names)}"
    X = df[feature_names].copy()

    # 3. Model execution
    cost_probs = model_container.cost_overrun_model.predict_proba(X)[:, 1]
    delay_probs = model_container.delay_model.predict_proba(X)[:, 1]
    delay_preds = model_container.delay_regressor.predict(X)

    # 4. No NaN or Inf
    assert not np.isnan(cost_probs).any(), "NaN found in cost overrun probabilities"
    assert not np.isnan(delay_probs).any(), "NaN found in schedule delay probabilities"
    assert not np.isnan(delay_preds).any(), "NaN found in predicted delay regression"
    assert not np.isinf(cost_probs).any(), "Inf found in cost overrun probabilities"
    assert not np.isinf(delay_probs).any(), "Inf found in schedule delay probabilities"
    assert not np.isinf(delay_preds).any(), "Inf found in predicted delay regression"

    # 5. Probability range validation
    assert ((cost_probs >= 0.0) & (cost_probs <= 1.0)).all(), "Cost probabilities out of [0, 1] bounds"
    assert ((delay_probs >= 0.0) & (delay_probs <= 1.0)).all(), "Delay probabilities out of [0, 1] bounds"

    # 6. Risk policy validation
    valid_risk_labels = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
    for idx in range(total_projects):
        c_p = float(cost_probs[idx])
        d_p = float(delay_probs[idx])
        c_flag = 1 if c_p >= model_container.cost_threshold else 0
        d_flag = 1 if d_p >= model_container.delay_threshold else 0

        risk = compute_overall_risk(
            cost_flag=c_flag,
            delay_flag=d_flag,
            cost_probability=c_p,
            delay_probability=d_p,
        )
        assert risk in valid_risk_labels, f"Invalid risk tier '{risk}' for row {idx}"


def test_predictor_service_on_diverse_cohort(model_container, project_service):
    """
    Tests PredictorService.predict_project_by_id on diverse boundary projects
    spanning low risk, high risk, ahead of schedule, and large delay projects.
    """
    predictor = PredictorService()
    test_cohort = [
        "400234",  # Low risk, negative delay
        "400161",  # High cost risk, positive delay
        "701586",  # Medium risk, negative delay
        "619084",  # Top positive delay (191.35 mo)
        "709757",  # Top negative delay (-19.70 mo)
    ]

    for pid in test_cohort:
        resp = predictor.predict_project_by_id(pid)
        assert resp.project_id == pid
        assert 0.0 <= resp.cost_overrun_probability <= 1.0
        assert 0.0 <= resp.schedule_delay_probability <= 1.0
        assert resp.overall_risk in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
        assert not math.isnan(resp.predicted_delay_months)
