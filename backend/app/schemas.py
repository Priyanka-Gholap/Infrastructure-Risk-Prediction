from typing import Literal, Annotated
from pydantic import BaseModel, ConfigDict, Field

class ProjectFeatures(BaseModel):
    """
    Exact 36 SAFE_MVP model features defined authoritatively by:
    - ml/schemas/inference_input_schema.json
    - ml/schemas/production_feature_schema.csv

    Features marked in 'required' in inference_input_schema.json must be present in the payload.
    Nullable features accept null (None) for pipeline median/constant imputation.
    Unknown or extraneous features are strictly forbidden.
    """
    model_config = ConfigDict(extra="forbid")

    # --- Core Required Features (Mandatory keys in input payload) ---
    original_cost: Annotated[
        float | None,
        Field(description="Sanctioned project cost in INR Crores. If null, imputed with training median.")
    ]
    cumulative_expenditure: Annotated[
        float | None,
        Field(description="Total funds disbursed up to snapshot in INR Crores. If null, imputed with training median.")
    ]
    physical_progress_pct: Annotated[
        float | None,
        Field(description="Reported cumulative physical progress percentage. If null, imputed with training median.")
    ]
    planned_duration_months: Annotated[
        float | None,
        Field(description="Total planned duration sanctioned in months. If null, imputed with training median.")
    ]
    elapsed_months: Annotated[
        float | None,
        Field(description="Actual calendar months elapsed since start. If null, imputed with training median.")
    ]

    # --- Derived / Optional Numerical Features (Optional in payload, default to None) ---
    approval_to_start_months: float | None = Field(
        default=None,
        description="Lead time between approval and ground start in months."
    )
    expenditure_percent_of_original_cost: float | None = Field(
        default=None,
        description="Financial budget utilization percentage at snapshot."
    )
    monthly_expenditure_change: float | None = Field(
        default=None,
        description="Net capital expenditure disbursed during month preceding snapshot."
    )
    monthly_expenditure_growth_pct: float | None = Field(
        default=None,
        description="Percentage growth rate in cumulative expenditure over prior month."
    )
    monthly_progress_change: float | None = Field(
        default=None,
        description="Percentage points of physical progress completed in prior month."
    )
    progress_growth_rate: float | None = Field(
        default=None,
        description="Relative percentage growth in cumulative physical progress."
    )
    remaining_planned_months: float | None = Field(
        default=None,
        description="Months remaining until original deadline (negative if past)."
    )
    elapsed_duration_ratio: float | None = Field(
        default=None,
        description="Ratio of timeline elapsed to original planned duration."
    )
    is_past_original_doc: float | None = Field(
        default=None,
        description="Indicator whether project has already exceeded original scheduled deadline."
    )
    efficiency_gap: float | None = Field(
        default=None,
        description="Difference between physical delivery % and financial utilization %."
    )
    cost_physical_ratio: float | None = Field(
        default=None,
        description="Capital expenditure consumed per unit percentage of physical completion."
    )
    expected_progress_pct: float | None = Field(
        default=None,
        description="Analytical linear planned progress benchmark derived from original schedule."
    )
    progress_gap_pct_points: float | None = Field(
        default=None,
        description="Progress delivery gap relative to analytical linear baseline."
    )
    months_since_first_observation: float | int | None = Field(
        default=None,
        description="Number of months project has been monitored in dataset."
    )
    observation_count_to_date: float | int | None = Field(
        default=None,
        description="Total number of monthly monitoring records available for project."
    )
    physical_progress_1_month_change: float | None = Field(
        default=None,
        description="1-month change in physical progress."
    )
    physical_progress_2_month_change: float | None = Field(
        default=None,
        description="2-month change in physical progress."
    )
    expenditure_1_month_change: float | None = Field(
        default=None,
        description="1-month change in cumulative expenditure."
    )
    expenditure_2_month_change: float | None = Field(
        default=None,
        description="2-month change in cumulative expenditure."
    )
    progress_trend_slope: float | None = Field(
        default=None,
        description="Average monthly progress rate over monitored window."
    )
    expenditure_trend_slope: float | None = Field(
        default=None,
        description="Average monthly capital spend rate over monitored window."
    )

    # --- Data Quality / Schedule Anomaly Flags (Binary: 0, 1, or None) ---
    negative_expenditure_flag: Literal[0, 1] | None = Field(
        default=None,
        description="Flags negative expenditure accounting anomalies (1 if active, 0 otherwise)."
    )
    missing_previous_month_flag: Literal[0, 1] | None = Field(
        default=None,
        description="Flags whether prior-month observation was unavailable."
    )
    invalid_duration_flag: Literal[0, 1] | None = Field(
        default=None,
        description="Flags projects where original duration is invalid/zero/negative."
    )
    past_original_doc_flag: Literal[0, 1] | None = Field(
        default=None,
        description="Flags projects already in schedule overrun at snapshot."
    )
    missing_key_date_flag: Literal[0, 1] | None = Field(
        default=None,
        description="Flags projects missing milestone baseline dates."
    )
    suspicious_value_flag: Literal[0, 1] | None = Field(
        default=None,
        description="Flags physical progress >100% or extreme expenditure ratios."
    )

    # --- Categorical Features (Sponsoring entity & geography) ---
    ministry: str | None = Field(
        default=None,
        description="Central Government Ministry sponsoring the project. If null, imputed as 'Unknown'."
    )
    sector: str | None = Field(
        default=None,
        description="Sector classification (Railways, Road Transport, Power, etc.). If null, imputed as 'Unknown'."
    )
    implementing_agency: str | None = Field(
        default=None,
        description="Public sector agency executing the project. If null, imputed as 'Unknown'."
    )
    state: str | None = Field(
        default=None,
        description="State/UT where project is physically executed. If null, imputed as 'Unknown'."
    )


class PredictRequest(BaseModel):
    """
    Request payload conforming to ml/schemas/inference_input_schema.json.
    """
    model_config = ConfigDict(extra="forbid")

    project_id: Annotated[
        str,
        Field(min_length=1, description="Unique official MoSPI Project ID identifier.")
    ]
    project_name: str | None = Field(
        default=None,
        description="Official Project Title (metadata identifier)."
    )
    snapshot_month: str | None = Field(
        default=None,
        description="Monitoring snapshot month YYYY-MM (metadata identifier)."
    )
    features: ProjectFeatures


class PredictResponse(BaseModel):
    """
    Response payload conforming strictly to ml/schemas/inference_output_schema.json.
    """
    model_config = ConfigDict(extra="forbid")

    project_id: str = Field(
        description="Project ID of evaluated snapshot."
    )
    cost_overrun_probability: float = Field(
        ge=0.0, le=1.0,
        description="Predicted probability of cost overrun >= 10% from cost_overrun_model.joblib."
    )
    cost_overrun_flag: Literal[0, 1] = Field(
        description="Binary early-warning alert: 1 if cost_overrun_probability >= cost_overrun_threshold, else 0."
    )
    cost_overrun_threshold: float = Field(
        description="Locked operating decision threshold for cost overrun classification (0.40)."
    )
    delay_probability: float = Field(
        ge=0.0, le=1.0,
        description="Predicted probability of delay >= 60 days vs revised deadline from delay_model.joblib."
    )
    delay_flag: Literal[0, 1] = Field(
        description="Binary early-warning alert: 1 if delay_probability >= delay_threshold, else 0."
    )
    delay_threshold: float = Field(
        description="Locked operating decision threshold for delay classification (0.50)."
    )
    predicted_delay_months: float = Field(
        description="Continuous prediction of total calendar months delayed from original baseline from delay_regressor.joblib."
    )
    overall_risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(
        description="Deterministic composite risk tier: CRITICAL if both flagged; HIGH if either flagged; MEDIUM if probability >= 0.30; LOW otherwise."
    )


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    models_loaded: bool = True


class ModelDetail(BaseModel):
    algorithm: str
    operating_threshold: float | None = None
    cv_metrics: dict
    test_metrics: dict
    hyperparameters: dict | None = None


class ModelInfoResponse(BaseModel):
    pipeline_stage: str
    trained_date: str
    n_training_samples: int
    n_test_samples: int
    feature_count: int
    safe_mvp_features: list[str]
    categorical_features: list[str]
    numerical_features: list[str]
    operating_thresholds: dict[str, float]
    models: dict[str, ModelDetail]


class ProjectLookupItem(BaseModel):
    """
    Lightweight project summary for search and dropdown selection.
    """
    model_config = ConfigDict(extra="forbid")

    project_id: str = Field(
        description="Unique official MoSPI Project ID identifier."
    )
    project_name: str = Field(
        description="Official Project Title."
    )
    snapshot_month: str = Field(
        description="Latest observed report month (YYYY-MM)."
    )


class ProjectPredictionResponse(BaseModel):
    """
    Production prediction response for a monitored infrastructure project.
    """
    model_config = ConfigDict(extra="forbid")

    project_id: str = Field(
        description="Unique official MoSPI Project ID identifier."
    )
    project_name: str = Field(
        description="Official Project Title."
    )
    snapshot_month: str = Field(
        description="Latest observed report month (YYYY-MM)."
    )
    overall_risk: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(
        description="Deterministic composite risk tier: CRITICAL if both flagged; HIGH if either flagged; MEDIUM if probability >= 0.30; LOW otherwise."
    )
    cost_overrun_probability: float = Field(
        ge=0.0, le=1.0,
        description="Predicted probability of cost overrun >= 10% from cost_overrun_model.joblib."
    )
    cost_overrun_risk: Literal["HIGH", "MEDIUM", "LOW"] = Field(
        description="Cost overrun risk tier derived from threshold: HIGH if probability >= 0.40, MEDIUM if >= 0.30, LOW otherwise."
    )
    schedule_delay_probability: float = Field(
        ge=0.0, le=1.0,
        description="Predicted probability of schedule delay >= 60 days from delay_model.joblib."
    )
    schedule_delay_risk: Literal["HIGH", "MEDIUM", "LOW"] = Field(
        description="Schedule delay risk tier derived from threshold: HIGH if probability >= 0.50, MEDIUM if >= 0.30, LOW otherwise."
    )
    predicted_delay_months: float = Field(
        description="Continuous raw prediction of total calendar months delayed from original baseline from delay_regressor.joblib."
    )


class FeatureDriver(BaseModel):
    """
    Individual feature contribution driver from SHAP TreeExplainer.
    """
    model_config = ConfigDict(extra="forbid")

    feature_name: str = Field(description="Production feature identifier from 36 SAFE_MVP schema.")
    display_name: str = Field(description="Human-readable business label.")
    feature_value: float | str | None = Field(description="Actual project feature value (null if missing).")
    is_missing: bool = Field(default=False, description="True if feature was missing/null in raw snapshot.")
    unit: str = Field(description="Metric unit: %, months, INR Cr, ratio, flag, or category.")
    contribution: float = Field(description="Exact SHAP attribution value.")
    contribution_display: str = Field(description="Formatted contribution string, e.g. +7.81% pts or +82.97 mo.")
    direction: Literal["INCREASES_RISK", "DECREASES_RISK", "INCREASES_DELAY", "REDUCES_DELAY"] = Field(
        description="Model-specific effect direction."
    )
    rank: int = Field(ge=1, le=36, description="Rank ordered by descending abs(contribution).")


class ModelExplanation(BaseModel):
    """
    Complete attribution audit and top drivers for an individual model.
    """
    model_config = ConfigDict(extra="forbid")

    model_name: str = Field(description="Model identifier: cost_overrun_model, delay_model, or delay_regressor.")
    target_metric: Literal["cost_overrun_probability", "schedule_delay_probability", "predicted_delay_months"] = Field(
        description="Name of the predicted target metric."
    )
    base_value: float = Field(description="Model expected base value across training baseline.")
    predicted_value: float = Field(description="Authoritative model output.")
    total_contribution: float = Field(description="Sum of all 36 SAFE_MVP feature contributions.")
    displayed_contribution: float = Field(description="Sum of the top-K displayed feature contributions.")
    audit_reconciliation_gap: float = Field(description="abs(base_value + total_contribution - predicted_value).")
    top_drivers: list[FeatureDriver] = Field(description="Top K ranked feature drivers.")
    audit_status: Literal["reconciled", "discrepancy"] = Field(
        default="reconciled",
        description="reconciled if audit_reconciliation_gap <= 1e-5 else discrepancy."
    )


class ProjectExplainabilityResponse(BaseModel):
    """
    Production explainability response for a monitored infrastructure project.
    Contains model-specific explanations for cost overrun, delay, and secondary regression models.
    """
    model_config = ConfigDict(extra="forbid")

    project_id: str = Field(description="Unique official MoSPI Project ID identifier.")
    project_name: str = Field(description="Official Project Title.")
    snapshot_month: str = Field(description="Latest observed report month (YYYY-MM).")
    cost_overrun_explanation: ModelExplanation
    schedule_delay_explanation: ModelExplanation
    predicted_delay_explanation: ModelExplanation
    top_k: int = Field(default=5, description="Number of top drivers displayed per model.")


