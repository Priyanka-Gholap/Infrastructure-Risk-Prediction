# Extraction & Standardization Summary Report
**SIH Problem Statement 26103**: AI-Powered Predictive Analytics & Early Warning System for Infrastructure Project Monitoring  
**Dataset Scope**: 8 Monthly MoSPI/IPMD Flash Reports (December 2025 – July 2026)

---

## 1. Portfolio Extraction Overview

The Step 1 extraction and standardization process successfully converted 8 published MoSPI PDF reports into unified, tabular project-month records without any data loss, transformation, or imputation.

| Metric | Table 6: Master Monitoring Records | Table 3: Completed Projects Records | Combined Total |
|---|---|---|---|
| **Total Rows Extracted** | **14,573** project-month observations | **234** completed project records | **14,807** records |
| **Unique Project IDs** | **2,131** unique projects | **234** unique projects | **2,148** unique projects across both tables |
| **Missing Project IDs** | **0** (100% resolved) | **0** (100% resolved) | **0** |
| **Duplicate Rows** | **0** duplicate records | **0** duplicate records | **0** |
| **Total Source PDF Pages Scanned** | 1,204 pages | 26 pages | 1,204 pages |

---

## 2. Monthly Row Counts & Progression

The monthly monitoring portfolio expanded steadily from December 2025 through May 2026 as line ministries onboarded legacy and newly sanctioned projects onto PAIMANA, followed by a major commissioning wave in June 2026:

| Report Month | File Name | Table 6 Rows (Ongoing) | Table 3 Rows (Completed) | Newly Added in Month | Ongoing Line Ministries |
|---|---|---|---|---|---|
| **2025-12** | `December_2025_copy.pdf` | 1,392 | 17 | 20 | 17 |
| **2026-01** | `January_2026_copy.pdf` | 1,702 | 3 | 203 | 17 |
| **2026-02** | `February_2026_copy.pdf` | 1,948 | 9 | 268 | 17 |
| **2026-03** | `March_2026_copy.pdf` | 1,941 | 25 | 12 | 17 |
| **2026-04** | `April_2026_copy.pdf` | 1,981 | 9 | 55 | 17 |
| **2026-05** | `May_2026_copy.pdf` | 1,987 | 16 | 35 | 17 |
| **2026-06** | `June_2026__copy.pdf` | 1,847 | 130 | 17 | 17 |
| **2026-07** | `July_2026__copy.pdf` | 1,775 | 25 | 36 | 17 |
| **Total** | — | **14,573** | **234** | **646** | — |

---

## 3. Table 3 ↔ Table 6 Matching & Linkage Analysis

To determine whether historical monitoring trajectories in Table 6 can be linked to final project outcomes in Table 3:

- **Total Completed Projects in Table 3**: 234 projects
- **Matched with Prior Table 6 Monitoring Trajectories**: **217 projects (92.7%)**
- **Unmatched Table 3 Projects**: **17 projects (7.3%)**

### Monthly Linkage Breakdown:
- **December 2025**: **0 / 17 matched**. (December 2025 is the first available report month; projects completed in or before December 2025 were never monitored as ongoing within this dataset).
- **January 2026**: **3 / 3 (100.0%)** matched with December 2025 ongoing records.
- **February 2026**: **9 / 9 (100.0%)** matched with prior ongoing records.
- **March 2026**: **25 / 25 (100.0%)** matched with prior ongoing records.
- **April 2026**: **9 / 9 (100.0%)** matched with prior ongoing records.
- **May 2026**: **16 / 16 (100.0%)** matched with prior ongoing records.
- **June 2026**: **130 / 130 (100.0%)** matched with prior ongoing records.
- **July 2026**: **25 / 25 (100.0%)** matched with prior ongoing records.

> [!IMPORTANT]
> **100% Tracking Rate Post-December**: For every month after December 2025, **100% of all completed projects** were actively monitored in Table 6 during earlier months. This enables constructing longitudinal panel features leading up to realized project outcomes.

---

## 4. Missing Values, Duplicates & Data Quality Audit

### 4.1 Missing Values
- `project_id`, `project_name`, `ministry`, `sector`, `implementing_agency`: **0 missing values** across all 14,573 records.
- `original_cost`, `revised_cost`, `cumulative_expenditure`, `physical_progress_pct`: **0 missing values**.
- `date_of_approval`: **0 missing values**.
- `state`: **2 records missing** (`project_id: 612885` in Jan & Feb 2026, `project_id: 617272` in Mar 2026) due to empty cells in source PDF.
- `start_date` & `original_doc`: **11 records missing** in May 2026 (newly sanctioned projects pending contract award).
- `revised_doc`: **3,965 records missing** (represented as `NULL`). These correspond to raw `(-)` entries indicating that the project has not received an approved completion deadline revision.

### 4.2 Duplicate Integrity
- **Within-month duplicates**: **0**. The combination of `(report_month, project_id)` forms a strictly unique primary key.
- **Across-month duplicates**: Projects naturally repeat across months (panel structure). Over 86.6% of projects persist across 6 to 8 monthly reports.

### 4.3 Unusual Values Flagged for Review
1. **Negative Cumulative Expenditure**:
   - `report_month: 2026-01`, `project_id: 618451`: Reported cumulative expenditure of **-₹54.57 Cr** (accounting credit adjustment).
2. **Nominal / Placeholder Revised Costs**:
   - Several projects report `revised_cost = ₹0.10 Cr` (e.g., `project_id: 617947`, `project_id: 618751`) despite an `original_cost` over ₹1,000 Cr.
3. **Mega-Budget Projects**:
   - `project_id: 400010` and `project_id: 701113`: Sanctioned budgets up to **₹108,000 Cr** (Mumbai-Ahmedabad Bullet Train).
4. **Inverted Date Sequences**:
   - In rare projects (e.g., `project_id: 618090`), `start_date` was entered after `original_doc` due to retrospective project restructuring.

---

## 5. Generated Artifacts & File Deliverables

The following standardized datasets and documentation files are now produced and verified:

1. [`standardized_table6_project_month.csv`](file:///d:/reports/standardized_table6_project_month.csv): 14,573 project-month records (18 standardized columns).
2. [`standardized_table3_completed_projects.csv`](file:///d:/reports/standardized_table3_completed_projects.csv): 234 completed project records (19 standardized columns).
3. [`data_quality_report.csv`](file:///d:/reports/data_quality_report.csv): 26 categorized data-quality issue logs with severity classifications.
4. [`raw_to_standardized_mapping.md`](file:///C:/Users/Priyanka%20Durvesh/.gemini/antigravity/brain/635324cd-763d-4ac7-be67-c51610ba85e2/raw_to_standardized_mapping.md): Field-by-field mapping rules and special value conventions.
5. [`extraction_summary.md`](file:///C:/Users/Priyanka%20Durvesh/.gemini/antigravity/brain/635324cd-763d-4ac7-be67-c51610ba85e2/extraction_summary.md): This comprehensive summary.

---

## 6. DO NOT PROCEED YET: Human Review Checklist

Before creating prediction timestamps, engineering features, or formulating delay/cost-overrun ML labels, the following design decisions require human review and consensus:

1. **Negative Cumulative Expenditure Handling**:
   - How should the single -₹54.57 Cr record (`project_id: 618451` in Jan 2026) be treated during feature engineering? Should it be clamped to ₹0.00 Cr, replaced with the prior month's spend, or flagged as an accounting revision indicator?
2. **Placeholder Revised Cost Imputation Policy**:
   - For records where `revised_cost = ₹0.10 Cr` (while `original_cost > ₹1,000 Cr`), should downstream feature engineering default `revised_cost` to `original_cost` (i.e., cost escalation ratio = 0) to avoid artificial negative cost overrun ratios?
3. **Target Formulation for Completed Projects**:
   - For the 217 matched completed projects from Table 3:
     - Should **Delay** be defined as `actual_date_of_completion - original_doc` (original schedule slippage) or `actual_date_of_completion - revised_doc` (slippage beyond revised deadline)?
     - Should **Cost Overrun** be defined as `completion_cost - original_cost` (overall cost escalation) or `completion_cost - revised_cost` (escalation beyond sanctioned revision)?
4. **Prediction Cutoff Timestamps**:
   - For ongoing projects that have not yet appeared in Table 3, what observation horizon ($T_0$) should be chosen for early warning prediction (e.g., predict outcome at 20%, 40%, or 60% of planned lifecycle duration)?
