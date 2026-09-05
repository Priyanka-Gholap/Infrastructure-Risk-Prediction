# Development & Engineering Log

This log provides an auditable, chronological record of technical decisions, architectural evolutions, schema modifications, and development milestones across the lifecycle of **SIH26103**.

---

## [2026-09-05] - Project Initialization & Documentation Architecture

### Context & Objective
Establish the project documentation foundation, formalize MVP scope and boundaries, define provisional technology stack, and establish data contracts before writing any application code for SIH 2026 Problem Statement `SIH26103` (*AI-Powered Predictive Analytics & Early Warning System for Infrastructure Project Monitoring*).

### Actions Completed
1. **Defined Project Context (`PROJECT_CONTEXT.md`):**
   - Established `PROJECT_CONTEXT.md` as the single source of truth.
   - Formalized Core Objective and End-to-End MVP Core Flow.
   - Enforced explicit boundaries: MVP is demo-ready and robust, but deliberately avoids production government platform scope creep (no IoT sensors, no live MoSPI OCMS scrapers, no national SSO auth, no chatbot dependencies).
2. **Specified MVP Requirements (`MVP_REQUIREMENTS.md`):**
   - Detailed functional requirements (FR-1 through FR-7) covering data ingestion, Pydantic validation, feature engineering, dual predictive models (Delay Risk + Cost Overrun Risk), SHAP-based explainability, early warning alert tiers, and interactive dashboard views.
   - Specified Non-Functional Requirements (latency, zero external network dependency, visual polish, determinism).
3. **Structured Data Contracts (`DATA_SCHEMA.md`):**
   - Formulated input schema across metadata, financial variables, schedule parameters, physical progress, and clearance risk factors.
   - Defined derived engineered feature specifications (time-elapsed ratio, schedule slippage, cost-physical divergence, land risk factor).
   - Structured the output prediction payload including composite risk, categorical risk tiers, and top-3 explainability driver schema.
4. **Drafted ML Roadmap (`ML_PLAN.md`):**
   - Structured dual prediction tasks: Delay Risk (classification/score) and Cost Overrun Risk (classification/score), unified into a Composite Risk Index.
   - Outlined candidate models: EVM Baseline, Logistic Regression, Random Forest, and Gradient Boosted Trees (XGBoost/LightGBM).
   - Enforced scientific rigor: explicitly prohibited inventing unverified accuracy numbers or claiming official government endorsement without empirical basis.
5. **Architected System Design (`ARCHITECTURE.md`):**
   - Created Mermaid architecture diagram separating Presentation (React/Tailwind/Recharts), API Gateway (FastAPI), Analytics Engine (Pandas/XGBoost/SHAP), and Storage (SQLAlchemy/PostgreSQL/SQLite fallback).
   - Outlined directory structure and end-to-end data flow.
6. **Configured Environment Protection (`.gitignore` & `README.md`):**
   - Created comprehensive `.gitignore` preventing commit of node_modules, Python virtual environments, binaries, model caches, and environment secrets.
   - Created structured `README.md` providing clear orientation for developers and evaluators.

### Decisions Recorded
- **Scope Discipline:** Focus exclusively on predictive intelligence and early warning for delay and cost overrun. Keep scope tightly bounded to ensure a polished, reliable hackathon demo.
- **Explainability as a Core Pillar:** Every predictive alert must be coupled with human-readable, quantifiable drivers (via TreeSHAP attribution) to make warnings actionable for project authorities.
- **Provisional Stack:** React (TypeScript) + Tailwind CSS + Recharts for Frontend; FastAPI + Pydantic + Scikit-learn/XGBoost for Backend; Docker for containerization.
- **Demo Portability:** Persistence layer to support SQLite alongside PostgreSQL so the platform can run locally with zero network dependencies.

### Pending Decisions
- **Data Sourcing Decision [PENDING]:** Feasibility analysis of extracting tabular project records from public MoSPI monthly flash reports vs. generating a statistically calibrated synthetic project dataset adhering to published MoSPI empirical distributions.
- **Model Target Formulation [PENDING]:** Multi-tier classification (Low/Medium/High/Critical) vs. Hybrid multi-task output (Risk Tier + Quantitative Duration/Cost Regression).

### Next Recommended Step
- Execute Phase 1 Data Strategy: Investigate public MoSPI flash report structures and construct the benchmark project data generator script (`generate_benchmark.py`) with domain-accurate distributions.
