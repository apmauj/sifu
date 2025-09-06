import React from 'react';
import { render, screen } from '@testing-library/react';
import { I18nProvider } from '../../contexts/I18nContext';
import Dashboard from '../../components/Dashboard.jsx';

// Smoke test simple que monta el Dashboard con la prop isOpen para que se rendericen las claves i18n.
// No mockeamos servicios aquí: el objetivo es que el árbol inicial incluya las llamadas t('dashboard.*')
// para que el test de claves huérfanas las recoja durante el escaneo estático.

describe('Dashboard Component (i18n smoke)', () => {
  it('renders basic dashboard structure when open (fallback keys visible)', () => {
    render(
      <I18nProvider>
        <Dashboard isOpen={true} onClose={() => {}} />
      </I18nProvider>
    );

    // Dado que en entorno de tests el provider devuelve la clave cuando aún no está cargada la traducción remota,
    // verificamos directamente la presencia de algunas claves críticas del namespace dashboard.
  // Las claves pueden aparecer con espacios/emoji alrededor; usamos matchers parciales.
  expect(screen.getByText((c) => c.includes('dashboard.title'))).toBeTruthy();
  expect(screen.getByText((c) => c.includes('dashboard.tab_health'))).toBeTruthy();
  expect(screen.getByText((c) => c.includes('dashboard.tab_performance'))).toBeTruthy();
  });
});
