import React, { useState } from 'react';

interface ProjectSearchProps {
  onSearch: (query: string) => void;
  isLoading: boolean;
  onSelectKnownId: (id: string) => void;
}

export const ProjectSearch: React.FC<ProjectSearchProps> = ({
  onSearch,
  isLoading,
  onSelectKnownId,
}) => {
  const [searchInput, setSearchInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(searchInput);
  };

  const handleClear = () => {
    setSearchInput('');
    onSearch('');
  };

  // Safe reference chips: Project IDs only, no hardcoded prediction stats (Correction 4)
  const referenceProjectIds = ['400234', '400161', '400104'];

  return (
    <section className="search-section card" data-testid="project-search">
      <div className="section-header-row">
        <div>
          <h2 className="section-title">Project Discovery & Lookup</h2>
          <p className="section-description">
            Search by Project ID or Project Name across all 2,131 monitored infrastructure snapshots.
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="search-form">
        <div className="search-input-wrapper">
          <span className="search-icon" aria-hidden="true">🔍</span>
          <input
            type="text"
            className="search-input"
            placeholder="Enter Project ID (e.g. 400234) or Keyword (e.g. Railway, Metro, Pipeline)..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            disabled={isLoading}
          />
          {searchInput && (
            <button
              type="button"
              className="clear-button"
              onClick={handleClear}
              disabled={isLoading}
              title="Clear search"
            >
              ×
            </button>
          )}
        </div>
        <button type="submit" className="button button-primary" disabled={isLoading}>
          {isLoading ? 'Searching...' : 'Search Projects'}
        </button>
      </form>

      <div className="quick-select">
        <span className="quick-select-label">Quick-Demo Reference Assets:</span>
        <div className="chip-group">
          {referenceProjectIds.map((id) => (
            <button
              key={id}
              type="button"
              className="chip chip-reference"
              onClick={() => {
                setSearchInput(id);
                onSelectKnownId(id);
              }}
              disabled={isLoading}
            >
              Project {id}
            </button>
          ))}
        </div>
      </div>
    </section>
  );
};
