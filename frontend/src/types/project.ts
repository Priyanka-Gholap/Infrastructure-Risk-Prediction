/**
 * TypeScript contracts mirroring backend Pydantic schemas in backend/app/schemas.py.
 */

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type ComponentRisk = 'LOW' | 'MEDIUM' | 'HIGH';

export interface ProjectLookupItem {
  project_id: string;
  project_name: string;
  snapshot_month: string;
}

export interface ProjectPredictionResponse {
  project_id: string;
  project_name: string;
  snapshot_month: string;
  overall_risk: RiskLevel;
  cost_overrun_probability: number;
  cost_overrun_risk: ComponentRisk;
  schedule_delay_probability: number;
  schedule_delay_risk: ComponentRisk;
  predicted_delay_months: number;
}

export interface HealthResponse {
  status: string;
  models_loaded: boolean;
  version?: string;
  feature_count?: number;
}

export type DriverDirection =
  | 'INCREASES_RISK'
  | 'DECREASES_RISK'
  | 'INCREASES_DELAY'
  | 'REDUCES_DELAY';

export interface FeatureDriver {
  feature_name: string;
  display_name: string;
  feature_value: number | string | null;
  is_missing: boolean;
  unit: string;
  contribution: number;
  contribution_display: string;
  direction: DriverDirection;
  rank: number;
}

export interface ModelExplanation {
  model_name: string;
  target_metric: 'cost_overrun_probability' | 'schedule_delay_probability' | 'predicted_delay_months';
  base_value: number;
  predicted_value: number;
  total_contribution: number;
  displayed_contribution: number;
  audit_reconciliation_gap: number;
  top_drivers: FeatureDriver[];
  audit_status: 'reconciled' | 'discrepancy';
}

export interface ProjectExplainabilityResponse {
  project_id: string;
  project_name: string;
  snapshot_month: string;
  cost_overrun_explanation: ModelExplanation;
  schedule_delay_explanation: ModelExplanation;
  predicted_delay_explanation: ModelExplanation;
  top_k: number;
}
