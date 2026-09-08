import logging
from typing import Any
import numpy as np
import pandas as pd
import shap

from backend.app.model_loader import get_model_container
from backend.app.project_service import get_project_service
from backend.app.schemas import (
    FeatureDriver,
    ModelExplanation,
    ProjectExplainabilityResponse,
)

logger = logging.getLogger("sih26103.explainability")

# Comprehensive business labels and measurement units for all 36 SAFE_MVP features
FEATURE_METADATA: dict[str, tuple[str, str]] = {
    "original_cost": ("Original Sanctioned Cost", "INR Cr"),
    "cumulative_expenditure": ("Cumulative Expenditure", "INR Cr"),
    "expenditure_percent_of_original_cost": ("Budget Utilization vs Original Sanction", "%"),
    "monthly_expenditure_change": ("Monthly Expenditure Change", "INR Cr"),
    "monthly_expenditure_growth_pct": ("Monthly Expenditure Growth", "%"),
    "expenditure_1_month_change": ("1-Month Expenditure Change", "INR Cr"),
    "expenditure_2_month_change": ("2-Month Expenditure Change", "INR Cr"),
    "expenditure_trend_slope": ("Average Capital Spend Rate", "INR Cr/mo"),
    "approval_to_start_months": ("Pre-Construction Lead Time", "months"),
    "planned_duration_months": ("Sanctioned Duration", "months"),
    "elapsed_months": ("Elapsed Construction Timeline", "months"),
    "remaining_planned_months": ("Remaining Planned Months", "months"),
    "elapsed_duration_ratio": ("Elapsed Duration Ratio", "ratio"),
    "is_past_original_doc": ("Past Original Sanction Date", "flag"),
    "physical_progress_pct": ("Cumulative Physical Progress", "%"),
    "monthly_progress_change": ("Monthly Progress Change", "% pts"),
    "progress_growth_rate": ("Progress Growth Rate", "%"),
    "expected_progress_pct": ("Linear Expected Progress", "%"),
    "progress_gap_pct_points": ("Progress Baseline Gap", "% pts"),
    "physical_progress_1_month_change": ("1-Month Physical Progress Change", "% pts"),
    "physical_progress_2_month_change": ("2-Month Physical Progress Change", "% pts"),
    "progress_trend_slope": ("Average Progress Rate", "% pts/mo"),
    "efficiency_gap": ("Physical vs Financial Delivery Gap", "% pts"),
    "cost_physical_ratio": ("Cost to Physical Progress Ratio", "ratio"),
    "months_since_first_observation": ("Months Monitored", "months"),
    "observation_count_to_date": ("Observation Record Count", "records"),
    "negative_expenditure_flag": ("Negative Expenditure Anomaly", "flag"),
    "missing_previous_month_flag": ("Missing Prior Month Record", "flag"),
    "invalid_duration_flag": ("Invalid Duration Baseline", "flag"),
    "past_original_doc_flag": ("Schedule Overrun Baseline Flag", "flag"),
    "missing_key_date_flag": ("Missing Milestone Date Baseline", "flag"),
    "suspicious_value_flag": ("Progress/Spend Anomaly Flag", "flag"),
    "ministry": ("Sponsoring Central Ministry", "category"),
    "sector": ("Infrastructure Sector", "category"),
    "implementing_agency": ("Executing Public Agency", "category"),
    "state": ("Project Location State/UT", "category"),
}

KNOWN_CATEGORICALS = ["ministry", "sector", "implementing_agency", "state"]


class ExplainabilityService:
    _instance: "ExplainabilityService | None" = None

    def __init__(self) -> None:
        container = get_model_container()
        self.preprocessor = container.cost_overrun_model.named_steps["preprocessor"]
        self.cost_classifier = container.cost_overrun_model.named_steps["classifier"]
        self.delay_classifier = container.delay_model.named_steps["classifier"]
        self.delay_regressor = container.delay_regressor.named_steps["regressor"]
        self.feature_names = container.feature_names

        # 1. Dynamically introspect transformed feature names from ColumnTransformer
        transformed_names = list(self.preprocessor.get_feature_names_out())
        self.col_to_orig: list[str] = []
        for col in transformed_names:
            if col.startswith("num__"):
                orig = col.replace("num__", "")
            elif col.startswith("cat__"):
                stripped = col.replace("cat__", "")
                for cat in KNOWN_CATEGORICALS:
                    if stripped.startswith(cat + "_"):
                        orig = cat
                        break
                else:
                    orig = stripped
            else:
                orig = col
            self.col_to_orig.append(orig)

        # 2. Pre-cache SHAP TreeExplainer instances
        logger.info("Initializing cached SHAP TreeExplainer instances for all 3 models...")
        self.exp_cost = shap.TreeExplainer(self.cost_classifier)
        self.exp_delay = shap.TreeExplainer(self.delay_classifier)
        self.exp_reg = shap.TreeExplainer(self.delay_regressor)

        # Base values
        self.cost_base = float(self.exp_cost.expected_value[1])
        self.delay_base = float(self.exp_delay.expected_value[1])
        reg_exp = self.exp_reg.expected_value
        self.reg_base = float(reg_exp[0] if isinstance(reg_exp, (list, np.ndarray)) else reg_exp)
        logger.info(
            "SHAP TreeExplainer cache ready. Base rates: Cost=%.4f, Delay=%.4f, DelayRegressor=%.2f mo",
            self.cost_base,
            self.delay_base,
            self.reg_base,
        )

    @classmethod
    def get_instance(cls) -> "ExplainabilityService":
        if cls._instance is None:
            cls._instance = ExplainabilityService()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        cls._instance = None

    def explain_project(self, project_id: str, top_k: int = 5) -> ProjectExplainabilityResponse:
        """
        Generates mathematically reconciled feature attributions for a project snapshot.
        1. Retrieves row from ProjectService.
        2. Aligns the 36 SAFE_MVP production features.
        3. Preprocesses and evaluates TreeExplainer across 131 columns.
        4. Aggregates one-hot categorical SHAP values back to the 4 parent categoricals.
        5. Computes total attribution, displayed attribution, and audit reconciliation gap.
        6. Returns validated ProjectExplainabilityResponse.
        """
        project_service = get_project_service()
        record = project_service.get_project(project_id)
        container = get_model_container()

        # Extract features preserving None for NaNs
        features_dict: dict[str, Any] = {}
        for col in self.feature_names:
            val = record.get(col)
            features_dict[col] = None if pd.isna(val) else val

        row_df = pd.DataFrame([features_dict])[self.feature_names]

        # Preprocess features
        X_trans = self.preprocessor.transform(row_df)

        # 1. Compute raw SHAP attributions
        cost_shap_raw = self.exp_cost.shap_values(X_trans)[0, :, 1]
        delay_shap_raw = self.exp_delay.shap_values(X_trans)[0, :, 1]
        reg_shap_raw = self.exp_reg.shap_values(X_trans)[0]

        # 2. Dynamically aggregate 131 columns back to the 36 SAFE_MVP features
        cost_agg: dict[str, float] = {}
        delay_agg: dict[str, float] = {}
        reg_agg: dict[str, float] = {}

        for i, orig_feat in enumerate(self.col_to_orig):
            cost_agg[orig_feat] = cost_agg.get(orig_feat, 0.0) + float(cost_shap_raw[i])
            delay_agg[orig_feat] = delay_agg.get(orig_feat, 0.0) + float(delay_shap_raw[i])
            reg_agg[orig_feat] = reg_agg.get(orig_feat, 0.0) + float(reg_shap_raw[i])

        # 3. Model predicted values from pipeline
        cost_pred = float(container.cost_overrun_model.predict_proba(row_df)[0, 1])
        delay_pred = float(container.delay_model.predict_proba(row_df)[0, 1])
        reg_pred = float(container.delay_regressor.predict(row_df)[0])

        # 4. Build ModelExplanation for each of the 3 models
        cost_explanation = self._build_model_explanation(
            model_name="cost_overrun_model",
            target_metric="cost_overrun_probability",
            base_value=self.cost_base,
            predicted_value=cost_pred,
            feature_contributions=cost_agg,
            raw_features=features_dict,
            is_classifier=True,
            top_k=top_k,
        )

        delay_explanation = self._build_model_explanation(
            model_name="delay_model",
            target_metric="schedule_delay_probability",
            base_value=self.delay_base,
            predicted_value=delay_pred,
            feature_contributions=delay_agg,
            raw_features=features_dict,
            is_classifier=True,
            top_k=top_k,
        )

        reg_explanation = self._build_model_explanation(
            model_name="delay_regressor",
            target_metric="predicted_delay_months",
            base_value=self.reg_base,
            predicted_value=reg_pred,
            feature_contributions=reg_agg,
            raw_features=features_dict,
            is_classifier=False,
            top_k=top_k,
        )

        return ProjectExplainabilityResponse(
            project_id=project_id,
            project_name=str(record.get("project_name", "")),
            snapshot_month=str(record.get("snapshot_month", "")),
            cost_overrun_explanation=cost_explanation,
            schedule_delay_explanation=delay_explanation,
            predicted_delay_explanation=reg_explanation,
            top_k=top_k,
        )

    def _build_model_explanation(
        self,
        model_name: str,
        target_metric: Any,
        base_value: float,
        predicted_value: float,
        feature_contributions: dict[str, float],
        raw_features: dict[str, Any],
        is_classifier: bool,
        top_k: int,
    ) -> ModelExplanation:
        # Total contribution is strictly the sum of all 36 feature attributions
        total_contribution = float(sum(feature_contributions.values()))
        reconciliation_gap = float(abs(base_value + total_contribution - predicted_value))
        audit_status = "reconciled" if reconciliation_gap <= 1e-5 else "discrepancy"

        # Sort all 36 features by absolute contribution descending
        sorted_features = sorted(
            feature_contributions.items(),
            key=lambda item: abs(item[1]),
            reverse=True,
        )

        top_drivers: list[FeatureDriver] = []
        for rank, (feat_name, contrib) in enumerate(sorted_features[:top_k], start=1):
            disp_name, unit = FEATURE_METADATA.get(feat_name, (feat_name, ""))
            raw_val = raw_features.get(feat_name)
            is_missing = pd.isna(raw_val) or raw_val is None

            # Format feature value for display
            if is_missing:
                feat_val_parsed = None
            elif isinstance(raw_val, (int, float, np.number)):
                feat_val_parsed = round(float(raw_val), 4)
            else:
                feat_val_parsed = str(raw_val)

            # Model-specific direction semantics
            if is_classifier:
                direction = "INCREASES_RISK" if contrib > 0 else "DECREASES_RISK"
                pct_points = contrib * 100.0
                sign = "+" if pct_points > 0 else ""
                contrib_display = f"{sign}{pct_points:.2f}% pts"
            else:
                direction = "INCREASES_DELAY" if contrib > 0 else "REDUCES_DELAY"
                sign = "+" if contrib > 0 else ""
                contrib_display = f"{sign}{contrib:.2f} mo"

            top_drivers.append(
                FeatureDriver(
                    feature_name=feat_name,
                    display_name=disp_name,
                    feature_value=feat_val_parsed,
                    is_missing=is_missing,
                    unit=unit,
                    contribution=round(contrib, 6),
                    contribution_display=contrib_display,
                    direction=direction,
                    rank=rank,
                )
            )

        displayed_contribution = float(sum(d.contribution for d in top_drivers))

        return ModelExplanation(
            model_name=model_name,
            target_metric=target_metric,
            base_value=round(base_value, 6),
            predicted_value=round(predicted_value, 6),
            total_contribution=round(total_contribution, 6),
            displayed_contribution=round(displayed_contribution, 6),
            audit_reconciliation_gap=round(reconciliation_gap, 8),
            top_drivers=top_drivers,
            audit_status=audit_status,
        )
