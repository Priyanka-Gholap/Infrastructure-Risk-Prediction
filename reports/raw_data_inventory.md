# Raw-Data Inventory: MoSPI Infrastructure Project Monitoring Reports (Dec 2025 – Jul 2026)

## 1. Dataset Overview & Inventory Scope
This document provides a complete inventory of the 8 monthly infrastructure project monitoring datasets provided for **SIH Problem Statement 26103** (*AI-Powered Predictive Analytics & Early Warning System for Infrastructure Project Monitoring*).

All 8 files are official publications from the **Infrastructure Project Monitoring Division (IPMD)**, Ministry of Statistics and Programme Implementation (MoSPI), Government of India, generated from the **PAIMANA Portal** (`ipm.mospi.gov.in` / `paimana-proj.mospi.gov.in`). Each report covers Central Sector Infrastructure Projects costing ₹150 Crore and above.

---

## 2. File-Level Inventory

| Month | File Name | File Size (Bytes) | Format | Total Pages | Master Table Start Page | Master Table End Page | Total Projects Monitored |
|---|---|---|---|---|---|---|---|
| **December 2025** | `December_2025_copy.pdf` | 6,395,474 | PDF 1.7 | 108 | Page 50 | Page 107 | **1,392** |
| **January 2026** | `January_2026_copy.pdf` | 6,541,448 | PDF 1.7 | 134 | Page 62 | Page 134 | **1,702** |
| **February 2026** | `February_2026_copy.pdf` | 6,734,807 | PDF 1.7 | 168 | Page 65 | Page 168 | **1,948** |
| **March 2026** | `March_2026_copy.pdf` | 6,869,186 | PDF 1.7 | 158 | Page 55 | Page 158 | **1,941** |
| **April 2026** | `April_2026_copy.pdf` | 6,540,352 | PDF 1.7 | 163 | Page 55 | Page 163 | **1,981** |
| **May 2026** | `May_2026_copy.pdf` | 6,457,213 | PDF 1.7 | 159 | Page 54 | Page 159 | **1,987** |
| **June 2026** | `June_2026__copy.pdf` | 6,536,686 | PDF 1.7 | 161 | Page 59 | Page 161 | **1,847** |
| **July 2026** | `July_2026__copy.pdf` | 6,447,598 | PDF 1.7 | 153 | Page 55 | Page 153 | **1,775** |
| **Total Portfolio** | **8 Files** | **51.52 MB** | — | **1,204 Pages** | — | — | **14,573 project-month observations** (2,131 unique projects) |

---

## 3. Structural Table Architecture Per File
Each of the 8 monthly PDF files contains a standardized 6-part tabular appendix:

| Table Identifier | Table Title | Granularity | Description & Purpose | Typical Page Extent |
|---|---|---|---|---|
| **Table 1** | *Ministry-wise Ongoing Projects* | Ministry aggregate | Aggregated count, original cost, revised cost, and cumulative spend by line ministry | 1–2 pages |
| **Table 2** | *State-wise Ongoing Projects* | State/UT aggregate | Aggregated count, original cost, revised cost, and cumulative spend across Indian States/UTs | 8–9 pages |
| **Table 3** | *Completed Projects During Month* | Project level | Central sector projects commissioned/completed within that calendar month | 1–8 pages |
| **Table 4** | *Newly Added Projects During Month* | Project level | Central sector projects sanctioned and onboarded to PAIMANA within that month | 2–11 pages |
| **Table 5** | *Ongoing Projects of North-East Region* | Project level | Regional subset of active projects located within the 8 North-Eastern states | 8–13 pages |
| **Table 6** | *All Ongoing Projects* | Project level | **Master Portfolio Table**: Comprehensive project-by-project monitoring record of all active projects | **58–108 pages** |

---

## 4. Master Table (Table 6) Raw Visual Columns

Across all 8 monthly files, Table 6 is formatted as an 8-column tabular grid:

| Column Position | Visual Column Header in Report | Evolution Across Months | Data Encapsulated |
|---|---|---|---|
| **Col 1** | `Sl.No` | Unchanged (Dec 2025 – Jul 2026) | Sequential project index (`1` to `N`) |
| **Col 2** | `Project Name (Agency) (Project Code)` *(Dec 25 - Jan 26)*<br>`Project Name / (Agency) / (Project Code) (Legacy OCMS Code)` *(Feb, Mar, May 26)*<br>`Project Name / (Agency) / (Project Code) (Legacy OCMS Code) (PMGID)` *(Apr, Jun, Jul 26)* | Header expanded over time to reflect integration of Legacy OCMS and PMG portal IDs | Multiline string: Project Name, Implementing Agency, PAIMANA Project ID, Legacy OCMS Code, PMG ID |
| **Col 3** | `State` | Unchanged (Dec 2025 – Jul 2026) | Geographic State, UT, or `Multi-States` |
| **Col 4** | `Date of Approval`<br>`(Start Date)`<br>`MM/YYYY` | Unchanged (Dec 2025 – Jul 2026) | Upper line: Date of Government Sanction (`MM/YYYY`). Lower line: Actual/Targeted Start Date (`(MM/YYYY)`) |
| **Col 5** | `Orignal/Target DoC`<br>`(Revised DoC)`<br>`MM/YYYY` | Unchanged (Dec 2025 – Jul 2026) | Upper line: Original Target Date of Completion (`MM/YYYY`). Lower line: Currently anticipated Revised Date of Completion (`(MM/YYYY)`) |
| **Col 6** | `Orignal Cost`<br>`Revised Cost`<br>`in Rs. Crore` | Unchanged (Dec 2025 – Jul 2026) | Upper line: Originally Sanctioned Budget (`₹ Crore`). Lower line: Latest Approved Sanctioned Cost (`₹ Crore`) |
| **Col 7** | `Cumulative Expenditure`<br>`in Rs. Crore` | Unchanged (Dec 2025 – Jul 2026) | Actual cumulative capital spent to date (`₹ Crore`) |
| **Col 8** | `Physical Progress (%)` *(Dec 25 - Jan 26)*<br>`Physical Progress` *(Feb 26 - Jul 26)* | Header dropped `(%)` from Feb 2026 onwards | Progress percentage reported by nodal line agency (`0` to `100`) |

---

## 5. Decomposed Field Dictionary (Extracted Data Schema)

When each project row is parsed without transformation, 16 distinct data fields are present:

| Field Key | Source Location | Data Type | Missing Count Across All 14,573 Rows | Range / Domain Values | Description |
|---|---|---|---|---|---|
| `sl_no` | Column 1 | Integer (`int64`) | 0 | 1 to 1,987 | Sequential counter within that month's report |
| `ministry` | Section Header | String (`object`) | 0 | 17 Central Line Ministries | Administrative Ministry in charge of project |
| `sector` | Subsection Header | String (`object`) | 0 | Infrastructure sectors (Civil Aviation, Railways, Road Transport, Power, Petroleum, etc.) | Sector classification |
| `project_name` | Column 2 (Top lines) | String (`object`) | 0 | Min 5 chars, Max 450 chars | Official name and scope description of project |
| `implementing_agency`| Column 2 (Middle line) | String (`object`) | 0 | NHAI, RVNL, AAI, NTPC, MoRTH, etc. | Implementing PSU / Directorate / Agency |
| `project_id` | Column 2 (Parentheses) | String (`object`) | **0** | 5 to 7 digits (e.g., `612786`, `701107`) | **Unique PAIMANA Project Identification Code** |
| `legacy_ocms_code` | Column 2 (Trailing line) | String (`object`) | Present in Feb–Jul | Alphanumeric (e.g., `N04000106`) or `(-)` | Legacy Online Computerized Monitoring System Code |
| `pmgid` | Column 2 (Trailing line) | String (`object`) | Present in Apr, Jun, Jul | Integer (e.g., `4353`) or `(-)` | Project Monitoring Group Identifier |
| `state` | Column 3 | String (`object`) | 2 (Across all months) | Indian States, UTs, `Multi-States` | State or UT where project execution occurs |
| `date_of_approval` | Column 4 (Top) | Date String (`MM/YYYY`) | 0 | `04/1990` to `07/2026` | Formal Cabinet/Ministry sanction date |
| `start_date` | Column 4 (Bottom) | Date String (`MM/YYYY`) | 11 (May 2026) | `01/1995` to `07/2026` | Physical commencement / award date |
| `original_doc` | Column 5 (Top) | Date String (`MM/YYYY`) | 11 (May 2026) | `01/2000` to `12/2035` | Originally targeted Date of Completion (DoC) |
| `revised_doc` | Column 5 (Bottom) | Date String (`MM/YYYY`) | 3,965 (Reported as `(-)`) | `01/2020` to `03/2036` | Anticipated revised completion deadline |
| `original_cost` | Column 6 (Top) | Float (`float64`) | 0 | ₹100.00 Cr to ₹108,000.00 Cr | Original sanctioned project budget in ₹ Crore |
| `revised_cost` | Column 6 (Bottom) | Float (`float64`) | 0 | ₹0.10 Cr to ₹188,000.00 Cr | Current sanctioned/revised budget in ₹ Crore |
| `cumulative_expenditure` | Column 7 | Float (`float64`) | 0 | ₹-54.57 Cr to ₹124,623.00 Cr | Capital disbursed/spent to date in ₹ Crore |
| `physical_progress_pct` | Column 8 | Float (`float64`) | 0 | 0.0% to 100.0% | Certified physical execution progress |

---

## 6. Verification of Data Immutability
All 8 original PDF files located in `d:\reports\` have been preserved in their original, untouched state:
- No file was renamed, relocated, deleted, or overwritten.
- No values were trimmed, imputed, or altered in the source files.
- All inspection operations were performed via read-only file streams.
