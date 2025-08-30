import React, { useState, useEffect } from 'react';
import healthService from '../services/healthService';
import Card, { CardBody } from './ui/Card';

const Dashboard = ({ isOpen, onClose }) => {
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    console.log('Dashboard isOpen changed:', isOpen);
    if (isOpen) {
      console.log('Fetching health data...');
      fetchHealthData();
    }
  }, [isOpen]);

  const fetchHealthData = async () => {
    console.log('Starting fetchHealthData...');
    setLoading(true);
    setError(null);
    try {
      console.log('Calling healthService.getAdvancedHealth()...');
      const data = await healthService.getAdvancedHealth();
      console.log('Health data received:', data);
      setHealthData(data);
    } catch (err) {
      console.error('Error in fetchHealthData:', err);
      setError('Failed to load health data: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'warning':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'critical':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
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
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center p-6 border-b">
          <h2 className="text-2xl font-bold text-gray-900">Dashboard de Monitoreo</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        <div className="p-6">
          {loading && (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Cargando datos de salud...</p>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {healthData && (
            <div className="space-y-6">
              {/* Estado General */}
              <Card>
                <CardBody>
                  <h3 className="text-lg font-semibold mb-4">Estado General del Sistema</h3>
                  <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor(healthData.overall_status)}`}>
                    {getStatusIcon(healthData.overall_status)} {healthData.overall_status || 'Unknown'}
                  </div>
                  {healthData.timestamp && (
                    <p className="text-sm text-gray-500 mt-2">
                      Última actualización: {new Date(healthData.timestamp).toLocaleString()}
                    </p>
                  )}
                </CardBody>
              </Card>

              {/* Detalles de Checks */}
              {healthData.checks && (
                <div>
                  <h3 className="text-lg font-semibold mb-4">Detalles de Verificaciones</h3>
                  <div className="grid gap-4">
                    {Object.entries(healthData.checks).map(([checkName, checkData]) => (
                      <Card key={checkName}>
                        <CardBody>
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-medium capitalize">
                              {checkName.replace(/_/g, ' ')}
                            </h4>
                            <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(checkData.status)}`}>
                              {getStatusIcon(checkData.status)} {checkData.status}
                            </div>
                          </div>
                          {checkData.message && (
                            <p className="text-sm text-gray-600">{checkData.message}</p>
                          )}
                          {checkData.details && (
                            <div className="mt-2 text-xs text-gray-500">
                              <pre className="whitespace-pre-wrap">{JSON.stringify(checkData.details, null, 2)}</pre>
                            </div>
                          )}
                        </CardBody>
                      </Card>
                    ))}
                  </div>
                </div>
              )}

              {/* Métricas de Aplicación */}
              {healthData.metrics && (
                <Card>
                  <CardBody>
                    <h3 className="text-lg font-semibold mb-4">Métricas de Aplicación</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {Object.entries(healthData.metrics).map(([key, value]) => (
                        <div key={key} className="text-center">
                          <div className="text-2xl font-bold text-blue-600">{value}</div>
                          <div className="text-sm text-gray-500 capitalize">{key.replace(/_/g, ' ')}</div>
                        </div>
                      ))}
                    </div>
                  </CardBody>
                </Card>
              )}
            </div>
          )}
        </div>

        <div className="flex justify-end p-6 border-t">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 mr-2"
          >
            Cerrar
          </button>
          <button
            onClick={fetchHealthData}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Actualizar
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
