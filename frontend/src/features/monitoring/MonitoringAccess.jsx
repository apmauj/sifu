import { useState } from 'react';
import { useI18n } from '../../shared/contexts/I18nContext';
import './MonitoringAccess.css';

/**
 * Monitoring Access Component
 * Provides TOTP-based authentication for accessing monitoring dashboard
 */
const MonitoringAccess = ({ isOpen, onClose, onAccessGranted }) => {
  const { t } = useI18n();
  const [code, setCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [attemptsLeft, setAttemptsLeft] = useState(5);

  const handleInputChange = (e) => {
    const value = e.target.value.replace(/\D/g, ''); // Only digits
    if (value.length <= 6) {
      setCode(value);
      setError(''); // Clear error on input
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (code.length !== 6) {
      setError(t('monitoring.errors.invalidCodeFormat', 'Code must be 6 digits'));
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const baseUrl = import.meta.env.VITE_PUBLIC_API_URL || '';
      // baseUrl already includes /api suffix from build process
      const response = await fetch(`${baseUrl}/monitoring/verify?code=${encodeURIComponent(code)}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        
        // Store session token (matching App.jsx expectations)
        sessionStorage.setItem('monitoring_session_token', data.session_token);
        sessionStorage.setItem('monitoring_session_expires', 
          String(Date.now() + (data.expires_in * 1000))
        );
        
        // Call success callback
        if (onAccessGranted) {
          onAccessGranted(data.session_token);
        }
        
        // Clear form
        setCode('');
      } else if (response.status === 429) {
        // Rate limit exceeded
        setError(t('monitoring.errors.rateLimitExceeded', 
          'Too many attempts. Please wait a minute.'));
        setAttemptsLeft(0);
      } else if (response.status === 401) {
        // Invalid code
        setError(t('monitoring.errors.invalidCode', 
          'Invalid or expired code. Please try again.'));
        setAttemptsLeft(prev => Math.max(0, prev - 1));
        setCode(''); // Clear invalid code
      } else {
        // Other error
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        setError(errorData.detail || t('monitoring.errors.verificationFailed', 
          'Verification failed. Please try again.'));
      }
    } catch (err) {
      console.error('Error verifying TOTP code:', err);
      setError(t('monitoring.errors.networkError', 
        'Network error. Please check your connection.'));
    } finally {
      setIsLoading(false);
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pastedText = e.clipboardData.getData('text').replace(/\D/g, '');
    if (pastedText.length <= 6) {
      setCode(pastedText);
    }
  };

  // Don't render if not open
  if (!isOpen) {
    return null;
  }

  return (
    <div className="monitoring-access-overlay" onClick={onClose}>
      <div className="monitoring-access-modal" onClick={(e) => e.stopPropagation()}>
        <button 
          className="monitoring-access-close" 
          onClick={onClose}
          aria-label="Close"
        >
          ×
        </button>
        
        <div className="monitoring-access-header">
          <h2>{t('monitoring.title', 'Monitoring Access')}</h2>
          <p className="monitoring-access-subtitle">
            {t('monitoring.subtitle', 'Enter the 6-digit code from your authenticator app')}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="monitoring-access-form">
          <div className="totp-input-container">
            <input
              type="text"
              inputMode="numeric"
              pattern="\d{6}"
              placeholder="000000"
              value={code}
              onChange={handleInputChange}
              onPaste={handlePaste}
              maxLength={6}
              autoFocus
              disabled={isLoading || attemptsLeft === 0}
              className={`totp-input ${error ? 'totp-input-error' : ''}`}
              aria-label="TOTP Code"
            />
            <div className="totp-input-hint">
              {code.length}/6 {t('monitoring.digits', 'dígitos')}
            </div>
          </div>

          {error && (
            <div className="monitoring-access-error" role="alert">
              <span className="error-icon">⚠️</span>
              <span className="error-text">{error}</span>
            </div>
          )}

          {attemptsLeft < 5 && attemptsLeft > 0 && (
            <div className="monitoring-access-warning">
              {t('monitoring.attemptsLeft', { count: attemptsLeft })}
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading || code.length !== 6 || attemptsLeft === 0}
            className="monitoring-access-button"
          >
            {isLoading ? (
              <>
                <span className="spinner"></span>
                {t('monitoring.verifying', 'Verifying...')}
              </>
            ) : (
              t('monitoring.verify', 'Verify Code')
            )}
          </button>
        </form>

        <div className="monitoring-access-footer">
          <p className="help-text">
            <strong>{t('monitoring.help.title', 'Need help?')}</strong>
          </p>
          <ul className="help-list">
            <li>{t('monitoring.help.step1', 'Open your authenticator app (Google Authenticator, Authy, etc.)')}</li>
            <li>{t('monitoring.help.step2', 'Find "SIFU Monitoring" account')}</li>
            <li>{t('monitoring.help.step3', 'Enter the 6-digit code (refreshes every 30 seconds)')}</li>
          </ul>
          
          {attemptsLeft === 0 && (
            <div className="lockout-message">
              <p>{t('monitoring.locked', 'Too many failed attempts. Please wait 60 seconds and refresh the page.')}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MonitoringAccess;

