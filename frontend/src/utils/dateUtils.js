/**
 * Utilidades para manejo de fechas locales
 * Evita problemas de zona horaria al trabajar con fechas
 */

/**
 * Obtiene la fecha actual en formato YYYY-MM-DD usando la zona horaria local
 * @returns {string} Fecha en formato YYYY-MM-DD
 */
export const getTodayLocal = () => {
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, '0');
  const day = String(today.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

/**
 * Convierte una fecha a formato YYYY-MM-DD usando la zona horaria local
 * @param {Date} date - Fecha a convertir
 * @returns {string} Fecha en formato YYYY-MM-DD
 */
export const formatDateLocal = (date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

/**
 * Resta días a una fecha manteniendo la zona horaria local
 * @param {Date} date - Fecha base
 * @param {number} days - Días a restar
 * @returns {string} Fecha resultante en formato YYYY-MM-DD
 */
export const subtractDaysLocal = (date, days) => {
  const result = new Date(date);
  result.setDate(result.getDate() - days);
  return formatDateLocal(result);
};

/**
 * Obtiene la fecha de hace N días en formato YYYY-MM-DD
 * @param {number} days - Días hacia atrás
 * @returns {string} Fecha en formato YYYY-MM-DD
 */
export const getDaysAgoLocal = (days) => {
  return subtractDaysLocal(new Date(), days);
};

/**
 * Obtiene el timestamp actual para mostrar en la UI
 * @returns {Date} Fecha actual
 */
export const getCurrentTimestamp = () => {
  return new Date();
}; 