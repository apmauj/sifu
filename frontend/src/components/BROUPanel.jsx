import { useState, useCallback, useEffect, useRef, useMemo } from 'react';
// Eliminamos sentinel global para evitar quedarse en loading al volver desde otra pestaña
import { useI18n } from '../contexts/I18nContext';
import { useHourlySyncedUpdate } from '../hooks/useHourlySyncedUpdate';
import brouService from '../services/brouService';
import { useToast } from '../contexts/ToastContext';
import { OpenMojiIcon } from '../icons/openmoji/index.jsx';
import { Flag } from '../icons/flags.jsx';
import { RetryIcon } from '../components/icons/SimpleIcons.jsx';
import { getCurrencyDisplayMap } from '../utils/currencyDisplay.js';
import Badge from './ui/Badge';
import Alert from './ui/Alert';
import Button from './ui/Button';
import Spinner from './ui/Spinner';
import { getSemanticClass } from '../theme/colors';

const BROUPanel = () => {
  const { t } = useI18n();
  const [rates, setRates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [metadata, setMetadata] = useState(null);
  const { showSuccess, showError } = useToast();

  // Centralized currency info (panel-specific overrides handled in helper)
  const currencyInfo = useMemo(() => getCurrencyDisplayMap(t, 'brou'), [t]);

  const didInitRef = useRef(false);
  const fetchBROURates = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await brouService.getCurrent({ full: true });
      
      // Manejar nueva estructura de respuesta con metadata
      if (response.success && response.data && Array.isArray(response.data)) {
        setRates(response.data);
        setMetadata({
          source: response.source,
          sourceType: response.source_type,
          status: response.status,
          timestamp: response.timestamp,
          dataAge: response.data_age_minutes,
          isFresh: response.is_fresh,
          frontendDisplay: response.frontend_display
        });
        
        if (rates.length) {
          showSuccess(t('brou.updated') || 'Cotizaciones BROU actualizadas');
        }
      } else if (Array.isArray(response)) {
        // Compatibilidad con respuesta antigua (lista directa)
        setRates(response);
        setMetadata(null);
        if (rates.length) {
          showSuccess(t('brou.updated') || 'Cotizaciones BROU actualizadas');
        }
      } else {
        const msg = response.message || t('brou.error_loading') || 'Error obteniendo cotizaciones BROU';
        showError(msg);
        throw new Error(msg);
      }
    } catch (err) {
      console.error('Error fetching BROU rates:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [t, showSuccess, showError, rates.length]);

  // Cargar una vez al montar
  useEffect(() => {
    if (didInitRef.current) return;
    didInitRef.current = true;
    fetchBROURates();
  }, [fetchBROURates]);

  // Usar el hook personalizado para actualizaciones sincronizadas cada hora sin ejecución inmediata
  useHourlySyncedUpdate(fetchBROURates, true, { runImmediately: false });

  const formatRate = (rate) => {
    if (rate === null || rate === undefined) return '-';
    return rate.toFixed(2);
  };

  const formatArbitrage = (arbitrage) => {
    if (arbitrage === null || arbitrage === undefined) return '-';
    return arbitrage.toFixed(4);
  };

  const getCurrencyRowClass = (currency) => {
    // Better contrast in dark mode; subtle highlight for USD_EBROU
    const baseLight = "border-b border-neutral-100 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-700/30 transition-colors";
    if (currency === 'USD_EBROU') {
      return `${baseLight} bg-primary-50 dark:bg-primary-950/30 border-primary-100 dark:border-primary-800`;
    }
    return baseLight;
  };

  // Componente para badge de estado
  const StatusBadge = ({ metadata }) => {
    if (!metadata || !metadata.frontendDisplay) return null;
    
    const variantMap = {
      green: 'success',
      yellow: 'warning',
      red: 'error',
      gray: 'neutral'
    };
    
    const variant = variantMap[metadata.status.color] || 'neutral';
    
    return (
      <Badge variant={variant} size="sm" className="ml-2">
        {metadata.frontendDisplay.status_label}
      </Badge>
    );
  };

  // Componente para información de frescura
  const FreshnessInfo = ({ metadata }) => {
    if (!metadata) return null;
    
    const formatTimestamp = (timestamp) => {
      if (!timestamp) return '';
      try {
        return new Date(timestamp).toLocaleTimeString();
      } catch {
        return '';
      }
    };
    
    return (
      <div className="text-xs text-neutral-500 dark:text-neutral-400">
        {metadata.isFresh ? '✅' : '⚠️'} 
        {metadata.dataAge ? `${metadata.dataAge.toFixed(1)} min` : 'Sin datos'}
        {formatTimestamp(metadata.timestamp) && ` • ${formatTimestamp(metadata.timestamp)}`}
      </div>
    );
  };

  // Componente para mensaje de advertencia
  const WarningMessage = ({ metadata }) => {
    if (!metadata?.frontendDisplay?.warning_message) return null;
    
    return (
      <div className="mb-4">
        <Alert variant="warning">
          {metadata.frontendDisplay.warning_message}
        </Alert>
      </div>
    );
  };

  if (loading && Array.isArray(rates) && rates.length === 0) {
    return (
      <div className="bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100 flex items-center">
            <OpenMojiIcon name="bank" size={32} className="mr-3" />
            {t('brou.title') || 'BROU'}
          </h2>
        </div>
        <Spinner center size="lg" label={t('brou.loading') || 'Cargando cotizaciones...'} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100 flex items-center">
            <OpenMojiIcon name="bank" size={32} className="mr-3" />
            {t('brou.title') || 'BROU'}
          </h2>
          <Button
            onClick={fetchBROURates}
            variant="primary"
            leftIcon={<RetryIcon className="w-4 h-4" />}
          >
            {t('brou.retry') || 'Reintentar'}
          </Button>
        </div>
        <Alert variant="error" title={t('brou.error_loading') || 'Error al cargar cotizaciones'}>
          {error}
        </Alert>
      </div>
    );
  }

  const safeRates = Array.isArray(rates) ? rates : [];

  return (
    <div className="bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-lg shadow-md p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100 flex items-center">
          <OpenMojiIcon name="bank" size={32} className="mr-3" />
          {t('brou.title') || 'BROU'}
          <span className="ml-2 text-sm font-normal text-neutral-500 dark:text-neutral-400">
            {t('brou.bank_name') || 'Banco República'}
          </span>
          <StatusBadge metadata={metadata} />
        </h2>
        <div className="text-right">
          <FreshnessInfo metadata={metadata} />
        </div>
      </div>

      {/* Mensaje de advertencia si es necesario */}
      <WarningMessage metadata={metadata} />

      {/* Desktop View */}
      <div className="hidden md:block">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b-2 border-neutral-200 dark:border-neutral-700">
                <th className="text-left py-2 px-2 font-semibold text-neutral-700 dark:text-neutral-300">{t('brou.currency') || 'Moneda'}</th>
                <th className="text-center py-2 px-2 font-semibold text-neutral-700 dark:text-neutral-300">{t('brou.buy') || 'Compra'}</th>
                <th className="text-center py-2 px-2 font-semibold text-neutral-700 dark:text-neutral-300">{t('brou.sell') || 'Venta'}</th>
                <th className="text-center py-2 px-2 font-semibold text-neutral-700 dark:text-neutral-300">{t('brou.arbitrage_buy') || 'Arbitraje Compra'}</th>
                <th className="text-center py-2 px-2 font-semibold text-neutral-700 dark:text-neutral-300">{t('brou.arbitrage_sell') || 'Arbitraje Venta'}</th>
              </tr>
            </thead>
            <tbody>
              {safeRates.map((rate) => {
                const display = currencyInfo[rate.currency];
                if (!display) return null;

                return (
                  <tr key={rate.currency} className={getCurrencyRowClass(rate.currency)}>
        <td className="py-3 px-2">
                      <div className="flex items-center">
                        <Flag code={display.flag} className="flag-icon mr-2" />
                        <div>
          <div className="font-medium text-neutral-900 dark:text-neutral-100 flex items-center">
                            {display.name}
                            {display.special && (
                              <Badge variant="info" size="sm" className="ml-2">
                                {t('brou.preferential') || 'Preferencial'}
                              </Badge>
                            )}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="text-center py-3 px-2">
                      <span className={`font-mono font-medium ${getSemanticClass('buy', 'text', 600, 'data')}`}>
                        {display.symbol}{formatRate(rate.buy_rate)}
                      </span>
                    </td>
                    <td className="text-center py-3 px-2">
                      <span className={`font-mono font-medium ${getSemanticClass('sell', 'text', 600, 'data')}`}>
                        {display.symbol}{formatRate(rate.sell_rate)}
                      </span>
                    </td>
                    <td className="text-center py-3 px-2">
                      <span className={`font-mono text-sm ${getSemanticClass('highlight', 'text', 600, 'data')}`}>
                        {formatArbitrage(rate.arbitrage_buy)}
                      </span>
                    </td>
                    <td className="text-center py-3 px-2">
                      <span className={`font-mono text-sm ${getSemanticClass('highlight', 'text', 600, 'data')}`}>
                        {formatArbitrage(rate.arbitrage_sell)}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Mobile View */}
  <div className="md:hidden space-y-4">
        {safeRates.map((rate) => {
          const display = currencyInfo[rate.currency];
          if (!display) return null;

          return (
            <div key={rate.currency} className={`p-4 rounded-lg border ${
              rate.currency === 'USD_EBROU' 
                ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800' 
                : 'bg-neutral-50 dark:bg-neutral-700/40 border-neutral-200 dark:border-neutral-700'
            }`}>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center">
                  <Flag code={display.flag} className="flag-icon mr-2" />
                  <div>
                    <div className="font-medium text-neutral-900 dark:text-neutral-100 flex items-center">
                      {display.name}
                      {display.special && (
                        <Badge variant="info" size="sm" className="ml-2">
                          {t('brou.preferential') || 'Preferencial'}
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
              </div>
              
                              <div className="grid grid-cols-2 gap-3 text-sm">
                  <div className="text-center">
                    <div className="text-neutral-600 dark:text-neutral-300 mb-1">{t('brou.buy') || 'Compra'}</div>
                    <div className={`font-mono font-medium ${getSemanticClass('buy', 'text', 600, 'data')}`}>
                      {display.symbol}{formatRate(rate.buy_rate)}
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-neutral-600 dark:text-neutral-300 mb-1">{t('brou.sell') || 'Venta'}</div>
                    <div className={`font-mono font-medium ${getSemanticClass('sell', 'text', 600, 'data')}`}>
                      {display.symbol}{formatRate(rate.sell_rate)}
                    </div>
                  </div>
                
                {(rate.arbitrage_buy !== null || rate.arbitrage_sell !== null) && (
                                      <>
                      <div className="text-center">
                        <div className="text-neutral-600 dark:text-neutral-300 mb-1">{t('brou.arbitrage_buy') || 'Arb. Compra'}</div>
                        <div className={`font-mono text-sm ${getSemanticClass('highlight', 'text', 600, 'data')}`}>
                          {formatArbitrage(rate.arbitrage_buy)}
                        </div>
                      </div>
                      <div className="text-center">
                        <div className="text-neutral-600 dark:text-neutral-300 mb-1">{t('brou.arbitrage_sell') || 'Arb. Venta'}</div>
                        <div className={`font-mono text-sm ${getSemanticClass('highlight', 'text', 600, 'data')}`}>
                          {formatArbitrage(rate.arbitrage_sell)}
                        </div>
                      </div>
                    </>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer */}
      <div className="mt-4 pt-3 border-t border-neutral-200 dark:border-neutral-700">
        <div className="flex items-center justify-between text-xs text-neutral-500 dark:text-neutral-400">
          <span>{t('brou.source_footer') || t('brou.source') || 'Fuente: BROU • Actualización cada hora'}</span>
          <span>{t('brou.arbitrage_footer') || 'Arbitrajes calculados vs USD'}</span>
        </div>
      </div>
    </div>
  );
};

export default BROUPanel; 