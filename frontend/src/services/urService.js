import axios from 'axios';
import { getApiBaseUrl, getDirectApiUrl, API_CONFIG } from '../shared/utils/apiConfig.js';

// Configurar las instancias de axios
const api = axios.create({
  baseURL: getApiBaseUrl(),
  ...API_CONFIG,
});

// Instancia directa para fallback
const directApi = axios.create({
  baseURL: getDirectApiUrl(),
  ...API_CONFIG,
});

// Interceptor para manejo de errores
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    if (error.response) {
      console.error('Response data:', error.response.data);
      console.error('Response status:', error.response.status);
    }
    return Promise.reject(error);
  }
);

// Función auxiliar para hacer requests con fallback
const makeRequest = async (requestFn) => {
  try {
    const response = await requestFn(api);
    return response.data;
  } catch (proxyError) {
    try {
      const response = await requestFn(directApi);
      return response.data;
    } catch (directError) {
      console.error('Both proxy and direct requests failed');
      console.error('Proxy error:', proxyError.message);
      console.error('Direct error:', directError.message);
      throw directError;
    }
  }
};

// Servicios de la API para UR
const urService = {
  // Obtener último valor de UR
  getLatest: async () => {
    return makeRequest((apiInstance) => apiInstance.get('/ur/latest'));
  },

  // Obtener valor de UR por año y mes específico
  getByYearMonth: async (year, month) => {
    return makeRequest((apiInstance) => apiInstance.get(`/ur/year-month/${year}/${month}`));
  },

  // Obtener valores de UR por año completo
  getByYear: async (year) => {
    return makeRequest((apiInstance) => apiInstance.get(`/ur/year/${year}`));
  },

  // Obtener valores de UR por rango de períodos
  getByRange: async (startYear, startMonth, endYear, endMonth) => {
    return makeRequest((apiInstance) => apiInstance.get(`/ur/range/${startYear}/${startMonth}/${endYear}/${endMonth}`));
  },

  // Obtener información general de los datos UR
  getInfo: async () => {
    return makeRequest((apiInstance) => apiInstance.get('/ur/info'));
  },

  // Actualizar datos UR desde el BHU
  refresh: async () => {
    return makeRequest((apiInstance) => apiInstance.post('/ur/refresh'));
  },

  // Verificar estado del servicio UR
  healthCheck: async () => {
    return makeRequest((apiInstance) => apiInstance.get('/health'));
  },

  // Función de test para verificar conectividad
  testConnection: async () => {
    try {
      console.log('Testing UR proxy connection...');
      const proxyResult = await api.get('/ur/info');
      console.log('UR Proxy connection successful:', proxyResult.status);
      return { proxy: true, direct: false };
    } catch (proxyError) {
      console.log('UR Proxy failed, testing direct connection...');
      try {
        const directResult = await directApi.get('/ur/info');
        console.log('UR Direct connection successful:', directResult.status);
        return { proxy: false, direct: true };
      } catch (directError) {
        console.error('Both UR connections failed');
        return { proxy: false, direct: false };
      }
    }
  },

  // Simplified function to get UR summary information using existing getInfo
  getURInfo: async () => {
    try {
      const data = await urService.getInfo();
      return {
        success: true,
        data: data
      };
    } catch (error) {
      console.error('Error fetching UR info:', error);
      return {
        success: false,
        error: error.response?.data?.message || error.message || 'Error al obtener información de UR'
      };
    }
  },
};

export default urService;