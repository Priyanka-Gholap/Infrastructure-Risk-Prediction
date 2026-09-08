import logging
import pandas as pd

from backend.app.model_loader import get_model_container
from backend.app.project_service import get_project_service
from backend.app.risk_policy import compute_overall_risk
from backend.app.schemas import PredictRequest, PredictResponse, ProjectPredictionResponse

logger = logging.getLogger("sih26103.predictor")

class PredictorService:
    @staticmethod
    def predict(payload: PredictRequest) -> PredictResponse:
        """
        Executes inference for a validated project snapshot:
        1. Obtains loaded model container with frozen pipelines.
        2. Formats features into a single-row DataFrame aligned with model.feature_names_in_.
        3. Computes class probabilities and continuous delay months.
        4. Applies locked thresholds: Cost=0.40, Delay=0.50.
        5. Computes authoritative composite risk tier.
        6. Returns validated PredictResponse.
        """
        container = get_model_container()

        # Convert Pydantic features to dictionary
        features_dict = payload.features.model_dump()

        # Create DataFrame and ensure column sequence matches feature_names_in_
        row_df = pd.DataFrame([features_dict])
        aligned_df = row_df[container.feature_names]

        try:
            # 1. Cost overrun inference
            cost_prob = float(container.cost_overrun_model.predict_proba(aligned_df)[0, 1])
            cost_flag = 1 if cost_prob >= container.cost_threshold else 0

            # 2. Delay classification inference
            delay_prob = float(container.delay_model.predict_proba(aligned_df)[0, 1])
            delay_flag = 1 if delay_prob >= container.delay_threshold else 0

            # 3. Delay regression inference (continuous delay in months)
            predicted_delay_months = float(container.delay_regressor.predict(aligned_df)[0])

            # 4. Authoritative composite risk determination
            overall_risk = compute_overall_risk(
                cost_flag=cost_flag,
                delay_flag=delay_flag,
                cost_probability=cost_prob,
                delay_probability=delay_prob,
            )
        except Exception as exc:
            logger.error("Inference failure for project %s: %s", payload.project_id, exc)
            raise RuntimeError(f"Prediction execution failed: {exc}") from exc

        return PredictResponse(
            project_id=payload.project_id,
            cost_overrun_probability=round(cost_prob, 4),
            cost_overrun_flag=cost_flag,
            cost_overrun_threshold=container.cost_threshold,
            delay_probability=round(delay_prob, 4),
            delay_flag=delay_flag,
            delay_threshold=container.delay_threshold,
            predicted_delay_months=round(predicted_delay_months, 2),
            overall_risk_level=overall_risk,
        )

    @staticmethod
    def predict_project_by_id(project_id: str) -> ProjectPredictionResponse:
        """
        Executes inference for a project in the current inference dataset:
        1. Retrieves project row from cached ProjectService.
        2. Isolates the 36 SAFE_MVP features in exact production schema order.
        3. Excludes metadata columns (project_id, project_name, snapshot_month) from model input.
        4. Runs locked production models and existing risk policy.
        5. Returns ProjectPredictionResponse.
        """
        project_service = get_project_service()
        record = project_service.get_project(project_id)
        container = get_model_container()

        # Extract only the 36 SAFE_MVP model features, preserving None for NaNs
        features_dict = {}
        for col in container.feature_names:
            val = record.get(col)
            features_dict[col] = None if pd.isna(val) else val

        row_df = pd.DataFrame([features_dict])
        aligned_df = row_df[container.feature_names]

        try:
            # 1. Cost overrun inference
            cost_prob = float(container.cost_overrun_model.predict_proba(aligned_df)[0, 1])
            cost_flag = 1 if cost_prob >= container.cost_threshold else 0

            # 2. Delay classification inference
            delay_prob = float(container.delay_model.predict_proba(aligned_df)[0, 1])
            delay_flag = 1 if delay_prob >= container.delay_threshold else 0

            # 3. Delay regression inference (continuous delay in months)
            predicted_delay_months = float(container.delay_regressor.predict(aligned_df)[0])

            # 4. Authoritative composite risk determination
            overall_risk = compute_overall_risk(
                cost_flag=cost_flag,
                delay_flag=delay_flag,
                cost_probability=cost_prob,
                delay_probability=delay_prob,
            )

            # Categorical risk tiers aligned with threshold policy
            cost_overrun_risk = "HIGH" if cost_flag == 1 else ("MEDIUM" if cost_prob >= 0.30 else "LOW")
            schedule_delay_risk = "HIGH" if delay_flag == 1 else ("MEDIUM" if delay_prob >= 0.30 else "LOW")
        except Exception as exc:
            logger.error("Inference failure for project %s: %s", project_id, exc)
            raise RuntimeError(f"Prediction execution failed: {exc}") from exc

        return ProjectPredictionResponse(
            project_id=str(record["project_id"]),
            project_name=str(record["project_name"]),
            snapshot_month=str(record["snapshot_month"]),
            overall_risk=overall_risk,
            cost_overrun_probability=round(cost_prob, 4),
            cost_overrun_risk=cost_overrun_risk,
            schedule_delay_probability=round(delay_prob, 4),
            schedule_delay_risk=schedule_delay_risk,
            predicted_delay_months=round(predicted_delay_months, 2),
        )

