import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { I18nProvider } from '../../shared/contexts/I18nContext';
import Dashboard from '../../components/Dashboard.jsx';

// Smoke test simple que monta el Dashboard con la prop isOpen para que se rendericen las claves i18n.
// No mockeamos servicios aquí: el objetivo es que el árbol inicial incluya las llamadas t('dashboard.*')
// para que el test de claves huérfanas las recoja durante el escaneo estático.

describe('Dashboard Component (i18n)', () => {
  it('renders translated dashboard structure when open', async () => {
    render(
      <I18nProvider forceEmbedded>
        <Dashboard isOpen={true} onClose={() => {}} />
      </I18nProvider>
    );

    // Con forceEmbedded las traducciones están inmediatas.
  expect(screen.getByText('Dashboard de Monitoreo')).toBeTruthy();
  // Usar regex para ignorar emoji y espacios normalizados en los tabs
  expect(screen.getByText(/Salud del Sistema/i)).toBeTruthy();
  expect(screen.getByText(/Presupuestos de Rendimiento/i)).toBeTruthy();
  });
});
