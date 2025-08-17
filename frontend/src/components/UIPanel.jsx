import React from 'react';
import SearchForm from './SearchForm';
import ResultsDisplay from './ResultsDisplay';
import uiService from '../services/api';
import { useI18n } from '../contexts/I18nContext';
import Card, { CardBody } from './ui/Card';
import { CURRENCY, CURRENCY_LOCALE } from '../constants';

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

  // Cargar automáticamente los últimos valores de UI al inicializar
  const loadedLatestRef = React.useRef(false);
  React.useEffect(() => {
    const loadLatestUI = async () => {
      if (!uiInfoLoading && uiInfo.latest_ui && !loadedLatestRef.current) {
        try {
          setSearchLoading(true);
          setResults(null);
          setSearchType('single');
          const response = await uiService.getByDate(uiInfo.latest_ui.date);
          setResults(response);
        } catch (err) {
          console.error('Error loading latest UI:', err);
          setResults({
            success: false,
            message: t('errors.search_data_error') || 'Error al cargar últimos valores de UI'
          });
        } finally {
          setSearchLoading(false);
          loadedLatestRef.current = true;
        }
      }
    };
    if (refreshKey) {
      loadedLatestRef.current = false; // permitir recarga tras refresh manual
    }
    loadLatestUI();
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
      {/* Panel azul de estado de datos UI */}
  <div className="mb-6 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-xl p-4">
        {uiInfoLoading ? (
          <span className="text-blue-700 text-sm">{t('common.loading') || 'Cargando información...'}</span>
        ) : uiInfoError ? (
          <span className="text-red-600 text-sm">{uiInfoError}</span>
        ) : (
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-medium text-blue-900 dark:text-blue-100">
                📊 {t('ui.data_status') || 'Estado de los datos UI'}
              </h2>
              <p className="text-sm text-blue-800 dark:text-blue-100/90">
                {uiInfo && uiInfo.total_records ? uiInfo.total_records.toLocaleString() : 'N/D'} {t('common.records') || 'registros'} {t('ui.available') || 'disponibles'}
                {uiInfo && uiInfo.date_range && (
                  <span> • {t('common.period') || 'Período'}: {uiInfo.date_range.min_date} a {uiInfo.date_range.max_date}</span>
                )}
              </p>
            </div>
            {uiInfo && uiInfo.latest_ui && (
              <div className="text-right">
                <div className="text-sm text-blue-700 dark:text-blue-100">{t('ui.latest_value') || 'Último valor disponible'}:</div>
                <div className="text-lg font-semibold text-blue-900 dark:text-white">
                  {formatUIValue(uiInfo.latest_ui.value)} • {uiInfo.latest_ui.date}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
      {/* Formulario de búsqueda y resultados */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardBody>
            <SearchForm onSearch={handleSearch} isLoading={searchLoading} />
          </CardBody>
        </Card>
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
