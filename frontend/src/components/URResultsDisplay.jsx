import React from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { ExclamationTriangleIcon, MagnifyingGlassIcon } from '../icons';
import { useI18n } from '../contexts/I18nContext';

const URResultsDisplay = ({ results, searchType, isLoading, error }) => {
  const { t, translateBackendMessage, currentLanguage } = useI18n();

  // Function to format monetary values (UR with 2 decimals)
  const formatURValue = (value) => {
    if (value === null || value === undefined) return t('common.not_available') || 'N/D';
    return new Intl.NumberFormat('es-UY', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  // Function to format period
  const formatPeriod = (year, month) => {
    if (!year) return t('common.not_available') || 'N/D';
    if (!month) return year.toString();
    
    const monthKeys = [
      'january', 'february', 'march', 'april', 'may', 'june',
      'july', 'august', 'september', 'october', 'november', 'december'
    ];
    
    const monthName = t(`ur.${monthKeys[month - 1]}`) || monthKeys[month - 1];
    return `${monthName} ${year}`;
  };

  const formatPercentage = (value) => {
    if (value === null || value === undefined || isNaN(value)) return t('common.not_available') || 'N/D';
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
  };

  // Function to calculate statistics
  const calculateStats = (data) => {
    if (!data || data.length === 0) return null;
    
    const values = data.map(item => item.value).filter(v => v !== null && v !== undefined);
    if (values.length === 0) return null;
    
    const sum = values.reduce((acc, val) => acc + val, 0);
    const avg = sum / values.length;
    const min = Math.min(...values);
    const max = Math.max(...values);
    const initialValue = data[0]?.value;
    const finalValue = data[data.length - 1]?.value;
    const totalVariation = initialValue && finalValue ? 
      ((finalValue - initialValue) / initialValue) * 100 : null;
    
    return { avg, min, max, initialValue, finalValue, totalVariation };
  };

  // Function to calculate monthly variations
  const calculateMonthlyVariations = (data) => {
    if (!data || data.length < 2) return [];
    
    // Sort by year and month
    const sortedData = [...data].sort((a, b) => {
      if (a.year !== b.year) return a.year - b.year;
      return a.month - b.month;
    });

    return sortedData.map((item, index) => {
      if (index === 0) {
        return { ...item, variation: null };
      }
      
      const prevItem = sortedData[index - 1];
      const variation = prevItem.value && item.value ? 
        ((item.value - prevItem.value) / prevItem.value) * 100 : null;
      
      return { ...item, variation };
    });
  };

  // Estos datos pueden ser undefined, pero los hooks SIEMPRE deben ejecutarse
  const data = React.useMemo(() => {
    if (!results || !results.data) return [];
    return Array.isArray(results.data) ? results.data : [results.data];
  }, [results]);

  const stats = React.useMemo(() => calculateStats(data), [data]);
  const dataWithVariations = React.useMemo(() => calculateMonthlyVariations(data), [data]);
  const sortedData = React.useMemo(() => {
    return [...data].sort((a, b) => {
      if (a.year !== b.year) return a.year - b.year;
      return a.month - b.month;
    });
  }, [data]);
  const chartData = React.useMemo(() => {
    return sortedData.map(item => ({
      name: formatPeriod(item.year, item.month),
      value: item.value,
      year: item.year,
      month: item.month
    }));
  }, [sortedData, currentLanguage]);
  const variationChartData = React.useMemo(() => {
    return dataWithVariations.slice(1).map(item => ({
      ...item,
      name: formatPeriod(item.year, item.month)
    }));
  }, [dataWithVariations, currentLanguage]);

  // Render condicional SOLO aquí, después de todos los hooks
  if (isLoading) {
    return (
      <div className="card">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500 mr-3"></div>
          <span className="text-gray-600 dark:text-gray-300">{t('common.loading') || 'Cargando...'}</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="text-center py-8">
          <ExclamationTriangleIcon className="w-12 h-12 text-red-500 dark:text-red-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">{t('common.error') || 'Error'}</h3>
          <p className="text-gray-600 dark:text-gray-300">{error}</p>
        </div>
      </div>
    );
  }

  if (!results || !results.success) {
    return (
      <div className="card">
        <div className="text-center py-8">
          <MagnifyingGlassIcon className="w-12 h-12 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
            {t('ur.no_results') || 'No se encontraron valores de UR'}
          </h3>
          <p className="text-gray-600 dark:text-gray-300">
            {t('ur.no_results_hint') || 'Intenta con otro período o usa los selectores rápidos'}
          </p>
        </div>
      </div>
    );
  }

  // Render principal (sin URInfoSummary)
  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            {searchType === 'single' ? 
              (t('ur.ur_value') || 'Valor UR') : 
              (t('ur.ur_values') || 'Valores UR')
            }
          </h3>
          <div className="text-sm text-gray-500 dark:text-gray-400">
            {data.length} {data.length === 1 ? (t('common.record') || 'registro') : (t('common.records') || 'registros')}
          </div>
        </div>

        {searchType === 'single' && data.length === 1 ? (
          // Single value display
          <div className="text-center py-6">
            <div className="text-4xl font-bold text-uruguay-blue dark:text-blue-400 mb-2">
              {formatURValue(data[0].value)}
            </div>
            <div className="text-lg text-gray-600 dark:text-gray-300">
              {formatPeriod(data[0].year, data[0].month)}
            </div>
            {/* El mensaje del backend ahora se muestra como notificación toast */}
          </div>
        ) : (
          // Multiple values or range display
          <div className="space-y-4">
            {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-gray-50 dark:bg-gray-700/60 rounded-lg">
                <div className="text-center">
          <div className="text-sm text-gray-600 dark:text-gray-300">{t('ur.initial_value') || 'Valor inicial'}</div>
          <div className="text-lg font-semibold text-gray-900 dark:text-gray-100">{formatURValue(stats.initialValue)}</div>
                </div>
                <div className="text-center">
          <div className="text-sm text-gray-600 dark:text-gray-300">{t('ur.final_value') || 'Valor final'}</div>
          <div className="text-lg font-semibold text-gray-900 dark:text-gray-100">{formatURValue(stats.finalValue)}</div>
                </div>
                <div className="text-center">
          <div className="text-sm text-gray-600 dark:text-gray-300">{t('common.average') || 'Promedio'}</div>
          <div className="text-lg font-semibold text-gray-900 dark:text-gray-100">{formatURValue(stats.avg)}</div>
                </div>
                <div className="text-center">
          <div className="text-sm text-gray-600 dark:text-gray-300">{t('ur.total_variation') || 'Variación total'}</div>
              <div className={`text-lg font-semibold ${stats.totalVariation >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatPercentage(stats.totalVariation)}
                  </div>
                </div>
              </div>
            )}

            {/* El mensaje del backend ahora se muestra como notificación toast */}
          </div>
        )}
      </div>

      {/* Chart */}
      {data.length > 1 && (
        <div className="card">
          <h4 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            {t('ur.ur_evolution') || 'Evolución de la UR'}
          </h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis 
                  dataKey="name" 
                  angle={-45}
                  textAnchor="end"
                  height={80}
                  fontSize={12}
                  tick={{ fill: '#d1d5db' }}
                />
                <YAxis 
                  domain={['dataMin - 10', 'dataMax + 10']}
                  tickFormatter={formatURValue}
                  width={85}
                  fontSize={10}
                  tick={{ fill: '#d1d5db' }}
                />
                <Tooltip 
                  formatter={(value) => [formatURValue(value), t('ur.ur_value') || 'Valor UR']}
                  labelStyle={{ color: '#374151' }}
                />
                <Line 
                  type="monotone" 
                  dataKey="value" 
                  stroke="#2563eb" 
                  strokeWidth={2}
                  dot={{ fill: '#2563eb', strokeWidth: 2, r: 4 }}
                  activeDot={{ r: 6, stroke: '#2563eb', strokeWidth: 2 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Monthly Variations Chart */}
      {dataWithVariations.length > 1 && (
        <div className="card">
          <h4 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            {t('ur.monthly_percentage_variation') || 'Variación Porcentual Mensual'}
          </h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={variationChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis 
                  dataKey="name"
                  angle={-45}
                  textAnchor="end"
                  height={80}
                  fontSize={12}
                  tick={{ fill: '#d1d5db' }}
                />
                <YAxis tickFormatter={(value) => `${value}%`} tick={{ fill: '#d1d5db' }} />
                <Tooltip 
                  formatter={(value) => [formatPercentage(value), t('ur.variation_percentage') || 'Variación %']}
                  labelStyle={{ color: '#374151' }}
                />
                <Bar 
                  dataKey="variation" 
                  fill="#fbbf24"
                  name={t('ur.variation_percentage') || 'Variación %'}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-300 mt-2">
            {t('ur.variation_note') || 'Muestra el cambio porcentual respecto al mes anterior'}
          </p>
        </div>
      )}

      {/* Data Table */}
      <div className="card">
        <h4 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          {t('ur.period_information') || 'Información del Período'}
        </h4>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-600">
            <thead className="bg-gray-50 dark:bg-gray-700/60">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  {t('common.period') || 'Período'}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  {t('ur.ur_value') || 'Valor UR'}
                </th>
                {dataWithVariations.length > 1 && (
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    {t('ur.variation_percentage') || 'Variación %'}
                  </th>
                )}
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {(dataWithVariations.length > 1 ? dataWithVariations : data).map((item, index) => (
                <tr key={`${item.year}-${item.month}`} className={index % 2 === 0 ? 'bg-white dark:bg-gray-800' : 'bg-gray-50 dark:bg-gray-700/40'}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100">
                    {formatPeriod(item.year, item.month)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                    {formatURValue(item.value)}
                  </td>
                  {dataWithVariations.length > 1 && (
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {item.variation !== null ? (
                        <span className={item.variation >= 0 ? 'text-green-500' : 'text-red-500'}>
                          {formatPercentage(item.variation)}
                        </span>
                      ) : (
                        <span className="text-gray-400 dark:text-gray-500">-</span>
                      )}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Data Source */}
  <div className="text-center text-sm text-gray-500 dark:text-gray-400">
        {t('ur.data_source') || 'Fuente: Banco Hipotecario del Uruguay (BHU)'}
      </div>
    </div>
  );
};

export default URResultsDisplay;