# SIH26103 – AI-Powered Predictive Analytics & Early Warning System for Infrastructure Project Monitoring

[![Hackathon](https://img.shields.io/badge/Initiative-Smart_India_Hackathon_2026-orange.svg)](https://www.sih.gov.in/)
[![Problem Statement](https://img.shields.io/badge/Problem_ID-SIH26103-blue.svg)](#)
[![Backend Status](https://img.shields.io/badge/FastAPI-59%2F59_Tests_Passing-brightgreen.svg)](#)
[![Frontend Status](https://img.shields.io/badge/React_18-14%2F14_Tests_Passing-brightgreen.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](#)
[![SHAP](https://img.shields.io/badge/SHAP-0.52.0_Locked-blueviolet.svg)](#)

> **Predictive intelligence, multi-model risk classification, and Lundberg TreeSHAP root-cause explainability for major infrastructure undertakings, forecasting budget escalations and deadline slippages before critical milestones lapse.**

---

## 1. Problem Statement & Hackathon Context

Major public infrastructure undertakings frequently encounter cascading delays and budget escalations due to late detection of operational distress signals (e.g., land acquisition bottlenecks, expenditure divergence, milestone slippage).

- **Initiative**: Smart India Hackathon (SIH) 2026
- **Problem Statement ID**: **SIH26103**
- **Title**: *AI-Powered Predictive Analytics & Early Warning System for Infrastructure Project Monitoring*
- **Core Objective**: Transform static project-monitoring indicators into **actionable predictive early warnings** with quantifiable, mathematically grounded risk drivers, providing decision-makers with the foresight needed for proactive course-correction.

---

## 2. Ministry & IPMD Monitoring Context

The system models empirical infrastructure monitoring data sourced from the **Ministry of Statistics and Programme Implementation (MoSPI)** and the **Infrastructure and Project Monitoring Division (IPMD)**:

- **Source Lineage**: Standardized MoSPI/IPMD monthly project monitoring reports (**Table 6: Ongoing Projects**, capturing 14,573 project-month observations from Dec 2025 through Jul 2026).
- **Snapshot Architecture**: The production inference dataset (`current_inference_dataset.csv`) isolates the **latest available monthly monitoring snapshot for every unique monitored infrastructure project** (**2,131 unique projects**).
- **Zero-Leakage Ingestion**: Every project snapshot is mapped to the exact 36 production features using purely point-in-time indicators available as of that report month, eliminating target leakage and hindsight bias.

---

## 3. End-to-End System Architecture

```mermaid
flowchart TD
    subgraph DataLayer[Data & Artifact Storage]
        SNAP[current_inference_dataset.csv<br/>2,131 Monitored Snapshots]
        MODELS[ml/models/*.joblib<br/>3 Locked Production Models]
        META[ml/metadata/model_metadata.json<br/>Governance & Hyperparameters]
    end

    subgraph BackendAPI[FastAPI Service :8000]
        APP[FastAPI Engine - lifespan startup]
        SVC[ProjectService: In-Memory Index O(1)]
        PRED[PredictorService: Multi-Model Inference]
        POL[RiskPolicy: Authoritative 4-Tier Policy]
        SHAP_ENG[ExplainabilityService: TreeExplainer Pre-cached]
    end

    subgraph FrontendApp[React 18 + TypeScript Command Center :5173]
        SEARCH[ProjectSearch & Safe Reference Chips]
        HERO[OverallRiskHero: Composite Tier Badge]
        CARDS[RiskCommandCenter: 3 Decoupled Metric Cards]
        DRAWER[ExplainabilityPanel: Interactive SHAP Attribution]
    end

    SNAP --> SVC
    MODELS --> PRED
    MODELS --> SHAP_ENG
    META --> APP

    SVC --> APP
    PRED --> APP
    POL --> APP
    SHAP_ENG --> APP

    APP <-->|REST API / JSON| FrontendApp
```

The system operates across three decoupled, resilient tiers:
1. **Frontend Command Center**: React 18 with Vite and TypeScript, featuring instant project search across 2,131 projects, one-click canonical evaluation chips, and immediate state hygiene upon project switching.
2. **FastAPI Backend**: Asynchronous REST service validating payloads via Pydantic v2, managing an in-memory project index, and coordinating model execution.
3. **Machine Learning & Explainability Engine**: Scikit-Learn pipelines paired with pre-cached TreeSHAP explainers, computing feature attributions with strict mathematical additivity ($|\text{Gap}| \le 10^{-5}$).

---

## 4. Machine Learning Model Suite Summary

The locked production inference suite employs three dedicated models trained on historical public infrastructure monitoring data:

| Model Artifact | Algorithm | Task Type | Operating Threshold | Function & Governance |
|---|---|---|:---:|---|
| **`cost_overrun_model.joblib`** | `RandomForestClassifier`<br/>(`n_estimators=100`, `max_depth=4`, `class_weight=balanced`) | Binary Classification | **`0.40`** | Forecasts probability of $\ge 10\%$ budget escalation above original sanctioned cost. |
| **`delay_model.joblib`** | `RandomForestClassifier`<br/>(`n_estimators=100`, `max_depth=4`) | Binary Classification | **`0.50`** | Forecasts probability of completion slipping $\ge 60$ days beyond the latest revised deadline. |
| **`delay_regressor.joblib`** | `RandomForestRegressor`<br/>(`n_estimators=100`, `max_depth=6`) | Continuous Regression | *Continuous* | Estimates the expected schedule variance in continuous months relative to original completion baseline. |

---

## 5. 36 SAFE_MVP Feature Schema Summary

All three models evaluate an identical, locked 36-feature vector (`SAFE_MVP`) in strict schema order:

- **Categorical Features (4)**: `ministry`, `sector`, `implementing_agency`, `state`.
- **Financial & Cost Indicators (9)**: `original_cost`, `cumulative_expenditure`, `expenditure_percent_of_original_cost`, `monthly_expenditure_change`, `monthly_expenditure_growth_pct`, `expenditure_1_month_change`, `expenditure_2_month_change`, `expenditure_trend_slope`, `cost_physical_ratio`.
- **Schedule & Duration Indicators (6)**: `approval_to_start_months`, `planned_duration_months`, `elapsed_months`, `remaining_planned_months`, `elapsed_duration_ratio`, `is_past_original_doc`.
- **Physical Progress Indicators (9)**: `physical_progress_pct`, `monthly_progress_change`, `progress_growth_rate`, `expected_progress_pct`, `progress_gap_pct_points`, `efficiency_gap`, `physical_progress_1_month_change`, `physical_progress_2_month_change`, `progress_trend_slope`.
- **Observation History (2)**: `months_since_first_observation`, `observation_count_to_date`.
- **Data Quality & Anomaly Flags (6)**: `negative_expenditure_flag`, `missing_previous_month_flag`, `invalid_duration_flag`, `past_original_doc_flag`, `missing_key_date_flag`, `suspicious_value_flag`.

---

## 6. Cost Overrun Risk Target Definition

- **Locked Ground-Truth Target**:
  $$\text{target\_cost\_overrun\_binary} = \begin{cases} 1 & \text{if } \text{completion\_cost} \ge 1.10 \times \text{original\_cost} \\ 0 & \text{otherwise} \end{cases}$$
- **Meaning**: Predicts whether a project will exceed its original sanctioned budget by **10% or more**.
- **Decision Policy**:
  - **High Risk**: Predicted Probability $\ge 0.40$ (triggers `HIGH` composite risk).
  - **Advisory**: Predicted Probability $\ge 0.30$.
  - **Nominal / Low**: Predicted Probability $< 0.30$.

---

## 7. Schedule Delay Risk Target Definition

- **Locked Ground-Truth Target**:
  $$\text{target\_delay\_binary} = \begin{cases} 1 & \text{if } \text{actual\_completion} \ge \text{latest\_revised\_deadline} + 60 \text{ days} \\ 0 & \text{otherwise} \end{cases}$$
- **Meaning**: Evaluates the binary risk of completing **60 days or more beyond the latest revised deadline** (evaluating revised deadline adherence).
- **Decision Policy**:
  - **High Risk**: Predicted Probability $\ge 0.50$ (triggers `HIGH` composite risk).
  - **Advisory**: Predicted Probability $\ge 0.30$.
  - **Nominal / Low**: Predicted Probability $< 0.30$.

---

## 8. Projected Schedule Variance Definition

- **Continuous Regression Target**:
  $$\text{predicted\_delay\_months} = \text{estimated months beyond original scheduled completion baseline}$$
- **Directionality & Interpretation**:
  - **Positive Values ($> 0$)**: The project is projected to complete behind its original schedule baseline (e.g., `+26.73 months`). Displayed in UI as: `Predicted delay: 26.73 months`.
  - **Negative Values ($< 0$)**: The project is projected to complete ahead of its original schedule baseline (e.g., `-3.83 months`). The UI converts this into clear, human-readable wording: **`Ahead of schedule by 3.83 months`**.
- **Model Integrity Note**: The underlying regression model emits raw unclipped continuous float values; clamping or sign suppression is strictly avoided in the ML pipeline.

---

## 9. Explainability Engine

- **Methodology**: Lundberg TreeSHAP (`shap.TreeExplainer`) pre-cached at backend startup.
- **Additivity & Verification**: Strict mathematical reconciliation guarantees that feature attributions sum to the model's prediction gap relative to the expected base value:
  $$\left| \sum_{j=1}^{36} \phi_j - (f(x) - E[f(x)]) \right| \le 10^{-5}$$
- **Presentation**: Surfaces the top-5 risk drivers per model categorized by directional effect:
  - **Risk-Increasing Factors (Red)**: Indicators actively pushing the project toward overrun or delay.
  - **Risk-Mitigating Factors (Green)**: Positive milestones suppressing risk.
- **Architectural Isolation**: The explainability engine is strictly observational; failure of explainability computation never blocks or alters primary prediction delivery.

---

## 10. Backend Setup & Run Instructions

**Prerequisites**: Python 3.11+ (Python 3.11, 3.12, and 3.13 tested).

```bash
# 1. Install pinned backend dependencies (including locked shap==0.52.0)
pip install -r backend/requirements.txt

# 2. Launch FastAPI service on host 127.0.0.1, port 8000
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

*Verification*:
- Health probe: `http://127.0.0.1:8000/health` returns `{"status": "ok", "models_loaded": true}`.
- Interactive OpenAPI documentation: `http://127.0.0.1:8000/docs`.

---

## 11. Frontend Setup & Run Instructions

**Prerequisites**: Node.js 18+ (Node 20 / 22 tested), npm 9+.

```bash
# 1. Navigate to the frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start local development server
npm run dev
```

*Verification*: Open `http://localhost:5173` or `http://127.0.0.1:5173` in your browser. The connection badge in the header will display **`FastAPI Backend Live`** with a green status indicator.

---

## 12. Comprehensive Verification Suite

Run the full automated test suite and production build:

```bash
# 1. Backend Regression Suite (59/59 tests passing)
python -m pytest backend/tests -v

# 2. Frontend Test Suite (14/14 tests passing)
cd frontend && npm test -- --run
# On Windows PowerShell (if execution policy restricts npm.ps1):
cmd.exe /c npm test -- --run
# Or directly via npx:
npx vitest run

# 3. Frontend Production Build (Zero errors/warnings)
cd frontend && npm run build
```

---

## 13. Fresh-Clone Quickstart Guide

To run the complete system from a clean clone:

```bash
# 1. Clone repository
git clone https://github.com/<org>/SIH26103-Infrastructure-Risk-Prediction.git
cd SIH26103-Infrastructure-Risk-Prediction

# 2. Terminal 1: Setup and start Backend
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

# 3. Terminal 2: Setup and start Frontend
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## 14. Verified API Endpoints Reference

The backend exposes only the following 6 verified routes:

### `GET /health`
- **Summary**: Health & Model Readiness Probe.
- **Response `200 OK`**:
  ```json
  {"status": "ok", "models_loaded": true}
  ```

### `GET /model-info`
- **Summary**: Model Metadata, Metrics, Governance & Feature Schema.
- **Response `200 OK`**: Returns pipeline metadata, 36 feature names, operating thresholds (`cost=0.40`, `delay=0.50`), and cross-validation / test performance metrics.

### `GET /projects`
- **Summary**: Search and paginate monitored infrastructure projects.
- **Query Parameters**:
  - `search` *(optional string)*: Filters by project ID or name (case-insensitive).
  - `limit` *(optional int, default 50, max 500)*.
  - `offset` *(optional int, default 0)*.
- **Response `200 OK`**: Array of project summary items (`project_id`, `project_name`, `snapshot_month`).

### `POST /projects/{project_id}/predict`
- **Summary**: Predict risk for a monitored project by `project_id`.
- **Response `200 OK`**:
  ```json
  {
    "project_id": "400234",
    "project_name": "Third Railway Line between Patratu and Sonnagar [291 kms]",
    "snapshot_month": "2025-12",
    "cost_overrun_probability": 0.2388,
    "cost_overrun_risk_level": "LOW",
    "schedule_delay_probability": 0.1615,
    "schedule_delay_risk_level": "LOW",
    "predicted_delay_months": -3.83,
    "composite_risk_level": "LOW",
    "contributing_factors": ["Normal budget spend", "Long planned duration"],
    "recommendations": ["Nominal Execution — Continue standard monthly monitoring."]
  }
  ```

### `GET /projects/{project_id}/explain`
- **Summary**: Compute SHAP TreeExplainer feature attributions for a project snapshot.
- **Query Parameters**: `top_k` *(optional int, default 5, max 36)*.
- **Response `200 OK`**: Returns baseline values, actual feature values, and top-K positive/negative SHAP attributions for both the cost and schedule delay models.

### `POST /predict`
- **Summary**: Direct inference on a raw 36-feature vector payload (`PredictRequest` -> `PredictResponse`). Used for batch pipelines and automated testing.

---

## 15. Deterministic 3-Project Judge Demo Script

The frontend provides one-click reference chips for 3 verified projects demonstrating distinct operational scenarios:

### 1. Project `400234` — Nominal Low-Risk Execution (`LOW`)
- **Asset**: *Third Railway Line between Patratu and Sonnagar [291 kms]* (Snapshot: `2025-12`, Ministry of Railways / RVNL).
- **Hero Risk**: **`LOW`** (`Nominal Execution — All predictive indicators remain within normal operational tolerance (< 30%)`).
- **Cost Overrun Risk**: **`23.88%`** (LOW, well below 0.30 advisory).
- **Schedule Delay Risk**: **`16.15%`** (LOW, completion $\ge 60$ days beyond revised deadline is unlikely).
- **Projected Schedule Variance**: **`-3.83 months`** (Rendered as: **`Ahead of schedule by 3.83 months`**).
- **Explainability**: Demonstrates that low cumulative expenditure ratio (`53.47%`) and substantial remaining planned buffer suppress overrun risk.

### 2. Project `400161` — Severe Budget Escalation Alert (`HIGH Cost Risk`)
- **Asset**: *PP Project, Pata* (Snapshot: `2026-01`, Ministry of Petroleum & Natural Gas / GAIL).
- **Hero Risk**: **`HIGH`** (`High Priority Alert — Primary decision threshold breached for Cost Overrun (≥ 40%)`).
- **Cost Overrun Risk**: **`72.01%`** (HIGH, breaches the locked 0.40 decision threshold).
- **Schedule Delay Risk**: **`16.08%`** (LOW).
- **Projected Schedule Variance**: **`+26.73 months`** (Rendered as: `Predicted delay: 26.73 months`).
- **Explainability**: Highlights cumulative spend exceeding sanction (`117.84%`) and an adverse cost-to-physical ratio (`1.19`) driving cost escalation.

### 3. Project `400104` — Dual-Target Schedule Distinction (`HIGH Overall Risk`)
- **Asset**: *Punpun Barrage Project* (Snapshot: `2026-03`, Water Resources).
- **Hero Risk**: **`HIGH`** (Driven by cost overrun probability of `52.31%`).
- **Cost Overrun Risk**: **`52.31%`** (HIGH, breaches 0.40 threshold).
- **Schedule Delay Risk (`delay_model.joblib`)**: **`14.51%`** (LOW).
- **Projected Schedule Variance (`delay_regressor.joblib`)**: **`+153.04 months`** (`Predicted delay: 153.04 months` vs original baseline).
- **Judge Evaluation Key**: Illustrates the mathematical distinction between the two schedule targets:
  > *Schedule Delay Risk evaluates the probability of an additional $\ge 60$-day slip beyond the latest revised deadline. Since recent monthly progress change delta indicates stability relative to the revised target, the classifier remains LOW (14.51%). Concurrently, the continuous regressor captures the massive cumulative historical delay (+153.04 months / 12.75 years vs original sanction), and budget overruns trigger an authoritative composite **`HIGH`** rating.*

---

## 16. Limitations & Governance Boundaries

1. **Decision Support Nature**: Predictions and risk classifications are automated decision-support aids designed for prioritization, not automated executive decrees.
2. **Observational Attribution**: SHAP values represent statistical feature contributions within the tree structure of the trained model, not causal proof of real-world physical root causes.
3. **Snapshot Data Horizon**: The current MVP operates on standardized monthly snapshots from MoSPI/IPMD Table 6 (Dec 2025 – Jul 2026). Predictions reflect data recorded as of each snapshot month.
4. **No Synthetic Guarantees**: Model outputs should not be interpreted as absolute guarantees of final project outcomes; they reflect probabilistic early warnings.

---

## 17. Future Technical Roadmap & Team Attribution

### Current MVP (Delivered & Verified)
- 3 locked ML models evaluated on 2,131 real infrastructure projects.
- Sub-50ms REST inference and pre-cached Lundberg TreeSHAP attributions.
- React 18 command center with instant project switching and zero residual state.
- 100% test passing rate across backend (59/59) and frontend (14/14).

### Future Roadmap (Post-Hackathon)
- **Live Automated Ingestion**: Direct API integration with MoSPI / PRAGATI monitoring feeds.
- **Geospatial & Satellite Layers**: Integration with PM GatiShakti National Master Plan GIS spatial layers.
- **Physical Telemetry**: Ingestion of IoT sensor progress feeds from active construction sites.

### Team & License
- **Initiative**: Smart India Hackathon (SIH) 2026 — Problem Statement 26103.
- **License**: MIT License. Open-source research and educational demonstration.
