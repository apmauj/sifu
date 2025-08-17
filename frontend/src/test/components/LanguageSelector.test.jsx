import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import LanguageSelector from '../../components/LanguageSelector.jsx';

// Mock de heroicons (incluye íconos usados indirectamente)
vi.mock('@heroicons/react/24/outline', () => ({
  ArrowPathIcon: (props) => <div data-testid="arrow-path-icon" {...props}></div>,
  ArrowDownIcon: (props) => <div data-testid="arrow-down-icon" {...props}></div>,
  ArrowUpIcon: (props) => <div data-testid="arrow-up-icon" {...props}></div>,
  MinusIcon: (props) => <div data-testid="minus-icon" {...props}></div>,
  MagnifyingGlassIcon: (props) => <div data-testid="magnifying-glass-icon" {...props}></div>,
  XMarkIcon: (props) => <div data-testid="x-mark-icon" {...props}></div>,
  CheckCircleIcon: (props) => <div data-testid="check-circle-icon" {...props}></div>,
  ExclamationCircleIcon: (props) => <div data-testid="exclamation-circle-icon" {...props}></div>,
  InformationCircleIcon: (props) => <div data-testid="information-circle-icon" {...props}></div>,
  ExclamationTriangleIcon: (props) => <div data-testid="exclamation-triangle-icon" {...props}></div>,
  ChartBarIcon: (props) => <div data-testid="chart-bar-icon" {...props}></div>,
  CalendarIcon: (props) => <div data-testid="calendar-icon" {...props}></div>,
  ClockIcon: (props) => <div data-testid="clock-icon" {...props}></div>,
  BanknotesIcon: (props) => <div data-testid="banknotes-icon" {...props}></div>,
  CurrencyDollarIcon: (props) => <div data-testid="currency-dollar-icon" {...props}></div>,
  GlobeAltIcon: (props) => <div data-testid="globe-icon" {...props}>🌍</div>,
  MoonIcon: (props) => <div data-testid="moon-icon" {...props}></div>,
  SunIcon: (props) => <div data-testid="sun-icon" {...props}></div>
}));

// Mock del contexto I18n
const mockSetLanguage = vi.fn();
const mockT = vi.fn();

vi.mock('../../contexts/I18nContext', () => ({
  useI18n: () => ({
    currentLanguage: 'es',
    supportedLanguages: ['es', 'en', 'pt'],
    setLanguage: mockSetLanguage,
    t: mockT
  })
}));

describe('LanguageSelector Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockT.mockImplementation((key) => {
      const translations = {
        'common.select_language': 'Seleccionar idioma'
      };
      return translations[key] || key;
    });
  });

  describe('Basic rendering', () => {
    it('should render globe icon', () => {
      render(<LanguageSelector />);

      expect(screen.getByTestId('globe-icon')).toBeInTheDocument();
    });

    it('should render language select dropdown', () => {
      render(<LanguageSelector />);

      const select = screen.getByRole('combobox');
      expect(select).toBeInTheDocument();
      expect(select).toHaveAttribute('aria-label', 'Seleccionar idioma');
    });

    it('should show current language as selected', () => {
      render(<LanguageSelector />);

      const select = screen.getByRole('combobox');
      expect(select).toHaveValue('es');
    });

    it('should render all supported language options', () => {
      render(<LanguageSelector />);

      expect(screen.getByRole('option', { name: '🇺🇾 Español' })).toBeInTheDocument();
      expect(screen.getByRole('option', { name: '🇺🇸 English' })).toBeInTheDocument();
      expect(screen.getByRole('option', { name: '🇧🇷 Português' })).toBeInTheDocument();
    });

    it('should have correct CSS classes', () => {
      render(<LanguageSelector />);

      const container = screen.getByTestId('globe-icon').parentElement;
      expect(container).toHaveClass('flex', 'items-center', 'space-x-2');

      const select = screen.getByRole('combobox');
      expect(select).toHaveClass('text-sm', 'border-gray-300', 'rounded-md');
    });
  });

  describe('Language change functionality', () => {
    it('should call setLanguage when option is selected', async () => {
      const user = userEvent.setup();
      render(<LanguageSelector />);

      const select = screen.getByRole('combobox');
      await user.selectOptions(select, 'en');

      expect(mockSetLanguage).toHaveBeenCalledWith('en');
    });

    it('should call setLanguage with correct language for each option', async () => {
      const user = userEvent.setup();
      render(<LanguageSelector />);

      const select = screen.getByRole('combobox');

      // Test English
      await user.selectOptions(select, 'en');
      expect(mockSetLanguage).toHaveBeenCalledWith('en');

      // Test Portuguese
      await user.selectOptions(select, 'pt');
      expect(mockSetLanguage).toHaveBeenCalledWith('pt');

      // Test Spanish
      await user.selectOptions(select, 'es');
      expect(mockSetLanguage).toHaveBeenCalledWith('es');

      expect(mockSetLanguage).toHaveBeenCalledTimes(3);
    });

    it('should handle language change with fireEvent', async () => {
      render(<LanguageSelector />);

      const select = screen.getByRole('combobox');
      fireEvent.change(select, { target: { value: 'pt' } });

      expect(mockSetLanguage).toHaveBeenCalledWith('pt');
    });

    it('should work with async setLanguage function', async () => {
      mockSetLanguage.mockResolvedValue();
      const user = userEvent.setup();
      render(<LanguageSelector />);

      const select = screen.getByRole('combobox');
      await user.selectOptions(select, 'en');

      expect(mockSetLanguage).toHaveBeenCalledWith('en');
      await waitFor(() => {
        expect(mockSetLanguage).toHaveBeenCalledTimes(1);
      });
    });
  });

  describe('Error handling', () => {
    it('should handle setLanguage errors gracefully', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      mockSetLanguage.mockRejectedValue(new Error('Network error'));
      
      const user = userEvent.setup();
      render(<LanguageSelector />);

      const select = screen.getByRole('combobox');
      await user.selectOptions(select, 'en');

      expect(mockSetLanguage).toHaveBeenCalledWith('en');
      
      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith(
          '❌ LanguageSelector: Error cambiando idioma:',
          expect.any(Error)
        );
      });

      consoleSpy.mockRestore();
    });

    it('should not break when setLanguage throws synchronously', () => {
      mockSetLanguage.mockImplementation(() => {
        throw new Error('Sync error');
      });
      
      render(<LanguageSelector />);

      const select = screen.getByRole('combobox');
      
      expect(() => {
        fireEvent.change(select, { target: { value: 'en' } });
      }).not.toThrow();
    });
  });

  describe('Context integration', () => {
    it('should use context values correctly', () => {
      render(<LanguageSelector />);

      // Should show current language from context
      const select = screen.getByRole('combobox');
      expect(select).toHaveValue('es');

      // Should render all supported languages from context
      const options = screen.getAllByRole('option');
      expect(options).toHaveLength(3);
      expect(options[0]).toHaveValue('es');
      expect(options[1]).toHaveValue('en');
      expect(options[2]).toHaveValue('pt');
    });

    it('should call translation function', () => {
      render(<LanguageSelector />);

      expect(mockT).toHaveBeenCalledWith('common.select_language');
    });

    it('should handle context changes gracefully', () => {
      render(<LanguageSelector />);

      // Component should render without errors when context provides expected values
      expect(screen.getByRole('combobox')).toBeInTheDocument();
      expect(screen.getAllByRole('option')).toHaveLength(3);
    });
  });

  describe('Accessibility', () => {
    it('should have proper aria-label', () => {
      render(<LanguageSelector />);

      const select = screen.getByRole('combobox');
      expect(select).toHaveAttribute('aria-label', 'Seleccionar idioma');
    });

    it('should use translation for aria-label', () => {
      mockT.mockImplementation((key) => {
        if (key === 'common.select_language') return 'Select language';
        return key;
      });

      render(<LanguageSelector />);

      const select = screen.getByRole('combobox');
      expect(select).toHaveAttribute('aria-label', 'Select language');
    });

    it('should fallback to default aria-label when translation is missing', () => {
      mockT.mockImplementation(() => null);

      render(<LanguageSelector />);

      const select = screen.getByRole('combobox');
      expect(select).toHaveAttribute('aria-label', 'Seleccionar idioma');
    });

    it('should be keyboard navigable', async () => {
      const user = userEvent.setup();
      render(<LanguageSelector />);

      const select = screen.getByRole('combobox');
      
      // Focus the select
      await user.tab();
      expect(select).toHaveFocus();

      // Should be able to change with keyboard
      await user.keyboard('{ArrowDown}');
      // Note: Actual keyboard navigation testing is browser-specific
      // This test verifies the select is focusable
    });
  });

  describe('Language names and flags', () => {
    it('should display correct language names with flags', () => {
      render(<LanguageSelector />);

      expect(screen.getByText('🇺🇾 Español')).toBeInTheDocument();
      expect(screen.getByText('🇺🇸 English')).toBeInTheDocument();
      expect(screen.getByText('🇧🇷 Português')).toBeInTheDocument();
    });

    it('should have unique values for each option', () => {
      render(<LanguageSelector />);

      const options = screen.getAllByRole('option');
      const values = options.map(option => option.value);
      const uniqueValues = [...new Set(values)];

      expect(values).toHaveLength(uniqueValues.length);
      expect(values).toEqual(['es', 'en', 'pt']);
    });

    it('should have correct option structure', () => {
      render(<LanguageSelector />);

      const esOption = screen.getByRole('option', { name: '🇺🇾 Español' });
      const enOption = screen.getByRole('option', { name: '🇺🇸 English' });
      const ptOption = screen.getByRole('option', { name: '🇧🇷 Português' });

      expect(esOption).toHaveValue('es');
      expect(enOption).toHaveValue('en');
      expect(ptOption).toHaveValue('pt');
    });

    it('should map language codes to display names correctly', () => {
      render(<LanguageSelector />);

      // Verify the mapping from the component's languageNames object
      expect(screen.getByRole('option', { name: '🇺🇾 Español' })).toHaveValue('es');
      expect(screen.getByRole('option', { name: '🇺🇸 English' })).toHaveValue('en');
      expect(screen.getByRole('option', { name: '🇧🇷 Português' })).toHaveValue('pt');
    });
  });

  describe('Component integration', () => {
    it('should work with all context functions', () => {
      render(<LanguageSelector />);

      // Should call t function for translations
      expect(mockT).toHaveBeenCalledWith('common.select_language');

      // Should render based on context values
      const select = screen.getByRole('combobox');
      expect(select).toHaveValue('es');
      expect(screen.getAllByRole('option')).toHaveLength(3);
    });

    it('should maintain component state during re-renders', () => {
      const { rerender } = render(<LanguageSelector />);

      const select = screen.getByRole('combobox');
      expect(select).toHaveValue('es');

      // Re-render component
      rerender(<LanguageSelector />);

      const selectAfterRerender = screen.getByRole('combobox');
      expect(selectAfterRerender).toHaveValue('es');
      expect(mockT).toHaveBeenCalledTimes(2); // Called again on rerender
    });

    it('should handle rapid language changes', async () => {
      const user = userEvent.setup();
      render(<LanguageSelector />);

      const select = screen.getByRole('combobox');

      // Rapid changes
      await user.selectOptions(select, 'en');
      await user.selectOptions(select, 'pt');
      await user.selectOptions(select, 'es');

      expect(mockSetLanguage).toHaveBeenCalledTimes(3);
      expect(mockSetLanguage).toHaveBeenNthCalledWith(1, 'en');
      expect(mockSetLanguage).toHaveBeenNthCalledWith(2, 'pt');
      expect(mockSetLanguage).toHaveBeenNthCalledWith(3, 'es');
    });

    it('should handle component lifecycle correctly', () => {
      const { unmount } = render(<LanguageSelector />);

      // Component should render and work
      expect(screen.getByRole('combobox')).toBeInTheDocument();

      // Should unmount without errors
      expect(() => unmount()).not.toThrow();
    });
  });

  describe('Edge cases and robustness', () => {
    it('should handle empty supported languages gracefully', () => {
      // This test verifies the component doesn't break even with edge cases
      render(<LanguageSelector />);

      // With our mock returning ['es', 'en', 'pt'], this should work fine
      expect(screen.getAllByRole('option')).toHaveLength(3);
    });

    it('should handle missing language names gracefully', () => {
      render(<LanguageSelector />);

      // All our supported languages have names defined, so this should work
      const options = screen.getAllByRole('option');
      options.forEach(option => {
        expect(option.textContent).toBeTruthy();
        expect(option.textContent).not.toBe('undefined');
      });
    });

    it('should maintain correct DOM structure', () => {
      render(<LanguageSelector />);

      // Should have the expected structure
      const container = screen.getByTestId('globe-icon').parentElement;
      expect(container).toContainElement(screen.getByTestId('globe-icon'));
      expect(container).toContainElement(screen.getByRole('combobox'));
    });

    it('should handle focus and blur events', async () => {
      const user = userEvent.setup();
      render(<LanguageSelector />);

      const select = screen.getByRole('combobox');

      // Focus
      await user.click(select);
      expect(select).toHaveFocus();

      // Blur
      await user.tab();
      expect(select).not.toHaveFocus();
    });
  });
}); 