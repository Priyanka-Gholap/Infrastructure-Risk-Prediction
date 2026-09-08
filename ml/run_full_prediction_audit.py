"""
STEP 6C.1: Full Current-Project Prediction Audit Script.

Executes production inference across all 2,131 projects in current_inference_dataset.csv,
validates every prediction, analyzes extreme delay predictions, compares reference projects,
and generates the full audit artifacts.
"""

import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import joblib

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from backend.app.risk_policy import compute_overall_risk

MODELS_DIR = REPO_ROOT / "ml" / "models"
SCHEMAS_DIR = REPO_ROOT / "ml" / "schemas"
DATASET_PATH = REPO_ROOT / "current_inference_dataset.csv"
AUDIT_DIR = REPO_ROOT / "ml" / "audit"

AUDIT_DIR.mkdir(parents=True, exist_ok=True)

def run_audit():
    print("=" * 60)
    print("STEP 6C.1: FULL CURRENT-PROJECT PREDICTION AUDIT")
    print("=" * 60)

    # 1. Load dataset
    print(f"Loading dataset from: {DATASET_PATH}")
    df = pd.read_csv(DATASET_PATH, dtype={"project_id": str})
    total_projects = len(df)
    print(f"Total rows in dataset: {total_projects}")

    # 2. Load schema
    schema_path = SCHEMAS_DIR / "production_feature_schema.csv"
    schema_df = pd.read_csv(schema_path)
    feature_names = schema_df["feature_name"].tolist()
    print(f"Loaded {len(feature_names)} features from schema.")

    # 3. Load production models
    cost_model = joblib.load(MODELS_DIR / "cost_overrun_model.joblib")
    delay_model = joblib.load(MODELS_DIR / "delay_model.joblib")
    delay_reg = joblib.load(MODELS_DIR / "delay_regressor.joblib")
    print("Loaded locked production models:")
    print(f"  - Cost Model: {type(cost_model)}")
    print(f"  - Delay Model: {type(delay_model)}")
    print(f"  - Delay Regressor: {type(delay_reg)}")

    COST_THRESHOLD = 0.40
    DELAY_THRESHOLD = 0.50

    # 4. Prepare feature dataframe
    X = df[feature_names].copy()

    # 5. Run vector/batch predictions for speed, but also validate per-row
    print("\nRunning model inferences...")
    cost_probs = cost_model.predict_proba(X)[:, 1]
    delay_probs = delay_model.predict_proba(X)[:, 1]
    delay_reg_preds = delay_reg.predict(X)

    # 6. Process each project and build audit records
    audit_records = []
    validation_failures = []
    
    unique_pids = set()
    duplicate_pids = set()

    for idx, row in df.iterrows():
        pid = str(row["project_id"])
        pname = str(row["project_name"])
        smonth = str(row["snapshot_month"])

        if pid in unique_pids:
            duplicate_pids.add(pid)
        unique_pids.add(pid)

        c_prob = float(cost_probs[idx])
        d_prob = float(delay_probs[idx])
        raw_delay = float(delay_reg_preds[idx])

        # Validation checks
        errors = []
        if np.isnan(c_prob) or np.isinf(c_prob) or not (0.0 <= c_prob <= 1.0):
            errors.append(f"Invalid cost_probability: {c_prob}")
        if np.isnan(d_prob) or np.isinf(d_prob) or not (0.0 <= d_prob <= 1.0):
            errors.append(f"Invalid delay_probability: {d_prob}")
        if np.isnan(raw_delay) or np.isinf(raw_delay):
            errors.append(f"Invalid predicted_delay_months_raw: {raw_delay}")

        c_flag = 1 if c_prob >= COST_THRESHOLD else 0
        d_flag = 1 if d_prob >= DELAY_THRESHOLD else 0

        # Component risk labels
        c_risk = "HIGH" if c_flag == 1 else ("MEDIUM" if c_prob >= 0.30 else "LOW")
        d_risk = "HIGH" if d_flag == 1 else ("MEDIUM" if d_prob >= 0.30 else "LOW")

        # Overall risk
        o_risk = compute_overall_risk(
            cost_flag=c_flag,
            delay_flag=d_flag,
            cost_probability=c_prob,
            delay_probability=d_prob,
        )

        # Risk consistency check
        if c_flag == 1 and d_flag == 1 and o_risk != "CRITICAL":
            errors.append(f"Inconsistent overall_risk: expected CRITICAL, got {o_risk}")
        elif (c_flag == 1 or d_flag == 1) and o_risk not in ("HIGH", "CRITICAL"):
            errors.append(f"Inconsistent overall_risk: expected HIGH/CRITICAL, got {o_risk}")

        status = "SUCCESS" if not errors else "FAILED"
        err_msg = "; ".join(errors) if errors else ""

        if errors:
            validation_failures.append((pid, err_msg))

        audit_records.append({
            "project_id": pid,
            "project_name": pname,
            "snapshot_month": smonth,
            "cost_overrun_probability": round(c_prob, 4),
            "cost_overrun_risk": c_risk,
            "cost_overrun_flag": c_flag,
            "schedule_delay_probability": round(d_prob, 4),
            "schedule_delay_risk": d_risk,
            "schedule_delay_flag": d_flag,
            "predicted_delay_months_raw": round(raw_delay, 2),
            "overall_risk": o_risk,
            "prediction_status": status,
            "error_message": err_msg,
        })

    audit_df = pd.DataFrame(audit_records)

    # Save full prediction audit CSV
    audit_csv_path = AUDIT_DIR / "full_prediction_audit.csv"
    audit_df.to_csv(audit_csv_path, index=False)
    print(f"\nSaved full prediction audit to: {audit_csv_path}")

    # 7. Summary & Quality Statistics
    success_count = (audit_df["prediction_status"] == "SUCCESS").sum()
    failed_count = (audit_df["prediction_status"] == "FAILED").sum()

    print(f"\n--- INFERENCE AUDIT RESULTS ---")
    print(f"Total Projects Audited: {len(audit_df)}")
    print(f"Successful: {success_count} ({success_count / len(audit_df) * 100:.2f}%)")
    print(f"Failed: {failed_count}")
    print(f"Unique Project IDs: {len(unique_pids)}")
    print(f"Duplicate Project IDs: {len(duplicate_pids)}")

    # 8. Delay Statistics
    delays = audit_df["predicted_delay_months_raw"]
    min_delay = delays.min()
    max_delay = delays.max()
    mean_delay = delays.mean()
    median_delay = delays.median()
    std_delay = delays.std()

    neg_delays = audit_df[delays < 0]
    zero_delays = audit_df[delays == 0]
    near_zero = audit_df[(delays >= -1.0) & (delays <= 1.0)]
    pos_delays = audit_df[delays > 0]
    large_pos_60 = audit_df[delays > 60]
    large_pos_120 = audit_df[delays > 120]

    print(f"\n--- DELAY REGRESSION STATISTICS (RAW) ---")
    print(f"Min: {min_delay:.2f} months")
    print(f"Max: {max_delay:.2f} months")
    print(f"Mean: {mean_delay:.2f} months")
    print(f"Median: {median_delay:.2f} months")
    print(f"Std Dev: {std_delay:.2f} months")
    print(f"Negative delay (< 0): {len(neg_delays)} ({len(neg_delays)/len(audit_df)*100:.2f}%)")
    print(f"Near-zero ([-1, 1]): {len(near_zero)} ({len(near_zero)/len(audit_df)*100:.2f}%)")
    print(f"Positive delay (> 0): {len(pos_delays)} ({len(pos_delays)/len(audit_df)*100:.2f}%)")
    print(f"Large delay (> 60 mo / 5 yr): {len(large_pos_60)} ({len(large_pos_60)/len(audit_df)*100:.2f}%)")
    print(f"Extreme delay (> 120 mo / 10 yr): {len(large_pos_120)} ({len(large_pos_120)/len(audit_df)*100:.2f}%)")

    # 9. Extreme Delay Analysis
    audit_df_with_features = audit_df.copy()
    audit_df_with_features["abs_delay"] = audit_df["predicted_delay_months_raw"].abs()
    
    # Merge relevant features from df for deep inspection
    inspect_cols = [
        "project_id", "project_name", "snapshot_month", "predicted_delay_months_raw", "abs_delay",
        "schedule_delay_probability", "cost_overrun_probability", "overall_risk"
    ]
    
    feature_subset_cols = [
        "sector", "state", "total_sanctioned_cost", "total_cumulative_expenditure",
        "time_burn_rate", "cost_burn_rate", "schedule_cost_slippage_ratio",
        "elapsed_months_original", "revised_schedule_delay_months",
        "reported_cost_overrun_pct", "physical_progress_pct"
    ]
    for c in feature_subset_cols:
        if c in df.columns:
            audit_df_with_features[c] = df[c]

    extreme_df = audit_df_with_features.sort_values(by="abs_delay", ascending=False)
    
    # Save extreme delay predictions CSV
    extreme_csv_path = AUDIT_DIR / "extreme_delay_predictions.csv"
    extreme_df.to_csv(extreme_csv_path, index=False)
    print(f"\nSaved extreme delay predictions to: {extreme_csv_path}")

    # 10. Reference Projects Verification
    ref_pids = ["400234", "400161", "612786", "611950", "709790", "400152", "611142", "701586", "705503", "400104"]
    ref_df = audit_df[audit_df["project_id"].isin(ref_pids)].copy()
    print("\n--- REFERENCE PROJECTS AUDIT ---")
    print(ref_df[["project_id", "project_name", "cost_overrun_probability", "schedule_delay_probability", "predicted_delay_months_raw", "overall_risk"]].to_string(index=False))

    # 11. Risk Tier Distributions
    print("\n--- OVERALL RISK LEVEL DISTRIBUTION ---")
    print(audit_df["overall_risk"].value_counts().to_string())

    print("\n--- COST RISK DISTRIBUTION ---")
    print(audit_df["cost_overrun_risk"].value_counts().to_string())

    print("\n--- DELAY RISK DISTRIBUTION ---")
    print(audit_df["schedule_delay_risk"].value_counts().to_string())

    return {
        "audit_df": audit_df,
        "extreme_df": extreme_df,
        "ref_df": ref_df,
        "total_projects": total_projects,
        "success_count": success_count,
        "failed_count": failed_count,
        "min_delay": min_delay,
        "max_delay": max_delay,
        "mean_delay": mean_delay,
        "median_delay": median_delay,
        "std_delay": std_delay,
        "neg_delays_count": len(neg_delays),
        "zero_delays_count": len(zero_delays),
        "near_zero_count": len(near_zero),
        "pos_delays_count": len(pos_delays),
        "large_pos_60_count": len(large_pos_60),
        "large_pos_120_count": len(large_pos_120),
    }

if __name__ == "__main__":
    run_audit()
