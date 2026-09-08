# Step 2 — Target / Label Design & Prediction-Point Analysis
**SIH Problem Statement 26103**: AI-Powered Predictive Analytics & Early Warning System for Infrastructure Project Monitoring  
**Dataset Grounding**: 14,573 Table 6 Project-Month Records & 234 Table 3 Completed Project Outcomes (Dec 2025 – Jul 2026)

---

## 1. Executive Summary & Objective

The objective of Step 2 is to analyze the empirical distributions of completed project outcomes from MoSPI Table 3, evaluate candidate target formulations for **Cost Overrun** and **Schedule Delay**, investigate valid prediction cutoff strategies, and identify temporal leakage risks.

### Key Empirical Findings:
1. **Historical Traceability**: **217 of the 234 completed projects (92.7%)** possess prior Table 6 monitoring snapshots. For all projects completed between January 2026 and July 2026, the prior tracking rate is **100.0% (217 / 217)**.
2. **Cost Overrun Distribution**:
   - **22.2% of completed projects (52 projects)** experienced a net cost increase over their original budget.
   - **16.2% of projects (38 projects)** experienced $\ge 10\%$ cost overrun over original budget.
   - Conversely, only **7.0% of projects (11 projects)** exceeded their *revised budget*, because administrative revisions are continually updated upward to accommodate cost escalations before commissioning.
3. **Schedule Delay Distribution**:
   - **94.9% of completed projects (222 of 234)** finished AFTER their original deadline.
   - Mean delay against original target completion date is **36.8 months (3.1 years)**, and median delay is **25.0 months (2.1 years)**.
   - A naive binary threshold of $\ge 0$ days or $\ge 30$ days against original DoC creates an extreme 95% / 5% class imbalance.
   - Measuring delay beyond the *latest revised deadline* yields a balanced split: **56.7% delayed $\ge 30$ days** vs **43.3% on schedule**.
4. **Prediction Cutoff Feasibility**:
   - A fixed lifecycle cutoff (e.g. at 20%, 40%, or 60% of planned duration) is **statistically unfeasible** on this 8-month window because all projects completing in 2026 had already elapsed >100% of their planned duration years earlier (0 completed projects observable at 20% lifecycle).
   - A **Fixed Lead-Time Snapshot Strategy ($T-2$ or $T-3$ Months before Completion)** is highly feasible and operationally realistic, yielding **201 to 212 clean, un-leaked training examples**.

---

## 2. Completed Project Outcome Analysis (Table 3 Joined with Table 6)

Each of the 234 completed projects in Table 3 was linked with its prior Table 6 monthly monitoring history using `project_id`.

```
Completed Projects Summary:
- Total Completed Projects in Table 3: 234
- With Prior Table 6 Monitoring Snapshots: 217 (92.7%)
- Unmatched (All in Dec 2025 initial month): 17 (7.3%)
- Distribution of Prior Monthly Observations:
    1 prior observation  : 5 projects
    2 prior observations : 11 projects
    3 prior observations : 23 projects
    4 prior observations : 31 projects
    5 prior observations : 29 projects
    6 prior observations : 105 projects
    7 prior observations : 13 projects
```

---

## 3. Cost Outcome Analysis & Definition Comparison

### 3.1 Empirical Distributions

| Metric | Min | 25th %ile | Median | Mean | 75th %ile | Max |
|---|---|---|---|---|---|---|
| **Original Cost (₹ Cr)** | ₹100.00 | ₹293.34 | ₹666.45 | ₹1,472.43 | ₹1,315.57 | ₹43,129.00 |
| **Completion Cost (₹ Cr)** | ₹0.00 | ₹212.83 | ₹450.97 | ₹1,458.21 | ₹991.36 | ₹70,293.57 |
| **Absolute Cost Change (`Comp - Orig`)** | -₹2,836.43 | -₹226.77 | -₹65.04 | -₹14.23 | ₹0.00 | ₹27,164.57 |
| **Cost Overrun % vs Original Cost** | -100.0% | -39.4% | -18.9% | -17.8% | 0.0% | **+136.6%** |
| **Cost Overrun % vs Revised Cost** *(N=157)* | -100.0% | -36.6% | -18.4% | -23.9% | -6.2% | **+60.9%** |

### 3.2 Candidate Binary Cost Overrun Thresholds (N = 234)

| Threshold | Baseline: Original Cost (Pos / Neg) | Baseline: Original Cost (%) | Baseline: Revised Cost (Pos / Neg) | Baseline: Revised Cost (%) |
|---|---|---|---|---|
| **$\ge 0\%$ Overrun** | 62 / 172 | **26.5% / 73.5%** | 11 / 146 | **7.0% / 93.0%** |
| **$\ge 5\%$ Overrun** | 42 / 192 | **17.9% / 82.1%** | 3 / 154 | **1.9% / 98.1%** |
| **$\ge 10\%$ Overrun** | 38 / 196 | **16.2% / 83.8%** | 3 / 154 | **1.9% / 98.1%** |
| **$\ge 20\%$ Overrun** | 26 / 208 | **11.1% / 88.9%** | 2 / 155 | **1.3% / 98.7%** |
| **$\ge 30\%$ Overrun** | 19 / 215 | **8.1% / 91.9%** | 1 / 156 | **0.6% / 99.4%** |

### 3.3 Comparison: Definition A vs Definition B for Cost Overrun

- **Definition A (`completion_cost` vs `original_cost`)**:
  - *Question Answered*: Did this project escalate beyond the original public investment approved at inception?
  - *Domain Significance*: Represents true taxpayer capital escalation. 22.2% of projects experienced cost growth, and 16.2% had $\ge 10\%$ cost overrun.
  - *Risk of Bias*: In some completed projects, completion expenditure is reported lower than original sanction (73.5% underrun), which may reflect partial scope commissioning or final retention bills still pending settlement.
- **Definition B (`completion_cost` vs `revised_cost`)**:
  - *Question Answered*: Did this project violate its latest administrative budget sanction?
  - *Severe Masking Risk*: When costs rise, ministries formally sanction a higher revised cost. As a result, only 1.9% of completed projects exceed their revised budget by $\ge 5\%$. Evaluating overrun against revised cost creates a severe, artificial label masking where 93% of projects are labeled "no overrun" despite having doubled their original budgets.
- **Recommendation**: **Use Definition A (`completion_cost` vs `original_cost`) as the primary Cost Overrun target**.

---

## 4. Schedule Delay Outcome Analysis & Definition Comparison

### 4.1 Empirical Distributions

| Metric | Min | 25th %ile | Median | Mean | 75th %ile | Max |
|---|---|---|---|---|---|---|
| **Delay vs Original DoC (Months)** | -49.0 mo | +14.0 mo | **+25.0 mo** | **+36.8 mo** | +44.8 mo | **+209.0 mo** |
| **Delay vs Original DoC (Days)** | -1,491 days | +424 days | **+760 days** | **+1,120 days** | +1,368 days | **+6,360 days** |
| **Delay vs Revised DoC (Months)** *(N=233)* | -9.0 mo | 0.0 mo | **+2.0 mo** | **+5.5 mo** | +7.0 mo | **+144.0 mo** |
| **Delay vs Revised DoC (Days)** *(N=233)* | -273 days | 0 days | **+61 days** | **+166 days** | +214 days | **+4,383 days** |

### 4.2 Candidate Binary Delay Thresholds

| Threshold | Delay vs Original DoC (Pos / Neg) | Delay vs Original DoC (%) | Delay vs Revised DoC (Pos / Neg) | Delay vs Revised DoC (%) |
|---|---|---|---|---|
| **$\ge 0$ Days (Months $\ge 0$)** | 224 / 10 | **95.7% / 4.3%** | 221 / 12 | **94.8% / 5.2%** |
| **$\ge 30$ Days (Months $\ge 1$)** | 222 / 12 | **94.9% / 5.1%** | 132 / 101 | **56.7% / 43.3%** |
| **$\ge 60$ Days (Months $\ge 2$)** | 222 / 12 | **94.9% / 5.1%** | 120 / 113 | **51.5% / 48.5%** |
| **$\ge 90$ Days (Months $\ge 3$)** | 219 / 15 | **93.6% / 6.4%** | 109 / 124 | **46.8% / 53.2%** |
| **$\ge 180$ Days (Months $\ge 6$)** | 214 / 20 | **91.5% / 8.5%** | 73 / 160 | **31.3% / 68.7%** |
| **$\ge 12$ Months (1 Year)** | 185 / 49 | **79.1% / 20.9%** | 44 / 189 | **18.9% / 81.1%** |
| **$\ge 24$ Months (2 Years)** | 123 / 111 | **52.6% / 47.4%** | 18 / 215 | **7.7% / 92.3%** |

### 4.3 Comparison: Definition A vs Definition B for Delay

- **Definition A (`actual_completion` vs `original_doc`)**:
  - Over 94% of completed infrastructure projects suffer schedule slippage beyond the original contractual deadline.
  - Setting a binary threshold at $\ge 0$ days or $\ge 30$ days is **unsuitable for binary ML** because a dummy classifier predicting "Delayed" will achieve 95% accuracy without learning any signals.
  - However, Definition A is **ideal for Continuous Regression** (`delay_months`), and produces a well-balanced binary split if defined as **Major Schedule Delay ($\ge 24$ Months / 2 Years)**: **52.6% positive vs 47.4% negative**.
- **Definition B (`actual_completion` vs `revised_doc`)**:
  - Setting a binary threshold at **$\ge 30$ Days (1 Month) beyond the latest sanctioned deadline** produces a naturally balanced binary target: **56.7% positive vs 43.3% negative**.
  - Setting a binary threshold at **$\ge 90$ Days (1 Quarter) beyond revised deadline** yields **46.8% positive vs 53.2% negative**.
- **Recommendation**:
  1. Primary Continuous Target: `delay_from_original_months` (Regression).
  2. Primary Binary Early Warning Target: **Schedule Delay beyond Latest Sanctioned Revision ($\ge 60$ days or $\ge 2$ months)** (51.5% vs 48.5% split).
  3. Alternative Macro Target: **Chronic Original Schedule Delay ($\ge 24$ months)** (52.6% vs 47.4% split).

---

## 5. Prediction Cutoff Strategy Evaluation

| Strategy ID | Strategy Name | Usable Completed Examples | Early Warning Lead Time | Evaluation Assessment |
|---|---|---|---|---|
| **Approach 1** | Last Prior Observation ($T-1$ / $T-2$) | **217 projects** | 1 to 2 months | Maximum sample size. Excellent baseline, but lead time is short. |
| **Approach 2** | Fixed Lifecycle (20%, 40%, 60%) | **0 to 3 projects** | Early lifecycle | **Unfeasible**. Historical projects in 2026 had already elapsed >100% of planned duration. |
| **Approach 3** | Fixed Lead Time at $T-2$ Months | **212 projects** | $\ge 2$ months (60 days) | **Highly Recommended**. Realistic 60-day operational warning window. |
| **Approach 3b** | Fixed Lead Time at $T-3$ Months | **201 projects** | $\ge 3$ months (1 quarter) | **Highly Recommended**. Realistic 90-day quarterly warning window. |
| **Approach 4** | Pooled Multi-Snapshot Panel | **1,081 observations** | 1 to 7 months | High sample size, but requires strict `GroupKFold` by `project_id` to prevent leakage. |

---

## 6. Target Leakage Audit Classification

The complete field audit has been saved to [`target_leakage_audit.csv`](file:///d:/reports/target_leakage_audit.csv):

| Column Name | Classification | Leakage Risk Level | Strict Rule |
|---|---|---|---|
| `actual_date_of_completion` | **OUTCOME / TARGET ONLY** | **CRITICAL (100% Leakage)** | Banned from model inputs. Used solely to compute delay ground truth. |
| `completion_cost` | **OUTCOME / TARGET ONLY** | **CRITICAL (100% Leakage)** | Banned from model inputs. Used solely to compute cost overrun ground truth. |
| `revised_doc` *(from Table 3)* | **OUTCOME / TARGET ONLY** | **HIGH LEAKAGE** | Banned from model inputs. Contains post-hoc final deadline revisions. |
| `revised_cost` *(from Table 3)* | **OUTCOME / TARGET ONLY** | **HIGH LEAKAGE** | Banned from model inputs. Contains final sanctioned budget at closeout. |
| `revised_doc` *(from Table 6 snapshot)* | **POTENTIAL LEAKAGE / TEMPORAL CAUTION** | **MEDIUM CAUTION** | Permitted ONLY if taken strictly from the observation snapshot month ($t_{pred}$). Banned if taken from any future month. |
| `revised_cost` *(from Table 6 snapshot)* | **POTENTIAL LEAKAGE / TEMPORAL CAUTION** | **MEDIUM CAUTION** | Permitted ONLY if taken strictly from the observation snapshot month ($t_{pred}$). |
| `cumulative_expenditure` *(at $t_{pred}$)* | **SAFE AT PREDICTION TIME** | **NONE** | Cumulative disbursements certified up to observation date. |
| `physical_progress_pct` *(at $t_{pred}$)* | **SAFE AT PREDICTION TIME** | **NONE** | Cumulative physical completion certified up to observation date. |
| `date_of_approval`, `start_date`, `original_doc`, `original_cost` | **SAFE AT PREDICTION TIME** | **NONE** | Project baseline parameters fixed at inception. |
| `ministry`, `sector`, `state`, `implementing_agency` | **SAFE AT PREDICTION TIME** | **NONE** | Categorical project metadata known at inception. |

---

## 7. Formal Step 2 Recommendations

### Recommendation 1: Cost Overrun Target Definition
- **Target Name**: `cost_overrun_pct` (Continuous) and `cost_overrun_binary` (Binary).
- **Formula**:
  $$\text{cost\_overrun\_pct} = \frac{\text{completion\_cost} - \text{original\_cost}}{\text{original\_cost}} \times 100$$
- **Recommended Modeling Threshold**: **$\ge 10.0\%$ Overrun over Original Cost** (38 positive / 196 negative, 16.2% positive rate). Identifies projects with significant capital escalation while avoiding minor budget noise.

### Recommendation 2: Schedule Delay Target Definition
- **Dual Target Architecture**:
  1. **Continuous Regression**: `delay_from_original_months` (Mean: 36.8 mo, Median: 25.0 mo).
  2. **Binary Early Warning Classifier**: **Delay beyond Latest Sanctioned Revision ($\ge 60$ days / 2 months)**.
     - Formula: $\text{delay\_from\_revised\_days} = \text{actual\_completion} - \text{revised\_doc}$.
     - Class Split: **120 positive (51.5%) vs 113 negative (48.5%)** — ideal balanced distribution.
     - Domain Meaning: Predicts whether the project will fail to meet its current approved government milestone deadline.

### Recommendation 3: Prediction Cutoff Strategy
- For the MVP, adopt a **Fixed Lead-Time Snapshot Strategy at $T-2$ or $T-3$ Months before Completion** using **One Training Snapshot per Completed Project** (201 to 212 clean examples).
- *Rationale*: Guarantees that the early warning alert fires at least 60 to 90 days before project completion, giving monitoring officers actionable lead time, while eliminating artificial group leakage across folds.

---

## 8. DO NOT PROCEED YET: Human Review Checklist

The following decisions must be reviewed and agreed upon before proceeding to Step 3 (Feature Engineering):

1. **Target Formulation Alignment**:
   - Do you approve using **$\ge 10\%$ Overrun over Original Cost** as the binary Cost Overrun threshold (16.2% positive rate), or do you prefer **$\ge 0\%$ (Any Cost Growth, 26.5%)**?
   - Do you approve using **$\ge 60$ Days Delay beyond Revised Deadline** as the binary Delay threshold (51.5% balanced split), or do you prefer **Major Original Delay ($\ge 24$ Months, 52.6% split)**?
2. **Prediction Lead Time ($T-2$ vs $T-3$)**:
   - Do you prefer a **60-day ($T-2$) lead time** (212 usable completed training projects) or a **90-day ($T-3$) quarterly lead time** (201 usable completed training projects)?
3. **Handling of 19 Table 3 Projects with Actual DoC = NA**:
   - Is using `report_month` as the effective completion month acceptable for these 19 projects, or should they be excluded from the delay target evaluation?
