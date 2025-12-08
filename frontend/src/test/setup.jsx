import '@testing-library/jest-dom'
import { vi, afterEach } from 'vitest'
import { cleanup } from '@testing-library/react'
import React from 'react'

// Cleanup after each test
afterEach(() => {
  cleanup()
})

// Load real translations for tests
import esTranslations from './es.json'

// Import real constants instead of mocking them
import * as realConstants from '../constants.js'

// Export real constants for use in tests
globalThis.REAL_CONSTANTS = realConstants

// Enhanced I18n mock with better branch coverage
vi.mock('../shared/contexts/I18nContext', () => {
  const createMockI18nContext = () => {
    const t = (key, params = {}) => {
      const keys = key.split('.')
      let value = esTranslations
      
      for (const k of keys) {
        if (value && typeof value === 'object' && k in value) {
          value = value[k]
        } else {
          console.warn(`Translation key not found in tests: ${key}`)
          return key // Return key if not found
        }
      }
      
      // Replace parameters if any
      if (typeof value === 'string' && Object.keys(params).length > 0) {
        return value.replace(/\{(\w+)\}/g, (match, param) => {
          return params[param] || match
        })
      }
      
      return value
    }

    const translateBackendMessage = (message) => {
      // Enhanced implementation for branch coverage tests
      if (!message) return ''
      if (message.includes('error')) return `Error: ${message}`
      if (message.includes('success')) return `Éxito: ${message}`
      return message
    }

    return {
      currentLanguage: globalThis.__TEST_LANGUAGE__ || 'es',
      supportedLanguages: ['es', 'en', 'pt'],
      isLoading: globalThis.__TEST_I18N_LOADING__ || false,
      t,
      translateBackendMessage,
      setLanguage: vi.fn().mockImplementation((lang) => {
        globalThis.__TEST_LANGUAGE__ = lang
        if (globalThis.__TEST_LANG_ERROR__) {
          throw new Error('Language change error')
        }
      }),
      reloadTranslations: vi.fn().mockImplementation(() => {
        if (globalThis.__TEST_RELOAD_ERROR__) {
          throw new Error('Reload translations error')
        }
      })
    }
  }

  const mockContext = createMockI18nContext()
  
  return {
    useI18n: () => mockContext,
    I18nProvider: ({ children }) => React.createElement('div', { 'data-testid': 'i18n-provider' }, children)
  }
})

// Mock ThemeContext for tests
vi.mock('../shared/contexts/ThemeContext', () => {
  const createMockThemeContext = () => {
    return {
      theme: globalThis.__TEST_THEME__ || 'light',
      isDark: (globalThis.__TEST_THEME__ || 'light') === 'dark',
      isLight: (globalThis.__TEST_THEME__ || 'light') === 'light',
      toggleTheme: vi.fn(() => {
        const newTheme = (globalThis.__TEST_THEME__ || 'light') === 'light' ? 'dark' : 'light';
        globalThis.__TEST_THEME__ = newTheme;
      }),
      setTheme: vi.fn((theme) => {
        globalThis.__TEST_THEME__ = theme;
      })
    }
  }

  const mockContext = createMockThemeContext()

  return {
    useTheme: () => mockContext,
    ThemeProvider: ({ children }) => React.createElement('div', { 'data-testid': 'theme-provider' }, children)
  }
})

// Simple Toast Context mock for non-ToastContext tests
const mockToastContext = () => ({
  useToast: vi.fn(() => ({
    showSuccess: vi.fn((message) => {
      if (globalThis.__TEST_TOAST_ERROR__) {
        throw new Error('Toast error')
      }
      console.log('Toast Success:', message)
    }),
    showError: vi.fn((message) => {
      if (globalThis.__TEST_TOAST_ERROR__) {
        throw new Error('Toast error')
      }
      console.log('Toast Error:', message)
    }),
    showInfo: vi.fn((message) => {
      if (globalThis.__TEST_TOAST_ERROR__) {
        throw new Error('Toast error')
      }
      console.log('Toast Info:', message)
    }),
    showWarning: vi.fn((message) => {
      if (globalThis.__TEST_TOAST_ERROR__) {
        throw new Error('Toast error')
      }
      console.log('Toast Warning:', message)
    }),
    addToast: vi.fn((message, type = 'info', duration = 3000) => {
      if (globalThis.__TEST_TOAST_ERROR__) {
        throw new Error('Toast error')
      }
      console.log(`Toast ${type}:`, message)
    }),
    removeToast: vi.fn((id) => {
      console.log('Remove toast:', id)
    })
  })),
  ToastProvider: ({ children }) => React.createElement('div', { 'data-testid': 'toast-provider' }, children)
})

// Mock ToastContext solo si no estamos testeando específicamente ToastContext
if (!globalThis.__TESTING_TOAST_CONTEXT__) {
  vi.mock('../shared/contexts/ToastContext', () => mockToastContext())
}

// Enhanced axios mock with more realistic error scenarios
const createEnhancedAxiosMock = () => ({
  get: vi.fn().mockImplementation(async (url) => {
    // Simulate different response scenarios for branch coverage
    if (globalThis.__TEST_NETWORK_ERROR__) {
      throw new Error('Network Error')
    }
    if (globalThis.__TEST_SERVER_ERROR__) {
      const error = new Error('Server Error')
      error.response = { status: 500, data: { error: 'Internal Server Error' } }
      throw error
    }
    if (globalThis.__TEST_NOT_FOUND__) {
      const error = new Error('Not Found')
      error.response = { status: 404, data: { error: 'Not Found' } }
      throw error
    }
    if (globalThis.__TEST_TIMEOUT__) {
      const error = new Error('Timeout')
      error.code = 'ECONNABORTED'
      throw error
    }
    
    // Default success response
    return {
      data: globalThis.__TEST_MOCK_DATA__ || { success: true, data: {} },
      status: 200
    }
  }),
  post: vi.fn().mockImplementation(async (url, data) => {
    if (globalThis.__TEST_POST_ERROR__) {
      throw new Error('POST Error')
    }
    return {
      data: { success: true, data: {} },
      status: 200
    }
  }),
  interceptors: {
    response: {
      use: vi.fn()
    }
  }
})

// Mock global de date-fns
vi.mock('date-fns', () => {
  // Usar fecha actual para consistencia
  const today = new Date()
  
  // Función helper para formatear fecha como YYYY-MM-DD
  const formatDateToYMD = (date) => {
    if (!date || !(date instanceof Date)) {
      // Devolver fecha actual en formato YYYY-MM-DD
      return today.getFullYear() + '-' + 
        String(today.getMonth() + 1).padStart(2, '0') + '-' + 
        String(today.getDate()).padStart(2, '0')
    }
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }

  return {
         format: vi.fn((date, formatStr) => {
       if (!date) return ''
       const d = new Date(date)
       
       // Verificar si la fecha es inválida
       if (isNaN(d.getTime())) {
         console.warn('Invalid date provided to format function:', date)
         return 'Fecha inválida'
       }
       
       if (formatStr === 'dd/MM/yyyy') {
         // Handle specific test dates
         try {
           const dateStr = d.toISOString().split('T')[0]
           if (dateStr === '2024-01-01') return '01/01/2024'
           if (dateStr === '2024-12-25') return '25/12/2024'
           if (dateStr === '2023-12-31') return '31/12/2023'
           return `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()}`
         } catch (error) {
           console.warn('Error formatting date:', error)
           return 'Fecha inválida'
         }
       }
       if (formatStr === 'HH:mm') {
         return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
       }
       if (formatStr === 'yyyy-MM-dd') {
         return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
       }
       try {
         return d.toISOString().split('T')[0]
       } catch (error) {
         console.warn('Error converting date to ISO string:', error)
         return 'Fecha inválida'
       }
     }),
    parseISO: vi.fn((dateString) => {
      if (!dateString || typeof dateString !== 'string') {
        console.warn('Invalid date string provided to parseISO:', dateString)
        return new Date() // Return current date as fallback
      }
      const parsed = new Date(dateString)
      if (isNaN(parsed.getTime())) {
        console.warn('Invalid date string parsed:', dateString)
        return new Date() // Return current date as fallback
      }
      return parsed
    }),
    isValid: vi.fn((date) => date instanceof Date && !isNaN(date)),
    startOfMonth: vi.fn((date) => {
      if (!date || !(date instanceof Date) || isNaN(date.getTime())) {
        return new Date(today.getFullYear(), today.getMonth(), 1)
      }
      const d = new Date(date)
      return new Date(d.getFullYear(), d.getMonth(), 1)
    }),
    endOfMonth: vi.fn((date) => {
      if (!date || !(date instanceof Date) || isNaN(date.getTime())) {
        return new Date(today.getFullYear(), today.getMonth() + 1, 0)
      }
      const d = new Date(date)
      return new Date(d.getFullYear(), d.getMonth() + 1, 0)
    }),
    startOfYear: vi.fn((date) => {
      if (!date || !(date instanceof Date) || isNaN(date.getTime())) {
        return new Date(today.getFullYear(), 0, 1)
      }
      const d = new Date(date)
      return new Date(d.getFullYear(), 0, 1)
    }),
    endOfYear: vi.fn((date) => {
      if (!date || !(date instanceof Date) || isNaN(date.getTime())) {
        return new Date(today.getFullYear(), 11, 31)
      }
      const d = new Date(date)
      return new Date(d.getFullYear(), 11, 31)
    }),
    subDays: vi.fn((date, days) => {
      if (!date || !(date instanceof Date) || isNaN(date.getTime())) {
        const d = new Date(today)
        d.setDate(d.getDate() - (days || 0))
        return d
      }
      const d = new Date(date)
      d.setDate(d.getDate() - (days || 0))
      return d
    }),
    subWeeks: vi.fn((date, weeks) => {
      if (!date || !(date instanceof Date) || isNaN(date.getTime())) {
        const d = new Date(today)
        d.setDate(d.getDate() - ((weeks || 0) * 7))
        return d
      }
      const d = new Date(date)
      d.setDate(d.getDate() - ((weeks || 0) * 7))
      return d
    }),
    subMonths: vi.fn((date, months) => {
      if (!date || !(date instanceof Date) || isNaN(date.getTime())) {
        const d = new Date(today)
        d.setMonth(d.getMonth() - (months || 0))
        return d
      }
      const d = new Date(date)
      d.setMonth(d.getMonth() - (months || 0))
      return d
    }),
    subYears: vi.fn((date, years) => {
      if (!date || !(date instanceof Date) || isNaN(date.getTime())) {
        const d = new Date(today)
        d.setFullYear(d.getFullYear() - (years || 0))
        return d
      }
      const d = new Date(date)
      d.setFullYear(d.getFullYear() - (years || 0))
      return d
    })
  }
})

// Mock para window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock para IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
}

// Mock para ResizeObserver (needed for Recharts)
global.ResizeObserver = class ResizeObserver {
  constructor(callback) {
    this.callback = callback
  }
  observe() {}
  unobserve() {}
  disconnect() {}
}

// Mock para HTMLInputElement.prototype.removeAttribute
HTMLInputElement.prototype.removeAttribute = vi.fn()

// NOTA: Mock de dateUtils removido intencionalmente
// Los tests de dateUtils ahora ejecutan el código real para obtener cobertura correcta

// Mock global de recharts (usado en múltiples componentes)
vi.mock('recharts', () => ({
  LineChart: ({ children, ...props }) => {
    // Remove invalid DOM props
    const { width, height, data, margin, ...validProps } = props;
    return React.createElement('div', { 
      'data-testid': 'line-chart', 
      'data-width': width,
      'data-height': height,
      ...validProps 
    }, children);
  },
  BarChart: ({ children, ...props }) => {
    // Remove invalid DOM props
    const { width, height, data, margin, ...validProps } = props;
    return React.createElement('div', { 
      'data-testid': 'bar-chart', 
      'data-width': width,
      'data-height': height,
      ...validProps 
    }, children);
  },
  XAxis: (props) => {
    const { dataKey, type, tick, fontSize, ...validProps } = props;
    return React.createElement('div', { 
      'data-testid': 'x-axis', 
      'data-datakey': dataKey,
      'data-type': type,
      ...validProps 
    });
  },
  YAxis: (props) => {
    // Filtramos tickFormatter para que no llegue al DOM y evitar el warning
    const { domain, type, tick, fontSize, width, tickFormatter, ...validProps } = props;
    return React.createElement('div', {
      'data-testid': 'y-axis',
      'data-domain': domain,
      'data-type': type,
      'data-width': width,
      ...validProps
    });
  },
  CartesianGrid: (props) => {
    const { strokeDasharray, ...validProps } = props;
    return React.createElement('div', { 
      'data-testid': 'cartesian-grid', 
      'data-stroke-dasharray': strokeDasharray,
      ...validProps 
    });
  },
  Tooltip: (props) => {
    const { formatter, labelFormatter, contentStyle, labelStyle, itemStyle, wrapperStyle, ...validProps } = props;
    return React.createElement('div', {
      'data-testid': 'tooltip',
      ...validProps
    });
  },
  Legend: (props) => {
    const { wrapperStyle, ...validProps } = props;
    return React.createElement('div', { 
      'data-testid': 'legend', 
      ...validProps 
    });
  },
  Line: (props) => {
    const { 
      dataKey, 
      stroke, 
      strokeWidth, 
      strokeDasharray, 
      type, 
      dot, 
      name, 
      ...validProps 
    } = props;
    return React.createElement('div', { 
      'data-testid': props.dataKey ? `line-${props.dataKey}` : 'line', 
      'data-datakey': dataKey,
      'data-stroke': stroke,
      'data-stroke-width': strokeWidth,
      'data-stroke-dasharray': strokeDasharray,
      'data-type': type,
      'data-dot': dot,
      'data-name': name,
      ...validProps
    });
  },
  Bar: (props) => {
    const { 
      dataKey, 
      fill, 
      stroke, 
      strokeWidth, 
      name, 
      ...validProps 
    } = props;
    return React.createElement('div', { 
      'data-testid': props.dataKey ? `bar-${props.dataKey}` : 'bar', 
      'data-datakey': dataKey,
      'data-fill': fill,
      'data-stroke': stroke,
      'data-stroke-width': strokeWidth,
      'data-name': name,
      ...validProps
    });
  },
  ResponsiveContainer: ({ children, ...props }) => {
    const { width, height, ...validProps } = props;
    return React.createElement('div', { 
      'data-testid': 'responsive-container', 
      'data-width': width,
      'data-height': height,
      ...validProps 
    }, children);
  }
}))

// Mock global de @heroicons/react (usado en múltiples componentes)
vi.mock('@heroicons/react/24/outline', () => ({
  ChevronDownIcon: (props) => React.createElement('svg', { 'data-testid': 'chevron-down-icon', ...props }),
  MagnifyingGlassIcon: (props) => React.createElement('svg', { 'data-testid': 'magnifying-glass-icon', ...props }),
  CalendarIcon: (props) => React.createElement('svg', { 'data-testid': 'calendar-icon', ...props }),
  ArrowPathIcon: (props) => React.createElement('svg', { 'data-testid': 'arrow-path-icon', ...props }),
  XMarkIcon: (props) => React.createElement('svg', { 'data-testid': 'x-mark-icon', ...props }),
  CheckCircleIcon: (props) => React.createElement('svg', { 'data-testid': 'check-circle-icon', ...props }),
  ExclamationCircleIcon: (props) => React.createElement('svg', { 'data-testid': 'exclamation-circle-icon', ...props }),
  InformationCircleIcon: (props) => React.createElement('svg', { 'data-testid': 'information-circle-icon', ...props }),
  ExclamationTriangleIcon: (props) => React.createElement('svg', { 'data-testid': 'exclamation-triangle-icon', ...props }),
  ChartBarIcon: (props) => React.createElement('svg', { 'data-testid': 'chart-bar-icon', ...props }),
  CurrencyDollarIcon: (props) => React.createElement('svg', { 'data-testid': 'currency-dollar-icon', ...props }),
  ClockIcon: (props) => React.createElement('svg', { 'data-testid': 'clock-icon', ...props }),
  BanknotesIcon: (props) => React.createElement('svg', { 'data-testid': 'banknotes-icon', ...props }),
  ArrowUpIcon: (props) => React.createElement('svg', { 'data-testid': 'arrow-up-icon', ...props }),
  ArrowDownIcon: (props) => React.createElement('svg', { 'data-testid': 'arrow-down-icon', ...props }),
  GlobeAltIcon: (props) => React.createElement('svg', { 'data-testid': 'globe-alt-icon', ...props }),
  MoonIcon: (props) => React.createElement('svg', { 'data-testid': 'moon-icon', ...props }),
  SunIcon: (props) => React.createElement('svg', { 'data-testid': 'sun-icon', ...props }),
  MinusIcon: (props) => React.createElement('svg', { 'data-testid': 'minus-icon', ...props })
}))

// Mock global de react-hook-form (usado en formularios)
vi.mock('react-hook-form', () => ({
  useForm: vi.fn(() => ({
    register: vi.fn((name) => ({
      name,
      onChange: vi.fn(),
      onBlur: vi.fn(),
      ref: vi.fn()
    })),
    handleSubmit: vi.fn((fn) => (e) => {
      e?.preventDefault?.()
      return fn({})
    }),
    formState: {
      errors: {},
      isSubmitting: false,
      isValid: true
    },
    setValue: vi.fn(),
    getValues: vi.fn(() => ({})),
    reset: vi.fn(),
    watch: vi.fn(),
    control: {}
  })),
  Controller: ({ render, ...props }) => {
    const mockField = {
      value: '',
      onChange: vi.fn(),
      onBlur: vi.fn(),
      name: props.name || 'test-field'
    }
    const mockFormState = {
      errors: {},
      isSubmitting: false,
      isValid: true
    }
    return render({ field: mockField, formState: mockFormState })
  }
}))

// Mock global de react-dom/client (usado en main.jsx)
vi.mock('react-dom/client', () => ({
  createRoot: vi.fn(() => ({
    render: vi.fn()
  }))
}))

// Enhanced axios mock with realistic error scenarios
const mockAxiosInstance = createEnhancedAxiosMock();
const mockDirectAxiosInstance = createEnhancedAxiosMock();

vi.mock('axios', () => ({
  default: {
    create: vi.fn((config) => {
      if (config && config.baseURL === 'http://localhost:8000/api') {
        return mockDirectAxiosInstance;
      }
      return mockAxiosInstance;
    })
  }
}));

// Export enhanced mocks for use in tests
globalThis.mockAxiosInstance = mockAxiosInstance;
globalThis.mockDirectAxiosInstance = mockDirectAxiosInstance;

// Global test utilities for branch coverage
globalThis.setupBranchTest = (scenario) => {
  // Reset all test flags
  globalThis.__TEST_NETWORK_ERROR__ = false;
  globalThis.__TEST_SERVER_ERROR__ = false;
  globalThis.__TEST_NOT_FOUND__ = false;
  globalThis.__TEST_TIMEOUT__ = false;
  globalThis.__TEST_POST_ERROR__ = false;
  globalThis.__TEST_TOAST_ERROR__ = false;
  globalThis.__TEST_LANG_ERROR__ = false;
  globalThis.__TEST_RELOAD_ERROR__ = false;
  globalThis.__TEST_I18N_LOADING__ = false;
  globalThis.__TEST_LANGUAGE__ = 'es';
  globalThis.__TEST_MOCK_DATA__ = null;
  
  // Set specific scenario
  if (scenario === 'network_error') globalThis.__TEST_NETWORK_ERROR__ = true;
  if (scenario === 'server_error') globalThis.__TEST_SERVER_ERROR__ = true;
  if (scenario === 'not_found') globalThis.__TEST_NOT_FOUND__ = true;
  if (scenario === 'timeout') globalThis.__TEST_TIMEOUT__ = true;
  if (scenario === 'toast_error') globalThis.__TEST_TOAST_ERROR__ = true;
  if (scenario === 'lang_error') globalThis.__TEST_LANG_ERROR__ = true;
  if (scenario === 'i18n_loading') globalThis.__TEST_I18N_LOADING__ = true;
};

// Mock global de useHourlySyncedUpdate (usado en paneles)
// Solo mockear si no estamos testeando el hook específicamente
if (!globalThis.__TESTING_HOOK_DIRECTLY__) {
  vi.mock('../shared/hooks/useHourlySyncedUpdate', () => ({
  useHourlySyncedUpdate: vi.fn((updateFn) => {
    // For component tests, provide a simple mock
    return vi.fn()
  })
}))
} 
