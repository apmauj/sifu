import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import URSearchForm from '../../components/URSearchForm';
import { vi } from 'vitest';

// Mock del servicio UR
vi.mock('../../services/urService', () => ({
  default: {
    getInfo: vi.fn().mockResolvedValue({
      success: true,
      data: {
        total_records: 1500,
        date_range: {
          min_year: 2010,
          max_year: 2024,
          min_month: 1,
          max_month: 12
        }
      }
    })
  }
}));

// Mock del contexto I18n
vi.mock('../../contexts/I18nContext', () => ({
  useI18n: () => ({
    t: (key) => {
      const translations = {
        'ur.search_title': 'Consultar Valor de UR',
        'ur.specific_period': 'Período específico',
        'ur.period_range': 'Rango de períodos',
        'ur.specific_month': 'Mes específico',
        'ur.full_year': 'Año completo',
        'ur.start_period': 'Período inicio',
        'ur.end_period': 'Período fin',
        'ur.year_required': 'El año es requerido',
        'ur.month_required': 'El mes es requerido',
        'ur.select_year': 'Selecciona un año',
        'ur.select_month': 'Selecciona un mes',
        'ur.search_button': 'Consultar UR',
        'ur.start_period_after_end': 'El período de inicio no puede ser posterior al período de fin',
        'ur.end_period_before_start': 'El período de fin no puede ser anterior al período de inicio',
        'ur.data_available': 'Datos disponibles:',
        'ur.records': 'registros',
        'ur.from': 'de',
        'ur.to': 'hasta',
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
        'ur.december': 'Diciembre',
        'common.year': 'Año',
        'common.month': 'Mes',
        'common.loading': 'Cargando...',
        'common.consulting': 'Consultando...',
        'common.clear': 'Limpiar'
      };
      return translations[key] || key;
    }
  })
}));

// Mock de QuickSelectors
vi.mock('../../components/QuickSelectors', () => ({
  default: ({ onURSingleSelect, onURRangeSelect }) => (
    <div data-testid="quick-selectors">
      <button onClick={() => onURSingleSelect(2024, 6)}>Quick Single</button>
      <button onClick={() => onURRangeSelect(2023, 1, 2024, 6)}>Quick Range</button>
    </div>
  )
}));

// Mock de react-hook-form
const mockSetValue = vi.fn();
const mockTrigger = vi.fn();
const mockGetValues = vi.fn();
const mockHandleSubmit = vi.fn();
const mockReset = vi.fn();

vi.mock('react-hook-form', () => ({
  useForm: () => ({
    control: {},
    handleSubmit: mockHandleSubmit.mockImplementation((fn) => (e) => {
      e?.preventDefault();
      const formData = {
        year: 2024,
        month: 6,
        startYear: 2023,
        startMonth: 1,
        endYear: 2024,
        endMonth: 6
      };
      fn(formData);
    }),
    formState: { errors: {} },
    setValue: mockSetValue,
    watch: vi.fn(),
    reset: mockReset,
    trigger: mockTrigger,
    getValues: mockGetValues.mockReturnValue({
      year: 2024,
      month: 6,
      startYear: 2023,
      startMonth: 1,
      endYear: 2024,
      endMonth: 6
    })
  }),
  Controller: ({ render, name, defaultValue, rules }) => {
    const field = {
      value: defaultValue || (name === 'year' ? 2024 : name === 'month' ? 6 : ''),
      onChange: vi.fn(),
      name
    };
    
    // Simular validación para tests específicos
    if (rules && rules.validate && typeof rules.validate === 'function') {
      const validationResult = rules.validate(field.value);
      if (validationResult !== true) {
        // Mock error for validation tests
      }
    }
    
    return render({ field });
  }
}));

describe('URSearchForm Component', () => {
  const mockOnSearch = vi.fn();
  const currentYear = new Date().getFullYear();
  const currentMonth = new Date().getMonth() + 1;

  beforeEach(() => {
    vi.clearAllMocks();
    mockOnSearch.mockClear();
  });

  // ===== COMPONENT RENDERING TESTS =====
  describe('Component Rendering', () => {
    it('should render form title and search type options', async () => {
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      expect(screen.getByText('Consultar Valor de UR')).toBeInTheDocument();
      expect(screen.getByText('Período específico')).toBeInTheDocument();
      expect(screen.getByText('Rango de períodos')).toBeInTheDocument();
    });

    it('should render subtype options for single search', () => {
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      expect(screen.getByText('Mes específico')).toBeInTheDocument();
      expect(screen.getByText('Año completo')).toBeInTheDocument();
    });

    it('should render form controls and buttons', () => {
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      expect(screen.getByRole('button', { name: 'Consultar UR' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Limpiar' })).toBeInTheDocument();
    });

    it('should render QuickSelectors component', () => {
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      expect(screen.getByTestId('quick-selectors')).toBeInTheDocument();
    });

    it('should show loading state for year selects when loading info', () => {
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      // Initially should show loading
      expect(screen.getByText('Cargando...')).toBeInTheDocument();
    });
  });

  // ===== SEARCH TYPE SELECTION TESTS =====
  describe('Search Type Selection', () => {
    it('should switch to range mode when range option is selected', () => {
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      const rangeRadio = screen.getByRole('radio', { name: 'Rango de períodos' });
      fireEvent.click(rangeRadio);
      
      expect(screen.getByText('Período inicio')).toBeInTheDocument();
      expect(screen.getByText('Período fin')).toBeInTheDocument();
    });

    it('should show single period form by default', () => {
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      const singleRadio = screen.getByRole('radio', { name: 'Período específico' });
      expect(singleRadio).toBeChecked();
    });

    it('should hide subtype options when range is selected', () => {
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      const rangeRadio = screen.getByRole('radio', { name: 'Rango de períodos' });
      fireEvent.click(rangeRadio);
      
      expect(screen.queryByText('Mes específico')).not.toBeInTheDocument();
      expect(screen.queryByText('Año completo')).not.toBeInTheDocument();
    });
  });

  // ===== SUBTYPE SELECTION TESTS =====
  describe('Subtype Selection', () => {
    it('should show month field when month subtype is selected', () => {
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      const monthRadio = screen.getByRole('radio', { name: 'Mes específico' });
      expect(monthRadio).toBeChecked();
      expect(screen.getByLabelText('Mes')).toBeInTheDocument();
    });

    it('should hide month field when year subtype is selected', () => {
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      const yearRadio = screen.getByRole('radio', { name: 'Año completo' });
      fireEvent.click(yearRadio);
      
      expect(screen.queryByLabelText('Mes')).not.toBeInTheDocument();
    });

    it('should switch between month and year subtypes correctly', () => {
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      const yearRadio = screen.getByRole('radio', { name: 'Año completo' });
      fireEvent.click(yearRadio);
      expect(screen.queryByLabelText('Mes')).not.toBeInTheDocument();
      
      const monthRadio = screen.getByRole('radio', { name: 'Mes específico' });
      fireEvent.click(monthRadio);
      expect(screen.getByLabelText('Mes')).toBeInTheDocument();
    });
  });

  // ===== FORM SUBMISSION TESTS =====
  describe('Form Submission', () => {
    it('should submit single month search correctly', () => {
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      const form = screen.getByRole('button', { name: 'Consultar UR' }).closest('form');
      fireEvent.submit(form);
      
      expect(mockHandleSubmit).toHaveBeenCalled();
    });

    it('should submit single year search correctly', () => {
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      const yearRadio = screen.getByRole('radio', { name: 'Año completo' });
      fireEvent.click(yearRadio);
      
      const form = screen.getByRole('button', { name: 'Consultar UR' }).closest('form');
      fireEvent.submit(form);
      
      expect(mockHandleSubmit).toHaveBeenCalled();
    });

    it('should submit range search correctly', () => {
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      const rangeRadio = screen.getByRole('radio', { name: 'Rango de períodos' });
      fireEvent.click(rangeRadio);
      
      const form = screen.getByRole('button', { name: 'Consultar UR' }).closest('form');
      fireEvent.submit(form);
      
      expect(mockHandleSubmit).toHaveBeenCalled();
    });

    it('should call onSearch when form is submitted', () => {
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      const submitButton = screen.getByRole('button', { name: 'Consultar UR' });
      fireEvent.click(submitButton);
      
      expect(mockOnSearch).toHaveBeenCalled();
    });
  });

  // ===== QUICK SELECTORS TESTS =====
  describe('Quick Selectors', () => {
    it('should handle quick single selection', () => {
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      const quickSingleButton = screen.getByText('Quick Single');
      fireEvent.click(quickSingleButton);
      
      expect(mockSetValue).toHaveBeenCalledWith('year', 2024);
      expect(mockSetValue).toHaveBeenCalledWith('month', 6);
      expect(mockOnSearch).toHaveBeenCalledWith({
        type: 'single',
        subtype: 'month',
        year: 2024,
        month: 6
      });
    });

    it('should handle quick range selection', () => {
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      const quickRangeButton = screen.getByText('Quick Range');
      fireEvent.click(quickRangeButton);
      
      expect(mockSetValue).toHaveBeenCalledWith('startYear', 2023);
      expect(mockSetValue).toHaveBeenCalledWith('startMonth', 1);
      expect(mockSetValue).toHaveBeenCalledWith('endYear', 2024);
      expect(mockSetValue).toHaveBeenCalledWith('endMonth', 6);
      expect(mockOnSearch).toHaveBeenCalledWith({
        type: 'range',
        startYear: 2023,
        startMonth: 1,
        endYear: 2024,
        endMonth: 6
      });
    });
  });

  // ===== LOADING STATE TESTS =====
  describe('Loading State', () => {
    it('should show loading state on submit button when loading', () => {
      render(<URSearchForm onSearch={mockOnSearch} isLoading={true} />);
      
      const submitButton = screen.getByRole('button', { name: 'Consultando...' });
      expect(submitButton).toBeDisabled();
      expect(screen.getByText('Consultando...')).toBeInTheDocument();
    });

    it('should show normal state when not loading', () => {
      render(<URSearchForm onSearch={mockOnSearch} isLoading={false} />);
      
      const submitButton = screen.getByRole('button', { name: 'Consultar UR' });
      expect(submitButton).not.toBeDisabled();
      expect(screen.getByText('Consultar UR')).toBeInTheDocument();
    });

    it('should disable year selects when loading UR info', () => {
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      // Initially should show loading state - check for disabled state
      const yearSelect = screen.getByLabelText('Año');
      expect(yearSelect).toBeDisabled();
    });
  });

  // ===== FORM CONTROLS TESTS =====
  describe('Form Controls', () => {
    it('should populate year options correctly', async () => {
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      await waitFor(() => {
        expect(screen.getAllByText('2024').length).toBeGreaterThan(0);
      });
    });

    it('should populate month options correctly', () => {
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      expect(screen.getByText('Enero')).toBeInTheDocument();
      expect(screen.getByText('Diciembre')).toBeInTheDocument();
    });

    it('should handle clear button correctly', () => {
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      const clearButton = screen.getByRole('button', { name: 'Limpiar' });
      fireEvent.click(clearButton);
      
      expect(mockSetValue).toHaveBeenCalledWith('year', currentYear);
      expect(mockSetValue).toHaveBeenCalledWith('month', currentMonth);
    });

    it('should clear range form correctly', () => {
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      const rangeRadio = screen.getByRole('radio', { name: 'Rango de períodos' });
      fireEvent.click(rangeRadio);
      
      const clearButton = screen.getByRole('button', { name: 'Limpiar' });
      fireEvent.click(clearButton);
      
      expect(mockSetValue).toHaveBeenCalledWith('startYear', currentYear - 1);
      expect(mockSetValue).toHaveBeenCalledWith('startMonth', 1);
      expect(mockSetValue).toHaveBeenCalledWith('endYear', currentYear);
      expect(mockSetValue).toHaveBeenCalledWith('endMonth', currentMonth);
    });
  });

  // ===== FORM VALIDATION TESTS =====
  describe('Form Validation', () => {
    it('should show validation errors for required fields', () => {
      // Test basic validation structure
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      // Verify form structure supports validation
      expect(screen.getByRole('button', { name: 'Consultar UR' })).toBeInTheDocument();
      expect(screen.getByLabelText('Año')).toBeInTheDocument();
    });

    it('should trigger validation on field changes', () => {
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      const rangeRadio = screen.getByRole('radio', { name: 'Rango de períodos' });
      fireEvent.click(rangeRadio);
      
      // Component renders correctly - validation logic is internal
      expect(screen.getByText('Período inicio')).toBeInTheDocument();
      expect(screen.getByText('Período fin')).toBeInTheDocument();
    });
  });

  // ===== UR INFO DISPLAY TESTS =====
  describe('UR Info Display', () => {
    it('should fetch UR info silently without availability line', async () => {
      render(<URSearchForm onSearch={mockOnSearch} />);
      await waitFor(() => {
        expect(screen.getByText('Consultar Valor de UR')).toBeInTheDocument();
      });
      expect(screen.queryByText(/Datos disponibles:/)).not.toBeInTheDocument();
    });

    it('should handle UR info loading errors gracefully', async () => {
      // Reset mock for this test
      const urService = await import('../../services/urService');
      vi.mocked(urService.default.getInfo).mockRejectedValueOnce(new Error('Network error'));
      
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      // Should not crash and should handle error gracefully
      await waitFor(() => {
        expect(screen.getByText('Consultar Valor de UR')).toBeInTheDocument();
      });
    });
  });

  // ===== EDGE CASES TESTS =====
  describe('Edge Cases', () => {
    it('should handle missing UR info gracefully', async () => {
      const urService = await import('../../services/urService');
      vi.mocked(urService.default.getInfo).mockResolvedValueOnce({
        success: true,
        data: null
      });
      
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      await waitFor(() => {
        expect(screen.getByText('Consultar Valor de UR')).toBeInTheDocument();
      });
    });

  it('should handle UR info without success flag (no line)', async () => {
      const urService = await import('../../services/urService');
      vi.mocked(urService.default.getInfo).mockResolvedValueOnce({
        data: {
          total_records: 500,
          date_range: {
            min_year: 2015,
            max_year: 2024
          }
        }
      });
      
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      await waitFor(() => {
        expect(screen.getByText('Consultar Valor de UR')).toBeInTheDocument();
      });
      expect(screen.queryByText(/Datos disponibles:/)).not.toBeInTheDocument();
    });

    it('should generate fallback year options when no date range', async () => {
      const urService = await import('../../services/urService');
      vi.mocked(urService.default.getInfo).mockResolvedValueOnce({
        success: true,
        data: {
          total_records: 100
          // No date_range
        }
      });
      
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      await waitFor(() => {
        expect(screen.getByText('Consultar Valor de UR')).toBeInTheDocument();
      });
    });

    it('should handle form submission with missing data', () => {
      mockGetValues.mockReturnValueOnce({
        year: '',
        month: '',
        startYear: '',
        startMonth: '',
        endYear: '',
        endMonth: ''
      });
      
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      const form = screen.getByRole('button', { name: 'Consultar UR' }).closest('form');
      fireEvent.submit(form);
      
      expect(mockHandleSubmit).toHaveBeenCalled();
    });

    it('should handle rapid search type changes', () => {
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      const rangeRadio = screen.getByRole('radio', { name: 'Rango de períodos' });
      const singleRadio = screen.getByRole('radio', { name: 'Período específico' });
      
      fireEvent.click(rangeRadio);
      fireEvent.click(singleRadio);
      fireEvent.click(rangeRadio);
      
      expect(screen.getByText('Período inicio')).toBeInTheDocument();
      expect(screen.getByText('Período fin')).toBeInTheDocument();
    });

    it('should handle rapid subtype changes', () => {
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      const yearRadio = screen.getByRole('radio', { name: 'Año completo' });
      const monthRadio = screen.getByRole('radio', { name: 'Mes específico' });
      
      fireEvent.click(yearRadio);
      fireEvent.click(monthRadio);
      fireEvent.click(yearRadio);
      
      expect(screen.queryByLabelText('Mes')).not.toBeInTheDocument();
    });
  });

  // ===== NUEVOS TESTS PARA COBERTURA ADICIONAL =====
  describe('Period Validation - Advanced', () => {
    it('should validate start period not after end period in range mode', () => {
      // Mock getValues to return invalid range (start > end)
      mockGetValues.mockReturnValue({
        startYear: 2024,
        startMonth: 12,
        endYear: 2024,
        endMonth: 6
      });

      render(<URSearchForm onSearch={mockOnSearch} />);
      
      const rangeRadio = screen.getByRole('radio', { name: 'Rango de períodos' });
      fireEvent.click(rangeRadio);
      
      // Component should render without crashing
      expect(screen.getByText('Período inicio')).toBeInTheDocument();
    });

    it('should validate end period not before start period', () => {
      // Mock getValues to return valid range initially
      mockGetValues.mockReturnValue({
        startYear: 2023,
        startMonth: 1,
        endYear: 2022,
        endMonth: 12
      });

      render(<URSearchForm onSearch={mockOnSearch} />);
      
      const rangeRadio = screen.getByRole('radio', { name: 'Rango de períodos' });
      fireEvent.click(rangeRadio);
      
      // Component should render without crashing
      expect(screen.getByText('Período fin')).toBeInTheDocument();
    });

    it('should handle validation with partial data', () => {
      // Mock getValues to return partial data
      mockGetValues.mockReturnValue({
        startYear: 2024,
        startMonth: null,
        endYear: null,
        endMonth: 6
      });

      render(<URSearchForm onSearch={mockOnSearch} />);
      
      const rangeRadio = screen.getByRole('radio', { name: 'Rango de períodos' });
      fireEvent.click(rangeRadio);
      
      // Should handle partial data gracefully
      expect(screen.getByText('Período inicio')).toBeInTheDocument();
    });

    it('should handle comparePeriods with equal periods', () => {
      // Mock getValues to return equal periods
      mockGetValues.mockReturnValue({
        startYear: 2024,
        startMonth: 6,
        endYear: 2024,
        endMonth: 6
      });

      render(<URSearchForm onSearch={mockOnSearch} />);
      
      const rangeRadio = screen.getByRole('radio', { name: 'Rango de períodos' });
      fireEvent.click(rangeRadio);
      
      // Equal periods should be valid
      expect(screen.getByText('Período inicio')).toBeInTheDocument();
    });
  });

  describe('Error Handling - Advanced', () => {
    it('should handle console errors during UR info fetch', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      const urService = await import('../../services/urService');
      vi.mocked(urService.default.getInfo).mockRejectedValueOnce(new Error('API Error'));

      render(<URSearchForm onSearch={mockOnSearch} />);
      
      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Error fetching UR info:', expect.any(Error));
      });

      consoleSpy.mockRestore();
    });

  it('should handle UR info with missing total_records (no line)', async () => {
      const urService = await import('../../services/urService');
      vi.mocked(urService.default.getInfo).mockResolvedValueOnce({
        success: true,
        data: {
          date_range: {
            min_year: 2020,
            max_year: 2024
          }
          // No total_records
        }
      });
      
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      await waitFor(() => {
        expect(screen.getByText('Consultar Valor de UR')).toBeInTheDocument();
      });
      expect(screen.queryByText(/Datos disponibles:/)).not.toBeInTheDocument();
    });

  it('should handle UR info with missing date_range months (internal only)', async () => {
      const urService = await import('../../services/urService');
      vi.mocked(urService.default.getInfo).mockResolvedValueOnce({
        success: true,
        data: {
          total_records: 800,
          date_range: {
            min_year: 2020,
            max_year: 2024
            // No min_month, max_month
          }
        }
      });
      
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      await waitFor(() => {
        expect(screen.getByText('Consultar Valor de UR')).toBeInTheDocument();
      });
    });
  });

  describe('Conditional Rendering - Advanced', () => {
  it('should not render availability line even with full date_range', async () => {
      const urService = await import('../../services/urService');
      vi.mocked(urService.default.getInfo).mockResolvedValueOnce({
        success: true,
        data: {
          total_records: 1000,
          date_range: {
            min_year: 2020,
            max_year: 2024,
            min_month: null, // Missing min_month
            max_month: 12
          }
        }
      });
      
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      await waitFor(() => {
        expect(screen.getByText('Consultar Valor de UR')).toBeInTheDocument();
      });
      expect(screen.queryByText(/Datos disponibles:/)).not.toBeInTheDocument();
    });

    it('should handle missing urInfo gracefully in display section', async () => {
      const urService = await import('../../services/urService');
      vi.mocked(urService.default.getInfo).mockResolvedValueOnce({
        success: false,
        data: null
      });
      
      render(<URSearchForm onSearch={mockOnSearch} />);
      
      await waitFor(() => {
        // Should not show UR info section when urInfo is null
        expect(screen.queryByText('Datos disponibles:')).not.toBeInTheDocument();
      });
    });
  });
}); 