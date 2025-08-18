import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import ExchangeSearchForm from '../../components/ExchangeSearchForm';
import * as dateUtils from '../../utils/dateUtils';

// Mock del contexto I18n
const mockT = vi.fn((key, params) => {
  const translations = {
    'exchange.search_title': 'Consultar Cotizaciones',
    'exchange.latest_data': 'Últimos datos',
    'exchange.currency': 'Moneda',
    'exchange.all_currencies': 'Todas las monedas',
    'exchange.currencies.USD': 'Dólar estadounidense',
    'exchange.currencies.EUR': 'Euro',
    'exchange.currencies.ARS': 'Peso argentino',
    'exchange.currencies.BRL': 'Real brasileño',
    'common.quick_actions': 'Acciones rápidas',
    'common.last_week': 'Última semana',
    'common.last_month': 'Último mes',
    'exchange.search_type': 'Tipo de consulta',
    'exchange.latest': 'Últimas',
    'exchange.by_date': 'Por fecha',
    'exchange.by_range': 'Por rango',
    'exchange.history': 'Historial',
    'exchange.date': 'Fecha',
    'exchange.start_date': 'Fecha de inicio',
    'exchange.end_date': 'Fecha de fin',
    'exchange.history_limit': 'Cantidad de registros',
    'common.searching': 'Consultando...',
    'common.search': 'Consultar',
    'exchange.future_date': 'No se pueden seleccionar fechas futuras',
    'exchange.invalid_date_range': 'La fecha de inicio no puede ser mayor que la fecha de fin',
    'ui.date_required': 'La fecha es requerida',
    'ui.start_date_required': 'Las fechas son requeridas',
    'exchange.select_currency_for_history': 'Selecciona una moneda para ver el historial'
  };
  let result = translations[key] || key;
  if (params) {
    Object.keys(params).forEach(param => {
      result = result.replace(`{${param}}`, params[param]);
    });
  }
  return result;
});

vi.mock('../../contexts/I18nContext', () => ({
  useI18n: () => ({ t: mockT })
}));

// Mock de dateUtils
vi.mock('../../utils/dateUtils', () => ({
  getTodayLocal: vi.fn(() => '2025-01-15'),
  getDaysAgoLocal: vi.fn((days) => {
    const dates = { 7: '2025-01-08', 30: '2024-12-16' };
    return dates[days] || '2025-01-01';
  })
}));

// Mock de Heroicons para evitar dependencias externas
vi.mock('@heroicons/react/24/outline', () => ({
  ArrowPathIcon: () => <div />,
  ArrowDownIcon: () => <div />,
  ArrowUpIcon: () => <div />,
  MinusIcon: () => <div />,
  MagnifyingGlassIcon: () => <div />,
  XMarkIcon: () => <div />,
  CheckCircleIcon: () => <div />,
  ExclamationCircleIcon: () => <div />,
  InformationCircleIcon: () => <div />,
  ExclamationTriangleIcon: () => <div />,
  ChartBarIcon: () => <div />,
  CalendarIcon: () => <div />,
  ClockIcon: () => <div />,
  BanknotesIcon: () => <div />,
  CurrencyDollarIcon: () => <div />,
  GlobeAltIcon: () => <div />,
  MoonIcon: () => <div />,
  SunIcon: () => <div />
}));

describe('ExchangeSearchForm Component', () => {
  const mockOnSearch = vi.fn();
  const defaultProps = { onSearch: mockOnSearch, isLoading: false };

  beforeEach(() => {
    vi.clearAllMocks();
    dateUtils.getTodayLocal.mockReturnValue('2025-01-15');
    dateUtils.getDaysAgoLocal.mockImplementation((days) => {
      const dates = { 7: '2025-01-08', 30: '2024-12-16' };
      return dates[days] || '2025-01-01';
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Component Rendering', () => {
    it('renders headings and main sections', () => {
      render(<ExchangeSearchForm {...defaultProps} />);
      expect(screen.getByRole('heading', { name: /Consultar Cotizaciones/ })).toBeInTheDocument();
      expect(screen.getByText('Moneda')).toBeInTheDocument();
      expect(screen.getByText('Acciones rápidas')).toBeInTheDocument();
      expect(screen.getByText('Tipo de consulta')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Consultar/i })).toBeInTheDocument();
    });

    it('renders currency toggle buttons with correct initial states', () => {
      render(<ExchangeSearchForm {...defaultProps} />);
      expect(screen.getByRole('button', { name: /Todas las monedas/ })).toHaveAttribute('aria-pressed', 'true');
      // Buttons still have aria-label with original singular names, but visible text changed to plural
      ;['Dólar estadounidense', 'Euro', 'Peso argentino', 'Real brasileño'].forEach(name => {
        expect(screen.getByRole('button', { name: new RegExp(name) })).toHaveAttribute('aria-pressed', 'false');
      });
      // Visible plural texts present
      // Buttons now show currency codes (USD, EUR, ARS, BRL) not plural names
      ['USD','EUR','ARS','BRL'].forEach(code => {
        expect(screen.getByText(code)).toBeInTheDocument();
      });
    });

    it('renders quick action buttons', () => {
      render(<ExchangeSearchForm {...defaultProps} />);
      ['Últimos datos', 'Última semana', 'Último mes'].forEach(label => {
        expect(screen.getByRole('button', { name: new RegExp(label) })).toBeInTheDocument();
      });
    });

    it('renders search type buttons', () => {
      render(<ExchangeSearchForm {...defaultProps} />);
      ['Últimas', 'Por fecha', 'Por rango', 'Historial'].forEach(label => {
        expect(screen.getByText(label)).toBeInTheDocument();
      });
    });
  });

  describe('Search Type Selection', () => {
    it('starts with latest selected', () => {
      render(<ExchangeSearchForm {...defaultProps} />);
      expect(screen.getByText('Últimas')).toHaveClass('bg-blue-600');
    });

    it('switches to date type', () => {
      render(<ExchangeSearchForm {...defaultProps} />);
      fireEvent.click(screen.getByText('Por fecha'));
      expect(screen.getByLabelText('Fecha')).toBeInTheDocument();
    });

    it('switches to range type', () => {
      render(<ExchangeSearchForm {...defaultProps} />);
      fireEvent.click(screen.getByText('Por rango'));
      expect(screen.getByLabelText('Fecha de inicio')).toBeInTheDocument();
      expect(screen.getByLabelText('Fecha de fin')).toBeInTheDocument();
    });

    it('switches to history type', () => {
      render(<ExchangeSearchForm {...defaultProps} />);
      fireEvent.click(screen.getByText('Historial'));
      expect(screen.getByLabelText('Cantidad de registros')).toBeInTheDocument();
    });
  });

  describe('Currency Selection', () => {
    it('toggles USD selection', () => {
      render(<ExchangeSearchForm {...defaultProps} />);
      const usdBtn = screen.getByRole('button', { name: /Dólar estadounidense/ });
      fireEvent.click(usdBtn);
      expect(usdBtn).toHaveAttribute('aria-pressed', 'true');
  // Card results (not buttons) show plural; buttons show code
  expect(screen.getByText('USD')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Todas las monedas/ })).toHaveAttribute('aria-pressed', 'false');
    });

    it('does not show filtered message after selection (removed feature)', () => {
      render(<ExchangeSearchForm {...defaultProps} />);
      fireEvent.click(screen.getByRole('button', { name: /Euro/ }));
      expect(screen.queryByText(/Filtrado por/)).not.toBeInTheDocument();
    });
  });

  describe('Quick Actions', () => {
    it('handles latest quick action (ALL currency)', () => {
      render(<ExchangeSearchForm {...defaultProps} />);
      fireEvent.click(screen.getByRole('button', { name: /Últimos datos/ }));
      expect(mockOnSearch).toHaveBeenCalledWith({ type: 'latest', currency: null });
    });

    it('handles week quick action', () => {
      render(<ExchangeSearchForm {...defaultProps} />);
      fireEvent.click(screen.getByRole('button', { name: /Última semana/ }));
      expect(mockOnSearch).toHaveBeenCalledWith({
        type: 'range',
        startDate: '2025-01-08',
        endDate: '2025-01-15',
        currency: null
      });
    });

    it('includes selected currency in quick actions', () => {
      render(<ExchangeSearchForm {...defaultProps} />);
      fireEvent.click(screen.getByRole('button', { name: /Euro/ }));
      fireEvent.click(screen.getByRole('button', { name: /Últimos datos/ }));
      expect(mockOnSearch).toHaveBeenCalledWith({ type: 'latest', currency: 'EUR' });
    });

    it('disables quick actions while loading', () => {
      render(<ExchangeSearchForm {...defaultProps} isLoading={true} />);
      ['Últimos datos', 'Última semana', 'Último mes'].forEach(label => {
        expect(screen.getByRole('button', { name: new RegExp(label) })).toBeDisabled();
      });
    });
  });

  describe('Form Submission', () => {
    it('submits latest search', () => {
      render(<ExchangeSearchForm {...defaultProps} />);
      fireEvent.click(screen.getByRole('button', { name: /Consultar/i }));
      expect(mockOnSearch).toHaveBeenCalledWith({ type: 'latest', currency: null });
    });

    it('submits date search', () => {
      render(<ExchangeSearchForm {...defaultProps} />);
      fireEvent.click(screen.getByText('Por fecha'));
      fireEvent.click(screen.getByRole('button', { name: /Consultar/i }));
      expect(mockOnSearch).toHaveBeenCalledWith({ type: 'date', date: '2025-01-15', currency: null });
    });

    it('submits range search', () => {
      render(<ExchangeSearchForm {...defaultProps} />);
      fireEvent.click(screen.getByText('Por rango'));
      fireEvent.click(screen.getByRole('button', { name: /Consultar/i }));
      expect(mockOnSearch).toHaveBeenCalledWith({
        type: 'range',
        startDate: '2024-12-16',
        endDate: '2025-01-15',
        currency: null
      });
    });

    it('submits history search with selected currency', () => {
      render(<ExchangeSearchForm {...defaultProps} />);
      fireEvent.click(screen.getByRole('button', { name: /Dólar estadounidense/ }));
      fireEvent.click(screen.getByText('Historial'));
      fireEvent.click(screen.getByRole('button', { name: /Consultar/i }));
      expect(mockOnSearch).toHaveBeenCalledWith({ type: 'history', currency: 'USD', limit: 10 });
    });

    it('includes selected currency in submission (ARS)', () => {
      render(<ExchangeSearchForm {...defaultProps} />);
      fireEvent.click(screen.getByRole('button', { name: /Peso argentino/ }));
      fireEvent.click(screen.getByRole('button', { name: /Consultar/i }));
      expect(mockOnSearch).toHaveBeenCalledWith({ type: 'latest', currency: 'ARS' });
    });
  });

  describe('Validation', () => {
    it('errors on missing date', () => {
      render(<ExchangeSearchForm {...defaultProps} />);
      mockOnSearch.mockClear();
      fireEvent.click(screen.getByText('Por fecha'));
      const dateInput = screen.getByLabelText('Fecha');
      fireEvent.change(dateInput, { target: { value: '' } });
      fireEvent.click(screen.getByRole('button', { name: /Consultar/i }));
      expect(screen.getByText('La fecha es requerida')).toBeInTheDocument();
      expect(mockOnSearch).not.toHaveBeenCalled();
    });

    it('errors on missing range dates', () => {
      render(<ExchangeSearchForm {...defaultProps} />);
      mockOnSearch.mockClear();
      fireEvent.click(screen.getByText('Por rango'));
      const startDate = screen.getByLabelText('Fecha de inicio');
      fireEvent.change(startDate, { target: { value: '' } });
      fireEvent.click(screen.getByRole('button', { name: /Consultar/i }));
      expect(screen.getByText('Las fechas son requeridas')).toBeInTheDocument();
      expect(mockOnSearch).not.toHaveBeenCalled();
    });

    it('errors on invalid date range', () => {
      render(<ExchangeSearchForm {...defaultProps} />);
      mockOnSearch.mockClear();
      fireEvent.click(screen.getByText('Por rango'));
      fireEvent.change(screen.getByLabelText('Fecha de inicio'), { target: { value: '2025-01-15' } });
      fireEvent.change(screen.getByLabelText('Fecha de fin'), { target: { value: '2025-01-10' } });
      fireEvent.click(screen.getByRole('button', { name: /Consultar/i }));
      expect(screen.getByText('La fecha de inicio no puede ser mayor que la fecha de fin')).toBeInTheDocument();
      expect(mockOnSearch).not.toHaveBeenCalled();
    });

    it('keeps history disabled with ALL currency', () => {
      render(<ExchangeSearchForm {...defaultProps} />);
      mockOnSearch.mockClear();
      fireEvent.click(screen.getByText('Historial'));
      const submitButton = screen.getByRole('button', { name: /Consultar/i });
      expect(submitButton).toBeDisabled();
      fireEvent.click(submitButton);
      expect(mockOnSearch).not.toHaveBeenCalled();
    });
  });

  describe('Loading State', () => {
    it('shows loading state', () => {
      render(<ExchangeSearchForm {...defaultProps} isLoading={true} />);
      const btn = screen.getByRole('button', { name: /Consultando/i });
      expect(btn).toBeDisabled();
    });

    it('disables history when ALL selected', () => {
      render(<ExchangeSearchForm {...defaultProps} />);
      fireEvent.click(screen.getByText('Historial'));
      expect(screen.getByRole('button', { name: /Consultar/i })).toBeDisabled();
    });

    it('enables history when currency selected', () => {
      render(<ExchangeSearchForm {...defaultProps} />);
      fireEvent.click(screen.getByRole('button', { name: /Euro/ }));
      fireEvent.click(screen.getByText('Historial'));
      expect(screen.getByRole('button', { name: /Consultar/i })).not.toBeDisabled();
    });
  });

  describe('Inputs', () => {
    it('updates date input', () => {
      render(<ExchangeSearchForm {...defaultProps} />);
      fireEvent.click(screen.getByText('Por fecha'));
      const dateInput = screen.getByLabelText('Fecha');
      fireEvent.change(dateInput, { target: { value: '2025-01-10' } });
      expect(dateInput.value).toBe('2025-01-10');
    });

    it('updates range inputs', () => {
      render(<ExchangeSearchForm {...defaultProps} />);
      fireEvent.click(screen.getByText('Por rango'));
      const start = screen.getByLabelText('Fecha de inicio');
      const end = screen.getByLabelText('Fecha de fin');
      fireEvent.change(start, { target: { value: '2025-01-01' } });
      fireEvent.change(end, { target: { value: '2025-01-10' } });
      expect(start.value).toBe('2025-01-01');
      expect(end.value).toBe('2025-01-10');
    });

    it('updates history limit', () => {
      render(<ExchangeSearchForm {...defaultProps} />);
      fireEvent.click(screen.getByText('Historial'));
      const limit = screen.getByLabelText('Cantidad de registros');
      fireEvent.change(limit, { target: { value: '25' } });
      expect(limit.value).toBe('25');
    });

    it('enforces constraints', () => {
      render(<ExchangeSearchForm {...defaultProps} />);
      fireEvent.click(screen.getByText('Por fecha'));
      expect(screen.getByLabelText('Fecha')).toHaveAttribute('max', '2025-01-15');
      fireEvent.click(screen.getByText('Historial'));
      const limit = screen.getByLabelText('Cantidad de registros');
      expect(limit).toHaveAttribute('min', '1');
      expect(limit).toHaveAttribute('max', '365');
    });
  });

  describe('Edge Cases', () => {
    it('treats ALL currency as null on submit', () => {
      render(<ExchangeSearchForm {...defaultProps} />);
      fireEvent.click(screen.getByRole('button', { name: /Consultar/i }));
      expect(mockOnSearch).toHaveBeenCalledWith({ type: 'latest', currency: null });
    });

    it('initializes with correct defaults', () => {
      render(<ExchangeSearchForm {...defaultProps} />);
      expect(screen.getByText('Últimas')).toHaveClass('bg-blue-600');
      expect(screen.getByRole('button', { name: /Todas las monedas/ })).toHaveAttribute('aria-pressed', 'true');
    });

    it('calls date utils on mount', () => {
      render(<ExchangeSearchForm {...defaultProps} />);
      expect(dateUtils.getTodayLocal).toHaveBeenCalled();
      expect(dateUtils.getDaysAgoLocal).toHaveBeenCalledWith(30);
    });
  });
});