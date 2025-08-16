import React, { useState, useEffect, useRef } from 'react';
import { useI18n } from '../contexts/I18nContext';
import { ExclamationTriangleIcon } from '../icons';
import { getTodayLocal, getDaysAgoLocal } from '../utils/dateUtils';
import { ExchangeIcon, ChartIcon, TrendingUpIcon, TodayIcon, WeekIcon, SearchIcon } from '../icons';

const ExchangeSearchForm = ({ onSearch, isLoading }) => {
  const { t } = useI18n();
  
  // Estados del formulario
  const [searchType, setSearchType] = useState('latest');
  const [searchDate, setSearchDate] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [historyLimit, setHistoryLimit] = useState(10);
  const [selectedCurrency, setSelectedCurrency] = useState('ALL');
  const [error, setError] = useState('');

  // Referencias para los elementos del formulario
  const currencyRef = useRef();
  const dateRef = useRef();
  const startDateRef = useRef();
  const endDateRef = useRef();

  // Inicializar fecha de hoy
  useEffect(() => {
    const today = getTodayLocal();
    setSearchDate(today);
    setEndDate(today);
    
    const thirtyDaysAgo = getDaysAgoLocal(30);
    setStartDate(thirtyDaysAgo);
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

    const currency = currencyRef.current?.value;
    const finalCurrency = currency === 'ALL' ? null : currency;

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

  const handleQuickAction = (action) => {
    const currency = currencyRef.current?.value;
    const finalCurrency = currency === 'ALL' ? null : currency;

    switch (action) {
      case 'today': {
        setSearchType('date');
        const today = getTodayLocal();
        setSearchDate(today);
        onSearch({ type: 'date', date: today, currency: finalCurrency });
        break;
      }
      case 'latest':
        setSearchType('latest');
        onSearch({
          type: 'latest',
          currency: finalCurrency,
        });
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
      default:
        break;
    }
  };

  const handleCurrencyChange = (e) => {
    setSelectedCurrency(e.target.value);
  };

  // Función para obtener las monedas soportadas con traducciones y emojis Unicode
  const getSupportedCurrencies = () => [
    { code: 'ALL', name: t('exchange.all_currencies') || 'Todas las monedas', flag: '🌍' },
    { code: 'USD', name: t('exchange.currencies.USD') || 'Dólar estadounidense', flag: '🇺🇸' },
    { code: 'EUR', name: t('exchange.currencies.EUR') || 'Euro', flag: '🇪🇺' },
    { code: 'ARS', name: t('exchange.currencies.ARS') || 'Peso argentino', flag: '🇦🇷' },
    { code: 'BRL', name: t('exchange.currencies.BRL') || 'Real brasileño', flag: '🇧🇷' },
  ];

  return (
  <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center">
        <ExchangeIcon className="w-8 h-8 mr-3 text-blue-600" />
        {t('exchange.search_title') || 'Consultar Cotizaciones'}
      </h2>

      {/* Mensaje de error */}
      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {/* Selector de moneda */}
      <div className="mb-4">
        <label htmlFor="currency" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {t('exchange.currency') || 'Moneda'}
        </label>
        <select
          id="currency"
          ref={currencyRef}
          value={selectedCurrency}
          onChange={handleCurrencyChange}
          className="w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          {getSupportedCurrencies().map(currency => (
            <option key={currency.code} value={currency.code}>
              {currency.code} - {currency.name}
            </option>
          ))}
        </select>
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
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm flex items-center justify-center"
          >
            <ChartIcon className="w-4 h-4 mr-2" />
            {t('exchange.latest_rates') || 'Últimas cotizaciones'}
          </button>
          <button
            type="button"
            onClick={() => handleQuickAction('today')}
            disabled={isLoading}
            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed text-sm flex items-center justify-center"
          >
            <TodayIcon className="w-4 h-4 mr-2" />
            {t('common.today') || 'Hoy'}
          </button>
          <button
            type="button"
            onClick={() => handleQuickAction('week')}
            disabled={isLoading}
            className="px-4 py-2 bg-blue-400 text-white rounded-md hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-sm flex items-center justify-center"
          >
            <WeekIcon className="w-4 h-4 mr-2" />
            {t('common.last_week') || 'Última semana'}
          </button>
        </div>
      </div>

      {/* Selector de tipo de búsqueda */}
      <div className="mb-6">
  <h3 className="text-sm font-medium text-gray-800 dark:text-gray-200 mb-3">
          {t('exchange.search_type') || 'Tipo de consulta'}
        </h3>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-2">
          <button
            type="button"
            onClick={() => setSearchType('latest')}
            className={`px-3 py-2 rounded-md text-sm font-medium ${
              searchType === 'latest'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-800 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-100 dark:hover:bg-gray-600'
            }`}
          >
            {t('exchange.latest') || 'Últimas'}
          </button>
          <button
            type="button"
            onClick={() => setSearchType('date')}
            className={`px-3 py-2 rounded-md text-sm font-medium ${
              searchType === 'date'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-800 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-100 dark:hover:bg-gray-600'
            }`}
          >
            {t('exchange.by_date') || 'Por fecha'}
          </button>
          <button
            type="button"
            onClick={() => setSearchType('range')}
            className={`px-3 py-2 rounded-md text-sm font-medium ${
              searchType === 'range'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-800 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-100 dark:hover:bg-gray-600'
            }`}
          >
            {t('exchange.by_range') || 'Por rango'}
          </button>
          <button
            type="button"
            onClick={() => setSearchType('history')}
            className={`px-3 py-2 rounded-md text-sm font-medium ${
              searchType === 'history'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-800 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-100 dark:hover:bg-gray-600'
            }`}
          >
            {t('exchange.history') || 'Historial'}
          </button>
        </div>
      </div>

      {/* Formulario específico según el tipo */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {searchType === 'latest' && (
          <div className="p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-600">
              {t('exchange.latest_description') || 'Se mostrarán las últimas cotizaciones disponibles.'}
              {selectedCurrency && selectedCurrency !== 'ALL' && (
                <span className="font-medium"> {t('common.filtered_by') || 'Filtrado por'}: {selectedCurrency}</span>
              )}
            </p>
          </div>
        )}

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
          <>
            <div className="mb-4">
              <label htmlFor="startDate" className="block text-sm font-medium text-gray-700 mb-1">
                {t('exchange.start_date') || 'Fecha de inicio'}
              </label>
              <input
                type="date"
                id="startDate"
                ref={startDateRef}
                className="w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                max={getTodayLocal()}
              />
            </div>
            <div className="mb-4">
              <label htmlFor="endDate" className="block text-sm font-medium text-gray-700 mb-1">
                {t('exchange.end_date') || 'Fecha de fin'}
              </label>
              <input
                type="date"
                id="endDate"
                ref={endDateRef}
                className="w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                max={getTodayLocal()}
              />
            </div>
          </>
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
          disabled={isLoading || (searchType === 'history' && !selectedCurrency)}
          className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
        >
          <SearchIcon className="w-5 h-5 mr-2" />
          {isLoading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {t('common.searching') || 'Consultando...'}
            </span>
          ) : (
            `🔍 ${t('common.search') || 'Consultar'}`
          )}
        </button>
      </form>

      {/* Información adicional */}
      <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <h4 className="text-sm font-medium text-yellow-800 mb-2">
          ℹ️ {t('exchange.info_title') || 'Información sobre cotizaciones'}
        </h4>
        <ul className="text-xs text-yellow-700 space-y-1">
          <li>• {t('exchange.info_source') || 'Datos obtenidos del Banco Central del Uruguay (BCU)'}</li>
          <li>• {t('exchange.info_frequency') || 'Las cotizaciones se actualizan en días hábiles'}</li>
          <li>• {t('exchange.info_rates') || 'Se muestran tasas de compra, venta y promedio cuando están disponibles'}</li>
        </ul>
      </div>
    </div>
  );
};

export default ExchangeSearchForm; 