# Development & Engineering Log

This log provides an auditable, chronological record of technical decisions, architectural evolutions, schema modifications, and development milestones across the lifecycle of **SIH26103**.

---

## [2026-09-05] - Documentation Review & Governance Corrections

### Context & Objective
Conduct a cross-document audit across all architectural specifications (`PROJECT_CONTEXT.md`, `MVP_REQUIREMENTS.md`, `DATA_SCHEMA.md`, `ML_PLAN.md`, `ARCHITECTURE.md`, `DEVELOPMENT_LOG.md`, `README.md`) to enforce strict scientific integrity, clarify fact vs. assumption boundaries, prevent premature technical complexity, and ensure consistent MVP scoping before writing any application code or scripts.

### Changes & Corrections Completed
1. **Data Source Status Alignment:**
   - Explicitly marked all training data strategies as **PENDING DATA RESEARCH**.
   - Removed any statements implying that a synthetic dataset is "necessary" or "already selected".
   - Standardized data sourcing status across all documents:
     > *"Training data strategy is PENDING. Candidate approaches include publicly extracted project-level records, carefully constructed benchmark/synthetic data where necessary, or a hybrid approach. The final strategy will be selected only after evaluating the actual availability and quality of project-level historical data."*
2. **ML Targets Ground Truth Derivation:**
   - Marked exact risk score thresholds and tier definitions as **PENDING DATA VALIDATION**.
   - Documented that ground-truth target labels must ultimately be derived from observable historical outcomes wherever possible (e.g., actual recorded delay in months, realized cost growth percentage over sanctioned budget), rather than arbitrarily assigning risk labels based only on current feature values.
   - Reaffirmed **Delay Risk** and **Cost Overrun Risk** as the two confirmed core prediction objectives.
3. **What-If Simulator Prioritization (P1 Enhancement):**
   - Reclassified the interactive "What-If Simulator" from a potential blocker to a **P1 / high-value enhancement**.
   - Preserved the core MVP pipeline (Data Ingestion → Validation → Feature Engineering → Dual Predictive Models → Composite Risk → Explainability → Early Warning → Dashboard) as fully functional and demo-ready without requiring the simulator.
4. **Database Strategy Simplification (SQLite Preference):**
   - Selected **SQLite** as the primary local/demo persistence option for initial MVP development to ensure zero-configuration, zero-daemon, and zero-network-failure execution during live hackathon evaluation.
   - Retained PostgreSQL as an optional future/production deployment path via SQLAlchemy ORM abstraction.
   - Avoided introducing premature Docker/PostgreSQL configuration complexity before justified.
5. **Fact vs. Assumption Separation:**
   - Reviewed `PROJECT_CONTEXT.md` and `DATA_SCHEMA.md` to ensure any statement contingent on future research is categorized under `Assumptions` or `Pending Decisions`, rather than stated as confirmed facts.
6. **Preserved Core MVP Demonstration Standard:**
   - Maintained all high-impact visualization, feature engineering, and explainability (TreeSHAP) requirements to ensure executive-level demo presentation.
7. **Strict Development Discipline:**
   - Confirmed that no application code, database models, frontend code, or scripts (including `generate_benchmark.py`) were created prematurely.

### Decisions Recorded
- **Primary MVP Storage:** SQLite via SQLAlchemy for local/demo simplicity; PostgreSQL preserved as optional future/production deployment path.
- **Core Prediction Targets:** Delay Risk and Cost Overrun Risk remain the two confirmed core prediction objectives.
- **Feature Prioritization:** Interactive What-If Simulator classified as P1 enhancement; Core MVP is self-sufficient without it.

### Remaining Pending Decisions
- **Training Data Strategy [PENDING DATA RESEARCH]:** Awaiting empirical evaluation of public MoSPI project-level disclosures to determine whether publicly extracted records, domain-constructed benchmarks, or a hybrid strategy provides the highest quality dataset.
- **Target Label Formulation [PENDING DATA VALIDATION]:** Final definition of classification tier cutoffs or continuous outcome targets derived from observed historical delays and cost escalations.
- **Packaging & Deployment [PENDING]:** Decision on standalone local execution vs Docker containerization, to be addressed after backend and frontend modules stabilize.

### Recommended Next Step
- **Conduct Phase 1 Data Research:** Investigate the actual structure, completeness, and accessibility of public MoSPI project-level disclosures and flash reports to inform the data sourcing strategy decision before writing any generation or ingestion scripts.

---

## [2026-09-05] - Project Initialization & Documentation Architecture

### Context & Objective
Establish initial project documentation foundation and define provisional technology stack for SIH 2026 Problem Statement `SIH26103`.

### Actions Completed
- Created initial set of documentation: `PROJECT_CONTEXT.md`, `MVP_REQUIREMENTS.md`, `DATA_SCHEMA.md`, `ML_PLAN.md`, `ARCHITECTURE.md`, `DEVELOPMENT_LOG.md`, `README.md`, `.gitignore`.
