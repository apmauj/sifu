/**
 * Configuración centralizada de URLs de API
 * Maneja automáticamente las rutas según el contexto (gateway vs directo)
 */

// Detectar si estamos en desarrollo
const isDevelopment = import.meta.env.DEV;

/**
 * Obtener la URL base para las llamadas API
 * @returns {string} URL base para las API calls
 */
export const getApiBaseUrl = () => {
  // Si estamos accediendo desde el gateway, usar la ruta del gateway
  if (typeof window !== 'undefined' && window.location.pathname.startsWith('/sifu')) {
    return '/sifu/api';
  }
  // Forzar en producción el uso de /sifu/api
  if (import.meta.env.PROD) {
    return '/sifu/api';
  }
  // En desarrollo, usar la configuración de entorno o ruta por defecto
  if (isDevelopment) {
    return import.meta.env.VITE_API_URL || '/api';
  }
  // En otros casos, usar /api
  return '/api';
};

/**
 * URL para conexión directa (fallback)
 * @returns {string} URL directa al backend
 */
export const getDirectApiUrl = () => {
  return import.meta.env.VITE_DIRECT_API_URL || 'http://localhost:8000/api';
};

/**
 * Configuración común para axios
 */
export const API_CONFIG = {
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
};

/**
 * Configuración para debug
 */
export const DEBUG_CONFIG = {
  logRequests: isDevelopment,
  logResponses: isDevelopment,
  logErrors: true,
};
