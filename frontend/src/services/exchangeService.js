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

// Servicios de Exchange Rates API - Terminología Unificada (Punto 5)
const exchangeService = {
  // Obtener cotizaciones actuales (tiempo real) - Unificado
  getCurrent: async (source = null) => {
    const params = source ? { source } : {};
    return makeRequest((apiInstance) => 
      apiInstance.get('/exchange-rate/current', { params })
    );
  },

  // Obtener cotizaciones actuales del BCU (tiempo real) - Legacy
  getCurrentRates: async () => {
    return makeRequest((apiInstance) => apiInstance.get('/exchange-rate/current'));
  },

  // Obtener últimas cotizaciones (todas las monedas o una específica) - Unificado
  getLatest: async (currency = null) => {
    // Convertir array a string separado por comas si es necesario
    let currencyParam = currency;
    if (Array.isArray(currency)) {
      currencyParam = currency.join(',');
    }
    const params = currencyParam ? { currencies: currencyParam } : {};
    return makeRequest((apiInstance) => 
      apiInstance.get('/exchange-rate/latest', { params })
    );
  },

  // Obtener información general de cotizaciones - Unificado
  getInfo: async () => {
    return makeRequest((apiInstance) => apiInstance.get('/exchange-rate/info'));
  },

  // Obtener historial por moneda específica - Unificado
  getCurrencyHistory: async (currency, limit = 30) => {
    return makeRequest((apiInstance) => 
      apiInstance.get(`/exchange-rate/currency/${currency}`, { 
        params: { limit } 
      })
    );
  },

  // Obtener cotizaciones por fecha específica - Unificado
  getByDate: async (date, currency = null) => {
    // Convertir array a string separado por comas si es necesario
    let currencyParam = currency;
    if (Array.isArray(currency)) {
      currencyParam = currency.join(',');
    }
    const params = currencyParam ? { currency: currencyParam } : {};
    return makeRequest((apiInstance) => 
      apiInstance.get(`/exchange-rate/${date}`, { params })
    );
  },

  // Obtener cotización específica (fecha + moneda) - Unificado
  getSpecificRate: async (date, currency) => {
    return makeRequest((apiInstance) => 
      apiInstance.get(`/exchange-rate/${date}/${currency}`)
    );
  },

  // Obtener cotizaciones por rango de fechas - Unificado
  getByDateRange: async (startDate, endDate, currency = null) => {
    // Convertir array a string separado por comas si es necesario
    let currencyParam = currency;
    if (Array.isArray(currency)) {
      currencyParam = currency.join(',');
    }
    const params = currencyParam ? { currency: currencyParam } : {};
    return makeRequest((apiInstance) => 
      apiInstance.get(`/exchange-rate/range/${startDate}/${endDate}`, { params })
    );
  },

  // Actualizar datos - Unificado
  refresh: async (useSampleData = false) => {
    // Mantener endpoint síncrono legado (podría retirarse en el futuro)
    const params = useSampleData ? { use_sample_data: true } : {};
    return makeRequest((apiInstance) =>
      apiInstance.post('/exchange-rate/refresh', {}, { params })
    );
  },

  // Iniciar refresh histórico asíncrono (202 Accepted) - Legacy
  startAsyncHistoricalRefresh: async () => {
    return makeRequest((apiInstance) => 
      apiInstance.post('/exchange-rate/refresh-async')
    );
  },

  // Obtener estado de un job - Legacy
  getJobStatus: async (jobId) => {
    if (!jobId) throw new Error('jobId requerido');
    return makeRequest((apiInstance) => 
      apiInstance.get(`/jobs/${jobId}`)
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

// Constantes para monedas soportadas - Terminología Unificada (Punto 5)
export const SUPPORTED_CURRENCIES = [
  { code: 'USD', name: 'Dólar Estadounidense', flag: '🇺🇸' },
  { code: 'USD_EBROU', name: 'Dólar eBROU', flag: '🇺🇸' },
  { code: 'EUR', name: 'Euro', flag: '🇪🇺' },
  { code: 'ARS', name: 'Peso Argentino', flag: '🇦🇷' },
  { code: 'BRL', name: 'Real Brasileño', flag: '🇧🇷' },
  { code: 'CLP', name: 'Peso Chileno', flag: '🇨🇱' },
];

export const CURRENCY_SYMBOLS = {
  USD: 'US$',
  USD_EBROU: 'US$',
  EUR: '€',
  ARS: '$',
  BRL: 'R$',
  CLP: '$',
};

// Fuentes de datos unificadas
export const EXCHANGE_SOURCES = {
  BCU: {
    code: 'BCU',
    name: 'Banco Central del Uruguay',
    description: 'Datos en tiempo real del BCU'
  },
  INE: {
    code: 'INE',
    name: 'Instituto Nacional de Estadística',
    description: 'Datos históricos del INE'
  },
  BROU: {
    code: 'BROU',
    name: 'Banco República del Uruguay',
    description: 'Cotizaciones bancarias del BROU'
  }
};

// Tipos de fuente unificados
export const SOURCE_TYPES = {
  LIVE: 'live',
  HISTORICAL: 'historical',
  SAMPLE: 'sample',
  PERSISTED: 'persisted'
};

// Helper para obtener información de una moneda
export const getCurrencyInfo = (currencyCode) => {
  return SUPPORTED_CURRENCIES.find(currency => currency.code === currencyCode);
};

// Helper para obtener información de una fuente
export const getSourceInfo = (sourceCode) => {
  return EXCHANGE_SOURCES[sourceCode] || {
    code: sourceCode,
    name: sourceCode,
    description: `Fuente: ${sourceCode}`
  };
};

// Helper para formatear tasas de cambio
export const formatExchangeRate = (rate, decimals = 2) => {
  if (rate === null || rate === undefined) return 'N/A';
  return new Intl.NumberFormat('es-UY', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(rate);
};

// Helper para formatear datos de exchange unificados
export const formatExchangeData = (data) => {
  if (!data || !Array.isArray(data)) return [];
  
  return data.map(item => ({
    currency: item.currency,
    currencyName: getCurrencyInfo(item.currency)?.name || item.currency,
    buyRate: item.buy_rate,
    sellRate: item.sell_rate,
    averageRate: item.average_rate,
    date: item.date,
    source: item.source,
    sourceType: item.source_type,
    timestamp: item.timestamp,
    isPreferential: item.is_preferential || false,
    arbitrageBuy: item.arbitrage_buy,
    arbitrageSell: item.arbitrage_sell
  }));
};

// Helper para obtener metadatos de exchange
export const getExchangeMetadata = (response) => {
  if (!response || !response.metadata) return null;
  
  return {
    totalRecords: response.metadata.total_records,
    source: response.metadata.source,
    sourceType: response.metadata.source_type,
    sourceDescription: response.metadata.source_description,
    timestamp: response.metadata.timestamp,
    currencyNames: response.metadata.currency_names,
    dataAgeMinutes: response.metadata.data_age_minutes,
    isFresh: response.metadata.is_fresh,
    status: response.metadata.status
  };
};

export default exchangeService; 