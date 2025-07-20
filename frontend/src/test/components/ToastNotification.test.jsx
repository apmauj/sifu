import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ToastNotification from '../../components/ToastNotification.jsx';
import { TOAST_DURATION } from '../../constants.js';

describe('ToastNotification Component', () => {
  const defaultProps = {
    message: 'Test message',
    type: 'success',
    onClose: vi.fn()
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Basic rendering', () => {
    it('should render toast with message', () => {
      render(<ToastNotification {...defaultProps} />);

      expect(screen.getByText('Test message')).toBeInTheDocument();
    });

    it('should render close button', () => {
      render(<ToastNotification {...defaultProps} />);

      const closeButton = screen.getByRole('button');
      expect(closeButton).toBeInTheDocument();
      expect(closeButton).toHaveTextContent('✕');
    });

    it('should render progress bar', () => {
      render(<ToastNotification {...defaultProps} />);

      const progressBar = document.querySelector('.toast-progress-bar');
      expect(progressBar).toBeInTheDocument();
    });

    it('should be visible initially', () => {
      render(<ToastNotification {...defaultProps} />);

      const toast = screen.getByText('Test message').closest('div[class*="max-w-sm"]');
      expect(toast).toBeInTheDocument();
    });

    it('should have proper container structure', () => {
      render(<ToastNotification {...defaultProps} />);

      const container = screen.getByText('Test message').closest('div[class*="bg-green-50"]');
      expect(container).toBeInTheDocument();
      expect(container).toHaveClass('border', 'rounded-lg', 'shadow-lg', 'p-4');
    });
  });

  describe('Toast types and styling', () => {
    it('should render success toast with correct styling', () => {
      render(<ToastNotification {...defaultProps} type="success" />);

      expect(screen.getByText('✅')).toBeInTheDocument();
      const container = screen.getByText('Test message').closest('div[class*="bg-green-50"]');
      expect(container).toBeInTheDocument();
    });

    it('should render error toast with correct styling', () => {
      render(<ToastNotification {...defaultProps} type="error" />);

      expect(screen.getByText('❌')).toBeInTheDocument();
      const container = screen.getByText('Test message').closest('div[class*="bg-red-50"]');
      expect(container).toBeInTheDocument();
    });

    it('should render warning toast with correct styling', () => {
      render(<ToastNotification {...defaultProps} type="warning" />);

      expect(screen.getByText('⚠️')).toBeInTheDocument();
      const container = screen.getByText('Test message').closest('div[class*="bg-yellow-50"]');
      expect(container).toBeInTheDocument();
    });

    it('should render info toast with correct styling', () => {
      render(<ToastNotification {...defaultProps} type="info" />);

      expect(screen.getByText('ℹ️')).toBeInTheDocument();
      const container = screen.getByText('Test message').closest('div[class*="bg-blue-50"]');
      expect(container).toBeInTheDocument();
    });

    it('should render default toast with correct styling', () => {
      render(<ToastNotification {...defaultProps} type="unknown" />);

      expect(screen.getByText('📢')).toBeInTheDocument();
      const container = screen.getByText('Test message').closest('div[class*="bg-gray-50"]');
      expect(container).toBeInTheDocument();
    });

    it('should default to success type when type is not provided', () => {
      render(<ToastNotification message="Test" onClose={vi.fn()} />);

      expect(screen.getByText('✅')).toBeInTheDocument();
    });

    it('should have correct icon background colors', () => {
      const { rerender } = render(<ToastNotification {...defaultProps} type="success" />);
      expect(document.querySelector('.bg-green-100')).toBeInTheDocument();

      rerender(<ToastNotification {...defaultProps} type="error" />);
      expect(document.querySelector('.bg-red-100')).toBeInTheDocument();

      rerender(<ToastNotification {...defaultProps} type="warning" />);
      expect(document.querySelector('.bg-yellow-100')).toBeInTheDocument();

      rerender(<ToastNotification {...defaultProps} type="info" />);
      expect(document.querySelector('.bg-blue-100')).toBeInTheDocument();
    });
  });

  describe('Progress bar colors', () => {
    it('should show green progress bar for success', () => {
      render(<ToastNotification {...defaultProps} type="success" />);

      const progressBar = document.querySelector('.bg-green-400');
      expect(progressBar).toBeInTheDocument();
    });

    it('should show red progress bar for error', () => {
      render(<ToastNotification {...defaultProps} type="error" />);

      const progressBar = document.querySelector('.bg-red-400');
      expect(progressBar).toBeInTheDocument();
    });

    it('should show yellow progress bar for warning', () => {
      render(<ToastNotification {...defaultProps} type="warning" />);

      const progressBar = document.querySelector('.bg-yellow-400');
      expect(progressBar).toBeInTheDocument();
    });

    it('should show blue progress bar for info', () => {
      render(<ToastNotification {...defaultProps} type="info" />);

      const progressBar = document.querySelector('.bg-blue-400');
      expect(progressBar).toBeInTheDocument();
    });

    it('should show gray progress bar for default', () => {
      render(<ToastNotification {...defaultProps} type="unknown" />);

      const progressBar = document.querySelector('.bg-gray-400');
      expect(progressBar).toBeInTheDocument();
    });
  });

  describe('Animation behavior', () => {
    it('should start with animation state false', () => {
      render(<ToastNotification {...defaultProps} />);

      const toast = screen.getByText('Test message').closest('div[class*="max-w-sm"]');
      expect(toast).toHaveClass('-translate-x-full', 'translate-y-4', 'opacity-0');
    });

    it('should have animation classes ready for transition', () => {
      render(<ToastNotification {...defaultProps} />);

      const toast = screen.getByText('Test message').closest('div[class*="max-w-sm"]');
      expect(toast).toHaveClass('transform', 'transition-all', 'duration-300', 'ease-in-out');
    });

    it('should have proper layout structure', () => {
      render(<ToastNotification {...defaultProps} />);

      const toast = screen.getByText('Test message').closest('div[class*="max-w-sm"]');
      expect(toast).toHaveClass('max-w-sm', 'w-full');
    });
  });

  describe('Manual close functionality', () => {
    it('should call onClose when close button is clicked', async () => {
      const onClose = vi.fn();
      render(<ToastNotification message="Test" onClose={onClose} />);

      const closeButton = screen.getByRole('button');
      fireEvent.click(closeButton);

      // Wait for the 300ms animation delay
      await waitFor(() => {
        expect(onClose).toHaveBeenCalledTimes(1);
      }, { timeout: 500 });
    });

    it('should handle close without onClose callback', () => {
      render(<ToastNotification message="Test" />);

      const closeButton = screen.getByRole('button');
      
      expect(() => {
        fireEvent.click(closeButton);
      }).not.toThrow();
    });

    it('should have clickable close button', () => {
      render(<ToastNotification {...defaultProps} />);

      const closeButton = screen.getByRole('button');
      expect(closeButton).toBeEnabled();
      expect(closeButton).toHaveClass('p-1', 'rounded-full');
    });
  });

  describe('Component structure and layout', () => {
    it('should have proper flex layout', () => {
      render(<ToastNotification {...defaultProps} />);

      const flexContainer = document.querySelector('.flex.items-start');
      expect(flexContainer).toBeInTheDocument();
    });

    it('should have icon container with proper styling', () => {
      render(<ToastNotification {...defaultProps} />);

      const iconContainer = document.querySelector('.flex-shrink-0.w-8.h-8.rounded-full');
      expect(iconContainer).toBeInTheDocument();
      expect(iconContainer).toHaveClass('flex', 'items-center', 'justify-center', 'mr-3');
    });

    it('should have message container with proper styling', () => {
      render(<ToastNotification {...defaultProps} />);

      const messageContainer = document.querySelector('.flex-1.min-w-0');
      expect(messageContainer).toBeInTheDocument();
    });

    it('should have progress bar container with proper styling', () => {
      render(<ToastNotification {...defaultProps} />);

      const progressContainer = document.querySelector('.mt-2.w-full');
      expect(progressContainer).toBeInTheDocument();
      expect(progressContainer).toHaveClass('bg-white', 'bg-opacity-30', 'rounded-full', 'h-1');
    });
  });

  describe('Accessibility and interaction', () => {
    it('should have accessible close button', () => {
      render(<ToastNotification {...defaultProps} />);

      const closeButton = screen.getByRole('button');
      expect(closeButton).toBeInTheDocument();
    });

    it('should handle hover effects on close button', () => {
      render(<ToastNotification {...defaultProps} />);

      const closeButton = screen.getByRole('button');
      expect(closeButton).toHaveClass('hover:bg-white', 'hover:bg-opacity-20');
    });

    it('should have proper ARIA structure', () => {
      render(<ToastNotification {...defaultProps} />);

      const toast = screen.getByText('Test message').closest('div[class*="max-w-sm"]');
      expect(toast).toBeInTheDocument();
    });

    it('should have semantic message structure', () => {
      render(<ToastNotification {...defaultProps} />);

      const messageElement = screen.getByText('Test message');
      expect(messageElement.tagName).toBe('P');
      expect(messageElement).toHaveClass('text-sm', 'font-medium');
    });
  });

  describe('Edge cases and error handling', () => {
    it('should handle empty message', () => {
      render(<ToastNotification message="" onClose={vi.fn()} />);

      const messageElement = document.querySelector('p.text-sm.font-medium');
      expect(messageElement).toBeInTheDocument();
    });

    it('should handle very long messages', () => {
      const longMessage = 'This is a very long message that might wrap to multiple lines and should still be displayed correctly in the toast notification component.';
      render(<ToastNotification message={longMessage} onClose={vi.fn()} />);

      expect(screen.getByText(longMessage)).toBeInTheDocument();
    });

    it('should handle missing props gracefully', () => {
      expect(() => {
        render(<ToastNotification />);
      }).not.toThrow();
    });

    it('should handle null message', () => {
      expect(() => {
        render(<ToastNotification message={null} onClose={vi.fn()} />);
      }).not.toThrow();
    });

    it('should handle undefined onClose', () => {
      expect(() => {
        render(<ToastNotification message="Test" onClose={undefined} />);
      }).not.toThrow();
    });

    it('should handle special characters in message', () => {
      const specialMessage = 'Message with émojis 🎉 & special chars: <>&"\'';
      render(<ToastNotification message={specialMessage} onClose={vi.fn()} />);

      expect(screen.getByText(specialMessage)).toBeInTheDocument();
    });
  });

  describe('Progress bar animation', () => {
    it('should have correct animation duration', () => {
      const customDuration = 3000;
      render(<ToastNotification {...defaultProps} duration={customDuration} />);

      const progressBar = document.querySelector('.toast-progress-bar');
      expect(progressBar).toHaveStyle(`animation: toast-shrink ${customDuration}ms linear`);
    });

    it('should use default duration for progress bar when not specified', () => {
      render(<ToastNotification message="Test" onClose={vi.fn()} />);

      const progressBar = document.querySelector('.toast-progress-bar');
      expect(progressBar).toHaveStyle(`animation: toast-shrink ${TOAST_DURATION}ms linear`);
    });

    it('should have progress bar with correct width', () => {
      render(<ToastNotification {...defaultProps} />);

      const progressBar = document.querySelector('.toast-progress-bar');
      expect(progressBar).toHaveStyle('width: 100%');
    });

    it('should handle zero duration', () => {
      render(<ToastNotification message="Test" duration={0} onClose={vi.fn()} />);

      const progressBar = document.querySelector('.toast-progress-bar');
      expect(progressBar).toHaveStyle('animation: toast-shrink 0ms linear');
    });

    it('should handle negative duration', () => {
      render(<ToastNotification message="Test" duration={-1000} onClose={vi.fn()} />);

      const progressBar = document.querySelector('.toast-progress-bar');
      expect(progressBar).toHaveStyle('animation: toast-shrink -1000ms linear');
    });
  });

  describe('Component props validation', () => {
    it('should handle all valid toast types', () => {
      const types = ['success', 'error', 'warning', 'info'];
      const icons = ['✅', '❌', '⚠️', 'ℹ️'];

      types.forEach((type, index) => {
        const { unmount } = render(<ToastNotification message="Test" type={type} onClose={vi.fn()} />);
        expect(screen.getByText(icons[index])).toBeInTheDocument();
        unmount();
      });
    });

    it('should handle duration prop correctly', () => {
      const durations = [1000, 2000, 5000];

      durations.forEach(duration => {
        const { unmount } = render(<ToastNotification message="Test" duration={duration} onClose={vi.fn()} />);
        const progressBar = document.querySelector('.toast-progress-bar');
        expect(progressBar).toHaveStyle(`animation: toast-shrink ${duration}ms linear`);
        unmount();
      });
    });

    it('should maintain consistent styling across different props', () => {
      render(<ToastNotification message="Test" type="error" duration={2000} onClose={vi.fn()} />);

      expect(screen.getByText('❌')).toBeInTheDocument();
      expect(document.querySelector('.bg-red-400')).toBeInTheDocument();
      expect(document.querySelector('.toast-progress-bar')).toHaveStyle('animation: toast-shrink 2000ms linear');
    });
  });
}); 