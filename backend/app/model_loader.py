import json
import logging
from dataclasses import dataclass
from typing import Any
import joblib
import pandas as pd

from backend.app.config import settings

logger = logging.getLogger("sih26103.model_loader")

@dataclass
class ModelContainer:
    """Holds loaded estimators, metadata, and production configuration."""
    cost_overrun_model: Any
    delay_model: Any
    delay_regressor: Any
    metadata: dict[str, Any]
    feature_names: list[str]
    cost_threshold: float
    delay_threshold: float
    is_loaded: bool = True


_container: ModelContainer | None = None


def load_models() -> ModelContainer:
    """
    Loads all three production Scikit-Learn pipelines and metadata once at startup.
    Performs rigorous startup checks:
    1. Ensures all artifact files exist.
    2. Validates that authoritative metadata thresholds match locked constants (0.40 / 0.50).
    3. Validates that production_feature_schema.csv columns exactly match model.feature_names_in_
       across all three models.
    4. Fails fast with clear exceptions if any discrepancy is detected.
    """
    global _container

    cost_path = settings.MODELS_DIR / "cost_overrun_model.joblib"
    delay_path = settings.MODELS_DIR / "delay_model.joblib"
    reg_path = settings.MODELS_DIR / "delay_regressor.joblib"
    meta_path = settings.METADATA_DIR / "model_metadata.json"
    schema_path = settings.SCHEMAS_DIR / "production_feature_schema.csv"

    # 1. Existence checks
    for path, label in [
        (cost_path, "Cost Overrun Model"),
        (delay_path, "Delay Model"),
        (reg_path, "Delay Regressor"),
        (meta_path, "Model Metadata JSON"),
        (schema_path, "Production Feature Schema CSV"),
    ]:
        if not path.exists():
            raise FileNotFoundError(
                f"Startup Failure: Required production artifact [{label}] not found at '{path}'."
            )

    logger.info("Loading production ML model pipelines...")
    try:
        cost_model = joblib.load(cost_path)
        delay_model = joblib.load(delay_path)
        delay_regressor = joblib.load(reg_path)
    except Exception as e:
        raise RuntimeError(f"Startup Failure: Error deserializing joblib model pipelines: {e}") from e

    # 2. Metadata & Threshold validation
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
    except Exception as e:
        raise RuntimeError(f"Startup Failure: Error reading model metadata JSON: {e}") from e

    meta_cost_thresh = metadata.get("models", {}).get("cost_overrun", {}).get("operating_threshold")
    meta_delay_thresh = metadata.get("models", {}).get("delay", {}).get("operating_threshold")

    if meta_cost_thresh != settings.LOCKED_COST_THRESHOLD:
        raise RuntimeError(
            f"Startup Failure: Cost threshold in metadata ({meta_cost_thresh}) conflicts "
            f"with locked production threshold ({settings.LOCKED_COST_THRESHOLD})."
        )
    if meta_delay_thresh != settings.LOCKED_DELAY_THRESHOLD:
        raise RuntimeError(
            f"Startup Failure: Delay threshold in metadata ({meta_delay_thresh}) conflicts "
            f"with locked production threshold ({settings.LOCKED_DELAY_THRESHOLD})."
        )

    # 3. Feature alignment validation across models and CSV schema
    m1_features = list(cost_model.feature_names_in_)
    m2_features = list(delay_model.feature_names_in_)
    m3_features = list(delay_regressor.feature_names_in_)

    if m1_features != m2_features or m1_features != m3_features:
        raise RuntimeError(
            "Startup Failure: Inconsistent feature_names_in_ across serialized models.\n"
            f"Cost: {m1_features}\nDelay: {m2_features}\nRegressor: {m3_features}"
        )

    try:
        csv_df = pd.read_csv(schema_path)
        csv_features = list(csv_df["feature_name"])
    except Exception as e:
        raise RuntimeError(f"Startup Failure: Error reading production feature schema CSV: {e}") from e

    if len(csv_features) != 36:
        raise RuntimeError(
            f"Startup Failure: Expected 36 features in production_feature_schema.csv, found {len(csv_features)}."
        )

    if set(csv_features) != set(m1_features):
        missing_in_model = set(csv_features) - set(m1_features)
        missing_in_csv = set(m1_features) - set(csv_features)
        raise RuntimeError(
            "Startup Failure: Feature set mismatch between production_feature_schema.csv and model.feature_names_in_!\n"
            f"Missing in model: {missing_in_model}\nMissing in schema CSV: {missing_in_csv}"
        )

    logger.info(
        "Successfully verified and loaded all 3 models with 36 locked SAFE_MVP features. "
        "Thresholds locked: Cost=%.2f, Delay=%.2f",
        settings.LOCKED_COST_THRESHOLD,
        settings.LOCKED_DELAY_THRESHOLD,
    )

    _container = ModelContainer(
        cost_overrun_model=cost_model,
        delay_model=delay_model,
        delay_regressor=delay_regressor,
        metadata=metadata,
        feature_names=m1_features,
        cost_threshold=settings.LOCKED_COST_THRESHOLD,
        delay_threshold=settings.LOCKED_DELAY_THRESHOLD,
        is_loaded=True,
    )
    return _container


def get_model_container() -> ModelContainer:
    """Returns the loaded ModelContainer singleton."""
    global _container
    if _container is None or not _container.is_loaded:
        raise RuntimeError("Model container is not loaded. Models must be initialized at startup.")
    return _container
