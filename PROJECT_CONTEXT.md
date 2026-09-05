# SIH26103 – AI-Powered Predictive Analytics & Early Warning System for Infrastructure Project Monitoring

## 1. Project Overview & Identity
- **Problem Statement ID:** SIH26103
- **Title:** AI-Powered Predictive Analytics & Early Warning System for Infrastructure Project Monitoring
- **Initiative:** Smart India Hackathon (SIH) 2026
- **Status:** Initialization / Pre-Development Phase
- **Single Source of Truth:** This document (`PROJECT_CONTEXT.md`) serves as the definitive reference for project scope, architectural decisions, operational boundaries, and developmental status.

---

## 2. Core Objective
Build an AI/ML-powered infrastructure project monitoring system that converts project monitoring data into predictive early warnings for **project delay** and **cost overrun**.

---

## 3. MVP Core Flow
The end-to-end processing pipeline for the Minimum Viable Product (MVP) is strictly defined as follows:

```
[ Project Data (Inputs / Milestones) ]
                  │
                  ▼
[ Data Validation & Preprocessing (Pydantic / Cleaners) ]
                  │
                  ▼
[ Feature Engineering (Schedule / Cost Variances, Rates) ]
                  │
                  ▼
[ Predictive ML Models (Delay Risk & Cost Overrun Risk) ]
                  │
                  ▼
[ Delay Risk Assessment ] + [ Cost Overrun Risk Assessment ]
                  │
                  ▼
[ Overall Composite Project Risk Index ]
                  │
                  ▼
[ Risk Factors & Explainability (Feature Attribution / SHAP) ]
                  │
                  ▼
[ Early Warning Alert Engine (Thresholds & Severity Levels) ]
                  │
                  ▼
[ Interactive Demonstration Dashboard (React + Charts) ]
```

---

## 4. Guiding MVP Principles & Boundaries

### 4.1 Demo-Ready Pragmatism
The MVP must be functionally impressive, scientifically sound, visually compelling, and demo-ready for SIH evaluation panels. However, **it must not attempt to become a production-scale government platform during hackathon development.**

### 4.2 Explicit Out-of-Scope (What MVP Will NOT Include)
To prevent scope creep and brittle dependencies during evaluation, the MVP explicitly excludes:
- **Real-time government system integration:** No live API dependencies or automated scraping of live government portals (e.g., MoSPI OCMS, PM GatiShakti, PRAGATI).
- **IoT / On-site sensor integration:** No physical sensor ingestion, drone feeds, or RFID tracking.
- **Nationwide infrastructure database:** No requirement to store or index tens of thousands of active national projects.
- **Production-grade government authentication:** No integration with National Single Sign-On (Jan Parichay), Aadhaar, DigiLocker, or complex multi-tenant government RBAC.
- **Separate ML models for every infrastructure sector:** A unified, robust model architecture across key indicators rather than 50 bespoke sector-specific models.
- **Large-scale automated model retraining pipelines:** No MLOps distributed cluster or automated online continuous retraining.
- **Enterprise notification infrastructure:** No production SMS gateways, telephonic alerts, or official government dispatch mechanisms.
- **Chatbot as a core dependency:** A conversational bot is non-essential and will not be a blocker or prerequisite for core analytics.

---

## 5. Classification of Project Knowledge

### 5.1 Confirmed Facts & Decisions
1. **Core Problem:** Major infrastructure projects suffer from chronic schedule delays and budget overruns due to delayed detection of early distress signals.
2. **Dual-Risk Focus:** Predictions must address both **Delay Risk** and **Cost Overrun Risk**, synthesized into a unified composite risk score.
3. **Actionable Insights:** Predictions must not be opaque black-box numbers; they must be accompanied by explainable risk drivers (e.g., land acquisition lag, fund disbursement deficit, environmental clearance hurdles).
4. **Target Users for Demo:** Infrastructure monitoring officers, departmental analysts, and project appraisal committees seeking proactive intervention rather than retrospective auditing.

### 5.2 Assumptions
1. **Data Availability:** Public project-level data from government sources (e.g., MoSPI Flash Reports) is largely available in aggregate PDF/HTML formats rather than ready-to-train ML tabular datasets.
2. **Benchmark Generation:** A high-fidelity, statistically grounded synthetic/calibrated dataset representing real-world infrastructure parameters (cost ratios, milestone completion percentages, typical delay patterns) is necessary to train and validate robust demo models if raw historic tabular dumps are inaccessible.
3. **Evaluation Environment:** The project will be evaluated in a local or cloud demo environment where stability, determinism, and zero external runtime failures are paramount.

### 5.3 Pending Decisions (Marked PENDING)
1. **Data Sourcing Strategy [PENDING]:** Evaluation of whether public MoSPI flash reports can be extracted into a sufficiently rich tabular training set vs. developing a calibrated domain-accurate synthetic data generator based on published MoSPI statistical distributions.
2. **Model Paradigm [PENDING]:** Decision between Dual Classification (High/Medium/Low Risk for delay & cost) vs. Hybrid Classification + Regression (predicting probability level + estimated delay duration in months and overrun percentage).
3. **Database Selection for MVP Demo [PENDING]:** PostgreSQL as primary target vs. SQLite local fallback for zero-configuration standalone demonstration portability.

### 5.4 Future Scope (Post-MVP)
- Live synchronization with MoSPI OCMS / PM GatiShakti national portals via secure government data APIs.
- Satellite earth-observation & computer-vision progress verification.
- Natural Language Processing (NLP) on contractor progress notes and regulatory clearance documentation.
- Multi-tier contractor performance tracking and credit risk linkage.
- Automated escalation matrix dispatching alerts via SMS/WhatsApp to field engineers.

---

## 6. Provisional Technology Stack
*All selections are provisional and subject to implementation justification. No premature dependencies or complex boilerplates should be introduced before required.*

| Tier | Provisional Technology | Purpose in MVP | Status |
|---|---|---|---|
| **Frontend UI** | React (TypeScript) | Responsive, stateful monitoring dashboard | Provisional |
| **Styling** | Tailwind CSS | Clean, professional UI layout & risk badges | Provisional |
| **Visualization** | Recharts | Interactive risk charts, milestone timelines, EVM curves | Provisional |
| **Backend API** | FastAPI (Python) | High-performance asynchronous REST API & validation | Provisional |
| **Data Processing** | Pandas + NumPy | Tabular transformation, feature calculations | Provisional |
| **Machine Learning** | Scikit-learn / XGBoost | Classification, regression, and tree-based risk models | Provisional |
| **Explainability** | SHAP / TreeExplainer | Feature attribution and top risk driver generation | Provisional |
| **Validation** | Pydantic (v2) | Strict input data schema validation & integrity | Provisional |
| **ORM / Storage** | SQLAlchemy / PostgreSQL | Persistence of project snapshots and alert logs | Provisional |
| **Containerization** | Docker + Docker Compose | Portable, reproducible multi-container deployment | Provisional |

---

## 7. Governance Rules for Developers
1. **Source of Truth:** Always verify decisions against this document before introducing architectural modifications.
2. **No Fabricated Assertions:** Never invent training accuracy figures, benchmark numbers, or claim official Ministry endorsement without evidence.
3. **Documented Evolution:** Any alteration to confirmed decisions must be discussed, justified, and logged in `DEVELOPMENT_LOG.md` and updated in `PROJECT_CONTEXT.md`.
