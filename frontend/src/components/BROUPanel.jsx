import { useState, useCallback, useEffect, useRef } from 'react';
// Eliminamos sentinel global para evitar quedarse en loading al volver desde otra pestaña
import { useI18n } from '../contexts/I18nContext';
import { useHourlySyncedUpdate } from '../hooks/useHourlySyncedUpdate';
import brouService from '../services/brouService';
import { useToast } from '../contexts/ToastContext';

const BROUPanel = () => {
  const { t } = useI18n();
  const [rates, setRates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { showSuccess, showError } = useToast();

  // Currency display configuration with official Unicode emojis
  const currencyInfo = {
  USD: { symbol: '$', flag: 'USD', name: t('brou.currencies.USD') || 'Dólar USA' },
  USD_EBROU: { symbol: '$', flag: 'USD', name: t('brou.currencies.USD_EBROU') || 'Dólar eBROU', special: true },
  EUR: { symbol: '€', flag: 'EUR', name: t('brou.currencies.EUR') || 'Euro' },
  ARS: { symbol: '$', flag: 'ARS', name: t('brou.currencies.ARS') || 'Peso Arg.' },
  BRL: { symbol: 'R$', flag: 'BRL', name: t('brou.currencies.BRL') || 'Real' }
  };

  const didInitRef = useRef(false);
  const fetchBROURates = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await brouService.getCurrent();
      // Backend puede devolver lista directa (compat anterior) o objeto { success, data }
      const list = Array.isArray(data) ? data : (Array.isArray(data?.data) ? data.data : []);
      if (list.length > 0) {
        setRates(list);
        if (rates.length) {
          showSuccess(t('brou.updated') || 'Cotizaciones BROU actualizadas');
        }
      } else {
        const msg = (data && data.message) || t('brou.error_loading') || 'Error obteniendo cotizaciones BROU';
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
    const baseLight = "border-b border-gray-100 hover:bg-gray-50 transition-colors";
    const baseDark = "dark:border-gray-700 dark:hover:bg-gray-700/30";
    if (currency === 'USD_EBROU') {
      return `${baseLight} ${baseDark} bg-blue-50 dark:bg-blue-900/20 border-blue-100 dark:border-blue-800`;
    }
    return `${baseLight} ${baseDark}`;
  };

  if (loading && Array.isArray(rates) && rates.length === 0) {
    return (
              <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 flex items-center">
              <OpenMojiIcon name="bank" size={32} className="mr-3" />
              {t('brou.title') || 'BROU'}
            </h2>
          </div>
          <div className="flex justify-center items-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-2 text-gray-600">{t('brou.loading') || 'Cargando cotizaciones...'}</span>
          </div>
        </div>
    );
  }

  if (error) {
    return (
              <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 flex items-center">
              <OpenMojiIcon name="bank" size={32} className="mr-3" />
              {t('brou.title') || 'BROU'}
            </h2>
            <button
              onClick={fetchBROURates}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              <RetryIcon className="w-4 h-4 mr-2" />
              {t('brou.retry') || 'Reintentar'}
            </button>
          </div>
          <div className="text-center text-red-600 bg-red-50 p-4 rounded">
            <p className="font-medium">{t('brou.error_loading') || 'Error al cargar cotizaciones'}</p>
            <p className="text-sm mt-1">{error}</p>
          </div>
        </div>
    );
  }

  const safeRates = Array.isArray(rates) ? rates : [];

  return (
    <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-md p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 flex items-center">
          <OpenMojiIcon name="bank" size={32} className="mr-3" />
          {t('brou.title') || 'BROU'}
          <span className="ml-2 text-sm font-normal text-gray-500">
            {t('brou.bank_name') || 'Banco República'}
          </span>
        </h2>
        {/* Manual refresh button removed (auto hourly updates + retry only on error) */}
      </div>

      {/* Desktop View */}
      <div className="hidden md:block">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b-2 border-gray-200 dark:border-gray-700">
                <th className="text-left py-2 px-2 font-semibold text-gray-700 dark:text-gray-300">{t('brou.currency') || 'Moneda'}</th>
                <th className="text-center py-2 px-2 font-semibold text-gray-700 dark:text-gray-300">{t('brou.buy') || 'Compra'}</th>
                <th className="text-center py-2 px-2 font-semibold text-gray-700 dark:text-gray-300">{t('brou.sell') || 'Venta'}</th>
                <th className="text-center py-2 px-2 font-semibold text-gray-700 dark:text-gray-300">{t('brou.arbitrage_buy') || 'Arbitraje Compra'}</th>
                <th className="text-center py-2 px-2 font-semibold text-gray-700 dark:text-gray-300">{t('brou.arbitrage_sell') || 'Arbitraje Venta'}</th>
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
          <div className="font-medium text-gray-900 dark:text-gray-100 flex items-center">
                            {display.name}
                            {display.special && (
                              <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                                {t('brou.preferential') || 'Preferencial'}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="text-center py-3 px-2">
                      <span className="font-mono text-green-600 font-medium">
                        {display.symbol}{formatRate(rate.buy_rate)}
                      </span>
                    </td>
                    <td className="text-center py-3 px-2">
                      <span className="font-mono text-red-600 font-medium">
                        {display.symbol}{formatRate(rate.sell_rate)}
                      </span>
                    </td>
                    <td className="text-center py-3 px-2">
                      <span className="font-mono text-blue-600 text-sm">
                        {formatArbitrage(rate.arbitrage_buy)}
                      </span>
                    </td>
                    <td className="text-center py-3 px-2">
                      <span className="font-mono text-blue-600 text-sm">
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
                : 'bg-gray-50 dark:bg-gray-700/40 border-gray-200 dark:border-gray-700'
            }`}>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center">
                  <Flag code={display.flag} className="flag-icon mr-2" />
                  <div>
                    <div className="font-medium text-gray-900 dark:text-gray-100 flex items-center">
                      {display.name}
                      {display.special && (
                                              <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                        {t('brou.preferential') || 'Preferencial'}
                      </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
              
                              <div className="grid grid-cols-2 gap-3 text-sm">
                  <div className="text-center">
                    <div className="text-gray-600 dark:text-gray-300 mb-1">{t('brou.buy') || 'Compra'}</div>
                    <div className="font-mono text-green-600 font-medium">
                      {display.symbol}{formatRate(rate.buy_rate)}
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-gray-600 dark:text-gray-300 mb-1">{t('brou.sell') || 'Venta'}</div>
                    <div className="font-mono text-red-600 font-medium">
                      {display.symbol}{formatRate(rate.sell_rate)}
                    </div>
                  </div>
                
                {(rate.arbitrage_buy !== null || rate.arbitrage_sell !== null) && (
                                      <>
                      <div className="text-center">
                        <div className="text-gray-600 dark:text-gray-300 mb-1">{t('brou.arbitrage_buy') || 'Arb. Compra'}</div>
                        <div className="font-mono text-blue-600 text-sm">
                          {formatArbitrage(rate.arbitrage_buy)}
                        </div>
                      </div>
                      <div className="text-center">
                        <div className="text-gray-600 dark:text-gray-300 mb-1">{t('brou.arbitrage_sell') || 'Arb. Venta'}</div>
                        <div className="font-mono text-blue-600 text-sm">
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
      <div className="mt-4 pt-3 border-t border-gray-200">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>{t('brou.source_footer') || t('brou.source') || 'Fuente: BROU • Actualización cada hora'}</span>
          <span>{t('brou.arbitrage_footer') || 'Arbitrajes calculados vs USD'}</span>
        </div>
      </div>
    </div>
  );
};

export default BROUPanel; 