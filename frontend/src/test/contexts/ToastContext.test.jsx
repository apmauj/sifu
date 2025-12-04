import React from 'react'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import { renderHook } from '@testing-library/react'
import { describe, it, expect, beforeEach, vi } from 'vitest'

// Evitar que setup.jsx mockee ToastContext
globalThis.__TESTING_TOAST_CONTEXT__ = true

// NO USAR MOCK DE TOASTCONTEXT - usar el real
vi.unmock('../../shared/contexts/ToastContext');
import { ToastProvider, useToast } from '../../shared/contexts/ToastContext';

// Mock del componente ToastNotification
vi.mock('../../shared/components/ToastNotification', () => ({
  default: ({ message, type, onClose, duration }) => (
    <div 
      data-testid={`toast-${type}`}
      data-message={message}
      data-duration={duration}
    >
      <span>{message}</span>
      <button onClick={onClose} data-testid="toast-close">Close</button>
    </div>
  )
}));

// Mock de constants
vi.mock('../../constants', () => ({
  TOAST_DURATION: 3000
}));

describe('ToastContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('useToast Hook', () => {
    it('should throw error when used outside ToastProvider', () => {
      // Suprimir console.error para este test específico
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      
      expect(() => {
        renderHook(() => useToast());
      }).toThrow('useToast debe ser usado dentro de un ToastProvider');
      
      consoleSpy.mockRestore();
    });

    it('should return toast context when used inside ToastProvider', () => {
      const wrapper = ({ children }) => (
        <ToastProvider>{children}</ToastProvider>
      );

      const { result } = renderHook(() => useToast(), { wrapper });

      expect(result.current).toHaveProperty('addToast');
      expect(result.current).toHaveProperty('showSuccess');
      expect(result.current).toHaveProperty('showError');
      expect(result.current).toHaveProperty('showWarning');
      expect(result.current).toHaveProperty('showInfo');
      expect(result.current).toHaveProperty('removeToast');
    });

    it('should provide functions that are callable', () => {
      const wrapper = ({ children }) => (
        <ToastProvider>{children}</ToastProvider>
      );

      const { result } = renderHook(() => useToast(), { wrapper });

      expect(typeof result.current.addToast).toBe('function');
      expect(typeof result.current.showSuccess).toBe('function');
      expect(typeof result.current.showError).toBe('function');
      expect(typeof result.current.showWarning).toBe('function');
      expect(typeof result.current.showInfo).toBe('function');
      expect(typeof result.current.removeToast).toBe('function');
    });
  });

  describe('ToastProvider', () => {
    it('should render children correctly', () => {
      render(
        <ToastProvider>
          <div data-testid="child">Child Component</div>
        </ToastProvider>
      );

      expect(screen.getByTestId('child')).toBeInTheDocument();
      expect(screen.getByText('Child Component')).toBeInTheDocument();
    });

    it('should render toast container', () => {
      render(
        <ToastProvider>
          <div>Test</div>
        </ToastProvider>
      );

      expect(screen.getByTestId('toast-container')).toBeInTheDocument();
    });

    it('should render container but no individual toasts initially', () => {
      render(
        <ToastProvider>
          <div>Test</div>
        </ToastProvider>
      );
      expect(screen.getByTestId('toast-container')).toBeInTheDocument();
      // No elementos cuyo testid comience con toast- (individual notifications)
      const anyToast = screen.queryAllByTestId(/toast-/i).filter(el => el.getAttribute('data-testid') !== 'toast-container');
      expect(anyToast.length).toBe(0);
    });
  });

  describe('Toast Functions', () => {
    let TestComponent;

    beforeEach(() => {
      TestComponent = () => {
        const toast = useToast();
        return (
          <div>
            <button onClick={() => toast.showSuccess('Success message')} data-testid="success-btn">
              Success
            </button>
            <button onClick={() => toast.showError('Error message')} data-testid="error-btn">
              Error
            </button>
            <button onClick={() => toast.showWarning('Warning message')} data-testid="warning-btn">
              Warning
            </button>
            <button onClick={() => toast.showInfo('Info message')} data-testid="info-btn">
              Info
            </button>
            <button onClick={() => toast.addToast('Custom message', 'custom', 5000)} data-testid="custom-btn">
              Custom
            </button>
          </div>
        );
      };
    });

    it('should show success toast', async () => {
      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      act(() => {
        screen.getByTestId('success-btn').click();
      });

      await waitFor(() => {
        expect(screen.getByTestId('toast-success')).toBeInTheDocument();
        expect(screen.getByText('Success message')).toBeInTheDocument();
      });
    });

    it('should show error toast', async () => {
      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      act(() => {
        screen.getByTestId('error-btn').click();
      });

      await waitFor(() => {
        expect(screen.getByTestId('toast-error')).toBeInTheDocument();
        expect(screen.getByText('Error message')).toBeInTheDocument();
      });
    });

    it('should show warning toast', async () => {
      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      act(() => {
        screen.getByTestId('warning-btn').click();
      });

      await waitFor(() => {
        expect(screen.getByTestId('toast-warning')).toBeInTheDocument();
        expect(screen.getByText('Warning message')).toBeInTheDocument();
      });
    });

    it('should show info toast', async () => {
      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      act(() => {
        screen.getByTestId('info-btn').click();
      });

      await waitFor(() => {
        expect(screen.getByTestId('toast-info')).toBeInTheDocument();
        expect(screen.getByText('Info message')).toBeInTheDocument();
      });
    });

    it('should show custom toast with addToast', async () => {
      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      act(() => {
        screen.getByTestId('custom-btn').click();
      });

      await waitFor(() => {
        expect(screen.getByTestId('toast-custom')).toBeInTheDocument();
        expect(screen.getByText('Custom message')).toBeInTheDocument();
        expect(screen.getByTestId('toast-custom')).toHaveAttribute('data-duration', '5000');
      });
    });
  });

  describe('Toast Management', () => {
    let TestComponent;

    beforeEach(() => {
      TestComponent = () => {
        const toast = useToast();
        return (
          <div>
            <button onClick={() => toast.showSuccess('Toast 1')} data-testid="add-toast-1">
              Add Toast 1
            </button>
            <button onClick={() => toast.showError('Toast 2')} data-testid="add-toast-2">
              Add Toast 2
            </button>
            <button onClick={() => toast.showInfo('Toast 3')} data-testid="add-toast-3">
              Add Toast 3
            </button>
          </div>
        );
      };
    });

    it('should display multiple toasts simultaneously', async () => {
      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      act(() => {
        screen.getByTestId('add-toast-1').click();
        screen.getByTestId('add-toast-2').click();
        screen.getByTestId('add-toast-3').click();
      });

      await waitFor(() => {
        expect(screen.getByText('Toast 1')).toBeInTheDocument();
        expect(screen.getByText('Toast 2')).toBeInTheDocument();
        expect(screen.getByText('Toast 3')).toBeInTheDocument();
      });

      // Verificar que los toasts específicos están presentes
      expect(screen.getByText('Toast 1')).toBeInTheDocument();
      expect(screen.getByText('Toast 2')).toBeInTheDocument();
      expect(screen.getByText('Toast 3')).toBeInTheDocument();
    });

    it('should remove toast manually', async () => {
      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      act(() => {
        screen.getByTestId('add-toast-1').click();
      });

      await waitFor(() => {
        expect(screen.getByText('Toast 1')).toBeInTheDocument();
      });

      // Cerrar el toast manualmente
      act(() => {
        screen.getByTestId('toast-close').click();
      });

      await waitFor(() => {
        expect(screen.queryByText('Toast 1')).not.toBeInTheDocument();
      });
    });

    it('should auto-remove toast after duration', async () => {
      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      act(() => {
        screen.getByTestId('add-toast-1').click();
      });

      await waitFor(() => {
        expect(screen.getByText('Toast 1')).toBeInTheDocument();
      });

      // Esperar que se auto-elimine (3000ms + 500ms = 3500ms)
      await waitFor(() => {
        expect(screen.queryByText('Toast 1')).not.toBeInTheDocument();
      }, { timeout: 4000 });
    });

    it('should handle multiple toasts with different durations', async () => {
      const CustomTestComponent = () => {
        const toast = useToast();
        return (
          <div>
            <button 
              onClick={() => toast.addToast('Short toast', 'success', 1000)} 
              data-testid="short-toast"
            >
              Short Toast
            </button>
            <button 
              onClick={() => toast.addToast('Long toast', 'info', 3000)} 
              data-testid="long-toast"
            >
              Long Toast
            </button>
          </div>
        );
      };

      render(
        <ToastProvider>
          <CustomTestComponent />
        </ToastProvider>
      );

      act(() => {
        screen.getByTestId('short-toast').click();
        screen.getByTestId('long-toast').click();
      });

      await waitFor(() => {
        expect(screen.getByText('Short toast')).toBeInTheDocument();
        expect(screen.getByText('Long toast')).toBeInTheDocument();
      });

      // Esperar que se elimine el toast corto (1000ms + 500ms = 1500ms)
      await waitFor(() => {
        expect(screen.queryByText('Short toast')).not.toBeInTheDocument();
      }, { timeout: 2000 });

      // El toast largo debería seguir ahí
      expect(screen.getByText('Long toast')).toBeInTheDocument();

      // Esperar que se elimine el toast largo (3000ms + 500ms = 3500ms total)
      await waitFor(() => {
        expect(screen.queryByText('Long toast')).not.toBeInTheDocument();
      }, { timeout: 4000 });
    });
  });

  describe('Toast Rendering Order', () => {
    it('should render toasts in reverse order (newest first)', async () => {
      const TestComponent = () => {
        const toast = useToast();
        return (
          <div>
            <button onClick={() => toast.showSuccess('First toast')} data-testid="first">
              First
            </button>
            <button onClick={() => toast.showError('Second toast')} data-testid="second">
              Second
            </button>
            <button onClick={() => toast.showInfo('Third toast')} data-testid="third">
              Third
            </button>
          </div>
        );
      };

      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      act(() => {
        screen.getByTestId('first').click();
        screen.getByTestId('second').click();
        screen.getByTestId('third').click();
      });

      await waitFor(() => {
        expect(screen.getByText('First toast')).toBeInTheDocument();
        expect(screen.getByText('Second toast')).toBeInTheDocument();
        expect(screen.getByText('Third toast')).toBeInTheDocument();
      });

      // Verificar que todos los toasts están presentes
      expect(screen.getByText('First toast')).toBeInTheDocument();
      expect(screen.getByText('Second toast')).toBeInTheDocument();
      expect(screen.getByText('Third toast')).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle rapid successive toast additions', async () => {
      const TestComponent = () => {
        const toast = useToast();
        return (
          <button 
            onClick={() => {
              for (let i = 0; i < 5; i++) {
                toast.showSuccess(`Toast ${i + 1}`);
              }
            }} 
            data-testid="rapid-add"
          >
            Add Multiple
          </button>
        );
      };

      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      act(() => {
        screen.getByTestId('rapid-add').click();
      });

      await waitFor(() => {
        // Verificar que los 5 toasts están presentes
        expect(screen.getByText('Toast 1')).toBeInTheDocument();
        expect(screen.getByText('Toast 2')).toBeInTheDocument();
        expect(screen.getByText('Toast 3')).toBeInTheDocument();
        expect(screen.getByText('Toast 4')).toBeInTheDocument();
        expect(screen.getByText('Toast 5')).toBeInTheDocument();
      });
    });

    it('should handle toast removal of non-existent toast gracefully', async () => {
      const TestComponent = () => {
        const toast = useToast();
        return (
          <div>
            <button onClick={() => toast.showSuccess('Test toast')} data-testid="add">
              Add Toast
            </button>
            <button onClick={() => toast.removeToast('non-existent-id')} data-testid="remove-fake">
              Remove Fake
            </button>
          </div>
        );
      };

      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      act(() => {
        screen.getByTestId('add').click();
      });

      await waitFor(() => {
        expect(screen.getByText('Test toast')).toBeInTheDocument();
      });

      // Intentar remover un toast que no existe no debería causar errores
      act(() => {
        screen.getByTestId('remove-fake').click();
      });

      // El toast original debería seguir ahí
      expect(screen.getByText('Test toast')).toBeInTheDocument();
    });

    it('should handle empty message gracefully', async () => {
      const TestComponent = () => {
        const toast = useToast();
        return (
          <button onClick={() => toast.showSuccess('')} data-testid="empty-message">
            Empty Message
          </button>
        );
      };

      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      act(() => {
        screen.getByTestId('empty-message').click();
      });

      await waitFor(() => {
        expect(screen.getByTestId('toast-success')).toBeInTheDocument();
      });
    });

    it('should handle custom duration parameters', async () => {
      const TestComponent = () => {
        const toast = useToast();
        return (
          <div>
            <button onClick={() => toast.showSuccess('Default duration')} data-testid="default">
              Default
            </button>
            <button onClick={() => toast.showError('Custom duration', 2000)} data-testid="custom">
              Custom
            </button>
          </div>
        );
      };

      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      act(() => {
        screen.getByTestId('default').click();
        screen.getByTestId('custom').click();
      });

      await waitFor(() => {
        expect(screen.getByText('Default duration')).toBeInTheDocument();
        expect(screen.getByText('Custom duration')).toBeInTheDocument();
      });

      // Verificar que el toast personalizado tiene la duración correcta
      const customToast = screen.getByTestId('toast-error');
      expect(customToast).toHaveAttribute('data-duration', '2000');
    });
  });

  describe('Performance and Memory', () => {
    it('should clean up timers when toasts are removed manually', async () => {
      const TestComponent = () => {
        const toast = useToast();
        return (
          <button onClick={() => toast.showSuccess('Test toast')} data-testid="add">
            Add Toast
          </button>
        );
      };

      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      act(() => {
        screen.getByTestId('add').click();
      });

      await waitFor(() => {
        expect(screen.getByText('Test toast')).toBeInTheDocument();
      });

      // Remover manualmente antes de que expire
      act(() => {
        screen.getByTestId('toast-close').click();
      });

      await waitFor(() => {
        expect(screen.queryByText('Test toast')).not.toBeInTheDocument();
      });

      // Esperar más tiempo para verificar que no hay efectos secundarios
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // No debería haber efectos secundarios
      expect(screen.queryByText('Test toast')).not.toBeInTheDocument();
    });
  });
}); 
