import React, { useState, useCallback, useEffect, useRef } from 'react';
// Sentinel de módulo para carga inicial única bajo StrictMode
// Reemplazamos sentinel global por ref interna para evitar estados inconsistentes al cambiar de pestañas
let EXCHANGE_RATE_PANEL_INIT = false;
import exchangeService from '../services/exchangeService';
import { useI18n } from '../contexts/I18nContext';
import { useHourlySyncedUpdate } from '../hooks/useHourlySyncedUpdate';
// Centralized icons (RefreshIcon not used after removing manual refresh)
import { LoadingIcon } from '../icons';
import { OpenMojiIcon } from '../icons/openmoji/index.jsx';
import { Flag } from '../icons/flags';
import { useToast } from '../contexts/ToastContext';

const ExchangeRatePanel = () => {
  const [glow, setGlow] = useState(false);
  // Persisted preference to hide the status dot
  const DOT_HIDE_KEY = 'bcu.statusDotHidden';
  const [dotHidden, setDotHidden] = useState(() => {
    try { return localStorage.getItem(DOT_HIDE_KEY) === 'true'; } catch { return false; }
  });
  const [dotActive, setDotActive] = useState(true);
  const [currentRates, setCurrentRates] = useState([]);
  const lastDataHashRef = useRef(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const { t } = useI18n();
  const { showSuccess, showError } = useToast();
  const didInitRef = useRef(false);
  const manualRefreshRef = useRef(false); // retained for minimal change though manual trigger removed

  // Centralizamos flags por código (sin emojis en UI para consistencia visual SVG)
  const currencyInfo = {
    USD: { symbol: 'US$', flag: 'USD', name: t('exchange.currencies.USD') || 'Dólar USA' },
    EUR: { symbol: '€', flag: 'EUR', name: t('exchange.currencies.EUR') || 'Euro' },
    ARS: { symbol: 'AR$', flag: 'ARS', name: t('exchange.currencies.ARS') || 'Peso Arg.' },
    BRL: { symbol: 'R$', flag: 'BRL', name: t('exchange.currencies.BRL') || 'Real' }
  };

  const fetchCurrentRates = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await exchangeService.getCurrentRates();
      const raw = response && (response.data ?? response);
      const list = Array.isArray(raw) ? raw : (Array.isArray(raw?.data) ? raw.data : []);
      if (response?.success && list.length >= 0) { // accept empty list
        // Calculate a simple hash of the data for change detection
        const dataHash = JSON.stringify(list);
        const isUpdated = lastDataHashRef.current !== dataHash;
        setCurrentRates(list);
        const now = new Date();
        setLastUpdate(now);
        if (isUpdated) {
          setGlow(true);
          // Respeta preferencia del usuario: no reactivar si eligió ocultarlo
          if (!dotHidden) setDotActive(true);
          setTimeout(() => setGlow(false), 2000);
        }
  // Success toast removed: no notification on update or currency change
        lastDataHashRef.current = dataHash;
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
  }, [t, showSuccess, showError, dotHidden]);

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
              {/* Retry button removed: automatic hourly sync / potential future auto retry */}
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
            {/* Title fixed at left (new UX without emoji or manual refresh) */}
            <div className="absolute left-0 top-1/2 -translate-y-1/2 flex items-center pr-4">
              <span className="text-sm font-medium flex items-center">
                <OpenMojiIcon name="chartUp" size={16} className="mr-2" />
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
                      <Flag code={display.flag} className="w-5 h-4" />
                      <span className="sr-only">{display.flag}</span>
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
            {/* Status dot at the far right for visual balance */}
            { !dotHidden && (
              <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center group">
                <span
                  className={`inline-block w-3 h-3 rounded-full ${dotActive ? 'bg-green-400' : 'bg-gray-400'} cursor-pointer ${dotActive && glow ? 'animate-glow' : ''}`}
                  style={{ boxShadow: dotActive ? (glow ? '0 0 8px 4px #22c55e' : '0 0 2px 1px #22c55e') : '0 0 2px 1px #888', transition: 'box-shadow 0.3s' }}
                  onClick={() => { setDotActive(false); setDotHidden(true); try { localStorage.setItem(DOT_HIDE_KEY, 'true'); } catch {} }}
                  title={lastUpdate ? `${t('bcu.last_update') || 'Actualizado'}: ${formatTime(lastUpdate)}` : t('bcu.no_update') || 'Sin actualización'}
                />
                <span className="absolute right-6 top-1/2 -translate-y-1/2 bg-gray-900 text-white text-xs rounded px-2 py-1 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-10 shadow-lg border border-gray-700">
                  {lastUpdate ? `${t('bcu.last_update') || 'Actualizado'}: ${formatTime(lastUpdate)}` : t('bcu.no_update') || 'Sin actualización'}
                </span>
              </div>
            )}
          </div>

          {/* Tablet */}
          <div className="hidden md:block lg:hidden">
            <div className="flex items-center justify-between mb-4 relative">
              <span className="text-sm font-medium flex items-center">
                <OpenMojiIcon name="chartUp" size={16} className="mr-2" />
                {t('bcu.title') || 'Cotizaciones BCU'}
              </span>
              {/* Status dot at right */}
              { !dotHidden && (
                <span className="flex items-center group">
                  <span
                    className={`inline-block w-3 h-3 rounded-full ${dotActive ? 'bg-green-400' : 'bg-gray-400'} cursor-pointer ${dotActive && glow ? 'animate-glow' : ''}`}
                    style={{ boxShadow: dotActive ? (glow ? '0 0 8px 4px #22c55e' : '0 0 2px 1px #22c55e') : '0 0 2px 1px #888', transition: 'box-shadow 0.3s' }}
                    onClick={() => { setDotActive(false); setDotHidden(true); try { localStorage.setItem(DOT_HIDE_KEY, 'true'); } catch {} }}
                    title={lastUpdate ? `${t('bcu.last_update') || 'Actualizado'}: ${formatTime(lastUpdate)}` : t('bcu.no_update') || 'Sin actualización'}
                  />
                  <span className="ml-2 bg-gray-900 text-white text-xs rounded px-2 py-1 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-10 shadow-lg border border-gray-700">
                    {lastUpdate ? `${t('bcu.last_update') || 'Actualizado'}: ${formatTime(lastUpdate)}` : t('bcu.no_update') || 'Sin actualización'}
                  </span>
                </span>
              )}
            </div>
            <div className="flex flex-wrap items-center gap-2 justify-center">
              {currentRates.slice(0, 4).map((rate) => {
                const display = currencyInfo[rate.currency];
                if (!display) return null;
                return (
                  <div key={rate.currency} className="flex items-center gap-1 bg-blue-600/50 px-2 py-1 rounded text-xs">
                    <Flag code={display.flag} className="w-5 h-4" />
                    <span className="sr-only">{display.flag}</span>
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
                <OpenMojiIcon name="chartUp" size={16} className="mr-2" />
                {t('bcu.title') || 'Cotizaciones BCU'}
              </span>
              {/* Status dot at right */}
              { !dotHidden && (
                <span className="flex items-center group">
                  <span
                    className={`inline-block w-3 h-3 rounded-full ${dotActive ? 'bg-green-400' : 'bg-gray-400'} cursor-pointer ${dotActive && glow ? 'animate-glow' : ''}`}
                    style={{ boxShadow: dotActive ? (glow ? '0 0 8px 4px #22c55e' : '0 0 2px 1px #22c55e') : '0 0 2px 1px #888', transition: 'box-shadow 0.3s' }}
                    onClick={() => { setDotActive(false); setDotHidden(true); try { localStorage.setItem(DOT_HIDE_KEY, 'true'); } catch {} }}
                    title={lastUpdate ? `${t('bcu.last_update') || 'Actualizado'}: ${formatTime(lastUpdate)}` : t('bcu.no_update') || 'Sin actualización'}
                  />
                  <span className="ml-2 bg-gray-900 text-white text-xs rounded px-2 py-1 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-10 shadow-lg border border-gray-700">
                    {lastUpdate ? `${t('bcu.last_update') || 'Actualizado'}: ${formatTime(lastUpdate)}` : t('bcu.no_update') || 'Sin actualización'}
                  </span>
                </span>
              )}
            </div>
            <div className="flex flex-wrap items-center gap-2">
              {currentRates.slice(0, 4).map((rate) => {
                const display = currencyInfo[rate.currency];
                if (!display) return null;
                return (
                  <div key={rate.currency} className="flex items-center gap-1 bg-blue-600/50 px-2 py-1 rounded text-xs">
                    <Flag code={display.flag} className="w-5 h-4" />
                    <span className="sr-only">{display.flag}</span>
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