import React from 'react';
import { CalendarIcon, ChartBarIcon, ArrowDownIcon, ArrowUpIcon, MinusIcon } from '../icons';
import { OpenMojiIcon } from '../icons/openmoji/index.jsx';
import IconCircle from './ui/IconCircle.jsx';
import { format, parseISO } from 'date-fns';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useI18n } from '../contexts/I18nContext';
import {
  DATE_FORMAT_DDMMYYYY,
  CURRENCY,
  CURRENCY_LOCALE,
  CURRENCY_DECIMALS,
  DATA_SOURCE_LABEL,
  NO_RESULTS_MESSAGE,
  NO_RESULTS_HINT
} from '../constants';

function calculateVariations(data) {
  if (!data || data.length === 0) return [];
  return data.map((item, idx) => {
    if (idx === 0) {
      return { ...item, variation: 0 };
    } else {
      const prev = data[idx - 1].value || data[idx - 1].valor;
      const current = item.value || item.valor;
      const variation = prev !== 0 ? ((current - prev) / prev) * 100 : 0;
      return { ...item, variation };
    }
  });
}

const ResultsDisplay = ({ results, searchType }) => {
  const { t } = useI18n();

  // ESLint workaround: declare used components with underscore prefix
  const _React = React;
  const _CalendarIcon = CalendarIcon;
  const _ChartBarIcon = ChartBarIcon;
  const _ArrowDownIcon = ArrowDownIcon;
  const _ArrowUpIcon = ArrowUpIcon;
  const _MinusIcon = MinusIcon;
  const _OpenMojiIcon = OpenMojiIcon;
  const _IconCircle = IconCircle;
  const _LineChart = LineChart;
  const _Line = Line;
  const _XAxis = XAxis;
  const _YAxis = YAxis;
  const _CartesianGrid = CartesianGrid;
  const _Tooltip = Tooltip;
  const _Legend = Legend;
  const _ResponsiveContainer = ResponsiveContainer;

  if (!results || !results.success) {
    return (
      <div className="rounded-lg border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 p-6 fade-in">
        <div className="text-center py-8">
          <div className="text-neutral-400 dark:text-neutral-500 mb-4">
            <_ChartBarIcon className="w-16 h-16 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-neutral-900 dark:text-neutral-100 mb-2">
            {results?.message || t('ui.no_results') || NO_RESULTS_MESSAGE}
          </h3>
          <p className="text-neutral-600 dark:text-neutral-300">
            {t('ui.no_results_hint') || NO_RESULTS_HINT}
          </p>
        </div>
      </div>
    );
  }

  const formatDate = (dateString) => {
    if (!dateString || typeof dateString !== 'string' || dateString.trim() === '') {
      return 'Fecha no disponible';
    }
    try {
      return format(parseISO(dateString), DATE_FORMAT_DDMMYYYY);
    } catch (error) {
      console.warn('Error formatting date:', dateString, error);
      return 'Fecha inválida';
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat(CURRENCY_LOCALE, {
      style: 'currency',
      currency: CURRENCY,
      minimumFractionDigits: CURRENCY_DECIMALS,
      maximumFractionDigits: CURRENCY_DECIMALS
    }).format(value);
  };

  const calculateVariation = (current, previous) => {
    if (!previous) return null;
    const variation = current - previous;
    const percentage = ((variation / previous) * 100);
    return {
      absolute: variation,
      percentage: percentage,
      trend: variation > 0 ? 'up' : variation < 0 ? 'down' : 'stable'
    };
  };

  const renderTrendIcon = (trend) => {
    switch (trend) {
      case 'up':
        return <_ArrowUpIcon className="w-4 h-4 text-green-600" />;
      case 'down':
        return <_ArrowDownIcon className="w-4 h-4 text-red-600" />;
      default:
        return <_MinusIcon className="w-4 h-4 text-neutral-400" />;
    }
  };

  const renderSingleResult = (data) => {
    return (
      <div className="rounded-lg border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 p-6 fade-in">
        <div className="text-center">
          <div className="flex justify-center mb-4"><_IconCircle><_OpenMojiIcon name="calculator" size={32} /></_IconCircle></div>
          
          <h3 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100 mb-2">
            {t('ui.ui_value') || 'Valor de la UI'}
          </h3>
          
          <div className="bg-neutral-50 dark:bg-neutral-700/60 rounded-lg p-6 mb-4">
            <div className="text-3xl font-bold text-uruguay-blue dark:text-blue-300 mb-2">
              {formatCurrency(data.value || data.valor)}
            </div>
            <div className="flex items-center justify-center text-neutral-600 dark:text-neutral-300">
              <_CalendarIcon className="w-4 h-4 mr-2" />
              {formatDate(data.date || data.fecha)}
            </div>
          </div>
          
          <div className="text-sm text-neutral-500 dark:text-neutral-400">
            {t('ui.data_source') || DATA_SOURCE_LABEL}
          </div>
        </div>
      </div>
    );
  };

  const renderRangeResults = (data) => {
    const sortedData = [...data].sort((a, b) => new Date(a.date || a.fecha) - new Date(b.date || b.fecha));
    const latest = sortedData[sortedData.length - 1];
    const oldest = sortedData[0];
    const variation = calculateVariation(latest.value || latest.valor, oldest.value || oldest.valor);
    const chartData = calculateVariations(sortedData).map(item => ({
      fecha: formatDate(item.date || item.fecha),
      valor: item.value || item.valor,
      variacion: Number(item.variation.toFixed(2)),
    }));

    return (
      <div className="space-y-6">
        {/* Resumen */}
        <div className="rounded-lg border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 p-6 fade-in">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-neutral-900 dark:text-neutral-100">
              {t('ui.period_summary') || 'Resumen del Período'}
            </h3>
            <div className="text-sm text-neutral-500 dark:text-neutral-400">
              {sortedData.length} {sortedData.length === 1 ? (t('common.record') || 'registro') : (t('common.records') || 'registros')}
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-neutral-50 dark:bg-neutral-700/60 rounded-lg p-4">
              <div className="text-sm text-neutral-600 dark:text-neutral-300 mb-1">{t('ui.initial_value') || 'Valor inicial'}</div>
              <div className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">
                {formatCurrency(oldest.value || oldest.valor)}
              </div>
              <div className="text-xs text-neutral-500 dark:text-neutral-400">
                {formatDate(oldest.date || oldest.fecha)}
              </div>
            </div>
            
            <div className="bg-neutral-50 dark:bg-neutral-700/60 rounded-lg p-4">
              <div className="text-sm text-neutral-600 dark:text-neutral-300 mb-1">{t('ui.final_value') || 'Valor final'}</div>
              <div className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">
                {formatCurrency(latest.value || latest.valor)}
              </div>
              <div className="text-xs text-neutral-500 dark:text-neutral-400">
                {formatDate(latest.date || latest.fecha)}
              </div>
            </div>
            
            {variation && (
              <div className="bg-neutral-50 dark:bg-neutral-700/60 rounded-lg p-4">
                <div className="text-sm text-neutral-600 dark:text-neutral-300 mb-1">{t('common.variation') || 'Variación'}</div>
                <div className={`text-lg font-semibold flex items-center ${
                  variation.trend === 'up' ? 'text-green-600' : 
                  variation.trend === 'down' ? 'text-red-600' : 'text-neutral-900 dark:text-neutral-100'
                }`}>
                  {renderTrendIcon(variation.trend)}
                  <span className="ml-1">
                    {variation.percentage.toFixed(4)}%
                  </span>
                </div>
                <div className="text-xs text-neutral-500 dark:text-neutral-400">
                  {formatCurrency(Math.abs(variation.absolute))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Gráfico de líneas: Valor de la UI */}
        <div className="rounded-lg border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 p-6 fade-in">
          <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-4">{t('ui.ui_evolution') || 'Evolución del valor de la UI'}</h3>
          <_ResponsiveContainer width="100%" height={300}>
            <_LineChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
              <_CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <_XAxis dataKey="fecha" tick={{ fontSize: 12, fill: '#d1d5db' }} />
              <_YAxis tick={{ fontSize: 12, fill: '#d1d5db' }} domain={['auto', 'auto']} />
              <_Tooltip formatter={formatCurrency} labelFormatter={v => `${t('common.date') || 'Fecha'}: ${v}`} />
              <_Legend />
              <_Line type="monotone" dataKey="valor" name={t('ui.ui_value') || 'Valor UI'} stroke="#2563eb" strokeWidth={2} dot={false} />
            </_LineChart>
          </_ResponsiveContainer>
        </div>

        {/* Gráfico de líneas: Variación porcentual diaria */}
        <div className="rounded-lg border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 p-6 fade-in">
          <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-4">{t('ui.daily_percentage_variation') || 'Variación porcentual diaria'}</h3>
          <_ResponsiveContainer width="100%" height={300}>
            <_LineChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
              <_CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <_XAxis dataKey="fecha" tick={{ fontSize: 12, fill: '#d1d5db' }} />
              <_YAxis tick={{ fontSize: 12, fill: '#d1d5db' }} domain={['auto', 'auto']} unit="%" />
              <_Tooltip formatter={v => `${v}%`} labelFormatter={v => `${t('common.date') || 'Fecha'}: ${v}`} />
              <_Legend />
              <_Line type="monotone" dataKey="variacion" name={t('ui.variation_percentage') || 'Variación %'} stroke="#f59e42" strokeWidth={2} dot={false} />
            </_LineChart>
          </_ResponsiveContainer>
        </div>
      </div>
    );
  };

  return (
    <div>
      {searchType === 'single' && results.data ? 
        renderSingleResult(results.data) : 
        Array.isArray(results.data) && results.data.length > 0 ? 
          renderRangeResults(results.data) : 
          <div className="rounded-lg border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 p-6 fade-in">
            <div className="text-center py-8">
              <div className="text-neutral-400 dark:text-neutral-500 mb-4">
                <_ChartBarIcon className="w-16 h-16 mx-auto" />
              </div>
              <h3 className="text-lg font-medium text-neutral-900 dark:text-neutral-100 mb-2">
                {t('ui.no_data_found') || 'No se encontraron datos'}
              </h3>
              <p className="text-neutral-600 dark:text-neutral-300">
                {t('ui.no_results_description') || 'Realiza una consulta para ver los valores de UI.'}
              </p>
            </div>
          </div>
      }
    </div>
  );
};

export default ResultsDisplay; 