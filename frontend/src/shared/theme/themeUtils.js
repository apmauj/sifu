/**
 * Utilidades para generación y manipulación de temas
 */

/**
 * Genera escala de shades (50-950) a partir de un color base
 * 
 * Algoritmo:
 * - Shades claros (50-400): Mezclar con blanco (lightness aumenta)
 * - Base (500): Color original sin modificar
 * - Shades oscuros (600-950): Mezclar con negro (lightness disminuye)
 * 
 * @param {string} baseColor - Color hex (ej: '#0EA5E9')
 * @returns {Object} Objeto con shades { 50: '#...', 100: '#...', ..., 950: '#...' }
 * 
 * @example
 * generateShades('#0EA5E9')
 * // {
 * //   50: '#f0f9ff',
 * //   100: '#e0f2fe',
 * //   ...
 * //   500: '#0ea5e9',  // original
 * //   ...
 * //   950: '#082f49'
 * // }
 */
export const generateShades = (baseColor) => {
  // Normalizar color hex (remover # si existe)
  const hex = baseColor.replace('#', '');
  
  // Parsear RGB
  const r = parseInt(hex.slice(0, 2), 16);
  const g = parseInt(hex.slice(2, 4), 16);
  const b = parseInt(hex.slice(4, 6), 16);

  /**
   * Mezcla un color con otro según ratio
   * @param {number} color - Componente de color (0-255)
   * @param {number} mixer - Color a mezclar (0 para negro, 255 para blanco)
   * @param {number} ratio - Proporción de mezcla (0-1)
   */
  const mix = (color, mixer, ratio) => {
    return Math.round(color * (1 - ratio) + mixer * ratio);
  };

  /**
   * Convierte RGB a hex
   */
  const toHex = (r, g, b) => {
    const componentToHex = (c) => {
      const hex = Math.max(0, Math.min(255, c)).toString(16);
      return hex.length === 1 ? '0' + hex : hex;
    };
    return `#${componentToHex(r)}${componentToHex(g)}${componentToHex(b)}`;
  };

  /**
   * Genera shade más claro (mezcla con blanco)
   */
  const lighten = (ratio) => toHex(
    mix(r, 255, ratio),
    mix(g, 255, ratio),
    mix(b, 255, ratio)
  );

  /**
   * Genera shade más oscuro (mezcla con negro)
   */
  const darken = (ratio) => toHex(
    mix(r, 0, ratio),
    mix(g, 0, ratio),
    mix(b, 0, ratio)
  );

  return {
    50: lighten(0.95),   // Casi blanco
    100: lighten(0.90),  // Muy claro
    200: lighten(0.75),  // Claro
    300: lighten(0.60),  // Medio-claro
    400: lighten(0.30),  // Claro-medio
    500: baseColor.startsWith('#') ? baseColor : `#${baseColor}`,  // Color base original
    600: darken(0.20),   // Medio-oscuro
    700: darken(0.40),   // Oscuro
    800: darken(0.60),   // Muy oscuro
    900: darken(0.75),   // Casi negro
    950: darken(0.85),   // Negro profundo
  };
};

/**
 * Convierte RGB (0-255) a HSL (Hue, Saturation, Lightness)
 * 
 * Útil para cálculos de color más precisos
 * 
 * @param {number} r - Rojo (0-255)
 * @param {number} g - Verde (0-255)
 * @param {number} b - Azul (0-255)
 * @returns {Array<number>} [H (0-360), S (0-100), L (0-100)]
 * 
 * @example
 * rgbToHsl(14, 165, 233) // → [199, 89, 48]
 */
export const rgbToHsl = (r, g, b) => {
  r /= 255;
  g /= 255;
  b /= 255;

  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  let h, s, l = (max + min) / 2;

  if (max === min) {
    h = s = 0; // achromatic (gray)
  } else {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);

    switch (max) {
      case r:
        h = ((g - b) / d + (g < b ? 6 : 0)) / 6;
        break;
      case g:
        h = ((b - r) / d + 2) / 6;
        break;
      case b:
        h = ((r - g) / d + 4) / 6;
        break;
      default:
        h = 0;
    }
  }

  return [
    Math.round(h * 360),  // Hue en grados (0-360)
    Math.round(s * 100),  // Saturation en porcentaje (0-100)
    Math.round(l * 100),  // Lightness en porcentaje (0-100)
  ];
};

/**
 * Convierte HSL a RGB
 * 
 * @param {number} h - Hue (0-360)
 * @param {number} s - Saturation (0-100)
 * @param {number} l - Lightness (0-100)
 * @returns {Array<number>} [R (0-255), G (0-255), B (0-255)]
 * 
 * @example
 * hslToRgb(199, 89, 48) // → [14, 165, 233]
 */
export const hslToRgb = (h, s, l) => {
  h /= 360;
  s /= 100;
  l /= 100;

  let r, g, b;

  if (s === 0) {
    r = g = b = l; // achromatic (gray)
  } else {
    const hue2rgb = (p, q, t) => {
      if (t < 0) t += 1;
      if (t > 1) t -= 1;
      if (t < 1/6) return p + (q - p) * 6 * t;
      if (t < 1/2) return q;
      if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
      return p;
    };

    const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
    const p = 2 * l - q;

    r = hue2rgb(p, q, h + 1/3);
    g = hue2rgb(p, q, h);
    b = hue2rgb(p, q, h - 1/3);
  }

  return [
    Math.round(r * 255),
    Math.round(g * 255),
    Math.round(b * 255),
  ];
};

/**
 * Convierte color hex a RGB
 * 
 * @param {string} hex - Color hex (ej: '#0EA5E9' o '0EA5E9')
 * @returns {Array<number>} [R, G, B]
 */
export const hexToRgb = (hex) => {
  const normalized = hex.replace('#', '');
  return [
    parseInt(normalized.slice(0, 2), 16),
    parseInt(normalized.slice(2, 4), 16),
    parseInt(normalized.slice(4, 6), 16),
  ];
};

/**
 * Convierte RGB a hex
 * 
 * @param {number} r - Rojo (0-255)
 * @param {number} g - Verde (0-255)
 * @param {number} b - Azul (0-255)
 * @returns {string} Color hex (ej: '#0EA5E9')
 */
export const rgbToHex = (r, g, b) => {
  const componentToHex = (c) => {
    const hex = Math.max(0, Math.min(255, Math.round(c))).toString(16);
    return hex.length === 1 ? '0' + hex : hex;
  };
  return `#${componentToHex(r)}${componentToHex(g)}${componentToHex(b)}`;
};

/**
 * Calcula contraste entre dos colores (WCAG)
 * 
 * @param {string} color1 - Color hex
 * @param {string} color2 - Color hex
 * @returns {number} Ratio de contraste (1-21)
 */
export const getContrastRatio = (color1, color2) => {
  const getLuminance = (r, g, b) => {
    const [rs, gs, bs] = [r, g, b].map(c => {
      c /= 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
  };

  const rgb1 = hexToRgb(color1);
  const rgb2 = hexToRgb(color2);

  const lum1 = getLuminance(...rgb1);
  const lum2 = getLuminance(...rgb2);

  const lighter = Math.max(lum1, lum2);
  const darker = Math.min(lum1, lum2);

  return (lighter + 0.05) / (darker + 0.05);
};

/**
 * Valida si un color cumple WCAG AA para texto
 * 
 * @param {string} textColor - Color del texto (hex)
 * @param {string} bgColor - Color del fondo (hex)
 * @param {boolean} largeText - ¿Es texto grande (>18px)?
 * @returns {boolean} True si cumple WCAG AA
 */
export const meetsWCAGAA = (textColor, bgColor, largeText = false) => {
  const ratio = getContrastRatio(textColor, bgColor);
  return largeText ? ratio >= 3 : ratio >= 4.5;
};

export default {
  generateShades,
  rgbToHsl,
  hslToRgb,
  hexToRgb,
  rgbToHex,
  getContrastRatio,
  meetsWCAGAA,
};
