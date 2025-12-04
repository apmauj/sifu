import React from 'react';
import { I18nProvider } from '../shared/contexts/I18nContext.jsx';
import { ToastProvider } from '../shared/contexts/ToastContext.jsx';
import { ThemeProvider } from '../shared/contexts/ThemeContext.jsx';
import ErrorBoundary from './ErrorBoundary.jsx';

/**
 * AppProviders - Wraps the application with all necessary context providers
 * 
 * Provider order (outer to inner):
 * 1. ThemeProvider - Theme management (dark/light mode, color themes)
 * 2. I18nProvider - Internationalization (translations)
 * 3. ToastProvider - Toast notifications
 * 4. ErrorBoundary - Error handling
 */
function AppProviders({ children }) {
  return (
    <ThemeProvider>
      <I18nProvider>
        <ToastProvider>
          <ErrorBoundary>
            {children}
          </ErrorBoundary>
        </ToastProvider>
      </I18nProvider>
    </ThemeProvider>
  );
}

export default AppProviders;
