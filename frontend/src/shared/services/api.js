import axios from 'axios';
import { getApiBaseUrl, getDirectApiUrl, API_CONFIG } from '../utils/apiConfig.js';

// Detectar si estamos en desarrollo
const isDevelopment = import.meta.env.DEV;

// Configurar las instancias de axios
const api = axios.create({
  baseURL: getApiBaseUrl(),
  ...API_CONFIG,
});

// Instancia alternativa para conexión directa (fallback)
const directApi = axios.create({
  baseURL: getDirectApiUrl(),
  ...API_CONFIG,
});

// Función helper para hacer peticiones con fallback
export const makeRequest = async (requestFn) => {
  try {
    // Intentar primero con el proxy
    const response = await requestFn(api);
    return response.data;
  } catch (error) {
    console.warn('Proxy failed, trying direct connection:', error.message);
    
    if (isDevelopment) {
      try {
        // Si falla el proxy, intentar conexión directa
        const response = await requestFn(directApi);
        return response.data;
      } catch (directError) {
        console.error('Direct connection also failed:', directError);
        throw directError;
      }
    }
    throw error;
  }
};

// Interceptor para manejo de errores globales
const setupInterceptors = (apiInstance) => {
  apiInstance.interceptors.response.use(
    (response) => response,
    (error) => {
      console.error('API Error:', error);
      
      if (error.response?.status === 500) {
        console.error('Error interno del servidor');
      } else if (error.response?.status === 404) {
        console.error('Recurso no encontrado');
      } else if (error.code === 'ECONNABORTED') {
        console.error('Timeout de la petición');
      } else if (error.code === 'ERR_NETWORK') {
        console.error('Error de red - no se puede conectar al servidor');
      }
      
      return Promise.reject(error);
    }
  );
};

// Configurar interceptores para ambas instancias
setupInterceptors(api);
setupInterceptors(directApi);

// Servicios de la API
let infoInFlightPromise = null;
const uiService = {
  // Obtener último valor de UI
  getLatest: async () => {
    return makeRequest((apiInstance) => apiInstance.get('/ui/latest'));
  },

  // Obtener valor de UI por fecha específica
  getByDate: async (fecha) => {
    return makeRequest((apiInstance) => apiInstance.get(`/ui/${fecha}`));
  },

  // Obtener valores de UI por rango de fechas
  getByRange: async (fechaInicio, fechaFin) => {
    return makeRequest((apiInstance) => apiInstance.get(`/ui/range/${fechaInicio}/${fechaFin}`));
  },

  // Obtener información general de los datos
  getInfo: async () => {
    if (infoInFlightPromise) {
      return infoInFlightPromise;
    }
    infoInFlightPromise = makeRequest((apiInstance) => apiInstance.get('/info'))
      .finally(() => {
        infoInFlightPromise = null;
      });
    return infoInFlightPromise;
  },

  // Actualizar datos desde el INE
  refresh: async () => {
    return makeRequest((apiInstance) => apiInstance.post('/refresh'));
  },

  // Verificar estado del servicio
  healthCheck: async () => {
    return makeRequest((apiInstance) => apiInstance.get('/health'));
  },

  // Función de test para verificar conectividad
  testConnection: async () => {
    try {
      console.log('Testing proxy connection...');
      const proxyResult = await api.get('/health');
      console.log('Proxy connection successful:', proxyResult.status);
      return { proxy: true, direct: false };
    } catch (proxyError) {
      console.log('Proxy failed, testing direct connection...');
      try {
        const directResult = await directApi.get('/health');
        console.log('Direct connection successful:', directResult.status);
        return { proxy: false, direct: true };
      } catch (directError) {
        console.error('Both connections failed');
        return { proxy: false, direct: false };
      }
    }
  },
};

export default uiService; 