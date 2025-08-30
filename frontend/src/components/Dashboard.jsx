import React, { useState, useEffect } from 'react';
import healthService from '../services/healthService';
import Card, { CardBody } from './ui/Card';

const Dashboard = ({ isOpen, onClose }) => {
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen) {
      fetchHealthData();
    }
  }, [isOpen]);

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

        <div className="p-6">
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
                  <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Estado General del Sistema</h3>
                  <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor(healthData.status)}`}>
                    {getStatusIcon(healthData.status)} {healthData.status || 'Unknown'}
                  </div>
                  {healthData.timestamp && (
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                      Última actualización: {new Date(healthData.timestamp).toLocaleString()}
                    </p>
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
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-medium capitalize text-gray-900 dark:text-white">
                              {checkData.name.replace(/_/g, ' ')}
                            </h4>
                            <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(checkData.status)}`}>
                              {getStatusIcon(checkData.status)} {checkData.status}
                            </div>
                          </div>
                          {checkData.message && (
                            <p className="text-sm text-gray-600 dark:text-gray-300">{checkData.message}</p>
                          )}
                          {checkData.details && Object.keys(checkData.details).length > 0 && (
                            <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                              <pre className="whitespace-pre-wrap">{JSON.stringify(checkData.details, null, 2)}</pre>
                            </div>
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
                    <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Información del Sistema</h3>
                    <div className="text-sm text-gray-600 dark:text-gray-300">
                      <pre className="whitespace-pre-wrap">{JSON.stringify(healthData.system_info, null, 2)}</pre>
                    </div>
                  </CardBody>
                </Card>
              )}

              {/* Estadísticas Generales */}
              <Card>
                <CardBody>
                  <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Estadísticas Generales</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{healthData.total_checks}</div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">Total de verificaciones</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600 dark:text-green-400">{healthData.healthy_checks}</div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">Verificaciones saludables</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{healthData.warning_checks}</div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">Verificaciones con advertencia</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-red-600 dark:text-red-400">{healthData.critical_checks}</div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">Verificaciones críticas</div>
                    </div>
                  </div>
                </CardBody>
              </Card>
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
            onClick={fetchHealthData}
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
