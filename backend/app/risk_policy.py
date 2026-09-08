"""
Risk Policy Module for SIH26103.

Authoritative specification from ml/schemas/inference_output_schema.json:
"Deterministic rule-based composite risk category:
- CRITICAL if both cost and delay flagged;
- HIGH if either cost or delay flagged;
- MEDIUM if probability >= 0.30;
- LOW otherwise."
"""

from typing import Literal

RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]

def compute_overall_risk(
    cost_flag: int,
    delay_flag: int,
    cost_probability: float,
    delay_probability: float,
) -> RiskLevel:
    """
    Computes the composite risk tier strictly following the authoritative rule.

    Args:
        cost_flag: Binary early-warning alert (1 if cost_probability >= 0.40, else 0).
        delay_flag: Binary early-warning alert (1 if delay_probability >= 0.50, else 0).
        cost_probability: Predicted probability of cost overrun >= 10%.
        delay_probability: Predicted probability of schedule delay >= 60 days.

    Returns:
        One of 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'.
    """
    if cost_flag == 1 and delay_flag == 1:
        return "CRITICAL"
    if cost_flag == 1 or delay_flag == 1:
        return "HIGH"
    if cost_probability >= 0.30 or delay_probability >= 0.30:
        return "MEDIUM"
    return "LOW"
