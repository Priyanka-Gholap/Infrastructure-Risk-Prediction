import React from 'react';
import {
  ProjectPredictionResponse,
  ProjectExplainabilityResponse,
  RiskLevel,
} from '../types/project';
import { OverallRiskHero } from './OverallRiskHero';
import {
  RiskCommandCenter,
  formatDelayDisplay,
  getComponentRiskBadgeClass,
} from './RiskCommandCenter';
import { ExplainabilityPanel } from './ExplainabilityPanel';
import { EarlyWarningSummary } from './EarlyWarningSummary';
import { ProjectMetadataPanel } from './ProjectMetadataPanel';
import { PredictionPipeline } from './PredictionPipeline';

interface PredictionDisplayProps {
  prediction: ProjectPredictionResponse | null;
  isLoading: boolean;
  explainability?: ProjectExplainabilityResponse | null;
  isLoadingExplain?: boolean;
  explainError?: string | null;
}

export { formatDelayDisplay, getComponentRiskBadgeClass };

export const getRiskBadgeClass = (risk: RiskLevel): string => {
  switch (risk) {
    case 'CRITICAL':
      return 'badge-critical';
    case 'HIGH':
      return 'badge-high';
    case 'MEDIUM':
      return 'badge-medium';
    case 'LOW':
      return 'badge-low';
    default:
      return '';
  }
};

export const PredictionDisplay: React.FC<PredictionDisplayProps> = ({
  prediction,
  isLoading,
  explainability = null,
  isLoadingExplain = false,
  explainError = null,
}) => {
  if (isLoading) {
    return (
      <section className="prediction-section card loading-card" data-testid="prediction-loading">
        <div className="loading-container">
          <div className="spinner" />
          <p className="loading-text">Executing Multi-Model ML Ensemble...</p>
          <span className="subtext">
            Evaluating 36 SAFE_MVP features against <code>cost_overrun_model</code>, <code>delay_model</code>, and <code>delay_regressor</code>
          </span>
        </div>
      </section>
    );
  }

  if (!prediction) {
    return null;
  }

  return (
    <section className="prediction-section-wrapper" data-testid="prediction-display">
      {/* 1. Overall Risk Hero Banner (Authoritative Backend overall_risk) */}
      <OverallRiskHero
        projectName={prediction.project_name}
        projectId={prediction.project_id}
        snapshotMonth={prediction.snapshot_month}
        overallRisk={prediction.overall_risk}
      />

      {/* 2. Risk Command Center (3 Core Metric Cards with Progress Meters) */}
      <RiskCommandCenter
        costProbability={prediction.cost_overrun_probability}
        costRisk={prediction.cost_overrun_risk}
        delayProbability={prediction.schedule_delay_probability}
        delayRisk={prediction.schedule_delay_risk}
        predictedDelayMonths={prediction.predicted_delay_months}
      />

      {/* 3. Predictive Risk Drivers & Early Warning Attribution (SHAP TreeExplainer) */}
      <ExplainabilityPanel
        explainability={explainability}
        isLoading={isLoadingExplain}
        error={explainError}
      />

      {/* 4. Operational & Technical Intelligence Grid */}
      <div className="details-two-col-grid">
        {/* Left Column: Early Warning Summary (Real API outputs only) */}
        <EarlyWarningSummary
          overallRisk={prediction.overall_risk}
          costRisk={prediction.cost_overrun_risk}
          costProbability={prediction.cost_overrun_probability}
          delayRisk={prediction.schedule_delay_risk}
          delayProbability={prediction.schedule_delay_probability}
          predictedDelayMonths={prediction.predicted_delay_months}
        />

        {/* Right Column: Project Metadata & Technical Prediction Pipeline */}
        <div className="metadata-pipeline-stack">
          <ProjectMetadataPanel
            projectId={prediction.project_id}
            projectName={prediction.project_name}
            snapshotMonth={prediction.snapshot_month}
          />
          <PredictionPipeline />
        </div>
      </div>
    </section>
  );
};
