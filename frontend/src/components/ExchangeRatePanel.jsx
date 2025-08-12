import React, { useState, useCallback, useEffect, useRef } from 'react';
// Sentinel de módulo para carga inicial única bajo StrictMode
// Reemplazamos sentinel global por ref interna para evitar estados inconsistentes al cambiar de pestañas
let EXCHANGE_RATE_PANEL_INIT = false;
import exchangeService from '../services/exchangeService';
import { useI18n } from '../contexts/I18nContext';
import { useHourlySyncedUpdate } from '../hooks/useHourlySyncedUpdate';
import { ChartIcon, RefreshIcon, LoadingIcon } from './icons';
import { useToast } from '../contexts/ToastContext';

const ExchangeRatePanel = () => {
  const [currentRates, setCurrentRates] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const { t } = useI18n();
  const { showSuccess, showError } = useToast();
  const didInitRef = useRef(false);
  const manualRefreshRef = useRef(false);

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
      const msg = t('bcu.error') || 'Error de conexión';
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

  const handleManualRefresh = () => {
    manualRefreshRef.current = true;
    fetchCurrentRates();
  };

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
          <div className="hidden lg:flex items-center justify-between gap-4">
            <div className="flex items-center gap-2 flex-shrink-0">
              <span className="text-sm font-medium flex items-center">
                <ChartIcon className="w-4 h-4 mr-2 text-white" />
                {t('bcu.title') || 'Cotizaciones BCU'}
              </span>
              {lastUpdate && <span className="text-xs text-blue-200">{formatTime(lastUpdate)}</span>}
            </div>

            <div className="flex items-center gap-3 flex-1 justify-center">
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

            <div className="flex items-center gap-2 flex-shrink-0">
              <button
                onClick={handleManualRefresh}
                disabled={isLoading}
                className="text-xs bg-blue-600 hover:bg-blue-500 px-2 py-1 rounded transition-colors disabled:opacity-50"
                title={t('bcu.retry') || 'Actualizar cotizaciones'}
              >
                {isLoading ? <LoadingIcon className="w-4 h-4" /> : <RefreshIcon className="w-4 h-4" />}
              </button>
              <span className="text-xs text-blue-200">{t('bcu.source') || 'BCU'}</span>
            </div>
          </div>

          {/* Tablet */}
          <div className="hidden md:block lg:hidden">
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm font-medium flex items-center">
                <ChartIcon className="w-4 h-4 mr-2 text-white" />
                {t('bcu.title') || 'Cotizaciones BCU'}
              </span>
              <button onClick={handleManualRefresh} disabled={isLoading} className="p-2 text-white/80 hover:text-white disabled:opacity-50">
                {isLoading ? <LoadingIcon className="w-4 h-4" /> : <RefreshIcon className="w-4 h-4" />}
              </button>
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
                {t('bcu.source') || 'BCU'}
              </span>
              <button onClick={handleManualRefresh} disabled={isLoading} className="p-2 text-white/80 hover:text-white disabled:opacity-50">
                {isLoading ? <LoadingIcon className="w-4 h-4" /> : <RefreshIcon className="w-4 h-4" />}
              </button>
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