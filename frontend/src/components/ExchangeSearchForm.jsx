import React, { useState, useEffect } from 'react';
import { useI18n } from '../contexts/I18nContext';
import { ExclamationTriangleIcon } from '../icons';
import { OpenMojiIcon } from '../icons/openmoji/index.jsx';
import { Flag } from '../icons/flags';
import { getTodayLocal, getDaysAgoLocal } from '../utils/dateUtils';
// Removed decorative icons to simplify UI per request

const ExchangeSearchForm = ({ onSearch, isLoading }) => {
  const { t } = useI18n();
  
  // Estados del formulario
  const [searchType, setSearchType] = useState('latest');
  const [searchDate, setSearchDate] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [historyLimit, setHistoryLimit] = useState(10);
  const [selectedCurrency, setSelectedCurrency] = useState('ALL'); // 'ALL' o código singular
  const [error, setError] = useState('');
  const [latestDataDate, setLatestDataDate] = useState(null); // fecha retornada por 'latest'
  const [latestHintNeeded, setLatestHintNeeded] = useState(false);

  // Referencias eliminadas para currency (usamos toggles). Conservamos lógica de fechas por estado.
  const dateRef = React.useRef();
  const startDateRef = React.useRef();
  const endDateRef = React.useRef();

  // Inicializar fecha de hoy
  // Efecto de auto-inicialización: se ejecuta sólo una vez al montar.
  // Antes dependía de `onSearch` y como el contenedor recreaba la función en cada render
  // (sin useCallback), provocaba re-ejecuciones infinitas y múltiples toasts.
  // Con arreglo vacío garantizamos una sola consulta inicial.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    const today = getTodayLocal();
    setSearchDate(today);
    setEndDate(today);
    const thirtyDaysAgo = getDaysAgoLocal(30);
    setStartDate(thirtyDaysAgo);
    onSearch?.({ type: 'latest', currency: null });
  }, []);

  const validateDates = (start, end) => {
    const today = getTodayLocal();
    
    if (start > today || end > today) {
      setError(t('exchange.future_date') || 'No se pueden seleccionar fechas futuras');
      return false;
    }
    
    if (start > end) {
      setError(t('exchange.invalid_date_range') || 'La fecha de inicio no puede ser mayor que la fecha de fin');
      return false;
    }
    
    return true;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    const finalCurrency = selectedCurrency === 'ALL' ? null : selectedCurrency;

    const searchParams = {
      type: searchType,
      currency: finalCurrency,
    };

    switch (searchType) {
      case 'latest':
        // No additional params needed
        break;
      case 'date':
        const date = dateRef.current?.value;
        if (!date) {
          setError(t('ui.date_required') || 'La fecha es requerida');
          return;
        }
        if (!validateDates(date, date)) {
          return;
        }
        searchParams.date = date;
        break;
      case 'range':
        const start = startDateRef.current?.value;
        const end = endDateRef.current?.value;
        if (!start || !end) {
          setError(t('ui.start_date_required') || 'Las fechas son requeridas');
          return;
        }
        if (!validateDates(start, end)) {
          return;
        }
        searchParams.startDate = start;
        searchParams.endDate = end;
        break;
      case 'history':
        if (!finalCurrency) {
          setError(t('exchange.select_currency_for_history') || 'Selecciona una moneda para ver el historial');
          return;
        }
        searchParams.limit = historyLimit;
        break;
      default:
        break;
    }

    onSearch(searchParams);
  };

  const isWeekend = (dateStr) => {
    const d = new Date(dateStr);
    const day = d.getDay();
    return day === 0 || day === 6;
  };

  const handleQuickAction = (action) => {
    const finalCurrency = selectedCurrency === 'ALL' ? null : selectedCurrency;

    switch (action) {
      case 'latest':
        setSearchType('latest');
        // Ejecuta búsqueda 'latest'; se espera que el contenedor procese y devuelva datos.
        onSearch({ type: 'latest', currency: finalCurrency })
          ?.then((resp) => {
            const today = getTodayLocal();
            const latestDate = resp?.meta?.latest_date || resp?.data?.[0]?.date || resp?.data?.[0]?.fecha;
            if (latestDate) {
              setLatestDataDate(latestDate);
              setLatestHintNeeded(latestDate !== today && !searchDate && (isWeekend(today) || today > latestDate));
            }
          })
          .catch(() => {});
        break;
      case 'week':
        const weekAgo = getDaysAgoLocal(7);
        const todayWeek = getTodayLocal();
        setSearchType('range');
        setStartDate(weekAgo);
        setEndDate(todayWeek);
        onSearch({
          type: 'range',
          startDate: weekAgo,
          endDate: todayWeek,
          currency: finalCurrency,
        });
        break;
      case 'month': {
        const monthAgo = getDaysAgoLocal(30);
        const todayMonth = getTodayLocal();
        setSearchType('range');
        setStartDate(monthAgo);
        setEndDate(todayMonth);
        onSearch({ type: 'range', startDate: monthAgo, endDate: todayMonth, currency: finalCurrency });
        break;
      }
      default:
        break;
    }
  };

  const performLatestForCurrency = (currencyCodeOrAll) => {
    const finalCurrency = currencyCodeOrAll === 'ALL' ? null : currencyCodeOrAll;
    // For UX we reset to latest each time a moneda se selecciona automáticamente
    setSearchType('latest');
    onSearch?.({ type: 'latest', currency: finalCurrency });
  };

  const toggleCurrency = (code) => {
    setSelectedCurrency(prev => {
      const next = prev === code ? 'ALL' : code;
      performLatestForCurrency(next);
      return next;
    });
  };
  const setAllCurrencies = () => {
    setSelectedCurrency('ALL');
    performLatestForCurrency('ALL');
  };

  const currencyButtons = [
    { code: 'USD', label: t('exchange.currencies.USD') || 'USD' },
    { code: 'EUR', label: t('exchange.currencies.EUR') || 'EUR' },
    { code: 'ARS', label: t('exchange.currencies.ARS') || 'ARS' },
    { code: 'BRL', label: t('exchange.currencies.BRL') || 'BRL' },
  ];


  return (
  <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
        <OpenMojiIcon name="chartUp" size={32} className="mr-3" />
        {t('exchange.search_title') || 'Consultar Cotizaciones'}
      </h2>

      {/* Mensaje de error */}
      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {/* Filtro de monedas: botón mundo (ALL) + toggles de banderas (single-select por ahora) */}
      <div className="mb-4">
        <span className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {t('exchange.currency') || 'Moneda'}
        </span>
  <div className="flex items-center gap-3 overflow-x-auto whitespace-nowrap py-1" style={{minHeight: '40px'}}>
          <button
            type="button"
            onClick={setAllCurrencies}
            aria-pressed={selectedCurrency === 'ALL'}
            aria-label={(t('exchange.all_currencies') || 'Todas las monedas') + (selectedCurrency === 'ALL' ? ' (activo)' : '')}
            className={`px-2 py-1 rounded-md text-sm flex items-center gap-1 border transition-colors ${selectedCurrency === 'ALL' ? 'bg-blue-600 text-white border-blue-600' : 'bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 border-gray-300 dark:border-gray-600 hover:bg-gray-300 dark:hover:bg-gray-600'}`}
          >
            <span role="img" aria-hidden="true">🌍</span>
            {t('exchange.all_currencies') || 'Todas'}
          </button>
          {currencyButtons.map(c => (
            <button
              key={c.code}
              type="button"
              onClick={() => toggleCurrency(c.code)}
              aria-pressed={selectedCurrency === c.code}
              aria-label={`${c.label} ${selectedCurrency === c.code ? '(activo)' : ''}`}
              className={`px-2 py-1 rounded-md text-sm flex items-center gap-1 border transition-colors ${selectedCurrency === c.code ? 'bg-blue-600 text-white border-blue-600' : 'bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 border-gray-300 dark:border-gray-600 hover:bg-gray-300 dark:hover:bg-gray-600'}`}
            style={{display: 'flex', alignItems: 'center', gap: '4px', minWidth: '60px', justifyContent: 'center'}}>
              <Flag code={c.code} className="flag-icon" style={{verticalAlign: 'middle'}} />
              <span style={{verticalAlign: 'middle'}}>{c.code}</span>
            </button>
          ))}
        </div>
      </div>

  {/* Botones de acción rápida */}
      <div className="mb-6">
        <h3 className="text-sm font-medium text-gray-800 dark:text-gray-200 mb-3">
          {t('common.quick_actions') || 'Acciones rápidas'}
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
          <button
            type="button"
            onClick={() => handleQuickAction('latest')}
            disabled={isLoading}
    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium transition-colors"
          >
            {t('exchange.latest_data') || 'Últimos datos'}
          </button>
          <button
            type="button"
            onClick={() => handleQuickAction('week')}
            disabled={isLoading}
    className="px-4 py-2 bg-blue-400 text-white rounded-md hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium transition-colors"
          >
            {t('common.last_week') || 'Última semana'}
          </button>
          <button
            type="button"
            onClick={() => handleQuickAction('month')}
            disabled={isLoading}
            className="px-4 py-2 bg-blue-300 text-white rounded-md hover:bg-blue-400 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium transition-colors"
          >
            {t('common.last_month') || 'Último mes'}
          </button>
        </div>
        {latestHintNeeded && (
          <div className="mt-3 text-xs text-yellow-600 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-900/30 border border-yellow-200 dark:border-yellow-800 rounded-md px-3 py-2">
            {t('exchange.latest_hint') || 'No hay datos publicados para hoy todavía; se muestran los últimos disponibles.'}
          </div>
        )}
      </div>

      {/* Selector de tipo de búsqueda (mismo estilo que acciones rápidas) */}
      <div className="mb-6">
        <h3 className="text-sm font-medium text-gray-800 dark:text-gray-200 mb-3">
          {t('exchange.search_type') || 'Tipo de consulta'}
        </h3>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-2">
          {[
            { key: 'latest', label: t('exchange.latest') || 'Últimas' },
            { key: 'date', label: t('exchange.by_date') || 'Por fecha' },
            { key: 'range', label: t('exchange.by_range') || 'Por rango' },
            { key: 'history', label: t('exchange.history') || 'Historial' }
          ].map(btn => (
            <button
              key={btn.key}
              type="button"
              onClick={() => setSearchType(btn.key)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                searchType === btn.key
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-800 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-100 dark:hover:bg-gray-600'
              }`}
            >
              {btn.label}
            </button>
          ))}
        </div>
      </div>

      {/* Formulario específico según el tipo */}
      <form onSubmit={handleSubmit} className="space-y-4">
  {/* Descripción para 'latest' removida por redundancia */}

        {searchType === 'date' && (
          <div className="mb-4">
            <label htmlFor="date" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {t('exchange.date') || 'Fecha'}
            </label>
            <input
              type="date"
              id="date"
              ref={dateRef}
              className="w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              value={searchDate}
              onChange={(e) => setSearchDate(e.target.value)}
              max={getTodayLocal()}
            />
          </div>
        )}

        {searchType === 'range' && (
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {t('exchange.date_range') || 'Rango de fechas'}
            </label>
            <div className="flex items-center gap-2">
              <input
                type="date"
                id="startDate"
                aria-label={t('exchange.start_date') || 'Fecha de inicio'}
                ref={startDateRef}
                className="flex-1 rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                max={getTodayLocal()}
              />
              <span className="text-gray-500 dark:text-gray-400">→</span>
              <input
                type="date"
                id="endDate"
                aria-label={t('exchange.end_date') || 'Fecha de fin'}
                ref={endDateRef}
                className="flex-1 rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                max={getTodayLocal()}
              />
            </div>
          </div>
        )}

        {searchType === 'history' && (
          <div className="mb-4">
            <label
              htmlFor="limit"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
            >
              {t('exchange.history_limit') || 'Cantidad de registros'}
            </label>
            <input
              type="number"
              id="limit"
              className="w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 shadow-sm focus:border-blue-500 focus:ring-blue-500 placeholder-gray-400 dark:placeholder-gray-500"
              value={historyLimit}
              onChange={(e) => setHistoryLimit(e.target.value)}
              min="1"
              max="365"
            />
          </div>
        )}

        {/* Botón de búsqueda */}
        <button
          type="submit"
          disabled={isLoading || (searchType === 'history' && (selectedCurrency === 'ALL'))}
          className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium flex items-center justify-center"
        >
          {isLoading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {t('common.searching') || 'Consultando...'}
            </span>
          ) : (
            t('common.search') || 'Consultar'
          )}
        </button>
      </form>

  {/* Panel informativo removido por simplificación de interfaz */}
    </div>
  );
};

export default ExchangeSearchForm; 