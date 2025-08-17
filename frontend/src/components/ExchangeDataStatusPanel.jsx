import React from 'react';
import exchangeService from '../services/exchangeService';
import { useI18n } from '../contexts/I18nContext';

/**
 * Panel azul de estado (similar a UI / UR) para cotizaciones históricas.
 * Muestra: total de registros, período disponible, monedas soportadas y fecha del último día.
 */
const ExchangeDataStatusPanel = ({ refreshKey }) => {
  const { t } = useI18n();
  const [info, setInfo] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);

  const hasFetchedRef = React.useRef(false);

  React.useEffect(() => {
    const fetchInfo = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await exchangeService.getInfo();
        if (data && data.total_records) {
          setInfo(data);
        } else {
          setInfo(null);
          setError(t('exchange.status_error') || 'Error al cargar estado de cotizaciones');
        }
      } catch (e) {
        console.error('ExchangeDataStatusPanel fetchInfo error', e);
        setInfo(null);
        setError(t('exchange.status_error') || 'Error al cargar estado de cotizaciones');
      } finally {
        setLoading(false);
      }
    };
    if (hasFetchedRef.current && refreshKey === undefined) return; // evita doble fetch StrictMode inicial
    hasFetchedRef.current = true;
    fetchInfo();
  }, [t, refreshKey]);

  const totalRecords = info?.total_records ?? 'N/D';
  const minDate = info?.date_range?.min_date || '—';
  const maxDate = info?.date_range?.max_date || '—';
  const currencies = info?.available_currencies || [];
  const lastDate = maxDate;

  return (
    <div className="mb-6 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-xl p-4">
      {loading ? (
        <span className="text-blue-700 text-sm">{t('common.loading') || 'Cargando información...'}</span>
      ) : error ? (
        <span className="text-red-600 text-sm">{error}</span>
      ) : (
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-sm font-medium text-blue-900 dark:text-blue-100">📊 {t('exchange.data_status_title') || 'Estado de los datos de Cotizaciones'}</h2>
            <p className="text-sm text-blue-800 dark:text-blue-100/90">
              {totalRecords.toLocaleString ? totalRecords.toLocaleString() : totalRecords} {t('common.records') || 'registros'} {t('exchange.available') || 'disponibles'}
              {minDate !== '—' && maxDate !== '—' && (
                <span> • {t('common.period') || 'Período'}: {minDate} a {maxDate}</span>
              )}
              {currencies.length > 0 && (
                <span> • {t('exchange.currencies_label') || 'Monedas'}: {currencies.join(', ')}</span>
              )}
            </p>
          </div>
          <div className="text-right">
            <div className="text-sm text-blue-700 dark:text-blue-100">{t('exchange.latest_day') || 'Último día disponible'}:</div>
            <div className="text-lg font-semibold text-blue-900 dark:text-white">{lastDate}</div>
            <div className="text-xs text-blue-700 dark:text-blue-200 mt-1">{t('exchange.source_note') || t('exchange.source_note_fallback') || 'Fuente: INE (histórico, último día hábil publicado)'}</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExchangeDataStatusPanel;
