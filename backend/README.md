# SIH26103 Predictive Analytics & Early Warning Inference Backend

## 1. Overview & Purpose
This backend service provides the production inference API for **SIH Problem Statement 26103 — AI-Powered Predictive Analytics & Early Warning System for Infrastructure Project Monitoring**.

The service loads three serialized, locked Scikit-Learn pipelines (`cost_overrun_model.joblib`, `delay_model.joblib`, `delay_regressor.joblib`) once at application startup, performs strict Pydantic v2 schema validation against the authoritative production feature contracts, and evaluates infrastructure project snapshots for early warning risk.

### Scope Boundaries (Step 6A)
- **Inference Only:** The backend performs real-time ML inference. It does **not** perform model training or retraining.
- **Engineered Input Expected:** The `/predict` endpoint expects the **36 locked `SAFE_MVP` features already engineered**. The backend does **not** extract features from raw PDF flash reports.
- **No Database / Frontend:** Database persistence, background batch pipelines, and React frontend integration are deferred to subsequent project steps.

---

## 2. Environment Setup (Windows-Friendly)

### Prerequisites
- Python 3.11, 3.12, or 3.13 installed.
- PowerShell or Command Prompt.

### Step 1: Create a Virtual Environment
From the project root (`SIH26103-Infrastructure-Risk-Prediction/`):

```powershell
# In PowerShell or Command Prompt
python -m venv venv
```

### Step 2: Activate the Virtual Environment
```powershell
# In Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Or in Windows Command Prompt (cmd.exe):
.\venv\Scripts\activate.bat
```

### Step 3: Install Required Dependencies
```powershell
pip install -r backend/requirements.txt
```

---

## 3. Starting the Backend Service

Run Uvicorn from the project root:

```powershell
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Or from inside the `backend/` directory:

```powershell
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The application will start, load the ML models, verify the schemas and thresholds, and bind to `http://127.0.0.1:8000`.

---

## 4. Interactive API Documentation

Once the server is running, explore the interactive documentation:
- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **OpenAPI JSON Contract:** [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

---

## 5. Endpoints Reference

### 1. `GET /health`
Verifies service availability and confirms that all three production models are loaded in memory.

**Sample Response:**
```json
{
  "status": "ok",
  "models_loaded": true
}
```

### 2. `GET /model-info`
Returns authoritative metadata directly from `ml/metadata/model_metadata.json`, including locked operating thresholds, model architectures, and evaluation metrics.

**Sample Response:**
```json
{
  "pipeline_stage": "Step 4",
  "trained_date": "2026-09-05",
  "feature_count": 36,
  "operating_thresholds": {
    "cost_overrun_threshold": 0.40,
    "delay_threshold": 0.50
  },
  "safe_mvp_features": [
    "ministry",
    "sector",
    "implementing_agency",
    "state",
    "original_cost",
    "approval_to_start_months",
    "..."
  ],
  "n_training_samples": 143,
  "n_test_samples": 36,
  "models": { ... }
}
```

### 3. `POST /predict`
Evaluates a single project snapshot against the 36 locked `SAFE_MVP` features.

**Authoritative Thresholds & Composite Risk Policy:**
- **Cost Threshold:** $\tau = 0.40$ (alert triggered if cost probability $\ge 0.40$).
- **Delay Threshold:** $\tau = 0.50$ (alert triggered if delay probability $\ge 0.50$).
- **Deterministic Composite Risk Tier:**
  - `CRITICAL`: Both cost and delay flagged.
  - `HIGH`: Either cost or delay flagged.
  - `MEDIUM`: Either model probability $\ge 0.30$.
  - `LOW`: Otherwise.

**Sample Request Body:**
```json
{
  "project_id": "400234",
  "project_name": "Third Railway Line between Patratu-Sonnagar [291 kms]",
  "snapshot_month": "2026-04",
  "features": {
    "original_cost": 8975.0,
    "approval_to_start_months": 21.0,
    "cumulative_expenditure": 4798.96,
    "expenditure_percent_of_original_cost": 53.4703,
    "monthly_expenditure_change": null,
    "monthly_expenditure_growth_pct": null,
    "physical_progress_pct": 90.0,
    "monthly_progress_change": null,
    "progress_growth_rate": null,
    "planned_duration_months": 91.0,
    "elapsed_months": 88.0,
    "remaining_planned_months": 3.0,
    "elapsed_duration_ratio": 0.967,
    "is_past_original_doc": 0.0,
    "efficiency_gap": 36.5297,
    "cost_physical_ratio": 0.5941,
    "expected_progress_pct": 96.7033,
    "progress_gap_pct_points": -6.7033,
    "months_since_first_observation": 0.0,
    "observation_count_to_date": 1.0,
    "physical_progress_1_month_change": null,
    "physical_progress_2_month_change": null,
    "expenditure_1_month_change": null,
    "expenditure_2_month_change": null,
    "progress_trend_slope": null,
    "expenditure_trend_slope": null,
    "negative_expenditure_flag": 0,
    "missing_previous_month_flag": 1,
    "invalid_duration_flag": 0,
    "past_original_doc_flag": 0,
    "missing_key_date_flag": 0,
    "suspicious_value_flag": 0,
    "ministry": "Ministry of Railways",
    "sector": "Railways",
    "implementing_agency": "RVNL - II",
    "state": "Multi-States\n(Bihar, Jharkhand)"
  }
}
```

**Sample Response Body (Conforming to `ml/schemas/inference_output_schema.json`):**
```json
{
  "project_id": "400234",
  "cost_overrun_probability": 0.2388,
  "cost_overrun_flag": 0,
  "cost_overrun_threshold": 0.4,
  "delay_probability": 0.1615,
  "delay_flag": 0,
  "delay_threshold": 0.5,
  "predicted_delay_months": -3.83,
  "overall_risk_level": "LOW"
}
```

---

## 6. Running Tests

Run the complete test suite using pytest:

```powershell
python -m pytest backend/tests -v
```

All 23 automated tests cover:
- Health and model readiness (`/health`)
- Model metadata retrieval and schema compatibility (`/model-info`)
- Valid inference on low-risk and high-risk projects (`/predict`)
- Strict schema validation (missing required fields, bad datatypes, invalid flag enums, unexpected fields)
- Operating decision threshold boundaries ($\tau=0.40$, $\tau=0.50$)
- Feature-order invariance
- Authoritative 4-tier composite risk policy (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`)
- Startup fail-fast validation (missing files, conflicting thresholds, misaligned feature sets)
