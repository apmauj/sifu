import React from 'react';

/**
 * Error Boundary Component
 * Catches JavaScript errors anywhere in the child component tree,
 * logs those errors, and displays a fallback UI.
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error boundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-neutral-50 dark:bg-neutral-900 flex items-center justify-center">
          <div className="max-w-md mx-auto text-center">
            <div className="bg-error-50 dark:bg-error-950/30 
                            border border-error-200 dark:border-error-800 
                            rounded-lg p-6">
              <h2 className="text-lg font-medium text-error-800 dark:text-error-200 mb-2">
                ⚠️ Error en la aplicación
              </h2>
              <p className="text-sm text-error-600 dark:text-error-400 mb-4">
                Ha ocurrido un error inesperado. Por favor, recarga la página.
              </p>
              <button
                onClick={() => window.location.reload()}
                className="bg-error-600 hover:bg-error-700 active:bg-error-800 
                           dark:bg-error-600 dark:hover:bg-error-700
                           text-white px-4 py-2 rounded-lg 
                           transition-colors duration-200"
              >
                Recargar página
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
