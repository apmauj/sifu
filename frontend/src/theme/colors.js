/**
 * Sistema centralizado de colores semánticos
 * 
 * Este archivo mapea intenciones de diseño a la paleta cromática definida en tailwind.config.js
 * Usar estos helpers asegura consistencia en toda la aplicación
 */

/**
 * Mapeo semántico de colores por contexto de uso
 */
export const semanticColors = {
  // Estados de UI (feedback del sistema)
  status: {
    success: 'success',   // Éxito/confirmación → Verde
    error: 'error',       // Error/fallo → Rojo
    warning: 'secondary', // Advertencia/precaución → Naranja
    info: 'accent',       // Información/datos → Cyan
    neutral: 'gray',      // Neutral/sin estado → Gris
  },

  // Estados de datos financieros (específico para SIFU)
  data: {
    buy: 'success',       // Compra/positivo → Verde
    sell: 'error',        // Venta/negativo → Rojo
    highlight: 'primary', // Destacado/principal → Azul
    neutral: 'accent',    // Neutro/informativo → Cyan
    arbitrage: 'accent',  // Arbitraje → Cyan
  },

  // Estados de frescura/actualización de datos
  freshness: {
    fresh: 'success',     // Datos recientes (< 5 min) → Verde
    stale: 'secondary',   // Datos antiguos (> 1h) → Naranja
    outdated: 'error',    // Datos obsoletos (> 24h) → Rojo
    unknown: 'gray',      // Estado desconocido → Gris
  },

  // Elementos interactivos (botones, enlaces)
  interactive: {
    primary: 'primary',   // Acción principal → Azul
    secondary: 'secondary', // Acción secundaria → Naranja
    danger: 'error',      // Acción destructiva → Rojo
    neutral: 'gray',      // Acción neutra → Gris
    ghost: 'transparent', // Sin fondo → Transparente con border
  },

  // Bordes y separadores
  border: {
    default: 'gray-200',  // Bordes estándar light
    defaultDark: 'gray-700', // Bordes estándar dark
    subtle: 'gray-100',   // Bordes sutiles light
    subtleDark: 'gray-800', // Bordes sutiles dark
    emphasis: 'primary-200', // Bordes con énfasis
    emphasisDark: 'primary-800',
  },
};

/**
 * Genera clase Tailwind para un color semántico
 * 
 * @param {string} intent - Color semántico (ej: 'success', 'error', 'primary')
 * @param {string} type - Tipo de clase ('bg', 'text', 'border')
 * @param {number} shade - Shade del color (50-950)
 * @returns {string} Clase Tailwind (ej: 'bg-success-600')
 * 
 * @example
 * getSemanticClass('success', 'bg', 600) // → 'bg-success-600'
 * getSemanticClass('error', 'text', 700) // → 'text-error-700'
 */
export const getSemanticClass = (intent, type, shade = 600) => {
  // Si intent ya es un color de la paleta, usarlo directamente
  const validColors = ['primary', 'secondary', 'accent', 'success', 'error'];
  const color = validColors.includes(intent) ? intent : intent;
  
  return `${type}-${color}-${shade}`;
};

/**
 * Genera clases Tailwind con soporte dark mode
 * 
 * @param {string} intent - Color semántico
 * @param {string} type - Tipo de clase ('bg', 'text', 'border')
 * @param {number} lightShade - Shade para modo claro
 * @param {number} darkShade - Shade para modo oscuro
 * @returns {string} Clases con dark mode
 * 
 * @example
 * getSemanticClassWithDark('success', 'bg', 100, 900)
 * // → 'bg-success-100 dark:bg-success-900'
 */
export const getSemanticClassWithDark = (intent, type, lightShade = 600, darkShade = 400) => {
  const base = getSemanticClass(intent, type, lightShade);
  const dark = getSemanticClass(intent, type, darkShade);
  return `${base} dark:${dark}`;
};

/**
 * Variantes predefinidas para componentes comunes
 */
export const componentVariants = {
  // Variantes de Badge
  badge: {
    success: 'bg-success-100 text-success-800 dark:bg-success-950 dark:text-success-300',
    error: 'bg-error-100 text-error-800 dark:bg-error-950 dark:text-error-300',
    warning: 'bg-secondary-100 text-secondary-800 dark:bg-secondary-950 dark:text-secondary-300',
    info: 'bg-accent-100 text-accent-800 dark:bg-accent-950 dark:text-accent-300',
    neutral: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200',
    primary: 'bg-primary-100 text-primary-800 dark:bg-primary-950 dark:text-primary-300',
  },

  // Variantes de Alert
  alert: {
    success: 'bg-success-50 border-success-200 text-success-800 dark:bg-success-950/30 dark:border-success-800 dark:text-success-300',
    error: 'bg-error-50 border-error-200 text-error-800 dark:bg-error-950/30 dark:border-error-800 dark:text-error-300',
    warning: 'bg-secondary-50 border-secondary-200 text-secondary-800 dark:bg-secondary-950/30 dark:border-secondary-800 dark:text-secondary-300',
    info: 'bg-accent-50 border-accent-200 text-accent-800 dark:bg-accent-950/30 dark:border-accent-800 dark:text-accent-300',
  },

  // Variantes de Button
  button: {
    primary: 'bg-primary-600 hover:bg-primary-700 active:bg-primary-800 text-white dark:bg-primary-600 dark:hover:bg-primary-700',
    secondary: 'bg-secondary-500 hover:bg-secondary-600 active:bg-secondary-700 text-white dark:bg-secondary-600 dark:hover:bg-secondary-700',
    danger: 'bg-error-600 hover:bg-error-700 active:bg-error-800 text-white dark:bg-error-600 dark:hover:bg-error-700',
    ghost: 'bg-transparent hover:bg-gray-100 dark:hover:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300',
    success: 'bg-success-600 hover:bg-success-700 active:bg-success-800 text-white dark:bg-success-600 dark:hover:bg-success-700',
  },

  // Variantes de Spinner (loading)
  spinner: {
    primary: 'border-primary-600 dark:border-primary-400',
    secondary: 'border-secondary-600 dark:border-secondary-400',
    white: 'border-white',
    gray: 'border-gray-600 dark:border-gray-400',
  },
};

/**
 * Helper para obtener clases de variante de componente
 * 
 * @param {string} component - Tipo de componente ('badge', 'alert', 'button')
 * @param {string} variant - Variante deseada ('success', 'error', etc.)
 * @returns {string} Clases completas
 * 
 * @example
 * getComponentVariant('badge', 'success')
 * // → 'bg-success-100 text-success-800 dark:bg-success-950 dark:text-success-300'
 */
export const getComponentVariant = (component, variant) => {
  return componentVariants[component]?.[variant] || componentVariants[component]?.neutral || '';
};

/**
 * Clases de texto semánticas predefinidas
 */
export const textColors = {
  primary: 'text-gray-900 dark:text-gray-50',
  secondary: 'text-gray-600 dark:text-gray-400',
  tertiary: 'text-gray-500 dark:text-gray-500',
  muted: 'text-gray-400 dark:text-gray-600',
  
  // Colores de énfasis
  emphasis: 'text-primary-600 dark:text-primary-400',
  success: 'text-success-600 dark:text-success-400',
  error: 'text-error-600 dark:text-error-400',
  warning: 'text-secondary-600 dark:text-secondary-400',
  info: 'text-accent-600 dark:text-accent-400',
};

/**
 * Clases de fondo semánticas predefinidas
 */
export const backgroundColors = {
  primary: 'bg-white dark:bg-gray-800',
  secondary: 'bg-gray-50 dark:bg-gray-900',
  tertiary: 'bg-gray-100 dark:bg-gray-800',
  
  // Fondos de énfasis
  primarySubtle: 'bg-primary-50 dark:bg-primary-950/30',
  successSubtle: 'bg-success-50 dark:bg-success-950/30',
  errorSubtle: 'bg-error-50 dark:bg-error-950/30',
  warningSubtle: 'bg-secondary-50 dark:bg-secondary-950/30',
  infoSubtle: 'bg-accent-50 dark:bg-accent-950/30',
};

/**
 * Helper para debugging: muestra todos los colores disponibles
 */
export const getAllSemanticColors = () => {
  return {
    status: Object.keys(semanticColors.status),
    data: Object.keys(semanticColors.data),
    freshness: Object.keys(semanticColors.freshness),
    interactive: Object.keys(semanticColors.interactive),
    componentVariants: Object.keys(componentVariants),
  };
};

export default semanticColors;
