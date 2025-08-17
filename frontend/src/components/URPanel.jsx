import React from 'react';
import URSearchForm from './URSearchForm';
import URResultsDisplay from './URResultsDisplay';
import urService from '../services/urService';
import { useI18n } from '../contexts/I18nContext';
import Card, { CardBody } from './ui/Card';

const URPanel = ({ refreshKey }) => {
  const { t, currentLanguage } = useI18n();
  const [urInfo, setUrInfo] = React.useState({});
  const [urInfoLoading, setUrInfoLoading] = React.useState(true);
  const [urInfoError, setUrInfoError] = React.useState(null);

  // Estado para resultados de búsqueda UR
  const [results, setResults] = React.useState(null);
  const [searchLoading, setSearchLoading] = React.useState(false);
  const [searchType, setSearchType] = React.useState('single');

  const formatURValue = (value) => {
    if (value === null || value === undefined) return t('common.not_available') || 'N/D';
    return new Intl.NumberFormat('es-UY', {
      style: 'currency',
      currency: '$',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };
  
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

  const hasRequestedInfoRef = React.useRef(false);
  React.useEffect(() => {
    const fetchURInfo = async () => {
      setUrInfoLoading(true);
      setUrInfoError(null);
      try {
        const response = await urService.getInfo();
        const data = response.data || response;
        if (data && data.total_records) {
          setUrInfo(data);
        } else {
          setUrInfo({});
          setUrInfoError(t('ur.query_error') || 'Error al cargar información de UR');
        }
      } catch (err) {
        console.error('Error fetching UR info:', err);
        setUrInfo({});
        setUrInfoError(t('ur.query_error') || 'Error al cargar información de UR');
      } finally {
        setUrInfoLoading(false);
      }
    };
    if (hasRequestedInfoRef.current && !refreshKey) return; // evita doble fetch StrictMode inicial
    hasRequestedInfoRef.current = true;
    fetchURInfo();
  }, [refreshKey, t, currentLanguage]);

  // Cargar automáticamente el último valor de UR cuando la info esté disponible.
  // Usamos un ref para evitar llamadas duplicadas en StrictMode sin bloquear refrescos manuales.
  const loadedLatestRef = React.useRef(false);
  React.useEffect(() => {
    const loadLatestUR = async () => {
      if (!urInfoLoading && urInfo.latest_value && !loadedLatestRef.current) {
        try {
          setSearchLoading(true);
          setResults(null);
          setSearchType('single');
          const { year, month } = urInfo.latest_value;
          const response = await urService.getByYearMonth(year, month);
          setResults(response);
        } catch (err) {
          console.error('Error loading latest UR:', err);
          setResults({
            success: false,
            message: t('ur.query_error') || 'Error al cargar últimos valores de UR'
          });
        } finally {
          setSearchLoading(false);
          loadedLatestRef.current = true;
        }
      }
    };
    // Si llega un refreshKey forzamos la recarga del último valor
    if (refreshKey) {
      loadedLatestRef.current = false;
    }
    loadLatestUR();
  }, [urInfo, urInfoLoading, t, refreshKey]);

  // Función para buscar valores de UR
  const handleSearch = async (params) => {
    setSearchLoading(true);
    setResults(null);
    setSearchType(params.searchType || params.type || 'single');
    try {
      let response;
      if ((params.searchType || params.type) === 'range') {
        response = await urService.getByRange(
          params.startYear, 
          params.startMonth,
          params.endYear,
          params.endMonth
        );
      } else if (params.month) {
        response = await urService.getByYearMonth(params.year, params.month);
      } else {
        response = await urService.getByYear(params.year);
      }
      setResults(response);
    } catch (err) {
      console.error('UR search error:', err);
      setResults({ success: false, message: t('ur.query_error') || 'Error al consultar valores de UR' });
    } finally {
      setSearchLoading(false);
    }
  };


  return (
    <div>
      {/* Panel azul de estado de datos UR */}
  <div className="mb-6 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-xl p-4">
        {urInfoLoading ? (
          <span className="text-blue-700 text-sm">{t('common.loading') || 'Cargando información...'}</span>
        ) : urInfoError ? (
          <span className="text-red-600 text-sm">{urInfoError}</span>
        ) : (
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-medium text-blue-900 dark:text-blue-100">
                📊 Estado de los datos UR
              </h2>
              <p className="text-sm text-blue-800 dark:text-blue-100/90">
                {urInfo && urInfo.total_records ? urInfo.total_records.toLocaleString() : 'N/D'} {t('ur.records') || 'registros'} disponibles
                {urInfo && urInfo.year_range && (
                  <span> • {t('common.period') || 'Período'}: {urInfo.year_range.min_year} a {urInfo.year_range.max_year}</span>
                )}
              </p>
            </div>
            {urInfo && urInfo.latest_value && (
              <div className="text-right">
                <div className="text-sm text-blue-700 dark:text-blue-100">{t('ur.latest_value') || 'Último valor disponible'}:</div>
                <div className="text-lg font-semibold text-blue-900 dark:text-white">
                  {formatURValue(urInfo.latest_value.value)} • {formatPeriod(urInfo.latest_value.year, urInfo.latest_value.month)}
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
            <URSearchForm onSearch={handleSearch} isLoading={searchLoading} />
          </CardBody>
        </Card>
        <Card>
          <CardBody>
            <URResultsDisplay results={results} searchType={searchType} isLoading={searchLoading} />
          </CardBody>
        </Card>
      </div>
    </div>
  );
};

export default URPanel;
