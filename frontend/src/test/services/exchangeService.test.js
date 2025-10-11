import { describe, it, expect, vi, beforeEach } from 'vitest';
import { 
  SUPPORTED_CURRENCIES, 
  getCurrencyInfo, 
  formatExchangeRate 
} from '../../services/exchangeService.js';

describe('Exchange Service', () => {
  // Use global mocks from setup.jsx
  const mockAxiosInstance = globalThis.mockAxiosInstance;
  const mockDirectAxiosInstance = globalThis.mockDirectAxiosInstance;
  
  beforeEach(() => {
    vi.clearAllMocks();
    mockAxiosInstance.get.mockReset();
    mockAxiosInstance.post.mockReset();
    mockDirectAxiosInstance.get.mockReset();
    mockDirectAxiosInstance.post.mockReset();
  });

  describe('Service Methods', () => {
    // Importar dinámicamente el servicio después de configurar los mocks
    let exchangeService;
    
    beforeEach(async () => {
      // Re-import the service to get fresh instance with mocks
      exchangeService = (await import('../../services/exchangeService.js')).default;
    });

    describe('getCurrentRates', () => {
      it('should fetch current rates successfully', async () => {
        const mockData = {
          success: true,
          data: [
            { currency: 'USD', buy_rate: 38.50, sell_rate: 41.50, average_rate: 40.00 }
          ]
        };
        
        mockAxiosInstance.get.mockResolvedValue({ data: mockData });
        
        const result = await exchangeService.getCurrentRates();
        
        expect(mockAxiosInstance.get).toHaveBeenCalledWith('/exchange-rate/current');
        expect(result).toEqual(mockData);
      });

      it('should fallback to direct connection when proxy fails', async () => {
        const mockData = {
          success: true,
          data: [
            { currency: 'USD', buy_rate: 38.50, sell_rate: 41.50, average_rate: 40.00 }
          ]
        };
        
        mockAxiosInstance.get.mockRejectedValue(new Error('Proxy failed'));
        mockDirectAxiosInstance.get.mockResolvedValue({ data: mockData });
        
        const result = await exchangeService.getCurrentRates();
        
        expect(mockAxiosInstance.get).toHaveBeenCalledWith('/exchange-rate/current');
        expect(mockDirectAxiosInstance.get).toHaveBeenCalledWith('/exchange-rate/current');
        expect(result).toEqual(mockData);
      });

      it('should throw error when both connections fail', async () => {
        mockAxiosInstance.get.mockRejectedValue(new Error('Proxy failed'));
        mockDirectAxiosInstance.get.mockRejectedValue(new Error('Direct failed'));
        
        await expect(exchangeService.getCurrentRates()).rejects.toThrow('Direct failed');
      });
    });

    describe('getLatest', () => {
      it('should fetch latest rates without filters', async () => {
        const mockData = { success: true, data: [] };
        mockAxiosInstance.get.mockResolvedValue({ data: mockData });
        
        const result = await exchangeService.getLatest();
        
        expect(mockAxiosInstance.get).toHaveBeenCalledWith('/exchange-rate/latest', { params: {} });
        expect(result).toEqual(mockData);
      });

      it('should fetch latest rates with currency filter', async () => {
        const mockData = { success: true, data: [] };
        mockAxiosInstance.get.mockResolvedValue({ data: mockData });
        
        const result = await exchangeService.getLatest('USD');
        
        expect(mockAxiosInstance.get).toHaveBeenCalledWith('/exchange-rate/latest', { params: { currencies: 'USD' } });
        expect(result).toEqual(mockData);
      });
    });

    describe('getInfo', () => {
      it('should fetch exchange rate info successfully', async () => {
        const mockData = { success: true, info: 'Exchange rate information' };
        mockAxiosInstance.get.mockResolvedValue({ data: mockData });
        
        const result = await exchangeService.getInfo();
        
        expect(mockAxiosInstance.get).toHaveBeenCalledWith('/exchange-rate/info');
        expect(result).toEqual(mockData);
      });
    });

    describe('getCurrencyHistory', () => {
      it('should fetch currency history with default limit', async () => {
        const mockData = { success: true, data: [] };
        mockAxiosInstance.get.mockResolvedValue({ data: mockData });
        
        const result = await exchangeService.getCurrencyHistory('USD');
        
        expect(mockAxiosInstance.get).toHaveBeenCalledWith('/exchange-rate/currency/USD', { params: { limit: 30 } });
        expect(result).toEqual(mockData);
      });

      it('should fetch currency history with custom limit', async () => {
        const mockData = { success: true, data: [] };
        mockAxiosInstance.get.mockResolvedValue({ data: mockData });
        
        const result = await exchangeService.getCurrencyHistory('EUR', 50);
        
        expect(mockAxiosInstance.get).toHaveBeenCalledWith('/exchange-rate/currency/EUR', { params: { limit: 50 } });
        expect(result).toEqual(mockData);
      });
    });

    describe('getByDate', () => {
      it('should fetch rates by date without currency filter', async () => {
        const mockData = { success: true, data: [] };
        mockAxiosInstance.get.mockResolvedValue({ data: mockData });
        
        const result = await exchangeService.getByDate('2024-01-01');
        
        expect(mockAxiosInstance.get).toHaveBeenCalledWith('/exchange-rate/2024-01-01', { params: {} });
        expect(result).toEqual(mockData);
      });

      it('should fetch rates by date with currency filter', async () => {
        const mockData = { success: true, data: [] };
        mockAxiosInstance.get.mockResolvedValue({ data: mockData });
        
        const result = await exchangeService.getByDate('2024-01-01', 'USD');
        
        expect(mockAxiosInstance.get).toHaveBeenCalledWith('/exchange-rate/2024-01-01', { params: { currency: 'USD' } });
        expect(result).toEqual(mockData);
      });
    });

    describe('getSpecificRate', () => {
      it('should fetch specific rate for date and currency', async () => {
        const mockData = { success: true, data: { currency: 'USD', rate: 40.00 } };
        mockAxiosInstance.get.mockResolvedValue({ data: mockData });
        
        const result = await exchangeService.getSpecificRate('2024-01-01', 'USD');
        
        expect(mockAxiosInstance.get).toHaveBeenCalledWith('/exchange-rate/2024-01-01/USD');
        expect(result).toEqual(mockData);
      });
    });

    describe('getByDateRange', () => {
      it('should fetch rates by date range without currency filter', async () => {
        const mockData = { success: true, data: [] };
        mockAxiosInstance.get.mockResolvedValue({ data: mockData });
        
        const result = await exchangeService.getByDateRange('2024-01-01', '2024-01-31');
        
        expect(mockAxiosInstance.get).toHaveBeenCalledWith('/exchange-rate/range/2024-01-01/2024-01-31', { params: {} });
        expect(result).toEqual(mockData);
      });

      it('should fetch rates by date range with currency filter', async () => {
        const mockData = { success: true, data: [] };
        mockAxiosInstance.get.mockResolvedValue({ data: mockData });
        
        const result = await exchangeService.getByDateRange('2024-01-01', '2024-01-31', 'EUR');
        
        expect(mockAxiosInstance.get).toHaveBeenCalledWith('/exchange-rate/range/2024-01-01/2024-01-31', { params: { currency: 'EUR' } });
        expect(result).toEqual(mockData);
      });
    });

    describe('refresh', () => {
      it('should refresh data without sample data flag', async () => {
        const mockData = { success: true, message: 'Data refreshed' };
        mockAxiosInstance.post.mockResolvedValue({ data: mockData });
        
        const result = await exchangeService.refresh();
        
        expect(mockAxiosInstance.post).toHaveBeenCalledWith('/exchange-rate/refresh', {}, { params: {} });
        expect(result).toEqual(mockData);
      });

      it('should refresh data with sample data flag', async () => {
        const mockData = { success: true, message: 'Sample data loaded' };
        mockAxiosInstance.post.mockResolvedValue({ data: mockData });
        
        const result = await exchangeService.refresh(true);
        
        expect(mockAxiosInstance.post).toHaveBeenCalledWith('/exchange-rate/refresh', {}, { params: { use_sample_data: true } });
        expect(result).toEqual(mockData);
      });
    });

    describe('testConnection', () => {
      it('should return proxy success when proxy works', async () => {
        mockAxiosInstance.get.mockResolvedValue({ status: 200 });
        
        const result = await exchangeService.testConnection();
        
        expect(result).toEqual({ proxy: true, direct: false });
        expect(mockAxiosInstance.get).toHaveBeenCalledWith('/exchange-rate/latest');
      });

      it('should return direct success when proxy fails but direct works', async () => {
        mockAxiosInstance.get.mockRejectedValue(new Error('Proxy failed'));
        mockDirectAxiosInstance.get.mockResolvedValue({ status: 200 });
        
        const result = await exchangeService.testConnection();
        
        expect(result).toEqual({ proxy: false, direct: true });
        expect(mockDirectAxiosInstance.get).toHaveBeenCalledWith('/exchange-rate/latest');
      });

      it('should return both false when all connections fail', async () => {
        mockAxiosInstance.get.mockRejectedValue(new Error('Proxy failed'));
        mockDirectAxiosInstance.get.mockRejectedValue(new Error('Direct failed'));
        
        const result = await exchangeService.testConnection();
        
        expect(result).toEqual({ proxy: false, direct: false });
      });
    });
  });

  describe('Error Handling', () => {
    let exchangeService;
    
    beforeEach(async () => {
      exchangeService = (await import('../../services/exchangeService.js')).default;
    });

    it('should handle network errors gracefully', async () => {
      const networkError = new Error('Network Error');
      networkError.code = 'ERR_NETWORK';
      
      mockAxiosInstance.get.mockRejectedValue(networkError);
      mockDirectAxiosInstance.get.mockRejectedValue(networkError);
      
      await expect(exchangeService.getCurrentRates()).rejects.toThrow('Network Error');
    });

    it('should handle timeout errors', async () => {
      const timeoutError = new Error('Timeout');
      timeoutError.code = 'ECONNABORTED';
      
      mockAxiosInstance.get.mockRejectedValue(timeoutError);
      mockDirectAxiosInstance.get.mockRejectedValue(timeoutError);
      
      await expect(exchangeService.getLatest()).rejects.toThrow('Timeout');
    });

    it('should handle 404 errors', async () => {
      const notFoundError = new Error('Not Found');
      notFoundError.response = { status: 404 };
      
      mockAxiosInstance.get.mockRejectedValue(notFoundError);
      mockDirectAxiosInstance.get.mockRejectedValue(notFoundError);
      
      await expect(exchangeService.getByDate('2024-01-01')).rejects.toThrow('Not Found');
    });

    it('should handle 500 errors', async () => {
      const serverError = new Error('Internal Server Error');
      serverError.response = { status: 500 };
      
      mockAxiosInstance.get.mockRejectedValue(serverError);
      mockDirectAxiosInstance.get.mockRejectedValue(serverError);
      
      await expect(exchangeService.getInfo()).rejects.toThrow('Internal Server Error');
    });
  });

  describe('Edge Cases', () => {
    let exchangeService;
    
    beforeEach(async () => {
      exchangeService = (await import('../../services/exchangeService.js')).default;
    });

    it('should handle empty response data', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: null });
      
      const result = await exchangeService.getCurrentRates();
      expect(result).toBeNull();
    });

    it('should handle undefined response', async () => {
      mockAxiosInstance.get.mockResolvedValue({});
      
      const result = await exchangeService.getLatest();
      expect(result).toBeUndefined();
    });

    it('should handle malformed response structure', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: { unexpected: 'structure' } });
      
      const result = await exchangeService.getInfo();
      expect(result).toEqual({ unexpected: 'structure' });
    });
  });
});

describe('Exchange Service Helpers', () => {
  describe('SUPPORTED_CURRENCIES constant', () => {
    it('should have correct number of supported currencies', () => {
      expect(SUPPORTED_CURRENCIES).toHaveLength(6); // USD, USD_EBROU, EUR, ARS, BRL, CLP
    });

    it('should include all expected currencies with correct structure', () => {
      const expectedCurrencies = [
        { code: 'USD', flag: '🇺🇸' },
        { code: 'EUR', flag: '🇪🇺' },
        { code: 'ARS', flag: '🇦🇷' },
        { code: 'BRL', flag: '🇧🇷' },
      ];

      expectedCurrencies.forEach(expected => {
        const found = SUPPORTED_CURRENCIES.find(currency => currency.code === expected.code);
        expect(found).toBeDefined();
        expect(found.flag).toBe(expected.flag);
      });
    });

    it('should have proper structure for each currency', () => {
      SUPPORTED_CURRENCIES.forEach(currency => {
        expect(currency).toHaveProperty('code');
        expect(currency).toHaveProperty('flag');
        expect(typeof currency.code).toBe('string');
        expect(typeof currency.flag).toBe('string');
        // USD_EBROU has 9 characters, standard currencies have 3
        expect(currency.code.length).toBeGreaterThanOrEqual(3);
      });
    });

    it('should include USD as first currency', () => {
      expect(SUPPORTED_CURRENCIES[0].code).toBe('USD');
      expect(SUPPORTED_CURRENCIES[0].flag).toBe('🇺🇸');
    });

    it('should include CLP (added currency)', () => {
      const clp = SUPPORTED_CURRENCIES.find(currency => currency.code === 'CLP');
      expect(clp).toBeDefined();
      expect(clp.flag).toBe('🇨🇱');
    });
  });

  describe('getCurrencyInfo function', () => {
    it('should return correct currency info for valid codes', () => {
      const testCases = [
        { code: 'USD', expectedFlag: '🇺🇸' },
        { code: 'EUR', expectedFlag: '🇪🇺' },
        { code: 'ARS', expectedFlag: '🇦🇷' },
        { code: 'BRL', expectedFlag: '🇧🇷' },
      ];

      testCases.forEach(({ code, expectedFlag }) => {
        const result = getCurrencyInfo(code);
        expect(result).toBeDefined();
        expect(result.code).toBe(code);
        expect(result.flag).toBe(expectedFlag);
      });
    });

    it('should return undefined for invalid currency codes', () => {
      const invalidCodes = ['JPY', 'GBP', 'CNY', 'invalid', '', null, undefined];
      
      invalidCodes.forEach(code => {
        const result = getCurrencyInfo(code);
        expect(result).toBeUndefined();
      });
    });

    it('should be case sensitive', () => {
      expect(getCurrencyInfo('usd')).toBeUndefined();
      expect(getCurrencyInfo('USD')).toBeDefined();
      expect(getCurrencyInfo('Usd')).toBeUndefined();
    });

    it('should handle edge cases', () => {
      expect(getCurrencyInfo('')).toBeUndefined();
      expect(getCurrencyInfo('   ')).toBeUndefined();
      expect(getCurrencyInfo('USDD')).toBeUndefined();
      expect(getCurrencyInfo('US')).toBeUndefined();
    });
  });

  describe('formatExchangeRate function', () => {
    it('should format valid rates with default 2 decimals', () => {
      const testCases = [
        { input: 42.5, expected: '42,50' },
        { input: 43.123, expected: '43,12' },
        { input: 1000.99, expected: '1.000,99' },
        { input: 0.5, expected: '0,50' },
        { input: 0, expected: '0,00' },
      ];

      testCases.forEach(({ input, expected }) => {
        const result = formatExchangeRate(input);
        expect(result).toBe(expected);
      });
    });

    it('should format rates with custom decimal places', () => {
      const testCases = [
        { rate: 42.123456, decimals: 0, expected: '42' },
        { rate: 42.123456, decimals: 1, expected: '42,1' },
        { rate: 42.123456, decimals: 3, expected: '42,123' },
        { rate: 42.123456, decimals: 4, expected: '42,1235' },
      ];

      testCases.forEach(({ rate, decimals, expected }) => {
        const result = formatExchangeRate(rate, decimals);
        expect(result).toBe(expected);
      });
    });

    it('should handle null and undefined values', () => {
      expect(formatExchangeRate(null)).toBe('N/A');
      expect(formatExchangeRate(undefined)).toBe('N/A');
    });

    it('should handle edge number cases', () => {
      const testCases = [
        { input: 0, expected: '0,00' },
        { input: -42.5, expected: '-42,50' },
        { input: 0.001, expected: '0,00' },
        { input: 999999.99, expected: '999.999,99' },
      ];

      testCases.forEach(({ input, expected }) => {
        const result = formatExchangeRate(input);
        expect(result).toBe(expected);
      });
    });

    it('should use Spanish (Uruguay) locale formatting', () => {
      // Verificar que usa coma como separador decimal y punto como separador de miles
      expect(formatExchangeRate(1234.56)).toBe('1.234,56');
      expect(formatExchangeRate(1234567.89)).toBe('1.234.567,89');
    });

    it('should handle very small numbers', () => {
      expect(formatExchangeRate(0.001, 3)).toBe('0,001');
      expect(formatExchangeRate(0.0001, 4)).toBe('0,0001');
      expect(formatExchangeRate(0.00001, 2)).toBe('0,00');
    });

    it('should handle very large numbers', () => {
      expect(formatExchangeRate(1000000)).toBe('1.000.000,00');
      expect(formatExchangeRate(1000000.123, 3)).toBe('1.000.000,123');
    });
  });

  describe('Integration tests for helpers', () => {
    it('should work together for currency display', () => {
      const currency = 'USD';
      const rate = 42.75;
      
      const currencyInfo = getCurrencyInfo(currency);
      const formattedRate = formatExchangeRate(rate);
      
      expect(currencyInfo).toBeDefined();
      expect(currencyInfo.code).toBe('USD');
      expect(currencyInfo.flag).toBe('🇺🇸');
      expect(formattedRate).toBe('42,75');
    });

    it('should handle all supported currencies consistently', () => {
      SUPPORTED_CURRENCIES.forEach(currency => {
        const info = getCurrencyInfo(currency.code);
        expect(info).toBeDefined();
        expect(info.code).toBe(currency.code);
        expect(info.flag).toBe(currency.flag);
      });
    });

    it('should format rates for all supported currencies', () => {
      const sampleRates = {
        USD: 42.75,
        EUR: 46.20,
        ARS: 0.85,
        BRL: 8.30
      };

      Object.entries(sampleRates).forEach(([currency, rate]) => {
        const info = getCurrencyInfo(currency);
        const formatted = formatExchangeRate(rate);
        
        expect(info).toBeDefined();
        expect(formatted).toMatch(/^\d{1,3}(\.\d{3})*,\d{2}$/);
      });
    });
  });

  describe('Constants validation', () => {
    it('should maintain currency order for UI consistency', () => {
      const expectedOrder = ['USD', 'USD_EBROU', 'EUR', 'ARS', 'BRL', 'CLP'];
      const actualOrder = SUPPORTED_CURRENCIES.map(c => c.code);
      expect(actualOrder).toEqual(expectedOrder);
    });

    it('should have unique currency codes', () => {
      const codes = SUPPORTED_CURRENCIES.map(c => c.code);
      const uniqueCodes = [...new Set(codes)];
      expect(codes).toEqual(uniqueCodes);
    });

    it('should have valid flag emojis', () => {
      SUPPORTED_CURRENCIES.forEach(currency => {
        expect(currency.flag).toMatch(/^[\u{1F1E6}-\u{1F1FF}]{2}$/u);
      });
    });
  });
});