import { makeRequest } from './api';

const brouService = {
  getCurrent: async () => makeRequest(api => api.get('/brou/current')),
};

export default brouService; 