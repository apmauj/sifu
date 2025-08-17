import React, { useState, useCallback, useEffect, useRef } from 'react';
// Sentinel de módulo para carga inicial única bajo StrictMode
// Reemplazamos sentinel global por ref interna para evitar estados inconsistentes al cambiar de pestañas
let EXCHANGE_RATE_PANEL_INIT = false;
import exchangeService from '../services/exchangeService';
import { useI18n } from '../contexts/I18nContext';
import { useHourlySyncedUpdate } from '../hooks/useHourlySyncedUpdate';
// Centralized icons (RefreshIcon not used after removing manual refresh)
import { ChartIcon, LoadingIcon } from '../icons';
import { useToast } from '../contexts/ToastContext';

const ExchangeRatePanel = () => {
  const [currentRates, setCurrentRates] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const { t } = useI18n();
  const { showSuccess, showError } = useToast();
  const didInitRef = useRef(false);
  const manualRefreshRef = useRef(false); // retained for minimal change though manual trigger removed

  const currencyInfo = {
    USD: { symbol: 'US$', flag: '🇺🇸', name: t('exchange.currencies.USD') || 'Dólar USA' },
    EUR: { symbol: '€', flag: '🇪🇺', name: t('exchange.currencies.EUR') || 'Euro' },
    ARS: { symbol: 'AR$', flag: '🇦🇷', name: t('exchange.currencies.ARS') || 'Peso Arg.' },
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
        if (manualRefreshRef.current) {
          // Only show toast on user-initiated refreshes, not first load
          showSuccess(t('bcu.updated') || 'Cotizaciones BCU actualizadas');
        }
      } else {
        const msg = t('bcu.error') || 'Error obteniendo cotizaciones actuales';
        setError(msg);
        if (manualRefreshRef.current) showError(msg);
      }
    } catch (e) {
      console.error('Error fetching current rates:', e);
      const msg = t('errors.exchange_load_failed') || 'Error de conexión';
      setError(msg);
      if (manualRefreshRef.current) showError(msg);
    } finally {
      setIsLoading(false);
      manualRefreshRef.current = false;
    }
  }, [t, showSuccess, showError, currentRates.length]);

  // First load on mount (manteniendo compatibilidad StrictMode sin doble fetch)
  useEffect(() => {
    if (didInitRef.current) return;
    didInitRef.current = true;
    fetchCurrentRates();
  }, [fetchCurrentRates]);

  // Manual refresh removed (auto hourly update); leaving helper commented for potential future use
  // const handleManualRefresh = () => {
  //   manualRefreshRef.current = true;
  //   fetchCurrentRates();
  // };

  // Hourly sync without immediate initial fetch (to avoid duplicate on mount)
  useHourlySyncedUpdate(fetchCurrentRates, true, { runImmediately: false });

  const formatRate = (rate) => {
    if (rate === null || rate === undefined) return 'N/A';
    return rate >= 1 ? rate.toFixed(2) : rate.toFixed(4);
  };

  const formatTime = (date) =>
    date.toLocaleTimeString('es-UY', { hour: '2-digit', minute: '2-digit', hour12: false });

  if (isLoading && currentRates.length === 0) {
    return (
      <div className="px-4">
        <div className="max-w-7xl mx-auto">
          <div className="bg-gray-800 text-white py-2 px-4 rounded-xl shadow-sm">
            <div className="text-center">
              <span className="text-sm flex items-center justify-center">
                <LoadingIcon className="w-4 h-4 mr-2 text-blue-400" />
                {t('bcu.loading') || 'Cargando cotizaciones...'}
              </span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error && currentRates.length === 0) {
    return (
      <div className="px-4">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-600 text-white py-2 px-4 rounded-xl shadow-sm">
            <div className="text-center">
              <span className="text-sm">❌ {error}</span>
              <button onClick={fetchCurrentRates} className="ml-2 text-xs underline hover:no-underline">
                {t('bcu.retry') || 'Reintentar'}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="bg-gradient-to-r from-blue-700 to-blue-800 text-white py-2 px-4 shadow-lg rounded-xl ring-1 ring-blue-900/20">
          {/* Desktop */}
          <div className="hidden lg:block relative">
            {/* Title fixed at left */}
            <div className="absolute left-0 top-1/2 -translate-y-1/2 flex items-center gap-2 pr-4">
              <span className="text-sm font-medium flex items-center">
                <ChartIcon className="w-4 h-4 mr-2 text-white" />
                {t('bcu.title') || 'Cotizaciones BCU'}
              </span>
            </div>
            {/* Centered rates independent of title width */}
            <div className="pointer-events-none flex items-center justify-center">
              <div className="flex items-center gap-3 justify-center mx-auto">
                {currentRates.slice(0, 4).map((rate) => {
                  const display = currencyInfo[rate.currency];
                  if (!display) return null;
                  return (
                    <div key={rate.currency} className="flex items-center gap-1 bg-blue-600/50 px-2 py-1 rounded text-xs pointer-events-auto">
                      <span className="text-sm">{display.flag}</span>
                      <span className="font-medium">{rate.currency}</span>
                      <span className="text-blue-200">|</span>
                      {rate.buy_rate === rate.sell_rate ? (
                        <span className="text-yellow-300 font-medium">{display.symbol}{formatRate(rate.average_rate)}</span>
                      ) : (
                        <>
                          <span className="text-green-300">{display.symbol}{formatRate(rate.buy_rate)}</span>
                          <span className="text-blue-200">-</span>
                          <span className="text-red-300">{display.symbol}{formatRate(rate.sell_rate)}</span>
                        </>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
            {/* Loader at right */}
            <div className="absolute right-0 top-1/2 -translate-y-1/2 flex items-center gap-2">
              {isLoading && <LoadingIcon className="w-4 h-4 animate-spin" />}
            </div>
          </div>

          {/* Tablet */}
          <div className="hidden md:block lg:hidden">
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm font-medium flex items-center">
                <ChartIcon className="w-4 h-4 mr-2 text-white" />
                {t('bcu.title') || 'Cotizaciones BCU'}
              </span>
              {isLoading && <LoadingIcon className="w-4 h-4 animate-spin" />}
            </div>
            <div className="flex flex-wrap items-center gap-2 justify-center">
              {currentRates.slice(0, 4).map((rate) => {
                const display = currencyInfo[rate.currency];
                if (!display) return null;
                return (
                  <div key={rate.currency} className="flex items-center gap-1 bg-blue-600/50 px-2 py-1 rounded text-xs">
                    <span className="text-sm">{display.flag}</span>
                    <span className="font-medium">{rate.currency}</span>
                    <span className="text-blue-200">|</span>
                    {rate.buy_rate === rate.sell_rate ? (
                      <span className="text-yellow-300 font-medium">{display.symbol}{formatRate(rate.average_rate)}</span>
                    ) : (
                      <>
                        <span className="text-green-300">{display.symbol}{formatRate(rate.buy_rate)}</span>
                        <span className="text-blue-200">-</span>
                        <span className="text-red-300">{display.symbol}{formatRate(rate.sell_rate)}</span>
                      </>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Mobile */}
          <div className="md:hidden">
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm font-medium flex items-center">
                <ChartIcon className="w-4 h-4 mr-2 text-white" />
                {t('bcu.title') || 'Cotizaciones BCU'}
              </span>
              {isLoading && <LoadingIcon className="w-4 h-4 animate-spin" />}
            </div>
            <div className="flex flex-wrap items-center gap-2">
              {currentRates.slice(0, 4).map((rate) => {
                const display = currencyInfo[rate.currency];
                if (!display) return null;
                return (
                  <div key={rate.currency} className="flex items-center gap-1 bg-blue-600/50 px-2 py-1 rounded text-xs">
                    <span className="text-sm">{display.flag}</span>
                    <span className="font-medium">{rate.currency}</span>
                    <span className="text-blue-200">|</span>
                    {rate.buy_rate === rate.sell_rate ? (
                      <span className="text-yellow-300 font-medium">{display.symbol}{formatRate(rate.average_rate)}</span>
                    ) : (
                      <>
                        <span className="text-green-300">{display.symbol}{formatRate(rate.buy_rate)}</span>
                        <span className="text-blue-200">-</span>
                        <span className="text-red-300">{display.symbol}{formatRate(rate.sell_rate)}</span>
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