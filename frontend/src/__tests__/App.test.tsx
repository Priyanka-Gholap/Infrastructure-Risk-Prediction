import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { App } from '../App';
import * as api from '../services/api';
import {
  ProjectLookupItem,
  ProjectPredictionResponse,
  ProjectExplainabilityResponse,
} from '../types/project';

vi.mock('../services/api');

describe('App Component Integration & Stale State Hygiene Tests', () => {
  const mock400234Lookup: ProjectLookupItem = {
    project_id: '400234',
    project_name: 'Third Railway Line between Patratu-Sonnagar [291 kms]',
    snapshot_month: '2025-12',
  };

  const mock400161Lookup: ProjectLookupItem = {
    project_id: '400161',
    project_name: 'PP Project, Pata',
    snapshot_month: '2026-01',
  };

  const mock400234Prediction: ProjectPredictionResponse = {
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

  const mock400161Prediction: ProjectPredictionResponse = {
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

  const mock400234Explain: ProjectExplainabilityResponse = {
    project_id: '400234',
    project_name: 'Third Railway Line between Patratu-Sonnagar [291 kms]',
    snapshot_month: '2025-12',
    top_k: 5,
    cost_overrun_explanation: {
      model_name: 'cost_overrun_model',
      target_metric: 'cost_overrun_probability',
      base_value: 0.4964,
      predicted_value: 0.2388,
      total_contribution: -0.2576,
      displayed_contribution: -0.22,
      audit_reconciliation_gap: 0.0,
      audit_status: 'reconciled',
      top_drivers: [],
    },
    schedule_delay_explanation: {
      model_name: 'delay_model',
      target_metric: 'schedule_delay_probability',
      base_value: 0.6452,
      predicted_value: 0.1615,
      total_contribution: -0.4837,
      displayed_contribution: -0.28,
      audit_reconciliation_gap: 0.0,
      audit_status: 'reconciled',
      top_drivers: [],
    },
    predicted_delay_explanation: {
      model_name: 'delay_regressor',
      target_metric: 'predicted_delay_months',
      base_value: 38.71,
      predicted_value: -3.83,
      total_contribution: -42.54,
      displayed_contribution: -35.2,
      audit_reconciliation_gap: 0.0,
      audit_status: 'reconciled',
      top_drivers: [],
    },
  };

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(api.checkHealth).mockResolvedValue({
      status: 'ok',
      models_loaded: true,
    });
    vi.mocked(api.getProjects).mockImplementation(async (search) => {
      if (search === '400234') return [mock400234Lookup];
      if (search === '400161') return [mock400161Lookup];
      return [mock400234Lookup, mock400161Lookup];
    });
    vi.mocked(api.getProjectPrediction).mockImplementation(async (id) => {
      if (id === '400234') return mock400234Prediction;
      if (id === '400161') return mock400161Prediction;
      throw new Error('Project not found');
    });
    vi.mocked(api.getProjectExplainability).mockResolvedValue(mock400234Explain);
  });

  it('renders application header and connects to backend health check', async () => {
    render(<App />);
    expect(screen.getByText(/SIH26103 • National Infrastructure Project Monitoring Portal/i)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText('FastAPI Backend Live')).toBeInTheDocument();
    });
  });

  it('clears stale prediction immediately when quick-selecting another project chip', async () => {
    render(<App />);

    // Select Project 400234
    const chip400234 = screen.getByRole('button', { name: /Project 400234/i });
    fireEvent.click(chip400234);

    // Wait for 400234 prediction to render
    await waitFor(() => {
      expect(screen.getByText(/Third Railway Line between Patratu-Sonnagar/i)).toBeInTheDocument();
    });
    expect(screen.getAllByText('Ahead of schedule by 3.83 months').length).toBeGreaterThanOrEqual(1);

    // Now click Project 400161 chip
    const chip400161 = screen.getByRole('button', { name: /Project 400161/i });
    fireEvent.click(chip400161);

    // Old prediction should be immediately cleared (no lingering 400234 cards)
    expect(screen.queryAllByText('Ahead of schedule by 3.83 months').length).toBe(0);

    // Wait for 400161 prediction to load
    await waitFor(() => {
      expect(screen.getByText('PP Project, Pata')).toBeInTheDocument();
    });
    expect(screen.getAllByText('Predicted delay: 26.73 months').length).toBeGreaterThanOrEqual(1);
  });
});
