import React from 'react';
import { getCurrencyInfo, formatExchangeRate } from '../services/exchangeService';
import { useI18n } from '../contexts/I18nContext';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { format, parseISO } from 'date-fns';
import { LegacyFlagIcon as FlagIcon, ExchangeIcon, ChartIcon, SummaryIcon } from '../icons';

const ExchangeResultsDisplay = ({ results, searchType, isLoading, error }) => {
  const { t, translateBackendMessage } = useI18n();

  // Función para formatear fecha para el gráfico
  const formatDateForChart = (dateString) => {
    try {
      return format(parseISO(dateString), 'dd/MM/yyyy');
    } catch (error) {
      return dateString;
    }
  };

  // Función para preparar datos para gráficos
  const prepareChartData = (data) => {
    const sortedData = [...data].sort((a, b) => new Date(a.date) - new Date(b.date));
    return sortedData.map(item => ({
      date: formatDateForChart(item.date),
      fullDate: item.date,
      currency: item.currency,
      buy_rate: parseFloat(item.buy_rate),
      sell_rate: parseFloat(item.sell_rate),
      average_rate: item.average_rate ? parseFloat(item.average_rate) : null,
      ...getCurrencyInfo(item.currency)
    }));
  };

  // Función para calcular dominio ajustado del gráfico
  const calculateYAxisDomain = (data) => {
    const allRates = [];
    data.forEach(item => {
      allRates.push(item.buy_rate);
      allRates.push(item.sell_rate);
      if (item.average_rate) allRates.push(item.average_rate);
    });

    const minRate = Math.min(...allRates);
    const maxRate = Math.max(...allRates);
    const range = maxRate - minRate;
    
    // Agregar un 5% de padding arriba y abajo para mejor visualización
    const padding = range * 0.05;
    const adjustedMin = Math.max(0, minRate - padding);
    const adjustedMax = maxRate + padding;
    
    return [adjustedMin.toFixed(4), adjustedMax.toFixed(4)];
  };

  // Función para agrupar datos por moneda
  const groupByCurrency = (data) => {
    const grouped = {};
    data.forEach(item => {
      if (!grouped[item.currency]) {
        grouped[item.currency] = [];
      }
      grouped[item.currency].push(item);
    });
    return grouped;
  };

  // Mostrar loading
  if (isLoading) {
    return (
	<div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-md p-6">
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <svg className="animate-spin -ml-1 mr-3 h-8 w-8 text-blue-600 mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p className="text-gray-600 dark:text-gray-300">{t('common.loading') || 'Cargando cotizaciones...'}</p>
          </div>
        </div>
      </div>
    );
  }

  // Mostrar error
  if (error) {
    return (
  <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-md p-6">
    <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <span className="text-red-400 text-xl">⚠️</span>
            </div>
            <div className="ml-3">
      <h3 className="text-sm font-medium text-red-800 dark:text-red-300">
                {t('common.error') || 'Error'}
              </h3>
      <p className="text-sm text-red-700 dark:text-red-400">{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // No hay resultados
  if (!results || !results.success || !results.data) {
    return (
  <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-md p-6">
        <div className="text-center py-12">
          <span className="text-6xl mb-4 block">💱</span>
 	  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
            {t('exchange.no_results') || 'Sin resultados'}
          </h3>
 	  <p className="text-gray-600 dark:text-gray-300">
            {t('exchange.no_results_description') || 'Realiza una consulta para ver las cotizaciones.'}
          </p>
        </div>
      </div>
    );
  }

  const data = Array.isArray(results.data) ? results.data : [results.data];
  
  // Filtrar solo las monedas soportadas
  const filteredData = data.filter(rate => {
    const currencyInfo = getCurrencyInfo(rate.currency);
    return currencyInfo !== undefined;
  });

  // Si no hay datos después del filtrado, mostrar mensaje
  if (filteredData.length === 0 && data.length > 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="text-center py-12">
          <span className="text-6xl mb-4 block">💱</span>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {t('exchange.no_supported_currencies') || 'No hay monedas soportadas'}
          </h3>
          <p className="text-gray-600 mb-4">
            {t('exchange.no_supported_currencies_description') || 'Los datos contienen monedas que no están en nuestra lista de monedas soportadas.'}
          </p>
          <p className="text-sm text-gray-500">
            {t('exchange.supported_currencies_list') || 'Monedas soportadas'}: USD, EUR, ARS, BRL
          </p>
        </div>
      </div>
    );
  }

  // Componente para mostrar una tarjeta de moneda
  const CurrencyCard = ({ rate }) => {
    const currencyInfo = getCurrencyInfo(rate.currency);
    
    return (
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center">
            <span className="text-2xl mr-2">{currencyInfo?.flag || '💱'}</span>
            <div>
              <h3 className="font-bold text-gray-900">{rate.currency}</h3>
              <p className="text-xs text-gray-600">{currencyInfo?.name || rate.currency}</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-xs text-gray-500">{rate.date}</p>
            {rate.arbitrage && (
              <p className="text-xs text-blue-600 font-medium">{rate.arbitrage}</p>
            )}
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-3">
          <div className="text-center">
            <p className="text-xs text-gray-600 mb-1">{t('exchange.buy_rate') || 'Compra'}</p>
            <p className="text-lg font-bold text-green-600">
              ${formatExchangeRate(rate.buy_rate)}
            </p>
          </div>
          <div className="text-center">
            <p className="text-xs text-gray-600 mb-1">{t('exchange.sell_rate') || 'Venta'}</p>
            <p className="text-lg font-bold text-red-600">
              ${formatExchangeRate(rate.sell_rate)}
            </p>
          </div>
        </div>
        
        {rate.average_rate && (
          <div className="mt-3 pt-3 border-t border-blue-200">
            <div className="text-center">
              <p className="text-xs text-gray-600 mb-1">{t('exchange.average_rate') || 'Promedio'}</p>
              <p className="text-sm font-semibold text-blue-700">
                ${formatExchangeRate(rate.average_rate)}
              </p>
            </div>
          </div>
        )}
      </div>
    );
  };

  // Componente para tabla de historial optimizada
  const HistoryTable = ({ rates }) => (
    <>
      {/* Vista de tabla para pantallas medianas y grandes */}
      <div className="hidden md:block overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700">
        <table className="w-full divide-y divide-gray-200 dark:divide-gray-700 text-sm">
          <thead className="bg-gray-50 dark:bg-gray-700/60">
            <tr>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-600 dark:text-gray-200 uppercase tracking-wider w-24">
                {t('common.date') || 'Fecha'}
              </th>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-600 dark:text-gray-200 uppercase tracking-wider w-20">
                {t('exchange.currency') || 'Moneda'}
              </th>
              <th className="px-3 py-2 text-center text-xs font-medium text-gray-600 dark:text-gray-200 uppercase tracking-wider w-20">
                {t('exchange.buy_rate') || 'Compra'}
              </th>
              <th className="px-3 py-2 text-center text-xs font-medium text-gray-600 dark:text-gray-200 uppercase tracking-wider w-20">
                {t('exchange.sell_rate') || 'Venta'}
              </th>
              <th className="px-3 py-2 text-center text-xs font-medium text-gray-600 dark:text-gray-200 uppercase tracking-wider w-20">
                {t('exchange.average_rate') || 'Promedio'}
              </th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {rates.map((rate, index) => {
              const currencyInfo = getCurrencyInfo(rate.currency);
              return (
                <tr key={`${rate.date}-${rate.currency}-${index}`} className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                  <td className="px-3 py-3 text-xs text-gray-900 dark:text-gray-100 font-mono">
                    <div className="whitespace-nowrap">
                      {rate.date}
                    </div>
                  </td>
                  <td className="px-3 py-3">
                    <div className="flex items-center space-x-2">
                      <span className="text-lg">{currencyInfo?.flag || '💱'}</span>
                      <div className="flex flex-col">
                        <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">{rate.currency}</span>
                        <span className="text-xs text-gray-500 dark:text-gray-400 truncate" style={{maxWidth: '80px'}}>
                          {currencyInfo?.name}
                        </span>
                      </div>
                    </div>
                  </td>
                  <td className="px-3 py-3 text-center">
                    <div className="text-sm font-semibold text-green-600">
                      ${formatExchangeRate(rate.buy_rate)}
                    </div>
                  </td>
                  <td className="px-3 py-3 text-center">
                    <div className="text-sm font-semibold text-red-600">
                      ${formatExchangeRate(rate.sell_rate)}
                    </div>
                  </td>
                  <td className="px-3 py-3 text-center">
                    <div className="text-sm font-semibold text-blue-600">
                      {rate.average_rate ? `$${formatExchangeRate(rate.average_rate)}` : (
                        <span className="text-gray-400 dark:text-gray-500">{t('common.not_available') || 'N/A'}</span>
                      )}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Vista de tarjetas para móviles */}
  <div className="md:hidden space-y-3">
        {rates.map((rate, index) => {
          const currencyInfo = getCurrencyInfo(rate.currency);
          return (
    <div key={`${rate.date}-${rate.currency}-${index}`} className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <span className="text-xl">{currencyInfo?.flag || '💱'}</span>
                  <div>
        <div className="text-sm font-semibold text-gray-900 dark:text-gray-100">{rate.currency}</div>
        <div className="text-xs text-gray-500 dark:text-gray-400">{currencyInfo?.name}</div>
                  </div>
                </div>
        <div className="text-xs text-gray-500 dark:text-gray-400 font-mono">
                  {rate.date}
                </div>
              </div>
              
              <div className="grid grid-cols-3 gap-3 text-center">
                <div>
                  <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">{t('exchange.buy_rate') || 'Compra'}</div>
                  <div className="text-sm font-semibold text-green-600">
                    ${formatExchangeRate(rate.buy_rate)}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">{t('exchange.sell_rate') || 'Venta'}</div>
                  <div className="text-sm font-semibold text-red-600">
                    ${formatExchangeRate(rate.sell_rate)}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">{t('exchange.average_rate') || 'Promedio'}</div>
                  <div className="text-sm font-semibold text-blue-600">
                    {rate.average_rate ? `$${formatExchangeRate(rate.average_rate)}` : (
                      <span className="text-gray-400">{t('common.not_available') || 'N/A'}</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </>
  );

  // Componente de gráfico de cotizaciones
  const ExchangeChart = ({ data }) => {
    const currencies = [...new Set(data.map(item => item.currency))];
    
    // Colores para diferentes monedas
    const currencyColors = {
      'USD': '#10b981', // Verde
      'EUR': '#3b82f6', // Azul
      'ARS': '#f59e0b', // Amarillo
      'BRL': '#ef4444'  // Rojo
    };

    // Si hay múltiples monedas, crear un gráfico por moneda
    if (currencies.length > 1) {
      return (
        <div className="space-y-6">
          {currencies.map(currency => {
            const currencyData = prepareChartData(data.filter(item => item.currency === currency));
            if (currencyData.length === 0) return null;

            const yAxisDomain = calculateYAxisDomain(currencyData);

            return (
              <div key={currency} className="card fade-in">
                <h4 className="text-lg font-semibold text-gray-900 mb-4">
                  {getCurrencyInfo(currency)?.flag || '💱'} {currency} - {t('exchange.rates_evolution') || 'Evolución de Cotizaciones'}
                </h4>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={currencyData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="date" 
                        angle={-45}
                        textAnchor="end"
                        height={80}
                        fontSize={11}
                      />
                      <YAxis 
                        fontSize={11}
                        domain={yAxisDomain}
                        tickFormatter={(value) => `$${value.toFixed(2)}`}
                      />
                      <Tooltip 
                        formatter={(value, name) => [`$${value.toFixed(4)}`, name]}
                        labelFormatter={(label) => `${t('common.date') || 'Fecha'}: ${label}`}
                      />
                      <Legend />
                      
                      <Line
                        type="monotone"
                        dataKey="buy_rate"
                        name={`${t('exchange.buy_rate') || 'Compra'}`}
                        stroke={currencyColors[currency] || '#6b7280'}
                        strokeWidth={2}
                        dot={{ fill: currencyColors[currency] || '#6b7280', strokeWidth: 2, r: 3 }}
                      />
                      
                      <Line
                        type="monotone"
                        dataKey="sell_rate"
                        name={`${t('exchange.sell_rate') || 'Venta'}`}
                        stroke={currencyColors[currency] || '#6b7280'}
                        strokeWidth={2}
                        strokeDasharray="5 5"
                        dot={{ fill: currencyColors[currency] || '#6b7280', strokeWidth: 2, r: 3 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            );
          })}
        </div>
      );
    }

    // Si hay una sola moneda, mostrar un gráfico simple
    const chartData = prepareChartData(data);
    const currency = currencies[0];
    const yAxisDomain = calculateYAxisDomain(chartData);

    return (
      <div className="card fade-in">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">
          📈 {getCurrencyInfo(currency)?.flag || '💱'} {currency} - {t('exchange.rates_evolution') || 'Evolución de Cotizaciones'}
        </h4>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="date" 
                angle={-45}
                textAnchor="end"
                height={80}
                fontSize={11}
              />
              <YAxis 
                fontSize={11}
                domain={yAxisDomain}
                tickFormatter={(value) => `$${value.toFixed(2)}`}
              />
              <Tooltip 
                formatter={(value, name) => [`$${value.toFixed(4)}`, name]}
                labelFormatter={(label) => `${t('common.date') || 'Fecha'}: ${label}`}
              />
              <Legend />
              
              <Line
                type="monotone"
                dataKey="buy_rate"
                name={`${t('exchange.buy_rate') || 'Compra'}`}
                stroke={currencyColors[currency] || '#10b981'}
                strokeWidth={2}
                dot={{ fill: currencyColors[currency] || '#10b981', strokeWidth: 2, r: 3 }}
              />
              
              <Line
                type="monotone"
                dataKey="sell_rate"
                name={`${t('exchange.sell_rate') || 'Venta'}`}
                stroke={currencyColors[currency] || '#ef4444'}
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={{ fill: currencyColors[currency] || '#ef4444', strokeWidth: 2, r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-4 flex flex-wrap justify-center gap-4 text-xs text-gray-600">
          <div className="flex items-center">
            <div className="w-4 h-0.5" style={{backgroundColor: currencyColors[currency] || '#10b981'}}></div>
            <span className="ml-2">{t('exchange.buy_rate') || 'Compra'} ({t('exchange.solid_line') || 'línea sólida'})</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-0.5" style={{
              backgroundImage: `repeating-linear-gradient(to right, transparent, transparent 2px, ${currencyColors[currency] || '#ef4444'} 2px, ${currencyColors[currency] || '#ef4444'} 4px)`
            }}></div>
            <span className="ml-2">{t('exchange.sell_rate') || 'Venta'} ({t('exchange.dashed_line') || 'línea punteada'})</span>
          </div>
        </div>
      </div>
    );
  };

  // Paginación para tabla / listado
  const PAGE_SIZE = 20;
  const [page, setPage] = React.useState(0);
  const totalPages = Math.ceil(filteredData.length / PAGE_SIZE) || 1;
  const paginatedData = React.useMemo(() => {
    const start = page * PAGE_SIZE;
    return filteredData.slice(start, start + PAGE_SIZE);
  }, [filteredData, page]);

  return (
    <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-md p-6">
      <div className="text-center mb-8">
        {/* Eliminamos ícono azul grande para reducir ruido visual y mejor contraste en dark */}
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          {t('exchange.results_title') || 'Resultados de Cotizaciones'}
        </h1>
	<p className="text-gray-600 dark:text-gray-400">
          {t('exchange.results_subtitle') || 'Consulta realizada exitosamente'}
        </p>
      </div>

      {/* Mostrar resultados según el tipo de búsqueda */}
      {(searchType === 'latest' || searchType === 'date') && filteredData.length <= 6 ? (
        // Vista de tarjetas en una sola columna
        <div className="space-y-4">
          {filteredData.map((rate, index) => (
            <div key={`${rate.date}-${rate.currency}-${index}`} className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-700 border border-blue-200 dark:border-gray-600/70 rounded-lg p-6 shadow-sm dark:shadow-[0_0_0_1px_rgba(255,255,255,0.04)]">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <span className="text-3xl mr-3">{getCurrencyInfo(rate.currency)?.flag || '💱'}</span>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900 dark:text-gray-50">{rate.currency}</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-300">{getCurrencyInfo(rate.currency)?.name || rate.currency}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-500 dark:text-gray-400">{rate.date}</p>
                  {rate.arbitrage && (
                    <p className="text-sm text-blue-600 dark:text-blue-400 font-medium">{rate.arbitrage}</p>
                  )}
                </div>
              </div>
              
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center p-3 bg-white dark:bg-gray-900/40 rounded-lg shadow-sm">
                  <p className="text-sm text-gray-600 dark:text-gray-300 mb-1">{t('exchange.buy_rate') || 'Compra'}</p>
                  <p className="text-xl font-bold text-green-600">
                    ${formatExchangeRate(rate.buy_rate)}
                  </p>
                </div>
                <div className="text-center p-3 bg-white dark:bg-gray-900/40 rounded-lg shadow-sm">
                  <p className="text-sm text-gray-600 dark:text-gray-300 mb-1">{t('exchange.sell_rate') || 'Venta'}</p>
                  <p className="text-xl font-bold text-red-600">
                    ${formatExchangeRate(rate.sell_rate)}
                  </p>
                </div>
                {rate.average_rate && (
                  <div className="text-center p-3 bg-white dark:bg-gray-900/40 rounded-lg shadow-sm">
                    <p className="text-sm text-gray-600 dark:text-gray-300 mb-1">{t('exchange.average_rate') || 'Promedio'}</p>
                    <p className="text-xl font-bold text-blue-600">
                      ${formatExchangeRate(rate.average_rate)}
                    </p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        // Vista de tabla para muchas cotizaciones o historial
        <div className="space-y-6">
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {filteredData.length > 1 && (
                <span className="text-sm text-gray-600 dark:text-gray-300">
                  {t('exchange.total_records') || 'Total de registros'}: <strong className="text-gray-900 dark:text-gray-100">{filteredData.length}</strong>
                </span>
              )}
              {filteredData.length > 0 && (
                <span className="text-sm text-gray-600 dark:text-gray-300">
                  {t('common.period') || 'Período'}: <strong className="text-gray-900 dark:text-gray-100">{filteredData[filteredData.length - 1]?.date} - {filteredData[0]?.date}</strong>
                </span>
              )}
            </div>
          </div>

          {/* Gráfico de cotizaciones para múltiples datos */}
          {filteredData.length > 1 && (searchType === 'range' || searchType === 'history') && (
            <ExchangeChart data={filteredData} />
          )}

          <div className="card">
            <HistoryTable rates={paginatedData} />
            {filteredData.length > PAGE_SIZE && (
              <div className="flex items-center justify-between mt-4 text-sm">
                <button
                  onClick={() => setPage(p => Math.max(0, p - 1))}
                  disabled={page === 0}
                  className={`px-3 py-1 rounded ${page === 0 ? 'bg-gray-200 text-gray-400 dark:bg-gray-700 dark:text-gray-500 cursor-not-allowed' : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600'}`}
                >
                  {t('common.previous') || 'Anterior'}
                </button>
                <div className="text-gray-600 dark:text-gray-300">
                  {t('common.page') || 'Página'} {page + 1} / {totalPages}
                </div>
                <button
                  onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
                  disabled={page >= totalPages - 1}
                  className={`px-3 py-1 rounded ${page >= totalPages - 1 ? 'bg-gray-200 text-gray-400 dark:bg-gray-700 dark:text-gray-500 cursor-not-allowed' : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600'}`}
                >
                  {t('common.next') || 'Siguiente'}
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Resumen estadístico para múltiples resultados */}
      {filteredData.length > 1 && (
        <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700/60 rounded-lg">
          <div className="flex items-center mb-4">
            <SummaryIcon className="w-6 h-6 mr-3 text-blue-600" />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
              {t('exchange.summary') || 'Resumen'}
            </h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <p className="text-gray-600 dark:text-gray-300">{t('exchange.currencies_included') || 'Monedas incluidas'}:</p>
              <p className="font-medium text-gray-900 dark:text-gray-100">
                {[...new Set(filteredData.map(rate => rate.currency))].join(', ')}
              </p>
            </div>
            <div>
              <p className="text-gray-600 dark:text-gray-300">{t('exchange.date_range') || 'Rango de fechas'}:</p>
              <p className="font-medium text-gray-900 dark:text-gray-100">
                {filteredData.length > 1 
                  ? `${filteredData[filteredData.length - 1]?.date} - ${filteredData[0]?.date}`
                  : filteredData[0]?.date
                }
              </p>
            </div>
            {filteredData.length > 1 && (
              <div>
                <p className="text-gray-600 dark:text-gray-300">{t('exchange.total_records') || 'Total de registros'}:</p>
                <p className="font-medium text-gray-900 dark:text-gray-100">{filteredData.length}</p>
              </div>
            )}
          </div>
        </div>
      )}
      {/* Panel informativo eliminado por redundancia */}
    </div>
  );
};

export default ExchangeResultsDisplay; 