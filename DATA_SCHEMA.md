# Data Schema & Feature Engineering Specification

## 1. Overview & Data Philosophy
This document formalizes the input, internal feature engineering, and output prediction data contracts for **SIH26103**.

> [!IMPORTANT]
> **Data Grounding & Integrity Rule:**
> - Official MoSPI (Ministry of Statistics and Programme Implementation) Flash Reports publish monthly aggregated tables and PDF/HTML lists of Central Sector Projects costing ₹150 Crore and above.
> - **We do not assume that a pre-packaged, ML-ready historical tabular dataset is directly downloadable from MoSPI.**
> - Tabular data for training must either be parsed from publicly published report tables or generated via a statistically calibrated benchmark generator that mirrors real-world infrastructure parameters (cost ranges, schedule timelines, sector characteristics, and common delay factors).
> - No fabricated datasets or fictitious ministry statistics will be claimed as official ground truth.

---

## 2. Ingestion / Input Schema (`ProjectInput`)
The raw data fields accepted by the system per project record:

### 2.1 Project Metadata
| Field Name | Type | Constraints | Description |
|---|---|---|---|
| `project_id` | `string` | Unique identifier (e.g., `PRJ-INFRA-1021`) | Primary reference ID |
| `project_name` | `string` | Min 3 chars, Max 150 chars | Name of the infrastructure project |
| `sector` | `string` | Enum: `Roads & Highways`, `Railways`, `Power`, `Petroleum`, `Urban Development`, `Water Resources`, `Other` | Infrastructure sector category |
| `state_ut` | `string` | Valid Indian State/UT name | Geographic location |
| `implementing_agency`| `string` | Optional (e.g., `NHAI`, `RVNL`, `NTPC`, `State PWD`) | Nodal execution body |

### 2.2 Financial Parameters
| Field Name | Type | Constraints | Description | Unit |
|---|---|---|---|---|
| `original_cost` | `float` | $> 0$ | Original approved project budget | ₹ in Crores |
| `revised_cost` | `float` | $\ge \text{original\_cost}$ | Latest approved sanctioned cost | ₹ in Crores |
| `cumulative_expenditure`| `float` | $\ge 0$ | Actual capital spent to date | ₹ in Crores |

### 2.3 Schedule & Timeline Parameters
| Field Name | Type | Constraints | Description |
|---|---|---|---|
| `commencement_date` | `date` | ISO 8601 (`YYYY-MM-DD`) | Date project work officially commenced |
| `original_completion_date` | `date` | Strictly $> \text{commencement\_date}$ | Originally targeted completion date |
| `revised_completion_date` | `date` | $\ge \text{original\_completion\_date}$ | Current anticipated completion date |
| `snapshot_date` | `date` | $\ge \text{commencement\_date}$ | Date this monitoring record was recorded |

### 2.4 Physical & Operational Progress Parameters
| Field Name | Type | Constraints | Description | Unit |
|---|---|---|---|---|
| `physical_progress_pct` | `float` | $0.0 \le x \le 100.0$ | Cumulative physical work completed | Percentage (%) |
| `financial_progress_pct`| `float` | $0.0 \le x \le 100.0$ | Expenditure as % of revised cost | Percentage (%) |
| `milestones_total` | `integer`| $\ge 1$ | Total defined project milestones | Count |
| `milestones_achieved` | `integer`| $0 \le x \le \text{milestones\_total}$ | Milestones successfully completed | Count |

### 2.5 Risk Drivers & Clearance Indicators (Domain Context)
| Field Name | Type | Constraints | Description |
|---|---|---|---|
| `land_acquisition_pct` | `float` | $0.0 \le x \le 100.0$ | Proportion of required land acquired |
| `forest_clearance_status` | `string` | Enum: `Approved`, `In-Process`, `Pending`, `Not-Applicable` | Forest & environmental clearance status |
| `contractor_count` | `integer` | $\ge 1$ | Number of active primary EPC contractors |
| `revised_dates_count` | `integer` | $\ge 0$ | Number of times completion deadline was revised |

---

## 3. Preprocessed & Engineered Feature Schema (`ProjectFeatures`)
Features generated programmatically prior to feeding the machine learning inference models:

| Feature Name | Derived From | Formula / Logic | Business / Analytical Meaning |
|---|---|---|---|
| `planned_duration_months` | Dates | $(\text{orig\_completion} - \text{commencement}) / 30.44$ | Total scheduled timeline |
| `elapsed_duration_months` | Dates | $(\text{snapshot\_date} - \text{commencement}) / 30.44$ | Operational timeline used up so far |
| `time_elapsed_ratio` | Durations | $\text{elapsed\_duration} / \max(\text{planned\_duration}, 1.0)$ | Fraction of planned time consumed |
| `schedule_slippage_index`| Progress vs Time | $\text{time\_elapsed\_ratio} - (\text{physical\_progress\_pct} / 100.0)$ | Positive value indicates progress is lagging behind time spent |
| `cost_burn_ratio` | Spend vs Budget | $\text{cumulative\_expenditure} / \text{original\_cost}$ | Capital burn relative to original budget |
| `cost_physical_divergence`| Spend vs Progress | $(\text{financial\_progress\_pct} - \text{physical\_progress\_pct}) / 100.0$ | Divergence when funds are spent faster than physical structures are built |
| `milestone_completion_rate`| Milestones | $\text{milestones\_achieved} / \text{milestones\_total}$ | Formal milestone achievement velocity |
| `land_risk_factor` | Land % | $(100.0 - \text{land\_acquisition\_pct}) / 100.0$ | Unacquired land vulnerability |
| `regulatory_delay_flag` | Clearances | $1$ if `Pending` or `In-Process` and `time_elapsed_ratio` $> 0.4$, else $0$ | Regulatory hold-up in mature project phase |
| `sanction_escalation_ratio`| Costs | $(\text{revised\_cost} - \text{original\_cost}) / \text{original\_cost}$ | Administrative cost revision approved to date |

---

## 4. Prediction & Output Schema (`ProjectRiskAssessment`)
The payload returned by the prediction engine:

### 4.1 Risk Scores & Classifications
| Field Name | Type | Range / Format | Description |
|---|---|---|---|
| `delay_risk_score` | `float` | $0.0 - 100.0$ | Probability-weighted delay likelihood |
| `delay_risk_tier` | `string` | Enum: `Low`, `Medium`, `High`, `Critical` | Categorical schedule risk classification |
| `cost_overrun_risk_score`| `float` | $0.0 - 100.0$ | Probability-weighted cost overrun likelihood |
| `cost_overrun_risk_tier` | `string` | Enum: `Low`, `Medium`, `High`, `Critical` | Categorical financial overrun classification |
| `composite_risk_index` | `float` | $0.0 - 100.0$ | Synthesized overall project risk index |
| `early_warning_status` | `string` | Enum: `Normal`, `Watchlist`, `High Alert`, `Critical Red Flag` | Portfolio-level early warning banner |

### 4.2 Explainability & Risk Drivers (`RiskFactorExplanation`)
```json
{
  "top_risk_drivers": [
    {
      "driver_name": "Schedule-Time Slippage",
      "impact_direction": "INCREASING_RISK",
      "contribution_weight": 0.38,
      "human_readable_detail": "Project has consumed 72% of planned time but only achieved 39% physical progress."
    },
    {
      "driver_name": "Cost-Physical Divergence",
      "impact_direction": "INCREASING_RISK",
      "contribution_weight": 0.29,
      "human_readable_detail": "Financial disbursement (68%) severely outpaces physical progress (39%), signaling high cost overrun vulnerability."
    },
    {
      "driver_name": "Pending Environmental Clearance",
      "impact_direction": "INCREASING_RISK",
      "contribution_weight": 0.18,
      "human_readable_detail": "Forest/environmental clearance remains pending despite entering mid-lifecycle."
    }
  ]
}
```

### 4.3 Actionable Recommendations (`AlertAction`)
- List of system-generated guidance suggestions (e.g., *"Initiate joint tripartite review with state land revenue authority"*, *"Freeze non-essential contract scope amendments"*).

---

## 5. Sourcing & Benchmark Strategy [PENDING DATA RESEARCH]

| Strategy | Description | Advantages | Limitations / Risks | Status |
|---|---|---|---|---|
| **Option A: Public MoSPI Flash Report Extraction** | Scrape or parse tables from published monthly flash reports on `cspm.gov.in` / MoSPI portal. | Direct government grounding. | Reports often lack temporal milestone progressions; time-consuming manual cleaning required. | **PENDING EVALUATION** |
| **Option B: Calibrated Synthetic Benchmark Generator** | Statistically calibrated simulation generating 1,000–5,000 realistic project life-cycles conforming to published MoSPI statistical spreads (average delay lengths, cost revision distributions). | Complete control over edge cases, reproducible, guarantees clean balanced training splits. | Must be transparently labeled as a calibrated domain benchmark, not unverified raw data. | **PENDING EVALUATION** |
| **Option C: Hybrid Approach** | Seed benchmark with actual published macro parameters from recent MoSPI reports, then simulate plausible project trajectories. | Balances real macro statistics with rich ML feature granularity. | Requires careful calibration logic. | **RECOMMENDED DIRECTION** |
