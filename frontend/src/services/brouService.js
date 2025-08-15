import { makeRequest } from './api';

const brouService = {
  getCurrent: async (opts = {}) => {
    // En el futuro podemos activar '?full=true' para metadatos; por ahora simple.
    const query = opts.full ? '?full=true' : '';
    return makeRequest(api => api.get(`/brou/current${query}`));
  }
};

export default brouService; 