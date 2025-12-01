import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * Hook para monitorear la salud de la conexión entre frontend y backend
 * 
 * @param {Object} options - Opciones de configuración
 * @param {number} options.checkInterval - Intervalo de verificación en milisegundos (default: 60000 - 1 minuto)
 * @param {number} options.timeout - Timeout para la petición en milisegundos (default: 5000 - 5 segundos)
 * @param {boolean} options.enabled - Si el monitoreo está habilitado (default: true)
 * @param {Function} options.onStatusChange - Callback cuando cambia el estado de conexión
 * @returns {Object} Estado de la conexión y funciones de control
 */
export const useBackendHealth = (options = {}) => {
  const {
    checkInterval = 60000, // 1 minuto por defecto
    timeout = 5000, // 5 segundos timeout
    enabled = true,
    onStatusChange = null
  } = options;

  const [isHealthy, setIsHealthy] = useState(null); // null = no verificado aún
  const [lastCheck, setLastCheck] = useState(null);
  const [error, setError] = useState(null);
  const [isChecking, setIsChecking] = useState(false);
  const intervalRef = useRef(null);
  const abortControllerRef = useRef(null);
  const previousStatusRef = useRef(null);

  /**
   * Realiza una verificación de salud del backend
   */
  const checkHealth = useCallback(async () => {
    // Cancelar petición anterior si existe
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();
    setIsChecking(true);
    setError(null);

    try {
      const apiUrl = import.meta.env.VITE_PUBLIC_API_URL || 'http://localhost:8000';
      const healthUrl = `${apiUrl}/api/health`;

      const timeoutId = setTimeout(() => {
        abortControllerRef.current?.abort();
      }, timeout);

      const response = await fetch(healthUrl, {
        method: 'GET',
        signal: abortControllerRef.current.signal,
        headers: {
          'Accept': 'application/json',
        },
      });

      clearTimeout(timeoutId);

      const isOk = response.ok && response.status === 200;
      const newStatus = isOk;
      
      setIsHealthy(newStatus);
      setLastCheck(new Date());

      // Notificar cambio de estado si cambió
      if (previousStatusRef.current !== newStatus && previousStatusRef.current !== null) {
        onStatusChange?.(newStatus, previousStatusRef.current);
      }
      previousStatusRef.current = newStatus;

      if (!isOk) {
        setError(`Backend respondió con estado ${response.status}`);
      }

    } catch (err) {
      if (err.name === 'AbortError') {
        setError('Timeout: El backend no respondió a tiempo');
      } else {
        setError(err.message || 'Error al conectar con el backend');
      }
      
      const newStatus = false;
      setIsHealthy(newStatus);
      setLastCheck(new Date());

      // Notificar cambio de estado
      if (previousStatusRef.current !== newStatus && previousStatusRef.current !== null) {
        onStatusChange?.(newStatus, previousStatusRef.current);
      }
      previousStatusRef.current = newStatus;

    } finally {
      setIsChecking(false);
      abortControllerRef.current = null;
    }
  }, [timeout, onStatusChange]);

  /**
   * Fuerza una verificación manual inmediata
   */
  const forceCheck = useCallback(() => {
    checkHealth();
  }, [checkHealth]);

  /**
   * Función de limpieza
   */
  const cleanup = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  }, []);

  // Efecto para configurar el monitoreo periódico
  useEffect(() => {
    if (!enabled) {
      cleanup();
      return;
    }

    // Verificación inicial
    checkHealth();

    // Configurar verificación periódica
    if (checkInterval > 0) {
      intervalRef.current = setInterval(checkHealth, checkInterval);
    }

    return cleanup;
  }, [enabled, checkInterval, checkHealth, cleanup]);

  return {
    isHealthy,        // true/false/null (null = no verificado aún)
    isChecking,       // boolean - si está verificando en este momento
    lastCheck,        // Date - última vez que se verificó
    error,            // string - mensaje de error si hubo
    forceCheck,       // function - fuerza verificación manual
    cleanup,          // function - limpia recursos manualmente
  };
};

export default useBackendHealth;
