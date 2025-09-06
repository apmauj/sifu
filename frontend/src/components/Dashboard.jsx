import React, { useState, useEffect } from 'react';
import healthService from '../services/healthService';
import performanceService from '../services/performanceService';
import Card, { CardBody } from './ui/Card';
import { useI18n } from '../contexts/I18nContext';

const Dashboard = ({ isOpen, onClose }) => {
  const { t, translateBackendMessage } = useI18n();
  const [healthData, setHealthData] = useState(null);
  const [performanceData, setPerformanceData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('health');
  const controllersRef = React.useRef({});

  useEffect(() => {
    if (!isOpen) return;
    fetchHealthData();
    // No cargar performance aún; esperar a que el usuario active la pestaña
  }, [isOpen]);

  // Cargar performance de forma lazy cuando el usuario va a esa pestaña
  useEffect(() => {
    if (!isOpen) return;
    if (activeTab === 'performance' && !performanceData) {
      fetchPerformanceData();
    }
    // Al cambiar de pestaña, cancela requests en vuelo de la otra pestaña
    return () => {
      // cancelar cualquier fetch en curso
      Object.values(controllersRef.current).forEach((c) => c?.abort?.());
      controllersRef.current = {};
    };
  }, [activeTab, isOpen]);

  const fetchHealthData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await healthService.getAdvancedHealth();
      setHealthData(data);
    } catch (err) {
  setError(t('dashboard.error_loading_health') || 'Failed to load health data');
      console.error('Error fetching health data:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchPerformanceData = async () => {
    try {
      // Crear AbortControllers por request para poder cancelarlos al cambiar de pestaña
      const c1 = new AbortController();
      const c2 = new AbortController();
      const c3 = new AbortController();
      const c4 = new AbortController();
      controllersRef.current = { c1, c2, c3, c4 };

      const [budgets, status, throughputResp, serviceStatus] = await Promise.all([
        performanceService.getBudgets(c1.signal),
        performanceService.getBudgetStatus(c2.signal),
        performanceService.getThroughput(c3.signal),
        performanceService.getServiceStatus(c4.signal).catch(() => null)
      ]);

      // Normalizar definiciones y estado
      const defsArray = Array.isArray(budgets?.budgets)
        ? budgets.budgets
        : Object.values(budgets?.budgets || {});
      const statusMap = status?.budget_status || {};
      const statusEntries = Object.entries(statusMap);

      // Mezclar por nombre (cuando existan ambos); si no hay defs, usar sólo status
      const byName = new Map(defsArray.map((d) => [d.name, d]));
      const merged = statusEntries.length > 0
        ? statusEntries.map(([name, st]) => {
            const def = byName.get(name) || {};
            return {
              name,
              type: def.type || st.type,
              target: def.target_value ?? st.target,
              warning_threshold: def.warning_threshold ?? st.warning_threshold,
              critical_threshold: def.critical_threshold ?? st.critical_threshold,
              window_minutes: def.window_minutes,
              description: def.description,
              enabled: def.enabled,
              current_value: st.current,
              status: st.status,
            };
          })
        : defsArray; // si no hay status aún, mostrar definiciones sin estado

      // Resumen de estado
      const totals = statusEntries.reduce(
        (acc, [, st]) => {
          acc.total_budgets += 1;
          const s = (st.status || '').toLowerCase();
          if (s === 'healthy') acc.healthy_budgets += 1;
          else if (s === 'warning') acc.warning_budgets += 1;
          else if (s === 'critical') acc.critical_budgets += 1;
          return acc;
        },
        { total_budgets: 0, healthy_budgets: 0, warning_budgets: 0, critical_budgets: 0 }
      );

      const throughput = throughputResp?.throughput || throughputResp || null;
      setPerformanceData({
        budgets: merged,
        status: totals,
        throughput,
        serviceStatus
      });
    } catch (err) {
      console.error('Error fetching performance data:', err);
      // Don't set error for performance data, just log it
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
        return 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800';
      case 'warning':
        return 'text-yellow-600 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800';
      case 'critical':
        return 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800';
      default:
        return 'text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-900/20 border-gray-200 dark:border-gray-800';
    }
  };

  const getStatusIcon = (status) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
        return '✅';
      case 'warning':
        return '⚠️';
      case 'critical':
        return '❌';
      default:
        return '❓';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 dark:bg-black dark:bg-opacity-70 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{t('dashboard.title') || 'Dashboard de Monitoreo'}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:text-gray-300 dark:hover:text-gray-100 text-2xl"
          >
            ×
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="px-6 pt-4">
          <div className="flex space-x-1 bg-gray-100 dark:bg-gray-800 p-1 rounded-lg">
            <button
              onClick={() => setActiveTab('health')}
              className={`flex-1 py-2 px-4 text-sm font-medium rounded-md transition-colors ${
                activeTab === 'health'
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              🏥 {t('dashboard.tab_health') || 'Salud del Sistema'}
            </button>
            <button
              onClick={() => setActiveTab('performance')}
              className={`flex-1 py-2 px-4 text-sm font-medium rounded-md transition-colors ${
                activeTab === 'performance'
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              📊 {t('dashboard.tab_performance') || 'Presupuestos de Rendimiento'}
            </button>
          </div>
        </div>

        <div className="p-6">
          {activeTab === 'health' && (
            <>
        {loading && (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 dark:border-blue-400 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-300">{t('dashboard.loading_health') || 'Cargando datos de salud...'}</p>
                </div>
              )}

              {error && (
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6">
                  <p className="text-red-800 dark:text-red-200">{error}</p>
                </div>
              )}

              {healthData && (
                <div className="space-y-6">
                  {/* Estado General */}
                  <Card>
                    <CardBody>
                      <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
                        <span className="text-lg">🚀</span>
                        {t('dashboard.general_status.title') || 'Estado General del Sistema'}
                        <span
                          className="text-xs text-gray-400 cursor-help"
                          title={t('dashboard.tooltips.general_status') || 'Resumen agregado del estado actual de todos los checks'}
                        >ℹ️</span>
                      </h3>
                      <div className="mb-4 grid grid-cols-1 md:grid-cols-2 gap-4 items-start">
                        <div className="flex items-center gap-3 flex-wrap">
                          <span className="text-3xl">
                            {healthData.status === 'healthy' ? '✅' :
                              healthData.status === 'warning' ? '⚠️' :
                              healthData.status === 'critical' ? '❌' : '❓'}
                          </span>
                          <div className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium border ${
                            healthData.status === 'healthy' ? 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800' :
                              healthData.status === 'warning' ? 'text-yellow-600 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800' :
                                healthData.status === 'critical' ? 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800' :
                                  'text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-900/20 border-gray-200 dark:border-gray-800'
                          }`}>
                            {healthData.status === 'healthy' ? (t('dashboard.general_status.healthy') || 'Sistema Saludable') :
                              healthData.status === 'warning' ? (t('dashboard.general_status.warning') || 'Sistema con Advertencias') :
                                healthData.status === 'critical' ? (t('dashboard.general_status.critical') || 'Sistema Crítico') :
                                  (t('dashboard.general_status.unknown') || 'Estado Desconocido')}
                          </div>
                        </div>
                        {healthData.timestamp && (
                          <div className="flex md:justify-end items-center gap-1 text-sm text-gray-500 dark:text-gray-400 md:text-right">
                            <span className="text-lg">🕒</span>
                            <span className="whitespace-nowrap">{(t('dashboard.general_status.last_update_prefix') || 'Última actualización:')}</span>
                            <time className="truncate" dateTime={new Date(healthData.timestamp).toISOString()}>{new Date(healthData.timestamp).toLocaleString()}</time>
                          </div>
                        )}
                      </div>
                    </CardBody>
                  </Card>

                  {/* Detalles de Checks */}
                  {healthData.checks && Array.isArray(healthData.checks) && (
                    <div>
                      <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
                        <span>{t('dashboard.checks.details_title') || 'Detalles de Verificaciones'}</span>
                        <span className="text-xs text-gray-400 cursor-help" title={t('dashboard.tooltips.checks_section') || 'Listado detallado de verificaciones individuales'}>ℹ️</span>
                      </h3>
                      <div className="grid gap-4">
                        {healthData.checks.map((checkData, index) => (
                          <Card key={index}>
                            <CardBody>
                              <div className="flex items-center justify-between mb-3">
                                <h4 className="font-medium capitalize text-gray-900 dark:text-white flex items-center gap-2">
                                  <span className="text-lg">
                                    {checkData.name === 'database' && '🗄️'}
                                    {checkData.name === 'brou_api' && '💰'}
                                    {checkData.name === 'bcu_api' && '🏦'}
                                    {checkData.name === 'system_resources' && '🖥️'}
                                    {checkData.name === 'application_metrics' && '📊'}
                                    {checkData.name === 'brou_cache' && '🗄️'}
                                  </span>
                                  {/* Translate known check names; fallback to formatted name */}
                                  {(
                                    checkData.name === 'database' ? (t('dashboard.checks.names.database') || 'Database') :
                                    checkData.name === 'brou_api' ? (t('dashboard.checks.names.brou_api') || 'Brou Api') :
                                    checkData.name === 'bcu_api' ? (t('dashboard.checks.names.bcu_api') || 'Bcu Api') :
                                    checkData.name === 'system_resources' ? (t('dashboard.checks.names.system_resources') || 'System Resources') :
                                    checkData.name === 'application_metrics' ? (t('dashboard.checks.names.application_metrics') || 'Application Metrics') :
                                    checkData.name === 'brou_cache' ? (t('dashboard.checks.names.brou_cache') || 'Brou Cache') :
                                    checkData.name.replace(/_/g, ' ')
                                  )}
                                  <span
                                    className="text-[10px] text-gray-400 cursor-help"
                                    title={
                                      (checkData.name === 'database' && (t('dashboard.tooltips.database_check') || 'Conexión y conteos de registros')) ||
                                      (checkData.name === 'brou_api' && (t('dashboard.tooltips.brou_api_check') || 'Disponibilidad de API BROU')) ||
                                      (checkData.name === 'bcu_api' && (t('dashboard.tooltips.bcu_api_check') || 'Disponibilidad de API BCU')) ||
                                      (checkData.name === 'brou_cache' && (t('dashboard.tooltips.brou_cache_check') || 'Estado de frescura de caché BROU')) ||
                                      (checkData.name === 'system_resources' && (t('dashboard.tooltips.system_resources_check') || 'Uso de CPU y memoria')) ||
                                      (checkData.name === 'application_metrics' && (t('dashboard.tooltips.application_metrics_check') || 'Métricas internas de la app')) ||
                                      undefined
                                    }
                                  >ℹ️</span>
                                </h4>
                                <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(checkData.status)}`} title={t('dashboard.tooltips.status_badge') || 'Estado actual del check'}>
                                  {getStatusIcon(checkData.status)} {t(`dashboard.status.${checkData.status}`) || checkData.status}
                                </div>
                              </div>

                              {checkData.message && (
                                <p className="text-sm text-gray-600 dark:text-gray-300 mb-3">{translateBackendMessage(checkData.message) === checkData.message && checkData.message === 'Database connection successful'
                                  ? (t('dashboard.checks.database_ok') || 'Conexión a base de datos exitosa')
                                  : translateBackendMessage(checkData.message)}</p>
                              )}

                              {/* Database Details */}
                              {checkData.name === 'database' && checkData.details && (
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                                  <div className="text-center p-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                                    <div className="text-xl font-bold text-blue-600 dark:text-blue-400">{checkData.details.ui_records?.toLocaleString()}</div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">{t('dashboard.checks.ui_records') || 'UI Records'}</div>
                                  </div>
                                  <div className="text-center p-2 bg-green-50 dark:bg-green-900/20 rounded-lg">
                                    <div className="text-xl font-bold text-green-600 dark:text-green-400">{checkData.details.ur_records?.toLocaleString()}</div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">{t('dashboard.checks.ur_records') || 'UR Records'}</div>
                                  </div>
                                  <div className="text-center p-2 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                                    <div className="text-xl font-bold text-purple-600 dark:text-purple-400">{checkData.details.brou_records?.toLocaleString()}</div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">{t('dashboard.checks.brou_records') || 'BROU Records'}</div>
                                  </div>
                                  <div className="text-center p-2 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                                    <div className="text-xl font-bold text-orange-600 dark:text-orange-400">{checkData.details.total_records?.toLocaleString()}</div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">{t('dashboard.checks.total_records') || 'Total'}</div>
                                  </div>
                                </div>
                              )}

                              {/* API Details */}
                              {(checkData.name === 'brou_api' || checkData.name === 'bcu_api') && checkData.details && (
                                <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-3">
                                  <div className="text-center p-2 bg-green-50 dark:bg-green-900/20 rounded-lg">
                                    <div className="text-xl font-bold text-green-600 dark:text-green-400">{checkData.details.currencies_count}</div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">{t('dashboard.checks.currencies') || 'Monedas'}</div>
                                  </div>
                                  <div className="text-center p-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                                    <div className="text-lg font-bold text-blue-600 dark:text-blue-400">
                                      {checkData.details.is_live ? `🟢 ${t('dashboard.labels.live') || 'Live'}` : `🟡 ${t('dashboard.labels.cache') || 'Cache'}`}
                                    </div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">{t('dashboard.checks.state') || 'Estado'}</div>
                                  </div>
                                  {checkData.details.source_type && (
                                    <div className="text-center p-2 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                                      <div className="text-sm font-bold text-purple-600 dark:text-purple-400 capitalize">
                                        {checkData.details.source_type}
                                      </div>
                                      <div className="text-xs text-gray-500 dark:text-gray-400">{t('dashboard.checks.source') || 'Fuente'}</div>
                                    </div>
                                  )}
                                </div>
                              )}

                              {/* System Resources Details */}
                              {checkData.name === 'system_resources' && checkData.details && (
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                                  <div className="text-center p-2 bg-red-50 dark:bg-red-900/20 rounded-lg">
                                    <div className="text-xl font-bold text-red-600 dark:text-red-400">{checkData.details.cpu_percent?.toFixed(1)}%</div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">{t('dashboard.system_info.cpu') || 'CPU'}</div>
                                  </div>
                                  <div className="text-center p-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                                    <div className="text-xl font-bold text-blue-600 dark:text-blue-400">{checkData.details.memory_percent?.toFixed(1)}%</div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">{t('dashboard.system_info.memory') || 'Memoria'}</div>
                                  </div>
                                  <div className="text-center p-2 bg-green-50 dark:bg-green-900/20 rounded-lg">
                                    <div className="text-lg font-bold text-green-600 dark:text-green-400">{(checkData.details.memory_used_mb / 1024)?.toFixed(1)} GB</div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">{t('dashboard.system_info.used') || 'Usada'}</div>
                                  </div>
                                  <div className="text-center p-2 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                                    <div className="text-lg font-bold text-purple-600 dark:text-purple-400">{(checkData.details.memory_total_mb / 1024)?.toFixed(1)} GB</div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">{t('dashboard.system_info.total') || 'Total'}</div>
                                  </div>
                                </div>
                              )}

                              {/* Application Metrics Details */}
                              {checkData.name === 'application_metrics' && checkData.details && (
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                                  <div className="text-center p-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                                    <div className="text-xl font-bold text-blue-600 dark:text-blue-400">{checkData.details.total_requests?.toLocaleString()}</div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">{t('dashboard.application_metrics.total_requests') || 'Total Requests'}</div>
                                  </div>
                                  <div className="text-center p-2 bg-red-50 dark:bg-red-900/20 rounded-lg">
                                    <div className="text-xl font-bold text-red-600 dark:text-red-400">{checkData.details.error_rate_percent?.toFixed(1)}%</div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">{t('dashboard.application_metrics.error_rate') || 'Error Rate'}</div>
                                  </div>
                                  <div className="text-center p-2 bg-green-50 dark:bg-green-900/20 rounded-lg">
                                    <div className="text-lg font-bold text-green-600 dark:text-green-400">{checkData.details.avg_response_time_ms?.toFixed(0)}ms</div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">{t('dashboard.application_metrics.avg_response') || 'Avg Response'}</div>
                                  </div>
                                  <div className="text-center p-2 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                                    <div className="text-lg font-bold text-purple-600 dark:text-purple-400">{Math.floor(checkData.details.uptime_seconds / 3600)}h</div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">{t('dashboard.application_metrics.uptime') || 'Uptime'}</div>
                                  </div>
                                </div>
                              )}

                              {/* Removed technical data details panel for compactness */}
                            </CardBody>
                          </Card>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Información del Sistema */}
                  {healthData.system_info && (
                    <Card>
                      <CardBody>
                        <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
                          <span className="text-lg">🖥️</span>
                          {t('dashboard.system_info.title') || 'Información del Sistema'}
                          <span className="text-xs text-gray-400 cursor-help" title={t('dashboard.tooltips.system_resources_check') || 'Uso de recursos del servidor'}>ℹ️</span>
                        </h3>

                        {healthData.system_info.error ? (
                          <div className="text-center py-6">
                            <div className="text-yellow-600 dark:text-yellow-400 mb-2 text-2xl">⚠️</div>
                            <p className="text-sm text-gray-600 dark:text-gray-300 font-medium">
                              {t('dashboard.system_info.unavailable') || 'Monitoreo de recursos no disponible'}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                              {healthData.system_info.error}
                            </p>
                          </div>
                        ) : (
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div className="text-center p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
                              <div className="text-2xl font-bold text-red-600 dark:text-red-400 mb-1">
                                {healthData.system_info.cpu_percent?.toFixed(1)}%
                              </div>
                              <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1 mb-2">
                                <span className="text-lg">🔥</span>
                                {t('dashboard.system_info.cpu_usage') || 'CPU Usage'}
                              </div>
                              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                                <div
                                  className="bg-red-600 dark:bg-red-400 h-2 rounded-full transition-all duration-300"
                                  style={{ width: `${Math.min(healthData.system_info.cpu_percent, 100)}%` }}
                                ></div>
                              </div>
                            </div>

                            <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                              <div className="text-2xl font-bold text-blue-600 dark:text-blue-400 mb-1">
                                {healthData.system_info.memory_percent?.toFixed(1)}%
                              </div>
                              <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1 mb-2">
                                <span className="text-lg">💾</span>
                                {t('dashboard.system_info.memory_usage') || 'Memory Usage'}
                              </div>
                              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                                <div
                                  className="bg-blue-600 dark:bg-blue-400 h-2 rounded-full transition-all duration-300"
                                  style={{ width: `${healthData.system_info.memory_percent}%` }}
                                ></div>
                              </div>
                            </div>

                            <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                              <div className="text-xl font-bold text-green-600 dark:text-green-400 mb-1">
                                {(healthData.system_info.memory_used_mb / 1024)?.toFixed(1)} GB
                              </div>
                              <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                                <span className="text-lg">📈</span>
                                {t('dashboard.system_info.memory_used') || 'Memory Used'}
                              </div>
                            </div>

                            <div className="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                              <div className="text-xl font-bold text-purple-600 dark:text-purple-400 mb-1">
                                {(healthData.system_info.memory_total_mb / 1024)?.toFixed(1)} GB
                              </div>
                              <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                                <span className="text-lg">💿</span>
                                {t('dashboard.system_info.memory_total') || 'Memory Total'}
                              </div>
                            </div>
                          </div>
                        )}
                      </CardBody>
                    </Card>
                  )}

                  {/* Métricas de Rendimiento */}
                  {healthData.uptime_seconds && (
                    <Card>
                      <CardBody>
                        <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
                          <span className="text-lg">⚡</span>
                          {t('dashboard.performance_metrics.title') || 'Métricas de Rendimiento'}
                          <span className="text-xs text-gray-400 cursor-help" title={t('dashboard.tooltips.performance_metrics') || 'Métricas agregadas de rendimiento'}>ℹ️</span>
                        </h3>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                          <div className="text-center p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg border border-indigo-200 dark:border-indigo-800">
                            <div className="text-2xl font-bold text-indigo-600 dark:text-indigo-400 mb-1">
                              {Math.floor(healthData.uptime_seconds / 86400)}d {Math.floor((healthData.uptime_seconds % 86400) / 3600)}h
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                              <span className="text-lg">⏱️</span>
                              {t('dashboard.performance_metrics.uptime_total') || 'Uptime Total'}
                            </div>
                          </div>
                          <div className="text-center p-4 bg-teal-50 dark:bg-teal-900/20 rounded-lg border border-teal-200 dark:border-teal-800">
                            <div className="text-2xl font-bold text-teal-600 dark:text-teal-400 mb-1">
                              {healthData.avg_response_time_ms?.toFixed(0) || 'N/A'}ms
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                              <span className="text-lg">🚀</span>
                              {t('dashboard.performance_metrics.response_time') || 'Tiempo de Respuesta'}
                            </div>
                          </div>
                          <div className="text-center p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg border border-orange-200 dark:border-orange-800">
                            <div className="text-2xl font-bold text-orange-600 dark:text-orange-400 mb-1">
                              {healthData.total_requests?.toLocaleString() || 'N/A'}
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                              <span className="text-lg">📊</span>
                              {t('dashboard.performance_metrics.total_requests') || 'Total de Solicitudes'}
                            </div>
                          </div>
                        </div>
                      </CardBody>
                    </Card>
                  )}

                  {/* Estadísticas Generales */}
                  <Card>
                    <CardBody>
                      <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
                        <span className="text-lg">📊</span>
                        {t('dashboard.statistics.title') || 'Estadísticas Generales'}
                      </h3>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="text-center p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                          <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">{healthData.total_checks}</div>
                          <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                            <span className="text-lg">🔍</span>
                            {t('dashboard.statistics.total_checks') || 'Total de verificaciones'}
                          </div>
                        </div>
                        <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                          <div className="text-3xl font-bold text-green-600 dark:text-green-400 mb-1">{healthData.healthy_checks}</div>
                          <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                            <span className="text-lg">✅</span>
                            {t('dashboard.statistics.healthy_checks') || 'Verificaciones saludables'}
                          </div>
                        </div>
                        <div className="text-center p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                          <div className="text-3xl font-bold text-yellow-600 dark:text-yellow-400 mb-1">{healthData.warning_checks}</div>
                          <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                            <span className="text-lg">⚠️</span>
                            {t('dashboard.statistics.warning_checks') || 'Verificaciones con advertencia'}
                          </div>
                        </div>
                        <div className="text-center p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
                          <div className="text-3xl font-bold text-red-600 dark:text-red-400 mb-1">{healthData.critical_checks}</div>
                          <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                            <span className="text-lg">❌</span>
                            {t('dashboard.statistics.critical_checks') || 'Verificaciones críticas'}
                          </div>
                        </div>
                      </div>
                    </CardBody>
                  </Card>
                </div>
              )}
            </>
          )}

          {activeTab === 'performance' && (
            <div className="space-y-6">
              {/* Performance Budgets Overview */}
              <Card>
                <CardBody>
                    <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
                      <span className="text-lg">📊</span>
                      {t('dashboard.performance_budgets.title') || 'Presupuestos de Rendimiento'}
                      <span className="text-xs text-gray-400 cursor-help" title={t('dashboard.tooltips.performance_budgets') || 'Objetivos y umbrales de salud para métricas clave'}>ℹ️</span>
                    </h3>
                  
                  {performanceData?.budgets && performanceData.budgets.length > 0 ? (
                    <div className="grid gap-4">
                      {performanceData.budgets.map((budget, index) => (
                        <Card key={index} className="border-l-4 border-blue-500">
                          <CardBody>
                            <div className="flex items-center justify-between mb-3">
                              <h4 className="font-medium text-gray-900 dark:text-white flex items-center gap-2">
                                <span className="text-lg">
                                  {budget.name === 'api_latency_budget' && '⚡'}
                                  {budget.name === 'throughput_budget' && '🚀'}
                                  {budget.name === 'error_rate_budget' && '⚠️'}
                                  {budget.name === 'availability_budget' && '🟢'}
                                </span>
                                {budget.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                              </h4>
                              <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${
                                budget.status === 'healthy' ? 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800' :
                                budget.status === 'warning' ? 'text-yellow-600 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800' :
                                budget.status === 'critical' ? 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800' :
                                'text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-900/20 border-gray-200 dark:border-gray-800'
                              }`}>
                                {budget.status === 'healthy' ? (t('dashboard.performance_budgets.status.healthy') || '✅ Saludable') :
                                 budget.status === 'warning' ? (t('dashboard.performance_budgets.status.warning') || '⚠️ Advertencia') :
                                 budget.status === 'critical' ? (t('dashboard.performance_budgets.status.critical') || '❌ Crítico') :
                                 (t('dashboard.performance_budgets.status.unknown') || '❓ Desconocido')}
                              </div>
                            </div>

                            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                              <div className="text-center p-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                                <div className="text-lg font-bold text-blue-600 dark:text-blue-400">{budget.target}</div>
                                <div className="text-xs text-gray-500 dark:text-gray-400">{t('dashboard.performance_budgets.labels.target') || 'Objetivo'}</div>
                              </div>
                              <div className="text-center p-2 bg-green-50 dark:bg-green-900/20 rounded-lg">
                                <div className="text-lg font-bold text-green-600 dark:text-green-400">{budget.warning_threshold}</div>
                                <div className="text-xs text-gray-500 dark:text-gray-400">{t('dashboard.performance_budgets.labels.warning_threshold') || 'Advertencia'}</div>
                              </div>
                              <div className="text-center p-2 bg-red-50 dark:bg-red-900/20 rounded-lg">
                                <div className="text-lg font-bold text-red-600 dark:text-red-400">{budget.critical_threshold}</div>
                                <div className="text-xs text-gray-500 dark:text-gray-400">{t('dashboard.performance_budgets.labels.critical_threshold') || 'Crítico'}</div>
                              </div>
                              <div className="text-center p-2 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                                <div className="text-lg font-bold text-purple-600 dark:text-purple-400">{budget.current_value || 'N/A'}</div>
                                <div className="text-xs text-gray-500 dark:text-gray-400">{t('dashboard.performance_budgets.labels.current') || 'Actual'}</div>
                              </div>
                            </div>

                            {budget.message && (
                              <p className="text-sm text-gray-600 dark:text-gray-300">{budget.message}</p>
                            )}
                          </CardBody>
                        </Card>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                        <div className="text-gray-400 dark:text-gray-500 mb-2 text-4xl">📊</div>
                        <p className="text-gray-600 dark:text-gray-300 mb-2">{t('dashboard.performance_budgets.no_budgets') || 'No se encontraron presupuestos de rendimiento configurados'}</p>
                      {performanceData?.serviceStatus && (
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {(t('dashboard.performance_budgets.service_status_prefix') || 'Estado del servicio:')} {performanceData.serviceStatus.status}. {performanceData.serviceStatus.message}
                        </p>
                      )}
                    </div>
                  )}
                </CardBody>
              </Card>

              {/* Throughput Metrics */}
              {performanceData?.throughput && (
                <Card>
                  <CardBody>
                    <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
                      <span className="text-lg">🚀</span>
                      {t('dashboard.throughput_metrics.title') || 'Métricas de Throughput'}
                      <span className="text-xs text-gray-400 cursor-help" title={t('dashboard.tooltips.throughput_metrics') || 'Rendimiento reciente de solicitudes'}>ℹ️</span>
                    </h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                        <div className="text-2xl font-bold text-blue-600 dark:text-blue-400 mb-1">
                          {performanceData.throughput?.requests_per_minute ?? 'N/A'}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                          <span className="text-lg">📈</span>
                          {t('dashboard.throughput_metrics.requests_per_minute') || 'Solicitudes/min'}
                        </div>
                      </div>
                      <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                        <div className="text-2xl font-bold text-green-600 dark:text-green-400 mb-1">
                          {performanceData.throughput?.avg_response_time_ms?.toFixed?.(0) ?? 'N/A'}ms
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                          <span className="text-lg">⚡</span>
                          {t('dashboard.throughput_metrics.avg_response_time') || 'Tiempo de Respuesta'}
                        </div>
                      </div>
                      <div className="text-center p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                        <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400 mb-1">
                          {performanceData.throughput?.error_rate_percent?.toFixed?.(2) ?? 'N/A'}%
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                          <span className="text-lg">⚠️</span>
                          {t('dashboard.throughput_metrics.error_rate') || 'Tasa de Error'}
                        </div>
                      </div>
                      <div className="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                        <div className="text-2xl font-bold text-purple-600 dark:text-purple-400 mb-1">
                          {performanceData.throughput?.uptime_percent?.toFixed?.(2) ?? 'N/A'}%
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                          <span className="text-lg">🟢</span>
                          {t('dashboard.throughput_metrics.uptime') || 'Disponibilidad'}
                        </div>
                      </div>
                    </div>
                  </CardBody>
                </Card>
              )}

              {/* Performance Status Summary */}
              {performanceData?.status && (
                <Card>
                  <CardBody>
                    <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
                      <span className="text-lg">📋</span>
                      {t('dashboard.status_summary.title') || 'Resumen de Estado'}
                      <span className="text-xs text-gray-400 cursor-help" title={t('dashboard.tooltips.status_summary') || 'Conteo de presupuestos por estado'}>ℹ️</span>
                    </h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="text-center p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                        <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
                          {performanceData.status.total_budgets || 0}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                          <span className="text-lg">📊</span>
                          {t('dashboard.status_summary.total_budgets') || 'Total Presupuestos'}
                        </div>
                      </div>
                      <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                        <div className="text-3xl font-bold text-green-600 dark:text-green-400 mb-1">
                          {performanceData.status.healthy_budgets || 0}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                          <span className="text-lg">✅</span>
                          {t('dashboard.status_summary.healthy') || 'Saludables'}
                        </div>
                      </div>
                      <div className="text-center p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                        <div className="text-3xl font-bold text-yellow-600 dark:text-yellow-400 mb-1">
                          {performanceData.status.warning_budgets || 0}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                          <span className="text-lg">⚠️</span>
                          {t('dashboard.status_summary.warning') || 'Advertencias'}
                        </div>
                      </div>
                      <div className="text-center p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
                        <div className="text-3xl font-bold text-red-600 dark:text-red-400 mb-1">
                          {performanceData.status.critical_budgets || 0}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                          <span className="text-lg">❌</span>
                          {t('dashboard.status_summary.critical') || 'Críticos'}
                        </div>
                      </div>
                    </div>
                  </CardBody>
                </Card>
              )}
            </div>
          )}
        </div>

        <div className="flex justify-end p-6 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 mr-2"
          >
            {t('dashboard.actions.close') || 'Cerrar'}
          </button>
          <button
            onClick={() => {
              fetchHealthData();
              if (activeTab === 'performance') {
                fetchPerformanceData();
              }
            }}
            className="px-4 py-2 bg-blue-600 dark:bg-blue-500 text-white rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600"
          >
            {t('dashboard.actions.refresh') || 'Actualizar'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
