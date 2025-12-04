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
  // 0) Override manual para debugging: ?api=https://host.tld/api
  try {
    if (typeof window !== 'undefined') {
      const p = new URLSearchParams(window.location.search).get('api')
      if (p) {
        return decodeURIComponent(p)
      }
    }
  } catch (_) { /* ignore */ }
  // 1) Si se define una URL pública para producción, usarla (ideal para GitHub Pages)
  if (import.meta.env.VITE_PUBLIC_API_URL) {
    return import.meta.env.VITE_PUBLIC_API_URL;
  }
  // 2) Si estamos accediendo desde /sifu (p.ej. detrás de Nginx o GitHub Pages con backend propio), usar /sifu/api
  if (typeof window !== 'undefined' && window.location.pathname.startsWith('/sifu')) {
    return '/sifu/api';
  }
  // 3) En producción sin VITE_PUBLIC_API_URL, dejar /sifu/api como valor por defecto
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
