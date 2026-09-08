import React from 'react';

interface ErrorAlertProps {
  message: string;
  onDismiss?: () => void;
  onRetry?: () => void;
}

export const ErrorAlert: React.FC<ErrorAlertProps> = ({ message, onDismiss, onRetry }) => {
  return (
    <div className="error-alert" role="alert">
      <div className="error-content">
        <span className="error-icon">⚠️</span>
        <div className="error-text-group">
          <strong>Request Error</strong>
          <p>{message}</p>
        </div>
      </div>
      <div className="error-actions">
        {onRetry && (
          <button type="button" className="button button-small" onClick={onRetry}>
            Retry
          </button>
        )}
        {onDismiss && (
          <button type="button" className="button-close" onClick={onDismiss} title="Dismiss">
            ×
          </button>
        )}
      </div>
    </div>
  );
};
