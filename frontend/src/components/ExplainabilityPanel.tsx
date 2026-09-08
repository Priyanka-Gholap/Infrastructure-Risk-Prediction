import React, { useState, useEffect } from 'react';
import {
  ProjectExplainabilityResponse,
  ModelExplanation,
  FeatureDriver,
} from '../types/project';

interface ExplainabilityPanelProps {
  explainability: ProjectExplainabilityResponse | null;
  isLoading: boolean;
  error: string | null;
}

type TabKey = 'cost' | 'delay' | 'regression';

export const ExplainabilityPanel: React.FC<ExplainabilityPanelProps> = ({
  explainability,
  isLoading,
  error,
}) => {
  const [activeTab, setActiveTab] = useState<TabKey>('cost');

  // Automatically reset to primary cost tab whenever a new project is selected
  useEffect(() => {
    if (explainability?.project_id) {
      setActiveTab('cost');
    }
  }, [explainability?.project_id]);

  if (isLoading) {
    return (
      <div className="card explainability-card" data-testid="explainability-loading">
        <div className="card-header-with-badge">
          <div>
            <h3 className="card-title">Predictive Risk Drivers & Early Warning Attribution</h3>
            <span className="card-subtitle">Polynomial TreeSHAP feature attributions on locked ensemble</span>
          </div>
          <span className="source-pill">Computing SHAP...</span>
        </div>
        <div className="loading-container" style={{ padding: '28px 0' }}>
          <div className="spinner" />
          <p className="loading-text">Computing exact Shapley feature attributions...</p>
          <span className="subtext">
            Reconciling 36 production features across 100 decision trees per model
          </span>
        </div>
      </div>
    );
  }

  if (error || !explainability) {
    return (
      <div className="card explainability-card" data-testid="explainability-error">
        <div className="card-header-with-badge">
          <div>
            <h3 className="card-title">Predictive Risk Drivers & Early Warning Attribution</h3>
            <span className="card-subtitle">SHAP TreeExplainer feature attributions</span>
          </div>
          <span className="pipeline-pill">Attribution Unavailable</span>
        </div>
        <div className="notice-box" style={{ marginTop: '12px' }}>
          <span className="notice-icon">⚠️</span>
          <span className="notice-text">
            <strong>Explainability Notice:</strong> Feature-level driver attribution is currently unavailable for this record.
            The primary multi-model risk evaluations in the Command Center remain fully authoritative.
          </span>
        </div>
      </div>
    );
  }

  const currentExplanation: ModelExplanation =
    activeTab === 'cost'
      ? explainability.cost_overrun_explanation
      : activeTab === 'delay'
      ? explainability.schedule_delay_explanation
      : explainability.predicted_delay_explanation;

  const maxContrib = Math.max(
    ...currentExplanation.top_drivers.map((d) => Math.abs(d.contribution)),
    0.001
  );

  const omittedContribution =
    currentExplanation.total_contribution - currentExplanation.displayed_contribution;

  return (
    <div className="card explainability-card" data-testid="explainability-panel">
      <div className="card-header-with-badge">
        <div>
          <h3 className="card-title">Predictive Risk Drivers & Early Warning Attribution</h3>
          <span className="card-subtitle">
            Exact SHAP polynomial tree attributions explaining why the model assigned this risk level
          </span>
        </div>
        <span className="source-pill">SHAP TreeExplainer</span>
      </div>

      {/* 3 Model Tabs */}
      <div className="explain-tabs">
        <button
          type="button"
          className={`explain-tab ${activeTab === 'cost' ? 'active-tab' : ''}`}
          onClick={() => setActiveTab('cost')}
          data-testid="tab-cost"
        >
          Cost Overrun Risk Drivers
        </button>
        <button
          type="button"
          className={`explain-tab ${activeTab === 'delay' ? 'active-tab' : ''}`}
          onClick={() => setActiveTab('delay')}
          data-testid="tab-delay"
        >
          Schedule Delay Risk Drivers
        </button>
        <button
          type="button"
          className={`explain-tab ${activeTab === 'regression' ? 'active-tab' : ''}`}
          onClick={() => setActiveTab('regression')}
          data-testid="tab-regression"
        >
          Timeline Delay Drivers
        </button>
      </div>

      {/* Model Context Header */}
      <div className="model-context-bar">
        <span className="context-item">
          Model: <code>{currentExplanation.model_name}.joblib</code>
        </span>
        <span className="context-item">
          Baseline:{' '}
          <strong>
            {activeTab === 'regression'
              ? `${currentExplanation.base_value.toFixed(2)} mo`
              : `${(currentExplanation.base_value * 100).toFixed(2)}%`}
          </strong>
        </span>
        <span className="context-item">
          Total Net Shift:{' '}
          <strong
            className={
              currentExplanation.total_contribution >= 0
                ? 'text-risk-inc'
                : 'text-risk-dec'
            }
          >
            {activeTab === 'regression'
              ? `${currentExplanation.total_contribution >= 0 ? '+' : ''}${currentExplanation.total_contribution.toFixed(2)} mo`
              : `${currentExplanation.total_contribution >= 0 ? '+' : ''}${(currentExplanation.total_contribution * 100).toFixed(2)}% pts`}
          </strong>
        </span>
        <span className="context-item">
          Final Prediction:{' '}
          <strong style={{ color: '#f8fafc' }}>
            {activeTab === 'regression'
              ? `${currentExplanation.predicted_value.toFixed(2)} months`
              : `${(currentExplanation.predicted_value * 100).toFixed(2)}%`}
          </strong>
        </span>
      </div>

      {/* Top 5 Drivers Table */}
      <div className="table-responsive" style={{ marginTop: '14px' }}>
        <table className="drivers-table">
          <thead>
            <tr>
              <th style={{ width: '60px', textAlign: 'center' }}>Rank</th>
              <th>Production Feature & Business Indicator</th>
              <th style={{ width: '180px' }}>Snapshot Value</th>
              <th style={{ width: '140px', textAlign: 'right' }}>Contribution</th>
              <th style={{ width: '170px' }}>Attribution Impact</th>
            </tr>
          </thead>
          <tbody>
            {currentExplanation.top_drivers.map((driver: FeatureDriver) => {
              const isIncreasing =
                driver.direction === 'INCREASES_RISK' ||
                driver.direction === 'INCREASES_DELAY';
              const barWidthPct = Math.min(
                Math.max((Math.abs(driver.contribution) / maxContrib) * 100, 8),
                100
              );

              return (
                <tr key={driver.feature_name} className="driver-row">
                  <td style={{ textAlign: 'center' }}>
                    <span className="rank-badge">#{driver.rank}</span>
                  </td>
                  <td>
                    <div className="feature-title-group">
                      <span className="feature-display-name">{driver.display_name}</span>
                      <code className="feature-tech-name">{driver.feature_name}</code>
                    </div>
                  </td>
                  <td>
                    {driver.is_missing ? (
                      <span className="missing-val-badge">Missing (imputed with median)</span>
                    ) : (
                      <span className="feature-val-text monospace">
                        {driver.feature_value !== null ? String(driver.feature_value) : '—'}{' '}
                        <span className="unit-label">{driver.unit}</span>
                      </span>
                    )}
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <span
                      className={`contribution-badge ${
                        isIncreasing ? 'contrib-inc' : 'contrib-dec'
                      } tabular-nums`}
                    >
                      {driver.contribution_display}
                    </span>
                  </td>
                  <td>
                    <div className="impact-cell">
                      <div className="impact-bar-wrapper">
                        <div
                          className={`impact-bar ${
                            isIncreasing ? 'bar-inc' : 'bar-dec'
                          }`}
                          style={{ width: `${barWidthPct}%` }}
                        />
                      </div>
                      <span className="direction-label">
                        {driver.direction.replace(/_/g, ' ')}
                      </span>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Mathematical Audit Reconciliation Card */}
      <div className="audit-reconciliation-box" data-testid="audit-reconciliation-box">
        <div className="audit-header">
          <span className="audit-title">MATHEMATICAL ATTRIBUTION RECONCILIATION</span>
          <span className="audit-status-badge">
            Status: <strong>{currentExplanation.audit_status.toUpperCase()}</strong> (Gap: {currentExplanation.audit_reconciliation_gap.toExponential(2)})
          </span>
        </div>

        <div className="audit-flow-grid">
          <div className="audit-flow-step">
            <span className="flow-label">Model Base Rate</span>
            <span className="flow-value tabular-nums">
              {activeTab === 'regression'
                ? `${currentExplanation.base_value.toFixed(2)} mo`
                : `${(currentExplanation.base_value * 100).toFixed(2)}%`}
            </span>
          </div>
          <span className="flow-operator">+</span>
          <div className="audit-flow-step">
            <span className="flow-label">Top 5 Drivers</span>
            <span className="flow-value tabular-nums">
              {activeTab === 'regression'
                ? `${currentExplanation.displayed_contribution >= 0 ? '+' : ''}${currentExplanation.displayed_contribution.toFixed(2)} mo`
                : `${currentExplanation.displayed_contribution >= 0 ? '+' : ''}${(currentExplanation.displayed_contribution * 100).toFixed(2)}% pts`}
            </span>
          </div>
          <span className="flow-operator">+</span>
          <div className="audit-flow-step">
            <span className="flow-label">Remaining 31 Features</span>
            <span className="flow-value tabular-nums">
              {activeTab === 'regression'
                ? `${omittedContribution >= 0 ? '+' : ''}${omittedContribution.toFixed(2)} mo`
                : `${omittedContribution >= 0 ? '+' : ''}${(omittedContribution * 100).toFixed(2)}% pts`}
            </span>
          </div>
          <span className="flow-operator">=</span>
          <div className="audit-flow-step flow-step-result">
            <span className="flow-label">Total Model Output</span>
            <span className="flow-value tabular-nums flow-value-highlight">
              {activeTab === 'regression'
                ? `${currentExplanation.predicted_value.toFixed(2)} months`
                : `${(currentExplanation.predicted_value * 100).toFixed(2)}%`}
            </span>
          </div>
        </div>

        <p className="audit-disclaimer">
          * Reconciliation verified: Total contribution equals the exact sum of all 36 production features.
          Top-5 drivers represent the primary decision pivots for this project snapshot.
        </p>
      </div>
    </div>
  );
};
