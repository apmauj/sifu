import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import axios from 'axios';

// Mock de axios
vi.mock('axios');
const mockedAxios = vi.mocked(axios, true);

// Mock de console para evitar logs en las pruebas
const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
const consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
const consoleLogSpy = vi.spyOn(console, 'log').mockImplementation(() => {});

describe('UR Service', () => {
  let urService;

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
    const module = await import('../../shared/services/urService.js');
    urService = module.default;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('getLatest', () => {
    it('should fetch latest UR value successfully', async () => {
      const mockData = { ur_value: 2500.50, year: 2024, month: 12 };
      mockedAxios.get.mockResolvedValue({ data: mockData });
      
      const result = await urService.getLatest();
      
      expect(mockedAxios.get).toHaveBeenCalledWith('/ur/latest');
      expect(result).toEqual(mockData);
    });

    it('should handle errors correctly', async () => {
      const error = new Error('Network error');
      mockedAxios.get.mockRejectedValue(error);
      
      await expect(urService.getLatest()).rejects.toThrow('Network error');
    });
  });

  describe('getByYearMonth', () => {
    it('should fetch UR value by year and month successfully', async () => {
      const mockData = { ur_value: 2450.25, year: 2024, month: 6 };
      mockedAxios.get.mockResolvedValue({ data: mockData });
      
      const result = await urService.getByYearMonth(2024, 6);
      
      expect(mockedAxios.get).toHaveBeenCalledWith('/ur/year-month/2024/6');
      expect(result).toEqual(mockData);
    });

    it('should handle not found errors', async () => {
      const error = new Error('Not found');
      error.response = { status: 404 };
      mockedAxios.get.mockRejectedValue(error);
      
      await expect(urService.getByYearMonth(2030, 12)).rejects.toThrow('Not found');
    });

    it('should handle invalid parameters', async () => {
      const error = new Error('Invalid parameters');
      mockedAxios.get.mockRejectedValue(error);
      
      await expect(urService.getByYearMonth('invalid', 'invalid')).rejects.toThrow('Invalid parameters');
    });
  });

  describe('getByYear', () => {
    it('should fetch UR values by year successfully', async () => {
      const mockData = {
        year: 2024,
        months: [
          { month: 1, ur_value: 2400.00 },
          { month: 2, ur_value: 2420.50 }
        ]
      };
      mockedAxios.get.mockResolvedValue({ data: mockData });
      
      const result = await urService.getByYear(2024);
      
      expect(mockedAxios.get).toHaveBeenCalledWith('/ur/year/2024');
      expect(result).toEqual(mockData);
    });

    it('should handle year not found', async () => {
      const error = new Error('Year not found');
      error.response = { status: 404 };
      mockedAxios.get.mockRejectedValue(error);
      
      await expect(urService.getByYear(1990)).rejects.toThrow('Year not found');
    });

    it('should handle invalid year format', async () => {
      const error = new Error('Invalid year');
      mockedAxios.get.mockRejectedValue(error);
      
      await expect(urService.getByYear('not-a-year')).rejects.toThrow('Invalid year');
    });
  });

  describe('getByRange', () => {
    it('should fetch UR values by range successfully', async () => {
      const mockData = {
        periods: [
          { year: 2023, month: 6, ur_value: 2300.00 },
          { year: 2024, month: 12, ur_value: 2500.50 }
        ]
      };
      mockedAxios.get.mockResolvedValue({ data: mockData });
      
      const result = await urService.getByRange(2023, 6, 2024, 12);
      
      expect(mockedAxios.get).toHaveBeenCalledWith('/ur/range/2023/6/2024/12');
      expect(result).toEqual(mockData);
    });

    it('should handle invalid range parameters', async () => {
      const error = new Error('Invalid range');
      mockedAxios.get.mockRejectedValue(error);
      
      await expect(urService.getByRange(2025, 1, 2024, 12)).rejects.toThrow('Invalid range');
    });

    it('should handle empty range results', async () => {
      const mockData = { periods: [] };
      mockedAxios.get.mockResolvedValue({ data: mockData });
      
      const result = await urService.getByRange(2030, 1, 2030, 12);
      
      expect(result).toEqual(mockData);
      expect(result.periods).toHaveLength(0);
    });
  });

  describe('getInfo', () => {
    it('should fetch UR info successfully', async () => {
      const mockData = {
        total_records: 156,
        earliest_period: '2010-01',
        latest_period: '2024-12'
      };
      mockedAxios.get.mockResolvedValue({ data: mockData });
      
      const result = await urService.getInfo();
      
      expect(mockedAxios.get).toHaveBeenCalledWith('/ur/info');
      expect(result).toEqual(mockData);
    });

    it('should handle service unavailable errors', async () => {
      const error = new Error('Service unavailable');
      error.response = { status: 503 };
      mockedAxios.get.mockRejectedValue(error);
      
      await expect(urService.getInfo()).rejects.toThrow('Service unavailable');
    });
  });

  describe('refresh', () => {
    it('should refresh UR data successfully', async () => {
      const mockData = {
        success: true,
        message: 'UR data refreshed successfully'
      };
      mockedAxios.post.mockResolvedValue({ data: mockData });
      
      const result = await urService.refresh();
      
      expect(mockedAxios.post).toHaveBeenCalledWith('/ur/refresh');
      expect(result).toEqual(mockData);
    });

    it('should handle refresh failures', async () => {
      const error = new Error('Failed to refresh data');
      error.response = { status: 500 };
      mockedAxios.post.mockRejectedValue(error);
      
      await expect(urService.refresh()).rejects.toThrow('Failed to refresh data');
    });

    it('should handle timeout errors', async () => {
      const error = new Error('Request timeout');
      error.code = 'ECONNABORTED';
      mockedAxios.post.mockRejectedValue(error);
      
      await expect(urService.refresh()).rejects.toThrow('Request timeout');
    });
  });

  describe('healthCheck', () => {
    it('should perform health check successfully', async () => {
      const mockData = {
        status: 'healthy',
        timestamp: '2024-12-01T10:00:00Z'
      };
      mockedAxios.get.mockResolvedValue({ data: mockData });
      
      const result = await urService.healthCheck();
      
      expect(mockedAxios.get).toHaveBeenCalledWith('/health');
      expect(result).toEqual(mockData);
    });

    it('should handle health check failures', async () => {
      const error = new Error('Service unhealthy');
      error.response = { status: 503 };
      mockedAxios.get.mockRejectedValue(error);
      
      await expect(urService.healthCheck()).rejects.toThrow('Service unhealthy');
    });
  });

  describe('testConnection', () => {
    it('should test connection successfully', async () => {
      mockedAxios.get.mockResolvedValue({ status: 200, data: { status: 'ok' } });
      
      const result = await urService.testConnection();
      
      expect(mockedAxios.get).toHaveBeenCalledWith('/ur/info');
      expect(result).toEqual({ proxy: true, direct: false });
    });

    it('should handle connection failures', async () => {
      mockedAxios.get.mockRejectedValue(new Error('Connection failed'));
      
      const result = await urService.testConnection();
      
      expect(result).toEqual({ proxy: false, direct: false });
    });

    it('should test direct connection fallback', async () => {
      mockedAxios.get
        .mockRejectedValueOnce(new Error('Proxy failed'))
        .mockResolvedValueOnce({ status: 200, data: { status: 'ok' } });
      
      const result = await urService.testConnection();
      
      expect(result).toEqual({ proxy: false, direct: true });
    });
  });

  describe('Error handling', () => {
    it('should handle response errors correctly', async () => {
      const error = new Error('Server Error');
      error.response = {
        data: { message: 'Internal server error' },
        status: 500
      };
      mockedAxios.get.mockRejectedValue(error);
      
      await expect(urService.getLatest()).rejects.toThrow('Server Error');
    });

    it('should handle network errors', async () => {
      const error = new Error('Network Error');
      error.code = 'NETWORK_ERROR';
      mockedAxios.get.mockRejectedValue(error);
      
      await expect(urService.getLatest()).rejects.toThrow('Network Error');
    });

    it('should handle connection refused errors', async () => {
      const error = new Error('connect ECONNREFUSED');
      error.code = 'ECONNREFUSED';
      mockedAxios.get.mockRejectedValue(error);
      
      await expect(urService.getLatest()).rejects.toThrow('connect ECONNREFUSED');
    });
  });

  describe('Edge cases', () => {
    it('should handle empty response data', async () => {
      mockedAxios.get.mockResolvedValue({ data: null });
      
      const result = await urService.getLatest();
      
      expect(result).toBeNull();
    });

    it('should handle undefined response data', async () => {
      mockedAxios.get.mockResolvedValue({ data: undefined });
      
      const result = await urService.getLatest();
      
      expect(result).toBeUndefined();
    });

    it('should handle malformed response structure', async () => {
      mockedAxios.get.mockResolvedValue({ notData: 'invalid' });
      
      const result = await urService.getLatest();
      
      expect(result).toBeUndefined();
    });
  });
}); 
