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

## 2. Predictive Tasks Formulation

### Task 1: Delay Risk Prediction
- **Target Formulation:**
  - *Primary (Classification):* Predict the probability of substantial project delay (> 3-6 months beyond sanctioned completion).
    - Class labels: `Low Risk` ($\le 10\%$ delay), `Moderate Risk` ($10-25\%$ delay), `High Risk` ($25-50\%$ delay), `Critical Risk` ($> 50\%$ delay).
  - *Secondary / Continuous Output:* Calibrated probability score ($0.0 - 100.0$) mapping to an early warning gauge.
- **Key Signal Drivers:** Time-elapsed ratio vs physical progress %, milestone lapse velocity, pending land acquisition %, regulatory clearance bottlenecks.

### Task 2: Cost Overrun Risk Prediction
- **Target Formulation:**
  - *Primary (Classification):* Predict the likelihood of project expenditures exceeding the originally approved sanctioned cost.
    - Class labels: `No/Low Overrun` ($\le 5\%$), `Moderate Overrun` ($5-20\%$), `High Overrun` ($> 20\%$).
  - *Secondary / Continuous Output:* Calibrated overrun probability score ($0.0 - 100.0$).
- **Key Signal Drivers:** Capital expenditure burn rate relative to physical completion, cumulative cost revision count, time slippage spillover into financial overhead.

### Task 3: Composite Project Risk Index
- Synthesizes the individual delay and cost risk predictions into an overall decision metric for portfolio prioritization:
  $$\text{Composite Risk Index} = w_{\text{delay}} \cdot \text{Delay Score} + w_{\text{cost}} \cdot \text{Cost Score} + w_{\text{gov}} \cdot \text{Clearance Risk Factor}$$
- *Note:* Weights ($w$) will be calibrated to ensure balanced sensitivity during empirical validation.

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
   - Industry gold standard for tabular risk prediction.
   - High performance on tabular non-linear interactions.
   - Direct compatibility with TreeSHAP for millisecond-latency local explainability.

> [!NOTE]
> Deep learning (transformers, deep tabular networks) is considered **inappropriate and over-engineered** for tabular infrastructure datasets of this size and is excluded from the MVP.

---

## 4. Explainability & Interpretability Strategy
Prediction without explanation will not be accepted by government project directors. The system must accompany every high-risk alert with attributable drivers.

### 4.1 SHAP (SHapley Additive exPlanations)
- **Method:** Use `shap.TreeExplainer` for tree-based candidate models (XGBoost / Random Forest).
- **Execution:**
  - Compute base value (expected average portfolio risk).
  - Compute SHAP values per feature for the specific project instance.
  - Rank features by absolute magnitude of positive contribution to risk score.
  - Return the top 3–5 features transformed into human-understandable administrative summaries.

---

## 5. Evaluation Protocol & Scientific Rigor

> [!CAUTION]
> **No Fabricated Benchmarks:**
> We explicitly avoid asserting invented accuracy metrics (such as claiming "98.7% accuracy") before model training. Metrics will be measured transparently once the benchmark dataset and training pipeline are executed.

### 5.1 Evaluation Metrics (Theoretical Standard)
- **Classification Metrics:**
  - **PR-AUC (Precision-Recall Area Under Curve):** Critical metric due to typical class imbalance in severe project failure.
  - **Recall on High/Critical Risk Cases:** Crucial to prevent false negatives (a failing multi-crore project incorrectly flagged as healthy).
  - **Macro F1-Score:** Ensures balanced performance across all risk tiers.
- **Continuous Calibration:**
  - Brier Score / Reliability curves to verify that a predicted 80% risk score truly corresponds to high real-world failure likelihood.

### 5.2 Validation Strategy
- Stratified $K$-Fold Cross Validation ($k=5$), stratified across risk categories and sectors.
- Holdout test split (20%) reserved strictly for final validation report.

---

## 6. Sourcing & Implementation Roadmap

| Phase | Milestone | Focus | Status |
|---|---|---|---|
| **Phase 1** | Data Strategy Formulation | Finalize between MoSPI extracted tables vs calibrated synthetic generator. | **PENDING RESEARCH** |
| **Phase 2** | Preprocessing & Pipeline | Implement Pydantic data schemas, feature transformers, and EVM baseline. | Next Step |
| **Phase 3** | Model Training & Tuning | Train candidate models, evaluate PR-AUC/Recall, select champion model. | Planned |
| **Phase 4** | SHAP Integration | Wire `TreeExplainer` to produce serializable JSON explainability payloads. | Planned |
| **Phase 5** | Artifact Serialization | Export trained models (`.joblib` / ONNX) and bundle into backend API service. | Planned |
