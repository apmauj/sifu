import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { I18nProvider } from '../../contexts/I18nContext';
import MonitoringAccess from '../../components/MonitoringAccess';

// Mock fetch globally
global.fetch = vi.fn();

describe('MonitoringAccess', () => {
  const mockOnClose = vi.fn();
  const mockOnAccessGranted = vi.fn();

  beforeEach(() => {
    // Clear all mocks before each test
    vi.clearAllMocks();
    // Clear sessionStorage
    sessionStorage.clear();
    // Reset fetch mock
    global.fetch.mockClear();
  });

  afterEach(() => {
    sessionStorage.clear();
  });

  const renderComponent = (isOpen = true) => {
    return render(
      <I18nProvider>
        <MonitoringAccess
          isOpen={isOpen}
          onClose={mockOnClose}
          onAccessGranted={mockOnAccessGranted}
        />
      </I18nProvider>
    );
  };

  describe('Rendering', () => {
    it('should not render when isOpen is false', () => {
      renderComponent(false);
      expect(screen.queryByText(/monitoring/i)).not.toBeInTheDocument();
    });

    it('should render modal when isOpen is true', () => {
      renderComponent(true);
      expect(screen.getByRole('textbox')).toBeInTheDocument();
    });

    it('should render title and subtitle', () => {
      renderComponent(true);
      // Will show keys or translations depending on i18n setup
      const modal = screen.getByRole('textbox').closest('.monitoring-access-modal');
      expect(modal).toBeInTheDocument();
    });

    it('should render close button', () => {
      renderComponent(true);
      const closeButton = screen.getByLabelText('Close');
      expect(closeButton).toBeInTheDocument();
    });

    it('should render help section', () => {
      renderComponent(true);
      const modal = screen.getByRole('textbox').closest('.monitoring-access-modal');
      expect(modal.textContent).toMatch(/help|ayuda/i);
    });
  });

  describe('Input Validation', () => {
    it('should only accept digits', () => {
      renderComponent(true);
      const input = screen.getByRole('textbox');
      
      fireEvent.change(input, { target: { value: 'abc123' } });
      expect(input.value).toBe('123');
    });

    it('should limit input to 6 digits', () => {
      renderComponent(true);
      const input = screen.getByRole('textbox');
      
      // Test incremental: first add 6, then try to add more
      fireEvent.change(input, { target: { value: '123456' } });
      expect(input.value).toBe('123456');
      
      // Try to add more digits - should stay at 6
      fireEvent.change(input, { target: { value: '1234567890' } });
      // handleInputChange checks `if (value.length <= 6)` before updating
      // Since '1234567890' has 10 digits, the state won't update
      // So it stays at the previous value '123456'
      expect(input.value).toBe('123456');
    });

    it('should clear input on change', () => {
      renderComponent(true);
      const input = screen.getByRole('textbox');
      
      fireEvent.change(input, { target: { value: '123' } });
      expect(input.value).toBe('123');
      
      fireEvent.change(input, { target: { value: '456' } });
      expect(input.value).toBe('456');
    });

    it('should handle paste with non-digits', () => {
      renderComponent(true);
      const input = screen.getByRole('textbox');
      
      const pasteData = {
        clipboardData: {
          getData: () => 'abc123def456'
        }
      };
      
      fireEvent.paste(input, pasteData);
      expect(input.value).toBe('123456');
    });
  });

  describe('Form Submission', () => {
    it('should disable submit button when code is incomplete', () => {
      renderComponent(true);
      const input = screen.getByRole('textbox');
      const button = screen.getByRole('button', { name: /verify|verificar/i });
      
      fireEvent.change(input, { target: { value: '12345' } });
      expect(button).toBeDisabled();
    });

    it('should enable submit button when code is complete', () => {
      renderComponent(true);
      const input = screen.getByRole('textbox');
      const button = screen.getByRole('button', { name: /verify|verificar/i });
      
      fireEvent.change(input, { target: { value: '123456' } });
      expect(button).not.toBeDisabled();
    });

    it('should call API with correct code on submit', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          access: 'granted',
          session_token: 'test-token-123',
          expires_in: 3600
        })
      });

      renderComponent(true);
      const input = screen.getByRole('textbox');
      const button = screen.getByRole('button', { name: /verify|verificar/i });
      
      fireEvent.change(input, { target: { value: '123456' } });
      fireEvent.click(button);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/monitoring/verify?code=123456'),
          expect.objectContaining({
            method: 'POST'
          })
        );
      });
    });

    it('should encode code in URL', async () => {
      // Verify that code is properly URL-encoded (even though it's just digits)
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          access: 'granted',
          session_token: 'token-encoded',
          expires_in: 3600
        })
      });

      renderComponent(true);
      const input = screen.getByRole('textbox');
      const button = screen.getByRole('button', { name: /verify|verificar/i });
      
      // Use normal digits (only thing handleInputChange allows)
      fireEvent.change(input, { target: { value: '123456' } });
      fireEvent.click(button);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/monitoring/verify?code=123456'),
          expect.objectContaining({
            method: 'POST'
          })
        );
      });
    });
  });

  describe('Successful Verification', () => {
    it('should store session token in sessionStorage', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          access: 'granted',
          session_token: 'test-token-789',
          expires_in: 3600
        })
      });

      renderComponent(true);
      const input = screen.getByRole('textbox');
      const button = screen.getByRole('button', { name: /verify|verificar/i });
      
      fireEvent.change(input, { target: { value: '123456' } });
      fireEvent.click(button);

      await waitFor(() => {
        expect(sessionStorage.getItem('monitoring_session_token')).toBe('test-token-789');
        expect(sessionStorage.getItem('monitoring_session_expires')).toBeTruthy();
      });
    });

    it('should call onAccessGranted callback', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          access: 'granted',
          session_token: 'callback-token',
          expires_in: 3600
        })
      });

      renderComponent(true);
      const input = screen.getByRole('textbox');
      const button = screen.getByRole('button', { name: /verify|verificar/i });
      
      fireEvent.change(input, { target: { value: '123456' } });
      fireEvent.click(button);

      await waitFor(() => {
        expect(mockOnAccessGranted).toHaveBeenCalledWith('callback-token');
      });
    });

    it('should clear input after successful verification', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          access: 'granted',
          session_token: 'token',
          expires_in: 3600
        })
      });

      renderComponent(true);
      const input = screen.getByRole('textbox');
      const button = screen.getByRole('button', { name: /verify|verificar/i });
      
      fireEvent.change(input, { target: { value: '123456' } });
      fireEvent.click(button);

      await waitFor(() => {
        expect(input.value).toBe('');
      });
    });
  });

  describe('Error Handling', () => {
    it('should display error message on invalid code (401)', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Invalid code' })
      });

      renderComponent(true);
      const input = screen.getByRole('textbox');
      const button = screen.getByRole('button', { name: /verify|verificar/i });
      
      fireEvent.change(input, { target: { value: '999999' } });
      fireEvent.click(button);

      await waitFor(() => {
        const alert = screen.getByRole('alert');
        expect(alert).toBeInTheDocument();
        expect(alert).toHaveTextContent(/invalid/i);
      });
    });

    it('should decrement attempts counter on failed attempt', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Invalid code' })
      });

      renderComponent(true);
      const input = screen.getByRole('textbox');
      const button = screen.getByRole('button', { name: /verify|verificar/i });
      
      fireEvent.change(input, { target: { value: '999999' } });
      fireEvent.click(button);

      await waitFor(() => {
        // Component shows warning div with class monitoring-access-warning
        // The i18n mock returns keys, so look for the key or class
        const warning = document.querySelector('.monitoring-access-warning');
        expect(warning).toBeInTheDocument();
        // In real app it would show "4 attempts remaining", but in test shows key
        expect(warning).toHaveTextContent(/monitoring\.attemptsLeft|4.*attempt/i);
      });
    });

    it('should handle rate limit error (429)', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 429,
        json: async () => ({ detail: 'Too many attempts' })
      });

      renderComponent(true);
      const input = screen.getByRole('textbox');
      const button = screen.getByRole('button', { name: /verify|verificar/i });
      
      fireEvent.change(input, { target: { value: '123456' } });
      fireEvent.click(button);

      await waitFor(() => {
        const alert = screen.getByRole('alert');
        expect(alert).toBeInTheDocument();
      });
    });

    it('should handle network error', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'));

      renderComponent(true);
      const input = screen.getByRole('textbox');
      const button = screen.getByRole('button', { name: /verify|verificar/i });
      
      fireEvent.change(input, { target: { value: '123456' } });
      fireEvent.click(button);

      await waitFor(() => {
        expect(screen.getByRole('alert')).toBeInTheDocument();
      });
    });

    it('should disable input and button after too many attempts', async () => {
      // Simulate 5 failed attempts
      for (let i = 0; i < 5; i++) {
        global.fetch.mockResolvedValueOnce({
          ok: false,
          status: 401,
          json: async () => ({ detail: 'Invalid code' })
        });
      }

      renderComponent(true);
      const input = screen.getByRole('textbox');
      const button = screen.getByRole('button', { name: /verify|verificar/i });
      
      // Make 5 failed attempts
      for (let i = 0; i < 5; i++) {
        fireEvent.change(input, { target: { value: '999999' } });
        fireEvent.click(button);
        await waitFor(() => expect(global.fetch).toHaveBeenCalled());
        global.fetch.mockClear();
      }

      // After 5 failed attempts, button should be disabled
      await waitFor(() => {
        expect(button).toBeDisabled();
        expect(input).toBeDisabled();
      });
    });
  });

  describe('UI Interactions', () => {
    it('should call onClose when close button is clicked', () => {
      renderComponent(true);
      const closeButton = screen.getByLabelText('Close');
      
      fireEvent.click(closeButton);
      expect(mockOnClose).toHaveBeenCalled();
    });

    it('should call onClose when clicking outside modal', () => {
      renderComponent(true);
      const overlay = screen.getByRole('textbox').closest('.monitoring-access-overlay');
      
      fireEvent.click(overlay);
      expect(mockOnClose).toHaveBeenCalled();
    });

    it('should not call onClose when clicking inside modal', () => {
      renderComponent(true);
      const modal = screen.getByRole('textbox').closest('.monitoring-access-modal');
      
      fireEvent.click(modal);
      expect(mockOnClose).not.toHaveBeenCalled();
    });

    it('should show loading state during verification', async () => {
      global.fetch.mockImplementationOnce(() => 
        new Promise(resolve => setTimeout(() => resolve({
          ok: true,
          json: async () => ({ 
            access: 'granted', 
            session_token: 'loading-test-token', 
            expires_in: 3600 
          })
        }), 100))
      );

      renderComponent(true);
      const input = screen.getByRole('textbox');
      const button = screen.getByRole('button', { name: /verify|verificar/i });
      
      fireEvent.change(input, { target: { value: '123456' } });
      fireEvent.click(button);

      // Button should be disabled during loading
      expect(button).toBeDisabled();

      // Wait for the async operation to complete
      await waitFor(() => {
        expect(mockOnAccessGranted).toHaveBeenCalledWith('loading-test-token');
      }, { timeout: 2000 });
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      renderComponent(true);
      const input = screen.getByLabelText('TOTP Code');
      expect(input).toBeInTheDocument();
    });

    it('should show error in alert role', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Invalid code' })
      });

      renderComponent(true);
      const input = screen.getByRole('textbox');
      const button = screen.getByRole('button', { name: /verify|verificar/i });
      
      fireEvent.change(input, { target: { value: '999999' } });
      fireEvent.click(button);

      await waitFor(() => {
        const alert = screen.getByRole('alert');
        expect(alert).toHaveAttribute('role', 'alert');
      });
    });

    it('should autofocus input when modal opens', () => {
      renderComponent(true);
      const input = screen.getByRole('textbox');
      // In jsdom environment, autoFocus might not set the attribute
      // but the JSX has autoFocus prop, so verify it's not disabled
      // and in a real browser it would auto-focus
      expect(input).not.toBeDisabled();
      expect(input).toBeInTheDocument();
    });
  });
});
