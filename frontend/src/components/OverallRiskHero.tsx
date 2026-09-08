import React from 'react';
import { RiskLevel } from '../types/project';

interface OverallRiskHeroProps {
  projectName: string;
  projectId: string;
  snapshotMonth: string;
  overallRisk: RiskLevel;
}

export const getRiskDescription = (risk: RiskLevel): string => {
  switch (risk) {
    case 'CRITICAL':
      return 'Dual High Risk — Both Cost Overrun (≥ 40%) and Schedule Delay (≥ 50%) alert thresholds simultaneously breached.';
    case 'HIGH':
      return 'High Priority Alert — Primary decision threshold breached for Cost Overrun (≥ 40%) or Schedule Delay (≥ 50%).';
    case 'MEDIUM':
      return 'Elevated Watchlist — Probability exceeds early warning advisory level (≥ 30%). Close monitoring recommended.';
    case 'LOW':
      return 'Nominal Execution — All predictive indicators remain within normal operational tolerance (< 30%).';
    default:
      return 'Status under evaluation.';
  }
};

export const getHeroRiskClass = (risk: RiskLevel): string => {
  switch (risk) {
    case 'CRITICAL':
      return 'hero-risk-critical';
    case 'HIGH':
      return 'hero-risk-high';
    case 'MEDIUM':
      return 'hero-risk-medium';
    case 'LOW':
      return 'hero-risk-low';
    default:
      return '';
  }
};

export const OverallRiskHero: React.FC<OverallRiskHeroProps> = ({
  projectName,
  projectId,
  snapshotMonth,
  overallRisk,
}) => {
  return (
    <div className={`overall-risk-hero card ${getHeroRiskClass(overallRisk)}`} data-testid="overall-risk-hero">
      <div className="hero-top-row">
        <div className="hero-project-info">
          <span className="hero-kicker">MONITORED INFRASTRUCTURE ASSET</span>
          <h2 className="hero-project-title">{projectName}</h2>
          <div className="hero-meta-pills">
            <span className="hero-meta-pill">
              Project ID: <strong>{projectId}</strong>
            </span>
            <span className="hero-meta-pill">
              Snapshot Month: <strong>{snapshotMonth}</strong>
            </span>
            <span className="hero-meta-pill">
              Pipeline: <strong>MoSPI / IPMD</strong>
            </span>
          </div>
        </div>

        <div className="hero-badge-container">
          <span className="hero-badge-label">OVERALL RISK TIER</span>
          <div className={`hero-badge hero-badge-${overallRisk.toLowerCase()}`}>
            <span className="hero-badge-dot" />
            <span className="hero-badge-text">{overallRisk}</span>
          </div>
        </div>
      </div>

      <div className="hero-summary-bar">
        <div className="hero-summary-content">
          <span className="hero-summary-tag">OPERATIONAL STATUS</span>
          <p className="hero-summary-text">{getRiskDescription(overallRisk)}</p>
        </div>
      </div>
    </div>
  );
};
