import React, { useState, useEffect, useRef, useCallback } from 'react';
// Sentinel de módulo para evitar doble inicialización con React StrictMode
let APP_INIT_DONE = false;
import Header from './components/Header';
import UIPanel from './components/UIPanel';
import URPanel from './components/URPanel';
import ExchangeRatePanel from './components/ExchangeRatePanel';
import ExchangeSearchForm from './components/ExchangeSearchForm';
import ExchangeResultsDisplay from './components/ExchangeResultsDisplay';
import ExchangeDataStatusPanel from './components/ExchangeDataStatusPanel';
import BROUPanel from './components/BROUPanel';
import Dashboard from './components/Dashboard';
import exchangeService from './services/exchangeService';
import uiService from './services/api';
import urService from './services/urService';
import { useI18n } from './contexts/I18nContext';
import { useToast } from './contexts/ToastContext';
import {
  OFFICIAL_URLS
} from './constants';
import { OpenMojiIcon } from './icons/openmoji/index.jsx';
import { UruguayFlagIcon } from './icons/system_icons';
import Card, { CardBody } from './components/ui/Card';
import { Tabs, Tab } from './components/ui/Tabs';
import { useHourlySyncedUpdate } from './hooks/useHourlySyncedUpdate';
import BuildInfoFooter from './components/BuildInfoFooter.jsx';

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
  const { t, isLoading: i18nLoading } = useI18n();
  
  // Toast notifications hook
  const { showError } = useToast();
  
  // Exchange states
  const [exchangeResults, setExchangeResults] = useState(null);
  const [exchangeSearchType, setExchangeSearchType] = useState('latest');
  const [isExchangeLoading, setIsExchangeLoading] = useState(false);
  const [exchangeError, setExchangeError] = useState(null);
  // Ref para evitar múltiples intentos de auto-inicialización
  const initialExchangeFetchAttemptedRef = useRef(false);
  
  // Tab and refresh state
  const [activeTab, setActiveTab] = useState('ui'); // 'ui', 'ur', 'exchange', or 'brou'
  const [isRefreshing, setIsRefreshing] = useState(false);
  // Keys to trigger child panels to refetch when refresh completes
  const [uiRefreshKey, setUiRefreshKey] = useState(0);
  const [urRefreshKey, setUrRefreshKey] = useState(0);
  const [exchangeRefreshKey, setExchangeRefreshKey] = useState(0); // fuerza refetch panel cotizaciones

  // Dashboard state
  const [isDashboardOpen, setIsDashboardOpen] = useState(false);

    // Load initial information when component mounts
  // Helper seguro de traducción que cae a fallback si todavía retorna la key
  const safeT = useCallback((key, fallback) => {
    const val = t(key);
    if (!val || val === key) return fallback;
    return val;
  }, [t]);

  const loadLatestExchange = async (options = {}) => {
    const { skipAutoInit = false } = options;
    try {
      setIsExchangeLoading(true);
      setExchangeError(null);
      const latest = await exchangeService.getLatest();

      if (latest && latest.success && latest.data) {
        setExchangeResults(latest);
        setExchangeSearchType('latest');
      } else {
        // Si no hay datos y aún no intentamos inicializar, lanzamos un refresh inicial
        if (!skipAutoInit && !initialExchangeFetchAttemptedRef.current) {
          await attemptInitialExchangeBootstrap();
        } else {
          setExchangeError(t('errors.no_exchange_data') || 'No se encontraron datos de cotizaciones disponibles');
        }
      }
    } catch (error) {
      console.error('Error cargando últimas cotizaciones:', error);
      if (!skipAutoInit && !initialExchangeFetchAttemptedRef.current) {
        await attemptInitialExchangeBootstrap();
      } else {
        setExchangeError(t('errors.exchange_load_failed') || 'No se pudo cargar las cotizaciones');
      }
    } finally {
      setIsExchangeLoading(false);
    }
  };

  // Exchange functions
  // useCallback para proveer referencia estable al formulario y evitar re-render inútil / efectos extra
  const handleExchangeSearch = useCallback(async (searchParams) => {
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

      // Remover toast de éxito en búsquedas - el resultado se muestra en pantalla
      // if (response && response.success && response.message) {
      //   const translatedMessage = translateBackendMessage(response.message);
      //   showSuccess(translatedMessage);
      // }
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
  }, [t, showError]);

  // Inicializar sólo cuando las traducciones estén cargadas para no mostrar keys crudas
  useEffect(() => {
    if (i18nLoading) return; // Esperar
    if (APP_INIT_DONE) return;
    APP_INIT_DONE = true;
    (async () => {
      try {
        console.log('App initializing after i18n ready...');
        await loadLatestExchange();
      } catch (error) {
        console.error('Error initializing app:', error);
      }
    })();
  }, [i18nLoading, loadLatestExchange]);
  // Refresco horario automático sólo cuando la pestaña de cotizaciones está activa y el tipo actual es 'latest'
  const hourlyExchangeRefresh = useCallback(async () => {
    if (activeTab === 'exchange' && exchangeSearchType === 'latest' && !isExchangeLoading) {
      await loadLatestExchange({ skipAutoInit: true });
    }
  }, [activeTab, exchangeSearchType, isExchangeLoading, loadLatestExchange]);

  useHourlySyncedUpdate(hourlyExchangeRefresh, true, { runImmediately: false });

  // Intento de bootstrap inicial si la base está vacía
  const attemptInitialExchangeBootstrap = async () => {
    initialExchangeFetchAttemptedRef.current = true;
    // Remover toast informativo intrusivo durante inicialización automática
    // showInfo(safeT('exchange.initial_bootstrap_loading', 'Cargando cotizaciones iniciales (job asíncrono)...'));
    try {
      const jobStart = await exchangeService.startAsyncHistoricalRefresh();
      if (jobStart?.job_id) {
        await pollExchangeJob(jobStart.job_id, {
          autoReload: true,
        });
      } else {
        showError(t('errors.exchange_refresh_failed') || 'No se pudo iniciar el job de actualización');
      }
    } catch (err) {
      console.error('Error en bootstrap inicial de cotizaciones (async):', err);
      const errorMessage = t('errors.exchange_refresh_failed') || 'Error al iniciar job de cotizaciones';
      setExchangeError(errorMessage);
      showError(errorMessage);
    }
  };

  // Polling de job de refresh histórico
  const pollExchangeJob = async (jobId, options = {}) => {
    const { intervalMs = 4000, timeoutMs = 180000, autoReload = false } = options;
    const start = Date.now();
    let statusData = null;
    let shouldContinue = true;
    try {
      while (shouldContinue) {
        statusData = await exchangeService.getJobStatus(jobId);
        if (!statusData || !statusData.status) {
          shouldContinue = false;
          break;
        }
        if (['success', 'error'].includes(statusData.status)) {
          shouldContinue = false;
          break;
        }
        if (Date.now() - start > timeoutMs) {
          showError(t('errors.exchange_refresh_timeout') || 'Timeout esperando finalización de la actualización');
          return;
        }
        await new Promise(r => setTimeout(r, intervalMs));
      }
      if (statusData?.status === 'success') {
        // Remover toast de éxito - el resultado se ve en pantalla
        // if (successToast) {
        //   const msg = translateBackendMessage(statusData.message) || t('common.exchange_refresh_success') || 'Actualización completada';
        //   showSuccess(msg);
        // }
        if (autoReload) {
          await loadLatestExchange({ skipAutoInit: true });
        }
      } else if (statusData?.status === 'error') {
        const msg = statusData?.error || statusData?.message || t('errors.exchange_refresh_failed') || 'Error en actualización';
        showError(msg);
      }
    } catch (err) {
      console.error('Error en polling de job de cotizaciones:', err);
      showError(t('errors.exchange_refresh_failed') || 'Fallo durante el monitoreo de actualización');
    }
  };

  const handleRefresh = async () => {
    try {
      setIsRefreshing(true);
      setExchangeError(null);
      
      if (activeTab === 'ui') {
        // Refresh UI data (INE) and trigger UIPanel to refetch
        const response = await uiService.refresh();
        if (response.success) {
          // Remover toast de éxito - el resultado se ve en pantalla
          // const successMessage = translateBackendMessage(response.message) || t('common.ui_refresh_success') || 'Datos de UI actualizados correctamente';
          // showSuccess(successMessage);
          setUiRefreshKey((k) => k + 1);
        } else {
          const errorMessage = response.message || t('errors.ui_refresh_failed') || 'Error al actualizar los datos de UI';
          showError(errorMessage);
        }
      } else if (activeTab === 'ur') {
        // Refresh UR data (BHU) and trigger URPanel to refetch
        const response = await urService.refresh();
        if (response.success) {
          // Remover toast de éxito - el resultado se ve en pantalla
          // const successMessage = translateBackendMessage(response.message) || t('common.ur_refresh_success') || 'Datos de UR actualizados correctamente';
          // showSuccess(successMessage);
          setUrRefreshKey((k) => k + 1);
        } else {
          const errorMessage = response.message || t('errors.ur_refresh_failed') || 'Error al actualizar los datos de UR';
          showError(errorMessage);
        }
      } else if (activeTab === 'exchange') {
        // Iniciar job async y monitorear
        const job = await exchangeService.startAsyncHistoricalRefresh();
        if (job?.job_id) {
          // Remover toast informativo intrusivo - solo mostrar errores
          // showInfo(safeT('exchange.refresh_started', 'Actualización iniciada...'));
          await pollExchangeJob(job.job_id, { autoReload: true });
        } else {
          showError(t('errors.exchange_refresh_failed') || 'No se pudo iniciar la actualización');
        }
        // Después de solicitar refresh incrementar clave para forzar re-fetch del panel de estado
        setExchangeRefreshKey(k => k + 1);
      }
      // UI refresh is now handled internally by UIPanel component
    } catch (error) {
      console.error('Error en refresh:', error);
      if (activeTab === 'ui') {
        const errorMessage = t('errors.ui_refresh_failed') || 'Error al actualizar los datos de UI. Por favor, intenta nuevamente.';
        showError(errorMessage);
      } else if (activeTab === 'ur') {
        const errorMessage = t('errors.ur_refresh_failed') || 'Error al actualizar los datos de UR. Por favor, intenta nuevamente.';
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
                          <p className="text-gray-600">{safeT('common.loading', 'Cargando...')}</p>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
  <div className="min-h-screen bg-gray-50 dark:bg-gray-950" data-testid="app-component">
        <Header 
          onRefresh={handleRefresh} 
          isRefreshing={isRefreshing}
        />
        
        {/* Panel de cotizaciones BCU en tiempo real */}
        <ExchangeRatePanel />
        
  <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Tabs de navegación modernos */}
          <div className="mb-6">
            <Tabs value={activeTab} onChange={setActiveTab}>
              {/* UI: calculator/money icon */}
              <Tab value="ui" icon={(props) => <OpenMojiIcon name="calculator" {...props} />}>{t('navigation.ui_calculator') || 'Unidad Indexada (UI)'}</Tab>
              {/* UR: use Money icon to differentiate */}
              <Tab value="ur" icon={(props) => <OpenMojiIcon name="exchange" {...props} />}>{t('navigation.ur_calculator') || 'Unidad Reajustable (UR)'}</Tab>
              {/* BCU Exchange rates: chart icon more market-like */}
              <Tab value="exchange" icon={(props) => <OpenMojiIcon name="chartUp" {...props} />}>{t('navigation.exchange_rates') || 'Cotizaciones'}</Tab>
              {/* BROU: bank icon */}
              <Tab value="brou" icon={(props) => <OpenMojiIcon name="bank" {...props} />}>BROU</Tab>
            </Tabs>
          </div>

          {/* Contenido de UI */}
          {activeTab === 'ui' && (
            <>
              <UIPanel refreshKey={uiRefreshKey} />
            </>
          )}

          {/* Contenido de UR */}
          {activeTab === 'ur' && (
            <>
              <URPanel refreshKey={urRefreshKey} />
            </>
          )}

          {/* Contenido de Exchange Rates */}
          {activeTab === 'exchange' && (
            <>
                        {/* Panel azul de estado de datos históricos de cotizaciones (INE) */}
                        <ExchangeDataStatusPanel refreshKey={exchangeRefreshKey} />
              {exchangeError && (
                <Card className="mb-6 border-red-200/70 bg-red-50">
                  <CardBody>
                    <div className="flex">
                      <div className="flex-shrink-0">
                        <span className="text-red-400">⚠️</span>
                      </div>
                      <div className="ml-3">
                        <h3 className="text-sm font-medium text-red-800">Error Cotizaciones</h3>
                        <p className="text-sm text-red-700">{exchangeError}</p>
                      </div>
                    </div>
                  </CardBody>
                </Card>
              )}

              <div className="grid lg:grid-cols-2 gap-8 items-start">
                <Card>
                  <CardBody>
                    <ExchangeSearchForm 
                      onSearch={handleExchangeSearch} 
                      isLoading={isExchangeLoading}
                    />
                  </CardBody>
                </Card>

                <Card>
                  <CardBody>
                    <ExchangeResultsDisplay 
                      results={exchangeResults} 
                      searchType={exchangeSearchType}
                      isLoading={isExchangeLoading}
                      error={exchangeError}
                    />
                  </CardBody>
                </Card>
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
                <span 
                  className="cursor-pointer hover:text-red-500 transition-colors" 
                  onClick={() => setIsDashboardOpen(true)}
                  title="Abrir Dashboard de Monitoreo"
                >
                  {t('footer.developed_with_love') || 'Desarrollado con ❤️ usando React, FastAPI y Python'}
                </span>
              </p>
              <div className="flex justify-center items-center my-2">
                <UruguayFlagIcon className="flag-icon" aria-label="Uruguay" style={{verticalAlign: 'middle'}} />
              </div>
              <BuildInfoFooter />
            </div>
          </footer>
        </main>

        {/* Dashboard de Monitoreo */}
        <Dashboard 
          isOpen={isDashboardOpen} 
          onClose={() => setIsDashboardOpen(false)} 
        />
      </div>
    </ErrorBoundary>
  );
}

export default App; 