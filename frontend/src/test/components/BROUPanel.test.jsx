import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import BROUPanel from '../../features/brou/BROUPanel';

// Mock i18n context (return deterministic Spanish strings)
vi.mock('../../shared/contexts/I18nContext', () => ({
  useI18n: () => ({
    t: (k) => {
      const map = {
        'brou.title': 'BROU',
        'brou.bank_name': 'Banco República',
        'brou.loading': 'Cargando cotizaciones...',
        'brou.retry': 'Reintentar',
        'brou.error_loading': 'Error al cargar cotizaciones',
        'brou.currencies.USD': 'Dólar USA',
        'brou.currencies.USD_EBROU': 'Dólar eBROU',
        'brou.currencies.EUR': 'Euro',
        'brou.currencies.ARS': 'Peso Arg.',
        'brou.currencies.BRL': 'Real',
        'brou.buy': 'Compra',
        'brou.sell': 'Venta',
        'brou.arbitrage_buy': 'Arbitraje Compra',
        'brou.arbitrage_sell': 'Arbitraje Venta',
        'brou.preferential': 'Preferencial',
        'brou.source_footer': 'Fuente: BROU • Actualización cada hora',
        'brou.arbitrage_footer': 'Arbitrajes calculados vs USD',
        'common.refresh': 'Actualizar Datos',
        'common.refresh_data': 'Actualizar Datos',
        'common.loading': 'Cargando...'
      };
      return map[k] || k;
    }
  })
}));

// Mock toast context (no-op implementations)
vi.mock('../../shared/contexts/ToastContext', () => ({
  useToast: () => ({ showSuccess: vi.fn(), showError: vi.fn() })
}));

// Mock hourly hook so it does not schedule intervals; call function once after mount
vi.mock('../../shared/hooks/useHourlySyncedUpdate', () => ({
  useHourlySyncedUpdate: (fn) => fn
}));

// Service mock
const getCurrentMock = vi.fn();
vi.mock('../../shared/services/brouService', () => ({
  default: { getCurrent: (...args) => getCurrentMock(...args) }
}));

// Mock data para respuestas completas con metadata
const mockFullResponse = {
  success: true,
  message: "Cotizaciones BROU obtenidas (4 monedas)",
  data: [
    {
      currency: "USD",
      buy_rate: 42.50,
      sell_rate: 42.80,
      average_rate: 42.65,
      arbitrage_buy: 0.1234,
      arbitrage_sell: 0.5678,
      preferential: false,
      source: "BROU",
      timestamp: "2025-09-21T17:30:00Z"
    }
  ],
  source: "BROU",
  source_type: "live",
  status: {
    label: "Datos en vivo",
    color: "green",
    description: "Cotizaciones obtenidas directamente del BROU"
  },
  timestamp: "2025-09-21T17:30:00Z",
  data_age_minutes: 15.5,
  is_fresh: true,
  frontend_display: {
    status_label: "Datos en vivo",
    status_color: "green",
    warning_message: null
  }
};

const mockStaleResponse = {
  ...mockFullResponse,
  source_type: "persisted",
  status: {
    label: "Datos históricos",
    color: "yellow",
    description: "Cotizaciones almacenadas de consultas anteriores"
  },
  data_age_minutes: 120.5,
  is_fresh: false,
  frontend_display: {
    status_label: "Datos históricos",
    status_color: "yellow",
    warning_message: "Los datos son históricos de consultas anteriores"
  }
};

const mockRatesData = [
  { currency: 'USD', buy_rate: 38.5, sell_rate: 41.5, arbitrage_buy: 0.025, arbitrage_sell: 0.018 },
  { currency: 'USD_EBROU', buy_rate: 39.2, sell_rate: 40.8, arbitrage_buy: 0.032, arbitrage_sell: 0.022 },
  { currency: 'EUR', buy_rate: 42.3, sell_rate: 45.7, arbitrage_buy: 0.041, arbitrage_sell: 0.038 }
];

const flush = () => new Promise(r => setTimeout(r, 0));

describe('BROUPanel', () => {
  beforeEach(() => {
    getCurrentMock.mockReset();
  });

  describe('Loading state', () => {
    it('shows loading spinner and text initially', () => {
      getCurrentMock.mockImplementation(() => new Promise(() => {})); // never resolves
      render(<BROUPanel />);
      expect(screen.getByText('BROU')).toBeInTheDocument();
      expect(screen.getByText('Cargando cotizaciones...')).toBeInTheDocument();
    });
  });

  describe('Error state', () => {
    it('renders error UI when service rejects', async () => {
      getCurrentMock.mockRejectedValue(new Error('Network fail'));
      render(<BROUPanel />);
      await waitFor(() => {
        expect(screen.getByText('Error al cargar cotizaciones')).toBeInTheDocument();
      });
      expect(screen.getByRole('button', { name: /reintentar/i })).toBeInTheDocument();
    });

    it('retries on click', async () => {
      getCurrentMock
        .mockRejectedValueOnce(new Error('Network fail'))
        .mockResolvedValueOnce({
          success: true,
          data: mockRatesData,
          source: "BROU",
          source_type: "live",
          status: { label: "Datos en vivo", color: "green" },
          frontend_display: { status_label: "Datos en vivo" }
        });
      render(<BROUPanel />);
      await screen.findByText('Error al cargar cotizaciones');
      fireEvent.click(screen.getByRole('button', { name: /reintentar/i }));
      await waitFor(() => {
        const usd = screen.getAllByText(/Dólar\s+USA/)[0];
        expect(usd).toBeInTheDocument();
      });
    });
  });

  describe('Success state', () => {
    beforeEach(() => {
      // Usar la estructura completa con metadata
      getCurrentMock.mockResolvedValue({
        success: true,
        data: mockRatesData,
        source: "BROU",
        source_type: "live",
        status: { label: "Datos en vivo", color: "green" },
        frontend_display: { status_label: "Datos en vivo" }
      });
    });

    it('renders table with currencies', async () => {
      render(<BROUPanel />);
      await waitFor(() => expect(screen.getAllByText(/Dólar\s+USA/)[0]).toBeInTheDocument());
      expect(screen.getByText('Banco República')).toBeInTheDocument();
      expect(screen.getAllByText('Euro').length).toBeGreaterThan(0);
    });

    // Manual refresh removed; ensure no refresh button rendered
    it('does not render manual refresh button (auto updates only)', async () => {
      render(<BROUPanel />);
      await waitFor(() => expect(screen.getAllByText(/Dólar\s+USA/)[0]).toBeInTheDocument());
      expect(screen.queryByRole('button', { name: /actualizar|refresh/i })).not.toBeInTheDocument();
    });
  });

  describe('Data formatting edge cases', () => {
    it('handles null values with dash', async () => {
      getCurrentMock.mockResolvedValue({
        success: true,
        data: [ { currency: 'USD', buy_rate: null, sell_rate: null, arbitrage_buy: null, arbitrage_sell: null } ],
        source: "BROU",
        source_type: "live",
        status: { label: "Datos en vivo", color: "green" },
        frontend_display: { status_label: "Datos en vivo" }
      });
      render(<BROUPanel />);
      await waitFor(() => expect(screen.getAllByText(/Dólar\s+USA/)[0]).toBeInTheDocument());
      expect(screen.getAllByText('-').length).toBeGreaterThan(0);
    });

    it('handles empty list gracefully (error path)', async () => {
      getCurrentMock.mockResolvedValue({
        success: false,
        data: [],
        message: "Error al cargar cotizaciones"
      });
      render(<BROUPanel />);
      await waitFor(() => {
        const errs = screen.getAllByText('Error al cargar cotizaciones');
        expect(errs.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Metadata functionality', () => {
    beforeEach(() => {
      getCurrentMock.mockClear();
    });

    it('calls service with full=true parameter', async () => {
      getCurrentMock.mockResolvedValue(mockFullResponse);
      render(<BROUPanel />);
      await waitFor(() => expect(screen.getByText('Datos en vivo')).toBeInTheDocument());
      expect(getCurrentMock).toHaveBeenCalledWith({ full: true });
    });

    it('displays status badge for live data', async () => {
      getCurrentMock.mockResolvedValue(mockFullResponse);
      render(<BROUPanel />);
      await waitFor(() => {
        expect(screen.getByText('Datos en vivo')).toBeInTheDocument();
        // Buscar el contenedor que tiene la información de frescura
        const freshnessContainer = screen.getByText(/✅/).parentElement;
        expect(freshnessContainer).toHaveTextContent('15.5 min');
      });
    });

    it('displays warning message for stale data', async () => {
      getCurrentMock.mockResolvedValue(mockStaleResponse);
      render(<BROUPanel />);
      await waitFor(() => {
        expect(screen.getByText('Datos históricos')).toBeInTheDocument();
        expect(screen.getByText('Los datos son históricos de consultas anteriores')).toBeInTheDocument();
        // Buscar el contenedor que tiene la información de frescura (el primero)
        const freshnessContainers = screen.getAllByText(/⚠️/);
        const freshnessContainer = freshnessContainers[0].parentElement;
        expect(freshnessContainer).toHaveTextContent('120.5 min');
      });
    });

    it('displays freshness info with timestamp', async () => {
      getCurrentMock.mockResolvedValue(mockFullResponse);
      render(<BROUPanel />);
      await waitFor(() => {
        // Buscar el contenedor que tiene la información de frescura
        const freshnessContainer = screen.getByText(/✅/).parentElement;
        expect(freshnessContainer).toHaveTextContent('15.5 min');
        expect(freshnessContainer).toHaveTextContent('•');
      });
    });

    it('handles backward compatibility with array response', async () => {
      getCurrentMock.mockResolvedValue(mockRatesData);
      render(<BROUPanel />);
      await waitFor(() => expect(screen.getAllByText(/Dólar\s+USA/)[0]).toBeInTheDocument());
      // No debería mostrar badge de estado para respuesta antigua
      expect(screen.queryByText('Datos en vivo')).not.toBeInTheDocument();
      expect(screen.queryByText('Datos históricos')).not.toBeInTheDocument();
    });

    it('handles missing metadata gracefully', async () => {
      const responseWithoutMetadata = {
        success: true,
        data: mockRatesData
      };
      getCurrentMock.mockResolvedValue(responseWithoutMetadata);
      render(<BROUPanel />);
      await waitFor(() => expect(screen.getAllByText(/Dólar\s+USA/)[0]).toBeInTheDocument());
      // No debería mostrar badge de estado si no hay metadata
      expect(screen.queryByText('Datos en vivo')).not.toBeInTheDocument();
    });
  });
});
