import { useState, useEffect, useCallback, useRef } from 'react';
import { Header } from './components/Header';
import { ProjectSearch } from './components/ProjectSearch';
import { ProjectList } from './components/ProjectList';
import { PredictionDisplay } from './components/PredictionDisplay';
import { ErrorAlert } from './components/ErrorAlert';
import { LoadingIndicator } from './components/LoadingIndicator';
import {
  checkHealth,
  getProjects,
  getProjectPrediction,
  getProjectExplainability,
} from './services/api';
import {
  ProjectLookupItem,
  ProjectPredictionResponse,
  ProjectExplainabilityResponse,
} from './types/project';

export function App() {
  const [backendConnected, setBackendConnected] = useState<boolean | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [projects, setProjects] = useState<ProjectLookupItem[]>([]);
  const [selectedProject, setSelectedProject] = useState<ProjectLookupItem | null>(null);
  const [prediction, setPrediction] = useState<ProjectPredictionResponse | null>(null);
  const [explainability, setExplainability] = useState<ProjectExplainabilityResponse | null>(null);

  const [isLoadingSearch, setIsLoadingSearch] = useState(false);
  const [isLoadingPredict, setIsLoadingPredict] = useState(false);
  const [isLoadingExplain, setIsLoadingExplain] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [explainError, setExplainError] = useState<string | null>(null);

  // Active project ID reference to prevent out-of-order race conditions on rapid switching
  const activeProjectIdRef = useRef<string | null>(null);

  // Probe backend on mount
  useEffect(() => {
    checkHealth()
      .then(() => setBackendConnected(true))
      .catch(() => setBackendConnected(false));
  }, []);

  const handleSearch = useCallback(async (query: string) => {
    setIsLoadingSearch(true);
    setErrorMessage(null);
    setHasSearched(true);
    try {
      const results = await getProjects(query, 30);
      setProjects(results);
      setBackendConnected(true);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Search failed. Please try again.';
      setErrorMessage(msg);
      setProjects([]);
      setBackendConnected(false);
    } finally {
      setIsLoadingSearch(false);
    }
  }, []);

  const handleSelectProject = useCallback(async (project: ProjectLookupItem) => {
    // Prevent redundant fetch if project is already active with prediction loaded
    if (selectedProject?.project_id === project.project_id && prediction !== null && !isLoadingPredict) {
      return;
    }
    // Prevent duplicate in-flight requests on the same project
    if (selectedProject?.project_id === project.project_id && (isLoadingPredict || isLoadingExplain)) {
      return;
    }

    const currentProjectId = project.project_id;
    activeProjectIdRef.current = currentProjectId;

    setSelectedProject(project);
    setPrediction(null); // Immediately reset prediction so old data never lingers
    setIsLoadingPredict(true);
    setErrorMessage(null);

    // Reset explainability state cleanly for the new project
    setExplainability(null);
    setExplainError(null);
    setIsLoadingExplain(true);

    // 1. Primary prediction fetch (fast)
    try {
      const result = await getProjectPrediction(currentProjectId);
      if (activeProjectIdRef.current === currentProjectId) {
        setPrediction(result);
        setBackendConnected(true);
      }
    } catch (err: unknown) {
      if (activeProjectIdRef.current === currentProjectId) {
        const msg = err instanceof Error ? err.message : 'Prediction request failed.';
        setErrorMessage(msg);
        setPrediction(null);
      }
    } finally {
      if (activeProjectIdRef.current === currentProjectId) {
        setIsLoadingPredict(false);
      }
    }

    // 2. Separate explainability fetch (non-blocking, failure-isolated)
    try {
      const explainRes = await getProjectExplainability(currentProjectId);
      if (activeProjectIdRef.current === currentProjectId) {
        setExplainability(explainRes);
      }
    } catch (err: unknown) {
      if (activeProjectIdRef.current === currentProjectId) {
        const msg = err instanceof Error ? err.message : 'Explainability fetch failed.';
        setExplainError(msg);
        setExplainability(null);
      }
    } finally {
      if (activeProjectIdRef.current === currentProjectId) {
        setIsLoadingExplain(false);
      }
    }
  }, [selectedProject, prediction, isLoadingPredict, isLoadingExplain]);

  const handleSelectKnownId = useCallback(async (id: string) => {
    // If this project is already selected and prediction is loaded, do not re-fetch
    if (selectedProject?.project_id === id && prediction !== null && !isLoadingPredict) {
      return;
    }

    // Immediately clear stale state so previous project does not linger during search
    activeProjectIdRef.current = id;
    setSelectedProject(null);
    setPrediction(null);
    setExplainability(null);
    setExplainError(null);

    setIsLoadingSearch(true);
    setErrorMessage(null);
    setHasSearched(true);
    try {
      const results = await getProjects(id, 10);
      if (activeProjectIdRef.current === id) {
        setProjects(results);
        const match = results.find((p) => p.project_id === id) || results[0];
        if (match) {
          handleSelectProject(match);
        }
      }
    } catch (err: unknown) {
      if (activeProjectIdRef.current === id) {
        const msg = err instanceof Error ? err.message : 'Search failed.';
        setErrorMessage(msg);
      }
    } finally {
      if (activeProjectIdRef.current === id) {
        setIsLoadingSearch(false);
      }
    }
  }, [handleSelectProject, selectedProject, prediction, isLoadingPredict]);

  return (
    <div className="app-layout">
      <Header backendConnected={backendConnected} />

      <main className="main-content">
        {errorMessage && (
          <ErrorAlert
            message={errorMessage}
            onDismiss={() => setErrorMessage(null)}
            onRetry={() => {
              if (selectedProject) {
                handleSelectProject(selectedProject);
              } else {
                handleSearch('');
              }
            }}
          />
        )}

        <ProjectSearch
          onSearch={handleSearch}
          isLoading={isLoadingSearch}
          onSelectKnownId={handleSelectKnownId}
        />

        {isLoadingSearch && (
          <div className="card loading-card">
            <LoadingIndicator
              message="Searching current monitored infrastructure projects..."
              subtext="Querying FastAPI /projects endpoint across 2,131 snapshots"
            />
          </div>
        )}

        {!isLoadingSearch && (
          <ProjectList
            projects={projects}
            selectedProjectId={selectedProject?.project_id ?? null}
            onSelectProject={handleSelectProject}
            isLoadingPredict={isLoadingPredict}
            hasSearched={hasSearched}
          />
        )}

        <PredictionDisplay
          prediction={prediction}
          isLoading={isLoadingPredict}
          explainability={explainability}
          isLoadingExplain={isLoadingExplain}
          explainError={explainError}
        />
      </main>

      <footer className="app-footer">
        <div className="footer-content">
          <p className="footer-title">
            SIH26103 National Infrastructure Risk Monitoring Portal • Command Center Edition
          </p>
          <p className="footer-subtext">
            Powered by Locked Multi-Model Random Forest Ensemble • SHAP TreeExplainer Attribution • MoSPI / IPMD Production Pipeline
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
