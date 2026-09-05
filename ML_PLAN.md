# Machine Learning Strategy & Plan

## 1. Machine Learning Objectives & Problem Formulation
The predictive engine for **SIH26103** must detect early signals of distress in capital infrastructure projects, quantifying risks before irreversible delays or cost escalations materialize.

```
[ Engineered Features (Variance, Velocity, Milestones) ]
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
  [ Delay Risk Model ]         [ Cost Overrun Model ]
  • Risk Score (0-100)         • Risk Score (0-100)
  • Tier (Low/Med/High/Crit)   • Tier (Low/Med/High/Crit)
             │                           │
             └─────────────┬─────────────┘
                           ▼
            [ Composite Risk Synthesizer ]
                           │
                           ▼
          [ Explainability Engine (SHAP) ]
            • Top 3-5 Risk Drivers
```

---

## 2. Core Prediction Objectives & Target Formulation

The system maintains two confirmed core prediction objectives:
1. **Delay Risk Prediction**
2. **Cost Overrun Risk Prediction**

> [!IMPORTANT]
> **Ground Truth Derivation & Risk Thresholds [PENDING DATA VALIDATION]:**
> - The risk score tiers and numerical percentage boundaries presented below are provisional design constructs.
> - **The exact target formulation is PENDING DATA VALIDATION.**
> - Target labels must ultimately be derived from **observable historical outcomes wherever possible** (e.g., actual recorded delay in months relative to original schedule, realized cost growth percentage over sanctioned budget), rather than arbitrarily assigning risk labels based solely on current feature values.
> - Grounding targets in historical outcomes ensures the model learns true predictive patterns rather than reproducing circular rule-based definitions.

### Task 1: Delay Risk Prediction
- **Objective:** Quantify the likelihood and severity of project completion extending past the approved schedule.
- **Target Formulation [PENDING DATA VALIDATION]:**
  - *Candidate Categorical Tiers (Subject to Validation):* `Low Risk`, `Moderate Risk`, `High Risk`, `Critical Risk`.
  - *Continuous Risk Score:* Calibrated probability score ($0.0 - 100.0$) mapping to an early warning indicator.
- **Observable Historical Outcome Reference:** Historical schedule slippage: $(\text{Actual/Anticipated Completion Date} - \text{Original Completion Date})$ in months or percentage of original planned timeline.
- **Key Signal Drivers:** Time-elapsed ratio vs physical progress %, milestone lapse velocity, pending land acquisition %, regulatory clearance bottlenecks.

### Task 2: Cost Overrun Risk Prediction
- **Objective:** Quantify the likelihood and severity of project expenditures exceeding the originally approved sanctioned cost.
- **Target Formulation [PENDING DATA VALIDATION]:**
  - *Candidate Categorical Tiers (Subject to Validation):* `No/Low Overrun`, `Moderate Overrun`, `High Overrun`, `Critical Overrun`.
  - *Continuous Risk Score:* Calibrated overrun probability score ($0.0 - 100.0$).
- **Observable Historical Outcome Reference:** Realized cost escalation: $(\text{Revised/Final Cost} - \text{Original Sanctioned Cost}) / \text{Original Sanctioned Cost}$.
- **Key Signal Drivers:** Capital expenditure burn rate relative to physical completion, cumulative cost revision count, time slippage spillover into financial overhead.

### Task 3: Composite Project Risk Index
- Synthesizes the individual delay and cost risk predictions into an overall decision metric for portfolio prioritization:
  $$\text{Composite Risk Index} = w_{\text{delay}} \cdot \text{Delay Score} + w_{\text{cost}} \cdot \text{Cost Score} + w_{\text{gov}} \cdot \text{Clearance Risk Factor}$$
- *Note:* Weight coefficients ($w$) will be calibrated during empirical validation.

---

## 3. Modeling Hierarchy & Candidates

### 3.1 Baseline: Deterministic Earned Value Management (EVM)
- **Purpose:** Serve as the benchmark against which ML value-add is demonstrated.
- **Formulas:**
  - Schedule Performance Index (SPI): $\text{EV} / \text{PV} \approx \text{Physical Progress \%} / \text{Planned Progress \%}$
  - Cost Performance Index (CPI): $\text{EV} / \text{AC} \approx \text{Physical Progress \%} / \text{Financial Progress \%}$
- **Limitation of Baseline:** Linear and myopic; fails to capture non-linear bottlenecks (e.g., 90% progress stalled indefinitely by 10% unacquired critical land corridor).

### 3.2 Candidate Machine Learning Models
1. **Logistic Regression / ElasticNet:** Fast, highly interpretable linear baseline.
2. **Random Forest Classifier / Regressor:** Handles non-linear feature interactions, robust to outliers, resilient against overfitting on moderate-sized tabular datasets.
3. **XGBoost / LightGBM (Gradient Boosted Decision Trees):**
   - High performance on tabular non-linear interactions.
   - Native compatibility with TreeSHAP for fast, exact local explainability.

> [!NOTE]
> Deep tabular networks and complex deep learning are considered over-engineered for this domain and data scale and are excluded from the MVP.

---

## 4. Explainability & Interpretability Strategy
Prediction without explanation will not be accepted by government project directors. The system must accompany every high-risk alert with attributable drivers.

### 4.1 SHAP (SHapley Additive exPlanations)
- **Method:** Use `shap.TreeExplainer` for tree-based candidate models (XGBoost / Random Forest).
- **Execution:**
  - Compute base value (expected average portfolio risk).
  - Compute SHAP values per feature for the specific project instance.
  - Rank features by absolute magnitude of positive contribution to risk score.
  - Return top 3–5 features transformed into human-understandable administrative summaries.

---

## 5. Evaluation Protocol & Scientific Rigor

> [!CAUTION]
> **No Fabricated Benchmarks:**
> We explicitly avoid asserting invented accuracy metrics before model training. Metrics will be measured transparently once training datasets and validation pipelines are executed.

### 5.1 Evaluation Metrics (Theoretical Standard)
- **Classification Metrics:**
  - **PR-AUC (Precision-Recall Area Under Curve):** Critical metric given potential class imbalance in severe project failure.
  - **Recall on High/Critical Risk Cases:** Crucial to avoid false negatives on distressed multi-crore investments.
  - **Macro F1-Score:** Ensures balanced classification across all risk tiers.
- **Continuous Calibration:**
  - Brier Score and reliability curves to ensure predicted risk probabilities accurately reflect historical outcome frequencies.

### 5.2 Validation Strategy
- Stratified $K$-Fold Cross Validation ($k=5$), stratified across risk categories and sectors.
- Holdout test split (20%) reserved strictly for final validation reporting.

---

## 6. Sourcing & Implementation Roadmap

| Phase | Milestone | Focus | Status |
|---|---|---|---|
| **Phase 1** | Data Strategy Formulation | Training data strategy is PENDING. Candidate approaches include publicly extracted project-level records, carefully constructed benchmark/synthetic data where necessary, or a hybrid approach. The final strategy will be selected only after evaluating the actual availability and quality of project-level historical data. | **PENDING RESEARCH** |
| **Phase 2** | Preprocessing & Pipeline | Implement Pydantic data schemas, feature transformers, and EVM baseline. | Planned |
| **Phase 3** | Model Training & Tuning | Train candidate models, evaluate PR-AUC/Recall against historical outcome targets, select champion model. | Planned |
| **Phase 4** | SHAP Integration | Wire `TreeExplainer` to produce serializable JSON explainability payloads. | Planned |
| **Phase 5** | Artifact Serialization | Export trained models (`.joblib` / ONNX) and bundle into backend API service. | Planned |
