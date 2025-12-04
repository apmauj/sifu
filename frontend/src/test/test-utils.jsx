import React from 'react';
import { render } from '@testing-library/react';
import { vi } from 'vitest';

// Mock the useI18n hook directly
vi.mock('../contexts/I18nContext', () => ({
  useI18n: () => ({
    currentLanguage: 'es',
    isLoading: false,
    t: (key) => {
      // Simple mock translations
      const translations = {
        'ui.no_results': 'No se encontraron resultados',
        'ui.no_results_hint': 'Intenta con otra fecha o rango',
        'ui.ui_value': 'Valor de la UI',
        'ui.data_source': 'Fuente de datos: INE',
        'ui.period_summary': 'Resumen del Período',
        'ui.initial_value': 'Valor inicial',
        'ui.final_value': 'Valor final',
        'ui.ui_evolution': 'Evolución del valor de la UI',
        'common.variation': 'Variación',
        'common.date': 'Fecha',
        'common.value': 'Valor'
      };
      return translations[key] || key;
    },
    translateBackendMessage: (message) => {
      if (typeof message !== 'string') return message;
      return message;
    },
    changeLanguage: () => {},
    getSupportedLanguages: () => ['es', 'en', 'pt']
  })
}));

// Re-export everything from testing library
export * from '@testing-library/react';
export { render }; 
