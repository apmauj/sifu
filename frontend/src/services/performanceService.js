import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class PerformanceService {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
    });
  }

  async getBudgets() {
    try {
      const response = await this.client.get('/api/performance/budgets');
      return response.data;
    } catch (error) {
      console.error('Error fetching performance budgets:', error);
      throw error;
    }
  }

  async getBudgetStatus() {
    try {
      const response = await this.client.get('/api/performance/budgets/status');
      return response.data;
    } catch (error) {
      console.error('Error fetching budget status:', error);
      throw error;
    }
  }

  async getThroughput() {
    try {
      const response = await this.client.get('/api/performance/throughput');
      return response.data;
    } catch (error) {
      console.error('Error fetching throughput metrics:', error);
      throw error;
    }
  }

  async getBudgetDetails(name) {
    try {
      const response = await this.client.get(`/api/performance/budgets/${name}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching budget details:', error);
      throw error;
    }
  }
}

const performanceService = new PerformanceService();
export default performanceService;
