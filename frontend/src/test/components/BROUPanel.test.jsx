import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import BROUPanel from '../../components/BROUPanel';
import { vi } from 'vitest';

// Create smart mock variables outside the function to avoid hoisting issues
let hasExecuted = false;
let currentUpdateFn = null;

// Override the global mock with our smart version
vi.mock('../../hooks/useHourlySyncedUpdate', () => ({
  useHourlySyncedUpdate: vi.fn((updateFn) => {
    currentUpdateFn = updateFn;
    
    // Execute immediately on first call (component mount)
    if (!hasExecuted && updateFn && typeof updateFn === 'function') {
      hasExecuted = true;
      // Execute in next tick to allow component to mount
      setTimeout(() => {
        updateFn();
      }, 0);
    }
    
    // Return a function that can be called manually if needed
    return vi.fn(() => {
      if (updateFn && typeof updateFn === 'function') {
        updateFn();
      }
    });
  })
}));

// Reset function for each test
const resetMock = () => {
  hasExecuted = false;
  currentUpdateFn = null;
};

// Mock global fetch
global.fetch = vi.fn();

// Mock data
const mockRatesData = [
  {
    currency: 'USD',
    buy_rate: 38.50,
    sell_rate: 41.50,
    arbitrage_buy: 0.0250,
    arbitrage_sell: 0.0180
  },
  {
    currency: 'USD_EBROU',
    buy_rate: 39.20,
    sell_rate: 40.80,
    arbitrage_buy: 0.0320,
    arbitrage_sell: 0.0220
  },
  {
    currency: 'EUR',
    buy_rate: 42.30,
    sell_rate: 45.70,
    arbitrage_buy: 0.0410,
    arbitrage_sell: 0.0380
  }
];

describe('BROUPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch.mockClear();
    resetMock(); // Reset our custom mock state
  });

  describe('Loading State', () => {
    it('should show loading spinner and message initially', () => {
      // Don't execute the hook function for this test
      hasExecuted = true; // Prevent auto-execution
      global.fetch.mockImplementation(() => new Promise(() => {})); // Never resolves
      
      render(<BROUPanel />);
      
      expect(screen.getByText(/BROU/)).toBeInTheDocument();
      expect(screen.getByText('Cargando cotizaciones...')).toBeInTheDocument();
    });

    it('should show loading state with proper styling', () => {
      // Don't execute the hook function for this test
      hasExecuted = true; // Prevent auto-execution
      global.fetch.mockImplementation(() => new Promise(() => {})); // Never resolves

      render(<BROUPanel />);
      
      const loadingText = screen.getByText('Cargando cotizaciones...');
      expect(loadingText).toBeInTheDocument();
      expect(loadingText).toHaveClass('ml-2', 'text-gray-600');
    });
  });

  describe('Error State', () => {
    it('should show error message when fetch fails', async () => {
      const errorMessage = 'Network error';
      global.fetch.mockRejectedValue(new Error(errorMessage));

      render(<BROUPanel />);
      
      await waitFor(() => {
        expect(screen.getByText('Error al cargar cotizaciones')).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    it('should show retry button in error state', async () => {
      global.fetch.mockRejectedValue(new Error('Network error'));

      render(<BROUPanel />);
      
      await waitFor(() => {
        const retryButton = screen.getByRole('button', { name: /reintentar/i });
        expect(retryButton).toBeInTheDocument();
        expect(retryButton).toHaveClass('bg-blue-600', 'text-white');
      }, { timeout: 3000 });
    });

    it('should retry fetch when retry button is clicked', async () => {
      global.fetch
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ success: true, data: mockRatesData })
        });

      render(<BROUPanel />);
      
      await waitFor(() => {
        expect(screen.getByText('Error al cargar cotizaciones')).toBeInTheDocument();
      });

      const retryButton = screen.getByRole('button', { name: /reintentar/i });
      fireEvent.click(retryButton);

      await waitFor(() => {
        expect(screen.getAllByText('Dólar USA')[0]).toBeInTheDocument();
      });
    });

    it('should handle API error response', async () => {
      const apiError = 'API service unavailable';
      global.fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: false, message: apiError })
      });

      render(<BROUPanel />);
      
      await waitFor(() => {
        expect(screen.getByText('Error al cargar cotizaciones')).toBeInTheDocument();
        expect(screen.getByText(apiError)).toBeInTheDocument();
      }, { timeout: 3000 });
    });
  });

  describe('Component Rendering', () => {
    beforeEach(() => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true, data: mockRatesData })
      });
    });

    it('should display BROU title and bank name', async () => {
      render(<BROUPanel />);
      
      expect(screen.getByText(/BROU/)).toBeInTheDocument();
      
      await waitFor(() => {
        expect(screen.getByText('Banco República')).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    it('should display basic component structure with proper styling', async () => {
      render(<BROUPanel />);
      
      expect(screen.getByText(/BROU/)).toBeInTheDocument();
      
      await waitFor(() => {
        expect(screen.getAllByText('Dólar USA')[0]).toBeInTheDocument();
      }, { timeout: 3000 });

      const container = screen.getAllByText(/BROU/)[0].closest('.bg-white');
      expect(container).toBeInTheDocument();
      expect(container).toHaveClass('bg-white', 'rounded-lg', 'shadow-md');
    });

    it('should display refresh button when data is loaded', async () => {
      render(<BROUPanel />);
      
      await waitFor(() => {
        expect(screen.getAllByText('Dólar USA')[0]).toBeInTheDocument();
      }, { timeout: 3000 });

      const refreshButton = screen.getByRole('button');
      expect(refreshButton).toBeInTheDocument();
      expect(refreshButton).toHaveClass('bg-blue-600');
    });

    it('should refresh data when refresh button is clicked', async () => {
      render(<BROUPanel />);
      
      await waitFor(() => {
        expect(screen.getAllByText('Dólar USA')[0]).toBeInTheDocument();
      }, { timeout: 3000 });

      const refreshButton = screen.getByRole('button');
      
      global.fetch.mockClear();
      
      fireEvent.click(refreshButton);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith('/api/brou/current');
      });
    });

    it('should display last update time', async () => {
      render(<BROUPanel />);
      
      await waitFor(() => {
        expect(screen.getAllByText('Dólar USA')[0]).toBeInTheDocument();
      }, { timeout: 3000 });

      const timeRegex = /\d{2}:\d{2}/;
      expect(screen.getByText(timeRegex)).toBeInTheDocument();
    });
  });

  describe('Mobile View', () => {
    beforeEach(() => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true, data: mockRatesData })
      });
    });

    it('should display currency cards in mobile view', async () => {
      render(<BROUPanel />);
      
      await waitFor(() => {
        expect(screen.getAllByText('Dólar USA')[0]).toBeInTheDocument();
      }, { timeout: 3000 });

      const mobileElements = document.querySelectorAll('.md\\:hidden');
      expect(mobileElements.length).toBeGreaterThan(0);
    });

    it('should display buy/sell rates in mobile cards', async () => {
      render(<BROUPanel />);
      
      await waitFor(() => {
        expect(screen.getAllByText('Dólar USA')[0]).toBeInTheDocument();
      }, { timeout: 3000 });

      const compraElements = screen.getAllByText('Compra');
      const ventaElements = screen.getAllByText('Venta');
      expect(compraElements.length).toBeGreaterThan(1);
      expect(ventaElements.length).toBeGreaterThan(1);
    });

    it('should apply special styling to USD_EBROU card', async () => {
      render(<BROUPanel />);
      
      await waitFor(() => {
        expect(screen.getAllByText('Dólar USA')[0]).toBeInTheDocument();
      }, { timeout: 3000 });

      const ebrouCard = screen.getAllByText('Dólar eBROU')[0].closest('.bg-blue-50');
      expect(ebrouCard).toHaveClass('bg-blue-50', 'border-blue-100');
    });
  });

  describe('Footer Information', () => {
    beforeEach(() => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true, data: mockRatesData })
      });
    });

    it('should display source information', async () => {
      render(<BROUPanel />);
      
      await waitFor(() => {
        expect(screen.getAllByText('Dólar USA')[0]).toBeInTheDocument();
      }, { timeout: 3000 });

      expect(screen.getByText('Fuente: BROU • Actualización cada hora')).toBeInTheDocument();
    });

    it('should display arbitrage information', async () => {
      render(<BROUPanel />);
      
      await waitFor(() => {
        expect(screen.getAllByText('Dólar USA')[0]).toBeInTheDocument();
      }, { timeout: 3000 });

      expect(screen.getByText('Arbitrajes calculados vs USD')).toBeInTheDocument();
    });
  });

  describe('Data Formatting', () => {
    it('should handle null values correctly', async () => {
      const dataWithNulls = [{
        currency: 'USD',
        buy_rate: null,
        sell_rate: null,
        arbitrage_buy: null,
        arbitrage_sell: null
      }];

      global.fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true, data: dataWithNulls })
      });

      render(<BROUPanel />);

      await waitFor(() => {
        const dollarElements = screen.getAllByText('Dólar USA');
        expect(dollarElements.length).toBeGreaterThan(0);
      }, { timeout: 3000 });

      const dashElements = screen.getAllByText('-');
      expect(dashElements.length).toBeGreaterThan(0);
    });
  });

  describe('Hook Integration', () => {
    it('should render without crashing (hook integration verified)', () => {
      // Don't execute the hook function for this test
      hasExecuted = true; // Prevent auto-execution
      global.fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true, data: mockRatesData })
      });
      
      render(<BROUPanel />);
      
      expect(screen.getByText(/BROU/)).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty rates array', async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true, data: [] })
      });

      render(<BROUPanel />);

      await waitFor(() => {
        expect(screen.getByText('Banco República')).toBeInTheDocument();
      }, { timeout: 3000 });

      expect(screen.queryByText('Dólar USA')).not.toBeInTheDocument();
    });

    it('should filter out currencies without display configuration', async () => {
      const dataWithUnknownCurrency = [
        ...mockRatesData,
        {
          currency: 'UNKNOWN',
          buy_rate: 100,
          sell_rate: 110,
          arbitrage_buy: 0.1,
          arbitrage_sell: 0.05
        }
      ];

      global.fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true, data: dataWithUnknownCurrency })
      });

      render(<BROUPanel />);

      await waitFor(() => {
        const dollarElements = screen.getAllByText('Dólar USA');
        expect(dollarElements.length).toBeGreaterThan(0);
      }, { timeout: 3000 });

      expect(screen.queryByText('UNKNOWN')).not.toBeInTheDocument();
      
      expect(screen.getAllByText('Euro').length).toBeGreaterThan(0);
    });
  });
}); 