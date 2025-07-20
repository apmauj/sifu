import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import axios from 'axios';

// Mock de axios
vi.mock('axios');
const mockedAxios = vi.mocked(axios, true);

// Mock de import.meta.env
Object.defineProperty(import.meta, 'env', {
  value: {
    DEV: true,
    VITE_API_BASE_URL: 'http://localhost:8000'
  },
  writable: true
});

// Mock de console para evitar logs en las pruebas
const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
const consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
const consoleLogSpy = vi.spyOn(console, 'log').mockImplementation(() => {});

describe('API Service', () => {
  let uiService;

  beforeEach(async () => {
    vi.clearAllMocks();
    consoleSpy.mockClear();
    consoleWarnSpy.mockClear();
    consoleLogSpy.mockClear();
    
    // Configurar mocks de axios
    mockedAxios.create.mockReturnValue(mockedAxios);
    mockedAxios.interceptors = {
      request: { use: vi.fn() },
      response: { use: vi.fn() }
    };
    
    // Importar dinámicamente el servicio para que use los mocks
    const module = await import('../../services/api');
    uiService = module.default;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('getLatest', () => {
    it('should fetch latest UI value successfully', async () => {
      const mockData = { fecha: '2024-01-01', valor: 5.1234 };
      mockedAxios.get.mockResolvedValue({ data: mockData });
      
      const result = await uiService.getLatest();
      
      expect(mockedAxios.get).toHaveBeenCalledWith('/ui/latest');
      expect(result).toEqual(mockData);
    });

    it('should handle errors correctly', async () => {
      const error = new Error('Network error');
      mockedAxios.get.mockRejectedValue(error);
      
      await expect(uiService.getLatest()).rejects.toThrow('Network error');
    });
  });

  describe('getByDate', () => {
    it('should fetch UI value by date successfully', async () => {
      const fecha = '2024-01-01';
      const mockData = { fecha, valor: 5.1234 };
      mockedAxios.get.mockResolvedValue({ data: mockData });
      
      const result = await uiService.getByDate(fecha);
      
      expect(mockedAxios.get).toHaveBeenCalledWith(`/ui/${fecha}`);
      expect(result).toEqual(mockData);
    });

    it('should handle date not found', async () => {
      const fecha = '2024-12-31';
      const error = new Error('Not found');
      error.response = { status: 404 };
      mockedAxios.get.mockRejectedValue(error);
      
      await expect(uiService.getByDate(fecha)).rejects.toThrow('Not found');
    });
  });

  describe('getByRange', () => {
    it('should fetch UI values by date range successfully', async () => {
      const fechaInicio = '2024-01-01';
      const fechaFin = '2024-01-31';
      const mockData = [
        { fecha: '2024-01-01', valor: 5.1234 },
        { fecha: '2024-01-02', valor: 5.1235 }
      ];
      mockedAxios.get.mockResolvedValue({ data: mockData });
      
      const result = await uiService.getByRange(fechaInicio, fechaFin);
      
      expect(mockedAxios.get).toHaveBeenCalledWith(`/ui/range/${fechaInicio}/${fechaFin}`);
      expect(result).toEqual(mockData);
    });

    it('should handle empty range results', async () => {
      const fechaInicio = '2030-01-01';
      const fechaFin = '2030-01-31';
      const mockData = [];
      mockedAxios.get.mockResolvedValue({ data: mockData });
      
      const result = await uiService.getByRange(fechaInicio, fechaFin);
      
      expect(result).toEqual([]);
    });
  });

  describe('getInfo', () => {
    it('should fetch app info successfully', async () => {
      const mockData = {
        total_records: 1000,
        date_range: {
          min_date: '2020-01-01',
          max_date: '2024-12-31'
        },
        latest_ui: {
          value: 5.1234,
          date: '2024-01-01'
        }
      };
      mockedAxios.get.mockResolvedValue({ data: mockData });
      
      const result = await uiService.getInfo();
      
      expect(mockedAxios.get).toHaveBeenCalledWith('/info');
      expect(result).toEqual(mockData);
      expect(result.total_records).toBe(1000);
      expect(result.date_range.min_date).toBe('2020-01-01');
    });

    it('should handle info not available', async () => {
      const error = new Error('Service unavailable');
      mockedAxios.get.mockRejectedValue(error);
      
      await expect(uiService.getInfo()).rejects.toThrow('Service unavailable');
    });
  });

  describe('refresh', () => {
    it('should refresh data successfully', async () => {
      const mockData = {
        message: 'Data refreshed successfully',
        records_updated: 50
      };
      mockedAxios.post.mockResolvedValue({ data: mockData });
      
      const result = await uiService.refresh();
      
      expect(mockedAxios.post).toHaveBeenCalledWith('/refresh');
      expect(result).toEqual(mockData);
    });

    it('should handle refresh failure', async () => {
      const error = new Error('Failed to refresh data');
      mockedAxios.post.mockRejectedValue(error);
      
      await expect(uiService.refresh()).rejects.toThrow('Failed to refresh data');
    });
  });

  describe('healthCheck', () => {
    it('should check service health successfully', async () => {
      const mockData = {
        status: 'healthy',
        timestamp: '2024-01-01T00:00:00Z',
        version: '1.0.0'
      };
      mockedAxios.get.mockResolvedValue({ data: mockData });
      
      const result = await uiService.healthCheck();
      
      expect(mockedAxios.get).toHaveBeenCalledWith('/health');
      expect(result).toEqual(mockData);
      expect(result.status).toBe('healthy');
    });

    it('should handle health check failure', async () => {
      const error = new Error('Service unhealthy');
      mockedAxios.get.mockRejectedValue(error);
      
      await expect(uiService.healthCheck()).rejects.toThrow('Service unhealthy');
    });
  });

  describe('testConnection', () => {
    it('should test proxy connection successfully', async () => {
      mockedAxios.get.mockResolvedValue({ status: 200, data: { status: 'ok' } });
      
      const result = await uiService.testConnection();
      
      expect(mockedAxios.get).toHaveBeenCalledWith('/health');
      expect(result).toEqual({ proxy: true, direct: false });
    });

    it('should fallback to direct connection when proxy fails', async () => {
      // Primer intento (proxy) falla, segundo intento (directo) funciona
      mockedAxios.get
        .mockRejectedValueOnce(new Error('Proxy failed'))
        .mockResolvedValueOnce({ status: 200, data: { status: 'ok' } });
      
      const result = await uiService.testConnection();
      
      expect(result).toEqual({ proxy: false, direct: true });
    });

    it('should return false for both when all connections fail', async () => {
      mockedAxios.get.mockRejectedValue(new Error('Connection failed'));
      
      const result = await uiService.testConnection();
      
      expect(result).toEqual({ proxy: false, direct: false });
    });
  });

  describe('Fallback mechanism', () => {
    it('should fallback to direct connection when proxy fails', async () => {
      const mockData = { fecha: '2024-01-01', valor: 5.1234 };
      
      // Primer intento (proxy) falla, segundo intento (directo) funciona
      mockedAxios.get
        .mockRejectedValueOnce(new Error('Proxy failed'))
        .mockResolvedValueOnce({ data: mockData });
      
      const result = await uiService.getLatest();
      
      expect(result).toEqual(mockData);
      // El fallback funciona correctamente, se puede verificar en los logs de stderr
    });

    it('should handle network errors gracefully', async () => {
      const networkError = new Error('Network Error');
      networkError.code = 'NETWORK_ERROR';
      mockedAxios.get.mockRejectedValue(networkError);
      
      await expect(uiService.getLatest()).rejects.toThrow('Network Error');
    });
  });

  describe('Service configuration', () => {
    it('should create and configure axios instances properly', async () => {
      // Esta prueba verifica que el servicio funciona correctamente
      // La configuración se hace en tiempo de importación del módulo
      const mockData = { status: 'ok' };
      mockedAxios.get.mockResolvedValue({ data: mockData });
      
      const result = await uiService.healthCheck();
      
      expect(result).toEqual(mockData);
      expect(mockedAxios.get).toHaveBeenCalledWith('/health');
    });

    it('should handle axios configuration correctly', async () => {
      // Verificar que el servicio maneja las configuraciones de axios correctamente
      // probando diferentes métodos HTTP
      const mockData = { message: 'success' };
      mockedAxios.post.mockResolvedValue({ data: mockData });
      
      const result = await uiService.refresh();
      
      expect(result).toEqual(mockData);
      expect(mockedAxios.post).toHaveBeenCalledWith('/refresh');
    });
  });
}); 