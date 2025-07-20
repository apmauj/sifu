// 📊 Fixtures de Datos para Tests de Exchange Rates
// Valores controlados y determinísticos para testing

// Constantes base para testing (valores que nunca cambiarán)
export const TEST_EXCHANGE_RATES = {
  // Valores principales para tests estándar
  STANDARD: {
    USD: {
      currency: 'USD',
      buy_rate: 38.50,
      sell_rate: 41.50,
      average_rate: 40.00
    },
    EUR: {
      currency: 'EUR', 
      buy_rate: 42.30,
      sell_rate: 45.70,
      average_rate: 44.00
    },
    ARS: {
      currency: 'ARS',
      buy_rate: 0.85,
      sell_rate: 0.92,
      average_rate: 0.885
    },
    BRL: {
      currency: 'BRL',
      buy_rate: 8.20,
      sell_rate: 8.80,
      average_rate: 8.50
    }
  },

  // Valores para tests de formateo con decimales
  DECIMAL_TESTING: {
    USD: {
      currency: 'USD',
      buy_rate: 38.1234,
      sell_rate: 41.9876,
      average_rate: 40.0555
    },
    EUR: {
      currency: 'EUR',
      buy_rate: 42.3456,
      sell_rate: 45.6789,
      average_rate: 44.0123
    }
  },

  // Valores pequeños para tests de formateo < 1
  SMALL_VALUES: {
    ARS: {
      currency: 'ARS',
      buy_rate: 0.123456,
      sell_rate: 0.987654,
      average_rate: 0.555555
    }
  },

  // Valores iguales para tests de buy/sell iguales
  EQUAL_RATES: {
    USD: {
      currency: 'USD',
      buy_rate: 40.00,
      sell_rate: 40.00,
      average_rate: 40.00
    }
  },

  // Valores grandes para tests de números grandes
  LARGE_VALUES: {
    USD: {
      currency: 'USD',
      buy_rate: 999999.99,
      sell_rate: 1000000.01,
      average_rate: 1000000.00
    }
  },

  // Valores incompletos para tests de edge cases
  INCOMPLETE_DATA: {
    USD: {
      currency: 'USD',
      buy_rate: null,
      sell_rate: 41.50,
      average_rate: undefined
    }
  },

  // Moneda desconocida para tests de edge cases
  UNKNOWN_CURRENCY: {
    XYZ: {
      currency: 'XYZ',
      buy_rate: 1.00,
      sell_rate: 1.10,
      average_rate: 1.05
    }
  }
};

// Funciones helper para generar arrays de datos
export const createMockRatesArray = (rateSet) => {
  return Object.values(rateSet);
};

// Datos por defecto para la mayoría de tests
export const DEFAULT_MOCK_RATES = createMockRatesArray(TEST_EXCHANGE_RATES.STANDARD);

// Respuesta mock estándar del servicio
export const createMockServiceResponse = (data, success = true, message = null) => ({
  success,
  data: success ? data : null,
  message: success ? null : message
});

// Valores esperados en el DOM (para assertions)
export const EXPECTED_VALUES = {
  STANDARD: {
    USD_BUY: '38.50',
    USD_SELL: '41.50', 
    EUR_BUY: '42.30',
    EUR_SELL: '45.70',
    ARS_BUY: '0.8500',
    ARS_SELL: '0.9200',
    BRL_BUY: '8.20',
    BRL_SELL: '8.80'
  },
  DECIMAL_FORMATTED: {
    USD_BUY: '38.12',
    USD_SELL: '41.99',
    EUR_BUY: '42.35',
    EUR_SELL: '45.68'
  },
  SMALL_FORMATTED: {
    ARS_BUY: '0.1235',
    ARS_SELL: '0.9877'
  },
  EQUAL_RATES: {
    USD: '40.00'
  },
  LARGE_VALUES: {
    USD_BUY: '999999.99'
  }
};

// Configuraciones de test comunes
export const TEST_SCENARIOS = {
  LOADING: {
    description: 'Estado de carga',
    mockImplementation: () => new Promise(() => {}) // Never resolves
  },
  SUCCESS: {
    description: 'Datos cargados exitosamente',
    mockResponse: createMockServiceResponse(DEFAULT_MOCK_RATES)
  },
  ERROR: {
    description: 'Error de conexión',
    mockError: new Error('Error de conexión')
  },
  API_ERROR: {
    description: 'Error de API',
    mockResponse: createMockServiceResponse(null, false, 'API service unavailable')
  },
  EMPTY_DATA: {
    description: 'Datos vacíos',
    mockResponse: createMockServiceResponse([])
  }
};

// Función para resetear mocks con datos específicos
export const setupMockWithData = (mockService, scenario) => {
  if (scenario.mockImplementation) {
    mockService.getCurrentRates.mockImplementation(scenario.mockImplementation);
  } else if (scenario.mockResponse) {
    mockService.getCurrentRates.mockResolvedValue(scenario.mockResponse);
  } else if (scenario.mockError) {
    mockService.getCurrentRates.mockRejectedValue(scenario.mockError);
  }
};

// Exportar para compatibilidad con tests existentes
export const mockRatesData = DEFAULT_MOCK_RATES;

export default {
  TEST_EXCHANGE_RATES,
  DEFAULT_MOCK_RATES,
  EXPECTED_VALUES,
  TEST_SCENARIOS,
  createMockRatesArray,
  createMockServiceResponse,
  setupMockWithData
}; 