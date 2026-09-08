import React from 'react';

interface ProjectMetadataPanelProps {
  projectId: string;
  projectName: string;
  snapshotMonth: string;
}

export const ProjectMetadataPanel: React.FC<ProjectMetadataPanelProps> = ({
  projectId,
  projectName,
  snapshotMonth,
}) => {
  return (
    <div className="card project-metadata-card" data-testid="project-metadata-panel">
      <div className="card-header-with-badge">
        <div>
          <h3 className="card-title">Project Snapshot Metadata</h3>
          <span className="card-subtitle">Attributes returned by the project inference record</span>
        </div>
        <span className="source-pill">Project Record</span>
      </div>

      <div className="metadata-grid">
        <div className="metadata-item">
          <span className="metadata-key">PROJECT IDENTIFIER</span>
          <span className="metadata-val monospace">{projectId}</span>
        </div>
        <div className="metadata-item">
          <span className="metadata-key">REPORTING SNAPSHOT MONTH</span>
          <span className="metadata-val">{snapshotMonth}</span>
        </div>
        <div className="metadata-item metadata-full-row">
          <span className="metadata-key">OFFICIAL PROJECT DESIGNATION</span>
          <span className="metadata-val project-name-text">{projectName}</span>
        </div>
      </div>
    </div>
  );
};
