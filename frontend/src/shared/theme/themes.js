import { generateShades } from './themeUtils';

/**
 * Definición de temas disponibles en SIFU
 * 
 * Cada tema define:
 * - primary: Color principal del tema (10 shades: 50-950)
 * - neutral: Escala de grises del tema (10 shades: 50-950)
 * - semantic: Colores semánticos (success, error, warning, info)
 * 
 * Los neutrals VARÍAN por tema para crear diferentes "temperaturas" visuales:
 * - Tema azul: grays fríos (tinte azul)
 * - Tema cálido: grays cálidos (tinte sepia/marrón)
 * - Tema frío: grays muy fríos (blue-gray)
 */
export const themes = {
  /**
   * Tema por defecto: Uruguay Blue
   * Color principal: Sky Blue (#0EA5E9)
   * Neutrals: Grays fríos con ligero tinte azul
   */
  default: {
    id: 'default',
    name: 'Uruguay Blue',
    description: 'Tema oficial con azul celeste y grays fríos',
    primary: {
      50: '#f0f9ff',
      100: '#e0f2fe',
      200: '#bae6fd',
      300: '#7dd3fc',
      400: '#38bdf8',
      500: '#0ea5e9',   // ← Color base
      600: '#0284c7',
      700: '#0369a1',
      800: '#075985',
      900: '#0c4a6e',
      950: '#082f49',
    },
    neutral: {
      // Grays fríos (cool grays con tinte azul)
      50: '#f9fafb',
      100: '#f3f4f6',
      200: '#e5e7eb',
      300: '#d1d5db',
      400: '#9ca3af',
      500: '#6b7280',
      600: '#4b5563',
      700: '#374151',
      800: '#1f2937',
      900: '#111827',
      950: '#030712',
    },
    semantic: {
      success: '#10b981',  // green-500
      error: '#ef4444',    // red-500
      warning: '#f59e0b',  // amber-500
      info: '#06b6d4',     // cyan-500
    },
  },

  /**
   * Tema cálido: Warm Sunset
   * Color principal: Orange (#F97316)
   * Neutrals: Grays cálidos con tinte sepia/marrón
   */
  warm: {
    id: 'warm',
    name: 'Warm Sunset',
    description: 'Tema cálido con naranja y grays sepia',
    primary: {
      50: '#fff7ed',
      100: '#ffedd5',
      200: '#fed7aa',
      300: '#fdba74',
      400: '#fb923c',
      500: '#f97316',   // ← Color base
      600: '#ea580c',
      700: '#c2410c',
      800: '#9a3412',
      900: '#7c2d12',
      950: '#431407',
    },
    neutral: {
      // Grays cálidos (warm grays con tinte marrón/sepia)
      50: '#fafaf9',
      100: '#f5f5f4',
      200: '#e7e5e4',
      300: '#d6d3d1',
      400: '#a8a29e',
      500: '#78716c',
      600: '#57534e',
      700: '#44403c',
      800: '#292524',
      900: '#1c1917',
      950: '#0c0a09',
    },
    semantic: {
      success: '#10b981',  // green-500
      error: '#ef4444',    // red-500
      warning: '#eab308',  // yellow-500 (más amarillo en tema cálido)
      info: '#14b8a6',     // teal-500 (en vez de cyan)
    },
  },

  /**
   * Tema frío: Ocean Teal
   * Color principal: Teal (#14B8A6)
   * Neutrals: Grays muy fríos (blue-gray)
   */
  cool: {
    id: 'cool',
    name: 'Ocean Teal',
    description: 'Tema frío con teal y grays azulados',
    primary: {
      50: '#f0fdfa',
      100: '#ccfbf1',
      200: '#99f6e4',
      300: '#5eead4',
      400: '#2dd4bf',
      500: '#14b8a6',   // ← Color base
      600: '#0d9488',
      700: '#0f766e',
      800: '#115e59',
      900: '#134e4a',
      950: '#042f2e',
    },
    neutral: {
      // Grays muy fríos (blue-gray/slate)
      50: '#f8fafc',
      100: '#f1f5f9',
      200: '#e2e8f0',
      300: '#cbd5e1',
      400: '#94a3b8',
      500: '#64748b',
      600: '#475569',
      700: '#334155',
      800: '#1e293b',
      900: '#0f172a',
      950: '#020617',
    },
    semantic: {
      success: '#10b981',  // green-500
      error: '#ef4444',    // red-500
      warning: '#f59e0b',  // amber-500
      info: '#0ea5e9',     // sky-500 (cyan/blue)
    },
  },
};

/**
 * Obtiene tema por ID
 * 
 * @param {string} themeId - ID del tema ('default', 'warm', 'cool')
 * @returns {Object} Definición del tema
 */
export const getTheme = (themeId = 'default') => {
  return themes[themeId] || themes.default;
};

/**
 * Lista de temas disponibles para selector UI
 * 
 * @returns {Array<Object>} Array con id, name, description, primaryColor, neutralColor
 */
export const availableThemes = Object.values(themes).map(t => ({
  id: t.id,
  name: t.name,
  description: t.description,
  primaryColor: t.primary[500],
  neutralColor: t.neutral[500],
}));

/**
 * Genera un tema personalizado a partir de un color base
 * 
 * @param {string} baseColor - Color hex (ej: '#FF6B6B')
 * @param {string} neutralTone - Tono de neutrals: 'cool', 'warm', 'neutral'
 * @returns {Object} Definición de tema custom
 * 
 * @example
 * const myTheme = generateCustomTheme('#FF6B6B', 'warm');
 */
export const generateCustomTheme = (baseColor, neutralTone = 'neutral') => {
  const primary = generateShades(baseColor);
  
  // Usar neutral del tema que coincida con el tono deseado
  const neutralPresets = {
    cool: themes.cool.neutral,
    warm: themes.warm.neutral,
    neutral: themes.default.neutral,
  };
  
  return {
    id: 'custom',
    name: 'Custom Theme',
    description: 'Tema personalizado generado dinámicamente',
    primary,
    neutral: neutralPresets[neutralTone] || neutralPresets.neutral,
    semantic: themes.default.semantic, // Mantener semánticos estándar
  };
};

export default themes;
