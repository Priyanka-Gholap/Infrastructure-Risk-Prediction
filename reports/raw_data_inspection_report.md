# Raw-Data Inspection Report: Infrastructure Project Monitoring Datasets
**Smart India Hackathon (SIH 2026) — Problem Statement 26103**  
*AI-Powered Predictive Analytics & Early Warning System for Infrastructure Project Monitoring*

---

## 1. Executive Summary

This report delivers a rigorous, non-destructive raw-data inspection of **8 monthly infrastructure project datasets** spanning **December 2025 to July 2026**, located in `d:\reports\`.

- **Source Integrity Guarantee**: All 8 original files remain **strictly untouched, unmerged, uncleaned, and unaltered**. No missing values were removed, no duplicates were dropped, no ML labels were assigned, and no features were selected or discarded.
- **Data Provenance**: Official monthly project flash reports published by the **Infrastructure Project Monitoring Division (IPMD)**, Ministry of Statistics and Programme Implementation (MoSPI), Government of India (PAIMANA portal).
- **Total Portfolio Scope**:
  - **14,573 total project-month records** monitored across 8 months.
  - **2,131 unique infrastructure projects** tracked across the national portfolio.
  - **1,079 projects appear continuously across all 8 months**, providing a robust longitudinal baseline for schedule delay and cost overrun tracking.

---

## 2. Monthly Dataset Inspections

```
Summary Portfolio Progression:
December 2025 : 1,392 rows | 8 columns | 1,392 unique projects
January 2026  : 1,702 rows | 8 columns | 1,702 unique projects
February 2026 : 1,948 rows | 8 columns | 1,948 unique projects
March 2026    : 1,941 rows | 8 columns | 1,941 unique projects
April 2026    : 1,981 rows | 8 columns | 1,981 unique projects
May 2026      : 1,987 rows | 8 columns | 1,987 unique projects
June 2026     : 1,847 rows | 8 columns | 1,847 unique projects
July 2026     : 1,775 rows | 8 columns | 1,775 unique projects
```

---

### 2.1 December 2025
- **File name**: `December_2025_copy.pdf`
- **Number of rows**: **1,392** ongoing project records (Master Table 6)
- **Number of columns**: **8** visual table columns (enclosing 14 decomposed fields)
- **All column names (Raw Table 6 Headers)**:
  1. `Sl.No`
  2. `Project Name (Agency) (Project Code)`
  3. `State`
  4. `Date of Approval (Start Date) MM/YYYY`
  5. `Orignal/Target DoC (Revised DoC) MM/YYYY`
  6. `Orignal Cost Revised Cost in Rs. Crore`
  7. `Cumulative Expenditure in Rs. Crore`
  8. `Physical Progress (%)`
- **Data type of each column**:
  - `Sl.No`: Integer string (`object`)
  - `Project Name (Agency) (Project Code)`: Multi-line string (`object`)
  - `State`: Text string (`object`)
  - `Date of Approval (Start Date) MM/YYYY`: Dual-date string (`object`)
  - `Orignal/Target DoC (Revised DoC) MM/YYYY`: Dual-date string (`object`)
  - `Orignal Cost Revised Cost in Rs. Crore`: Dual-numeric string (`object`)
  - `Cumulative Expenditure in Rs. Crore`: Numeric float string (`object`)
  - `Physical Progress (%)`: Numeric float string (`object`)
- **Number of missing values in each raw column**:
  - `Sl.No`: 0
  - `Project Name (Agency) (Project Code)`: 0
  - `State`: 0
  - `Date of Approval (Start Date) MM/YYYY`: 0
  - `Orignal/Target DoC (Revised DoC) MM/YYYY`: 0
  - `Orignal Cost Revised Cost in Rs. Crore`: 0
  - `Cumulative Expenditure in Rs. Crore`: 0
  - `Physical Progress (%)`: 0
- **Number of missing values in decomposed fields**:
  - `project_id`: 0
  - `project_name`: 0
  - `agency`: 0
  - `state`: 0
  - `date_of_approval`: 0
  - `start_date`: 0
  - `original_doc`: 0
  - `revised_doc`: 525 (Reported as `(-)`, indicating project has not received formal revision)
  - `original_cost`: 0
  - `revised_cost`: 0
  - `cumulative_expenditure`: 0
  - `physical_progress_pct`: 0
- **Number of duplicate rows**: **0**
- **Number of unique Project IDs**: **1,392** (100% unique, 0 missing)
- **Minimum and maximum values for important numeric fields**:
  - `original_cost`: Min = **₹100.00 Cr**, Max = **₹108,000.00 Cr** (Mean: ₹2,132.36 Cr, Median: ₹746.88 Cr)
  - `revised_cost`: Min = **₹103.68 Cr**, Max = **₹188,000.00 Cr** (Mean: ₹2,522.21 Cr, Median: ₹769.35 Cr)
  - `cumulative_expenditure`: Min = **₹0.00 Cr**, Max = **₹124,623.00 Cr** (Mean: ₹1,365.78 Cr, Median: ₹252.40 Cr)
  - `physical_progress_pct`: Min = **0.0%**, Max = **100.0%** (Mean: 55.66%, Median: 65.00%)
- **Date/month fields available**:
  - `Date of Approval`: `MM/YYYY`
  - `Start Date`: `MM/YYYY`
  - `Orignal/Target DoC`: `MM/YYYY`
  - `Revised DoC`: `MM/YYYY` (or `(-)`)

---

### 2.2 January 2026
- **File name**: `January_2026_copy.pdf`
- **Number of rows**: **1,702** ongoing project records
- **Number of columns**: **8** visual table columns
- **All column names (Raw Table 6 Headers)**:
  1. `Sl.No`
  2. `Project Name (Agency) (Project Code)`
  3. `State`
  4. `Date of Approval (Start Date) MM/YYYY`
  5. `Orignal/Target DoC (Revised DoC) MM/YYYY`
  6. `Orignal Cost Revised Cost in Rs. Crore`
  7. `Cumulative Expenditure in Rs. Crore`
  8. `Physical Progress (%)`
- **Data type of each column**:
  - All 8 table columns stored as text (`object`)
- **Number of missing values in each raw column**:
  - All raw table cells are fully populated (0 nulls in raw cells).
- **Number of missing values in decomposed fields**:
  - `project_id`: 0
  - `project_name`: 0
  - `agency`: 0
  - `state`: 1 (Recorded as blank in source table for a multi-state transmission line)
  - `date_of_approval`: 0
  - `start_date`: 0
  - `original_doc`: 0
  - `revised_doc`: 768 (`(-)` unrevised)
  - `original_cost`: 0
  - `revised_cost`: 0
  - `cumulative_expenditure`: 0
  - `physical_progress_pct`: 0
- **Number of duplicate rows**: **0**
- **Number of unique Project IDs**: **1,702** (100% unique, 0 missing)
- **Minimum and maximum values for important numeric fields**:
  - `original_cost`: Min = **₹100.00 Cr**, Max = **₹108,000.00 Cr** (Mean: ₹1,981.09 Cr, Median: ₹776.06 Cr)
  - `revised_cost`: Min = **₹0.10 Cr**, Max = **₹188,000.00 Cr** (Mean: ₹2,305.84 Cr, Median: ₹785.30 Cr)
  - `cumulative_expenditure`: Min = **₹-54.57 Cr** (Accounting adjustment in raw MoSPI data), Max = **₹124,623.00 Cr** (Mean: ₹1,176.20 Cr, Median: ₹210.29 Cr)
  - `physical_progress_pct`: Min = **0.0%**, Max = **100.0%** (Mean: 57.34%, Median: 67.00%)
- **Date/month fields available**:
  - `Date of Approval` (`MM/YYYY`), `Start Date` (`MM/YYYY`), `Original DoC` (`MM/YYYY`), `Revised DoC` (`MM/YYYY` / `(-)`)

---

### 2.3 February 2026
- **File name**: `February_2026_copy.pdf`
- **Number of rows**: **1,948** ongoing project records
- **Number of columns**: **8** visual table columns
- **All column names (Raw Table 6 Headers)**:
  1. `Sl.No`
  2. `Project Name (Agency) (Project Code) (Legacy OCMS Code)`
  3. `State`
  4. `Date of Approval (Start Date) MM/YYYY`
  5. `Orignal/Target DoC (Revised DoC) MM/YYYY`
  6. `Orignal Cost Revised Cost in Rs. Crore`
  7. `Cumulative Expenditure in Rs. Crore`
  8. `Physical Progress` *(Header dropped `(%)`)*
- **Data type of each column**:
  - Text strings (`object`)
- **Number of missing values in each raw column**: 0
- **Number of missing values in decomposed fields**:
  - `project_id`: 0
  - `state`: 1
  - `date_of_approval`: 0
  - `start_date`: 0
  - `original_doc`: 0
  - `revised_doc`: 963 (`(-)` unrevised)
  - `original_cost`: 0
  - `revised_cost`: 0
  - `cumulative_expenditure`: 0
  - `physical_progress_pct`: 0
- **Number of duplicate rows**: **0**
- **Number of unique Project IDs**: **1,948** (100% unique, 0 missing)
- **Minimum and maximum values for important numeric fields**:
  - `original_cost`: Min = **₹100.00 Cr**, Max = **₹108,000.00 Cr** (Mean: ₹1,864.52 Cr, Median: ₹777.16 Cr)
  - `revised_cost`: Min = **₹0.10 Cr**, Max = **₹188,000.00 Cr** (Mean: ₹2,155.38 Cr, Median: ₹776.90 Cr)
  - `cumulative_expenditure`: Min = **₹0.00 Cr**, Max = **₹124,623.00 Cr** (Mean: ₹1,012.04 Cr, Median: ₹202.08 Cr)
  - `physical_progress_pct`: Min = **0.0%**, Max = **100.0%** (Mean: 58.04%, Median: 67.00%)
- **Date/month fields available**:
  - `Date of Approval`, `Start Date`, `Original DoC`, `Revised DoC`

---

### 2.4 March 2026
- **File name**: `March_2026_copy.pdf`
- **Number of rows**: **1,941** ongoing project records
- **Number of columns**: **8** visual table columns
- **All column names (Raw Table 6 Headers)**:
  1. `Sl.No`
  2. `Project Name (Agency) (Project Code) (Legacy OCMS Code)`
  3. `State`
  4. `Date of Approval (Start Date) MM/YYYY`
  5. `Orignal/Target DoC (Revised DoC) MM/YYYY`
  6. `Orignal Cost Revised Cost in Rs. Crore`
  7. `Cumulative Expenditure in Rs. Crore`
  8. `Physical Progress`
- **Data type of each column**: Text strings (`object`)
- **Number of missing values in each raw column**: 0
- **Number of missing values in decomposed fields**:
  - `project_id`: 0, `state`: 1, `date_of_approval`: 0, `start_date`: 0, `original_doc`: 0, `revised_doc`: 347 (`(-)`), `original_cost`: 0, `revised_cost`: 0, `cumulative_expenditure`: 0, `physical_progress_pct`: 0
- **Number of duplicate rows**: **0**
- **Number of unique Project IDs**: **1,941** (100% unique, 0 missing)
- **Minimum and maximum values for important numeric fields**:
  - `original_cost`: Min = **₹102.40 Cr**, Max = **₹108,000.00 Cr** (Mean: ₹1,848.98 Cr, Median: ₹769.93 Cr)
  - `revised_cost`: Min = **₹0.10 Cr**, Max = **₹188,000.00 Cr** (Mean: ₹2,138.16 Cr, Median: ₹770.12 Cr)
  - `cumulative_expenditure`: Min = **₹0.00 Cr**, Max = **₹124,623.00 Cr** (Mean: ₹1,026.77 Cr, Median: ₹224.60 Cr)
  - `physical_progress_pct`: Min = **0.0%**, Max = **100.0%** (Mean: 60.30%, Median: 70.00%)
- **Date/month fields available**:
  - `Date of Approval`, `Start Date`, `Original DoC`, `Revised DoC`

---

### 2.5 April 2026
- **File name**: `April_2026_copy.pdf`
- **Number of rows**: **1,981** ongoing project records
- **Number of columns**: **8** visual table columns
- **All column names (Raw Table 6 Headers)**:
  1. `Sl.No`
  2. `Project Name (Agency) (Project Code) (Legacy OCMS Code) (PMGID)`
  3. `State`
  4. `Date of Approval (Start Date) MM/YYYY`
  5. `Orignal/Target DoC (Revised DoC) MM/YYYY`
  6. `Orignal Cost Revised Cost in Rs. Crore`
  7. `Cumulative Expenditure in Rs. Crore`
  8. `Physical Progress`
- **Data type of each column**: Text strings (`object`)
- **Number of missing values in each raw column**: 0
- **Number of missing values in decomposed fields**:
  - `project_id`: 0, `state`: 0, `date_of_approval`: 0, `start_date`: 0, `original_doc`: 0, `revised_doc`: 354 (`(-)`), `original_cost`: 0, `revised_cost`: 0, `cumulative_expenditure`: 0, `physical_progress_pct`: 0
- **Number of duplicate rows**: **0**
- **Number of unique Project IDs**: **1,981** (100% unique, 0 missing)
- **Minimum and maximum values for important numeric fields**:
  - `original_cost`: Min = **₹102.40 Cr**, Max = **₹108,000.00 Cr** (Mean: ₹1,874.14 Cr, Median: ₹790.78 Cr)
  - `revised_cost`: Min = **₹0.10 Cr**, Max = **₹188,000.00 Cr** (Mean: ₹2,159.72 Cr, Median: ₹786.91 Cr)
  - `cumulative_expenditure`: Min = **₹0.00 Cr**, Max = **₹124,623.00 Cr** (Mean: ₹1,027.82 Cr, Median: ₹226.46 Cr)
  - `physical_progress_pct`: Min = **0.0%**, Max = **100.0%** (Mean: 60.21%, Median: 70.00%)
- **Date/month fields available**:
  - `Date of Approval`, `Start Date`, `Original DoC`, `Revised DoC`

---

### 2.6 May 2026
- **File name**: `May_2026_copy.pdf`
- **Number of rows**: **1,987** ongoing project records
- **Number of columns**: **8** visual table columns
- **All column names (Raw Table 6 Headers)**:
  1. `Sl.No`
  2. `Project Name (Agency) (Project Code) (Legacy OCMS Code)`
  3. `State`
  4. `Date of Approval (Start Date) MM/YYYY`
  5. `Orignal/Target DoC (Revised DoC) MM/YYYY`
  6. `Orignal Cost Revised Cost in Rs. Crore`
  7. `Cumulative Expenditure in Rs. Crore`
  8. `Physical Progress`
- **Data type of each column**: Text strings (`object`)
- **Number of missing values in each raw column**: 0
- **Number of missing values in decomposed fields**:
  - `project_id`: 0, `state`: 0, `date_of_approval`: 0, `start_date`: 11 (Newly sanctioned projects with pending award), `original_doc`: 11, `revised_doc`: 352, `original_cost`: 0, `revised_cost`: 0, `cumulative_expenditure`: 0, `physical_progress_pct`: 0
- **Number of duplicate rows**: **0**
- **Number of unique Project IDs**: **1,987** (100% unique, 0 missing)
- **Minimum and maximum values for important numeric fields**:
  - `original_cost`: Min = **₹102.40 Cr**, Max = **₹108,000.00 Cr** (Mean: ₹1,867.00 Cr, Median: ₹785.79 Cr)
  - `revised_cost`: Min = **₹0.10 Cr**, Max = **₹188,000.00 Cr** (Mean: ₹2,138.68 Cr, Median: ₹782.18 Cr)
  - `cumulative_expenditure`: Min = **₹0.00 Cr**, Max = **₹124,623.00 Cr** (Mean: ₹1,097.98 Cr, Median: ₹226.57 Cr)
  - `physical_progress_pct`: Min = **0.0%**, Max = **100.0%** (Mean: 60.23%, Median: 70.00%)
- **Date/month fields available**:
  - `Date of Approval`, `Start Date`, `Original DoC`, `Revised DoC`

---

### 2.7 June 2026
- **File name**: `June_2026__copy.pdf`
- **Number of rows**: **1,847** ongoing project records
- **Number of columns**: **8** visual table columns
- **All column names (Raw Table 6 Headers)**:
  1. `Sl.No`
  2. `Project Name (Agency) (Project Code) (Legacy OCMS Code) (PMGID)`
  3. `State`
  4. `Date of Approval (Start Date) MM/YYYY`
  5. `Orignal/Target DoC (Revised DoC) MM/YYYY`
  6. `Orignal Cost Revised Cost in Rs. Crore`
  7. `Cumulative Expenditure in Rs. Crore`
  8. `Physical Progress`
- **Data type of each column**: Text strings (`object`)
- **Number of missing values in each raw column**: 0
- **Number of missing values in decomposed fields**:
  - `project_id`: 0, `state`: 0, `date_of_approval`: 0, `start_date`: 0, `original_doc`: 0, `revised_doc`: 308, `original_cost`: 0, `revised_cost`: 0, `cumulative_expenditure`: 0, `physical_progress_pct`: 0
- **Number of duplicate rows**: **0**
- **Number of unique Project IDs**: **1,847** (100% unique, 0 missing)
- **Minimum and maximum values for important numeric fields**:
  - `original_cost`: Min = **₹102.40 Cr**, Max = **₹108,000.00 Cr** (Mean: ₹1,928.38 Cr, Median: ₹808.99 Cr)
  - `revised_cost`: Min = **₹0.10 Cr**, Max = **₹188,000.00 Cr** (Mean: ₹2,195.17 Cr, Median: ₹810.02 Cr)
  - `cumulative_expenditure`: Min = **₹0.00 Cr**, Max = **₹124,623.00 Cr** (Mean: ₹1,189.31 Cr, Median: ₹263.01 Cr)
  - `physical_progress_pct`: Min = **0.0%**, Max = **100.0%** (Mean: 58.85%, Median: 66.32%)
- **Date/month fields available**:
  - `Date of Approval`, `Start Date`, `Original DoC`, `Revised DoC`

---

### 2.8 July 2026
- **File name**: `July_2026__copy.pdf`
- **Number of rows**: **1,775** ongoing project records
- **Number of columns**: **8** visual table columns
- **All column names (Raw Table 6 Headers)**:
  1. `Sl.No`
  2. `Project Name (Agency) (Project Code) (Legacy OCMS Code) (PMGID)`
  3. `State`
  4. `Date of Approval (Start Date) MM/YYYY`
  5. `Orignal/Target DoC (Revised DoC) MM/YYYY`
  6. `Orignal Cost Revised Cost in Rs. Crore`
  7. `Cumulative Expenditure in Rs. Crore`
  8. `Physical Progress`
- **Data type of each column**: Text strings (`object`)
- **Number of missing values in each raw column**: 0
- **Number of missing values in decomposed fields**:
  - `project_id`: 0, `state`: 0, `date_of_approval`: 0, `start_date`: 0, `original_doc`: 0, `revised_doc`: 348, `original_cost`: 0, `revised_cost`: 0, `cumulative_expenditure`: 0, `physical_progress_pct`: 0
- **Number of duplicate rows**: **0**
- **Number of unique Project IDs**: **1,775** (100% unique, 0 missing)
- **Minimum and maximum values for important numeric fields**:
  - `original_cost`: Min = **₹102.40 Cr**, Max = **₹108,000.00 Cr** (Mean: ₹1,898.67 Cr, Median: ₹797.36 Cr)
  - `revised_cost`: Min = **₹0.10 Cr**, Max = **₹124,005.00 Cr** (Mean: ₹2,090.50 Cr, Median: ₹802.45 Cr)
  - `cumulative_expenditure`: Min = **₹0.00 Cr**, Max = **₹124,623.00 Cr** (Mean: ₹1,085.13 Cr, Median: ₹276.66 Cr)
  - `physical_progress_pct`: Min = **0.0%**, Max = **100.0%** (Mean: 59.00%, Median: 66.74%)
- **Date/month fields available**:
  - `Date of Approval`, `Start Date`, `Original DoC`, `Revised DoC`

---

## 3. Cross-Dataset Comparative Analysis

### 3.1 Columns Common to All Months
1. **Visual Table Columns**:
   - `Sl.No`
   - `State`
   - `Date of Approval (Start Date) MM/YYYY`
   - `Orignal/Target DoC (Revised DoC) MM/YYYY`
   - `Orignal Cost Revised Cost in Rs. Crore`
   - `Cumulative Expenditure in Rs. Crore`
2. **Decomposed Logical Columns (Semantic fields present across all 8 files)**:
   - `sl_no` (Project sequential identifier)
   - `ministry` (Administrative Central Ministry)
   - `sector` (Infrastructure sub-sector)
   - `project_name` (Name and scope description)
   - `agency` (Implementing Central Agency / PSU)
   - `project_id` (Nodal PAIMANA Project Identification Code)
   - `state` (State or Union Territory)
   - `date_of_approval` (Sanction Date `MM/YYYY`)
   - `start_date` (Execution Start Date `MM/YYYY`)
   - `original_doc` (Original Target Completion Date `MM/YYYY`)
   - `revised_doc` (Revised Target Completion Date `MM/YYYY` / `(-)`)
   - `original_cost` (Sanctioned Original Cost in ₹ Crore)
   - `revised_cost` (Sanctioned Revised Cost in ₹ Crore)
   - `cumulative_expenditure` (Actual Spend to Date in ₹ Crore)
   - `physical_progress_pct` (Reported Work Progress %)

---

### 3.2 Columns with Different Names Representing the Same Information
- **Project Details Column (Column 2)**:
  - `Project Name (Agency) (Project Code)` *(Dec 25 – Jan 26)*
  - `Project Name / (Agency) / (Project Code) (Legacy OCMS Code)` *(Feb, Mar, May 26)*
  - `Project Name / (Agency) / (Project Code) (Legacy OCMS Code) (PMGID)` *(Apr, Jun, Jul 26)*
  - *Synthesis*: All three variants convey the fundamental project identity (`project_name`, `agency`, and `project_id`), while later months appended cross-reference codes to legacy OCMS and PMG databases.
- **Physical Progress Column (Column 8)**:
  - `Physical Progress (%)` *(Dec 25 – Jan 26)*
  - `Physical Progress` *(Feb 26 – Jul 26)*
  - *Synthesis*: Both represent the certified cumulative physical execution progress percentage.

---

### 3.3 Columns Appearing Only in Some Months
- `Legacy OCMS Code`: Introduced in **February 2026**; present in Feb, Mar, Apr, May, Jun, and Jul 2026. Absent in Dec 2025 and Jan 2026.
- `PMGID` (Project Monitoring Group ID): Introduced in **April 2026**; present in Apr, Jun, and Jul 2026. (Omitted from May 2026 header).
- In monthly completion records (**Table 3**): `Actual Date of Completion` and `Completion Cost` appear exclusively in Table 3.

---

### 3.4 Functional Column Classifications

| Requirement Category | Candidate / Mapped Column(s) in Raw Data | Decomposed Representation | Format & Units |
|---|---|---|---|
| **Possible Project ID Column** | `Project Name (Agency) (Project Code)` [Primary]<br>`(Legacy OCMS Code)` [Secondary]<br>`(PMGID)` [Tertiary] | `project_id`<br>`legacy_ocms_code`<br>`pmgid` | 5–7 digit integer string (`612786`)<br>Alphanumeric string (`N04000106`)<br>Integer string (`4353`) |
| **Possible Project Cost Columns** | `Orignal Cost Revised Cost in Rs. Crore` [Table 6]<br>`Completion Cost in Rs. Crore` [Table 3] | `original_cost`<br>`revised_cost`<br>`completion_cost` | Numeric float, ₹ in Crores |
| **Possible Expenditure Columns** | `Cumulative Expenditure in Rs. Crore` [Table 6 & Table 3] | `cumulative_expenditure` | Numeric float, ₹ in Crores |
| **Possible Physical Progress Columns** | `Physical Progress (%)` / `Physical Progress` | `physical_progress_pct` | Numeric float / percentage (`0.0` to `100.0`) |
| **Original Completion Date Columns** | `Orignal/Target DoC (Revised DoC) MM/YYYY` [Upper Line] | `original_doc` | Date string, `MM/YYYY` |
| **Revised / Final Completion Date Columns** | `Orignal/Target DoC (Revised DoC) MM/YYYY` [Lower Line]<br>`Actual Date of Completion` [Table 3] | `revised_doc`<br>`actual_doc` | Date string, `MM/YYYY` (or `(-)` if unrevised) |
| **Original Cost Columns** | `Orignal Cost Revised Cost in Rs. Crore` [Upper Line] | `original_cost` | Numeric float, ₹ in Crores |
| **Revised / Final Cost Columns** | `Orignal Cost Revised Cost in Rs. Crore` [Lower Line]<br>`Completion Cost in Rs. Crore` [Table 3] | `revised_cost`<br>`completion_cost` | Numeric float, ₹ in Crores |

---

## 4. Longitudinal Project ID Tracking & Persistence

### 4.1 Persistence Distribution Across Months
A total of **2,131 unique Project IDs** were tracked across all 8 monthly files. The longitudinal persistence distribution demonstrates that the vast majority of projects remain active across monthly snapshots:

| Persistence Duration | Number of Unique Projects | Percentage of Total Projects | Cumulative Percentage |
|---|---|---|---|
| **Appears in 8 Months (Continuous)** | **1,079 projects** | **50.6%** | 50.6% |
| **Appears in 7 Months** | **398 projects** | **18.7%** | 69.3% |
| **Appears in 6 Months** | **368 projects** | **17.3%** | 86.6% |
| **Appears in 5 Months** | **58 projects** | **2.7%** | 89.3% |
| **Appears in 4 Months** | **89 projects** | **4.2%** | 93.5% |
| **Appears in 3 Months** | **66 projects** | **3.1%** | 96.6% |
| **Appears in 2 Months** | **30 projects** | **1.4%** | 98.0% |
| **Appears in 1 Month Only** | **43 projects** | **2.0%** | 100.0% |

> [!NOTE]
> **86.6% of all unique projects (1,845 projects)** persist across 6 or more monthly reporting cycles, confirming that this multi-month collection provides true longitudinal monitoring trajectories suitable for early warning modeling.

---

### 4.2 Pairwise Overlap Matrix (Count of Shared Project IDs)

The table below shows the exact number of overlapping `project_id` values between any two monthly datasets:

| Month | Dec 2025 | Jan 2026 | Feb 2026 | Mar 2026 | Apr 2026 | May 2026 | Jun 2026 | Jul 2026 |
|---|---|---|---|---|---|---|---|---|
| **Dec 2025** (1,392) | **1,392** | 1,388 | 1,367 | 1,351 | 1,336 | 1,309 | 1,187 | 1,095 |
| **Jan 2026** (1,702) | 1,388 | **1,702** | 1,678 | 1,661 | 1,646 | 1,617 | 1,485 | 1,387 |
| **Feb 2026** (1,948) | 1,367 | 1,678 | **1,948** | 1,919 | 1,902 | 1,873 | 1,716 | 1,617 |
| **Mar 2026** (1,941) | 1,351 | 1,661 | 1,919 | **1,941** | 1,924 | 1,895 | 1,737 | 1,637 |
| **Apr 2026** (1,981) | 1,336 | 1,646 | 1,902 | 1,924 | **1,981** | 1,951 | 1,791 | 1,687 |
| **May 2026** (1,987) | 1,309 | 1,617 | 1,873 | 1,895 | 1,951 | **1,987** | 1,825 | 1,719 |
| **Jun 2026** (1,847) | 1,187 | 1,485 | 1,716 | 1,737 | 1,791 | 1,825 | **1,847** | 1,732 |
| **Jul 2026** (1,775) | 1,095 | 1,387 | 1,617 | 1,637 | 1,687 | 1,719 | 1,732 | **1,775** |

---

### 4.3 Longitudinal Trajectory Case Studies (Observed in Raw Data)

Inspection of individual Project IDs confirms that operational distress signals (slippages and cost revisions) evolve dynamically over time in the raw records:

#### Case Study 1: Kadapa Airport Terminal Building (`Project ID: 612786`)
- **Agency**: Airport Authority of India (AAI) | **State**: Andhra Pradesh | **Original Cost**: ₹265.91 Cr
- **Dec 2025**: Original DoC: `01/2026`, Revised DoC: `03/2026` (+2 mo delay), Spend: ₹88.87 Cr, Progress: 46%
- **Feb 2026**: Original DoC: `01/2026`, Revised DoC: `05/2026` (+4 mo delay), Spend: ₹104.54 Cr, Progress: 53%
- **Apr 2026**: Original DoC: `01/2026`, Revised DoC: `07/2026` (+6 mo delay), Spend: ₹129.07 Cr, Progress: 65%
- **Jul 2026**: Original DoC: `01/2026`, Revised DoC: `09/2026` (+8 mo delay), Spend: ₹176.38 Cr, Progress: 80%
- *Observation*: Steady monthly schedule slippage (target repeatedly pushed back 2 months at a time) while expenditure and progress advance steadily.

#### Case Study 2: Vijayawada Airport Terminal Building (`Project ID: 701107`)
- **Agency**: Airport Authority of India (AAI) | **State**: Andhra Pradesh | **Original Cost**: ₹611.80 Cr
- **Dec 2025**: Revised Cost: ₹611.80 Cr, Revised DoC: `03/2026`, Spend: ₹523.14 Cr, Progress: 87.0%
- **Feb 2026**: Revised Cost: ₹611.80 Cr, Revised DoC: `07/2026`, Spend: ₹523.14 Cr, Progress: 87.0%
- **Apr 2026**: Revised Cost: ₹611.80 Cr, Revised DoC: `10/2026`, Spend: ₹523.14 Cr, Progress: 87.2%
- **Jul 2026**: **Revised Cost Jumped to ₹824.28 Cr** (+₹212.48 Cr / +34.7% cost overrun!), Revised DoC: `11/2026`, Spend: ₹572.99 Cr, Progress: 89.7%
- *Observation*: Stagnant progress at ~87% for over 5 months, followed by an official budget revision (+34.7%) and further completion deadline pushback.

---

## 5. Compliance with Strict Inspection Rules
- **No ML labels created**: Target columns or risk labels (`Delay Risk`, `Cost Overrun Risk`) have not been assigned.
- **No missing values imputed or removed**: Source records containing `(-)` for revised dates or missing state names were left intact.
- **No duplicate filtering executed**: Datasets reflect natural row frequencies.
- **No column drops or ML pruning**: All administrative, regional, and reference columns were preserved.
- **Zero modification to source files**: All 8 files in `d:\reports\` retain their original timestamps and byte sizes.
