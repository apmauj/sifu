import React, { useState, useEffect } from 'react';
import healthService from '../services/healthService';
import performanceService from '../services/performanceService';
import Card, { CardBody } from './ui/Card';

const Dashboard = ({ isOpen, onClose }) => {
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
      setError('Failed to load health data');
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
      controllersRef.current = { c1, c2, c3 };

      const [budgets, status, throughput] = await Promise.all([
        performanceService.getBudgets(c1.signal),
        performanceService.getBudgetStatus(c2.signal),
        performanceService.getThroughput(c3.signal)
      ]);

      // El backend devuelve budgets como objeto; mapear a array para la UI
      const budgetsArray = Array.isArray(budgets?.budgets)
        ? budgets.budgets
        : Object.values(budgets?.budgets || {});

      setPerformanceData({
        budgets: budgetsArray,
        status: status,
        throughput: throughput
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
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard de Monitoreo</h2>
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
              🏥 Salud del Sistema
            </button>
            <button
              onClick={() => setActiveTab('performance')}
              className={`flex-1 py-2 px-4 text-sm font-medium rounded-md transition-colors ${
                activeTab === 'performance'
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              📊 Presupuestos de Rendimiento
            </button>
          </div>
        </div>

        <div className="p-6">
          {activeTab === 'health' && (
            <>
              {loading && (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 dark:border-blue-400 mx-auto mb-4"></div>
                  <p className="text-gray-600 dark:text-gray-300">Cargando datos de salud...</p>
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
                        Estado General del Sistema
                      </h3>
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-3">
                          <span className="text-3xl">
                            {healthData.status === 'healthy' ? '✅' :
                             healthData.status === 'warning' ? '⚠️' :
                             healthData.status === 'critical' ? '❌' : '❓'}
                          </span>
                          <div>
                            <div className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium border ${
                              healthData.status === 'healthy' ? 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800' :
                              healthData.status === 'warning' ? 'text-yellow-600 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800' :
                              healthData.status === 'critical' ? 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800' :
                              'text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-900/20 border-gray-200 dark:border-gray-800'
                            }`}>
                              {healthData.status === 'healthy' ? 'Sistema Saludable' :
                               healthData.status === 'warning' ? 'Sistema con Advertencias' :
                               healthData.status === 'critical' ? 'Sistema Crítico' :
                               'Estado Desconocido'}
                            </div>
                          </div>
                        </div>
                      </div>
                      {healthData.timestamp && (
                        <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                          <span className="text-lg">🕒</span>
                          Última actualización: {new Date(healthData.timestamp).toLocaleString()}
                        </div>
                      )}
                    </CardBody>
                  </Card>

                  {/* Detalles de Checks */}
                  {healthData.checks && Array.isArray(healthData.checks) && (
                    <div>
                      <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Detalles de Verificaciones</h3>
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
                                  </span>
                                  {checkData.name.replace(/_/g, ' ')}
                                </h4>
                                <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(checkData.status)}`}>
                                  {getStatusIcon(checkData.status)} {checkData.status}
                                </div>
                              </div>

                              {checkData.message && (
                                <p className="text-sm text-gray-600 dark:text-gray-300 mb-3">{checkData.message}</p>
                              )}

                              {/* Database Details */}
                              {checkData.name === 'database' && checkData.details && (
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                                  <div className="text-center p-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                                    <div className="text-xl font-bold text-blue-600 dark:text-blue-400">{checkData.details.ui_records?.toLocaleString()}</div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">UI Records</div>
                                  </div>
                                  <div className="text-center p-2 bg-green-50 dark:bg-green-900/20 rounded-lg">
                                    <div className="text-xl font-bold text-green-600 dark:text-green-400">{checkData.details.ur_records?.toLocaleString()}</div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">UR Records</div>
                                  </div>
                                  <div className="text-center p-2 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                                    <div className="text-xl font-bold text-purple-600 dark:text-purple-400">{checkData.details.brou_records?.toLocaleString()}</div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">BROU Records</div>
                                  </div>
                                  <div className="text-center p-2 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                                    <div className="text-xl font-bold text-orange-600 dark:text-orange-400">{checkData.details.total_records?.toLocaleString()}</div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">Total</div>
                                  </div>
                                </div>
                              )}

                              {/* API Details */}
                              {(checkData.name === 'brou_api' || checkData.name === 'bcu_api') && checkData.details && (
                                <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-3">
                                  <div className="text-center p-2 bg-green-50 dark:bg-green-900/20 rounded-lg">
                                    <div className="text-xl font-bold text-green-600 dark:text-green-400">{checkData.details.currencies_count}</div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">Monedas</div>
                                  </div>
                                  <div className="text-center p-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                                    <div className="text-lg font-bold text-blue-600 dark:text-blue-400">
                                      {checkData.details.is_live ? '🟢 Live' : '🟡 Cache'}
                                    </div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">Estado</div>
                                  </div>
                                  {checkData.details.source_type && (
                                    <div className="text-center p-2 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                                      <div className="text-sm font-bold text-purple-600 dark:text-purple-400 capitalize">
                                        {checkData.details.source_type}
                                      </div>
                                      <div className="text-xs text-gray-500 dark:text-gray-400">Fuente</div>
                                    </div>
                                  )}
                                </div>
                              )}

                              {/* System Resources Details */}
                              {checkData.name === 'system_resources' && checkData.details && (
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                                  <div className="text-center p-2 bg-red-50 dark:bg-red-900/20 rounded-lg">
                                    <div className="text-xl font-bold text-red-600 dark:text-red-400">{checkData.details.cpu_percent?.toFixed(1)}%</div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">CPU</div>
                                  </div>
                                  <div className="text-center p-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                                    <div className="text-xl font-bold text-blue-600 dark:text-blue-400">{checkData.details.memory_percent?.toFixed(1)}%</div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">Memoria</div>
                                  </div>
                                  <div className="text-center p-2 bg-green-50 dark:bg-green-900/20 rounded-lg">
                                    <div className="text-lg font-bold text-green-600 dark:text-green-400">{(checkData.details.memory_used_mb / 1024)?.toFixed(1)} GB</div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">Usada</div>
                                  </div>
                                  <div className="text-center p-2 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                                    <div className="text-lg font-bold text-purple-600 dark:text-purple-400">{(checkData.details.memory_total_mb / 1024)?.toFixed(1)} GB</div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">Total</div>
                                  </div>
                                </div>
                              )}

                              {/* Application Metrics Details */}
                              {checkData.name === 'application_metrics' && checkData.details && (
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                                  <div className="text-center p-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                                    <div className="text-xl font-bold text-blue-600 dark:text-blue-400">{checkData.details.total_requests?.toLocaleString()}</div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">Total Requests</div>
                                  </div>
                                  <div className="text-center p-2 bg-red-50 dark:bg-red-900/20 rounded-lg">
                                    <div className="text-xl font-bold text-red-600 dark:text-red-400">{checkData.details.error_rate_percent?.toFixed(1)}%</div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">Error Rate</div>
                                  </div>
                                  <div className="text-center p-2 bg-green-50 dark:bg-green-900/20 rounded-lg">
                                    <div className="text-lg font-bold text-green-600 dark:text-green-400">{checkData.details.avg_response_time_ms?.toFixed(0)}ms</div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">Avg Response</div>
                                  </div>
                                  <div className="text-center p-2 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                                    <div className="text-lg font-bold text-purple-600 dark:text-purple-400">{Math.floor(checkData.details.uptime_seconds / 3600)}h</div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">Uptime</div>
                                  </div>
                                </div>
                              )}

                              {/* Raw JSON for debugging (collapsed by default) */}
                              {checkData.details && Object.keys(checkData.details).length > 0 && (
                                <details className="mt-3">
                                  <summary className="text-xs text-gray-500 dark:text-gray-400 cursor-pointer hover:text-gray-700 dark:hover:text-gray-300">
                                    Ver datos técnicos
                                  </summary>
                                  <pre className="mt-2 text-xs text-gray-600 dark:text-gray-300 whitespace-pre-wrap bg-gray-50 dark:bg-gray-800 p-2 rounded overflow-x-auto">
                                    {JSON.stringify(checkData.details, null, 2)}
                                  </pre>
                                </details>
                              )}
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
                          Información del Sistema
                        </h3>

                        {healthData.system_info.error ? (
                          <div className="text-center py-6">
                            <div className="text-yellow-600 dark:text-yellow-400 mb-2 text-2xl">⚠️</div>
                            <p className="text-sm text-gray-600 dark:text-gray-300 font-medium">
                              Monitoreo de recursos no disponible
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
                                CPU Usage
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
                                Memory Usage
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
                                Memory Used
                              </div>
                            </div>

                            <div className="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                              <div className="text-xl font-bold text-purple-600 dark:text-purple-400 mb-1">
                                {(healthData.system_info.memory_total_mb / 1024)?.toFixed(1)} GB
                              </div>
                              <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                                <span className="text-lg">💿</span>
                                Memory Total
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
                          Métricas de Rendimiento
                        </h3>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                          <div className="text-center p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg border border-indigo-200 dark:border-indigo-800">
                            <div className="text-2xl font-bold text-indigo-600 dark:text-indigo-400 mb-1">
                              {Math.floor(healthData.uptime_seconds / 86400)}d {Math.floor((healthData.uptime_seconds % 86400) / 3600)}h
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                              <span className="text-lg">⏱️</span>
                              Uptime Total
                            </div>
                          </div>
                          <div className="text-center p-4 bg-teal-50 dark:bg-teal-900/20 rounded-lg border border-teal-200 dark:border-teal-800">
                            <div className="text-2xl font-bold text-teal-600 dark:text-teal-400 mb-1">
                              {healthData.avg_response_time_ms?.toFixed(0) || 'N/A'}ms
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                              <span className="text-lg">🚀</span>
                              Tiempo de Respuesta
                            </div>
                          </div>
                          <div className="text-center p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg border border-orange-200 dark:border-orange-800">
                            <div className="text-2xl font-bold text-orange-600 dark:text-orange-400 mb-1">
                              {healthData.total_requests?.toLocaleString() || 'N/A'}
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                              <span className="text-lg">📊</span>
                              Total de Solicitudes
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
                        Estadísticas Generales
                      </h3>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="text-center p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                          <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">{healthData.total_checks}</div>
                          <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                            <span className="text-lg">🔍</span>
                            Total de verificaciones
                          </div>
                        </div>
                        <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                          <div className="text-3xl font-bold text-green-600 dark:text-green-400 mb-1">{healthData.healthy_checks}</div>
                          <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                            <span className="text-lg">✅</span>
                            Verificaciones saludables
                          </div>
                        </div>
                        <div className="text-center p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                          <div className="text-3xl font-bold text-yellow-600 dark:text-yellow-400 mb-1">{healthData.warning_checks}</div>
                          <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                            <span className="text-lg">⚠️</span>
                            Verificaciones con advertencia
                          </div>
                        </div>
                        <div className="text-center p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
                          <div className="text-3xl font-bold text-red-600 dark:text-red-400 mb-1">{healthData.critical_checks}</div>
                          <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                            <span className="text-lg">❌</span>
                            Verificaciones críticas
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
                    Presupuestos de Rendimiento
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
                                {budget.status === 'healthy' ? '✅ Saludable' :
                                 budget.status === 'warning' ? '⚠️ Advertencia' :
                                 budget.status === 'critical' ? '❌ Crítico' :
                                 '❓ Desconocido'}
                              </div>
                            </div>

                            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                              <div className="text-center p-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                                <div className="text-lg font-bold text-blue-600 dark:text-blue-400">{budget.target}</div>
                                <div className="text-xs text-gray-500 dark:text-gray-400">Objetivo</div>
                              </div>
                              <div className="text-center p-2 bg-green-50 dark:bg-green-900/20 rounded-lg">
                                <div className="text-lg font-bold text-green-600 dark:text-green-400">{budget.warning_threshold}</div>
                                <div className="text-xs text-gray-500 dark:text-gray-400">Advertencia</div>
                              </div>
                              <div className="text-center p-2 bg-red-50 dark:bg-red-900/20 rounded-lg">
                                <div className="text-lg font-bold text-red-600 dark:text-red-400">{budget.critical_threshold}</div>
                                <div className="text-xs text-gray-500 dark:text-gray-400">Crítico</div>
                              </div>
                              <div className="text-center p-2 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                                <div className="text-lg font-bold text-purple-600 dark:text-purple-400">{budget.current_value || 'N/A'}</div>
                                <div className="text-xs text-gray-500 dark:text-gray-400">Actual</div>
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
                      <p className="text-gray-600 dark:text-gray-300">No se encontraron presupuestos de rendimiento configurados</p>
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
                      Métricas de Throughput
                    </h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                        <div className="text-2xl font-bold text-blue-600 dark:text-blue-400 mb-1">
                          {performanceData.throughput.requests_per_minute || 'N/A'}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                          <span className="text-lg">📈</span>
                          Solicitudes/min
                        </div>
                      </div>
                      <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                        <div className="text-2xl font-bold text-green-600 dark:text-green-400 mb-1">
                          {performanceData.throughput.avg_response_time_ms?.toFixed(0) || 'N/A'}ms
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                          <span className="text-lg">⚡</span>
                          Tiempo de Respuesta
                        </div>
                      </div>
                      <div className="text-center p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                        <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400 mb-1">
                          {performanceData.throughput.error_rate_percent?.toFixed(2) || 'N/A'}%
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                          <span className="text-lg">⚠️</span>
                          Tasa de Error
                        </div>
                      </div>
                      <div className="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                        <div className="text-2xl font-bold text-purple-600 dark:text-purple-400 mb-1">
                          {performanceData.throughput.uptime_percent?.toFixed(2) || 'N/A'}%
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                          <span className="text-lg">🟢</span>
                          Disponibilidad
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
                      Resumen de Estado
                    </h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="text-center p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                        <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
                          {performanceData.status.total_budgets || 0}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                          <span className="text-lg">📊</span>
                          Total Presupuestos
                        </div>
                      </div>
                      <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                        <div className="text-3xl font-bold text-green-600 dark:text-green-400 mb-1">
                          {performanceData.status.healthy_budgets || 0}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                          <span className="text-lg">✅</span>
                          Saludables
                        </div>
                      </div>
                      <div className="text-center p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                        <div className="text-3xl font-bold text-yellow-600 dark:text-yellow-400 mb-1">
                          {performanceData.status.warning_budgets || 0}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                          <span className="text-lg">⚠️</span>
                          Advertencias
                        </div>
                      </div>
                      <div className="text-center p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
                        <div className="text-3xl font-bold text-red-600 dark:text-red-400 mb-1">
                          {performanceData.status.critical_budgets || 0}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-1">
                          <span className="text-lg">❌</span>
                          Críticos
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
            Cerrar
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
            Actualizar
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
