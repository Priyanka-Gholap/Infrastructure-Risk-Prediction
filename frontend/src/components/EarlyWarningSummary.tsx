import React from 'react';
import { RiskLevel, ComponentRisk } from '../types/project';
import { formatDelayDisplay, getComponentRiskBadgeClass } from './RiskCommandCenter';

interface EarlyWarningSummaryProps {
  overallRisk: RiskLevel;
  costRisk: ComponentRisk;
  costProbability: number;
  delayRisk: ComponentRisk;
  delayProbability: number;
  predictedDelayMonths: number;
}

export const EarlyWarningSummary: React.FC<EarlyWarningSummaryProps> = ({
  costRisk,
  costProbability,
  delayRisk,
  delayProbability,
  predictedDelayMonths,
}) => {
  const delayInfo = formatDelayDisplay(predictedDelayMonths);

  return (
    <div className="card early-warning-summary-card" data-testid="early-warning-summary">
      <div className="card-header-with-badge">
        <div>
          <h3 className="card-title">Early Warning Summary</h3>
          <span className="card-subtitle">Operational status synthesized from current prediction response</span>
        </div>
        <span className="source-pill">Real Model Outputs</span>
      </div>

      <div className="early-warning-items-grid">
        {/* Cost Risk Alert Status */}
        <div className="warning-item">
          <div className="warning-item-header">
            <span className="warning-indicator-label">COST OVERRUN WATCH</span>
            <span className={`badge-component ${getComponentRiskBadgeClass(costRisk)}`}>
              {costRisk}
            </span>
          </div>
          <div className="warning-item-body">
            <span className="warning-item-stat tabular-nums">
              {(costProbability * 100).toFixed(2)}% probability
            </span>
            <p className="warning-item-description">
              {costRisk === 'HIGH'
                ? 'High risk alert triggered (exceeds locked 0.40 threshold).'
                : costRisk === 'MEDIUM'
                ? 'Advisory watch triggered (exceeds 0.30 early warning level).'
                : 'Within nominal tolerance (< 0.30 advisory level).'}
            </p>
          </div>
        </div>

        {/* Schedule Risk Alert Status */}
        <div className="warning-item">
          <div className="warning-item-header">
            <span className="warning-indicator-label">SCHEDULE DELAY WATCH</span>
            <span className={`badge-component ${getComponentRiskBadgeClass(delayRisk)}`}>
              {delayRisk}
            </span>
          </div>
          <div className="warning-item-body">
            <span className="warning-item-stat tabular-nums">
              {(delayProbability * 100).toFixed(2)}% probability
            </span>
            <p className="warning-item-description">
              {delayRisk === 'HIGH'
                ? 'High risk alert triggered (exceeds locked 0.50 threshold).'
                : delayRisk === 'MEDIUM'
                ? 'Advisory watch triggered (exceeds 0.30 early warning level).'
                : 'Within nominal tolerance (< 0.30 advisory level).'}
            </p>
          </div>
        </div>

        {/* Timeline Outlook */}
        <div className="warning-item">
          <div className="warning-item-header">
            <span className="warning-indicator-label">TIMELINE OUTLOOK</span>
            <span className={`badge-component ${delayInfo.isAhead ? 'badge-low' : 'badge-high'}`}>
              {delayInfo.isAhead ? 'AHEAD' : 'DELAYED'}
            </span>
          </div>
          <div className="warning-item-body">
            <span className="warning-item-stat tabular-nums">
              {delayInfo.label}
            </span>
            <p className="warning-item-description">
              {delayInfo.isAhead
                ? `Continuous regressor estimates completion ${delayInfo.absMonths.toFixed(2)} months ahead of original completion baseline.`
                : `Continuous regressor estimates timeline delay of ${delayInfo.absMonths.toFixed(2)} months vs original completion baseline.`}
            </p>
          </div>
        </div>
      </div>

      <div className="notice-box active-explain-notice">
        <span className="notice-icon">✓</span>
        <span className="notice-text">
          <strong>SHAP Explainability Active:</strong> Granular root-cause feature attributions and mathematically reconciled decision drivers are presented in the SHAP Explainability Panel.
        </span>
      </div>
    </div>
  );
};
