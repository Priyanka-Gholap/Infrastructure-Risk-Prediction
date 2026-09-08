import React from 'react';

interface HeaderProps {
  backendConnected: boolean | null;
}

export const Header: React.FC<HeaderProps> = ({ backendConnected }) => {
  return (
    <header className="app-header">
      <div className="header-content">
        <div className="title-group">
          <div className="badge-pill">SIH26103 • National Infrastructure Project Monitoring Portal</div>
          <h1>AI-Powered Predictive Analytics & Early Warning System</h1>
          <p className="subtitle">
            MoSPI / IPMD Infrastructure Monitoring Pipeline • Real-time Risk Inference across 2,131 Active Projects
          </p>
        </div>

        <div className="header-controls">
          <div className="engine-status-pill">
            <span className="engine-dot" />
            <span className="engine-text">ML Ensemble Active (3 Models)</span>
          </div>

          <div className="status-indicator-box">
            <span
              className={`status-dot ${
                backendConnected === true
                  ? 'status-online'
                  : backendConnected === false
                  ? 'status-offline'
                  : 'status-checking'
              }`}
            />
            <span className="status-text">
              {backendConnected === true
                ? 'FastAPI Backend Live'
                : backendConnected === false
                ? 'Backend Disconnected'
                : 'Connecting to Backend...'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
