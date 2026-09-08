import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { PredictionDisplay, formatDelayDisplay } from '../components/PredictionDisplay';
import { ProjectPredictionResponse, ProjectExplainabilityResponse } from '../types/project';

describe('PredictionDisplay Unit & Component Tests', () => {
  describe('formatDelayDisplay logic', () => {
    it('formats negative delay as ahead of schedule with absolute value', () => {
      const res = formatDelayDisplay(-3.83);
      expect(res.label).toBe('Ahead of schedule by 3.83 months');
      expect(res.isAhead).toBe(true);
      expect(res.absMonths).toBe(3.83);
    });

    it('formats large negative delay correctly', () => {
      const res = formatDelayDisplay(-15.39);
      expect(res.label).toBe('Ahead of schedule by 15.39 months');
      expect(res.isAhead).toBe(true);
      expect(res.absMonths).toBe(15.39);
    });

    it('formats positive delay as predicted delay', () => {
      const res = formatDelayDisplay(26.73);
      expect(res.label).toBe('Predicted delay: 26.73 months');
      expect(res.isAhead).toBe(false);
      expect(res.absMonths).toBe(26.73);
    });

    it('formats zero delay as predicted delay: 0.00 months', () => {
      const res = formatDelayDisplay(0);
      expect(res.label).toBe('Predicted delay: 0.00 months');
      expect(res.isAhead).toBe(false);
    });
  });

  describe('PredictionDisplay Component Rendering (Step 6D-C Command Center + Explainability)', () => {
    const sample400234: ProjectPredictionResponse = {
      project_id: '400234',
      project_name: 'Third Railway Line between Patratu-Sonnagar [291 kms]',
      snapshot_month: '2025-12',
      overall_risk: 'LOW',
      cost_overrun_probability: 0.2388,
      cost_overrun_risk: 'LOW',
      schedule_delay_probability: 0.1615,
      schedule_delay_risk: 'LOW',
      predicted_delay_months: -3.83,
    };

    const sampleExplain400234: ProjectExplainabilityResponse = {
      project_id: '400234',
      project_name: 'Third Railway Line between Patratu-Sonnagar [291 kms]',
      snapshot_month: '2025-12',
      top_k: 5,
      cost_overrun_explanation: {
        model_name: 'cost_overrun_model',
        target_metric: 'cost_overrun_probability',
        base_value: 0.496415,
        predicted_value: 0.238848,
        total_contribution: -0.257566,
        displayed_contribution: -0.22438,
        audit_reconciliation_gap: 0.0,
        audit_status: 'reconciled',
        top_drivers: [
          {
            feature_name: 'expenditure_percent_of_original_cost',
            display_name: 'Budget Utilization vs Original Sanction',
            feature_value: 53.4703,
            is_missing: false,
            unit: '%',
            contribution: -0.055481,
            contribution_display: '-5.55% pts',
            direction: 'DECREASES_RISK',
            rank: 1,
          },
          {
            feature_name: 'remaining_planned_months',
            display_name: 'Remaining Planned Months',
            feature_value: 3.0,
            is_missing: false,
            unit: 'months',
            contribution: -0.05172,
            contribution_display: '-5.17% pts',
            direction: 'DECREASES_RISK',
            rank: 2,
          },
        ],
      },
      schedule_delay_explanation: {
        model_name: 'delay_model',
        target_metric: 'schedule_delay_probability',
        base_value: 0.645245,
        predicted_value: 0.161514,
        total_contribution: -0.483731,
        displayed_contribution: -0.28,
        audit_reconciliation_gap: 0.0,
        audit_status: 'reconciled',
        top_drivers: [
          {
            feature_name: 'progress_gap_pct_points',
            display_name: 'Progress Baseline Gap',
            feature_value: 12.5,
            is_missing: false,
            unit: '% pts',
            contribution: -0.082,
            contribution_display: '-8.20% pts',
            direction: 'DECREASES_RISK',
            rank: 1,
          },
        ],
      },
      predicted_delay_explanation: {
        model_name: 'delay_regressor',
        target_metric: 'predicted_delay_months',
        base_value: 38.7132,
        predicted_value: -3.8314,
        total_contribution: -42.5446,
        displayed_contribution: -35.2,
        audit_reconciliation_gap: 0.0,
        audit_status: 'reconciled',
        top_drivers: [
          {
            feature_name: 'elapsed_months',
            display_name: 'Elapsed Construction Timeline',
            feature_value: 87.0,
            is_missing: false,
            unit: 'months',
            contribution: -33.91,
            contribution_display: '-33.91 mo',
            direction: 'REDUCES_DELAY',
            rank: 1,
          },
        ],
      },
    };

    it('renders project 400234 with raw delay in audit and Early Warning Summary', () => {
      render(
        <PredictionDisplay
          prediction={sample400234}
          isLoading={false}
          explainability={sampleExplain400234}
        />
      );

      // 1. Overall Risk Hero Banner checks
      expect(screen.getByTestId('overall-risk-hero')).toBeInTheDocument();
      expect(screen.getAllByText(/Third Railway Line between Patratu-Sonnagar/i).length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText(/400234/).length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText('Nominal Execution — All predictive indicators remain within normal operational tolerance (< 30%).')).toBeInTheDocument();

      // 2. Risk Command Center & Approved Technical Subtitles
      expect(screen.getByTestId('risk-command-center')).toBeInTheDocument();
      expect(screen.getByText('Schedule Delay Risk')).toBeInTheDocument();
      expect(screen.getByTestId('card2-subtitle')).toHaveTextContent('Revised Deadline Risk');
      expect(screen.getByText('Projected Schedule Variance')).toBeInTheDocument();
      expect(screen.getByTestId('card3-subtitle')).toHaveTextContent('Original Baseline Delay');
      expect(screen.getByText('40% Threshold')).toBeInTheDocument();
      expect(screen.getByText('50% Threshold')).toBeInTheDocument();
      expect(screen.getAllByText('30% Advisory').length).toBe(2);

      // Multi-Model Target Interpretation Banner (Purely Explanatory)
      expect(screen.getByTestId('multi-model-explanation')).toHaveTextContent(
        /Schedule-delay probability measures the binary risk of completing .* 60 days beyond the revised deadline, while predicted delay estimates the continuous number of months beyond the original completion baseline\./
      );

      // 3. Human-readable ahead of schedule presentation & raw delay audit
      expect(screen.getAllByText('Ahead of schedule by 3.83 months').length).toBeGreaterThanOrEqual(1);
      const rawAudit = screen.getByTestId('raw-delay-audit');
      expect(rawAudit).toHaveTextContent('-3.83 mo');

      // 4. Early Warning Summary (active explainability badge)
      expect(screen.getByTestId('early-warning-summary')).toBeInTheDocument();
      expect(screen.getByText('Early Warning Summary')).toBeInTheDocument();
      expect(screen.getByText(/Granular root-cause feature attributions and mathematically reconciled decision drivers are presented in the SHAP Explainability Panel/i)).toBeInTheDocument();

      // 5. ExplainabilityPanel checks
      expect(screen.getByTestId('explainability-panel')).toBeInTheDocument();
      expect(screen.getByText('Budget Utilization vs Original Sanction')).toBeInTheDocument();
      expect(screen.getByText('-5.55% pts')).toBeInTheDocument();
      expect(screen.getByTestId('audit-reconciliation-box')).toBeInTheDocument();
      expect(screen.getByText(/MATHEMATICAL ATTRIBUTION RECONCILIATION/i)).toBeInTheDocument();
    });

    it('renders Project 400104 with HIGH cost risk, LOW schedule classifier, and 153.04 months delay', () => {
      const sample400104: ProjectPredictionResponse = {
        project_id: '400104',
        project_name: 'Punpun Barrage Project',
        snapshot_month: '2026-03',
        overall_risk: 'HIGH',
        cost_overrun_probability: 0.5231,
        cost_overrun_risk: 'HIGH',
        schedule_delay_probability: 0.1451,
        schedule_delay_risk: 'LOW',
        predicted_delay_months: 153.04,
      };

      render(
        <PredictionDisplay
          prediction={sample400104}
          isLoading={false}
          explainability={null}
        />
      );

      // Overall Risk Hero
      expect(screen.getByTestId('overall-risk-hero')).toBeInTheDocument();
      expect(screen.getAllByText('Punpun Barrage Project').length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText('400104').length).toBeGreaterThanOrEqual(1);

      // Cost Overrun Card (HIGH)
      const costCard = screen.getByTestId('cost-risk-card');
      expect(costCard).toHaveTextContent('52.31');
      expect(costCard).toHaveTextContent('HIGH');

      // Schedule Delay Card (LOW classifier)
      const delayCard = screen.getByTestId('delay-risk-card');
      expect(delayCard).toHaveTextContent('Schedule Delay Risk');
      expect(delayCard).toHaveTextContent('Revised Deadline Risk');
      expect(delayCard).toHaveTextContent('14.51');
      expect(delayCard).toHaveTextContent('LOW');

      // Projected Schedule Variance Card (Regressor: 153.04 months)
      const varianceCard = screen.getByTestId('schedule-variance-card');
      expect(varianceCard).toHaveTextContent('Projected Schedule Variance');
      expect(varianceCard).toHaveTextContent('Original Baseline Delay');
      expect(varianceCard).toHaveTextContent('Predicted delay: 153.04 months');

      // Explanatory Banner present
      expect(screen.getByTestId('multi-model-explanation')).toBeInTheDocument();
    });

    it('renders Project 400161 with HIGH cost risk (72.01%) and 26.73 months delay', () => {
      const sample400161: ProjectPredictionResponse = {
        project_id: '400161',
        project_name: 'PP Project, Pata',
        snapshot_month: '2026-01',
        overall_risk: 'HIGH',
        cost_overrun_probability: 0.7201,
        cost_overrun_risk: 'HIGH',
        schedule_delay_probability: 0.1608,
        schedule_delay_risk: 'LOW',
        predicted_delay_months: 26.73,
      };

      render(
        <PredictionDisplay
          prediction={sample400161}
          isLoading={false}
          explainability={null}
        />
      );

      const costCard = screen.getByTestId('cost-risk-card');
      expect(costCard).toHaveTextContent('72.01');
      expect(costCard).toHaveTextContent('HIGH');

      const delayCard = screen.getByTestId('delay-risk-card');
      expect(delayCard).toHaveTextContent('16.08');
      expect(delayCard).toHaveTextContent('LOW');

      const varianceCard = screen.getByTestId('schedule-variance-card');
      expect(varianceCard).toHaveTextContent('Predicted delay: 26.73 months');
    });

    it('allows switching tabs in ExplainabilityPanel to view delay and timeline drivers', () => {
      render(
        <PredictionDisplay
          prediction={sample400234}
          isLoading={false}
          explainability={sampleExplain400234}
        />
      );

      // Switch to Timeline Delay Drivers tab
      const regTab = screen.getByTestId('tab-regression');
      fireEvent.click(regTab);

      expect(screen.getByText('Elapsed Construction Timeline')).toBeInTheDocument();
      expect(screen.getByText('-33.91 mo')).toBeInTheDocument();
      expect(screen.getByText('REDUCES DELAY')).toBeInTheDocument();

      // Switch to Schedule Delay tab
      const delayTab = screen.getByTestId('tab-delay');
      fireEvent.click(delayTab);

      expect(screen.getByText('Progress Baseline Gap')).toBeInTheDocument();
      expect(screen.getByText('-8.20% pts')).toBeInTheDocument();
    });

    it('renders explainability loading state gracefully without affecting prediction', () => {
      render(
        <PredictionDisplay
          prediction={sample400234}
          isLoading={false}
          explainability={null}
          isLoadingExplain={true}
        />
      );

      expect(screen.getByTestId('overall-risk-hero')).toBeInTheDocument();
      expect(screen.getByTestId('risk-command-center')).toBeInTheDocument();
      expect(screen.getByTestId('explainability-loading')).toBeInTheDocument();
      expect(screen.getByText(/Computing exact Shapley feature attributions/i)).toBeInTheDocument();
    });

    it('renders explainability error notice gracefully without affecting prediction', () => {
      render(
        <PredictionDisplay
          prediction={sample400234}
          isLoading={false}
          explainability={null}
          explainError="Explainability service timeout"
        />
      );

      expect(screen.getByTestId('overall-risk-hero')).toBeInTheDocument();
      expect(screen.getByTestId('risk-command-center')).toBeInTheDocument();
      expect(screen.getByTestId('explainability-error')).toBeInTheDocument();
      expect(screen.getByText(/Feature-level driver attribution is currently unavailable/i)).toBeInTheDocument();
    });

    it('renders loading state when primary prediction is loading', () => {
      render(<PredictionDisplay prediction={null} isLoading={true} />);
      expect(screen.getByTestId('prediction-loading')).toBeInTheDocument();
      expect(screen.getByText(/Executing Multi-Model ML Ensemble/i)).toBeInTheDocument();
    });

    it('cleans up previous explainability error state when new project loads successfully', () => {
      const { rerender } = render(
        <PredictionDisplay
          prediction={sample400234}
          isLoading={false}
          explainability={null}
          explainError="Explainability service timeout"
        />
      );
      expect(screen.getByTestId('explainability-error')).toBeInTheDocument();

      // Rerender with project 400161 prediction and valid explainability
      const sample400161: ProjectPredictionResponse = {
        project_id: '400161',
        project_name: 'PP Project, Pata',
        snapshot_month: '2026-01',
        overall_risk: 'HIGH',
        cost_overrun_probability: 0.7201,
        cost_overrun_risk: 'HIGH',
        schedule_delay_probability: 0.1608,
        schedule_delay_risk: 'LOW',
        predicted_delay_months: 26.73,
      };

      rerender(
        <PredictionDisplay
          prediction={sample400161}
          isLoading={false}
          explainability={sampleExplain400234}
          explainError={null}
        />
      );
      expect(screen.queryByTestId('explainability-error')).not.toBeInTheDocument();
      expect(screen.getByTestId('explainability-panel')).toBeInTheDocument();
      expect(screen.getAllByText('PP Project, Pata').length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText('400161').length).toBeGreaterThanOrEqual(1);
    });
  });
});
