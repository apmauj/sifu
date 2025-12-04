import React, { useState, useEffect } from 'react';
import { TOAST_DURATION } from '../../constants';

const ToastNotification = ({ message, type = 'success', duration = TOAST_DURATION, onClose }) => {
  const [isVisible, setIsVisible] = useState(true);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    // Iniciar animación de entrada
    const enterTimer = setTimeout(() => {
      setIsAnimating(true);
    }, 100);

    // Programar cierre automático
    const closeTimer = setTimeout(() => {
      handleClose();
    }, duration);

    return () => {
      clearTimeout(enterTimer);
      clearTimeout(closeTimer);
    };
  }, [duration]);

  const handleClose = () => {
    setIsAnimating(false);
    setTimeout(() => {
      setIsVisible(false);
      if (onClose) onClose();
    }, 300); // Tiempo para animación de salida
  };

  if (!isVisible) return null;

  const getTypeStyles = () => {
    switch (type) {
      case 'success':
        return {
          bg: 'bg-green-50 border-green-200',
          text: 'text-green-800',
          icon: '✅',
          iconBg: 'bg-green-100',
          iconText: 'text-green-600'
        };
      case 'error':
        return {
          bg: 'bg-red-50 border-red-200',
          text: 'text-red-800',
          icon: '❌',
          iconBg: 'bg-red-100',
          iconText: 'text-red-600'
        };
      case 'warning':
        return {
          bg: 'bg-yellow-50 border-yellow-200',
          text: 'text-yellow-800',
          icon: '⚠️',
          iconBg: 'bg-yellow-100',
          iconText: 'text-yellow-600'
        };
      case 'info':
        return {
          bg: 'bg-blue-50 border-blue-200',
          text: 'text-blue-800',
          icon: 'ℹ️',
          iconBg: 'bg-blue-100',
          iconText: 'text-blue-600'
        };
      default:
        return {
          bg: 'bg-neutral-50 border-neutral-200',
          text: 'text-neutral-800',
          icon: '📢',
          iconBg: 'bg-neutral-100',
          iconText: 'text-neutral-600'
        };
    }
  };

  const styles = getTypeStyles();

  const progressBarColor = type === 'success' ? 'bg-green-400' : 
    type === 'error' ? 'bg-red-400' :
    type === 'warning' ? 'bg-yellow-400' :
    type === 'info' ? 'bg-blue-400' : 'bg-neutral-400';

  return (
    <div
      className={`
        max-w-sm w-full transform transition-all duration-300 ease-in-out
        ${isAnimating ? 'translate-x-0 translate-y-0 opacity-100' : '-translate-x-full translate-y-4 opacity-0'}
      `.trim()}
    >
      <div className={`${styles.bg} border rounded-lg shadow-lg p-4 backdrop-blur-sm`}>
        <div className="flex items-start">
          <div className={`flex-shrink-0 w-8 h-8 rounded-full ${styles.iconBg} flex items-center justify-center mr-3`}>
            <span className="text-sm">{styles.icon}</span>
          </div>
          
          <div className="flex-1 min-w-0">
            <p className={`text-sm font-medium ${styles.text}`}>
              {message}
            </p>
          </div>
          
          <button
            onClick={handleClose}
            className={`flex-shrink-0 ml-2 p-1 rounded-full hover:bg-white hover:bg-opacity-20 transition-colors duration-200 ${styles.iconText}`}
          >
            <span className="text-xs">✕</span>
          </button>
        </div>
        
        {/* Barra de progreso */}
        <div className="mt-2 w-full bg-white bg-opacity-30 rounded-full h-1">
          <div 
            className={`h-1 rounded-full transition-all ease-linear toast-progress-bar ${progressBarColor}`}
            style={{
              width: '100%',
              animation: `toast-shrink ${duration}ms linear`
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default ToastNotification; 