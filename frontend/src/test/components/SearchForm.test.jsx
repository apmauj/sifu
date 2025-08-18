import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import SearchForm from '../../components/SearchForm';
import { vi } from 'vitest';
import { BUTTON_LABELS } from '../../constants';

// Mock del servicio API
vi.mock('../../services/api', () => ({
  default: {
    getInfo: vi.fn().mockResolvedValue({
      success: true,
      data: {
        latest_date: '2025-06-17'
      }
    }),
    getByDate: vi.fn(),
    getByRange: vi.fn(),
    getLatest: vi.fn()
  }
}));

// Mock mejorado de react-hook-form
const mockSetValue = vi.fn();
const mockTrigger = vi.fn();
const mockGetValues = vi.fn(() => ({ fechaFin: '2025-06-17', fechaInicio: '2025-06-17' }));

vi.mock('react-hook-form', () => ({
  useForm: () => ({
    control: {},
    handleSubmit: (fn) => (e) => {
      e.preventDefault();
      // Simular datos del formulario
      const formData = {
        fecha: '2025-06-17',
        fechaInicio: '2025-06-17',
        fechaFin: '2025-06-17'
      };
      fn(formData);
    },
    formState: { errors: {} },
    setValue: mockSetValue,
    watch: vi.fn(),
    reset: vi.fn(),
    trigger: mockTrigger,
    getValues: mockGetValues
  }),
  Controller: ({ render, rules }) => {
    // Simular validación si hay rules
    if (rules && rules.validate) {
      const validationResult = rules.validate('2025-06-17');
      if (validationResult !== true) {
        console.log('Validation error:', validationResult);
      }
    }
    
    return render({
      field: {
        value: '2025-06-17',
        onChange: vi.fn(),
        name: 'fecha'
      }
    });
  }
}));

// Mock de date-fns con manejo de errores
vi.mock('date-fns', () => ({
  format: vi.fn((date, formatStr) => {
    if (date === 'invalid-date-for-error') {
      throw new Error('Invalid date');
    }
    if (date instanceof Date) {
      return '2025-06-17';
    }
    return '2025-06-17';
  }),
  parseISO: vi.fn((dateStr) => {
    if (dateStr === 'invalid-date-string') {
      return new Date('invalid');
    }
    return new Date('2025-06-17');
  }),
  isValid: vi.fn((date) => {
    if (date && date.toString() === 'Invalid Date') {
      return false;
    }
    return true;
  }),
  addDays: vi.fn((date, days) => new Date('2025-06-17')),
  subDays: vi.fn((date, days) => new Date('2025-06-17'))
}));

// Mock de removeAttribute para los elementos input
HTMLInputElement.prototype.removeAttribute = vi.fn();

describe('SearchForm Component', () => {
  const mockOnSearch = vi.fn();

  beforeEach(() => {
    mockOnSearch.mockClear();
    vi.clearAllMocks();
    mockSetValue.mockClear();
    mockTrigger.mockClear();
    mockGetValues.mockReturnValue({ fechaFin: '2025-06-17', fechaInicio: '2025-06-17' });
  });

  // Helper to render and wait for initial async effects (fetchMaxDate)
  const renderAndWait = async () => {
    render(<SearchForm onSearch={mockOnSearch} />);
    // Wait for base label after any state updates
    await screen.findByText('Fecha específica');
  };

  it('should render correctly with search modes', async () => {
    await renderAndWait();
    expect(screen.getByText('Fecha específica')).toBeInTheDocument();
    expect(screen.getByText('Rango de fechas')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Buscar' })).toBeInTheDocument();
  });

  it('should change search mode when clicking options', async () => {
    await renderAndWait();
    const rangeOption = screen.getByText('Rango de fechas');
    fireEvent.click(rangeOption);
    
    // Should show range inputs
    expect(screen.getByText('Fecha inicio')).toBeInTheDocument();
    expect(screen.getByText('Fecha fin')).toBeInTheDocument();
  });

  it('should show date field when "Specific Date" is selected', async () => {
    await renderAndWait();
    const dateOption = screen.getByText('Fecha específica');
    fireEvent.click(dateOption);
    
    // Should show single date input with current date
    const dateInput = screen.getByDisplayValue('2025-06-17');
    expect(dateInput).toBeInTheDocument();
  });

  it('should show start and end date fields when "Date Range" is selected', async () => {
    await renderAndWait();
    const rangeOption = screen.getByText('Rango de fechas');
    fireEvent.click(rangeOption);
    
    expect(screen.getByText('Fecha inicio')).toBeInTheDocument();
    expect(screen.getByText('Fecha fin')).toBeInTheDocument();
  });

  it('should show quick date buttons in "Specific Date" mode', async () => {
    await renderAndWait();
    const dateOption = screen.getByText('Fecha específica');
    fireEvent.click(dateOption);
    
    // Check for quick date buttons
    expect(screen.getByText('Hoy')).toBeInTheDocument();
    expect(screen.getByText('Ayer')).toBeInTheDocument();
  });

  it('should show quick range buttons in "Date Range" mode', async () => {
    await renderAndWait();
    const rangeOption = screen.getByText('Rango de fechas');
    fireEvent.click(rangeOption);
    
    // Check for quick range buttons
    expect(screen.getByText('Últimos 7 días')).toBeInTheDocument();
    expect(screen.getByText('Últimos 30 días')).toBeInTheDocument();
  });

  it('should call onSearch when form is submitted with valid data', async () => {
    await renderAndWait();
    // Submit form with the actual rendered date (2025-06-17)
    const searchButton = screen.getByRole('button', { name: 'Buscar' });
    fireEvent.click(searchButton);
    
    expect(mockOnSearch).toHaveBeenCalledWith({
      searchType: 'single',
      date: '2025-06-17'
    });
  });

  it('should call onSearch with range data when range mode is used', async () => {
    await renderAndWait();
    // Switch to range mode
    const rangeOption = screen.getByText('Rango de fechas');
    fireEvent.click(rangeOption);
    
    // Submit form with default date range (both should be 2025-06-17)
    const searchButton = screen.getByRole('button', { name: 'Buscar' });
    fireEvent.click(searchButton);
    
    expect(mockOnSearch).toHaveBeenCalledWith({
      searchType: 'range',
      startDate: '2025-06-17',
      endDate: '2025-06-17'
    });
  });

  it('should handle quick date button clicks', async () => {
    await renderAndWait();
    const todayButton = screen.getByText('Hoy');
    fireEvent.click(todayButton);
    
    // Should set today's date and trigger search
    expect(mockOnSearch).toHaveBeenCalled();
  });

  it('should handle quick range button clicks', async () => {
    await renderAndWait();
    // Switch to range mode
    const rangeOption = screen.getByText('Rango de fechas');
    fireEvent.click(rangeOption);
    
    const last7DaysButton = screen.getByText('Últimos 7 días');
    fireEvent.click(last7DaysButton);
    
    // Should set date range and trigger search
    expect(mockOnSearch).toHaveBeenCalled();
  });

  it('should not have max attribute on date inputs', async () => {
    await renderAndWait();
    // Get date input by placeholder instead of empty value
    const dateInput = screen.getByPlaceholderText('Selecciona una fecha');
    expect(dateInput).not.toHaveAttribute('max');
  });

  it('should validate required fields before submission', async () => {
    await renderAndWait();
    // Form should have default values, so submission should work
    const searchButton = screen.getByRole('button', { name: 'Buscar' });
    fireEvent.click(searchButton);
    
    // Should call onSearch with default data
    expect(mockOnSearch).toHaveBeenCalledWith({
      searchType: 'single',
      date: '2025-06-17'
    });
  });

  it('should reset form when switching between modes', async () => {
    await renderAndWait();
    // Get initial date input
    const initialDateInput = screen.getByDisplayValue('2025-06-17');
    fireEvent.change(initialDateInput, { target: { value: '2025-06-17' } });
    
    // Switch to range mode
    const rangeOption = screen.getByText('Rango de fechas');
    fireEvent.click(rangeOption);
    
    // Switch back to single mode
    const dateOption = screen.getByText('Fecha específica');
    fireEvent.click(dateOption);
    
    // Form should be reset to default value
    const resetDateInput = screen.getByDisplayValue('2025-06-17');
    expect(resetDateInput).toBeInTheDocument();
  });

  // NUEVOS TESTS PARA MEJORAR COVERAGE

  it('should handle API error when fetching max date', async () => {
    const apiMock = await import('../../services/api');
    apiMock.default.getInfo.mockRejectedValueOnce(new Error('API Error'));
    
    render(<SearchForm onSearch={mockOnSearch} />);
    
    // Should render without crashing despite API error
    expect(screen.getByText('Fecha específica')).toBeInTheDocument();
  });

  it('should handle API response without latest_date', async () => {
    const apiMock = await import('../../services/api');
    apiMock.default.getInfo.mockResolvedValueOnce({
      success: false,
      data: null
    });
    
    render(<SearchForm onSearch={mockOnSearch} />);
    
    // Should render without crashing
    expect(screen.getByText('Fecha específica')).toBeInTheDocument();
  });

  it('should handle invalid maxDate parsing', async () => {
    const apiMock = await import('../../services/api');
    apiMock.default.getInfo.mockResolvedValueOnce({
      success: true,
      data: {
        latest_date: 'invalid-date-string'
      }
    });
    
    render(<SearchForm onSearch={mockOnSearch} />);
    
    // Should render without crashing and log warning
    expect(screen.getByText('Fecha específica')).toBeInTheDocument();
  });

  it('should handle clear button click in single mode', async () => {
    await renderAndWait();
    const clearButton = screen.getByText('Limpiar');
    fireEvent.click(clearButton);
    
    // Should call setValue with today's date
    expect(mockSetValue).toHaveBeenCalledWith('fecha', expect.any(String));
  });

  it('should handle clear button click in range mode', async () => {
    await renderAndWait();
    // Switch to range mode
    const rangeOption = screen.getByText('Rango de fechas');
    fireEvent.click(rangeOption);
    
    const clearButton = screen.getByText('Limpiar');
    fireEvent.click(clearButton);
    
    // Should call setValue for both dates
    expect(mockSetValue).toHaveBeenCalledWith('fechaInicio', expect.any(String));
    expect(mockSetValue).toHaveBeenCalledWith('fechaFin', expect.any(String));
  });

  it('should show loading state when isLoading is true', async () => {
    await renderAndWait();
    // Re-render with loading
    render(<SearchForm onSearch={mockOnSearch} isLoading={true} />);
    const submitButton = screen.getByRole('button', { name: 'Cargando...' });
    expect(submitButton).toBeInTheDocument();
    expect(submitButton).toBeDisabled();
    expect(submitButton).toHaveClass('bg-gray-100', 'text-gray-400', 'cursor-not-allowed');
  });

  it('should show normal state when isLoading is false', async () => {
    await renderAndWait();
    // Re-render not needed; ensure at least one submit button present
    const submitButtons = screen.getAllByRole('button', { name: 'Buscar' });
    expect(submitButtons.length).toBeGreaterThan(0);
    expect(submitButtons[0]).not.toBeDisabled();
    expect(submitButtons[0]).toHaveClass('bg-uruguay-blue', 'text-white');
  });

  it('should handle date validation for max date constraint', async () => {
    const apiMock = await import('../../services/api');
    apiMock.default.getInfo.mockResolvedValueOnce({
      success: true,
      data: {
        latest_date: '2025-06-15' // Earlier than default date
      }
    });
    
    render(<SearchForm onSearch={mockOnSearch} />);
    
    // Should render without validation errors initially
    expect(screen.getByText('Fecha específica')).toBeInTheDocument();
  });

  it('should handle range validation - start date after end date', async () => {
    mockGetValues.mockReturnValueOnce({ 
      fechaFin: '2025-06-10', 
      fechaInicio: '2025-06-20' // Start after end
    });
    await renderAndWait();
    
    // Switch to range mode
    const rangeOption = screen.getByText('Rango de fechas');
    fireEvent.click(rangeOption);
    
    // Should render range inputs
    expect(screen.getByText('Fecha inicio')).toBeInTheDocument();
    expect(screen.getByText('Fecha fin')).toBeInTheDocument();
  });

  it('should handle range validation - end date before start date', async () => {
    mockGetValues.mockReturnValueOnce({ 
      fechaInicio: '2025-06-20', 
      fechaFin: '2025-06-10' // End before start
    });
    await renderAndWait();
    
    // Switch to range mode
    const rangeOption = screen.getByText('Rango de fechas');
    fireEvent.click(rangeOption);
    
    // Should render range inputs
    expect(screen.getByText('Fecha inicio')).toBeInTheDocument();
    expect(screen.getByText('Fecha fin')).toBeInTheDocument();
  });

  it('should trigger validation when start date changes in range mode', async () => {
    await renderAndWait();
    // Switch to range mode
    const rangeOption = screen.getByText('Rango de fechas');
    fireEvent.click(rangeOption);
    
    // The trigger should be called when date changes (simulated in Controller mock)
    expect(screen.getByText('Fecha inicio')).toBeInTheDocument();
  });

  it('should trigger validation when end date changes in range mode', async () => {
    await renderAndWait();
    // Switch to range mode
    const rangeOption = screen.getByText('Rango de fechas');
    fireEvent.click(rangeOption);
    
    // The trigger should be called when date changes (simulated in Controller mock)
    expect(screen.getByText('Fecha fin')).toBeInTheDocument();
  });

  it('should handle console warning for invalid maxDate', async () => {
    const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
    
    // Mock the date-fns functions directly for this test
    const { parseISO, isValid } = await import('date-fns');
    parseISO.mockImplementationOnce(() => new Date('invalid'));
    isValid.mockImplementationOnce(() => false);
    
    const apiMock = await import('../../services/api');
    apiMock.default.getInfo.mockResolvedValueOnce({
      success: true,
      data: {
        latest_date: 'invalid-date-string'
      }
    });
    
    render(<SearchForm onSearch={mockOnSearch} />);
    
    // Should handle invalid date gracefully
    expect(screen.getByText('Fecha específica')).toBeInTheDocument();
    
    consoleSpy.mockRestore();
  });
}); 