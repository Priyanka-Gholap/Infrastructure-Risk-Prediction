import React from 'react';
import { ProjectLookupItem } from '../types/project';

interface ProjectListProps {
  projects: ProjectLookupItem[];
  selectedProjectId: string | null;
  onSelectProject: (project: ProjectLookupItem) => void;
  isLoadingPredict: boolean;
  hasSearched: boolean;
}

export const ProjectList: React.FC<ProjectListProps> = ({
  projects,
  selectedProjectId,
  onSelectProject,
  isLoadingPredict,
  hasSearched,
}) => {
  if (projects.length === 0) {
    if (!hasSearched) {
      return null;
    }
    return (
      <div className="card empty-state" data-testid="project-list-empty">
        <p>No matching infrastructure projects found in current dataset.</p>
        <span className="empty-subtext">Try searching by numeric Project ID (e.g. 400234) or partial sector name.</span>
      </div>
    );
  }

  return (
    <section className="project-list-section card" data-testid="project-list">
      <div className="list-header">
        <div>
          <h2 className="section-title">Matching Project Records</h2>
          <span className="subtext">Showing {projects.length} matching candidate projects out of 2,131 active snapshots</span>
        </div>
        <span className="results-count-pill">{projects.length} Found</span>
      </div>

      <div className="table-responsive">
        <table className="project-table">
          <thead>
            <tr>
              <th style={{ width: '130px' }}>Project ID</th>
              <th>Infrastructure Project Name</th>
              <th style={{ width: '140px', textAlign: 'center' }}>Snapshot Month</th>
              <th style={{ width: '180px', textAlign: 'center' }}>Inference Action</th>
            </tr>
          </thead>
          <tbody>
            {projects.map((item) => {
              const isSelected = selectedProjectId === item.project_id;
              return (
                <tr
                  key={item.project_id}
                  className={`project-row ${isSelected ? 'row-selected' : ''}`}
                >
                  <td className="project-id-cell">
                    <span className="id-tag monospace">{item.project_id}</span>
                  </td>
                  <td className="project-name-cell">
                    <span className="project-name-title">{item.project_name}</span>
                  </td>
                  <td className="snapshot-cell" style={{ textAlign: 'center' }}>
                    <span className="snapshot-tag">{item.snapshot_month}</span>
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    <button
                      type="button"
                      className={`button ${isSelected ? 'button-selected' : 'button-secondary'}`}
                      onClick={() => onSelectProject(item)}
                      disabled={isLoadingPredict}
                    >
                      {isSelected && isLoadingPredict
                        ? 'Evaluating ML...'
                        : isSelected
                        ? 'Active Project ✓'
                        : 'Select & Predict'}
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
};
