import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import SearchForm from './components/SearchForm';
import ResultsDisplay from './components/ResultsDisplay';
import URSearchForm from './components/URSearchForm';
import URResultsDisplay from './components/URResultsDisplay';
import ExchangeSearchForm from './components/ExchangeSearchForm';
import ExchangeResultsDisplay from './components/ExchangeResultsDisplay';
import ExchangeRatePanel from './components/ExchangeRatePanel';
import BROUPanel from './components/BROUPanel';
import uiService from './services/api';
import urService from './services/urService';
import exchangeService from './services/exchangeService';
import { useI18n } from './contexts/I18nContext';
import { useToast } from './contexts/ToastContext';
import { getTodayLocal } from './utils/dateUtils';
import {
  APP_TITLE,
  OFFICIAL_URLS
} from './constants';
import { CalculatorIcon, ChartIcon, ExchangeIcon, BankIcon, SummaryIcon } from './components/icons';

// Error Boundary Component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error boundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="max-w-md mx-auto text-center">
            <div className="bg-red-50 border border-red-200 rounded-lg p-6">
              <h2 className="text-lg font-medium text-red-800 mb-2">
                ⚠️ Error en la aplicación
              </h2>
              <p className="text-sm text-red-600 mb-4">
                Ha ocurrido un error inesperado. Por favor, recarga la página.
              </p>
              <button
                onClick={() => window.location.reload()}
                className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
              >
                Recargar página
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

function App() {
  // Internationalization hook
  const { t, isLoading: i18nLoading, currentLanguage, translateBackendMessage } = useI18n();
  
  // Toast notifications hook
  const { showSuccess, showError, showInfo } = useToast();
  
  // UI states
  const [results, setResults] = useState(null);
  const [searchType, setSearchType] = useState('single');
  const [isLoading, setIsLoading] = useState(false);
  const [appInfo, setAppInfo] = useState(null);
  const [error, setError] = useState(null);
  
  // UR states
  const [urResults, setUrResults] = useState(null);
  const [urSearchType, setUrSearchType] = useState('single');
  const [isUrLoading, setIsUrLoading] = useState(false);
  const [urError, setUrError] = useState(null);
  
  // Exchange states
  const [exchangeResults, setExchangeResults] = useState(null);
  const [exchangeSearchType, setExchangeSearchType] = useState('latest');
  const [isExchangeLoading, setIsExchangeLoading] = useState(false);
  const [exchangeError, setExchangeError] = useState(null);
  
  // Tab and refresh state
  const [activeTab, setActiveTab] = useState('ui'); // 'ui', 'ur', 'exchange', or 'brou'
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Load initial information when component mounts
  useEffect(() => {
    const initializeApp = async () => {
      try {
        await loadAppInfo();
        await loadTodaysValue();
        await loadLatestUR();
        await loadLatestExchange();
      } catch (error) {
        console.error('Error initializing app:', error);
        setError(t('errors.app_initialization') || 'Error al inicializar la aplicación');
      }
    };

    initializeApp();
  }, []);

  const loadAppInfo = async () => {
    try {
      const info = await uiService.getInfo();
      if (info && info.success !== false) {
        setAppInfo(info);
      }
    } catch (error) {
      console.error('Error cargando información de la app:', error);
    }
  };

  const loadTodaysValue = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Get today's date in YYYY-MM-DD format using local timezone
      const today = getTodayLocal();
      
      // Try to get today's value
      const todayValue = await uiService.getByDate(today);
      
      if (todayValue && todayValue.success && todayValue.data) {
        setResults(todayValue);
        setSearchType('single');
      } else {
        // If no value for today, show the latest available
        const latest = await uiService.getLatest();
        if (latest && latest.success && latest.data) {
          setResults(latest);
          setSearchType('single');
        } else {
          setError(t('errors.no_ui_data') || 'No se encontraron datos de UI disponibles');
        }
      }
    } catch (error) {
      console.error('Error cargando valor del día:', error);
      // Fallback to latest available value
      try {
        const latest = await uiService.getLatest();
        if (latest && latest.success && latest.data) {
          setResults(latest);
          setSearchType('single');
        } else {
          setError(t('errors.ui_load_failed') || 'No se pudo cargar el valor de UI');
        }
      } catch (fallbackError) {
        console.error('Error cargando último valor:', fallbackError);
        setError(t('errors.server_connection') || 'No se pudo conectar con el servidor');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = async (searchParams) => {
    try {
      setIsLoading(true);
      setError(null);
      let response;

      if (searchParams.type === 'single') {
        response = await uiService.getByDate(searchParams.fecha);
        setSearchType('single');
      } else {
        response = await uiService.getByRange(
          searchParams.fechaInicio, 
          searchParams.fechaFin
        );
        setSearchType('range');
      }

      setResults(response);
      
      // Mostrar notificación toast con el mensaje del backend
      if (response && response.success && response.message) {
        const translatedMessage = translateBackendMessage(response.message);
        showSuccess(translatedMessage);
      }
    } catch (error) {
      console.error('Error en búsqueda:', error);
      const errorMessage = t('errors.search_failed') || 'Error al realizar la consulta. Por favor, intenta nuevamente.';
      setError(errorMessage);
      showError(errorMessage);
      setResults({
        success: false,
        message: t('errors.search_data_error') || 'Error al consultar los datos'
      });
    } finally {
      setIsLoading(false);
    }
  };

  // UR functions
  const handleURSearch = async (searchParams) => {
    try {
      setIsUrLoading(true);
      setUrError(null);
      let response;

      if (searchParams.type === 'single') {
        if (searchParams.subtype === 'month') {
          response = await urService.getByYearMonth(searchParams.year, searchParams.month);
          setUrSearchType('single');
        } else {
          response = await urService.getByYear(searchParams.year);
          setUrSearchType('year');
        }
      } else {
        response = await urService.getByRange(
          searchParams.startYear, 
          searchParams.startMonth,
          searchParams.endYear,
          searchParams.endMonth
        );
        setUrSearchType('range');
      }

      setUrResults(response);
      
      // Mostrar notificación toast con el mensaje del backend
      if (response && response.success && response.message) {
        const translatedMessage = translateBackendMessage(response.message);
        showSuccess(translatedMessage, 5000);
      }
    } catch (error) {
      console.error('Error en búsqueda UR:', error);
      const errorMessage = t('errors.ur_search_failed') || 'Error al realizar la consulta de UR. Por favor, intenta nuevamente.';
      setUrError(errorMessage);
      showError(errorMessage);
      setUrResults({
        success: false,
        message: t('errors.ur_data_error') || 'Error al consultar los datos de UR'
      });
    } finally {
      setIsUrLoading(false);
    }
  };

  const loadLatestUR = async () => {
    try {
      setIsUrLoading(true);
      setUrError(null);
      
      const latest = await urService.getLatest();
      if (latest && latest.success && latest.data) {
        setUrResults(latest);
        setUrSearchType('single');
      } else {
        setUrError(t('errors.no_ur_data') || 'No se encontraron datos de UR disponibles');
      }
    } catch (error) {
      console.error('Error cargando último valor UR:', error);
      setUrError(t('errors.ur_load_failed') || 'No se pudo cargar el valor de UR');
    } finally {
      setIsUrLoading(false);
    }
  };

  // Exchange functions
  const handleExchangeSearch = async (searchParams) => {
    try {
      setIsExchangeLoading(true);
      setExchangeError(null);
      let response;

      switch (searchParams.type) {
        case 'latest':
          response = await exchangeService.getLatest(searchParams.currency);
          setExchangeSearchType('latest');
          break;
        case 'date':
          response = await exchangeService.getByDate(searchParams.date, searchParams.currency);
          setExchangeSearchType('date');
          break;
        case 'range':
          response = await exchangeService.getByDateRange(
            searchParams.startDate, 
            searchParams.endDate, 
            searchParams.currency
          );
          setExchangeSearchType('range');
          break;
        case 'history':
          response = await exchangeService.getCurrencyHistory(
            searchParams.currency, 
            searchParams.limit
          );
          setExchangeSearchType('history');
          break;
        default:
          throw new Error(t('errors.invalid_search_type') || 'Tipo de búsqueda no válido');
      }

      setExchangeResults(response);
      
      // Mostrar notificación toast con el mensaje del backend
      if (response && response.success && response.message) {
        const translatedMessage = translateBackendMessage(response.message);
        showSuccess(translatedMessage);
      }
    } catch (error) {
      console.error('Error en búsqueda de cotizaciones:', error);
      const errorMessage = t('errors.exchange_search_failed') || 'Error al realizar la consulta de cotizaciones. Por favor, intenta nuevamente.';
      setExchangeError(errorMessage);
      showError(errorMessage);
      setExchangeResults({
        success: false,
        message: t('errors.exchange_data_error') || 'Error al consultar los datos de cotizaciones'
      });
    } finally {
      setIsExchangeLoading(false);
    }
  };

  const loadLatestExchange = async () => {
    try {
      setIsExchangeLoading(true);
      setExchangeError(null);
      
      const latest = await exchangeService.getLatest();
      if (latest && latest.success && latest.data) {
        setExchangeResults(latest);
        setExchangeSearchType('latest');
      } else {
        setExchangeError(t('errors.no_exchange_data') || 'No se encontraron datos de cotizaciones disponibles');
      }
    } catch (error) {
      console.error('Error cargando últimas cotizaciones:', error);
      setExchangeError(t('errors.exchange_load_failed') || 'No se pudo cargar las cotizaciones');
    } finally {
      setIsExchangeLoading(false);
    }
  };

  const handleRefresh = async () => {
    try {
      setIsRefreshing(true);
      setError(null);
      setUrError(null);
      setExchangeError(null);
      
      if (activeTab === 'ui') {
        const response = await uiService.refresh();
        
        if (response.success) {
          // Reload app info after refresh
          await loadAppInfo();
          
          // Show success message
          setError(null);
          const successMessage = translateBackendMessage(response.message) || t('common.refresh_success') || 'Datos actualizados correctamente';
          showSuccess(successMessage);
          
          // Load updated daily value
          await loadTodaysValue();
        } else {
          const errorMessage = response.message || t('errors.refresh_failed') || 'Error al actualizar los datos';
          setError(errorMessage);
          showError(errorMessage);
        }
      } else if (activeTab === 'ur') {
        const response = await urService.refresh();
        
        if (response.success) {
          // Show success message
          setUrError(null);
          const successMessage = translateBackendMessage(response.message) || t('common.ur_refresh_success') || 'Datos de UR actualizados correctamente';
          showSuccess(successMessage);
          
          // Load updated latest UR value
          await loadLatestUR();
        } else {
          const errorMessage = response.message || t('errors.ur_refresh_failed') || 'Error al actualizar los datos de UR';
          setUrError(errorMessage);
          showError(errorMessage);
        }
      } else if (activeTab === 'exchange') {
        const response = await exchangeService.refresh(true); // Use sample data for now
        
        if (response.success) {
          // Show success message
          setExchangeError(null);
          const successMessage = translateBackendMessage(response.message) || t('common.exchange_refresh_success') || 'Cotizaciones actualizadas correctamente';
          showSuccess(successMessage);
          
          // Load updated latest exchange rates
          await loadLatestExchange();
        } else {
          const errorMessage = response.message || t('errors.exchange_refresh_failed') || 'Error al actualizar las cotizaciones';
          setExchangeError(errorMessage);
          showError(errorMessage);
        }
      }
    } catch (error) {
      console.error('Error en refresh:', error);
      if (activeTab === 'ui') {
        const errorMessage = t('errors.refresh_failed') || 'Error al actualizar los datos. Por favor, intenta nuevamente.';
        setError(errorMessage);
        showError(errorMessage);
      } else if (activeTab === 'ur') {
        const errorMessage = t('errors.ur_refresh_failed') || 'Error al actualizar los datos de UR. Por favor, intenta nuevamente.';
        setUrError(errorMessage);
        showError(errorMessage);
      } else if (activeTab === 'exchange') {
        const errorMessage = t('errors.exchange_refresh_failed') || 'Error al actualizar las cotizaciones. Por favor, intenta nuevamente.';
        setExchangeError(errorMessage);
        showError(errorMessage);
      }
    } finally {
      setIsRefreshing(false);
    }
  };

  // Show loading while translations are loading
  if (i18nLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-uruguay-blue mx-auto mb-4"></div>
                          <p className="text-gray-600">{t('common.loading') || 'Cargando...'}</p>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50" data-testid="app-component">
        <Header 
          onRefresh={handleRefresh} 
          isRefreshing={isRefreshing}
        />
        
        {/* Panel de cotizaciones BCU en tiempo real */}
        <ExchangeRatePanel />
        
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Tabs de navegación */}
          <div className="mb-6">
            <div className="border-b border-gray-200">
              <nav className="-mb-px flex space-x-8">
                <button
                  onClick={() => setActiveTab('ui')}
                  className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center ${
                    activeTab === 'ui'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <CalculatorIcon className="w-4 h-4 mr-2" />
                  {t('navigation.ui_calculator') || 'Unidad Indexada (UI)'}
                </button>
                <button
                  onClick={() => setActiveTab('ur')}
                  className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center ${
                    activeTab === 'ur'
                      ? 'border-purple-500 text-purple-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <ChartIcon className="w-4 h-4 mr-2" />
                  {t('navigation.ur_calculator') || 'Unidad Reajustable (UR)'}
                </button>
                <button
                  onClick={() => setActiveTab('exchange')}
                  className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center ${
                    activeTab === 'exchange'
                      ? 'border-green-500 text-green-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <ExchangeIcon className="w-4 h-4 mr-2" />
                  {t('navigation.exchange_rates') || 'Cotizaciones'}
                </button>
                <button
                  onClick={() => setActiveTab('brou')}
                  className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center ${
                    activeTab === 'brou'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <BankIcon className="w-4 h-4 mr-2" />
                  BROU
                </button>
              </nav>
            </div>
          </div>

          {/* Contenido de UI */}
          {activeTab === 'ui' && (
            <>
              {/* Información de la aplicación UI */}
              {appInfo && (
                <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-sm font-medium text-blue-900">
                        📊 {t('ui.data_status') || 'Estado de los datos UI'}
                      </h2>
                      <p className="text-sm text-blue-700">
                        {appInfo.total_records} {t('common.records') || 'registros'} {t('ui.available') || 'disponibles'}
                        {appInfo.date_range?.min_date && appInfo.date_range?.max_date && (
                          <span> • {t('common.period') || 'Período'}: {appInfo.date_range.min_date} a {appInfo.date_range.max_date}</span>
                        )}
                      </p>
                    </div>
                    {appInfo.latest_ui && (
                      <div className="text-right">
                        <div className="text-sm text-blue-600">{t('ui.latest_value') || 'Último valor disponible'}:</div>
                        <div className="text-lg font-semibold text-blue-900">
                          ${(appInfo.latest_ui.value || 0).toFixed(4)} • {appInfo.latest_ui.date}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Mensaje de error UI */}
              {error && (
                <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <span className="text-red-400">⚠️</span>
                    </div>
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-red-800">Error UI</h3>
                      <p className="text-sm text-red-700">{error}</p>
                    </div>
                  </div>
                </div>
              )}

              <div className="grid lg:grid-cols-2 gap-8 items-start">
                {/* Formulario de búsqueda UI */}
                <div>
                  <SearchForm 
                    onSearch={handleSearch} 
                    isLoading={isLoading}
                  />
                </div>

                {/* Resultados UI */}
                <div>
                  <ResultsDisplay 
                    results={results} 
                    searchType={searchType}
                    isLoading={isLoading}
                    error={error}
                  />
                </div>
              </div>
            </>
          )}

          {/* Contenido de UR */}
          {activeTab === 'ur' && (
            <>
              {/* Mensaje de error UR */}
              {urError && (
                <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <span className="text-red-400">⚠️</span>
                    </div>
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-red-800">Error UR</h3>
                      <p className="text-sm text-red-700">{urError}</p>
                    </div>
                  </div>
                </div>
              )}

              <div className="grid lg:grid-cols-2 gap-8 items-start">
                {/* Formulario de búsqueda UR */}
                <div>
                  <URSearchForm 
                    onSearch={handleURSearch} 
                    isLoading={isUrLoading}
                  />
                </div>

                {/* Resultados UR */}
                <div>
                  <URResultsDisplay 
                    results={urResults} 
                    searchType={urSearchType}
                    isLoading={isUrLoading}
                    error={urError}
                  />
                </div>
              </div>
            </>
          )}

          {/* Contenido de Exchange Rates */}
          {activeTab === 'exchange' && (
            <>
              {/* Mensaje de error Exchange */}
              {exchangeError && (
                <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <span className="text-red-400">⚠️</span>
                    </div>
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-red-800">Error Cotizaciones</h3>
                      <p className="text-sm text-red-700">{exchangeError}</p>
                    </div>
                  </div>
                </div>
              )}

              <div className="grid lg:grid-cols-2 gap-8 items-start">
                {/* Formulario de búsqueda Exchange */}
                <div>
                  <ExchangeSearchForm 
                    onSearch={handleExchangeSearch} 
                    isLoading={isExchangeLoading}
                  />
                </div>

                {/* Resultados Exchange */}
                <div>
                  <ExchangeResultsDisplay 
                    results={exchangeResults} 
                    searchType={exchangeSearchType}
                    isLoading={isExchangeLoading}
                    error={exchangeError}
                  />
                </div>
              </div>
            </>
          )}

          {/* Contenido de BROU */}
          {activeTab === 'brou' && (
            <div>
              {/* Panel de cotizaciones BROU */}
              <BROUPanel />
            </div>
          )}

          {/* Footer con información */}
          <footer className="mt-12 border-t border-gray-200 pt-8">
            <div className="text-center text-sm text-gray-500">
              <p className="mb-2">
                <strong>{t('footer.sifu_title') || 'SIFU'}</strong> - {t('footer.sifu_description') || 'Sistema de Índices Financieros del Uruguay 🇺🇾'}
              </p>
              <p className="mb-2">
                {t('footer.official_sources') || 'Fuentes oficiales:'}{' '}
                <a 
                  href={OFFICIAL_URLS.INE}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-uruguay-blue hover:underline"
                >
                  INE
                </a>
                {' • '}
                <a 
                  href={OFFICIAL_URLS.BHU}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-uruguay-blue hover:underline"
                >
                  BHU
                </a>
                {' • '}
                <a 
                  href={OFFICIAL_URLS.BCU}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-uruguay-blue hover:underline"
                >
                  BCU
                </a>
                {' • '}
                <a 
                  href="https://www.brou.com.uy/web/guest/cotizaciones"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-uruguay-blue hover:underline"
                >
                  BROU
                </a>
              </p>
              <p className="text-xs">
                {t('footer.developed_with_love') || 'Desarrollado con ❤️ usando React, FastAPI y Python'}
              </p>
            </div>
          </footer>
        </main>
      </div>
    </ErrorBoundary>
  );
}

export default App; 