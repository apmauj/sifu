import React, { useState, useCallback } from 'react';
import { useI18n } from '../contexts/I18nContext';
import { useHourlySyncedUpdate } from '../hooks/useHourlySyncedUpdate';
import brouService from '../services/brouService';
import { BankIcon, RefreshIcon, LoadingIcon, RetryIcon } from './icons';

const BROUPanel = () => {
  const { t } = useI18n();
  const [rates, setRates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  // Currency display configuration with official Unicode emojis
  const currencyInfo = {
    USD: { symbol: '$', flag: '🇺🇸', name: t('brou.currencies.USD') || 'Dólar USA' },
    USD_EBROU: { symbol: '$', flag: '🇺🇸', name: t('brou.currencies.USD_EBROU') || 'Dólar eBROU', special: true },
    EUR: { symbol: '€', flag: '🇪🇺', name: t('brou.currencies.EUR') || 'Euro' },
    ARS: { symbol: '$', flag: '🇦🇷', name: t('brou.currencies.ARS') || 'Peso Arg.' },
    BRL: { symbol: 'R$', flag: '🇧🇷', name: t('brou.currencies.BRL') || 'Real' }
  };

  const fetchBROURates = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await brouService.getCurrent();
      if (data.success && data.data) {
        setRates(data.data);
        setLastUpdate(new Date());
      } else {
        throw new Error(data.message || t('brou.error_loading') || 'Error obteniendo cotizaciones BROU');
      }
    } catch (err) {
      console.error('Error fetching BROU rates:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [t]);

  // Usar el hook personalizado para actualizaciones sincronizadas cada hora
  useHourlySyncedUpdate(fetchBROURates);

  const formatRate = (rate) => {
    if (rate === null || rate === undefined) return '-';
    return rate.toFixed(2);
  };

  const formatArbitrage = (arbitrage) => {
    if (arbitrage === null || arbitrage === undefined) return '-';
    return arbitrage.toFixed(4);
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString('es-UY', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false 
    });
  };

  const getCurrencyRowClass = (currency) => {
    const baseClass = "border-b border-gray-100 hover:bg-gray-50 transition-colors";
    if (currency === 'USD_EBROU') {
      return `${baseClass} bg-blue-50 border-blue-100`;
    }
    return baseClass;
  };

  if (loading && rates.length === 0) {
    return (
              <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900 flex items-center">
              <BankIcon className="w-8 h-8 mr-3 text-green-600" />
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
              <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900 flex items-center">
              <BankIcon className="w-8 h-8 mr-3 text-green-600" />
              {t('brou.title') || 'BROU'}
            </h2>
            <button
              onClick={fetchBROURates}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
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

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center">
          <BankIcon className="w-8 h-8 mr-3 text-green-600" />
          {t('brou.title') || 'BROU'}
          <span className="ml-2 text-sm font-normal text-gray-500">
            {t('brou.bank_name') || 'Banco República'}
          </span>
        </h2>
        <button
          onClick={fetchBROURates}
          disabled={loading}
          className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
        >
          {loading ? (
            <LoadingIcon className="w-4 h-4 mr-2" />
          ) : (
            <RefreshIcon className="w-4 h-4 mr-2" />
          )}
          {loading ? t('common.loading') || 'Cargando...' : t('common.refresh') || 'Actualizar'}
        </button>
      </div>

      {/* Desktop View */}
      <div className="hidden md:block">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b-2 border-gray-200">
                <th className="text-left py-2 px-2 font-semibold text-gray-700">{t('brou.currency') || 'Moneda'}</th>
                <th className="text-center py-2 px-2 font-semibold text-gray-700">{t('brou.buy') || 'Compra'}</th>
                <th className="text-center py-2 px-2 font-semibold text-gray-700">{t('brou.sell') || 'Venta'}</th>
                <th className="text-center py-2 px-2 font-semibold text-gray-700">{t('brou.arbitrage_buy') || 'Arbitraje Compra'}</th>
                <th className="text-center py-2 px-2 font-semibold text-gray-700">{t('brou.arbitrage_sell') || 'Arbitraje Venta'}</th>
              </tr>
            </thead>
            <tbody>
              {rates.map((rate) => {
                const display = currencyInfo[rate.currency];
                if (!display) return null;

                return (
                  <tr key={rate.currency} className={getCurrencyRowClass(rate.currency)}>
                    <td className="py-3 px-2">
                      <div className="flex items-center">
                        <span className="text-lg mr-2">{display.flag}</span>
                        <div>
                          <div className="font-medium text-gray-900 flex items-center">
                            {display.name}
                            {display.special && (
                              <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                                {t('brou.preferential') || 'Preferencial'}
                              </span>
                            )}
                          </div>
                          <div className="text-sm text-gray-500">{rate.currency}</div>
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
        {rates.map((rate) => {
          const display = currencyInfo[rate.currency];
          if (!display) return null;

          return (
            <div key={rate.currency} className={`p-4 rounded-lg border ${
              rate.currency === 'USD_EBROU' ? 'bg-blue-50 border-blue-200' : 'bg-gray-50 border-gray-200'
            }`}>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center">
                  <span className="text-lg mr-2">{display.flag}</span>
                  <div>
                    <div className="font-medium text-gray-900 flex items-center">
                      {display.name}
                      {display.special && (
                                              <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                        {t('brou.preferential') || 'Preferencial'}
                      </span>
                      )}
                    </div>
                    <div className="text-sm text-gray-500">{rate.currency}</div>
                  </div>
                </div>
              </div>
              
                              <div className="grid grid-cols-2 gap-3 text-sm">
                  <div className="text-center">
                    <div className="text-gray-600 mb-1">{t('brou.buy') || 'Compra'}</div>
                    <div className="font-mono text-green-600 font-medium">
                      {display.symbol}{formatRate(rate.buy_rate)}
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-gray-600 mb-1">{t('brou.sell') || 'Venta'}</div>
                    <div className="font-mono text-red-600 font-medium">
                      {display.symbol}{formatRate(rate.sell_rate)}
                    </div>
                  </div>
                
                {(rate.arbitrage_buy !== null || rate.arbitrage_sell !== null) && (
                                      <>
                      <div className="text-center">
                        <div className="text-gray-600 mb-1">{t('brou.arbitrage_buy') || 'Arb. Compra'}</div>
                        <div className="font-mono text-blue-600 text-sm">
                          {formatArbitrage(rate.arbitrage_buy)}
                        </div>
                      </div>
                      <div className="text-center">
                        <div className="text-gray-600 mb-1">{t('brou.arbitrage_sell') || 'Arb. Venta'}</div>
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
          <span>{t('brou.source_footer') || 'Fuente: BROU • Actualización cada hora'}</span>
          <span>{t('brou.arbitrage_footer') || 'Arbitrajes calculados vs USD'}</span>
        </div>
      </div>
    </div>
  );
};

export default BROUPanel; 