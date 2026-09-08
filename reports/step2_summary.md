# Step 2 Executive Summary: Target Design & Prediction-Point Analysis
**SIH Problem Statement 26103**: AI-Powered Predictive Analytics & Early Warning System for Infrastructure Project Monitoring

---

## 1. What the Empirical Data Supports

1. **Longitudinal Grounding**:
   - Out of 234 completed projects in Table 3, **217 (92.7%)** possess prior Table 6 monthly monitoring history.
   - For all projects completed after December 2025 (Jan–Jul 2026), the prior tracking rate is **100.0% (217 / 217)**.
2. **Cost Overrun Dynamics**:
   - **22.2% of completed projects (52 projects)** experienced a net cost increase over their original approved budget.
   - **16.2% of completed projects (38 projects)** experienced $\ge 10\%$ cost overrun over original budget.
   - Only **7.0% of projects (11 projects)** exceeded their *revised budget*, because administrative revisions are continually updated upward to accommodate cost escalations before commissioning.
3. **Schedule Delay Dynamics**:
   - **94.9% of completed projects (222 of 234)** finished AFTER their original deadline.
   - Average schedule delay against original target completion date is **36.8 months (3.1 years)**, and median delay is **25.0 months (2.1 years)**.
   - A naive binary threshold of $\ge 0$ days or $\ge 30$ days against original DoC creates an extreme 95% / 5% class imbalance.
   - Measuring delay beyond the *latest revised deadline* yields a balanced split: **56.7% delayed $\ge 30$ days** vs **43.3% on schedule**.
4. **Prediction Cutoff Feasibility**:
   - A fixed lifecycle cutoff (e.g. at 20%, 40%, or 60% of planned duration) is **statistically unfeasible** on this 8-month window because all projects completing in 2026 had already elapsed >100% of their planned duration years earlier (0 completed projects observable at 20% lifecycle).
   - A **Fixed Lead-Time Snapshot Strategy ($T-2$ or $T-3$ Months before Completion)** is highly feasible and operationally realistic, yielding **201 to 212 clean, un-leaked training examples**.

---

## 2. Most Defensible Target Definitions

### Cost Overrun: Definition A (Completion Cost vs Original Sanctioned Budget)
- **Primary Metric**: $\text{cost\_overrun\_percent} = \frac{\text{completion\_cost} - \text{original\_cost}}{\text{original\_cost}} \times 100$.
- **Recommended Binary Modeling Threshold**: **$\ge 10.0\%$ Budget Escalation** (38 positive / 196 negative, 16.2% positive rate).
- *Reasoning*: Measures true public fund escalation. Evaluating against revised cost suffers severe label masking because budgets are revised upward to cover cost increases.

### Schedule Delay: Dual-Target Architecture
1. **Continuous Regression**: `delay_from_original_months` (retains full variance: 0 to 209 months).
2. **Binary Early Warning Classifier**: **Delay beyond Latest Sanctioned Revision ($\ge 60$ Days / 2 Months)**.
   - Class Split: **120 positive (51.5%) vs 113 negative (48.5%)** — exceptionally balanced.
   - Alternative Binary Target: **Major Chronic Original Delay ($\ge 24$ Months / 2 Years)**: **123 positive (52.6%) vs 111 negative (47.4%)**.

---

## 3. Usable Training Examples Feasibility

| Training Strategy | Completed Projects Available | Usable Cost Targets | Usable Delay Targets | Feature Snapshot Timing |
|---|---|---|---|---|
| **Single Snapshot ($T-1$ Month)** | 217 | 217 | 217 | 30 days prior to completion |
| **Single Snapshot ($T-2$ Months)** | **212** | **212** | **212** | **60 days prior to completion (Recommended)** |
| **Single Snapshot ($T-3$ Months)** | **201** | **201** | **201** | **90 days prior to completion (Quarterly Early Warning)** |
| **Pooled Multi-Snapshot Panel** | 217 projects | 1,081 rows | 1,081 rows | Variable (1 to 7 months prior to completion; requires GroupKFold) |

---

## 4. Major Leakage Risks Identified & Guardrails

1. **Table 3 Values are Target-Only**: `actual_date_of_completion`, `completion_cost`, Table 3 `revised_doc`, and Table 3 `revised_cost` must never be used as inputs to the model.
2. **Temporal Cutoff Enforcement**: All predictive features must be derived strictly from observations at or before $t_{pred}$. Any data from future months ($t > t_{pred}$) constitutes leakage.
3. **Grouped Cross-Validation**: If using multi-snapshot panel training (1,081 rows), `GroupKFold` on `project_id` must be enforced so that snapshots from the same project never appear in both training and validation folds.

---

## 5. Generated Deliverables

The following artifacts and datasets have been created in [`d:\reports\`](file:///d:/reports):
- [`completed_project_outcome_analysis.csv`](file:///d:/reports/completed_project_outcome_analysis.csv): 234 completed projects with full outcome metrics and Table 6 historical tracking.
- [`target_threshold_analysis.csv`](file:///d:/reports/target_threshold_analysis.csv): 26 evaluated binary thresholds across cost and delay.
- [`prediction_cutoff_analysis.csv`](file:///d:/reports/prediction_cutoff_analysis.csv): 8 evaluated cutoff strategies.
- [`target_leakage_audit.csv`](file:///d:/reports/target_leakage_audit.csv): 21 audited fields classified into Safe, Potential Leakage, or Outcome-Only.
- [`step2_target_recommendation.md`](file:///d:/reports/step2_target_recommendation.md): Complete technical specification and rationale.
- [`step2_summary.md`](file:///d:/reports/step2_summary.md): This executive summary.

---

## 6. DO NOT PROCEED YET: Decisions Requiring Human Review

Before proceeding to Step 3 (Feature Engineering):
1. **Approve Binary Cost Overrun Threshold**: Confirm **$\ge 10\%$ Overrun over Original Cost** (16.2% positive rate) vs **$\ge 0\%$ (Any Cost Increase, 26.5%)**.
2. **Approve Binary Delay Target**: Confirm **$\ge 60$ Days Delay beyond Revised Deadline** (51.5% split) vs **Major Chronic Delay ($\ge 24$ Months beyond Original DoC, 52.6% split)**.
3. **Approve Prediction Lead Time**: Confirm **60-day early warning horizon ($T-2$, 212 examples)** vs **90-day quarterly horizon ($T-3$, 201 examples)**.
4. **Confirm Imputation of 19 Table 3 Projects with Actual DoC = NA**: Confirm using `report_month` as the effective completion month for these 19 projects.
