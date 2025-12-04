import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useI18n } from '../../shared/contexts/I18nContext';
import { ExclamationTriangleIcon } from '../../shared/icons';
import { OpenMojiIcon } from '../../shared/icons/openmoji/index.jsx';
import { Flag } from '../../shared/icons/flags';
import { getTodayLocal, getDaysAgoLocal } from '../../shared/utils/dateUtils';
import Button from '../../shared/components/ui/Button';

// Rate limiting: máximo 10 requests por minuto
const MAX_REQUESTS_PER_MINUTE = 10;
const RATE_LIMIT_WINDOW = 60000; // 1 minuto en ms
const DEBOUNCE_DELAY = 500; // 500ms de debounce

// Removed decorative icons to simplify UI per request

const ExchangeSearchForm = ({ onSearch, isLoading }) => {
  const { t } = useI18n();
  
  // Rate limiting state
  const requestTimestamps = useRef([]);
  const debounceTimer = useRef(null);
  
  // Estados del formulario
  const [searchType, setSearchType] = useState('latest');
  const [searchDate, setSearchDate] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [historyLimit, setHistoryLimit] = useState(10);
  const [selectedCurrencies, setSelectedCurrencies] = useState(['USD', 'EUR', 'ARS', 'BRL']); // Array para selección múltiple
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
    
    if (!canMakeRequest()) return;
    
    // Para el backend: si están todas seleccionadas = null, si no = array o string único
    const finalCurrency = selectedCurrencies.length === 4 
      ? null // Todas las monedas
      : selectedCurrencies.length === 1 
        ? selectedCurrencies[0] // Una sola moneda (string)
        : selectedCurrencies; // Múltiples monedas (array - se convierte a CSV en el servicio)

    const searchParams = {
      type: searchType,
      currency: finalCurrency,
    };

    switch (searchType) {
      case 'latest':
        // Latest soporta múltiples monedas
        break;
      case 'date': {
        // Por fecha: ahora soporta múltiples monedas
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
      }
      case 'range': {
        // Por rango: ahora soporta múltiples monedas
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
      }
      case 'history': {
        // Historial: solo soporta UNA moneda específica
        if (selectedCurrencies.length !== 1) {
          setError(t('exchange.select_single_currency_for_history') || 'Selecciona solo una moneda para ver el historial');
          return;
        }
        searchParams.limit = historyLimit;
        break;
      }
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
    if (!canMakeRequest()) return;
    
    const finalCurrency = selectedCurrencies.length === 4 
      ? null 
      : selectedCurrencies.length === 1 
        ? selectedCurrencies[0] 
        : selectedCurrencies;

    switch (action) {
      case 'latest': {
        setSearchType('latest');
        // Latest soporta múltiples monedas
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
      }
      case 'week': {
        // Por rango: ahora soporta múltiples monedas
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
      }
      case 'month': {
        // Por rango: ahora soporta múltiples monedas
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

  // Rate limiting check
  const canMakeRequest = useCallback(() => {
    const now = Date.now();
    // Filtrar timestamps dentro de la ventana de tiempo
    requestTimestamps.current = requestTimestamps.current.filter(
      timestamp => now - timestamp < RATE_LIMIT_WINDOW
    );
    
    if (requestTimestamps.current.length >= MAX_REQUESTS_PER_MINUTE) {
      setError(`⏱️ Demasiadas búsquedas. Por favor espera un momento (máximo ${MAX_REQUESTS_PER_MINUTE} búsquedas por minuto).`);
      return false;
    }
    
    requestTimestamps.current.push(now);
    return true;
  }, []);

  // Auto-search con debounce cuando cambian las monedas
  const triggerAutoSearch = useCallback(() => {
    // Limpiar timer anterior
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }
    
    // Crear nuevo timer con debounce
    debounceTimer.current = setTimeout(() => {
      if (!canMakeRequest()) return;
      
      const finalCurrency = selectedCurrencies.length === 4 
        ? null 
        : selectedCurrencies.length === 1 
          ? selectedCurrencies[0] 
          : selectedCurrencies;
      
      // Buscar con el tipo actual
      if (searchType === 'latest') {
        onSearch?.({ type: 'latest', currency: finalCurrency });
      }
    }, DEBOUNCE_DELAY);
  }, [selectedCurrencies, searchType, canMakeRequest, onSearch]);

  // Cleanup del debounce timer
  useEffect(() => {
    return () => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
      }
    };
  }, []);

  const performLatestForCurrency = (currencyCodeOrAll) => {
    const finalCurrency = currencyCodeOrAll === 'ALL' ? null : currencyCodeOrAll;
    // For UX we reset to latest each time a moneda se selecciona automáticamente
    setSearchType('latest');
    onSearch?.({ type: 'latest', currency: finalCurrency });
  };

  const toggleCurrency = (code) => {
    setSelectedCurrencies(prev => {
      const isSelected = prev.includes(code);
      const next = isSelected 
        ? prev.filter(c => c !== code) // Deseleccionar
        : [...prev, code]; // Agregar
      
      // Si quedó vacío, no hacer nada (mantener al menos una)
      if (next.length === 0) return prev;
      
      return next;
    });
    
    // No llamar triggerAutoSearch aquí - se manejará con useEffect
  };

  const selectAllCurrencies = () => {
    setSelectedCurrencies(['USD', 'EUR', 'ARS', 'BRL']);
    
    // No llamar triggerAutoSearch aquí - se manejará con useEffect
  };

  // Auto-search cuando cambian las monedas seleccionadas
  useEffect(() => {
    // Solo disparar si estamos en modo "latest" y hay monedas seleccionadas
    if (searchType === 'latest' && selectedCurrencies.length > 0) {
      triggerAutoSearch();
    }
  }, [selectedCurrencies, searchType, triggerAutoSearch]);

  const currencyButtons = [
    { code: 'USD', label: t('exchange.currencies.USD') || 'USD' },
    { code: 'EUR', label: t('exchange.currencies.EUR') || 'EUR' },
    { code: 'ARS', label: t('exchange.currencies.ARS') || 'ARS' },
    { code: 'BRL', label: t('exchange.currencies.BRL') || 'BRL' },
  ];


  return (
  <div className="bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100 mb-6 flex items-center">
        <OpenMojiIcon name="chartUp" size={32} className="mr-3" />
        {t('exchange.search_title') || 'Consultar Cotizaciones'}
      </h2>

      {/* Mensaje de error */}
      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {/* Filtro de monedas: selección múltiple */}
      <div className="mb-4">
        <span className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-3">
          {t('exchange.currency') || 'Moneda'} <span className="text-xs text-neutral-500 dark:text-neutral-400">({t('exchange.select_multiple') || 'Selección múltiple'})</span>
        </span>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-2 md:gap-3">
          {currencyButtons.map(c => (
            <button
              key={c.code}
              type="button"
              onClick={() => toggleCurrency(c.code)}
              aria-pressed={selectedCurrencies.includes(c.code)}
              aria-label={`${c.label} ${selectedCurrencies.includes(c.code) ? '(seleccionado)' : ''}`}
              className={`px-3 md:px-4 py-2 rounded-lg text-sm md:text-base flex items-center gap-2 border transition-colors font-medium w-full ${
                selectedCurrencies.includes(c.code) 
                  ? 'bg-primary-600 text-white border-primary-600' 
                  : 'bg-neutral-50 dark:bg-neutral-800 text-neutral-800 dark:text-neutral-200 border-neutral-200 dark:border-neutral-700 hover:bg-neutral-100 dark:hover:bg-neutral-700'
              }`}
              style={{justifyContent: 'center'}}>
              <Flag code={c.code} className="flag-icon" />
              {c.code}
            </button>
          ))}
        </div>
      </div>

  {/* Botones de acción rápida */}
      <div className="mb-6">
        <h3 className="text-sm font-medium text-neutral-800 dark:text-neutral-200 mb-3">
          {t('common.quick_actions') || 'Acciones rápidas'}
        </h3>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={selectAllCurrencies}
            disabled={isLoading}
            className={`text-xs px-3 py-1 rounded-full transition-colors duration-200 border whitespace-nowrap disabled:opacity-50 ${
              selectedCurrencies.length === 4
                ? 'bg-blue-600 hover:bg-blue-700 text-white border-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 dark:border-blue-600'
                : 'bg-neutral-100 hover:bg-neutral-200 dark:bg-neutral-700 dark:hover:bg-neutral-600 text-neutral-700 dark:text-neutral-200 border-neutral-300 hover:border-neutral-400 dark:border-neutral-600 dark:hover:border-neutral-500'
            }`}
            title={t('exchange.select_all_currencies') || 'Seleccionar todas las monedas'}
          >
            🌍 {t('exchange.all_currencies') || 'Todas'}
          </button>
          <button
            type="button"
            onClick={() => handleQuickAction('latest')}
            disabled={isLoading}
            className="text-xs px-3 py-1 bg-neutral-100 hover:bg-neutral-200 dark:bg-neutral-700 dark:hover:bg-neutral-600 rounded-full transition-colors duration-200 border border-neutral-300 hover:border-neutral-400 dark:border-neutral-600 dark:hover:border-neutral-500 dark:text-neutral-100 whitespace-nowrap disabled:opacity-50"
          >
            {t('exchange.latest_data') || 'Últimos datos'}
          </button>
          <button
            type="button"
            onClick={() => handleQuickAction('week')}
            disabled={isLoading}
            className="text-xs px-3 py-1 bg-neutral-100 hover:bg-neutral-200 dark:bg-neutral-700 dark:hover:bg-neutral-600 rounded-full transition-colors duration-200 border border-neutral-300 hover:border-neutral-400 dark:border-neutral-600 dark:hover:border-neutral-500 dark:text-neutral-100 whitespace-nowrap disabled:opacity-50"
          >
            {t('common.last_week') || 'Última semana'}
          </button>
          <button
            type="button"
            onClick={() => handleQuickAction('month')}
            disabled={isLoading}
            className="text-xs px-3 py-1 bg-neutral-100 hover:bg-neutral-200 dark:bg-neutral-700 dark:hover:bg-neutral-600 rounded-full transition-colors duration-200 border border-neutral-300 hover:border-neutral-400 dark:border-neutral-600 dark:hover:border-neutral-500 dark:text-neutral-100 whitespace-nowrap disabled:opacity-50"
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

      {/* Selector de tipo de búsqueda (radio buttons en fila como es común) */}
      <div className="mb-6">
        <h3 className="text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-3">
          {t('exchange.search_type') || 'Tipo de consulta'}
        </h3>
        <div className="flex flex-wrap gap-4">
          <label className="flex items-center cursor-pointer">
            <input
              type="radio"
              value="latest"
              checked={searchType === 'latest'}
              onChange={(e) => setSearchType(e.target.value)}
              className="mr-2 text-primary-600 focus:ring-primary-600"
            />
            <span className="text-sm font-medium text-neutral-700 dark:text-neutral-300">{t('exchange.latest') || 'Últimas'}</span>
          </label>
          <label className="flex items-center cursor-pointer">
            <input
              type="radio"
              value="date"
              checked={searchType === 'date'}
              onChange={(e) => setSearchType(e.target.value)}
              className="mr-2 text-primary-600 focus:ring-primary-600"
            />
            <span className="text-sm font-medium text-neutral-700 dark:text-neutral-300">{t('exchange.by_date') || 'Por fecha'}</span>
          </label>
          <label className="flex items-center cursor-pointer">
            <input
              type="radio"
              value="range"
              checked={searchType === 'range'}
              onChange={(e) => setSearchType(e.target.value)}
              className="mr-2 text-primary-600 focus:ring-primary-600"
            />
            <span className="text-sm font-medium text-neutral-700 dark:text-neutral-300">{t('exchange.by_range') || 'Por rango'}</span>
          </label>
          <label className="flex items-center cursor-pointer">
            <input
              type="radio"
              value="history"
              checked={searchType === 'history'}
              onChange={(e) => setSearchType(e.target.value)}
              className="mr-2 text-primary-600 focus:ring-primary-600"
            />
            <span className="text-sm font-medium text-neutral-700 dark:text-neutral-300">{t('exchange.history') || 'Historial'}</span>
          </label>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">

        {searchType === 'date' && (
          <div className="mb-4">
            <label htmlFor="date" className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
              {t('exchange.date') || 'Fecha'}
            </label>
            <input
              type="date"
              id="date"
              ref={dateRef}
              className="w-full rounded-md border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-900 text-neutral-900 dark:text-neutral-100 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              value={searchDate}
              onChange={(e) => setSearchDate(e.target.value)}
              max={getTodayLocal()}
            />
          </div>
        )}

        {searchType === 'range' && (
          <div className="mb-4">
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
              {t('exchange.date_range') || 'Rango de fechas'}
            </label>
            <div className="flex items-center gap-2">
              <input
                type="date"
                id="startDate"
                aria-label={t('exchange.start_date') || 'Fecha de inicio'}
                ref={startDateRef}
                className="flex-1 rounded-md border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-900 text-neutral-900 dark:text-neutral-100 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                max={getTodayLocal()}
              />
              <span className="text-neutral-500 dark:text-neutral-400">→</span>
              <input
                type="date"
                id="endDate"
                aria-label={t('exchange.end_date') || 'Fecha de fin'}
                ref={endDateRef}
                className="flex-1 rounded-md border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-900 text-neutral-900 dark:text-neutral-100 shadow-sm focus:border-blue-500 focus:ring-blue-500"
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
              className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1"
            >
              {t('exchange.history_limit') || 'Cantidad de registros'}
            </label>
            <input
              type="number"
              id="limit"
              className="w-full rounded-md border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-900 text-neutral-900 dark:text-neutral-100 shadow-sm focus:border-blue-500 focus:ring-blue-500 placeholder-gray-400 dark:placeholder-gray-500"
              value={historyLimit}
              onChange={(e) => setHistoryLimit(e.target.value)}
              min="1"
              max="365"
            />
          </div>
        )}

        {/* Botón de búsqueda */}
        <Button
          type="submit"
          variant="primary"
          fullWidth={true}
          disabled={isLoading || (searchType === 'history' && (selectedCurrencies.length === 4))}
          loading={isLoading}
          className="py-3"
        >
          {t('common.search') || 'Consultar'}
        </Button>
      </form>

  {/* Panel informativo removido por simplificación de interfaz */}
    </div>
  );
};

export default ExchangeSearchForm; 
