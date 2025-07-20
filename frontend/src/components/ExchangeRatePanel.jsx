import React, { useState, useCallback } from 'react';
import exchangeService from '../services/exchangeService';
import { useI18n } from '../contexts/I18nContext';
import { useHourlySyncedUpdate } from '../hooks/useHourlySyncedUpdate';
import { ChartIcon, RefreshIcon, LoadingIcon } from './icons';

const ExchangeRatePanel = () => {
  const [currentRates, setCurrentRates] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const { t } = useI18n();

  // Currency symbols and flags with official Unicode emojis
  const currencyInfo = {
    USD: { symbol: '$', flag: '🇺🇸', name: t('exchange.currencies.USD') || 'Dólar USA' },
    EUR: { symbol: '€', flag: '🇪🇺', name: t('exchange.currencies.EUR') || 'Euro' },
    ARS: { symbol: '$', flag: '🇦🇷', name: t('exchange.currencies.ARS') || 'Peso Arg.' },
    BRL: { symbol: 'R$', flag: '🇧🇷', name: t('exchange.currencies.BRL') || 'Real' }
  };

  const fetchCurrentRates = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await exchangeService.getCurrentRates();
      
      if (response.success && response.data) {
        setCurrentRates(response.data);
        setLastUpdate(new Date());
      } else {
        setError(t('bcu.error') || 'Error obteniendo cotizaciones actuales');
      }
    } catch (error) {
      console.error('Error fetching current rates:', error);
      setError(t('bcu.error') || 'Error de conexión');
    } finally {
      setIsLoading(false);
    }
  }, [t]);

  // Usar el hook personalizado para actualizaciones sincronizadas cada hora
  useHourlySyncedUpdate(fetchCurrentRates);

  const formatRate = (rate) => {
    if (rate === null || rate === undefined) return 'N/A';
    if (rate >= 1) {
      return rate.toFixed(2);
    } else {
      return rate.toFixed(4);
    }
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString('es-UY', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false 
    });
  };

  if (isLoading && currentRates.length === 0) {
    return (
      <div className="bg-gray-800 text-white py-2 px-4 shadow-sm">
        <div className="container mx-auto text-center">
          <span className="text-sm flex items-center">
            <LoadingIcon className="w-4 h-4 mr-2 text-blue-600" />
            {t('bcu.loading') || 'Cargando cotizaciones...'}
          </span>
        </div>
      </div>
    );
  }

  if (error && currentRates.length === 0) {
    return (
      <div className="bg-red-600 text-white py-2 px-4 shadow-sm">
        <div className="container mx-auto text-center">
          <span className="text-sm">❌ {error}</span>
          <button 
            onClick={fetchCurrentRates}
            className="ml-2 text-xs underline hover:no-underline"
          >
            {t('bcu.retry') || 'Reintentar'}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-r from-blue-700 to-blue-800 text-white py-2 px-4 shadow-lg">
      <div className="container mx-auto">
        {/* Desktop Layout (lg and up) */}
        <div className="hidden lg:flex items-center justify-between gap-4">
          {/* Title and timestamp */}
          <div className="flex items-center gap-2 flex-shrink-0">
            <span className="text-sm font-medium flex items-center">
              <ChartIcon className="w-4 h-4 mr-2 text-blue-600" />
              {t('bcu.title') || 'Cotizaciones BCU'}
            </span>
            {lastUpdate && (
              <span className="text-xs text-blue-200">
                {formatTime(lastUpdate)}
              </span>
            )}
          </div>

          {/* Exchange Rates */}
          <div className="flex items-center gap-3 flex-1 justify-center">
            {currentRates.slice(0, 4).map((rate) => {
              const display = currencyInfo[rate.currency];
              if (!display) return null;

              return (
                <div 
                  key={rate.currency}
                  className="flex items-center gap-1 bg-blue-600 bg-opacity-50 px-2 py-1 rounded text-xs"
                >
                  <span className="text-sm">{display.flag}</span>
                  <span className="font-medium">{rate.currency}</span>
                  <span className="text-blue-200">|</span>
                  {rate.buy_rate === rate.sell_rate ? (
                    <span className="text-yellow-300 font-medium">
                      {display.symbol}{formatRate(rate.average_rate)}
                    </span>
                  ) : (
                    <>
                      <span className="text-green-300">
                        {display.symbol}{formatRate(rate.buy_rate)}
                      </span>
                      <span className="text-blue-200">-</span>
                      <span className="text-red-300">
                        {display.symbol}{formatRate(rate.sell_rate)}
                      </span>
                    </>
                  )}
                </div>
              );
            })}
          </div>

          {/* Refresh button and source */}
          <div className="flex items-center gap-2 flex-shrink-0">
            <button
              onClick={fetchCurrentRates}
              disabled={isLoading}
              className="text-xs bg-blue-600 hover:bg-blue-500 px-2 py-1 rounded transition-colors disabled:opacity-50"
              title={t('bcu.retry') || 'Actualizar cotizaciones'}
            >
              {isLoading ? (
                <LoadingIcon className="w-4 h-4" />
              ) : (
                <RefreshIcon className="w-4 h-4" />
              )}
            </button>
            <span className="text-xs text-blue-200">{t('bcu.source') || 'BCU'}</span>
          </div>
        </div>

        {/* Tablet Layout (md to lg) */}
        <div className="hidden md:block lg:hidden">
          {/* First row: Title and refresh button */}
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-medium flex items-center">
              <ChartIcon className="w-4 h-4 mr-2 text-blue-600" />
              {t('bcu.title') || 'Cotizaciones BCU'}
            </span>
            <button
              onClick={fetchCurrentRates}
              disabled={isLoading}
              className="p-2 text-gray-500 hover:text-gray-700 disabled:opacity-50"
            >
              {isLoading ? (
                <LoadingIcon className="w-4 h-4" />
              ) : (
                <RefreshIcon className="w-4 h-4" />
              )}
            </button>
          </div>
          
          {/* Second row: Exchange rates */}
          <div className="flex flex-wrap items-center gap-2 justify-center">
            {currentRates.slice(0, 4).map((rate) => {
              const display = currencyInfo[rate.currency];
              if (!display) return null;

              return (
                <div 
                  key={rate.currency}
                  className="flex items-center gap-1 bg-blue-600 bg-opacity-50 px-2 py-1 rounded text-xs"
                >
                  <span className="text-sm">{display.flag}</span>
                  <span className="font-medium">{rate.currency}</span>
                  <span className="text-blue-200">|</span>
                  {rate.buy_rate === rate.sell_rate ? (
                    <span className="text-yellow-300 font-medium">
                      {display.symbol}{formatRate(rate.average_rate)}
                    </span>
                  ) : (
                    <>
                      <span className="text-green-300">
                        {display.symbol}{formatRate(rate.buy_rate)}
                      </span>
                      <span className="text-blue-200">-</span>
                      <span className="text-red-300">
                        {display.symbol}{formatRate(rate.sell_rate)}
                      </span>
                    </>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Mobile Layout (below md) */}
        <div className="md:hidden">
          {/* First row: Title and refresh button */}
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-medium flex items-center">
              <ChartIcon className="w-4 h-4 mr-2 text-blue-600" />
              {t('bcu.source') || 'BCU'}
            </span>
            <button
              onClick={fetchCurrentRates}
              disabled={isLoading}
              className="p-2 text-gray-500 hover:text-gray-700 disabled:opacity-50"
            >
              {isLoading ? (
                <LoadingIcon className="w-4 h-4" />
              ) : (
                <RefreshIcon className="w-4 h-4" />
              )}
            </button>
          </div>
          
          {/* Second row: Exchange rates */}
          <div className="flex flex-wrap items-center gap-2">
            {currentRates.slice(0, 4).map((rate) => {
              const display = currencyInfo[rate.currency];
              if (!display) return null;

              return (
                <div 
                  key={rate.currency}
                  className="flex items-center gap-1 bg-blue-600 bg-opacity-50 px-2 py-1 rounded text-xs"
                >
                  <span className="text-sm">{display.flag}</span>
                  <span className="font-medium">{rate.currency}</span>
                  <span className="text-blue-200">|</span>
                  {rate.buy_rate === rate.sell_rate ? (
                    <span className="text-yellow-300 font-medium">
                      {display.symbol}{formatRate(rate.average_rate)}
                    </span>
                  ) : (
                    <>
                      <span className="text-green-300">
                        {display.symbol}{formatRate(rate.buy_rate)}
                      </span>
                      <span className="text-blue-200">-</span>
                      <span className="text-red-300">
                        {display.symbol}{formatRate(rate.sell_rate)}
                      </span>
                    </>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExchangeRatePanel; 