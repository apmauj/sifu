import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import UIPanel from '../../features/ui/UIPanel';

vi.mock('../../shared/contexts/I18nContext', () => ({
  useI18n: () => ({
    t: (k) => ({
      'common.loading': 'Cargando información...',
      'common.records': 'registros',
      'common.period': 'Período',
      'common.not_available': 'N/D',
      'ui.data_status': 'Estado de los datos UI',
      'ui.available': 'disponibles',
      'ui.latest_value': 'Último valor disponible',
      'errors.search_data_error': 'Error al cargar'
    })[k] || k,
    currentLanguage: 'es'
  })
}));

const getInfoMock = vi.fn();
const getByDateMock = vi.fn();

vi.mock('../../shared/services/api', () => ({
  __esModule: true,
  default: {
    getInfo: (...a) => getInfoMock(...a),
    getByDate: (...a) => getByDateMock(...a)
  }
}));

describe('UIPanel', () => {
  beforeEach(() => {
    getInfoMock.mockReset();
    getByDateMock.mockReset();
  });

  it('loads today if within range otherwise falls back to latest', async () => {
    // Caso: hoy fuera del rango (simular fecha futura > max_date) → debe usar latest_ui.date
    getInfoMock.mockResolvedValue({
      total_records: 10,
      date_range: { min_date: '2024-01-01', max_date: '2024-02-01' },
      latest_ui: { value: 123.4567, date: '2024-02-01' }
    });
    getByDateMock.mockResolvedValue({ success: true, value: 123.4567, date: '2024-02-01' });

    render(<UIPanel />);
    expect(screen.getByText('Cargando información...')).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText(/Estado de los datos UI/)).toBeInTheDocument());
    await waitFor(() => expect(getByDateMock).toHaveBeenCalledWith('2024-02-01'));
  });

  it('renders error state when info missing', async () => {
    getInfoMock.mockResolvedValue({ total_records: 0 });
    render(<UIPanel />);
    await waitFor(() => {
      const err = screen.queryByText(/Error UI:.*Error al cargar/) || screen.queryByText(/Error al cargar/);
      expect(err).toBeInTheDocument();
    });
  });
});
