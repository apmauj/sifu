import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_PUBLIC_API_URL || 'http://localhost:8000';

// Normalize the API base URL to ensure it doesn't have double /api
const normalizeApiUrl = (baseUrl) => {
  // Remove trailing slash
  let url = baseUrl.replace(/\/$/, '');

  // If it ends with /api, remove it since we'll add it in the endpoints
  if (url.endsWith('/api')) {
    url = url.slice(0, -4); // Remove '/api'
  }

  return url;
};

const NORMALIZED_API_URL = normalizeApiUrl(API_BASE_URL);

class PerformanceService {
  constructor() {
    this.client = axios.create({
      baseURL: NORMALIZED_API_URL,
  // Default timeout for lightweight endpoints; heavier ones override per-call
  timeout: parseInt(import.meta.env.VITE_DEFAULT_HTTP_TIMEOUT_MS || "10000", 10),
    });
  }

  async getBudgets() {
    try {
  // Backend waits up to ~15s for budgets; align client timeout (allow env override)
  const timeout = parseInt(import.meta.env.VITE_PERF_BUDGETS_TIMEOUT_MS || "20000", 10);
  const response = await this.client.get('/api/performance/budgets', { timeout });
      return response.data;
    } catch (error) {
  const msg = error?.code === 'ECONNABORTED' ? `Timeout fetching performance budgets after ${error?.config?.timeout}ms` : 'Error fetching performance budgets';
  console.error(msg + ':', error);
      throw error;
    }
  }

  async getBudgetStatus() {
    try {
  // Backend allows up to ~30s; align client timeout
  const timeout = parseInt(import.meta.env.VITE_PERF_STATUS_TIMEOUT_MS || "35000", 10);
  const response = await this.client.get('/api/performance/budgets/status', { timeout });
      return response.data;
    } catch (error) {
  const msg = error?.code === 'ECONNABORTED' ? `Timeout fetching budget status after ${error?.config?.timeout}ms` : 'Error fetching budget status';
  console.error(msg + ':', error);
      throw error;
    }
  }

  async getThroughput() {
    try {
  // Backend waits up to ~15s; align client
  const timeout = parseInt(import.meta.env.VITE_PERF_THROUGHPUT_TIMEOUT_MS || "20000", 10);
  const response = await this.client.get('/api/performance/throughput', { timeout });
      return response.data;
    } catch (error) {
  const msg = error?.code === 'ECONNABORTED' ? `Timeout fetching throughput metrics after ${error?.config?.timeout}ms` : 'Error fetching throughput metrics';
  console.error(msg + ':', error);
      throw error;
    }
  }
  
  async getBudgetDetails(name) {
    try {
  const timeout = parseInt(import.meta.env.VITE_PERF_BUDGET_DETAIL_TIMEOUT_MS || "20000", 10);
  const response = await this.client.get(`/api/performance/budgets/${name}`, { timeout });
      return response.data;
    } catch (error) {
  const msg = error?.code === 'ECONNABORTED' ? `Timeout fetching budget details after ${error?.config?.timeout}ms` : 'Error fetching budget details';
  console.error(msg + ':', error);
      throw error;
    }
  }
}

const performanceService = new PerformanceService();
export default performanceService;
