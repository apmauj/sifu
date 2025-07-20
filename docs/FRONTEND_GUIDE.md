# Guía de Desarrollo Frontend - SIFU

## 🎯 Objetivos del Frontend

Crear una interfaz web moderna, responsiva y accesible para consultar los tres módulos financieros:
- **📈 Unidad Indexada (UI)** - Índice de ajuste por inflación
- **💰 Unidad Reajustable (UR)** - Índice hipotecario del BHU
- **💱 Cotizaciones de Monedas** - Tipos de cambio del BCU

## 🛠️ Stack Tecnológico

### Core Technologies
- **React 18** - Biblioteca principal con hooks
- **TypeScript** - Tipado estático
- **Vite** - Build tool y dev server
- **Tailwind CSS** - Framework CSS utility-first

### Libraries & Tools
- **Axios** - Cliente HTTP para API calls
- **React Hook Form** - Manejo de formularios
- **date-fns** - Manipulación de fechas
- **Recharts** - Gráficos y visualizaciones
- **React Router DOM** - Enrutado
- **Heroicons** - Iconografía

## 🏗️ Arquitectura Frontend Propuesta

### Estructura de Directorios
```
frontend/
├── src/
│   ├── components/          # Componentes React
│   │   ├── common/         # Componentes reutilizables
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   ├── ErrorMessage.tsx
│   │   │   └── DatePicker.tsx
│   │   ├── ui/             # Componentes UI (existentes)
│   │   │   ├── UICalculator.tsx
│   │   │   ├── DateRangeSelector.tsx
│   │   │   └── ResultsDisplay.tsx
│   │   ├── ur/             # Componentes UR (nuevo)
│   │   │   ├── URCalculator.tsx
│   │   │   ├── URYearSelector.tsx
│   │   │   └── URResultsTable.tsx
│   │   └── exchange/       # Componentes Exchange Rates (nuevo)
│   │       ├── ExchangeRatePanel.tsx
│   │       ├── CurrencySelector.tsx
│   │       ├── RateDisplay.tsx
│   │       └── RateChart.tsx
│   ├── services/           # API Services
│   │   ├── api.ts          # Cliente base Axios
│   │   ├── uiService.ts    # Servicios UI (existente)
│   │   ├── urService.ts    # Servicios UR (nuevo)
│   │   └── exchangeService.ts # Servicios Exchange (nuevo)
│   ├── types/              # TypeScript types
│   │   ├── ui.ts
│   │   ├── ur.ts
│   │   └── exchange.ts
│   ├── contexts/           # React Contexts
│   │   ├── AppContext.tsx  # Estado global
│   │   └── NotificationContext.tsx
│   ├── hooks/              # Custom hooks
│   │   ├── useApi.ts
│   │   ├── useLocalStorage.ts
│   │   └── useDebounce.ts
│   ├── utils/              # Utilidades
│   │   ├── formatters.ts   # Formateo de números/fechas
│   │   ├── validators.ts   # Validaciones
│   │   └── constants.ts    # Constantes
│   └── test/               # Tests
│       ├── components/
│       ├── services/
│       └── utils/
├── public/                 # Assets estáticos
├── index.html             # HTML principal
├── package.json           # Dependencias
├── tsconfig.json          # TypeScript config
├── tailwind.config.js     # Tailwind config
└── vite.config.ts         # Vite config
```

## 📱 Diseño de Componentes

### Layout Principal
```tsx
// App.tsx
function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <TabNavigation />
        <Routes>
          <Route path="/ui" element={<UIModule />} />
          <Route path="/ur" element={<URModule />} />
          <Route path="/exchange" element={<ExchangeModule />} />
          <Route path="/" element={<Navigate to="/ui" />} />
        </Routes>
      </main>
      <Footer />
    </div>
  )
}
```

### Navegación por Tabs
```tsx
// components/common/TabNavigation.tsx
interface Tab {
  id: string
  label: string
  icon: React.ComponentType
  path: string
}

const tabs: Tab[] = [
  { id: 'ui', label: 'Unidad Indexada', icon: TrendingUpIcon, path: '/ui' },
  { id: 'ur', label: 'Unidad Reajustable', icon: HomeIcon, path: '/ur' },
  { id: 'exchange', label: 'Cotizaciones', icon: CurrencyDollarIcon, path: '/exchange' }
]

export function TabNavigation() {
  const location = useLocation()
  
  return (
    <nav className="mb-8 border-b border-gray-200">
      <div className="flex space-x-8">
        {tabs.map(tab => (
          <Link
            key={tab.id}
            to={tab.path}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              location.pathname === tab.path
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <tab.icon className="w-5 h-5 inline mr-2" />
            {tab.label}
          </Link>
        ))}
      </div>
    </nav>
  )
}
```

## 🎨 Componentes por Módulo

### 1. Módulo UI (Existente - Mejorar)

#### UICalculator.tsx
```tsx
interface UICalculatorProps {
  className?: string
}

export function UICalculator({ className }: UICalculatorProps) {
  const [searchType, setSearchType] = useState<'single' | 'range'>('single')
  const [singleDate, setSingleDate] = useState<Date>(new Date())
  const [dateRange, setDateRange] = useState<{start: Date, end: Date}>()
  const [results, setResults] = useState<UIValue[]>([])
  const [loading, setLoading] = useState(false)
  
  // Lógica del componente...
  
  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">
        📈 Consultar Unidad Indexada
      </h2>
      
      {/* Selector de tipo de búsqueda */}
      <SearchTypeSelector value={searchType} onChange={setSearchType} />
      
      {/* Formularios condicionales */}
      {searchType === 'single' ? (
        <SingleDateForm date={singleDate} onChange={setSingleDate} onSubmit={handleSingleSearch} />
      ) : (
        <DateRangeForm range={dateRange} onChange={setDateRange} onSubmit={handleRangeSearch} />
      )}
      
      {/* Resultados */}
      {loading && <LoadingSpinner />}
      {results.length > 0 && <UIResultsDisplay results={results} />}
    </div>
  )
}
```

### 2. Módulo UR (Nuevo)

#### URCalculator.tsx
```tsx
interface URCalculatorProps {
  className?: string
}

export function URCalculator({ className }: URCalculatorProps) {
  const [searchType, setSearchType] = useState<'month' | 'year' | 'range'>('month')
  const [selectedYear, setSelectedYear] = useState<number>(new Date().getFullYear())
  const [selectedMonth, setSelectedMonth] = useState<number>(new Date().getMonth() + 1)
  const [results, setResults] = useState<URValue[]>([])
  
  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">
        💰 Consultar Unidad Reajustable
      </h2>
      
      {/* Selector de tipo de búsqueda */}
      <div className="mb-6">
        <div className="flex space-x-4">
          <button 
            onClick={() => setSearchType('month')}
            className={`px-4 py-2 rounded-md ${searchType === 'month' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
          >
            Por Mes
          </button>
          <button 
            onClick={() => setSearchType('year')}
            className={`px-4 py-2 rounded-md ${searchType === 'year' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
          >
            Por Año
          </button>
          <button 
            onClick={() => setSearchType('range')}
            className={`px-4 py-2 rounded-md ${searchType === 'range' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
          >
            Por Rango
          </button>
        </div>
      </div>
      
      {/* Formularios condicionales */}
      {searchType === 'month' && (
        <MonthSelector 
          year={selectedYear} 
          month={selectedMonth}
          onYearChange={setSelectedYear}
          onMonthChange={setSelectedMonth}
          onSubmit={handleMonthSearch}
        />
      )}
      
      {searchType === 'year' && (
        <YearSelector 
          year={selectedYear}
          onChange={setSelectedYear}
          onSubmit={handleYearSearch}
        />
      )}
      
      {searchType === 'range' && (
        <URRangeSelector onSubmit={handleRangeSearch} />
      )}
      
      {/* Resultados */}
      {results.length > 0 && <URResultsTable results={results} />}
    </div>
  )
}
```

### 3. Módulo Exchange Rates (Nuevo)

#### ExchangeRatePanel.tsx
```tsx
interface ExchangeRatePanelProps {
  className?: string
}

export function ExchangeRatePanel({ className }: ExchangeRatePanelProps) {
  const [selectedCurrency, setSelectedCurrency] = useState<string>('USD')
  const [searchDate, setSearchDate] = useState<Date>(new Date())
  const [currentRates, setCurrentRates] = useState<ExchangeRateValue[]>([])
  const [historicalData, setHistoricalData] = useState<ExchangeRateValue[]>([])
  
  useEffect(() => {
    loadLatestRates()
  }, [])
  
  return (
    <div className={`space-y-6 ${className}`}>
      {/* Panel de cotizaciones actuales */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          💱 Cotizaciones de Monedas
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {currentRates.map(rate => (
            <CurrencyCard key={rate.currency} rate={rate} />
          ))}
        </div>
      </div>
      
      {/* Panel de consulta histórica */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">
          Consulta Histórica
        </h3>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <CurrencySelector 
              currencies={SUPPORTED_CURRENCIES}
              selected={selectedCurrency}
              onChange={setSelectedCurrency}
            />
            <DatePicker 
              selected={searchDate}
              onChange={setSearchDate}
            />
            <button 
              onClick={handleHistoricalSearch}
              className="mt-4 w-full bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600"
            >
              Consultar
            </button>
          </div>
          
          <div>
            {historicalData.length > 0 && (
              <RateChart data={historicalData} currency={selectedCurrency} />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
```

## 🎨 Sistema de Diseño

### Paleta de Colores
```css
:root {
  /* Colores de la bandera uruguaya */
  --primary-blue: #0066cc;
  --primary-light-blue: #3399ff;
  --accent-yellow: #ffcc00;
  --white: #ffffff;
  
  /* Grises */
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-500: #6b7280;
  --gray-700: #374151;
  --gray-900: #111827;
  
  /* Estados */
  --success: #10b981;
  --warning: #f59e0b;
  --error: #ef4444;
}
```

### Componentes Base
```tsx
// components/common/Button.tsx
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'outline'
  size: 'sm' | 'md' | 'lg'
  children: React.ReactNode
  onClick?: () => void
  disabled?: boolean
  loading?: boolean
}

export function Button({ variant, size, children, ...props }: ButtonProps) {
  const baseClasses = "inline-flex items-center justify-center font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2"
  
  const variantClasses = {
    primary: "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500",
    secondary: "bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500",
    outline: "border border-gray-300 text-gray-700 bg-white hover:bg-gray-50 focus:ring-blue-500"
  }
  
  const sizeClasses = {
    sm: "px-3 py-2 text-sm",
    md: "px-4 py-2 text-base",
    lg: "px-6 py-3 text-lg"
  }
  
  return (
    <button 
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]}`}
      {...props}
    >
      {children}
    </button>
  )
}
```

## 🔄 Gestión de Estado

### Context para Estado Global
```tsx
// contexts/AppContext.tsx
interface AppState {
  notifications: Notification[]
  loading: boolean
  user: User | null
}

interface AppContextType {
  state: AppState
  addNotification: (notification: Omit<Notification, 'id'>) => void
  removeNotification: (id: string) => void
  setLoading: (loading: boolean) => void
}

export const AppContext = createContext<AppContextType | null>(null)

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AppState>({
    notifications: [],
    loading: false,
    user: null
  })
  
  const addNotification = useCallback((notification: Omit<Notification, 'id'>) => {
    const id = Math.random().toString(36).substr(2, 9)
    setState(prev => ({
      ...prev,
      notifications: [...prev.notifications, { ...notification, id }]
    }))
    
    // Auto-remove after 5 seconds
    setTimeout(() => removeNotification(id), 5000)
  }, [])
  
  const removeNotification = useCallback((id: string) => {
    setState(prev => ({
      ...prev,
      notifications: prev.notifications.filter(n => n.id !== id)
    }))
  }, [])
  
  const setLoading = useCallback((loading: boolean) => {
    setState(prev => ({ ...prev, loading }))
  }, [])
  
  return (
    <AppContext.Provider value={{ state, addNotification, removeNotification, setLoading }}>
      {children}
    </AppContext.Provider>
  )
}
```

## 🌐 Servicios API

### Cliente Base
```tsx
// services/api.ts
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Interceptor para manejo de errores
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.message || 'Error en la conexión'
    throw new Error(message)
  }
)
```

### Servicio Exchange Rates
```tsx
// services/exchangeService.ts
export interface ExchangeRateValue {
  date: string
  currency: string
  buy_rate: number
  sell_rate: number
  average_rate?: number
  arbitrage?: string
}

export class ExchangeService {
  static async getLatest(currency?: string): Promise<ExchangeRateValue[]> {
    const params = currency ? { currency } : {}
    const response = await apiClient.get('/exchange-rate/latest', { params })
    return response.data.data
  }
  
  static async getByDate(date: string, currency?: string): Promise<ExchangeRateValue[]> {
    const url = currency 
      ? `/exchange-rate/${date}/${currency}`
      : `/exchange-rate/${date}`
    const response = await apiClient.get(url)
    return Array.isArray(response.data.data) ? response.data.data : [response.data.data]
  }
  
  static async getCurrencyHistory(currency: string, limit: number = 30): Promise<ExchangeRateValue[]> {
    const response = await apiClient.get(`/exchange-rate/currency/${currency}`, {
      params: { limit }
    })
    return response.data.data
  }
  
  static async getByDateRange(startDate: string, endDate: string): Promise<ExchangeRateValue[]> {
    const response = await apiClient.get(`/exchange-rate/range/${startDate}/${endDate}`)
    return response.data.data
  }
  
  static async refresh(): Promise<void> {
    await apiClient.post('/exchange-rate/refresh')
  }
}
```

## 📊 Componentes de Visualización

### Gráfico de Cotizaciones
```tsx
// components/exchange/RateChart.tsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface RateChartProps {
  data: ExchangeRateValue[]
  currency: string
}

export function RateChart({ data, currency }: RateChartProps) {
  const chartData = data.map(rate => ({
    date: rate.date,
    compra: rate.buy_rate,
    venta: rate.sell_rate,
    promedio: rate.average_rate || (rate.buy_rate + rate.sell_rate) / 2
  }))
  
  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="compra" 
            stroke="#10b981" 
            name="Compra"
            strokeWidth={2}
          />
          <Line 
            type="monotone" 
            dataKey="venta" 
            stroke="#ef4444" 
            name="Venta"
            strokeWidth={2}
          />
          <Line 
            type="monotone" 
            dataKey="promedio" 
            stroke="#6366f1" 
            name="Promedio"
            strokeWidth={2}
            strokeDasharray="5 5"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
```

## 🧪 Testing Strategy

### Configuración de Testing
```tsx
// test/setup.ts
import '@testing-library/jest-dom'
import { vi } from 'vitest'

// Mock para API calls
vi.mock('../src/services/api', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn()
  }
}))
```

### Test de Componente
```tsx
// test/components/ExchangeRatePanel.test.tsx
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ExchangeRatePanel } from '../../src/components/exchange/ExchangeRatePanel'
import { ExchangeService } from '../../src/services/exchangeService'

vi.mock('../../src/services/exchangeService')

describe('ExchangeRatePanel', () => {
  beforeEach(() => {
    vi.mocked(ExchangeService.getLatest).mockResolvedValue([
      {
        date: '2025-06-16',
        currency: 'USD',
        buy_rate: 42.50,
        sell_rate: 43.50,
        average_rate: 43.00,
        arbitrage: 'BCU'
      }
    ])
  })
  
  it('renders current exchange rates', async () => {
    render(<ExchangeRatePanel />)
    
    await waitFor(() => {
      expect(screen.getByText('💱 Cotizaciones de Monedas')).toBeInTheDocument()
      expect(screen.getByText('USD')).toBeInTheDocument()
      expect(screen.getByText('42.50')).toBeInTheDocument()
    })
  })
  
  it('handles currency selection', async () => {
    const user = userEvent.setup()
    render(<ExchangeRatePanel />)
    
    const currencySelect = screen.getByLabelText('Seleccionar moneda')
    await user.selectOptions(currencySelect, 'EUR')
    
    expect(currencySelect).toHaveValue('EUR')
  })
})
```

## 📱 Responsive Design

### Breakpoints Tailwind
```js
// tailwind.config.js
module.exports = {
  theme: {
    screens: {
      'sm': '640px',   // móviles
      'md': '768px',   // tablets
      'lg': '1024px',  // laptops
      'xl': '1280px',  // desktop
      '2xl': '1536px'  // large desktop
    }
  }
}
```

### Componente Responsivo
```tsx
function ResponsiveGrid({ children }: { children: React.ReactNode }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6">
      {children}
    </div>
  )
}
```

## ♿ Accesibilidad

### Mejores Prácticas
```tsx
// Ejemplo de componente accesible
function AccessibleButton({ onClick, children, ...props }) {
  return (
    <button
      {...props}
      onClick={onClick}
      className="focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
      aria-label={props['aria-label'] || children.toString()}
      tabIndex={0}
    >
      {children}
    </button>
  )
}
```

### ARIA Labels
```tsx
<div role="tablist" aria-label="Módulos financieros">
  <button role="tab" aria-selected={activeTab === 'ui'} aria-controls="ui-panel">
    Unidad Indexada
  </button>
</div>
```

## 🚀 Plan de Implementación

### Fase 1: Preparación
1. ✅ Actualizar estructura de directorios
2. ✅ Configurar TypeScript types
3. ✅ Implementar sistema de navegación
4. ✅ Crear componentes base

### Fase 2: Módulo UR
1. Implementar URCalculator
2. Crear formularios de búsqueda
3. Desarrollar tabla de resultados
4. Agregar validaciones

### Fase 3: Módulo Exchange Rates
1. Implementar ExchangeRatePanel
2. Crear CurrencyCard components
3. Desarrollar gráficos históricos
4. Agregar funcionalidad de actualización

### Fase 4: Mejoras UI/UX
1. Optimizar componentes existentes de UI
2. Agregar animaciones y transiciones
3. Mejorar responsive design
4. Implementar dark mode (opcional)

### Fase 5: Testing & Polish
1. Escribir tests unitarios
2. Implementar tests de integración
3. Optimizar performance
4. Accesibilidad y SEO

---

Esta guía proporciona la base completa para desarrollar el frontend del sistema. ¿Te gustaría que comencemos con alguna fase específica? 