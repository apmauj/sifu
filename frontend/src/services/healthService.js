const API_BASE_URL = import.meta.env.VITE_PUBLIC_API_URL || 'http://localhost:8000';

console.log('HealthService - API_BASE_URL:', API_BASE_URL);

class HealthService {
  async getSimpleHealth() {
    console.log('HealthService - getSimpleHealth called');
    try {
      const url = `${API_BASE_URL}/api/health/simple`;
      console.log('HealthService - Fetching from:', url);
      const response = await fetch(url);
      console.log('HealthService - Response status:', response.status);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log('HealthService - Response data:', data);
      return data;
    } catch (error) {
      console.error('Error fetching simple health:', error);
      return {
        status: 'error',
        message: 'Backend no disponible. El dashboard requiere que el backend esté ejecutándose.',
        overall_status: 'unknown',
        checks: {
          backend_availability: {
            status: 'critical',
            message: 'No se puede conectar al backend. Asegúrate de que esté ejecutándose en ' + API_BASE_URL
          }
        }
      };
    }
  }

  async getAdvancedHealth() {
    console.log('HealthService - getAdvancedHealth called');
    try {
      const url = `${API_BASE_URL}/api/health/advanced`;
      console.log('HealthService - Fetching from:', url);
      const response = await fetch(url);
      console.log('HealthService - Response status:', response.status);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log('HealthService - Response data:', data);
      return data;
    } catch (error) {
      console.error('Error fetching advanced health:', error);
      return {
        status: 'error',
        message: 'Backend no disponible. El dashboard requiere que el backend esté ejecutándose.',
        overall_status: 'unknown',
        checks: {
          backend_availability: {
            status: 'critical',
            message: 'No se puede conectar al backend. Asegúrate de que esté ejecutándose en ' + API_BASE_URL
          }
        }
      };
    }
  }
}

export default new HealthService();
