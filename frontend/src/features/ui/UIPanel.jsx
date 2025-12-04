import React from 'react';
import SearchForm from './SearchForm';
import ResultsDisplay from './ResultsDisplay';
import uiService from '../../services/api';
import { useI18n } from '../../shared/contexts/I18nContext';
import Card, { CardBody } from '../../shared/components/ui/Card';
import { CURRENCY, CURRENCY_LOCALE } from '../../constants';
import Spinner from '../../shared/components/ui/Spinner';
import Alert from '../../shared/components/ui/Alert';
import { getSemanticClass, getSemanticClassWithDark } from '../../shared/theme/colors';

const UIPanel = ({ refreshKey }) => {
  const { t, currentLanguage } = useI18n();
  const [uiInfo, setUiInfo] = React.useState({});
  const [uiInfoLoading, setUiInfoLoading] = React.useState(true);
  const [uiInfoError, setUiInfoError] = React.useState(null);
  
  // Estado para resultados de búsqueda UI
  const [results, setResults] = React.useState(null);
  const [searchLoading, setSearchLoading] = React.useState(false);
  const [searchType, setSearchType] = React.useState('single');

  const formatUIValue = (value) => {
    if (value === null || value === undefined) return t('common.not_available') || 'N/D';
    // Fallback defensivo: si por alguna razón CURRENCY quedó configurado en '$', usar 'UYU'
    const isoCurrency = CURRENCY === '$' ? 'UYU' : CURRENCY;
    const formatted = new Intl.NumberFormat(CURRENCY_LOCALE, {
      style: 'currency',
      currency: isoCurrency, // Código ISO válido (UYU)
      minimumFractionDigits: 4,
      maximumFractionDigits: 4
    }).format(value);
    // Opcional: normalizar a símbolo $ únicamente (evitar mostrar UYU si el locale lo antepone)
    return formatted.replace(/UYU\s*/i, '$');
  };

  const hasRequestedInfoRef = React.useRef(false);
  React.useEffect(() => {
    const fetchUIInfo = async () => {
      setUiInfoLoading(true);
      setUiInfoError(null);
      try {
        const response = await uiService.getInfo();
        // Aceptar forma directa o envuelta { success, data }
        const data = response?.data || response;
        if (data && data.total_records) {
          setUiInfo(data);
        } else {
          setUiInfo({});
          setUiInfoError(t('errors.search_data_error') || 'Error al cargar información de UI');
        }
      } catch (err) {
        console.error('Error fetching UI info:', err);
        setUiInfo({});
        setUiInfoError(t('errors.search_data_error') || 'Error al cargar información de UI');
      } finally {
        setUiInfoLoading(false);
      }
    };
    if (hasRequestedInfoRef.current && !refreshKey) return; // evita doble llamada StrictMode
    hasRequestedInfoRef.current = true;
    fetchUIInfo();
  }, [t, currentLanguage, refreshKey]);

  // Cargar automáticamente el valor correspondiente al día de hoy (o el más cercano previo)
  // en lugar de forzar siempre el último valor futuro disponible.
  const loadedTodayRef = React.useRef(false);
  React.useEffect(() => {
    const loadTodayUI = async () => {
      // Requisitos: no cargando, no ejecutado antes, info básica disponible
      if (uiInfoLoading || loadedTodayRef.current) return;
      const hasRange = !!uiInfo?.date_range?.min_date && !!uiInfo?.date_range?.max_date;
      const hasLatest = !!uiInfo?.latest_ui?.date;
      if (!hasRange || !hasLatest) return; // evita llamadas en estado de error / info incompleta
      try {
        setSearchLoading(true);
        setResults(null);
        setSearchType('single');
        const todayISO = new Date().toISOString().slice(0, 10);
        const latestISO = uiInfo.latest_ui.date;
        const minISO = uiInfo.date_range.min_date;
        const maxISO = uiInfo.date_range.max_date;
        let targetDate = todayISO;
        if (todayISO > maxISO) targetDate = latestISO; else if (todayISO < minISO) targetDate = minISO;
        const response = await uiService.getByDate(targetDate);
        setResults(response);
      } catch (err) {
        console.error('Error loading today UI value:', err);
        setResults({ success: false, message: t('errors.search_data_error') || 'Error al cargar valor de hoy' });
      } finally {
        setSearchLoading(false);
        loadedTodayRef.current = true;
      }
    };
    if (refreshKey) loadedTodayRef.current = false; // permitir recarga tras refresh manual
    loadTodayUI();
  }, [uiInfo, uiInfoLoading, t, refreshKey]);

  // Función para buscar valores de UI
  const handleSearch = async (params) => {
    setSearchLoading(true);
    setResults(null);
    setSearchType(params.searchType || params.type || 'single');
    try {
      let response;
      if ((params.searchType || params.type) === 'range') {
        response = await uiService.getByRange(params.startDate || params.fechaInicio, params.endDate || params.fechaFin);
      } else {
        response = await uiService.getByDate(params.date || params.fecha);
      }
      setResults(response);
    } catch (err) {
      console.error('UI search error:', err);
      setResults({ success: false, message: t('errors.search_data_error') || 'Error al consultar valores de UI' });
    } finally {
      setSearchLoading(false);
    }
  };

  return (
    <div>
      {/* Panel de estado de datos UI */}
      <div className={`mb-6 border rounded-xl p-4 ${getSemanticClassWithDark('info', 'bg', 50, 950)} ${getSemanticClassWithDark('info', 'border', 200, 800)}`}>
        {uiInfoLoading ? (
          <div className="flex items-center gap-2">
            <Spinner size="sm" variant="primary" />
            <span className={`text-sm ${getSemanticClass('info', 'text', 700)}`}>
              {t('common.loading') || 'Cargando información...'}
            </span>
          </div>
        ) : uiInfoError ? (
          <Alert variant="error">
            {uiInfoError}
          </Alert>
        ) : (
          <div className="flex items-center justify-between">
            <div>
              <h2 className={`text-sm font-medium ${getSemanticClassWithDark('info', 'text', 900, 100)}`}>
                📊 {t('ui.data_status') || 'Estado de los datos UI'}
              </h2>
              <p className={`text-sm ${getSemanticClassWithDark('info', 'text', 800, 300)}`}>
                {uiInfo && uiInfo.total_records ? uiInfo.total_records.toLocaleString() : 'N/D'} {t('common.records') || 'registros'} {t('ui.available') || 'disponibles'}
                {uiInfo && uiInfo.date_range && (
                  <span> • {t('common.period') || 'Período'}: {uiInfo.date_range.min_date} a {uiInfo.date_range.max_date}</span>
                )}
              </p>
            </div>
            {uiInfo && uiInfo.latest_ui && (
              <div className="text-right">
                <div className={`text-sm ${getSemanticClassWithDark('info', 'text', 700, 300)}`}>
                  {t('ui.latest_value') || 'Último valor disponible'}:
                </div>
                <div className={`text-lg font-semibold ${getSemanticClassWithDark('info', 'text', 900, 100)}`}>
                  {formatUIValue(uiInfo.latest_ui.value)} • {uiInfo.latest_ui.date}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
      {/* Formulario de búsqueda y resultados - Layout de una columna */}
      <div className="space-y-6">
        {/* Panel de búsqueda - ancho completo */}
        <Card>
          <CardBody>
            <SearchForm onSearch={handleSearch} isLoading={searchLoading} />
          </CardBody>
        </Card>
        
        {/* Panel de resultados - ancho completo */}
        <Card>
          <CardBody>
            <ResultsDisplay results={results} searchType={searchType} isLoading={searchLoading} />
          </CardBody>
        </Card>
      </div>
    </div>
  );
};

export default UIPanel;

