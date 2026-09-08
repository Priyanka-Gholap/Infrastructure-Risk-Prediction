import pytest
from backend.app.risk_policy import compute_overall_risk

def test_risk_critical():
    """CRITICAL: Both cost and delay flagged."""
    assert compute_overall_risk(cost_flag=1, delay_flag=1, cost_probability=0.75, delay_probability=0.85) == "CRITICAL"
    assert compute_overall_risk(cost_flag=1, delay_flag=1, cost_probability=0.40, delay_probability=0.50) == "CRITICAL"


def test_risk_high_cost_only():
    """HIGH: Only cost flagged."""
    assert compute_overall_risk(cost_flag=1, delay_flag=0, cost_probability=0.60, delay_probability=0.20) == "HIGH"
    assert compute_overall_risk(cost_flag=1, delay_flag=0, cost_probability=0.40, delay_probability=0.10) == "HIGH"


def test_risk_high_delay_only():
    """HIGH: Only delay flagged."""
    assert compute_overall_risk(cost_flag=0, delay_flag=1, cost_probability=0.25, delay_probability=0.70) == "HIGH"
    assert compute_overall_risk(cost_flag=0, delay_flag=1, cost_probability=0.10, delay_probability=0.50) == "HIGH"


def test_risk_medium_cost_prob_trigger():
    """MEDIUM: Neither flagged, but cost_probability >= 0.30."""
    assert compute_overall_risk(cost_flag=0, delay_flag=0, cost_probability=0.35, delay_probability=0.15) == "MEDIUM"
    # Exact boundary 0.30
    assert compute_overall_risk(cost_flag=0, delay_flag=0, cost_probability=0.30, delay_probability=0.10) == "MEDIUM"


def test_risk_medium_delay_prob_trigger():
    """MEDIUM: Neither flagged, but delay_probability >= 0.30."""
    assert compute_overall_risk(cost_flag=0, delay_flag=0, cost_probability=0.10, delay_probability=0.35) == "MEDIUM"
    # Exact boundary 0.30
    assert compute_overall_risk(cost_flag=0, delay_flag=0, cost_probability=0.29, delay_probability=0.30) == "MEDIUM"


def test_risk_low():
    """LOW: Neither flagged and both probabilities strictly < 0.30."""
    assert compute_overall_risk(cost_flag=0, delay_flag=0, cost_probability=0.2388, delay_probability=0.1615) == "LOW"
    assert compute_overall_risk(cost_flag=0, delay_flag=0, cost_probability=0.2999, delay_probability=0.2999) == "LOW"
    assert compute_overall_risk(cost_flag=0, delay_flag=0, cost_probability=0.0, delay_probability=0.0) == "LOW"


@pytest.mark.parametrize(
    "case_id, cost_prob, delay_prob, expected_risk",
    [
        ("A", 0.299, 0.299, "LOW"),
        ("B", 0.300, 0.299, "MEDIUM"),
        ("C", 0.299, 0.300, "MEDIUM"),
        ("D", 0.400, 0.499, "HIGH"),
        ("E", 0.399, 0.500, "HIGH"),
        ("F", 0.400, 0.500, "CRITICAL"),
    ],
)
def test_exact_production_policy_boundaries_a_to_f(case_id, cost_prob, delay_prob, expected_risk):
    """
    Validates exact production risk policy boundary thresholds:
    - Cost HIGH flag: cost_prob >= 0.40
    - Delay HIGH flag: delay_prob >= 0.50
    - CRITICAL: both cost and delay flagged
    - HIGH: either cost or delay flagged
    - MEDIUM: neither flagged, but cost_prob >= 0.30 or delay_prob >= 0.30
    - LOW: all criteria strictly below 0.30
    """
    cost_flag = 1 if cost_prob >= 0.40 else 0
    delay_flag = 1 if delay_prob >= 0.50 else 0
    assert compute_overall_risk(
        cost_flag=cost_flag,
        delay_flag=delay_flag,
        cost_probability=cost_prob,
        delay_probability=delay_prob,
    ) == expected_risk

