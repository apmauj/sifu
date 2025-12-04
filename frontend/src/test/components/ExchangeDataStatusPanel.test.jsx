import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import ExchangeDataStatusPanel from '../../features/exchange/ExchangeDataStatusPanel';

// Mock i18n
const t = (k) => {
  const map = {
    'common.loading': 'Cargando información...',
    'exchange.data_status_title': 'Estado de los datos de Cotizaciones',
    'common.records': 'registros',
    'exchange.available': 'disponibles',
    'common.period': 'Período',
    'exchange.currencies_label': 'Monedas',
    'exchange.latest_day': 'Último día disponible',
    'exchange.source_note': 'Fuente: INE (histórico, último día hábil publicado)',
    'exchange.status_error': 'Error al cargar estado de cotizaciones'
  };
  return map[k] || k;
};

vi.mock('../../shared/contexts/I18nContext', () => ({
  useI18n: () => ({
    t
  })
}));

// Mock service
vi.mock('../../shared/services/exchangeService', () => {
  const getInfoMock = vi.fn();
  return {
    __esModule: true,
    default: { getInfo: getInfoMock }
  };
});

let getInfoMock;
beforeEach(async () => {
  const { default: exchangeService } = await import('../../shared/services/exchangeService');
  getInfoMock = exchangeService.getInfo;
  getInfoMock.mockReset();
});

const sampleInfo = {
  total_records: 1234,
  date_range: { min_date: '2020-01-02', max_date: '2025-08-15' },
  available_currencies: ['USD', 'EUR', 'ARS', 'BRL']
};

describe('ExchangeDataStatusPanel', () => {

  it('shows loading text initially', () => {
    getInfoMock.mockImplementation(() => new Promise(() => {}));
    render(<ExchangeDataStatusPanel />);
    expect(screen.getByText('Cargando información...')).toBeInTheDocument();
  });

  it('renders data status info on success', async () => {
    getInfoMock.mockResolvedValue(sampleInfo);
    render(<ExchangeDataStatusPanel />);
    // Wait for the formatted number to appear (handles both 1,234 and 1.234 formats)
    await waitFor(() => expect(screen.getByText(/1[,.]234/)).toBeInTheDocument());
    // Heading contains an emoji prefix and extra whitespace; match by regex substring
    expect(screen.getByText(/Estado de los datos de Cotizaciones/)).toBeInTheDocument();
    // Dates appear in separate spans; assert individually
    expect(screen.getByText(/2020-01-02/)).toBeInTheDocument();
    expect(screen.getAllByText(/2025-08-15/).length).toBeGreaterThan(0); // appears twice (range + latest)
    // Currencies line has bullet and variable spacing around colon
    expect(screen.getByText(/Monedas\s*:.*USD, EUR, ARS, BRL/)).toBeInTheDocument();
  });

  it('renders error state', async () => {
    getInfoMock.mockResolvedValue({ total_records: 0 });
    render(<ExchangeDataStatusPanel />);
    await waitFor(() => expect(screen.getByText('Error al cargar estado de cotizaciones')).toBeInTheDocument());
  });
});
