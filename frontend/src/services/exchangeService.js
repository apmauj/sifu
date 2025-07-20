import axios from 'axios';
import { getApiBaseUrl, getDirectApiUrl, API_CONFIG, DEBUG_CONFIG } from '../utils/apiConfig.js';

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
const makeRequest = async (requestFn) => {
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
      console.error('Exchange API Error:', error);
      
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

// Servicios de Exchange Rates API
const exchangeService = {
  // Obtener cotizaciones actuales del BCU (tiempo real)
  getCurrentRates: async () => {
    return makeRequest((apiInstance) => apiInstance.get('/exchange-rate/current'));
  },

  // Obtener últimas cotizaciones (todas las monedas o una específica)
  getLatest: async (currency = null) => {
    const params = currency ? { currencies: currency } : {};
    return makeRequest((apiInstance) => 
      apiInstance.get('/exchange-rate/latest', { params })
    );
  },

  // Obtener información general de cotizaciones
  getInfo: async () => {
    return makeRequest((apiInstance) => apiInstance.get('/exchange-rate/info'));
  },

  // Obtener historial por moneda específica
  getCurrencyHistory: async (currency, limit = 30) => {
    return makeRequest((apiInstance) => 
      apiInstance.get(`/exchange-rate/currency/${currency}`, { 
        params: { limit } 
      })
    );
  },

  // Obtener cotizaciones por fecha específica
  getByDate: async (date, currency = null) => {
    const params = currency ? { currency } : {};
    return makeRequest((apiInstance) => 
      apiInstance.get(`/exchange-rate/${date}`, { params })
    );
  },

  // Obtener cotización específica (fecha + moneda)
  getSpecificRate: async (date, currency) => {
    return makeRequest((apiInstance) => 
      apiInstance.get(`/exchange-rate/${date}/${currency}`)
    );
  },

  // Obtener cotizaciones por rango de fechas
  getByDateRange: async (startDate, endDate, currency = null) => {
    const params = currency ? { currency } : {};
    return makeRequest((apiInstance) => 
      apiInstance.get(`/exchange-rate/range/${startDate}/${endDate}`, { params })
    );
  },

  // Actualizar datos desde el BCU
  refresh: async (useSampleData = false) => {
    const params = useSampleData ? { use_sample_data: true } : {};
    return makeRequest((apiInstance) => 
      apiInstance.post('/exchange-rate/refresh', {}, { params })
    );
  },

  // Función de test para verificar conectividad específica de exchange rates
  testConnection: async () => {
    try {
      console.log('Testing exchange rates proxy connection...');
      const proxyResult = await api.get('/exchange-rate/latest');
      console.log('Exchange rates proxy connection successful:', proxyResult.status);
      return { proxy: true, direct: false };
    } catch (proxyError) {
      console.log('Exchange rates proxy failed, testing direct connection...');
      try {
        const directResult = await directApi.get('/exchange-rate/latest');
        console.log('Exchange rates direct connection successful:', directResult.status);
        return { proxy: false, direct: true };
      } catch (directError) {
        console.error('Both exchange rates connections failed');
        return { proxy: false, direct: false };
      }
    }
  },
};

// Constantes para monedas soportadas
export const SUPPORTED_CURRENCIES = [
  { code: 'USD', flag: '🇺🇸' },
  { code: 'EUR', flag: '🇪🇺' },
  { code: 'ARS', flag: '🇦🇷' },
  { code: 'BRL', flag: '🇧🇷' },
];

// Helper para obtener información de una moneda
export const getCurrencyInfo = (currencyCode) => {
  return SUPPORTED_CURRENCIES.find(currency => currency.code === currencyCode);
};

// Helper para formatear tasas de cambio
export const formatExchangeRate = (rate, decimals = 2) => {
  if (rate === null || rate === undefined) return 'N/A';
  return new Intl.NumberFormat('es-UY', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(rate);
};

export default exchangeService; 