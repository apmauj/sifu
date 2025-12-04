import React from 'react';
import exchangeService from '../../services/exchangeService';
import Spinner from '../../shared/components/ui/Spinner';
import Alert from '../../shared/components/ui/Alert';
import { getSemanticClass } from '../../shared/theme/colors';
import { useI18n } from '../../shared/contexts/I18nContext';

/**
 * Panel azul de estado (similar a UI / UR) para cotizaciones históricas.
 * Muestra: total de registros, período disponible, monedas soportadas y fecha del último día.
 */
const ExchangeDataStatusPanel = ({ refreshKey, showSource = false }) => {
  const { t } = useI18n();
  const [info, setInfo] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);

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
    fetchInfo();
  }, [t, refreshKey]);

  const totalRecords = info?.total_records ?? 'N/D';
  const minDate = info?.date_range?.min_date || '—';
  const maxDate = info?.date_range?.max_date || '—';
  const currencies = info?.available_currencies || [];
  const lastDate = maxDate;

  return (
    <div className={`mb-6 border rounded-xl p-4 ${getSemanticClass('info', 'bg', 50)} dark:${getSemanticClass('info', 'bg', 950)} ${getSemanticClass('info', 'border', 200)} dark:${getSemanticClass('info', 'border', 800)}`}>
      {loading ? (
        <div className="flex items-center gap-2">
          <Spinner size="sm" variant="primary" />
          <span className={`text-sm ${getSemanticClass('info', 'text', 700)}`}>
            {t('common.loading') || 'Cargando información...'}
          </span>
        </div>
      ) : error ? (
        <Alert variant="error">
          {error}
        </Alert>
      ) : (
        <div className="flex items-center justify-between">
          <div>
            <h2 className={`text-sm font-medium ${getSemanticClass('info', 'text', 900)} dark:${getSemanticClass('info', 'text', 100)}`}>
              📊 {t('exchange.data_status_title') || 'Estado de los datos de Cotizaciones'}
            </h2>
            <p className={`text-sm ${getSemanticClass('info', 'text', 800)} dark:${getSemanticClass('info', 'text', 100)}/90`}>
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
            <div className={`text-sm ${getSemanticClass('info', 'text', 700)} dark:${getSemanticClass('info', 'text', 100)}`}>
              {t('exchange.latest_day') || 'Último día disponible'}:
            </div>
            <div className={`text-lg font-semibold ${getSemanticClass('info', 'text', 900)} dark:text-white`}>
              {lastDate}
            </div>
            {showSource && (
              <div className={`text-xs ${getSemanticClass('info', 'text', 700)} dark:${getSemanticClass('info', 'text', 200)} mt-1`}>
                {t('exchange.source_note') || t('exchange.source_note_fallback') || 'Fuente: INE (histórico, último día hábil publicado)'}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ExchangeDataStatusPanel;

