import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Base directory for backend and project root
BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent

class Settings:
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # CORS configuration - default allowed localhost and 127.0.0.1 ports for React / Vite
    _raw_cors = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173",
    )
    CORS_ORIGINS: list[str] = [origin.strip() for origin in _raw_cors.split(",") if origin.strip()]

    # ML Artifact directory resolution (robust relative path fallback)
    _models_dir_env = os.getenv("MODELS_DIR")
    MODELS_DIR: Path = (
        Path(_models_dir_env).resolve()
        if _models_dir_env and Path(_models_dir_env).is_absolute()
        else (BACKEND_DIR / _models_dir_env).resolve()
        if _models_dir_env
        else (PROJECT_ROOT / "ml" / "models").resolve()
    )

    _schemas_dir_env = os.getenv("SCHEMAS_DIR")
    SCHEMAS_DIR: Path = (
        Path(_schemas_dir_env).resolve()
        if _schemas_dir_env and Path(_schemas_dir_env).is_absolute()
        else (BACKEND_DIR / _schemas_dir_env).resolve()
        if _schemas_dir_env
        else (PROJECT_ROOT / "ml" / "schemas").resolve()
    )

    _metadata_dir_env = os.getenv("METADATA_DIR")
    METADATA_DIR: Path = (
        Path(_metadata_dir_env).resolve()
        if _metadata_dir_env and Path(_metadata_dir_env).is_absolute()
        else (BACKEND_DIR / _metadata_dir_env).resolve()
        if _metadata_dir_env
        else (PROJECT_ROOT / "ml" / "metadata").resolve()
    )

    # Current inference dataset resolution (produced by Step 6B)
    _dataset_path_env = os.getenv("CURRENT_INFERENCE_DATASET_PATH")
    CURRENT_INFERENCE_DATASET_PATH: Path = (
        Path(_dataset_path_env).resolve()
        if _dataset_path_env and Path(_dataset_path_env).is_absolute()
        else (BACKEND_DIR / _dataset_path_env).resolve()
        if _dataset_path_env
        else (PROJECT_ROOT / "current_inference_dataset.csv").resolve()
    )

    # Locked production operating decision thresholds
    # Sourced authoritatively from ml/metadata/model_metadata.json & ml/schemas/inference_output_schema.json
    # These are locked constants and MUST NOT be freely overridden via environment variables.
    LOCKED_COST_THRESHOLD: float = 0.40
    LOCKED_DELAY_THRESHOLD: float = 0.50

settings = Settings()
