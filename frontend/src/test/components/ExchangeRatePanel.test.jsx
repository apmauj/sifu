import React from 'react';
import { render, screen, waitFor, act, fireEvent } from '@testing-library/react';
import ExchangeRatePanel from '../../components/ExchangeRatePanel';
import { vi } from 'vitest';

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
    resetMock(); // Reset del mock del hook
    mockExchangeService = (await import('../../services/exchangeService')).default;
  });

  describe('Loading State', () => {
    it('should show loading message initially', async () => {
      mockExchangeService.getCurrentRates.mockImplementation(() => new Promise(() => {})); // Never resolves
      
      render(<ExchangeRatePanel />);
      
      expect(screen.getByText('📈 Cargando cotizaciones...')).toBeInTheDocument();
    });

    it('should apply correct loading styling', async () => {
      mockExchangeService.getCurrentRates.mockImplementation(() => new Promise(() => {})); // Never resolves

      render(<ExchangeRatePanel />);
      
      const loadingElement = screen.getByText('📈 Cargando cotizaciones...');
      expect(loadingElement).toBeInTheDocument();
      
      // Find the parent div with the correct classes
      const parentDiv = loadingElement.closest('.bg-gray-800');
      expect(parentDiv).toHaveClass('bg-gray-800', 'text-white');
    });

    it('should not show loading when data is already present', async () => {
      mockExchangeService.getCurrentRates.mockResolvedValue({
        success: true,
        data: mockRatesData
      });

      render(<ExchangeRatePanel />);

      await waitFor(() => {
        expect(screen.queryByText('📈 Cargando cotizaciones...')).not.toBeInTheDocument();
      }, { timeout: 3000 });
    });
  });

  describe('Error State', () => {
    it('should show error message when API fails', async () => {
      const errorMessage = 'Error de conexión';
      mockExchangeService.getCurrentRates.mockRejectedValue(new Error(errorMessage));

      render(<ExchangeRatePanel />);

      await waitFor(() => {
        expect(screen.getByText('❌ Error de conexión')).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    it('should show retry button in error state', async () => {
      mockExchangeService.getCurrentRates.mockRejectedValue(new Error('Network error'));

      render(<ExchangeRatePanel />);

      await waitFor(() => {
        const retryButton = screen.getByText('Reintentar');
        expect(retryButton).toBeInTheDocument();
        expect(retryButton.tagName).toBe('BUTTON');
      }, { timeout: 3000 });
    });

    it('should retry fetch when retry button is clicked', async () => {
      // First call fails
      mockExchangeService.getCurrentRates
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          success: true,
          data: mockRatesData
        });

      render(<ExchangeRatePanel />);

      // Wait for error state
      await waitFor(() => {
        expect(screen.getByText('❌ Error de conexión')).toBeInTheDocument();
      }, { timeout: 3000 });

      // Click retry button
      const retryButton = screen.getByText('Reintentar');
      await act(async () => {
        fireEvent.click(retryButton);
      });

      // Should show data after retry
      await waitFor(() => {
        expect(screen.getAllByText('USD')[0]).toBeInTheDocument();
      }, { timeout: 3000 });

      expect(mockExchangeService.getCurrentRates).toHaveBeenCalledTimes(2);
    });

    it('should handle API response with success: false', async () => {
      mockExchangeService.getCurrentRates.mockResolvedValue({
        success: false,
        message: 'API service unavailable'
      });

      render(<ExchangeRatePanel />);

      await waitFor(() => {
        expect(screen.getByText('❌ Error de conexión')).toBeInTheDocument();
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
      expect(screen.getByText('📈 Cargando cotizaciones...')).toBeInTheDocument();
      
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

    it('should display currency flags when data loads', async () => {
      render(<ExchangeRatePanel />);
      
      await waitFor(() => {
        expect(screen.getAllByText('🇺🇸')[0]).toBeInTheDocument();
      }, { timeout: 3000 });

      expect(screen.getAllByText('🇺🇸').length).toBeGreaterThan(0);
      expect(screen.getAllByText('🇪🇺').length).toBeGreaterThan(0);
    });

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

    it('should display timestamp when data loads', async () => {
      render(<ExchangeRatePanel />);
      
      await waitFor(() => {
        expect(screen.getAllByText('USD')[0]).toBeInTheDocument();
      }, { timeout: 3000 });

      // Should show timestamp in format HH:MM
      const timeElements = screen.getAllByText(/\d{2}:\d{2}/);
      expect(timeElements.length).toBeGreaterThan(0);
    });

    it('should display refresh button when data loads', async () => {
      render(<ExchangeRatePanel />);
      
      await waitFor(() => {
        expect(screen.getAllByText('USD')[0]).toBeInTheDocument();
      }, { timeout: 3000 });

              const refreshButtons = screen.getAllByTitle(/Reintentar/);
      expect(refreshButtons.length).toBeGreaterThan(0);
    });

    it('should display source information', async () => {
      render(<ExchangeRatePanel />);
      
      await waitFor(() => {
        expect(screen.getAllByText('BCU')[0]).toBeInTheDocument();
      }, { timeout: 3000 });
    });
  });

  describe('Refresh Functionality', () => {
    beforeEach(() => {
      mockExchangeService.getCurrentRates.mockResolvedValue({
        success: true,
        data: mockRatesData
      });
    });

    it('should refresh data when refresh button is clicked', async () => {
      render(<ExchangeRatePanel />);

      await waitFor(() => {
        expect(screen.getAllByText('USD')[0]).toBeInTheDocument();
      }, { timeout: 3000 });

      const refreshButton = screen.getAllByTitle(/Reintentar/)[0];
      
      await act(async () => {
        fireEvent.click(refreshButton);
      });

      // Should call the service again
      expect(mockExchangeService.getCurrentRates).toHaveBeenCalledTimes(2);
    });

    it('should disable refresh button while loading', async () => {
      // Mock to return a long-running promise
      let resolvePromise;
      const longPromise = new Promise((resolve) => {
        resolvePromise = resolve;
      });
      
      mockExchangeService.getCurrentRates
        .mockResolvedValueOnce({
          success: true,
          data: mockRatesData
        })
        .mockReturnValueOnce(longPromise);

      render(<ExchangeRatePanel />);

      await waitFor(() => {
        expect(screen.getAllByText('USD')[0]).toBeInTheDocument();
      }, { timeout: 3000 });

      const refreshButton = screen.getAllByTitle(/Reintentar/)[0];
      
      await act(async () => {
        fireEvent.click(refreshButton);
      });

      // Button should be disabled during loading
      expect(refreshButton).toBeDisabled();
      expect(refreshButton.textContent).toBe('⟳');

      // Resolve the promise
      await act(async () => {
        resolvePromise({
          success: true,
          data: mockRatesData
        });
      });

      await waitFor(() => {
        expect(refreshButton).not.toBeDisabled();
        expect(refreshButton.textContent).toBe('🔄');
      });
    });

    it('should handle refresh button click', async () => {
      mockExchangeService.getCurrentRates
        .mockResolvedValueOnce({
          success: true,
          data: mockRatesData
        })
        .mockResolvedValueOnce({
          success: true,
          data: mockRatesData
        });

      render(<ExchangeRatePanel />);

      await waitFor(() => {
        expect(screen.getAllByText((content, element) => {
          return element && element.textContent && element.textContent.includes(EXPECTED_VALUES.STANDARD.USD_BUY);
        })[0]).toBeInTheDocument();
      }, { timeout: 3000 });

      const refreshButton = screen.getAllByTitle(/Reintentar/)[0];
      
      await act(async () => {
        fireEvent.click(refreshButton);
      });

      expect(mockExchangeService.getCurrentRates).toHaveBeenCalledTimes(2);
    });
  });

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
        const container = screen.getAllByText('📈 Cotizaciones BCU')[0].closest('.container');
        expect(container).toBeInTheDocument();
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

  describe('Time Formatting', () => {
    it('should format time in 24-hour format', async () => {
      mockExchangeService.getCurrentRates.mockResolvedValue({
        success: true,
        data: mockRatesData
      });

      render(<ExchangeRatePanel />);

      await waitFor(() => {
        expect(screen.getAllByText('USD')[0]).toBeInTheDocument();
      }, { timeout: 3000 });

      // Should show time in HH:MM format (24-hour)
      const timeElements = screen.getAllByText(/\d{2}:\d{2}/);
      expect(timeElements.length).toBeGreaterThan(0);
      
      // Verify it's not 12-hour format (no AM/PM)
      expect(screen.queryByText(/AM|PM/)).not.toBeInTheDocument();
    });
  });
}); 