import { makeRequest } from './api';

const brouService = {
  getCurrent: async (opts = {}) => {
    // Usar modo completo por defecto para obtener metadata adicional
    // Opcional: usar opts.full = false para modo compacto (compatibilidad)
    const query = opts.full !== false ? '?full=true' : '';
    return makeRequest(api => api.get(`/brou/current${query}`));
  }
};

export default brouService; 