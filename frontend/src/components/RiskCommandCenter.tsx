import React from 'react';
import { ComponentRisk } from '../types/project';

interface RiskCommandCenterProps {
  costProbability: number;
  costRisk: ComponentRisk;
  delayProbability: number;
  delayRisk: ComponentRisk;
  predictedDelayMonths: number;
}

export const formatDelayDisplay = (rawDelay: number): { label: string; isAhead: boolean; absMonths: number } => {
  if (rawDelay < 0) {
    const absVal = Math.abs(rawDelay);
    return {
      label: `Ahead of schedule by ${absVal.toFixed(2)} months`,
      isAhead: true,
      absMonths: absVal,
    };
  }
  return {
    label: `Predicted delay: ${rawDelay.toFixed(2)} months`,
    isAhead: false,
    absMonths: rawDelay,
  };
};

export const getComponentRiskBadgeClass = (risk: ComponentRisk): string => {
  switch (risk) {
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

export const RiskCommandCenter: React.FC<RiskCommandCenterProps> = ({
  costProbability,
  costRisk,
  delayProbability,
  delayRisk,
  predictedDelayMonths,
}) => {
  const costPct = Math.min(Math.max(costProbability * 100, 0), 100);
  const delayPct = Math.min(Math.max(delayProbability * 100, 0), 100);
  const delayInfo = formatDelayDisplay(predictedDelayMonths);

  return (
    <div className="risk-command-center" data-testid="risk-command-center">
      <div className="command-center-header">
        <h3 className="section-title">Risk Assessment Command Center</h3>
        <span className="section-subtext">Real-time model inferences evaluated against locked decision thresholds</span>
      </div>

      <div className="metrics-grid">
        {/* Cost Overrun Risk Card */}
        <div className="metric-card" data-testid="cost-risk-card">
          <div className="metric-card-header">
            <div className="metric-header-titles">
              <span className="metric-title">COST OVERRUN RISK</span>
              <span className="metric-subtitle-pill">Sanction Budget Risk</span>
            </div>
            <span className={`badge-component ${getComponentRiskBadgeClass(costRisk)}`}>
              {costRisk}
            </span>
          </div>

          <div className="metric-hero-value">
            <span className="value-digits tabular-nums">{(costProbability * 100).toFixed(2)}</span>
            <span className="value-unit">%</span>
          </div>

          <div className="gauge-meter-wrapper">
            <div className="gauge-track">
              <div
                className={`gauge-fill gauge-fill-${costRisk.toLowerCase()}`}
                style={{ width: `${costPct}%` }}
              />
              {/* Threshold Pin at 40% */}
              <div className="gauge-threshold-pin" style={{ left: '40%' }} title="Decision Threshold: 40%">
                <span className="gauge-pin-label">40% Threshold</span>
              </div>
            </div>
            <div className="gauge-scale">
              <span>0%</span>
              <span className="scale-mark-advisory">30% Advisory</span>
              <span>100%</span>
            </div>
          </div>

          <div className="metric-card-footer">
            <span className="threshold-meta">
              Decision Threshold: <strong>0.40</strong> | Model: <code>cost_overrun_model</code>
            </span>
          </div>
        </div>

        {/* Schedule Delay Risk Card (Card 2) */}
        <div className="metric-card" data-testid="delay-risk-card">
          <div className="metric-card-header">
            <div className="metric-header-titles">
              <span className="metric-title">Schedule Delay Risk</span>
              <span className="metric-subtitle-pill" data-testid="card2-subtitle">Revised Deadline Risk</span>
            </div>
            <span className={`badge-component ${getComponentRiskBadgeClass(delayRisk)}`}>
              {delayRisk}
            </span>
          </div>

          <div className="metric-hero-value">
            <span className="value-digits tabular-nums">{(delayProbability * 100).toFixed(2)}</span>
            <span className="value-unit">%</span>
          </div>

          <div className="gauge-meter-wrapper">
            <div className="gauge-track">
              <div
                className={`gauge-fill gauge-fill-${delayRisk.toLowerCase()}`}
                style={{ width: `${delayPct}%` }}
              />
              {/* Threshold Pin at 50% */}
              <div className="gauge-threshold-pin" style={{ left: '50%' }} title="Decision Threshold: 50%">
                <span className="gauge-pin-label">50% Threshold</span>
              </div>
            </div>
            <div className="gauge-scale">
              <span>0%</span>
              <span className="scale-mark-advisory">30% Advisory</span>
              <span>100%</span>
            </div>
          </div>

          <div className="metric-card-footer">
            <span className="threshold-meta">
              Binary risk: completion &ge; 60 days beyond revised deadline | Model: <code>delay_model</code> (Threshold: <strong>0.50</strong>)
            </span>
          </div>
        </div>

        {/* Projected Schedule Variance Card (Card 3) */}
        <div className="metric-card" data-testid="schedule-variance-card">
          <div className="metric-card-header">
            <div className="metric-header-titles">
              <span className="metric-title">Projected Schedule Variance</span>
              <span className="metric-subtitle-pill" data-testid="card3-subtitle">Original Baseline Delay</span>
            </div>
            <span className={`badge-component ${delayInfo.isAhead ? 'badge-low' : 'badge-high'}`}>
              {delayInfo.isAhead ? 'AHEAD OF SCHEDULE' : 'PROJECTED DELAY'}
            </span>
          </div>

          <div className={`metric-hero-value variance-headline ${delayInfo.isAhead ? 'text-ahead' : 'text-delayed'}`}>
            <span className="variance-text">{delayInfo.label}</span>
          </div>

          <div className="variance-indicator-box">
            <div className={`variance-status-bar ${delayInfo.isAhead ? 'bar-ahead' : 'bar-delayed'}`} />
            <p className="variance-explanation">
              {delayInfo.isAhead
                ? 'Model projects project completion prior to original completion baseline.'
                : 'Predicted delay in months vs original completion baseline.'}
            </p>
          </div>

          <div className="metric-card-footer" data-testid="raw-delay-audit">
            <span className="threshold-meta">
              Predicted delay in months vs original completion baseline: <code>{predictedDelayMonths.toFixed(2)} mo</code> (from <code>delay_regressor</code>)
            </span>
          </div>
        </div>
      </div>

      {/* Multi-Model Target Interpretation Banner (Purely Explanatory) */}
      <div className="multi-model-note-box" data-testid="multi-model-explanation">
        <span className="note-icon" aria-hidden="true">ℹ️</span>
        <span className="note-text">
          <strong>Dual-Model Schedule Interpretation:</strong> Schedule-delay probability measures the binary risk of completing &ge; 60 days beyond the revised deadline, while predicted delay estimates the continuous number of months beyond the original completion baseline.
        </span>
      </div>
    </div>
  );
};
