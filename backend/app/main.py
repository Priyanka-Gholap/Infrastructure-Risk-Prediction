import logging
from contextlib import asynccontextmanager
from typing import Annotated, Any

from fastapi import FastAPI, HTTPException, Path, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.config import settings
from backend.app.model_loader import get_model_container, load_models
from backend.app.predictor import PredictorService
from backend.app.project_service import (
    DatasetUnavailableError,
    ProjectNotFoundError,
    get_project_service,
)
from backend.app.explainability import ExplainabilityService
from backend.app.schemas import (
    HealthResponse,
    PredictRequest,
    PredictResponse,
    ProjectLookupItem,
    ProjectPredictionResponse,
    ProjectExplainabilityResponse,
)

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("sih26103.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager that loads and validates ML pipelines,
    current inference dataset, and pre-caches SHAP TreeExplainer instances at startup.
    Fails fast if any model, schema artifact, or dataset is invalid.
    """
    logger.info("Initializing SIH26103 Inference Service...")
    try:
        load_models()
        get_project_service().load_dataset()
        ExplainabilityService.get_instance()
        logger.info("Inference Service ready. Production models, schemas, dataset, and explainability verified.")
    except Exception as exc:
        logger.critical("Failed to initialize service during startup: %s", exc)
        raise exc
    yield
    logger.info("Shutting down SIH26103 Inference Service.")


app = FastAPI(
    title="SIH26103 Infrastructure Risk Prediction API",
    description=(
        "AI-Powered Predictive Analytics & Early Warning System for Infrastructure Project Monitoring. "
        "Exposes inference endpoints for locked production ML models evaluating cost overrun and delay risk."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS for development frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Returns clean, standardized validation error messages without leaking internal traces.
    """
    errors = []
    for err in exc.errors():
        field_path = " -> ".join(str(loc) for loc in err.get("loc", []))
        errors.append({
            "field": field_path,
            "message": err.get("msg"),
            "type": err.get("type"),
        })
    logger.warning("Request validation error on %s: %s", request.url.path, errors)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "error": "Validation Error",
            "message": "Input payload failed schema validation.",
            "details": errors,
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """
    Catches unexpected internal exceptions and returns a generic 500 error
    to avoid exposing stack traces to external clients.
    """
    logger.exception("Unhandled server error processing request to %s", request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred while processing the request.",
        },
    )


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health & Model Readiness Probe",
    tags=["System"],
)
async def health_check():
    """
    Verifies that the API service is operational and that all production
    ML models are successfully loaded in memory.
    """
    try:
        container = get_model_container()
        models_ready = container.is_loaded
    except Exception:
        models_ready = False

    if not models_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Production models are not loaded.",
        )

    return HealthResponse(status="ok", models_loaded=True)


@app.get(
    "/model-info",
    summary="Model Metadata & Governance Info",
    tags=["Models"],
)
async def model_info() -> dict[str, Any]:
    """
    Exposes model metadata, operating thresholds, evaluation metrics, and
    locked feature schema details directly from model_metadata.json.
    """
    try:
        container = get_model_container()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Models not initialized.",
        ) from exc

    metadata = container.metadata
    return {
        "pipeline_stage": metadata.get("pipeline_stage"),
        "trained_date": metadata.get("trained_date"),
        "feature_count": len(container.feature_names),
        "operating_thresholds": {
            "cost_overrun_threshold": container.cost_threshold,
            "delay_threshold": container.delay_threshold,
        },
        "safe_mvp_features": container.feature_names,
        "n_training_samples": metadata.get("n_training_samples"),
        "n_test_samples": metadata.get("n_test_samples"),
        "models": metadata.get("models"),
    }


@app.post(
    "/predict",
    response_model=PredictResponse,
    summary="Generate Project Risk Prediction",
    tags=["Inference"],
)
async def predict_project_risk(payload: PredictRequest) -> PredictResponse:
    """
    Evaluates a single infrastructure project snapshot using the locked 36 SAFE_MVP features:
    1. Validates schema and data types.
    2. Runs Cost Overrun Classifier (RandomForestClassifier, threshold 0.40).
    3. Runs Delay Classifier (RandomForestClassifier, threshold 0.50).
    4. Runs Delay Regressor (RandomForestRegressor, months delayed).
    5. Determines composite risk tier (CRITICAL / HIGH / MEDIUM / LOW).
    """
    try:
        return PredictorService.predict(payload)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@app.get(
    "/projects",
    response_model=list[ProjectLookupItem],
    summary="List and Search Currently Monitored Projects",
    tags=["Projects"],
    responses={
        200: {
            "description": "List of project summaries matching search criteria.",
        },
        503: {
            "description": "Current inference dataset is unavailable on server.",
        },
    },
)
async def list_projects(
    search: str | None = Query(
        default=None,
        description="Optional filter matching project_id or project_name (case-insensitive).",
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=500,
        description="Maximum number of projects to return (default 50, max 500).",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of initial records to skip for pagination (default 0).",
    ),
) -> list[ProjectLookupItem]:
    """
    Retrieves currently monitored infrastructure projects from the current inference dataset.
    Supports substring search by project_id or project_name and deterministic pagination.
    Does not expose the 36-feature vector or model predictions.
    """
    try:
        service = get_project_service()
        return service.search_projects(search=search, limit=limit, offset=offset)
    except DatasetUnavailableError as exc:
        logger.error("Dataset unavailable during /projects request: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Current inference dataset is unavailable on server.",
        ) from exc


@app.post(
    "/projects/{project_id}/predict",
    response_model=ProjectPredictionResponse,
    summary="Predict Risk for a Current Monitored Project",
    tags=["Projects", "Inference"],
    responses={
        200: {
            "description": "Risk prediction successfully generated for monitored project.",
        },
        404: {
            "description": "Project ID not found in current inference dataset.",
        },
        422: {
            "description": "Validation error on project ID parameter.",
        },
        503: {
            "description": "Current inference dataset or models unavailable.",
        },
    },
)
async def predict_monitored_project(
    project_id: Annotated[
        str,
        Path(
            min_length=1,
            max_length=50,
            description="Official unique MoSPI Project ID identifier.",
        ),
    ],
) -> ProjectPredictionResponse:
    """
    Evaluates risk for a currently monitored project identified by project_id:
    1. Validates project_id.
    2. Retrieves the latest observation snapshot from current_inference_dataset.csv.
    3. Extracts the 36 SAFE_MVP production features in exact schema order.
    4. Evaluates the 3 locked ML models (cost overrun classifier, delay classifier, delay regressor).
    5. Applies the authoritative 4-tier composite risk policy.
    6. Returns clean, frontend-friendly risk probabilities and predicted delay.
    """
    clean_id = project_id.strip()
    if not clean_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Project ID cannot be empty or whitespace.",
        )

    try:
        return PredictorService.predict_project_by_id(clean_id)
    except ProjectNotFoundError as exc:
        logger.warning("Project lookup failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{clean_id}' was not found in the current inference dataset.",
        ) from exc
    except DatasetUnavailableError as exc:
        logger.error("Dataset unavailable during prediction for %s: %s", clean_id, exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Current inference dataset is unavailable on server.",
        ) from exc
    except RuntimeError as exc:
        logger.error("Prediction failed for project %s: %s", clean_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@app.get(
    "/projects/{project_id}/explain",
    response_model=ProjectExplainabilityResponse,
    summary="Generate Model Explainability Drivers for a Monitored Project",
    tags=["Projects", "Explainability"],
    responses={
        200: {
            "description": "Mathematically reconciled feature attributions successfully generated.",
        },
        404: {
            "description": "Project ID not found in current inference dataset.",
        },
        422: {
            "description": "Validation error on project ID parameter.",
        },
        503: {
            "description": "Current inference dataset or models unavailable.",
        },
    },
)
async def explain_monitored_project(
    project_id: Annotated[
        str,
        Path(
            min_length=1,
            max_length=50,
            description="Official unique MoSPI Project ID identifier.",
        ),
    ],
    top_k: int = Query(
        default=5,
        ge=1,
        le=36,
        description="Number of top drivers to return per model (default 5, max 36).",
    ),
) -> ProjectExplainabilityResponse:
    """
    Computes mathematically reconciled feature attributions using SHAP TreeExplainer
    for the project identified by project_id across all 3 production models.
    Does NOT modify project predictions or risk classifications.
    """
    clean_id = project_id.strip()
    if not clean_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Project ID cannot be empty or whitespace.",
        )

    try:
        service = ExplainabilityService.get_instance()
        return service.explain_project(clean_id, top_k=top_k)
    except ProjectNotFoundError as exc:
        logger.warning("Project lookup failed for explainability: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{clean_id}' was not found in the current inference dataset.",
        ) from exc
    except DatasetUnavailableError as exc:
        logger.error("Dataset unavailable during explainability for %s: %s", clean_id, exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Current inference dataset is unavailable on server.",
        ) from exc
    except Exception as exc:
        logger.error("Explainability generation failed for project %s: %s", clean_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Explainability computation failed: {exc}",
        ) from exc


