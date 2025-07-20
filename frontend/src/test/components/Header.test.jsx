import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import Header from '../../components/Header.jsx';

// Mock de LanguageSelector
vi.mock('../../components/LanguageSelector', () => ({
  default: () => <div data-testid="language-selector">Language Selector</div>
}));

// Mock de heroicons
vi.mock('@heroicons/react/24/outline', () => ({
  CurrencyDollarIcon: (props) => <div data-testid="currency-icon" {...props}>💰</div>,
  ArrowPathIcon: (props) => <div data-testid="arrow-icon" {...props}>🔄</div>
}));

// Mock del contexto I18n siguiendo el patrón del proyecto
vi.mock('../../contexts/I18nContext', () => ({
  useI18n: () => ({
    currentLanguage: 'es',
    isLoading: false,
    t: (key) => {
      const translations = {
        'header.sifu_title': 'SIFU',
        'header.sifu_subtitle': 'Sistema de Índices Financieros - Uruguay 🇺🇾',
        'common.updating': 'Actualizando...',
        'common.refresh_data': 'Actualizar Datos'
      };
      return translations[key] || key;
    }
  })
}));

describe('Header Component', () => {
  let mockOnRefresh;

  beforeEach(() => {
    mockOnRefresh = vi.fn();
  });

  describe('Basic rendering', () => {
    it('should render header with title and subtitle', () => {
      render(<Header onRefresh={mockOnRefresh} isRefreshing={false} />);

      expect(screen.getByText('SIFU')).toBeInTheDocument();
      expect(screen.getByText('Sistema de Índices Financieros - Uruguay 🇺🇾')).toBeInTheDocument();
    });

    it('should render currency icon', () => {
      render(<Header onRefresh={mockOnRefresh} isRefreshing={false} />);

      expect(screen.getByTestId('currency-icon')).toBeInTheDocument();
    });

    it('should render language selector', () => {
      render(<Header onRefresh={mockOnRefresh} isRefreshing={false} />);

      expect(screen.getByTestId('language-selector')).toBeInTheDocument();
    });

    it('should render refresh button', () => {
      render(<Header onRefresh={mockOnRefresh} isRefreshing={false} />);

      const refreshButton = screen.getByRole('button');
      expect(refreshButton).toBeInTheDocument();
      expect(refreshButton).toHaveTextContent('Actualizar Datos');
    });

    it('should render arrow icon in refresh button', () => {
      render(<Header onRefresh={mockOnRefresh} isRefreshing={false} />);

      expect(screen.getByTestId('arrow-icon')).toBeInTheDocument();
    });
  });

  describe('Refresh button functionality', () => {
    it('should call onRefresh when button is clicked', () => {
      render(<Header onRefresh={mockOnRefresh} isRefreshing={false} />);

      const refreshButton = screen.getByRole('button');
      fireEvent.click(refreshButton);

      expect(mockOnRefresh).toHaveBeenCalledTimes(1);
    });

    it('should be enabled when isRefreshing is false', () => {
      render(<Header onRefresh={mockOnRefresh} isRefreshing={false} />);

      const refreshButton = screen.getByRole('button');
      expect(refreshButton).not.toBeDisabled();
      expect(refreshButton).toHaveTextContent('Actualizar Datos');
    });

    it('should be disabled when isRefreshing is true', () => {
      render(<Header onRefresh={mockOnRefresh} isRefreshing={true} />);

      const refreshButton = screen.getByRole('button');
      expect(refreshButton).toBeDisabled();
      expect(refreshButton).toHaveTextContent('Actualizando...');
    });

    it('should not call onRefresh when disabled', () => {
      render(<Header onRefresh={mockOnRefresh} isRefreshing={true} />);

      const refreshButton = screen.getByRole('button');
      fireEvent.click(refreshButton);

      expect(mockOnRefresh).not.toHaveBeenCalled();
    });

    it('should show spinning animation when refreshing', () => {
      render(<Header onRefresh={mockOnRefresh} isRefreshing={true} />);

      const arrowIcon = screen.getByTestId('arrow-icon');
      expect(arrowIcon).toHaveClass('animate-spin');
    });

    it('should not show spinning animation when not refreshing', () => {
      render(<Header onRefresh={mockOnRefresh} isRefreshing={false} />);

      const arrowIcon = screen.getByTestId('arrow-icon');
      expect(arrowIcon).not.toHaveClass('animate-spin');
    });
  });

  describe('Button styling states', () => {
    it('should have correct styling when enabled', () => {
      render(<Header onRefresh={mockOnRefresh} isRefreshing={false} />);

      const refreshButton = screen.getByRole('button');
      expect(refreshButton).toHaveClass('bg-uruguay-blue', 'text-white');
      expect(refreshButton).not.toHaveClass('bg-gray-100', 'text-gray-400', 'cursor-not-allowed');
    });

    it('should have correct styling when disabled', () => {
      render(<Header onRefresh={mockOnRefresh} isRefreshing={true} />);

      const refreshButton = screen.getByRole('button');
      expect(refreshButton).toHaveClass('bg-gray-100', 'text-gray-400', 'cursor-not-allowed');
      expect(refreshButton).not.toHaveClass('bg-uruguay-blue', 'text-white');
    });
  });

  describe('Translation handling', () => {
    it('should use fallback text when translations are missing', () => {
      // Mock para retornar claves sin traducir
      vi.mocked(vi.importActual('../../contexts/I18nContext')).useI18n = () => ({
        currentLanguage: 'es',
        isLoading: false,
        t: (key) => key // Retorna la clave tal como viene
      });

      render(<Header onRefresh={mockOnRefresh} isRefreshing={false} />);

      // Debería mostrar los fallbacks del componente cuando no hay traducciones
      expect(screen.getByText('SIFU')).toBeInTheDocument();
    });

    it('should show updating text when refreshing', () => {
      render(<Header onRefresh={mockOnRefresh} isRefreshing={true} />);

      expect(screen.getByText('Actualizando...')).toBeInTheDocument();
      expect(screen.queryByText('Actualizar Datos')).not.toBeInTheDocument();
    });
  });

  describe('Layout and structure', () => {
    it('should have proper header structure', () => {
      render(<Header onRefresh={mockOnRefresh} isRefreshing={false} />);

      const header = screen.getByRole('banner');
      expect(header).toBeInTheDocument();
      expect(header.tagName).toBe('HEADER');
    });

    it('should have title as h1 element', () => {
      render(<Header onRefresh={mockOnRefresh} isRefreshing={false} />);

      const title = screen.getByRole('heading', { level: 1 });
      expect(title).toBeInTheDocument();
      expect(title).toHaveTextContent('SIFU');
    });

    it('should have proper CSS classes for layout', () => {
      render(<Header onRefresh={mockOnRefresh} isRefreshing={false} />);

      const header = screen.getByRole('banner');
      expect(header).toHaveClass('bg-white', 'shadow-sm', 'border-b', 'border-gray-200');
    });
  });

  describe('Props validation', () => {
    it('should handle missing onRefresh prop gracefully', () => {
      expect(() => {
        render(<Header isRefreshing={false} />);
      }).not.toThrow();
    });

    it('should handle missing isRefreshing prop gracefully', () => {
      expect(() => {
        render(<Header onRefresh={mockOnRefresh} />);
      }).not.toThrow();
    });

    it('should handle both props missing gracefully', () => {
      expect(() => {
        render(<Header />);
      }).not.toThrow();
    });
  });

  describe('Accessibility', () => {
    it('should have accessible button', () => {
      render(<Header onRefresh={mockOnRefresh} isRefreshing={false} />);

      const refreshButton = screen.getByRole('button');
      expect(refreshButton).toBeInTheDocument();
    });

    it('should have accessible heading', () => {
      render(<Header onRefresh={mockOnRefresh} isRefreshing={false} />);

      const heading = screen.getByRole('heading', { level: 1 });
      expect(heading).toBeInTheDocument();
    });

    it('should have proper button state for screen readers', () => {
      render(<Header onRefresh={mockOnRefresh} isRefreshing={true} />);

      const refreshButton = screen.getByRole('button');
      expect(refreshButton).toBeDisabled();
    });
  });

  describe('Integration tests', () => {
    it('should work with multiple rapid clicks when enabled', () => {
      render(<Header onRefresh={mockOnRefresh} isRefreshing={false} />);

      const refreshButton = screen.getByRole('button');
      fireEvent.click(refreshButton);
      fireEvent.click(refreshButton);
      fireEvent.click(refreshButton);

      expect(mockOnRefresh).toHaveBeenCalledTimes(3);
    });

    it('should maintain state consistency during refresh cycle', () => {
      const { rerender } = render(<Header onRefresh={mockOnRefresh} isRefreshing={false} />);

      // Estado inicial
      let refreshButton = screen.getByRole('button');
      expect(refreshButton).not.toBeDisabled();
      expect(refreshButton).toHaveTextContent('Actualizar Datos');

      // Cambiar a refreshing
      rerender(<Header onRefresh={mockOnRefresh} isRefreshing={true} />);

      refreshButton = screen.getByRole('button');
      expect(refreshButton).toBeDisabled();
      expect(refreshButton).toHaveTextContent('Actualizando...');

      // Volver a estado normal
      rerender(<Header onRefresh={mockOnRefresh} isRefreshing={false} />);

      refreshButton = screen.getByRole('button');
      expect(refreshButton).not.toBeDisabled();
      expect(refreshButton).toHaveTextContent('Actualizar Datos');
    });
  });

  describe('Component behavior edge cases', () => {
    it('should handle undefined onRefresh callback', () => {
      render(<Header onRefresh={undefined} isRefreshing={false} />);

      const refreshButton = screen.getByRole('button');
      expect(() => {
        fireEvent.click(refreshButton);
      }).not.toThrow();
    });

    it('should handle boolean props correctly', () => {
      render(<Header onRefresh={mockOnRefresh} isRefreshing={null} />);

      const refreshButton = screen.getByRole('button');
      expect(refreshButton).not.toBeDisabled(); // null should be falsy
    });

    it('should render with minimal props', () => {
      render(<Header />);

      expect(screen.getByText('SIFU')).toBeInTheDocument();
      expect(screen.getByRole('button')).toBeInTheDocument();
    });
  });
}); 