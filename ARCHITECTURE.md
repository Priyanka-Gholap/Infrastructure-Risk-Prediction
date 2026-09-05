# System Architecture Specification

## 1. System Overview & Architecture Diagram
The architecture for **SIH26103** is designed as a modular, decoupled, lightweight web-based predictive analytics platform. It cleanly separates presentation, API orchestration, ML inference, and data persistence to guarantee maintainability, testability, and offline demo reliability.

```mermaid
graph TB
    subgraph Client ["Frontend Presentation Layer (React + TypeScript)"]
        UI_Dash["Executive Dashboard<br/>(Recharts Summary)"]
        UI_Table["Project Explorer<br/>(Filterable Grid)"]
        UI_Detail["Project Inspector<br/>(S-Curve & Gauges)"]
        UI_Sim["What-If Simulator [P1]<br/>(High-Value Interactive Enhancement)"]
    end

    subgraph Gateway ["API & Orchestration Layer (FastAPI)"]
        API_Router["REST API Endpoints<br/>(/api/v1/...)"]
        Val_Engine["Validation Engine<br/>(Pydantic v2 Contracts)"]
    end

    subgraph Analytics ["Analytics & ML Inference Engine"]
        FE_Pipeline["Feature Engineering<br/>(Pandas / NumPy Transformers)"]
        Model_Delay["Delay Risk Model<br/>(Scikit-Learn / XGBoost)"]
        Model_Cost["Cost Overrun Model<br/>(Scikit-Learn / XGBoost)"]
        Synth_Engine["Composite Risk Synthesizer"]
        XAI_Engine["Explainability Engine<br/>(TreeSHAP Driver Attribution)"]
    end

    subgraph Storage ["Persistence Layer (SQLite Primary)"]
        DB_ORM["SQLAlchemy ORM"]
        DB_Storage[("SQLite (Local MVP Storage)<br/>[PostgreSQL as Optional Future Path]")]
    end

    UI_Dash & UI_Table & UI_Detail & UI_Sim <-->|JSON / HTTP REST| API_Router
    API_Router --> Val_Engine
    Val_Engine --> FE_Pipeline
    FE_Pipeline --> Model_Delay & Model_Cost
    Model_Delay & Model_Cost --> Synth_Engine
    Synth_Engine --> XAI_Engine
    XAI_Engine --> API_Router
    API_Router <--> DB_ORM
    DB_ORM <--> DB_Storage
```

---

## 2. Layer & Component Breakdown

### 2.1 Frontend Presentation Layer (React + TypeScript)
- **Role:** Deliver a high-impact, responsive, government-executive grade dashboard.
- **Core MVP Modules (P0):**
  - `ExecutiveSummary`: High-level portfolio KPI cards (monitored capital, delayed projects tally, cost overrun exposure, portfolio risk breakdown).
  - `ProjectExplorer`: Searchable, filterable data grid with sector tags, state filters, and risk status pills.
  - `ProjectInspector`: In-depth analytical view for a selected project displaying milestone timeline, EVM curves, risk score gauges, and top explainability drivers.
- **High-Value Enhancement Module (P1):**
  - `WhatIfSimulator`: Interactive parameter adjustment sliders enabling evaluators to simulate scenario changes (e.g. progress catch-up, clearance resolution) and trigger live API re-scoring.
  - *Note:* The core MVP dashboard functions completely and effectively without requiring the What-If simulator.
- **Tech Choices (Provisional):** React 18, TypeScript, Tailwind CSS, Recharts, Lucide Icons.

### 2.2 Backend API Layer (FastAPI + Python)
- **Role:** Expose standardized, secure, type-safe REST endpoints.
- **Key Endpoints:**
  - `GET /api/v1/health`: System health and model readiness probe.
  - `GET /api/v1/projects`: Retrieve paginated/filtered list of monitored projects.
  - `GET /api/v1/projects/{id}`: Detailed metadata, history, and risk assessment for a specific project.
  - `POST /api/v1/predict`: Single-project on-the-fly inference and explainability evaluation.
  - `POST /api/v1/predict/batch`: Ingestion of multiple project records (CSV/JSON upload).
  - `GET /api/v1/portfolio/summary`: Aggregated portfolio analytics and alert distribution.
- **Validation:** Strict validation enforced via Pydantic v2 schemas for all request/response contracts.

### 2.3 Analytics & ML Inference Engine
- **Role:** Execute deterministic feature transformations, run pre-trained ML models, compute composite risk index, and generate explainability breakdowns.
- **Subcomponents:**
  1. `FeatureTransformer`: Computes schedule slippage, cost burn ratio, time-elapsed ratio, and clearance bottlenecks.
  2. `PredictorService`: Loads serialized model artifacts (`.joblib` / ONNX) and executes inference.
  3. `ExplainabilityService`: Calculates SHAP values and translates top mathematical drivers into human-readable governance summaries.
  4. `AlertEngine`: Maps composite scores into standardized alert tiers (`Normal`, `Watchlist`, `High Alert`, `Critical Red Flag`) with prescriptive recommendations.

### 2.4 Persistence Layer (SQLAlchemy + SQLite Primary)
- **Role:** Persist project records, audit history, milestone logs, and benchmark presets.
- **Strategic Decision:**
  - **Initial MVP Development & Demo:** **SQLite** is preferred as the simplest, self-contained local persistence option, guaranteeing zero-configuration and zero-network-failure execution during evaluation.
  - **Future / Production Path:** PostgreSQL is retained as an optional migration path via SQLAlchemy's abstraction, but Docker/PostgreSQL complexity will not be introduced before actually needed.

---

## 3. End-to-End Data Flow Sequence

1. **Input Submission:**
   - User inputs parameters via Web Form or selects a Preloaded Project from the dashboard.
2. **Payload Validation:**
   - FastAPI receives JSON; Pydantic validates data types, date constraints, and non-negative financial values.
3. **Feature Generation:**
   - Feature transformer computes temporal durations, progress-to-time ratios, and cost burn metrics.
4. **Predictive Scoring:**
   - Model inference executes for Delay Risk and Cost Overrun Risk.
   - Composite risk index is synthesized.
5. **Explainability Extraction:**
   - SHAP TreeExplainer attributes local contributions; top 3-5 drivers are isolated.
6. **Alert Categorization:**
   - Alert threshold rules assign risk level badge and generate actionable mitigation guidance.
7. **Response Delivery:**
   - Unified JSON payload returned to React frontend; UI components update dynamically with animations and color-coded risk indicators.

---

## 4. Planned Project Repository Structure

```
SIH26103-Infrastructure-Risk-Prediction/
├── .gitignore
├── README.md
├── PROJECT_CONTEXT.md
├── MVP_REQUIREMENTS.md
├── DATA_SCHEMA.md
├── ML_PLAN.md
├── ARCHITECTURE.md
├── DEVELOPMENT_LOG.md
│
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI routers & endpoints
│   │   ├── core/            # Config, security, logging
│   │   ├── models/          # SQLAlchemy database models (SQLite default)
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── services/        # Business logic & orchestration
│   │   ├── ml/              # Model loaders, transformers, SHAP explainers
│   │   └── main.py          # Application entrypoint
│   ├── tests/               # Backend unit and integration tests
│   └── requirements.txt     # Python backend dependencies
│
├── frontend/
│   ├── src/
│   │   ├── assets/          # Icons, logos, styles
│   │   ├── components/      # UI components (cards, tables, charts)
│   │   ├── pages/           # Dashboard, Project Detail, Simulator (P1)
│   │   ├── services/        # API client bindings
│   │   ├── types/           # TypeScript interfaces conforming to backend schemas
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── ml_research/             # Offline data preparation, training notebooks, benchmarks
│   ├── data/                # Evaluated raw & processed project datasets
│   ├── notebooks/           # Exploratory data analysis & model tuning
│   └── artifacts/           # Serialized trained models (.joblib)
│
└── docker/                  # Optional deployment configs (for future containerization)
```

---

## 5. Architectural Quality Attributes & Pragmatic Decisions

| Attribute | Architectural Tactic |
|---|---|
| **Simplicity & Zero-Config** | SQLite eliminates database daemon setup, port conflicts, and container networking issues during live hackathon demos. |
| **Determinism** | Model inference uses frozen serialized pipelines with fixed random seeds; identical inputs consistently produce identical risk outputs. |
| **Decoupling** | Strict Pydantic contracts ensure frontend and backend can be tested and developed independently with mocked API contracts. |
| **Fault Isolation** | If the ML inference engine encounters an edge case, graceful fallback to standard EVM heuristic scoring prevents frontend crashes. |
