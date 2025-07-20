import React, { createContext, useContext, useState, useCallback } from 'react';
import ToastNotification from '../components/ToastNotification';
import { TOAST_DURATION } from '../constants';

const ToastContext = createContext();

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast debe ser usado dentro de un ToastProvider');
  }
  return context;
};

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = 'success', duration = TOAST_DURATION) => {
    const id = Date.now() + Math.random();
    const newToast = {
      id,
      message,
      type,
      duration
    };

    setToasts(prev => [...prev, newToast]);

    // Auto-remove toast after duration + animation time
    setTimeout(() => {
      setToasts(prev => prev.filter(toast => toast.id !== id));
    }, duration + 500);
  }, []);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);

  const showSuccess = useCallback((message, duration) => {
    addToast(message, 'success', duration);
  }, [addToast]);

  const showError = useCallback((message, duration) => {
    addToast(message, 'error', duration);
  }, [addToast]);

  const showWarning = useCallback((message, duration) => {
    addToast(message, 'warning', duration);
  }, [addToast]);

  const showInfo = useCallback((message, duration) => {
    addToast(message, 'info', duration);
  }, [addToast]);

  const value = {
    addToast,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    removeToast
  };

  return (
    <ToastContext.Provider value={value}>
      {children}
      
      {/* Renderizar todas las notificaciones */}
      <div className="fixed bottom-4 left-4 z-50 space-y-3 space-y-reverse pointer-events-none">
        {toasts.slice().reverse().map((toast) => (
          <div key={toast.id} className="pointer-events-auto">
            <ToastNotification
              message={toast.message}
              type={toast.type}
              duration={toast.duration}
              onClose={() => removeToast(toast.id)}
            />
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}; 