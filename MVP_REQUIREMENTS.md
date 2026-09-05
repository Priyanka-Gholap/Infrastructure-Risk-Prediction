# MVP Requirements Specification

## 1. Executive Summary
This document specifies the functional, non-functional, and operational requirements for the Minimum Viable Product (MVP) of **SIH26103: AI-Powered Predictive Analytics & Early Warning System for Infrastructure Project Monitoring**.

The MVP is engineered to deliver a robust, highly convincing, and interactive demonstration of how machine learning can detect early failure signals in capital infrastructure projects, predicting delay risk and cost overrun risk with interpretable risk attribution.

---

## 2. Target Personas & Use Cases

| Persona | Role / Context | Primary Goal in System |
|---|---|---|
| **Monitoring Officer (PMO)** | Oversees portfolio of ongoing multi-crore infrastructure works. | Rapidly identify which projects are heading into critical distress before scheduled milestones fail. |
| **Budget & Financial Analyst** | Tracks capital allocation, sanctions, and expenditure trends. | Anticipate cost escalation early enough to adjust contingency budgets and enforce financial discipline. |
| **Review Committee Member** | High-level decision maker presiding over quarterly infrastructure reviews. | Gain transparent, explainable insight into *why* a project is red-flagged without wading through 100-page paper reports. |

---

## 3. Functional Requirements (FRs)

### FR-1: Project Ingestion & Data Input
- **FR-1.1 (Manual Entry):** Provide an intuitive single-project assessment form allowing users to input key project parameters (budget, expenditure, start date, target completion date, physical progress, financial progress, sector, clearance status, etc.).
- **FR-1.2 (Preloaded Curated Benchmark / Batch Upload):** Provide pre-loaded reference projects (representing diverse sectors such as Roads, Railways, Power, Urban Infrastructure) and support batch file ingestion (CSV/JSON) for instant portfolio evaluation.
- **FR-1.3 (Sample Project Presets):** Provide quick-load test cases (e.g., "On-Track Highway", "Severely Delayed Railway Line", "Financially Strained Urban Metro") to ensure seamless live demonstrations.

### FR-2: Data Validation & Sanitization
- **FR-2.1 (Schema Conformance):** Strict validation of types, mandatory attributes, and bounds using Pydantic schemas.
- **FR-2.2 (Logical Integrity Checks):**
  - Physical progress must lie strictly within $[0, 100]\%$.
  - Financial progress must lie strictly within $[0, 100]\%$.
  - Cumulative expenditure must be $\ge 0$.
  - Original scheduled completion date must be strictly after project commencement date.
  - Revised completion date must be $\ge$ original completion date.
- **FR-2.3 (Missing Data Handling):** Graceful default imputation and explicit warnings when non-critical metadata fields are omitted.

### FR-3: Feature Engineering Pipeline
- **FR-3.1 (Temporal Progress Metrics):**
  - Planned duration (months).
  - Elapsed duration to date (months).
  - Time elapsed ratio: $\text{Elapsed Duration} / \text{Planned Duration}$.
- **FR-3.2 (Earned Value & Variance Indicators):**
  - Schedule Slippage / Variance Indicator (comparison between planned physical milestone % and actual achieved %).
  - Financial Burn vs Physical Completion Ratio: $\text{Financial Progress \%} / \max(\text{Physical Progress \%}, 1\%)$.
  - Expenditure Velocity: Average monthly spend rate relative to remaining budget.
- **FR-3.3 (Risk Bottleneck Indicators):**
  - Land acquisition completion ratio.
  - Regulatory / Environmental clearance status flag.
  - Contractor revision count / scope change frequency.

### FR-4: Predictive Risk Models (Delay Risk + Cost Overrun Risk)
- **FR-4.1 (Delay Risk Scoring):**
  - Predict likelihood of project delay.
  - Output: Delay Risk Score ($0.0 - 100.0$) and Categorical Risk Tier.
- **FR-4.2 (Cost Overrun Risk Scoring):**
  - Predict likelihood of expenditure exceeding sanctioned budget.
  - Output: Cost Overrun Risk Score ($0.0 - 100.0$) and Categorical Risk Tier.
- **FR-4.3 (Composite Project Risk Index):**
  - Synthesize Delay Risk and Cost Overrun Risk into a unified single Project Health / Risk Index.

> [!IMPORTANT]
> **Target Formulation & Ground Truth Derivation [PENDING DATA VALIDATION]:**
> The exact target formulation and risk score thresholds are **PENDING DATA VALIDATION**. Target labels must ultimately be derived from observable historical outcomes wherever possible (e.g., realized schedule delay in months, actual cost growth ratio), rather than arbitrarily assigning risk labels based only on current feature values. Delay risk and cost overrun risk remain the two confirmed core prediction objectives.

### FR-5: Risk Factor Explainability
- **FR-5.1 (Attribution Output):** Extract and display the top 3 to 5 contributing drivers behind a high risk score for any given project.
- **FR-5.2 (Interpretability Methodology):** Utilize feature attribution mechanisms (e.g., Tree SHAP values or normalized weight impact) so officers understand *why* the model flagged the project (e.g., "+34% risk driven by 40% physical progress lag relative to 75% elapsed duration").

### FR-6: Early Warning Alert System
- **FR-6.1 (Alert Generation):** Dynamically categorize projects into automated alert tiers based on predicted composite risk. Indicative tiers:
  - 🟢 **Normal / Low Risk:** Regular monitoring; no corrective escalation required.
  - 🟡 **Watchlist / Moderate Risk:** Emerging slippage; advisory warning issued.
  - 🟠 **High Risk:** Action required; milestone and financial audit recommended.
  - 🔴 **Critical / Red Flag:** Severe escalation; immediate administrative intervention needed.
  *(Note: Exact numeric threshold boundaries are subject to calibration during data validation.)*
- **FR-6.2 (Actionable Recommendations):** Pair alerts with contextual mitigation suggestions (e.g., "Expedite Stage-2 environmental clearance", "Reallocate regional contractor manpower").

### FR-7: Interactive Demonstration Dashboard
- **FR-7.1 (Portfolio Executive Summary):** Visual summary showing total projects monitored, portfolio risk distribution (pie/bar), total capital at risk, and critical alert tally.
- **FR-7.2 (Project Explorer & Filtering):** Searchable, filterable table by sector, state, risk tier, and budget size.
- **FR-7.3 (Project Detail View):** Dedicated drill-down view showing project trajectory, S-curve (planned vs actual progress), risk gauges, and top negative drivers.
- **FR-7.4 (Interactive "What-If" Simulator - P1 Enhancement):**
  - Interactive controls allowing an evaluator to adjust key project parameters (e.g., test 15% physical progress recovery, resolve pending forest clearance) and dynamically observe recalculated risk scores.
  - **Priority Status:** Designated as a **P1 / high-priority enhancement**. The core MVP must remain fully functional, demo-ready, and valuable without this simulator.

---

## 4. Non-Functional Requirements (NFRs)

### NFR-1: Performance & Responsiveness
- **API Response Latency:** Single project prediction and explainability payload must return within $\le 1.5$ seconds under standard local demo conditions.
- **Client-Side Rendering:** Dashboard views and charts must render smoothly without UI freeze or stutter.

### NFR-2: Reliability & Self-Sufficiency
- **Zero External Runtime Breakage:** The demo must operate autonomously without requiring external internet connections, live third-party APIs, or external database cloud clusters.
- **Graceful Error Handling:** Invalid user inputs must trigger clear, user-friendly field-level error messages rather than unhandled server crashes (500 errors).

### NFR-3: User Experience & Design
- **Visual Clarity:** Professional aesthetic appropriate for administrative governance; standard intuitive color coding for risk states (Emerald/Amber/Orange/Rose).
- **Responsive Layout:** Optimized for standard presentation display resolutions (1080p desktop/laptop viewing).

### NFR-4: Code Maintainability & Architecture Simplicity
- Decoupled API contracts between frontend and backend.
- Pure function data pipelines with unit-testable feature engineering.
- **Persistence Simplicity:** Use **SQLite** for initial MVP local/demo development; retain PostgreSQL as an optional future/production deployment path without introducing Docker/DB complexity prematurely.

---

## 5. Scope Boundaries & Anti-Requirements

The following items are **strictly outside the MVP scope**:
- ❌ Integration with live government portals (MoSPI OCMS, PRAGATI, PM GatiShakti).
- ❌ Direct hardware IoT sensor or on-site CCTV video analytics.
- ❌ Production multi-factor government identity federation.
- ❌ Enterprise SMS/telecom gateways for alert delivery.
- ❌ Autonomous automated online retraining on distributed clusters.
- ❌ Mandatory conversational chatbot as an interface bottleneck.

---

## 6. MVP Acceptance & Evaluation Criteria

| Requirement | Acceptance Benchmark | Priority | Status |
|---|---|---|---|
| **Input Ingestion** | Manual form entry and preloaded sample projects load reliably. | Core MVP (P0) | Pending Implementation |
| **Data Sanitization** | Pydantic model rejects negative budgets, impossible dates, and out-of-bound percentages with clear feedback. | Core MVP (P0) | Pending Implementation |
| **ML Predictive Pipeline** | Trained models predict Delay Risk and Cost Overrun Risk scores for valid input payloads. | Core MVP (P0) | Pending Implementation |
| **Explainability** | Top 3 risk contributors are visually rendered for any evaluated project. | Core MVP (P0) | Pending Implementation |
| **Early Warning Alerts** | Projects receive calibrated tier labels (Low, Medium, High, Critical) with actionable recommendations. | Core MVP (P0) | Pending Implementation |
| **Interactive Dashboard** | Portfolio view and project inspector render smoothly and responsively. | Core MVP (P0) | Pending Implementation |
| **What-If Simulator** | Dynamic parameter adjustment and real-time risk re-scoring. | High-Value Enhancement (P1) | Pending Implementation |
