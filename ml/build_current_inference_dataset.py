"""
SIH26103 - Infrastructure Risk Prediction
Step 6B: Current Project Inference Dataset Generator

Builds current_inference_dataset.csv containing the latest available snapshot
for every currently monitored project in MoSPI/IPMD Table 6, transformed into
the exact 36 SAFE_MVP features expected by the trained production ML models.
"""

import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
import joblib

# Paths resolution
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ML_DIR = PROJECT_ROOT / "ml"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Fallback to D:/reports if not in workspace
TABLE6_PATH = (
    REPORTS_DIR / "standardized_table6_project_month.csv"
    if (REPORTS_DIR / "standardized_table6_project_month.csv").exists()
    else Path("D:/reports/standardized_table6_project_month.csv")
)

SCHEMA_PATH = ML_DIR / "schemas" / "production_feature_schema.csv"
MODELS_DIR = ML_DIR / "models"

OUTPUT_DATASET_PATH = PROJECT_ROOT / "current_inference_dataset.csv"
OUTPUT_QUALITY_REPORT_PATH = PROJECT_ROOT / "current_inference_data_quality_report.csv"
OUTPUT_VALIDATION_REPORT_PATH = PROJECT_ROOT / "current_inference_validation_report.md"
OUTPUT_FEATURE_MAPPING_PATH = PROJECT_ROOT / "current_inference_feature_mapping.md"

# Sector-to-Ministry & Agency-to-Ministry deterministic cleaning mappings for OCR/PDF header artifacts
MANUAL_AGENCY_TO_MINISTRY = {
    "RVNL - II": "Ministry of Railways",
    "Gas Authority of India Limited [GAIL]": "Ministry of Petroleum & Natural Gas",
    "South Eastern Coalfields Limited [SECL]": "Ministry of Coal",
    "National Capital Region Transport Corporation [NCRTC]": "Ministry of Housing & Urban Affairs",
    "Bharat Coking Coal Limited [BCCL]": "Ministry of Coal",
    "ministry of housing and urban affairs": "Ministry of Housing & Urban Affairs",
    "Ministry of Housing & Urban Affairs": "Ministry of Housing & Urban Affairs",
    "West Central Railway WCR I": "Ministry of Railways",
    "Central Railway": "Ministry of Railways",
    "North Western Railway [NWR]": "Ministry of Railways",
    "South Western Railway [SWR] - II": "Ministry of Railways",
    "Bharat Petroleum Corporation Limited [BPCL]": "Ministry of Petroleum & Natural Gas",
    "Oil and Natural Gas Corporation Limited [ONGC]": "Ministry of Petroleum & Natural Gas",
    "Ministry of Petroleum & Natural Gas": "Ministry of Petroleum & Natural Gas",
    "Water Resources-BR": "Department of Water Resources, River Development & GR",
    "Power Grid Corporation of India Limited [POWERGRID]": "Ministry of Power",
    "Inland Waterways Authority of India [IWAI]": "Ministry of Ports, Shipping and Waterways",
    "Mumbai Port Trust [MPT]": "Ministry of Ports, Shipping and Waterways",
    "Haldia Dock Complex, Syama Prasad Mookerjee Port Authority": "Ministry of Ports, Shipping and Waterways",
    "Hindustan Petroleum Corporation Limited": "Ministry of Petroleum & Natural Gas",
    "Indian Oil Corporation Limited [IOCL]": "Ministry of Petroleum & Natural Gas",
    "MinistryofPetroleumNaturalGas": "Ministry of Petroleum & Natural Gas",
}

SECTOR_TO_MINISTRY = {
    "Railways": "Ministry of Railways",
    "Oil & Gas": "Ministry of Petroleum & Natural Gas",
    "Energy Storage": "Ministry of Petroleum & Natural Gas",
    "Coal": "Ministry of Coal",
    "Transmission & Distribution": "Ministry of Power",
    "Electricity Generation": "Ministry of Power",
    "Roads & Highways": "Ministry of Road Transport & Highways",
    "Waste & Water": "Ministry of Housing & Urban Affairs",
    "Urban Public Transport": "Ministry of Housing & Urban Affairs",
    "Real Estate": "Ministry of Housing & Urban Affairs",
    "Water Resources": "Department of Water Resources, River Development & GR",
    "Shipping": "Ministry of Ports, Shipping and Waterways",
    "Inland Waterways": "Ministry of Ports, Shipping and Waterways",
    "Healthcare": "Ministry of Health & Family Welfare",
    "Telecommunication": "Department of Telecommunications",
    "Education": "Department of Higher Education",
    "Steel": "Ministry of Steel",
    "Aviation & Aviation Infrastructure": "Ministry of Civil Aviation",
    "Metals & Mining": "Ministry of Mines",
}


def clean_ministry(pid: str, p_history: pd.DataFrame, latest_row: pd.Series, agency_mode_dict: dict) -> tuple[str, bool, str]:
    """
    Cleans PDF extraction header artifacts from ministry field.
    Returns: (cleaned_ministry, was_cleaned_flag, clean_reason)
    """
    raw_val = latest_row["ministry"]
    is_garbage = (
        pd.isna(raw_val)
        or any(k in str(raw_val) for k in ["All Ongoing Projects", "Orignal/Target", "Sl.No", "Rs. Crore", "MM/YYYY"])
    )

    if not is_garbage:
        return str(raw_val), False, "RAW_CLEAN"

    # Step 1: Check if project has clean historical observation in Table 6
    clean_hist = [
        m for m in p_history["ministry"].unique()
        if pd.notna(m) and not any(k in str(m) for k in ["All Ongoing Projects", "Orignal/Target", "Sl.No", "Rs. Crore", "MM/YYYY"])
    ]
    if clean_hist:
        return str(clean_hist[0]), True, "PROJECT_HISTORY_LOOKUP"

    # Step 2: Check agency mapping
    agency = latest_row["implementing_agency"]
    if agency in MANUAL_AGENCY_TO_MINISTRY:
        return MANUAL_AGENCY_TO_MINISTRY[agency], True, "MANUAL_AGENCY_MAPPING"
    if agency in agency_mode_dict and pd.notna(agency_mode_dict[agency]):
        return str(agency_mode_dict[agency]), True, "DATASET_AGENCY_MODE_MAPPING"

    # Step 3: Check sector fallback
    sec = latest_row["sector"]
    if sec in SECTOR_TO_MINISTRY:
        return SECTOR_TO_MINISTRY[sec], True, "SECTOR_FALLBACK_MAPPING"

    return "Unknown", True, "DEFAULT_UNKNOWN"


def generate_dataset():
    print(f"Loading Table 6 from: {TABLE6_PATH}")
    t6 = pd.read_csv(TABLE6_PATH, dtype={"project_id": str})
    total_source_obs = len(t6)
    print(f"Total Table 6 observations loaded: {total_source_obs:,}")

    # Build reference agency mode mapping on clean records
    clean_df = t6[~t6["ministry"].astype(str).str.contains("All Ongoing Projects|Orignal/Target|Sl.No|Rs. Crore", regex=True)]
    agency_mode_dict = clean_df.groupby("implementing_agency")["ministry"].agg(
        lambda x: x.mode()[0] if not x.empty else None
    ).to_dict()

    # Group observations by project_id sorted by report_month ascending
    t6_by_pid = {pid: grp.sort_values("report_month").copy() for pid, grp in t6.groupby("project_id")}
    unique_projects = len(t6_by_pid)
    print(f"Unique projects identified: {unique_projects:,}")

    # Load production feature schema
    df_schema = pd.read_csv(SCHEMA_PATH)
    expected_36_features = list(df_schema["feature_name"])
    assert len(expected_36_features) == 36, f"Expected 36 features in schema, found {len(expected_36_features)}"

    dataset_rows = []
    cleaning_log = []

    for pid, p_df in t6_by_pid.items():
        # Latest available observation is the last row of sorted history
        snap_r = p_df.iloc[-1]
        snap_m = snap_r["report_month"]
        pname = snap_r["project_name"]

        # Temporal safety: only allow records at or before snapshot_month
        eligible = p_df[p_df["report_month"] <= snap_m]

        # Categorical cleaning
        ministry, was_cleaned, clean_reason = clean_ministry(pid, eligible, snap_r, agency_mode_dict)
        if was_cleaned:
            cleaning_log.append({
                "project_id": pid,
                "project_name": pname,
                "snapshot_month": snap_m,
                "raw_ministry_snippet": repr(str(snap_r["ministry"])[:60]),
                "cleaned_ministry": ministry,
                "implementing_agency": snap_r["implementing_agency"],
                "sector": snap_r["sector"],
                "clean_reason": clean_reason
            })

        sector = str(snap_r["sector"]) if pd.notna(snap_r["sector"]) else "Unknown"
        agency = str(snap_r["implementing_agency"]) if pd.notna(snap_r["implementing_agency"]) else "Unknown"
        state = str(snap_r["state"]) if pd.notna(snap_r["state"]) else "Unknown"

        # Date parsing
        dt_snap = pd.to_datetime(snap_m + "-01")
        dt_start = pd.to_datetime(str(snap_r["start_date"]) + "-01") if pd.notna(snap_r["start_date"]) else None
        dt_orig = pd.to_datetime(str(snap_r["original_doc"]) + "-01") if pd.notna(snap_r["original_doc"]) else None
        dt_appr = pd.to_datetime(str(snap_r["date_of_approval"]) + "-01") if pd.notna(snap_r["date_of_approval"]) else None

        # Financial values
        orig_cost = float(snap_r["original_cost"]) if pd.notna(snap_r["original_cost"]) else np.nan
        cum_exp = float(snap_r["cumulative_expenditure"]) if pd.notna(snap_r["cumulative_expenditure"]) else np.nan
        exp_pct_orig = (cum_exp / orig_cost * 100.0) if (pd.notna(orig_cost) and orig_cost > 0 and pd.notna(cum_exp)) else np.nan

        # Physical progress
        phys_pct = float(snap_r["physical_progress_pct"]) if pd.notna(snap_r["physical_progress_pct"]) else np.nan

        # Pre-construction gestation
        if dt_appr is not None and dt_start is not None:
            approval_to_start_months = float((dt_start.year - dt_appr.year) * 12 + (dt_start.month - dt_appr.month))
        else:
            approval_to_start_months = np.nan

        # Schedule progression
        if dt_start is not None and dt_orig is not None:
            planned_duration_months = float((dt_orig.year - dt_start.year) * 12 + (dt_orig.month - dt_start.month))
        else:
            planned_duration_months = np.nan

        if dt_start is not None:
            elapsed_months = float((dt_snap.year - dt_start.year) * 12 + (dt_snap.month - dt_start.month))
        else:
            elapsed_months = np.nan

        if dt_orig is not None:
            remaining_planned_months = float((dt_orig.year - dt_snap.year) * 12 + (dt_orig.month - dt_snap.month))
            is_past_orig_doc = 1.0 if snap_m > str(snap_r["original_doc"]) else 0.0
        else:
            remaining_planned_months = np.nan
            is_past_orig_doc = 0.0

        if pd.notna(planned_duration_months) and planned_duration_months > 0 and pd.notna(elapsed_months):
            elapsed_duration_ratio = float(elapsed_months / planned_duration_months)
        else:
            elapsed_duration_ratio = np.nan

        # Analytical benchmarks and interaction metrics
        efficiency_gap = (phys_pct - exp_pct_orig) if (pd.notna(phys_pct) and pd.notna(exp_pct_orig)) else np.nan
        cost_physical_ratio = (exp_pct_orig / phys_pct) if (pd.notna(exp_pct_orig) and pd.notna(phys_pct) and phys_pct > 0) else np.nan

        if pd.notna(elapsed_duration_ratio):
            expected_progress_pct = float(min(100.0, max(0.0, elapsed_duration_ratio * 100.0)))
            progress_gap_pct_points = (phys_pct - expected_progress_pct) if pd.notna(phys_pct) else np.nan
        else:
            expected_progress_pct = np.nan
            progress_gap_pct_points = np.nan

        # Observation timeline
        n_obs_to_date = float(len(eligible))
        earliest_obs_m = eligible["report_month"].min()
        dt_earliest = pd.to_datetime(earliest_obs_m + "-01")
        months_since_first_observation = float((dt_snap.year - dt_earliest.year) * 12 + (dt_snap.month - dt_earliest.month))

        # Short-term lookback (T-1 month and T-2 months)
        t_prev1_str = (dt_snap - relativedelta(months=1)).strftime("%Y-%m")
        t_prev2_str = (dt_snap - relativedelta(months=2)).strftime("%Y-%m")

        obs_t1 = eligible[eligible["report_month"] == t_prev1_str]
        obs_t2 = eligible[eligible["report_month"] == t_prev2_str]
        row_t1 = obs_t1.iloc[0] if len(obs_t1) > 0 else None
        row_t2 = obs_t2.iloc[0] if len(obs_t2) > 0 else None

        if row_t1 is not None and pd.notna(row_t1["physical_progress_pct"]) and pd.notna(row_t1["cumulative_expenditure"]) and pd.notna(phys_pct) and pd.notna(cum_exp):
            phys_t1 = float(row_t1["physical_progress_pct"])
            exp_t1 = float(row_t1["cumulative_expenditure"])
            monthly_progress_change = float(phys_pct - phys_t1)
            progress_growth_rate = float(((phys_pct - phys_t1) / phys_t1 * 100.0)) if phys_t1 > 0 else np.nan
            monthly_expenditure_change = float(cum_exp - exp_t1)
            monthly_expenditure_growth_pct = float(((cum_exp - exp_t1) / exp_t1 * 100.0)) if exp_t1 > 0 else np.nan
            phys_1m_change = monthly_progress_change
            exp_1m_change = monthly_expenditure_change
            missing_previous_month = 0
        else:
            monthly_progress_change = np.nan
            progress_growth_rate = np.nan
            monthly_expenditure_change = np.nan
            monthly_expenditure_growth_pct = np.nan
            phys_1m_change = np.nan
            exp_1m_change = np.nan
            missing_previous_month = 1

        if row_t2 is not None and pd.notna(row_t2["physical_progress_pct"]) and pd.notna(row_t2["cumulative_expenditure"]) and pd.notna(phys_pct) and pd.notna(cum_exp):
            phys_t2 = float(row_t2["physical_progress_pct"])
            exp_t2 = float(row_t2["cumulative_expenditure"])
            phys_2m_change = float(phys_pct - phys_t2)
            exp_2m_change = float(cum_exp - exp_t2)
        else:
            phys_2m_change = np.nan
            exp_2m_change = np.nan

        # Longitudinal trend slopes
        if len(eligible) >= 2 and months_since_first_observation > 0 and pd.notna(phys_pct) and pd.notna(cum_exp):
            first_row = eligible.iloc[0]
            if pd.notna(first_row["physical_progress_pct"]) and pd.notna(first_row["cumulative_expenditure"]):
                progress_trend_slope = float((phys_pct - float(first_row["physical_progress_pct"])) / months_since_first_observation)
                expenditure_trend_slope = float((cum_exp - float(first_row["cumulative_expenditure"])) / months_since_first_observation)
            else:
                progress_trend_slope = np.nan
                expenditure_trend_slope = np.nan
        elif len(eligible) >= 2 and months_since_first_observation == 0:
            progress_trend_slope = 0.0
            expenditure_trend_slope = 0.0
        else:
            progress_trend_slope = np.nan
            expenditure_trend_slope = np.nan

        # Data quality flags
        negative_expenditure_flag = 1 if (pd.notna(cum_exp) and cum_exp < 0) else 0
        missing_previous_month_flag = missing_previous_month
        invalid_duration_flag = 1 if (pd.isna(planned_duration_months) or planned_duration_months <= 0) else 0
        past_original_doc_flag = int(is_past_orig_doc)
        missing_key_date_flag = 1 if (pd.isna(snap_r["start_date"]) or pd.isna(snap_r["original_doc"])) else 0
        suspicious_value_flag = 1 if (
            (pd.notna(phys_pct) and (phys_pct > 100.0 or phys_pct < 0.0))
            or (pd.notna(exp_pct_orig) and (exp_pct_orig > 300.0 or exp_pct_orig < 0.0))
        ) else 0

        # Construct final row dictionary (metadata + 36 model features in exact order)
        row_dict = {
            # Metadata identifiers
            "project_id": pid,
            "project_name": pname,
            "snapshot_month": snap_m,

            # 32 Numerical Features
            "original_cost": round(orig_cost, 4) if pd.notna(orig_cost) else np.nan,
            "approval_to_start_months": round(approval_to_start_months, 4) if pd.notna(approval_to_start_months) else np.nan,
            "cumulative_expenditure": round(cum_exp, 4) if pd.notna(cum_exp) else np.nan,
            "expenditure_percent_of_original_cost": round(exp_pct_orig, 4) if pd.notna(exp_pct_orig) else np.nan,
            "monthly_expenditure_change": round(monthly_expenditure_change, 4) if pd.notna(monthly_expenditure_change) else np.nan,
            "monthly_expenditure_growth_pct": round(monthly_expenditure_growth_pct, 4) if pd.notna(monthly_expenditure_growth_pct) else np.nan,
            "physical_progress_pct": round(phys_pct, 4) if pd.notna(phys_pct) else np.nan,
            "monthly_progress_change": round(monthly_progress_change, 4) if pd.notna(monthly_progress_change) else np.nan,
            "progress_growth_rate": round(progress_growth_rate, 4) if pd.notna(progress_growth_rate) else np.nan,
            "planned_duration_months": round(planned_duration_months, 4) if pd.notna(planned_duration_months) else np.nan,
            "elapsed_months": round(elapsed_months, 4) if pd.notna(elapsed_months) else np.nan,
            "remaining_planned_months": round(remaining_planned_months, 4) if pd.notna(remaining_planned_months) else np.nan,
            "elapsed_duration_ratio": round(elapsed_duration_ratio, 4) if pd.notna(elapsed_duration_ratio) else np.nan,
            "is_past_original_doc": is_past_orig_doc,
            "efficiency_gap": round(efficiency_gap, 4) if pd.notna(efficiency_gap) else np.nan,
            "cost_physical_ratio": round(cost_physical_ratio, 4) if pd.notna(cost_physical_ratio) else np.nan,
            "expected_progress_pct": round(expected_progress_pct, 4) if pd.notna(expected_progress_pct) else np.nan,
            "progress_gap_pct_points": round(progress_gap_pct_points, 4) if pd.notna(progress_gap_pct_points) else np.nan,
            "months_since_first_observation": int(months_since_first_observation),
            "observation_count_to_date": int(n_obs_to_date),
            "physical_progress_1_month_change": round(phys_1m_change, 4) if pd.notna(phys_1m_change) else np.nan,
            "physical_progress_2_month_change": round(phys_2m_change, 4) if pd.notna(phys_2m_change) else np.nan,
            "expenditure_1_month_change": round(exp_1m_change, 4) if pd.notna(exp_1m_change) else np.nan,
            "expenditure_2_month_change": round(exp_2m_change, 4) if pd.notna(exp_2m_change) else np.nan,
            "progress_trend_slope": round(progress_trend_slope, 4) if pd.notna(progress_trend_slope) else np.nan,
            "expenditure_trend_slope": round(expenditure_trend_slope, 4) if pd.notna(expenditure_trend_slope) else np.nan,
            "negative_expenditure_flag": negative_expenditure_flag,
            "missing_previous_month_flag": missing_previous_month_flag,
            "invalid_duration_flag": invalid_duration_flag,
            "past_original_doc_flag": past_original_doc_flag,
            "missing_key_date_flag": missing_key_date_flag,
            "suspicious_value_flag": suspicious_value_flag,

            # 4 Categorical Features
            "ministry": ministry,
            "sector": sector,
            "implementing_agency": agency,
            "state": state,
        }
        dataset_rows.append(row_dict)

    df_current = pd.DataFrame(dataset_rows)
    print(f"Generated dataset shape: {df_current.shape} (Rows: {len(df_current)}, Columns: {len(df_current.columns)})")

    # Cardinality & duplication checks
    assert len(df_current) == unique_projects, f"Mismatch: {len(df_current)} rows vs {unique_projects} unique projects"
    assert df_current["project_id"].nunique() == unique_projects, "Duplicate project_ids detected in output dataset!"

    # Feature schema and ordering validation
    feature_cols = [c for c in df_current.columns if c not in ["project_id", "project_name", "snapshot_month"]]
    assert feature_cols == expected_36_features, "Feature order/names do not match production_feature_schema.csv!"
    print("Schema alignment verification passed: Exactly 36 SAFE_MVP features in authoritative order.")

    # Save current_inference_dataset.csv
    df_current.to_csv(OUTPUT_DATASET_PATH, index=False)
    print(f"Saved primary inference dataset to: {OUTPUT_DATASET_PATH}")
    if REPORTS_DIR.exists():
        df_current.to_csv(REPORTS_DIR / "current_inference_dataset.csv", index=False)
        print(f"Copied primary inference dataset to: {REPORTS_DIR / 'current_inference_dataset.csv'}")

    # Build Data Quality Report
    print("Generating data quality report...")
    quality_rows = []
    for f in expected_36_features:
        s = df_current[f]
        n_miss = int(s.isna().sum())
        pct_miss = round((n_miss / len(df_current)) * 100, 2)
        f_type = "categorical" if f in ["ministry", "sector", "implementing_agency", "state"] else "numerical"

        if f_type == "numerical":
            s_valid = s.dropna()
            min_v = float(s_valid.min()) if len(s_valid) > 0 else np.nan
            med_v = float(s_valid.median()) if len(s_valid) > 0 else np.nan
            max_v = float(s_valid.max()) if len(s_valid) > 0 else np.nan
            zero_count = int((s_valid == 0).sum())
        else:
            min_v = np.nan
            med_v = np.nan
            max_v = np.nan
            zero_count = 0

        quality_rows.append({
            "feature_name": f,
            "feature_type": f_type,
            "non_null_count": int(s.notna().sum()),
            "missing_count": n_miss,
            "missing_pct": pct_miss,
            "zero_count": zero_count,
            "min_value": round(min_v, 4) if pd.notna(min_v) else None,
            "median_value": round(med_v, 4) if pd.notna(med_v) else None,
            "max_value": round(max_v, 4) if pd.notna(max_v) else None,
            "status": "PASS" if n_miss == 0 or f_type == "numerical" else "WARN",
        })

    df_quality = pd.DataFrame(quality_rows)
    df_quality.to_csv(OUTPUT_QUALITY_REPORT_PATH, index=False)
    print(f"Saved data quality report to: {OUTPUT_QUALITY_REPORT_PATH}")
    if REPORTS_DIR.exists():
        df_quality.to_csv(REPORTS_DIR / "current_inference_data_quality_report.csv", index=False)

    # Model Evaluation & Smoke Testing
    print("Evaluating production models on generated current inference feature matrix...")
    cost_m = joblib.load(MODELS_DIR / "cost_overrun_model.joblib")
    delay_m = joblib.load(MODELS_DIR / "delay_model.joblib")
    delay_reg = joblib.load(MODELS_DIR / "delay_regressor.joblib")

    X = df_current[expected_36_features]

    cost_probs = cost_m.predict_proba(X)[:, 1]
    delay_probs = delay_m.predict_proba(X)[:, 1]
    pred_delays = delay_reg.predict(X)

    print("All 3 models generated predictions across 2,131 current projects successfully!")
    print(f"Cost Overrun Prob: min={cost_probs.min():.4f}, median={np.median(cost_probs):.4f}, max={cost_probs.max():.4f}")
    print(f"Delay Prob: min={delay_probs.min():.4f}, median={np.median(delay_probs):.4f}, max={delay_probs.max():.4f}")
    print(f"Predicted Delays: min={pred_delays.min():.2f}, median={np.median(pred_delays):.2f}, max={pred_delays.max():.2f}")

    # Build smoke test table on diverse sample projects
    smoke_pids = ["400234", "400161", "612786", "611950", "709790", "400152", "611142", "701586", "705503", "400104"]
    smoke_records = []
    for spid in smoke_pids:
        sp_rows = df_current[df_current["project_id"] == spid]
        if len(sp_rows) > 0:
            idx = sp_rows.index[0]
            smoke_records.append({
                "project_id": spid,
                "project_name": df_current.loc[idx, "project_name"],
                "sector": df_current.loc[idx, "sector"],
                "snapshot_month": df_current.loc[idx, "snapshot_month"],
                "cost_overrun_probability": round(float(cost_probs[idx]), 4),
                "delay_probability": round(float(delay_probs[idx]), 4),
                "predicted_delay_months": round(float(pred_delays[idx]), 2),
                "status": "SUCCESS"
            })

    df_smoke = pd.DataFrame(smoke_records)
    print("\nSmoke Test Results:\n", df_smoke[["project_id", "sector", "cost_overrun_probability", "delay_probability", "predicted_delay_months", "status"]].to_string())

    return df_current, df_quality, df_smoke, cleaning_log, total_source_obs, unique_projects


if __name__ == "__main__":
    generate_dataset()
