# SIH26103 – AI-Powered Predictive Analytics & Early Warning System for Infrastructure Project Monitoring

[![Hackathon](https://img.shields.io/badge/Initiative-Smart_India_Hackathon_2026-orange.svg)](https://www.sih.gov.in/)
[![Problem Statement](https://img.shields.io/badge/Problem_ID-SIH26103-blue.svg)](#)
[![Status](https://img.shields.io/badge/Status-Documentation_&_Architecture_Initialized-brightgreen.svg)](#)

> **Predictive analytics and explainable early warning intelligence for capital infrastructure projects, forecasting delay and cost overrun risks before critical milestones lapse.**

---

## 📌 Executive Summary
Major public and private infrastructure undertakings frequently encounter cascading delays and budget escalations due to late detection of operational distress signals (e.g., land clearance bottlenecks, expenditure divergence, milestone slippage).

**SIH26103** is an AI/ML-powered monitoring and decision-support system designed to convert standard infrastructure project monitoring indicators into **actionable predictive early warnings** with quantifiable, explainable risk drivers.

---

## 🔄 MVP Core Flow

```
[ Project Data ]
       │
       ▼
[ Data Validation / Preprocessing ]
       │
       ▼
[ Feature Engineering ]
       │
       ▼
[ Predictive ML Models ]
       │
       ├─────────────────────────┐
       ▼                         ▼
[ Delay Risk (0-100) ]   [ Cost Overrun Risk (0-100) ]
       │                         │
       └───────────┬─────────────┘
                   ▼
       [ Composite Project Risk Index ]
                   │
                   ▼
       [ Explainable Risk Factors (SHAP) ]
                   │
                   ▼
       [ Early Warning Alerts & Actions ]
                   │
                   ▼
       [ Interactive Executive Dashboard ]
```

---

## 📑 Project Documentation Index

Before implementing any code or modifying schemas, consult the dedicated architecture and specification documents:

| Document | Description | Status |
|---|---|---|
| [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) | **Single Source of Truth** for project direction, scope boundaries, and core decisions. | Active |
| [MVP_REQUIREMENTS.md](MVP_REQUIREMENTS.md) | Comprehensive functional and non-functional requirements, user personas, and acceptance criteria. | Active |
| [DATA_SCHEMA.md](DATA_SCHEMA.md) | Data schemas for raw project inputs, engineered features, prediction outputs, and data sourcing strategy. | Active |
| [ML_PLAN.md](ML_PLAN.md) | ML problem formulation, candidate models, evaluation rigor, and TreeSHAP explainability design. | Active |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System components, Mermaid architecture diagrams, data flow sequences, and directory structure. | Active |
| [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md) | Chronological audit log of engineering milestones, decisions recorded, and pending items. | Active |

---

## 🎯 Guiding MVP Principles
- **Demo-Ready & High-Impact:** Focused on delivering an interactive, visually compelling, and scientifically sound experience for hackathon evaluators.
- **Strict Scope Discipline:** The MVP intentionally excludes production government platform overhead:
  - ❌ No live MoSPI/PRAGATI scraper dependencies.
  - ❌ No physical IoT sensor hardware feeds.
  - ❌ No nationwide multi-million record database requirement.
  - ❌ No complex government SSO or multi-tiered bureaucratic authentication.
  - ❌ No mandatory conversational chatbot as an interface bottleneck.
- **Scientific Integrity:** No fabricated accuracy claims, invented statistics, or fake ministry endorsements. Metrics are reported only upon empirical training.

---

## 🛠️ Provisional Technology Stack

*Technology selections are provisional and will be implemented incrementally as justified:*

- **Frontend:** React 18, TypeScript, Tailwind CSS, Lucide Icons
- **Data Visualization:** Recharts (Interactive EVM S-curves, gauge charts, risk distributions)
- **Backend API:** FastAPI (Python 3.11+), Pydantic v2
- **Data Science & ML:** Pandas, NumPy, Scikit-learn, XGBoost / LightGBM
- **Model Explainability:** SHAP (`TreeExplainer`)
- **Persistence:** SQLAlchemy with PostgreSQL (Docker target) / SQLite (Zero-config local fallback)
- **Deployment:** Docker & Docker Compose

---

## 📂 Repository Organization

```
SIH26103-Infrastructure-Risk-Prediction/
├── PROJECT_CONTEXT.md      # Definitive single source of truth
├── MVP_REQUIREMENTS.md     # Functional & non-functional requirements
├── DATA_SCHEMA.md          # Input, feature, and output data contracts
├── ML_PLAN.md              # Machine learning strategy & evaluation plan
├── ARCHITECTURE.md         # Component diagrams and data flow
├── DEVELOPMENT_LOG.md      # Chronological audit log of decisions
├── README.md               # Repository orientation
├── .gitignore              # Git ignore rules
│
├── backend/                # FastAPI application (to be initialized)
├── frontend/               # React + TypeScript dashboard (to be initialized)
├── ml_research/            # Data benchmarks, modeling scripts & notebooks (to be initialized)
└── docker/                 # Containerization configs (to be initialized)
```

---

## 🚀 Development Roadmap

- [x] **Phase 0:** Project Context, Architecture, and Data Contracts Initialization
- [ ] **Phase 1:** Data Sourcing & Calibrated Infrastructure Benchmark Generator
- [ ] **Phase 2:** Feature Engineering Pipeline & Baseline EVM Heuristic Engine
- [ ] **Phase 3:** Machine Learning Model Training (Delay & Cost Overrun) & SHAP Integration
- [ ] **Phase 4:** FastAPI Backend Service with Pydantic Validation & REST Endpoints
- [ ] **Phase 5:** Interactive React + TypeScript Dashboard (Executive Summary, Project Explorer, What-If Simulator)
- [ ] **Phase 6:** End-to-End Testing, Dockerization, and Demo Script Finalization
