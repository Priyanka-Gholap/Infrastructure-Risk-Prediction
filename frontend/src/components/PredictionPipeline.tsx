import React from 'react';

export const PredictionPipeline: React.FC = () => {
  return (
    <div className="card prediction-pipeline-card" data-testid="prediction-pipeline">
      <div className="card-header-with-badge">
        <div>
          <h3 className="card-title">Prediction Pipeline Architecture</h3>
          <span className="card-subtitle">Technical system specifications of the locked ML inference engine</span>
        </div>
        <span className="pipeline-pill">Pipeline Reference</span>
      </div>

      <div className="pipeline-specs-grid">
        <div className="pipeline-spec-item">
          <span className="spec-label">ENSEMBLE MODELS</span>
          <div className="spec-model-tags">
            <code>cost_overrun_model.joblib</code>
            <code>delay_model.joblib</code>
            <code>delay_regressor.joblib</code>
          </div>
        </div>

        <div className="pipeline-spec-item">
          <span className="spec-label">FEATURE VECTOR</span>
          <span className="spec-value">36 SAFE_MVP Production Features (Zero Leakage)</span>
        </div>

        <div className="pipeline-spec-item">
          <span className="spec-label">LOCKED RISK POLICY</span>
          <div className="policy-badges">
            <span className="policy-badge">Cost High: <strong>P ≥ 0.40</strong></span>
            <span className="policy-badge">Delay High: <strong>P ≥ 0.50</strong></span>
            <span className="policy-badge">Advisory: <strong>P ≥ 0.30</strong></span>
          </div>
        </div>
      </div>
    </div>
  );
};
