import { useEffect, useRef } from 'react';

/**
 * Hook personalizado para ejecutar una función cada hora sincronizada con el minuto cero
 * 
 * @param {Function} updateFunction - Función a ejecutar en cada actualización
 * @param {boolean} enabled - Si el hook está habilitado (default: true)
 * @returns {Function} cleanup function para limpiar manualmente si es necesario
 */
export const useHourlySyncedUpdate = (updateFunction, enabled = true, options = {}) => {
  const timeoutRef = useRef(null);
  const intervalRef = useRef(null);
  const hasRunInitialRef = useRef(false);

  /**
   * Calcula el tiempo en milisegundos hasta el próximo minuto cero de la hora
   * @returns {number} Milisegundos hasta la próxima hora en punto
   */
  const getTimeToNextHour = () => {
    const now = new Date();
    const nextHour = new Date(now);
    nextHour.setHours(now.getHours() + 1, 0, 0, 0); // Próxima hora en punto
    return nextHour.getTime() - now.getTime();
  };

  /**
   * Función de limpieza para cancelar todos los timers
   */
  const cleanup = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  useEffect(() => {
    if (!enabled || typeof updateFunction !== 'function') {
      return cleanup;
    }
    const runImmediately = options.runImmediately !== false;
    
    // Ejecutar inmediatamente al montar el componente (evitar doble ejecución en StrictMode)
    if (runImmediately && !hasRunInitialRef.current) {
      hasRunInitialRef.current = true;
      updateFunction();
    }

    // Calcular tiempo hasta la próxima hora en punto
    const timeToNextHour = getTimeToNextHour();

    // Programar la primera actualización sincronizada
    timeoutRef.current = setTimeout(() => {
      updateFunction();

      // Una vez sincronizado, configurar intervalo cada hora exacta
      intervalRef.current = setInterval(updateFunction, 60 * 60 * 1000);
    }, timeToNextHour);

    // Función de limpieza para el useEffect
    return cleanup;
  }, [updateFunction, enabled, options.runImmediately]);

  // Retornar función de limpieza manual por si se necesita
  return cleanup;
}; 