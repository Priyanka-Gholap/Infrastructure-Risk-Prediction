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

> [!NOTE]
> The core MVP delivers the full pipeline above. An interactive "What-If Simulator" is designated as a **P1 / high-value enhancement** to enrich user interaction during demonstrations, but the core MVP remains fully functional, credible, and complete without it.

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
- **Separate ML models for every infrastructure sector:** A unified, robust model architecture across key indicators rather than bespoke sector-specific models.
- **Large-scale automated model retraining pipelines:** No MLOps distributed cluster or automated online continuous retraining.
- **Enterprise notification infrastructure:** No production SMS gateways, telephonic alerts, or official government dispatch mechanisms.
- **Chatbot as a core dependency:** A conversational bot is non-essential and will not be a blocker or prerequisite for core analytics.

---

## 5. Classification of Project Knowledge

### 5.1 Confirmed Facts & Decisions
1. **Core Problem:** Major capital infrastructure projects suffer from chronic schedule delays and budget escalations due to late detection of operational distress signals.
2. **Dual Core Prediction Objectives:** Predictions must focus on **Delay Risk** and **Cost Overrun Risk**, synthesized into a unified composite project risk index.
3. **Actionable Explainability Requirement:** Predictions must not be opaque black-box numbers; they must be accompanied by explainable, attributable risk drivers (e.g., time-elapsed vs physical progress divergence, cost burn anomalies, clearance bottlenecks).
4. **Target Users for Demo:** Infrastructure monitoring officers, departmental analysts, and project appraisal committees seeking proactive intervention rather than retrospective auditing.
5. **Database Strategy for Initial MVP:** For initial MVP development, **SQLite** is selected as the simplest local/demo persistence option. PostgreSQL is maintained as an optional future/production-oriented deployment path. Docker and PostgreSQL complexity will not be introduced before actually needed.

### 5.2 Assumptions
1. **Reporting Structure Assumption:** Historical project-level data from public government disclosures (e.g., MoSPI Flash Reports) is primarily formatted as periodic PDF/HTML publication tables rather than pre-packaged, ML-ready tabular feature matrices.
2. **Evaluation Environment Assumption:** Hackathon evaluation will occur in a local or standalone presentation setting where offline stability, instant responsiveness, and zero external network dependencies are paramount.

### 5.3 Pending Decisions (Marked PENDING)
1. **Training Data Strategy [PENDING]:**
   > Training data strategy is PENDING. Candidate approaches include publicly extracted project-level records, carefully constructed benchmark/synthetic data where necessary, or a hybrid approach. The final strategy will be selected only after evaluating the actual availability and quality of project-level historical data.
   > *(Note: A synthetic dataset is not assumed to be necessary or already selected.)*
2. **Target Formulation & Ground Truth Derivation [PENDING DATA VALIDATION]:**
   > The exact target formulation and risk thresholds are PENDING DATA VALIDATION. Target labels must ultimately be derived from observable historical outcomes wherever possible (e.g., actual delay in months, realized cost growth ratio), rather than arbitrarily assigning risk labels based only on current feature values. Delay risk and cost-overrun risk remain the two confirmed core prediction objectives.
3. **Containerization & Deployment Orchestration [PENDING]:**
   > Full Docker containerization is retained as an optional packaging path once application modules stabilize, but will not precede core functionality.

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
| **Persistence** | SQLAlchemy + SQLite | Simplest local/demo persistence (PostgreSQL optional future path) | Confirmed Direction for MVP |
| **Deployment** | Python / Node Local; Docker optional | Standalone execution without premature container overhead | Provisional / Optional |

---

## 7. Governance Rules for Developers
1. **Source of Truth:** Always verify decisions against this document before introducing architectural modifications.
2. **No Fabricated Assertions:** Never invent training accuracy figures, benchmark numbers, or claim official Ministry endorsement without evidence.
3. **Documented Evolution:** Any alteration to confirmed decisions must be discussed, justified, and logged in `DEVELOPMENT_LOG.md` and updated in `PROJECT_CONTEXT.md`.
