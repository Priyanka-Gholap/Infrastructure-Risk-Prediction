import pytest
from unittest.mock import patch, MagicMock
from backend.app.model_loader import load_models

def test_missing_model_file_raises(tmp_path):
    """Missing model artifact must raise FileNotFoundError on startup."""
    with patch("backend.app.model_loader.settings.MODELS_DIR", tmp_path):
        with pytest.raises(FileNotFoundError, match="Startup Failure: Required production artifact"):
            load_models()


def test_metadata_threshold_conflict_raises():
    """Conflicting operating threshold in metadata must raise RuntimeError."""
    corrupted_metadata = {
        "pipeline_stage": "Step 4",
        "models": {
            "cost_overrun": {"operating_threshold": 0.50},  # Conflicted: should be 0.40
            "delay": {"operating_threshold": 0.50},
        },
    }
    with patch("json.load", return_value=corrupted_metadata):
        with pytest.raises(RuntimeError, match="conflicts with locked production threshold"):
            load_models()


def test_feature_mismatch_raises():
    """Mismatch between production_feature_schema.csv and model feature_names_in_ must raise RuntimeError."""
    mock_model = MagicMock()
    mock_model.feature_names_in_ = ["feature_a", "feature_b"]  # Not matching 36 features

    with patch("joblib.load", return_value=mock_model):
        with pytest.raises(RuntimeError, match="Startup Failure"):
            load_models()
