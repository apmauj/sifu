import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import URPanel from '../../components/URPanel';

vi.mock('../../shared/contexts/I18nContext', () => ({
  useI18n: () => ({
    t: (k) => ({
      'common.loading': 'Cargando información...',
      'common.period': 'Período',
      'common.not_available': 'N/D',
      'ur.records': 'registros',
      'ur.latest_value': 'Último valor disponible',
      'ur.query_error': 'Error al cargar información de UR',
      'ur.january': 'enero',
      'ur.february': 'febrero',
      'ur.march': 'marzo',
      'ur.april': 'abril',
      'ur.may': 'mayo',
      'ur.june': 'junio',
      'ur.july': 'julio',
      'ur.august': 'agosto',
      'ur.september': 'septiembre',
      'ur.october': 'octubre',
      'ur.november': 'noviembre',
      'ur.december': 'diciembre'
    })[k] || k,
    currentLanguage: 'es'
  })
}));

const getInfoMock = vi.fn();
const getByYearMonthMock = vi.fn();

vi.mock('../../services/urService', () => ({
  __esModule: true,
  default: {
    getInfo: (...a) => getInfoMock(...a),
    getByYearMonth: (...a) => getByYearMonthMock(...a)
  }
}));

describe('URPanel', () => {
  beforeEach(() => {
    getInfoMock.mockReset();
    getByYearMonthMock.mockReset();
  });

  it('loads and displays UR status with latest value', async () => {
    getInfoMock.mockResolvedValue({
      total_records: 50,
      year_range: { min_year: 2000, max_year: 2024 },
      latest_value: { year: 2024, month: 8, value: 42.12 }
    });
    getByYearMonthMock.mockResolvedValue({ success: true });

  render(<URPanel />);
  // Multiple occurrences (panel + select option) allowed
  expect(screen.getAllByText('Cargando información...').length).toBeGreaterThan(0);
    await waitFor(() => expect(screen.getByText(/Estado de los datos UR/)).toBeInTheDocument());
    expect(screen.getByText(/50/)).toBeInTheDocument();
  expect(screen.getAllByText(/2000/).length).toBeGreaterThan(0);
  expect(screen.getAllByText(/2024/).length).toBeGreaterThan(0);
    // Latest value formatted line contains the month name
    await waitFor(() => expect(getByYearMonthMock).toHaveBeenCalledWith(2024, 8));
  });

  it('shows error when missing records', async () => {
    getInfoMock.mockResolvedValue({ total_records: 0 });
    render(<URPanel />);
    await waitFor(() => expect(screen.getByText('Error al cargar información de UR')).toBeInTheDocument());
  });
});
