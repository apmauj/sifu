const API_BASE_URL = import.meta.env.VITE_PUBLIC_API_URL || 'http://localhost:8000';

class HealthService {
  async getSimpleHealth() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/health/simple`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
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
    try {
      const response = await fetch(`${API_BASE_URL}/api/health/advanced`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
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
