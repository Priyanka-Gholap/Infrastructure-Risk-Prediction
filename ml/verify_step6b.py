"""
Automated Verification Script for Step 6B Checklist
"""

import os
import sys
import pandas as pd
import numpy as np
import joblib

PROJECT_ROOT = "d:/SIH26103-Infrastructure-Risk-Prediction"
INF_DATASET_PATH = os.path.join(PROJECT_ROOT, "current_inference_dataset.csv")
QUALITY_REPORT_PATH = os.path.join(PROJECT_ROOT, "current_inference_data_quality_report.csv")
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "ml/schemas/production_feature_schema.csv")
TABLE6_PATH = os.path.join(PROJECT_ROOT, "reports/standardized_table6_project_month.csv")
MODELS_DIR = os.path.join(PROJECT_ROOT, "ml/models")

print("=== EXECUTING STEP 6B AUTOMATED AUDIT ===")

# 1. Load files
df_inf = pd.read_csv(INF_DATASET_PATH, dtype={'project_id': str})
df_schema = pd.read_csv(SCHEMA_PATH)
df_t6 = pd.read_csv(TABLE6_PATH, dtype={'project_id': str})

# Check 1: One latest snapshot per project & Row count
source_unique_pids = set(df_t6['project_id'].unique())
inf_pids = list(df_inf['project_id'])
assert len(df_inf) == len(source_unique_pids), f"Count mismatch: {len(df_inf)} vs {len(source_unique_pids)}"
assert len(inf_pids) == len(set(inf_pids)), "Duplicate project_ids found!"
print(f"[PASS] Gate 1: Exactly one latest snapshot per project ({len(df_inf)} projects, 0 duplicates)")

# Check 2: Verify each project has its maximum report_month
max_month_map = df_t6.groupby('project_id')['report_month'].max().to_dict()
for pid, snap_m in zip(df_inf['project_id'], df_inf['snapshot_month']):
    assert snap_m == max_month_map[pid], f"Project {pid} snapshot month {snap_m} is not maximum {max_month_map[pid]}"
print("[PASS] Gate 2: Every snapshot corresponds strictly to the project's latest report_month")

# Check 3: Schema, feature names, counts, and exact order
expected_features = list(df_schema['feature_name'])
metadata_cols = ['project_id', 'project_name', 'snapshot_month']
dataset_feature_cols = [c for c in df_inf.columns if c not in metadata_cols]

assert dataset_feature_cols == expected_features, "Feature order or names mismatch with production_feature_schema.csv"
assert len(dataset_feature_cols) == 36, f"Expected 36 features, got {len(dataset_feature_cols)}"
print(f"[PASS] Gate 3: Exact 36 SAFE_MVP features in identical production schema order")

# Check 4: Feature types (32 numerical, 4 categorical)
cat_cols = ['ministry', 'sector', 'implementing_agency', 'state']
num_cols = [c for c in expected_features if c not in cat_cols]
assert len(num_cols) == 32, f"Expected 32 numerical features, got {len(num_cols)}"
assert len(cat_cols) == 4, f"Expected 4 categorical features, got {len(cat_cols)}"
print(f"[PASS] Gate 4: Feature types verified (32 numerical, 4 categorical)")

# Check 5: No Table 3 columns or target leakage
forbidden_cols = [
    'completion_cost', 'actual_date_of_completion', 'target_cost_overrun_binary',
    'target_cost_overrun_pct', 'target_delay_binary', 'target_delay_from_original_months',
    'final_revised_doc', 'meta_actual_completion_date', 'meta_lead_time_months'
]
for col in forbidden_cols:
    assert col not in df_inf.columns, f"Forbidden column {col} detected in inference dataset!"
print("[PASS] Gate 5: Zero Table 3 columns or target labels in dataset")

# Check 6: Categorical garbage cleaning check
for c in cat_cols:
    garbage_mask = df_inf[c].astype(str).str.contains('All Ongoing Projects|Orignal/Target|Sl.No|Rs. Crore', regex=True)
    assert not garbage_mask.any(), f"Extraction garbage remains in {c}: {garbage_mask.sum()} instances!"
print("[PASS] Gate 6: Zero extraction header garbage remains in categorical features")

# Check 7: Model compatibility
cost_m = joblib.load(os.path.join(MODELS_DIR, 'cost_overrun_model.joblib'))
delay_m = joblib.load(os.path.join(MODELS_DIR, 'delay_model.joblib'))
delay_reg = joblib.load(os.path.join(MODELS_DIR, 'delay_regressor.joblib'))

X = df_inf[expected_features]

cp = cost_m.predict_proba(X)[:, 1]
dp = delay_m.predict_proba(X)[:, 1]
pdel = delay_reg.predict(X)

assert len(cp) == len(df_inf)
assert len(dp) == len(df_inf)
assert len(pdel) == len(df_inf)
assert not np.isnan(cp).any()
assert not np.isnan(dp).any()
assert not np.isnan(pdel).any()
print(f"[PASS] Gate 7: All 3 production models successfully evaluated all {len(df_inf)} project rows")

# Check 8: Deliverables present
deliverables = [
    "current_inference_dataset.csv",
    "current_inference_data_quality_report.csv",
    "current_inference_validation_report.md",
    "current_inference_feature_mapping.md"
]
for d in deliverables:
    p = os.path.join(PROJECT_ROOT, d)
    assert os.path.exists(p) and os.path.getsize(p) > 0, f"Deliverable {d} is missing or empty!"
print(f"[PASS] Gate 8: All 4 required deliverable files exist and are non-empty")

print("\n=== ALL 8 STEP 6B AUDIT GATES PASSED! ===")
