import {
  HealthResponse,
  ProjectLookupItem,
  ProjectPredictionResponse,
  ProjectExplainabilityResponse,
} from '../types/project';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/+$/, '');

class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = `HTTP Error ${response.status}: ${response.statusText}`;
    try {
      const errorData = await response.json();
      if (typeof errorData.detail === 'string') {
        errorMessage = errorData.detail;
      } else if (Array.isArray(errorData.detail)) {
        errorMessage = errorData.detail.map((d: { msg?: string }) => d.msg || JSON.stringify(d)).join('; ');
      }
    } catch {
      // JSON parse failed, use fallback text
    }
    throw new ApiError(errorMessage, response.status);
  }
  return response.json();
}

export async function checkHealth(): Promise<HealthResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return await handleResponse<HealthResponse>(response);
  } catch (err: unknown) {
    if (err instanceof ApiError) throw err;
    throw new ApiError('FastAPI backend is unreachable. Ensure the backend server is running on ' + API_BASE_URL, 0);
  }
}

export async function getProjects(search?: string, limit = 50, offset = 0): Promise<ProjectLookupItem[]> {
  try {
    const params = new URLSearchParams();
    if (search && search.trim()) {
      params.append('search', search.trim());
    }
    params.append('limit', String(limit));
    params.append('offset', String(offset));

    const response = await fetch(`${API_BASE_URL}/projects?${params.toString()}`);
    return await handleResponse<ProjectLookupItem[]>(response);
  } catch (err: unknown) {
    if (err instanceof ApiError) throw err;
    throw new ApiError('Failed to fetch projects from backend. Please check network connectivity.', 0);
  }
}

export async function getProjectPrediction(projectId: string): Promise<ProjectPredictionResponse> {
  try {
    const cleanId = encodeURIComponent(projectId.trim());
    const response = await fetch(`${API_BASE_URL}/projects/${cleanId}/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return await handleResponse<ProjectPredictionResponse>(response);
  } catch (err: unknown) {
    if (err instanceof ApiError) throw err;
    throw new ApiError('Failed to generate project prediction. Please check network connectivity.', 0);
  }
}

export async function getProjectExplainability(projectId: string, topK = 5): Promise<ProjectExplainabilityResponse> {
  try {
    const cleanId = encodeURIComponent(projectId.trim());
    const response = await fetch(`${API_BASE_URL}/projects/${cleanId}/explain?top_k=${topK}`);
    return await handleResponse<ProjectExplainabilityResponse>(response);
  } catch (err: unknown) {
    if (err instanceof ApiError) throw err;
    throw new ApiError('Failed to fetch project explainability drivers.', 0);
  }
}
