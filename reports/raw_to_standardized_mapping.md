# Raw to Standardized Data Mapping Specification
**SIH Problem Statement 26103**: AI-Powered Predictive Analytics & Early Warning System for Infrastructure Project Monitoring

---

## 1. Overview & Mapping Philosophy
This document formalizes the mapping and decomposition rules applied to convert raw, visual table layouts from the 8 official MoSPI/IPMD monthly monitoring reports (December 2025 to July 2026) into structured, machine-readable datasets.

**Core Principles Maintained:**
- **Zero Raw Alteration**: Original PDF documents were read without modifying byte content or layout.
- **No Early ML Filtering**: No columns were dropped, no rows were removed, and no synthetic imputations were applied.
- **Full Structural Decomposition**: Visual table cells packing multiple pieces of information (e.g., project name, agency, project ID, dates, and costs) were systematically decomposed into distinct, typed logical fields.
- **Consistent Unit Preservation**: All financial metrics strictly preserve the government publication unit (**₹ in Crores**).

---

## 2. Table 6: "All Ongoing Projects" Mapping Schema

Table 6 is the primary master monitoring portfolio in each monthly report. In the original PDFs, Table 6 is presented as an 8-column visual grid. These 8 visual columns are mapped and decomposed into **18 standardized logical columns**.

| # | Standardized Column | Data Type | Source Location in Raw PDF | Transformation & Normalization Rules |
|---|---|---|---|---|
| 1 | `report_month` | String (`YYYY-MM`) | Document metadata / Header | Standardized to ISO month format: `2025-12`, `2026-01`, ..., `2026-07`. |
| 2 | `sl_no` | Integer (`int64`) | Column 1 (`Sl.No`) | Sequential integer index of the project within that monthly report (1 to N). |
| 3 | `ministry` | String (`object`) | Preceding Section Header | Extracted from table section banner spanning across columns (e.g., `Ministry of Civil Aviation`, `Ministry of Railways`). |
| 4 | `sector` | String (`object`) | Preceding Sub-Section Header | Extracted from sub-section banner (e.g., `Aviation & Aviation Infrastructure`, `Roads and Bridges`). |
| 5 | `project_name` | String (`object`) | Column 2 (Upper lines) | Text block describing project scope, stripped of implementing agency and identifier codes. |
| 6 | `implementing_agency`| String (`object`) | Column 2 (Middle line) | Extracted from parenthesized agency string (e.g., `(Airport Authority of India [AAI])`, `(NHAI)`). |
| 7 | `project_id` | String (`object`) | Column 2 (Parentheses) | **Primary Key**: Extracted 5–7 digit numeric code (e.g., `612786`, `701107`). Stored as string to preserve leading digits. |
| 8 | `legacy_ocms_code` | String (`object`) | Column 2 (Bottom line, Feb–Jul) | Alphanumeric legacy OCMS code (e.g., `N04000106`). Set to `NULL` for Dec 2025 – Jan 2026 where not published. |
| 9 | `pmgid` | String (`object`) | Column 2 (Bottom line, Apr, Jun, Jul) | Project Monitoring Group numeric identifier (e.g., `4353`). Set to `NULL` where not present or reported as `(-)`. |
| 10 | `state` | String (`object`) | Column 3 (`State`) | Indian State, UT, or `Multi-States (...)`. Trimmed of whitespace. |
| 11 | `date_of_approval` | String (`YYYY-MM`) | Column 4 (Top line) | Approval/sanction date. Converted from `MM/YYYY` to `YYYY-MM`. |
| 12 | `start_date` | String (`YYYY-MM`) | Column 4 (Bottom line) | Actual or scheduled commencement date. Converted from `(MM/YYYY)` to `YYYY-MM`. |
| 13 | `original_doc` | String (`YYYY-MM`) | Column 5 (Top line) | Originally targeted Date of Completion. Converted from `MM/YYYY` to `YYYY-MM`. |
| 14 | `revised_doc` | String (`YYYY-MM`) | Column 5 (Bottom line) | Latest approved or anticipated Date of Completion. Converted from `(MM/YYYY)` to `YYYY-MM`. If reported as `(-)`, mapped to `NULL`. |
| 15 | `original_cost` | Float (`float64`) | Column 6 (Top line) | Original approved cost in **₹ Crore**. Commas removed and parsed as float. |
| 16 | `revised_cost` | Float (`float64`) | Column 6 (Bottom line) | Latest sanctioned cost in **₹ Crore**. Extracted from `(Cost)` format and parsed as float. |
| 17 | `cumulative_expenditure`| Float (`float64`) | Column 7 (`Cumulative Expenditure`) | Realized expenditure up to snapshot date in **₹ Crore**. Parsed as float. |
| 18 | `physical_progress_pct` | Float (`float64`) | Column 8 (`Physical Progress`) | Physical progress percentage (0.0 to 100.0). Trailing `%` stripped and parsed as float. |

---

## 3. Table 3: "Completed Projects During Month" Mapping Schema

Table 3 contains project-level outcomes for schemes commissioned during that reporting month. The 7 visual columns are mapped into **19 standardized logical columns**.

| # | Standardized Column | Data Type | Source Location in Raw PDF | Transformation & Normalization Rules |
|---|---|---|---|---|
| 1 | `report_month` | String (`YYYY-MM`) | Document metadata | Month of completion report (`2025-12` to `2026-07`). |
| 2 | `sl_no` | Integer (`int64`) | Column 1 (`Sl.No`) | Sequential index of completed project in that month. |
| 3 | `ministry` | String (`object`) | Preceding Section Header | Central Line Ministry. |
| 4 | `sector` | String (`object`) | Preceding Sub-Section Header | Infrastructure sector. |
| 5 | `project_name` | String (`object`) | Column 2 (Upper lines) | Project title. |
| 6 | `implementing_agency`| String (`object`) | Column 2 (Middle line) | Executing agency/PSU. |
| 7 | `project_id` | String (`object`) | Column 2 (Bottom line) | **Join Key**: 5–7 digit project identifier matching Table 6. |
| 8 | `legacy_ocms_code` | String (`object`) | Column 2 (Optional code) | Alphanumeric legacy code if present. |
| 9 | `pmgid` | String (`object`) | Column 2 (Optional code) | PMG code if present. |
| 10 | `state` | String (`object`) | Column 3 (`State`) | State or Union Territory. |
| 11 | `date_of_approval` | String (`YYYY-MM`) | Column 4 (Top line) | Government approval date. |
| 12 | `start_date` | String (`YYYY-MM`) | Column 4 (Bottom line) | Commencement date. |
| 13 | `original_doc` | String (`YYYY-MM`) | Column 5 (Line 2 in Dec-May, Jul; Line 1 in Jun) | Originally planned target completion date (`YYYY-MM`). |
| 14 | `revised_doc` | String (`YYYY-MM`) | Column 5 (Line 3 in Dec-May, Jul; Line 2 in Jun) | Latest anticipated completion date prior to completion. |
| 15 | `actual_date_of_completion` | String (`YYYY-MM`) | Column 5 (Line 1 in Dec-May, Jul; Report month in Jun) | **Ground Truth Outcome Date**: Realized completion date (`YYYY-MM`). |
| 16 | `original_cost` | Float (`float64`) | Column 6 (Top line) | Originally approved budget in **₹ Crore**. |
| 17 | `revised_cost` | Float (`float64`) | Column 6 (Bottom line) | Sanctioned revised cost in **₹ Crore**. |
| 18 | `completion_cost` | Float (`float64`) | Column 7 (`Cumulative Expenditure`) | **Realized Final Cost**: Realized expenditure at completion in **₹ Crore**. |
| 19 | `cumulative_expenditure`| Float (`float64`) | Column 7 (`Cumulative Expenditure`) | Total funds disbursed at completion. |

---

## 4. Special Value Handling & Edge Case Rules

### 4.1 Unrevised Dates (`revised_doc = '-'`)
- In government project reporting, a dash `(-)` under `(Revised DoC)` signifies that **no formal administrative deadline revision has been sanctioned**.
- In the standardized CSV (`standardized_table6_project_month.csv`), this is represented as an empty/`NULL` string.
- *Semantic Meaning*: The project is officially targeted against its `original_doc`, or a revision proposal is currently under departmental review.

### 4.2 Negative Expenditure (`cumulative_expenditure < 0`)
- Observed in January 2026 for `project_id: 618451` (`-₹54.57 Cr`).
- *Preservation Rule*: The raw negative float is preserved exactly as published. It is flagged in `data_quality_report.csv` as an accounting adjustment/credit entry rather than being clamped or zeroed out.

### 4.3 Extremely Low Revised Costs (`revised_cost < ₹1.00 Cr`)
- Several projects report a nominal `revised_cost` of `₹0.10 Cr` alongside an `original_cost` exceeding `₹1,000 Cr`.
- *Preservation Rule*: The raw float is preserved unchanged. It indicates a portal placeholder/unpopulated revision entry.

### 4.4 Header Evolution of Column 2 Across Reports
- **Dec 2025 & Jan 2026**: Header reads `Project Name (Agency) (Project Code)`.
- **Feb 2026, Mar 2026, May 2026**: Header reads `Project Name (Agency) (Project Code) (Legacy OCMS Code)`.
- **Apr 2026, Jun 2026, Jul 2026**: Header reads `Project Name (Agency) (Project Code) (Legacy OCMS Code) (PMGID)`.
- *Normalization Rule*: The parser dynamically searches trailing parenthesized tokens from the bottom of the cell to decouple `legacy_ocms_code` and `pmgid` into independent columns, ensuring that `project_id` and `project_name` remain 100% consistent across all 8 months.
