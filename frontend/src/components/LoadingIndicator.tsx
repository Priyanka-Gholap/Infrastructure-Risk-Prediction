import React from 'react';

interface LoadingIndicatorProps {
  message?: string;
  subtext?: string;
}

export const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({
  message = 'Loading...',
  subtext,
}) => {
  return (
    <div className="loading-container">
      <div className="spinner" />
      <p className="loading-text">{message}</p>
      {subtext && <span className="subtext">{subtext}</span>}
    </div>
  );
};
