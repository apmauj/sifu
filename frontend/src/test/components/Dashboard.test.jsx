import React from 'react';
import { render, screen, waitFor, cleanup } from '@testing-library/react';
import { I18nProvider } from '../../shared/contexts/I18nContext';
import Dashboard from '../../features/dashboard/Dashboard.jsx';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';

// Mock services to prevent async operations after test teardown
vi.mock('../../shared/services/healthService', () => ({
  default: {
    getAdvancedHealth: vi.fn(() => Promise.resolve({ status: 'healthy', checks: [] })),
  },
}));

vi.mock('../../shared/services/performanceService', () => ({
  default: {
    getBudgets: vi.fn(() => Promise.resolve({ budgets: [] })),
    getBudgetStatus: vi.fn(() => Promise.resolve({ status: 'ok' })),
    getThroughput: vi.fn(() => Promise.resolve({ requests_per_second: 0 })),
    getServiceStatus: vi.fn(() => Promise.resolve({ status: 'ok' })),
  },
}));

// Smoke test simple que monta el Dashboard con la prop isOpen para que se rendericen las claves i18n.
// No mockeamos servicios aquí: el objetivo es que el árbol inicial incluya las llamadas t('dashboard.*')
// para que el test de claves huérfanas las recoja durante el escaneo estático.

describe('Dashboard Component (i18n)', () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it('renders translated dashboard structure when open', async () => {
    render(
      <I18nProvider forceEmbedded>
        <Dashboard isOpen={true} onClose={() => {}} />
      </I18nProvider>
    );

    // Con forceEmbedded las traducciones están inmediatas.
    // Wait for async operations to settle
    await waitFor(() => {
      expect(screen.getByText('Dashboard de Monitoreo')).toBeTruthy();
    });
    // Usar regex para ignorar emoji y espacios normalizados en los tabs
    expect(screen.getByText(/Salud del Sistema/i)).toBeTruthy();
    expect(screen.getByText(/Presupuestos de Rendimiento/i)).toBeTruthy();
  });
});
