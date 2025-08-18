import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import ExchangeRatePanel from '../../components/ExchangeRatePanel';
import { vi } from 'vitest';
import { renderAsync, actFlush } from '../utils/renderAsync';

// Mock global fetch
global.fetch = vi.fn();

// Mock del exchangeService
vi.mock('../../services/exchangeService', () => ({
  default: {
    getCurrentRates: vi.fn()
  }
}));

// Mock inteligente del hook useHourlySyncedUpdate (estrategia del BROUPanel)
let hasExecuted = false;
let currentUpdateFn = null;

vi.mock('../../hooks/useHourlySyncedUpdate', () => ({
  useHourlySyncedUpdate: vi.fn((updateFn) => {
    currentUpdateFn = updateFn;
    
    // Ejecutar automáticamente en el primer render (como BROUPanel)
    if (!hasExecuted && updateFn && typeof updateFn === 'function') {
      hasExecuted = true;
      setTimeout(() => updateFn(), 0);
    }
    
    return vi.fn(() => {
      if (updateFn && typeof updateFn === 'function') {
        updateFn();
      }
    });
  })
}));

// Reset function para cada test
const resetMock = () => {
  hasExecuted = false;
  currentUpdateFn = null;
};

// Import test fixtures para datos controlados
import { 
  DEFAULT_MOCK_RATES,
  EXPECTED_VALUES,
  TEST_SCENARIOS,
  setupMockWithData,
  createMockRatesArray,
  TEST_EXCHANGE_RATES
} from '../fixtures/exchangeRateFixtures';

// Usar datos de fixtures (valores controlados y determinísticos)
const mockRatesData = DEFAULT_MOCK_RATES;

describe('ExchangeRatePanel', () => {
  let mockExchangeService;
  
  beforeEach(async () => {
    vi.clearAllMocks();
    resetMock();
    mockExchangeService = (await import('../../services/exchangeService')).default;
  });

  describe('Loading State', () => {
    it('should show loading message initially', async () => {
      mockExchangeService.getCurrentRates.mockImplementation(() => new Promise(() => {}));
      await renderAsync(<ExchangeRatePanel />);
      expect(screen.getByText('Cargando cotizaciones...')).toBeInTheDocument();
    });

    it('should apply correct loading styling', async () => {
      mockExchangeService.getCurrentRates.mockImplementation(() => new Promise(() => {}));
      await renderAsync(<ExchangeRatePanel />);
      const loadingElement = screen.getByText('Cargando cotizaciones...');
      expect(loadingElement).toBeInTheDocument();
      const parentDiv = loadingElement.closest('.bg-gray-800');
      expect(parentDiv).toHaveClass('bg-gray-800', 'text-white');
    });

    it('should not show loading when data is already present', async () => {
      mockExchangeService.getCurrentRates.mockResolvedValue({ success: true, data: mockRatesData });
      await renderAsync(<ExchangeRatePanel />);
      await waitFor(() => {
        expect(screen.queryByText('Cargando cotizaciones...')).not.toBeInTheDocument();
      });
    });
  });

  describe('Error State', () => {
    it('should show error message when API fails', async () => {
      mockExchangeService.getCurrentRates.mockRejectedValue(new Error('Network error'));

      render(<ExchangeRatePanel />);

      await waitFor(() => {
        // Component may show one of two i18n-based messages
        const possible = [
          /Error de conexión/i,
          /No se pudo cargar las cotizaciones/i,
          /Error obteniendo cotizaciones actuales/i
        ];
        expect(possible.some(r => screen.queryByText(r))).toBe(true);
      }, { timeout: 3000 });
    });

  // Retry button removed (automatic hourly updates only)

    it('should handle API response with success: false', async () => {
      mockExchangeService.getCurrentRates.mockResolvedValue({
        success: false,
        message: 'API service unavailable'
      });

      render(<ExchangeRatePanel />);

      await waitFor(() => {
        expect(screen.getByText(/error/i)).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    it('should not show error when data is already present', async () => {
      // First render with data
      mockExchangeService.getCurrentRates.mockResolvedValueOnce({
        success: true,
        data: mockRatesData
      });

      const { rerender } = render(<ExchangeRatePanel />);

      await waitFor(() => {
        expect(screen.getAllByText('USD')[0]).toBeInTheDocument();
      }, { timeout: 3000 });

      // Second render with error but data still present
      mockExchangeService.getCurrentRates.mockRejectedValue(new Error('Network error'));
      
      rerender(<ExchangeRatePanel />);

      // Should still show data, not error
      expect(screen.getAllByText('USD')[0]).toBeInTheDocument();
      expect(screen.queryByText('❌')).not.toBeInTheDocument();
    });
  });

  describe('Success State', () => {
    beforeEach(() => {
      mockExchangeService.getCurrentRates.mockResolvedValue({
        success: true,
        data: mockRatesData
      });
    });

    it('should display BCU title when data loads', async () => {
      render(<ExchangeRatePanel />);
      
      // Verificar estado inicial de loading
  expect(screen.getByText('Cargando cotizaciones...')).toBeInTheDocument();
      
      // Esperar a que el hook ejecute y cargue los datos (como BROUPanel)
      await waitFor(() => {
        expect(screen.getAllByText(/Cotizaciones BCU/)[0]).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    it('should display currency information when data loads', async () => {
      render(<ExchangeRatePanel />);
      
      // Esperar a que aparezcan las monedas (manejo de elementos duplicados)
      await waitFor(() => {
        expect(screen.getAllByText('USD')[0]).toBeInTheDocument();
      }, { timeout: 3000 });

      // Verificar que ambas monedas se muestran
      expect(screen.getAllByText('USD').length).toBeGreaterThan(0);
      expect(screen.getAllByText('EUR').length).toBeGreaterThan(0);
    });

  // Flag emojis replaced by SVG icons; skip emoji assertions

    it('should display buy and sell rates when data loads', async () => {
      render(<ExchangeRatePanel />);
      
      await waitFor(() => {
        expect(screen.getAllByText(/\$38\.50/)[0]).toBeInTheDocument();
      }, { timeout: 3000 });

                    // Verificar tasas formateadas usando valores de fixtures
      expect(screen.getAllByText((content, element) => {
        return element && element.textContent && element.textContent.includes(EXPECTED_VALUES.STANDARD.USD_BUY);
      })[0]).toBeInTheDocument();
      expect(screen.getAllByText((content, element) => {
        return element && element.textContent && element.textContent.includes(EXPECTED_VALUES.STANDARD.USD_SELL);
      })[0]).toBeInTheDocument();
    });

  // Timestamp optional in new UX

  // Refresh button removed

  // Source acronym 'BCU' is part of title; explicit standalone assertion removed in new UX
  });

  // Refresh functionality removed; suite deleted

  describe('Rate Formatting', () => {
    it('should format rates with 2 decimals for values >= 1', async () => {
      // Usar datos de fixtures para formateo decimal
      const mockRatesWithDecimals = createMockRatesArray(TEST_EXCHANGE_RATES.DECIMAL_TESTING);

      mockExchangeService.getCurrentRates.mockResolvedValue({
        success: true,
        data: mockRatesWithDecimals
      });

      render(<ExchangeRatePanel />);

      await waitFor(() => {
        expect(screen.getAllByText((content, element) => {
          return element && element.textContent && element.textContent.includes(EXPECTED_VALUES.DECIMAL_FORMATTED.USD_BUY);
        })[0]).toBeInTheDocument();
        expect(screen.getAllByText((content, element) => {
          return element && element.textContent && element.textContent.includes(EXPECTED_VALUES.DECIMAL_FORMATTED.USD_SELL);
        })[0]).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    it('should format rates with 4 decimals for values < 1', async () => {
      // Usar datos de fixtures para valores pequeños
      const ratesWithSmallValues = createMockRatesArray(TEST_EXCHANGE_RATES.SMALL_VALUES);

      mockExchangeService.getCurrentRates.mockResolvedValue({
        success: true,
        data: ratesWithSmallValues
      });

      render(<ExchangeRatePanel />);

      await waitFor(() => {
        expect(screen.getAllByText((content, element) => {
          return element && element.textContent && element.textContent.includes(EXPECTED_VALUES.SMALL_FORMATTED.ARS_BUY);
        })[0]).toBeInTheDocument();
        expect(screen.getAllByText((content, element) => {
          return element && element.textContent && element.textContent.includes(EXPECTED_VALUES.SMALL_FORMATTED.ARS_SELL);
        })[0]).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    it('should handle equal buy and sell rates', async () => {
      // Usar datos de fixtures para tasas iguales
      const ratesWithEqualValues = createMockRatesArray(TEST_EXCHANGE_RATES.EQUAL_RATES);

      mockExchangeService.getCurrentRates.mockResolvedValue({
        success: true,
        data: ratesWithEqualValues
      });

      render(<ExchangeRatePanel />);

      await waitFor(() => {
        expect(screen.getAllByText((content, element) => {
          return element && element.textContent && element.textContent.includes(EXPECTED_VALUES.EQUAL_RATES.USD);
        })[0]).toBeInTheDocument();
      }, { timeout: 3000 });

      // Should not show separate buy/sell rates
      const separators = screen.queryAllByText('-');
      expect(separators.length).toBe(0);
    });
  });

  describe('Responsive Layout', () => {
    beforeEach(() => {
      mockExchangeService.getCurrentRates.mockResolvedValue({
        success: true,
        data: mockRatesData
      });
    });

          it('should show desktop layout elements', async () => {
        mockExchangeService.getCurrentRates.mockResolvedValue({
          success: true,
          data: mockRatesData
        });

        render(<ExchangeRatePanel />);

        await waitFor(() => {
          expect(screen.getAllByText((content, element) => {
            return element && element.textContent && element.textContent.includes(EXPECTED_VALUES.STANDARD.USD_BUY);
          })[0]).toBeInTheDocument();
        }, { timeout: 3000 });

        // Desktop layout should have specific structure
  expect(screen.getAllByText(/Cotizaciones BCU/)[0]).toBeInTheDocument();
      });

    it('should limit display to first 4 currencies', async () => {
      // Usar datos de fixtures estándar + monedas adicionales
      const manyRates = [
        ...DEFAULT_MOCK_RATES, // Usar las 4 monedas estándar
        { currency: 'CLP', buy_rate: 0.05, sell_rate: 0.06, average_rate: 0.055 },
        { currency: 'GBP', buy_rate: 50.00, sell_rate: 53.00, average_rate: 51.50 }
      ];

      mockExchangeService.getCurrentRates.mockResolvedValue({
        success: true,
        data: manyRates
      });

      render(<ExchangeRatePanel />);

      await waitFor(() => {
        expect(screen.getAllByText('USD')[0]).toBeInTheDocument();
      }, { timeout: 3000 });

      // Should show first 4 currencies
      expect(screen.getAllByText('USD').length).toBeGreaterThan(0);
      expect(screen.getAllByText('EUR').length).toBeGreaterThan(0);
      expect(screen.getAllByText('ARS').length).toBeGreaterThan(0);
      expect(screen.getAllByText('BRL').length).toBeGreaterThan(0);
      
      // Should not show 5th and 6th currencies
      expect(screen.queryByText('CLP')).not.toBeInTheDocument();
      expect(screen.queryByText('GBP')).not.toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty data array', async () => {
      mockExchangeService.getCurrentRates.mockResolvedValue({
        success: true,
        data: []
      });

      render(<ExchangeRatePanel />);

      await waitFor(() => {
        expect(screen.getAllByText(/Cotizaciones BCU/)[0]).toBeInTheDocument();
      }, { timeout: 3000 });

      // Should show title but no currencies
      expect(screen.queryByText('USD')).not.toBeInTheDocument();
    });

    it('should handle currency without display configuration', async () => {
      // Usar datos de fixtures para moneda desconocida
      const unknownCurrencyData = createMockRatesArray(TEST_EXCHANGE_RATES.UNKNOWN_CURRENCY);

      mockExchangeService.getCurrentRates.mockResolvedValue({
        success: true,
        data: unknownCurrencyData
      });

      render(<ExchangeRatePanel />);

      await waitFor(() => {
        expect(screen.getAllByText(/Cotizaciones BCU/)[0]).toBeInTheDocument();
      }, { timeout: 3000 });

      // Should not render unknown currency
      expect(screen.queryByText('XYZ')).not.toBeInTheDocument();
    });

    it('should handle missing rate values', async () => {
      // Usar datos de fixtures para datos incompletos
      const incompleteData = createMockRatesArray(TEST_EXCHANGE_RATES.INCOMPLETE_DATA);

      mockExchangeService.getCurrentRates.mockResolvedValue({
        success: true,
        data: incompleteData
      });

      render(<ExchangeRatePanel />);

      await waitFor(() => {
        expect(screen.getAllByText('USD')[0]).toBeInTheDocument();
      }, { timeout: 3000 });

      // Should still render currency even with missing values
      expect(screen.getAllByText('USD').length).toBeGreaterThan(0);
    });

    it('should handle very large numbers', async () => {
      // Usar datos de fixtures para números grandes
      const largeNumberData = createMockRatesArray(TEST_EXCHANGE_RATES.LARGE_VALUES);

      mockExchangeService.getCurrentRates.mockResolvedValue({
        success: true,
        data: largeNumberData
      });

      render(<ExchangeRatePanel />);

      await waitFor(() => {
        expect(screen.getAllByText('USD')[0]).toBeInTheDocument();
      }, { timeout: 3000 });

      // Should format large numbers correctly
      expect(screen.getAllByText((content, element) => {
        return element && element.textContent && element.textContent.includes(EXPECTED_VALUES.LARGE_VALUES.USD_BUY);
      })[0]).toBeInTheDocument();
    });
  });

  // Time formatting test removed (timestamp optional)
});