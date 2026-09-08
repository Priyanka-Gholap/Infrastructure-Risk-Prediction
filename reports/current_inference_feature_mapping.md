# Current Project Inference Dataset — Feature Mapping Specification (Step 6B)

**Project:** SIH Problem Statement 26103 — AI-Powered Predictive Analytics & Early Warning System for Infrastructure Project Monitoring  
**Pipeline Stage:** Step 6B (Feature Mapping Specification)  
**Authoritative Sources:** Step 3 Feature Dictionary (`reports/step3_feature_dictionary.csv`), Production Feature Schema (`ml/schemas/production_feature_schema.csv`)  

---

## 1. Overview & Architectural Boundaries

This specification defines the authoritative mathematical and procedural mapping from MoSPI/IPMD Table 6 monthly monitoring records to the **36 locked `SAFE_MVP` production features** in `current_inference_dataset.csv`.

Every feature is engineered using historical data strictly $\le$ the project's selected latest observation month ($T$). Zero completion outcome data from Table 3 is utilized.

---

## 2. Dataset Structure

The dataset contains:
1. **3 Project Lookup / Identification Metadata Columns:** Not passed into ML models; reserved for FastAPI project lookup and dashboard visualization.
2. **32 Numerical Features:** Passed into the `num` transformer of the Scikit-Learn pipeline (Median Imputer).
3. **4 Categorical Features:** Passed into the `cat` transformer of the Scikit-Learn pipeline (`Unknown` Imputer + OneHotEncoder).

Total columns: **39 columns**.

---

## 3. Detailed Feature Mapping Table

### A. Project Identification / Lookup Metadata
| Column Name | Source Column | Derivation / Logic | Data Type | Role |
| :--- | :--- | :--- | :--- | :--- |
| `project_id` | Table 6: `project_id` | Unique MoSPI project identifier | String | Primary Lookup Key |
| `project_name` | Table 6: `project_name` | Official infrastructure project title | String | Human-Readable Metadata |
| `snapshot_month` | Table 6: `report_month` | Latest observed report month ($T$) | String (YYYY-MM) | Temporal Snapshot Marker |

---

### B. Baseline & Pre-Construction Features (Numerical)
| # | Feature Name | Source Fields | Mathematical Formula / Derivation | Missing Handling |
| :-: | :--- | :--- | :--- | :--- |
| 1 | `original_cost` | Table 6: `original_cost` | Baseline sanctioned expenditure ceiling in INR Crores. | None missing in Table 6. |
| 2 | `approval_to_start_months` | Table 6: `start_date`, `date_of_approval` | $(\text{start\_date} - \text{date\_of\_approval})$ in calendar months. Measures gestation lead time. | `NaN` if approval date missing; median imputed. |

---

### C. Financial Progress Features (Numerical)
| # | Feature Name | Source Fields | Mathematical Formula / Derivation | Missing Handling |
| :-: | :--- | :--- | :--- | :--- |
| 3 | `cumulative_expenditure` | Table 6: `cumulative_expenditure` | Total capital disbursed up to snapshot $T$ in INR Crores. | None missing in Table 6. |
| 4 | `expenditure_percent_of_original_cost` | Table 6: `cumulative_expenditure`, `original_cost` | $\frac{\text{cumulative\_expenditure}}{\text{original\_cost}} \times 100.0$ | `NaN` if cost $\le 0$; median imputed. |
| 5 | `monthly_expenditure_change` | Table 6: `cumulative_expenditure` ($T$, $T-1$) | $\text{expenditure}(T) - \text{expenditure}(T-1)$ | `NaN` if $T-1$ missing; median imputed. |
| 6 | `monthly_expenditure_growth_pct` | Table 6: `cumulative_expenditure` ($T$, $T-1$) | $\frac{\text{exp}(T) - \text{exp}(T-1)}{\text{exp}(T-1)} \times 100.0$ | `NaN` if $T-1$ missing or 0; median imputed. |

---

### D. Physical Progress Features (Numerical)
| # | Feature Name | Source Fields | Mathematical Formula / Derivation | Missing Handling |
| :-: | :--- | :--- | :--- | :--- |
| 7 | `physical_progress_pct` | Table 6: `physical_progress_pct` | Cumulative reported physical execution percentage at snapshot $T$. | None missing in Table 6. |
| 8 | `monthly_progress_change` | Table 6: `physical_progress_pct` ($T$, $T-1$) | $\text{progress}(T) - \text{progress}(T-1)$ in percentage points. | `NaN` if $T-1$ missing; median imputed. |
| 9 | `progress_growth_rate` | Table 6: `physical_progress_pct` ($T$, $T-1$) | $\frac{\text{phys}(T) - \text{phys}(T-1)}{\text{phys}(T-1)} \times 100.0$ | `NaN` if $T-1$ missing or 0; median imputed. |

---

### E. Schedule Progression Features (Numerical)
| # | Feature Name | Source Fields | Mathematical Formula / Derivation | Missing Handling |
| :-: | :--- | :--- | :--- | :--- |
| 10 | `planned_duration_months` | Table 6: `start_date`, `original_doc` | $(\text{original\_doc} - \text{start\_date})$ in calendar months. | `NaN` if dates missing; median imputed. |
| 11 | `elapsed_months` | Table 6: `start_date`, `report_month` | $(\text{snapshot\_month} - \text{start\_date})$ in calendar months. | `NaN` if start date missing; median imputed. |
| 12 | `remaining_planned_months` | Table 6: `original_doc`, `report_month` | $(\text{original\_doc} - \text{snapshot\_month})$ in months (negative if deadline breached). | `NaN` if DoC missing; median imputed. |
| 13 | `elapsed_duration_ratio` | Derived: `elapsed_months`, `planned_duration_months` | $\frac{\text{elapsed\_months}}{\text{planned\_duration\_months}}$ | `NaN` if duration $\le 0$; median imputed. |
| 14 | `is_past_original_doc` | Table 6: `original_doc`, `report_month` | $1.0$ if $\text{snapshot\_month} > \text{original\_doc}$ else $0.0$. | $0.0$ if DoC missing. |

---

### F. Interaction & Analytical Benchmarks (Numerical)
| # | Feature Name | Source Fields | Mathematical Formula / Derivation | Missing Handling |
| :-: | :--- | :--- | :--- | :--- |
| 15 | `efficiency_gap` | Derived: `physical_progress_pct`, `expenditure_percent_of_original_cost` | $\text{physical\_progress\_pct} - \text{expenditure\_percent\_of\_original\_cost}$ | `NaN` if components missing; median imputed. |
| 16 | `cost_physical_ratio` | Derived: `expenditure_percent_of_original_cost`, `physical_progress_pct` | $\frac{\text{expenditure\_percent\_of\_original\_cost}}{\text{physical\_progress\_pct}}$ | `NaN` if progress $\le 0$; median imputed. |
| 17 | `expected_progress_pct` | Derived: `elapsed_duration_ratio` | $\min(100.0, \max(0.0, \text{elapsed\_duration\_ratio} \times 100.0))$ | `NaN` if ratio missing; median imputed. |
| 18 | `progress_gap_pct_points` | Derived: `physical_progress_pct`, `expected_progress_pct` | $\text{physical\_progress\_pct} - \text{expected\_progress\_pct}$ | `NaN` if components missing; median imputed. |

---

### G. Longitudinal & Trend Features (Numerical)
| # | Feature Name | Source Fields | Mathematical Formula / Derivation | Missing Handling |
| :-: | :--- | :--- | :--- | :--- |
| 19 | `months_since_first_observation` | Table 6: `report_month` stream | Number of calendar months between earliest Table 6 observation and snapshot $T$. | Computed for all projects ($0$ to $7$). |
| 20 | `observation_count_to_date` | Table 6: count of rows | Total monthly observations recorded for this project up to $T$. | Integer count ($1$ to $8$). |
| 21 | `physical_progress_1_month_change` | Table 6: `physical_progress_pct` ($T$, $T-1$) | $\text{phys}(T) - \text{phys}(T-1)$ | `NaN` if $T-1$ missing; median imputed. |
| 22 | `physical_progress_2_month_change` | Table 6: `physical_progress_pct` ($T$, $T-2$) | $\text{phys}(T) - \text{phys}(T-2)$ | `NaN` if $T-2$ missing; median imputed. |
| 23 | `expenditure_1_month_change` | Table 6: `cumulative_expenditure` ($T$, $T-1$) | $\text{exp}(T) - \text{exp}(T-1)$ | `NaN` if $T-1$ missing; median imputed. |
| 24 | `expenditure_2_month_change` | Table 6: `cumulative_expenditure` ($T$, $T-2$) | $\text{exp}(T) - \text{exp}(T-2)$ | `NaN` if $T-2$ missing; median imputed. |
| 25 | `progress_trend_slope` | Table 6: historical progress | $\frac{\text{phys}(T) - \text{phys}(\text{first})}{\text{months\_since\_first\_observation}}$ if months $>0$ else $0.0$. | `NaN` if single observation; median imputed. |
| 26 | `expenditure_trend_slope` | Table 6: historical expenditure | $\frac{\text{exp}(T) - \text{exp}(\text{first})}{\text{months\_since\_first\_observation}}$ if months $>0$ else $0.0$. | `NaN` if single observation; median imputed. |

---

### H. Data Quality & Schedule Anomaly Flags (Numerical / Binary)
| # | Feature Name | Source Fields | Mathematical Formula / Derivation | Values |
| :-: | :--- | :--- | :--- | :---: |
| 27 | `negative_expenditure_flag` | Table 6: `cumulative_expenditure` | $1$ if $\text{cumulative\_expenditure} < 0$ else $0$. | $0$ or $1$ |
| 28 | `missing_previous_month_flag` | Table 6: $T-1$ presence | $1$ if $T-1$ record missing or incomplete else $0$. | $0$ or $1$ |
| 29 | `invalid_duration_flag` | Derived: `planned_duration_months` | $1$ if $\text{planned\_duration\_months} \le 0$ or missing else $0$. | $0$ or $1$ |
| 30 | `past_original_doc_flag` | Derived: `is_past_original_doc` | $1$ if project has breached original deadline at snapshot else $0$. | $0$ or $1$ |
| 31 | `missing_key_date_flag` | Table 6: `start_date`, `original_doc` | $1$ if either `start_date` or `original_doc` is missing else $0$. | $0$ or $1$ |
| 32 | `suspicious_value_flag` | Table 6: progress & expenditure | $1$ if $\text{phys} \notin [0, 100]$ or $\text{exp\_pct} \notin [0, 300]$ else $0$. | $0$ or $1$ |

---

### I. Administrative & Geographic Context (Categorical)
| # | Feature Name | Source Column | Cleaning & Standardizing Rules | Pipeline Encoding |
| :-: | :--- | :--- | :--- | :--- |
| 33 | `ministry` | Table 6: `ministry` | Cleaned of PDF page header OCR artifacts via historical lookup and agency mapping. | `Unknown` imputer + OneHotEncoder |
| 34 | `sector` | Table 6: `sector` | Preserved as verified 22 infrastructure sectors. | `Unknown` imputer + OneHotEncoder |
| 35 | `implementing_agency` | Table 6: `implementing_agency` | Preserved as reported executing agency. | `Unknown` imputer + OneHotEncoder |
| 36 | `state` | Table 6: `state` | Preserved as reported State/UT or Multi-State region. | `Unknown` imputer + OneHotEncoder |

---

## 4. Pipeline Compatibility Certification

The above 36 features in their numbered sequence (1 to 36) exactly match the feature expectations of:
1. `cost_overrun_model.joblib` (RandomForestClassifier, $\tau = 0.40$)
2. `delay_model.joblib` (RandomForestClassifier, $\tau = 0.50$)
3. `delay_regressor.joblib` (RandomForestRegressor)
4. `ml/schemas/production_feature_schema.csv`
5. `ml/schemas/inference_input_schema.json`
