import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import URResultsDisplay from '../../components/URResultsDisplay';

// Mock de contexto I18n
vi.mock('../../contexts/I18nContext', () => ({
  useI18n: vi.fn(() => ({
    t: vi.fn((key) => {
      const translations = {
        'common.loading': 'Cargando...',
        'common.error': 'Error',
        'common.record': 'registro',
        'common.records': 'registros',
        'common.period': 'Período',
        'common.average': 'Promedio',
        'ur.no_results': 'No se encontraron valores de UR',
        'ur.no_results_hint': 'Intenta con otro período o usa los selectores rápidos',
        'ur.ur_value': 'Valor UR',
        'ur.ur_values': 'Valores UR',
        'ur.initial_value': 'Valor inicial',
        'ur.final_value': 'Valor final',
        'ur.total_variation': 'Variación total',
        'ur.ur_evolution': 'Evolución de la UR',
        'ur.monthly_percentage_variation': 'Variación Porcentual Mensual',
        'ur.variation_percentage': 'Variación %',
        'ur.variation_note': 'Muestra el cambio porcentual respecto al mes anterior',
        'ur.period_information': 'Información del Período',
        'ur.data_source': 'Fuente: Banco Hipotecario del Uruguay (BHU)',
        'ur.january': 'Enero',
        'ur.february': 'Febrero',
        'ur.march': 'Marzo',
        'ur.april': 'Abril',
        'ur.may': 'Mayo',
        'ur.june': 'Junio',
        'ur.july': 'Julio',
        'ur.august': 'Agosto',
        'ur.september': 'Septiembre',
        'ur.october': 'Octubre',
        'ur.november': 'Noviembre',
        'ur.december': 'Diciembre'
      };
      return translations[key] || key;
    }),
    translateBackendMessage: vi.fn((msg) => msg),
    currentLanguage: 'es'
  }))
}));

// Mock de recharts
vi.mock('recharts', () => ({
  LineChart: vi.fn(({ children, data }) => (
    <div data-testid="line-chart" data-chart-data={JSON.stringify(data)}>
      {children}
    </div>
  )),
  BarChart: vi.fn(({ children, data }) => (
    <div data-testid="bar-chart" data-chart-data={JSON.stringify(data)}>
      {children}
    </div>
  )),
  Line: vi.fn(({ dataKey, stroke }) => (
    <div data-testid={`line-${dataKey}`} data-stroke={stroke}></div>
  )),
  Bar: vi.fn(({ dataKey, fill }) => (
    <div data-testid={`bar-${dataKey}`} data-fill={fill}></div>
  )),
  XAxis: vi.fn(() => <div data-testid="x-axis"></div>),
  YAxis: vi.fn(() => <div data-testid="y-axis"></div>),
  CartesianGrid: vi.fn(() => <div data-testid="cartesian-grid"></div>),
  Tooltip: vi.fn(() => <div data-testid="tooltip"></div>),
  Legend: vi.fn(() => <div data-testid="legend"></div>),
  ResponsiveContainer: vi.fn(({ children }) => (
    <div data-testid="responsive-container">{children}</div>
  ))
}));

// Mock de heroicons
vi.mock('@heroicons/react/24/outline', () => ({
  ExclamationTriangleIcon: vi.fn(({ className }) => (
    <div data-testid="exclamation-triangle-icon" className={className}></div>
  )),
  MagnifyingGlassIcon: vi.fn(({ className }) => (
    <div data-testid="magnifying-glass-icon" className={className}></div>
  ))
}));

describe('URResultsDisplay Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  // ===== LOADING STATE TESTS =====
  describe('Loading State', () => {
    it('should display loading spinner and message when isLoading is true', () => {
      render(<URResultsDisplay isLoading={true} />);
      
      expect(screen.getByText('Cargando...')).toBeInTheDocument();
      const spinner = document.querySelector('.animate-spin');
      expect(spinner).toBeInTheDocument();
    });

    it('should display loading with proper styling', () => {
      render(<URResultsDisplay isLoading={true} />);
      
      const loadingContainer = screen.getByText('Cargando...').closest('div');
      expect(loadingContainer).toHaveClass('flex', 'items-center', 'justify-center');
    });
  });

  // ===== ERROR STATE TESTS =====
  describe('Error State', () => {
    it('should display error message when error prop is provided', () => {
      const errorMessage = 'Error al cargar valores UR';
      render(<URResultsDisplay error={errorMessage} />);
      
      expect(screen.getByText('Error')).toBeInTheDocument();
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
      expect(screen.getByTestId('exclamation-triangle-icon')).toBeInTheDocument();
    });

    it('should display error with proper styling', () => {
      render(<URResultsDisplay error="Test error" />);
      
      const errorContainer = screen.getByText('Test error').closest('.card');
      expect(errorContainer).toBeInTheDocument();
    });
  });

  // ===== NO RESULTS TESTS =====
  describe('No Results State', () => {
    it('should display no results message when results is null', () => {
      render(<URResultsDisplay results={null} />);
      
      expect(screen.getByText('No se encontraron valores de UR')).toBeInTheDocument();
      expect(screen.getByText('Intenta con otro período o usa los selectores rápidos')).toBeInTheDocument();
      expect(screen.getByTestId('magnifying-glass-icon')).toBeInTheDocument();
    });

    it('should display no results when results.success is false', () => {
      render(<URResultsDisplay results={{ success: false }} />);
      
      expect(screen.getByText('No se encontraron valores de UR')).toBeInTheDocument();
    });

    it('should display no results when results is undefined', () => {
      render(<URResultsDisplay results={undefined} />);
      
      expect(screen.getByText('No se encontraron valores de UR')).toBeInTheDocument();
    });
  });

  // ===== SINGLE VALUE DISPLAY TESTS =====
  describe('Single Value Display', () => {
    const singleValueResult = {
      success: true,
      data: {
        year: 2024,
        month: 1,
        value: 1234.56
      }
    };

      it('should display single UR value without charts/table', () => {
        render(<URResultsDisplay results={singleValueResult} searchType="single" />);
        expect(screen.getByText('Valor UR')).toBeInTheDocument();
        expect(screen.getByText('1.234,56')).toBeInTheDocument();
        expect(screen.getByText('Enero 2024')).toBeInTheDocument();
        expect(screen.queryByText('Información del Período')).not.toBeInTheDocument();
        expect(screen.queryByText('Evolución de la UR')).not.toBeInTheDocument();
    });

    it('should display formatted value correctly', () => {
      const result = {
        success: true,
        data: { year: 2024, month: 1, value: 1000.10 }
      };
      
      render(<URResultsDisplay results={result} searchType="single" />);
      
        expect(screen.getByText('1.000,10')).toBeInTheDocument();
    });

    it('should handle null value gracefully', () => {
      const result = {
        success: true,
        data: { year: 2024, month: 1, value: null }
      };
      
      render(<URResultsDisplay results={result} searchType="single" />);
      
      // Check for the text that actually appears (either translation or literal)
      const notAvailableText = screen.queryAllByText('N/D');
      const literalText = screen.queryAllByText('common.not_available');
      expect(notAvailableText.length + literalText.length).toBeGreaterThanOrEqual(2); // Appears in display and table
  // Should show at least one N/D (no table in single mode now)
  expect(screen.getAllByText('N/D').length).toBeGreaterThanOrEqual(1);
    });

    it('should display period without month when month is not provided', () => {
      const result = {
        success: true,
        data: { year: 2024, value: 1234.56 }
      };
      
      render(<URResultsDisplay results={result} searchType="single" />);
      
      expect(screen.getAllByText('2024')).toHaveLength(2); // Appears in display and table
  expect(screen.getByText('2024')).toBeInTheDocument();
    });
  });

  // ===== MULTIPLE VALUES DISPLAY TESTS =====
  describe('Multiple Values Display', () => {
    const multipleValuesResult = {
      success: true,
      data: [
        { year: 2024, month: 1, value: 1000.00 },
        { year: 2024, month: 2, value: 1100.00 },
        { year: 2024, month: 3, value: 1050.00 }
      ]
    };

    it('should display multiple UR values with statistics', () => {
      render(<URResultsDisplay results={multipleValuesResult} searchType="range" />);
      
      expect(screen.getByText('Valores UR')).toBeInTheDocument();
      expect(screen.getByText('3 registros')).toBeInTheDocument();
      expect(screen.getByText('Valor inicial')).toBeInTheDocument();
      expect(screen.getByText('Valor final')).toBeInTheDocument();
      expect(screen.getByText('Promedio')).toBeInTheDocument();
      expect(screen.getByText('Variación total')).toBeInTheDocument();
    });

    it('should calculate and display statistics correctly', () => {
      render(<URResultsDisplay results={multipleValuesResult} searchType="range" />);
      
      // Initial value: 1000.00
      expect(screen.getAllByText('1.000,00')).toHaveLength(2); // Appears in stats and table
      // Final value: 1050.00
      expect(screen.getAllByText('1.050,00')).toHaveLength(3); // Appears in stats (final + average) and table
      // Average: 1050.00
      expect(screen.getByText('Promedio')).toBeInTheDocument();
      // Total variation: +5.00%
      expect(screen.getByText('+5.00%')).toBeInTheDocument();
    });

    it('should display negative variation with proper styling', () => {
      const decreasingResult = {
        success: true,
        data: [
          { year: 2024, month: 1, value: 1100.00 },
          { year: 2024, month: 2, value: 1000.00 }
        ]
      };
      
      render(<URResultsDisplay results={decreasingResult} searchType="range" />);
      
      const variationElements = screen.getAllByText('-9.09%');
      expect(variationElements).toHaveLength(2); // Appears in stats and table
      expect(variationElements[0]).toHaveClass('text-red-600'); // Stats element
      expect(variationElements[1]).toHaveClass('text-red-600'); // Table element
    });

    it('should display positive variation with proper styling', () => {
      render(<URResultsDisplay results={multipleValuesResult} searchType="range" />);
      
      const variationElement = screen.getByText('+5.00%');
      expect(variationElement).toHaveClass('text-green-600');
    });
  });

  // ===== CHART FUNCTIONALITY TESTS =====
  describe('Chart Functionality', () => {
    const chartData = {
      success: true,
      data: [
        { year: 2024, month: 1, value: 1000.00 },
        { year: 2024, month: 2, value: 1100.00 }
      ]
    };

    it('should display line chart for multiple values', () => {
      render(<URResultsDisplay results={chartData} searchType="range" />);
      
      expect(screen.getByText('Evolución de la UR')).toBeInTheDocument();
      expect(screen.getByTestId('line-chart')).toBeInTheDocument();
      expect(screen.getAllByTestId('responsive-container')).toHaveLength(2); // Line and bar charts
    });

    it('should display bar chart for monthly variations', () => {
      render(<URResultsDisplay results={chartData} searchType="range" />);
      
      expect(screen.getByText('Variación Porcentual Mensual')).toBeInTheDocument();
      expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
      expect(screen.getByText('Muestra el cambio porcentual respecto al mes anterior')).toBeInTheDocument();
    });

    it('should not display charts for single value', () => {
      const singleResult = {
        success: true,
        data: { year: 2024, month: 1, value: 1000.00 }
      };
      
      render(<URResultsDisplay results={singleResult} searchType="single" />);
      
      expect(screen.queryByTestId('line-chart')).not.toBeInTheDocument();
      expect(screen.queryByTestId('bar-chart')).not.toBeInTheDocument();
    });

    it('should display chart components correctly', () => {
      render(<URResultsDisplay results={chartData} searchType="range" />);
      
      expect(screen.getAllByTestId('x-axis')).toHaveLength(2); // One for each chart
      expect(screen.getAllByTestId('y-axis')).toHaveLength(2);
      expect(screen.getAllByTestId('cartesian-grid')).toHaveLength(2);
      expect(screen.getAllByTestId('tooltip')).toHaveLength(2);
    });

    it('should have correct chart data structure', () => {
      render(<URResultsDisplay results={chartData} searchType="range" />);
      
      const lineChart = screen.getByTestId('line-chart');
      const chartDataAttr = lineChart.getAttribute('data-chart-data');
      const parsedData = JSON.parse(chartDataAttr);
      
      expect(parsedData).toHaveLength(2);
      expect(parsedData[0]).toHaveProperty('name', 'Enero 2024');
      expect(parsedData[0]).toHaveProperty('value', 1000.00);
    });
  });

  // ===== TABLE DISPLAY TESTS =====
  describe('Table Display', () => {
    const tableData = {
      success: true,
      data: [
        { year: 2024, month: 1, value: 1000.00 },
        { year: 2024, month: 2, value: 1100.00 },
        { year: 2024, month: 3, value: 1050.00 }
      ]
    };

    it('should display data table with correct headers', () => {
      render(<URResultsDisplay results={tableData} searchType="range" />);
      
      expect(screen.getByText('Información del Período')).toBeInTheDocument();
      expect(screen.getByText('Período')).toBeInTheDocument();
      expect(screen.getByText('Valor UR')).toBeInTheDocument();
      expect(screen.getByText('Variación %')).toBeInTheDocument();
    });

    it('should display table rows with correct data', () => {
      render(<URResultsDisplay results={tableData} searchType="range" />);
      
      expect(screen.getByText('Enero 2024')).toBeInTheDocument();
      expect(screen.getByText('Febrero 2024')).toBeInTheDocument();
      expect(screen.getByText('Marzo 2024')).toBeInTheDocument();
      expect(screen.getAllByText('1.000,00')).toHaveLength(2); // Appears in stats and table
      expect(screen.getAllByText('1.100,00')).toHaveLength(1);
      expect(screen.getAllByText('1.050,00')).toHaveLength(3); // Appears in stats (final + average) and table
    });

    it('should display variations in table correctly', () => {
      render(<URResultsDisplay results={tableData} searchType="range" />);
      
      // First row should have "-" for variation
      expect(screen.getByText('-')).toBeInTheDocument();
      // Second row should have positive variation
      expect(screen.getByText('+10.00%')).toBeInTheDocument();
      // Third row should have negative variation
      expect(screen.getByText('-4.55%')).toBeInTheDocument();
    });

    it('should not display variation column for single value', () => {
      const singleData = {
        success: true,
        data: { year: 2024, month: 1, value: 1000.00 }
      };
      
      render(<URResultsDisplay results={singleData} searchType="single" />);
      
      expect(screen.queryByText('Variación %')).not.toBeInTheDocument();
    });

    it('should apply alternating row colors', () => {
      render(<URResultsDisplay results={tableData} searchType="range" />);
      
      const table = screen.getByRole('table');
      const rows = table.querySelectorAll('tbody tr');
      
      expect(rows[0]).toHaveClass('bg-white');
      expect(rows[1]).toHaveClass('bg-gray-50');
      expect(rows[2]).toHaveClass('bg-white');
    });
  });

  // ===== FORMATTING TESTS =====
  describe('Data Formatting', () => {
    it('should format UR values with Spanish locale', () => {
      const result = {
        success: true,
        data: { year: 2024, month: 1, value: 1234567.89 }
      };
      
      render(<URResultsDisplay results={result} searchType="single" />);
      
      expect(screen.getAllByText('1.234.567,89')).toHaveLength(2); // Appears in display and table
  expect(screen.getByText('1.234.567,89')).toBeInTheDocument();
    });

    it('should format percentage with proper sign and decimals', () => {
      const result = {
        success: true,
        data: [
          { year: 2024, month: 1, value: 1000.00 },
          { year: 2024, month: 2, value: 1123.45 }
        ]
      };
      
      render(<URResultsDisplay results={result} searchType="range" />);
      
      // The percentage appears in both stats and table
      expect(screen.getAllByText('+12.35%')).toHaveLength(2);
    });

    it('should format period with month name and year', () => {
      const result = {
        success: true,
        data: { year: 2024, month: 12, value: 1000.00 }
      };
      
      render(<URResultsDisplay results={result} searchType="single" />);
      
      expect(screen.getAllByText('Diciembre 2024')[0]).toBeInTheDocument();
  expect(screen.getByText('Diciembre 2024')).toBeInTheDocument();
    });

    it('should handle edge case months correctly', () => {
      const result = {
        success: true,
        data: { year: 2024, month: 6, value: 1000.00 }
      };
      
      render(<URResultsDisplay results={result} searchType="single" />);
      
      expect(screen.getAllByText('Junio 2024')[0]).toBeInTheDocument();
  expect(screen.getByText('Junio 2024')).toBeInTheDocument();
    });
  });

  // ===== DATA SOURCE TESTS =====
  describe('Data Source', () => {
    it('should always display data source information', () => {
      const result = {
        success: true,
        data: { year: 2024, month: 1, value: 1000.00 }
      };
      
      render(<URResultsDisplay results={result} searchType="single" />);
      
      expect(screen.getByText('Fuente: Banco Hipotecario del Uruguay (BHU)')).toBeInTheDocument();
  expect(screen.getByText('Fuente: Banco Hipotecario del Uruguay (BHU)')).toBeInTheDocument();
    });
  });

  // ===== EDGE CASES TESTS =====
  describe('Edge Cases', () => {
    it('should handle empty data array', () => {
      const emptyResult = {
        success: true,
        data: []
      };
      
      render(<URResultsDisplay results={emptyResult} searchType="range" />);
      
      expect(screen.getByText('0 registros')).toBeInTheDocument();
    });

    it('should handle data with missing values', () => {
      const result = {
        success: true,
        data: [
          { year: 2024, month: 1, value: null },
          { year: 2024, month: 2, value: 1000.00 }
        ]
      };
      
      render(<URResultsDisplay results={result} searchType="range" />);
      
      // Check for the text that actually appears (either translation or literal)
      const notAvailableText = screen.queryAllByText('N/D');
      const literalText = screen.queryAllByText('common.not_available');
      expect(notAvailableText.length + literalText.length).toBeGreaterThanOrEqual(3); // In stats (avg, initial, final) and table
    });

    it('should handle data with zero values', () => {
      const result = {
        success: true,
        data: { year: 2024, month: 1, value: 0 }
      };
      
      render(<URResultsDisplay results={result} searchType="single" />);
      
      expect(screen.getAllByText('0,00')[0]).toBeInTheDocument();
  expect(screen.getByText('0,00')).toBeInTheDocument();
    });

    it('should handle data with negative values', () => {
      const result = {
        success: true,
        data: { year: 2024, month: 1, value: -1000.00 }
      };
      
      render(<URResultsDisplay results={result} searchType="single" />);
      
      expect(screen.getAllByText('-1.000,00')[0]).toBeInTheDocument();
  expect(screen.getByText('-1.000,00')).toBeInTheDocument();
    });

    it('should handle very large numbers', () => {
      const result = {
        success: true,
        data: { year: 2024, month: 1, value: 999999999.99 }
      };
      
      render(<URResultsDisplay results={result} searchType="single" />);
      
      expect(screen.getAllByText('999.999.999,99')[0]).toBeInTheDocument();
  expect(screen.getByText('999.999.999,99')).toBeInTheDocument();
    });

    it('should handle data with undefined year or month', () => {
      const result = {
        success: true,
        data: { value: 1000.00 }
      };
      
      render(<URResultsDisplay results={result} searchType="single" />);
      
      // Check for the text that actually appears (either translation or literal)
      // Use getAllByText since there are multiple instances
      const notAvailableElements = screen.queryAllByText('N/D');
      const literalElements = screen.queryAllByText('common.not_available');
      expect(notAvailableElements.length + literalElements.length).toBeGreaterThanOrEqual(1);
    });

    it('should handle single item array correctly', () => {
      const result = {
        success: true,
        data: [{ year: 2024, month: 1, value: 1000.00 }]
      };
      
      render(<URResultsDisplay results={result} searchType="range" />);
      
      expect(screen.getByText('1 registro')).toBeInTheDocument();
    });
  });
}); 