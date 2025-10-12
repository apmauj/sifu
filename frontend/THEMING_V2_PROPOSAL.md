# Propuesta: Sistema de Theming Extensible v2

## 🎯 Problema Identificado

El sistema actual tiene:
- ✅ Colores semánticos centralizados (`primary`, `success`, `error`, etc.)
- ✅ Dark mode funcional
- ❌ **Grays hardcodeados** → No cambian con el tema
- ❌ No permite temas personalizados fácilmente
- ❌ Cambiar color principal requiere modificar `tailwind.config.js` manualmente

## 💡 Solución Propuesta

### Arquitectura de 3 Capas

```
┌─────────────────────────────────────┐
│  CAPA 1: Theme Definitions          │
│  (themes.js)                        │
│  - default: blue + cool grays       │
│  - warm: orange + warm grays        │
│  - cool: teal + blue-ish grays      │
│  - custom: user-defined             │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│  CAPA 2: CSS Variables              │
│  (Tailwind + CSS custom props)      │
│  --color-primary-500: #0EA5E9       │
│  --color-neutral-100: #F5F5F5       │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│  CAPA 3: Semantic Helpers           │
│  (colors.js)                        │
│  getSemanticClass('primary', ...)   │
│  getNeutralClass('bg', 100)         │
└─────────────────────────────────────┘
```

---

## 🎨 Definición de Tema

Cada tema incluye:

### 1. Color Principal (Primary)
- 10 shades (50, 100, 200, ..., 900, 950)
- Define la "personalidad" del tema

### 2. Paleta Neutral (Grays)
- 10 shades (50, 100, 200, ..., 900, 950)
- **Varía según el tema**:
  - Tema azul → grays fríos (con tinte azul)
  - Tema naranja → grays cálidos (con tinte marrón/sepia)
  - Tema teal → grays neutros-fríos

### 3. Colores Semánticos (Fijos)
- `success`: Verde (independiente del tema)
- `error`: Rojo (independiente del tema)
- `warning`: Naranja/Amarillo (independiente del tema)
- `accent`: Cyan (o derivado del primary si se desea)

---

## 📁 Estructura de Archivos

```
frontend/src/theme/
├── colors.js           # Helpers semánticos (existente, mejorado)
├── themes.js           # ⭐ NUEVO: Definiciones de temas
├── ThemeContext.jsx    # Context (existente, extendido)
└── themeUtils.js       # ⭐ NUEVO: Generación de shades
```

---

## 🔧 Implementación

### Archivo: `theme/themes.js`

```javascript
import { generateShades } from './themeUtils';

/**
 * Definición de temas disponibles
 * Cada tema define:
 * - primary: Color principal del tema
 * - neutral: Escala de grises del tema
 * - semantic: Colores semánticos (success, error, etc.)
 */
export const themes = {
  // Tema por defecto: Azul Uruguay + grays fríos
  default: {
    id: 'default',
    name: 'Uruguay Blue',
    primary: {
      // Basado en #0EA5E9 (sky-500)
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
      // Grays fríos (slight blue tint)
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

  // Tema cálido: Naranja + grays cálidos (sepia)
  warm: {
    id: 'warm',
    name: 'Warm Sunset',
    primary: {
      // Basado en #f97316 (orange-500)
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
      // Grays cálidos (slight brown/sepia tint)
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
      success: '#10b981',
      error: '#ef4444',
      warning: '#eab308',  // Más amarillo en tema cálido
      info: '#14b8a6',     // teal en vez de cyan
    },
  },

  // Tema frío: Teal + grays neutros-fríos
  cool: {
    id: 'cool',
    name: 'Ocean Teal',
    primary: {
      // Basado en #14b8a6 (teal-500)
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
      // Grays muy fríos (blue-gray)
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
      success: '#10b981',
      error: '#ef4444',
      warning: '#f59e0b',
      info: '#0ea5e9',  // Cyan/blue
    },
  },
};

/**
 * Obtiene tema por ID
 */
export const getTheme = (themeId = 'default') => {
  return themes[themeId] || themes.default;
};

/**
 * Lista de temas disponibles para selector
 */
export const availableThemes = Object.values(themes).map(t => ({
  id: t.id,
  name: t.name,
  primaryColor: t.primary[500],
  neutralColor: t.neutral[500],
}));

/**
 * Genera un tema personalizado a partir de un color base
 * 
 * @param {string} baseColor - Color hex (ej: '#FF6B6B')
 * @param {string} neutralTone - 'cool', 'warm', 'neutral'
 * @returns {Object} Definición de tema
 */
export const generateCustomTheme = (baseColor, neutralTone = 'neutral') => {
  const primary = generateShades(baseColor);
  
  // Usar neutral del tema que coincida con el tono
  const neutralPresets = {
    cool: themes.cool.neutral,
    warm: themes.warm.neutral,
    neutral: themes.default.neutral,
  };
  
  return {
    id: 'custom',
    name: 'Custom Theme',
    primary,
    neutral: neutralPresets[neutralTone],
    semantic: themes.default.semantic, // Mantener semánticos estándar
  };
};

export default themes;
```

---

### Archivo: `theme/themeUtils.js` (NUEVO)

```javascript
/**
 * Utilidades para generación de temas
 */

/**
 * Genera escala de shades (50-950) a partir de un color base
 * 
 * @param {string} baseColor - Color hex (ej: '#0EA5E9')
 * @returns {Object} Objeto con shades { 50: '#...', 100: '#...', ... }
 * 
 * Algoritmo simplificado:
 * - Shades claros (50-400): Mezclar con blanco
 * - Base (500): Color original
 * - Shades oscuros (600-950): Mezclar con negro
 */
export const generateShades = (baseColor) => {
  const hex = baseColor.replace('#', '');
  const r = parseInt(hex.slice(0, 2), 16);
  const g = parseInt(hex.slice(2, 4), 16);
  const b = parseInt(hex.slice(4, 6), 16);

  const mix = (color, mixer, ratio) => {
    return Math.round(color * (1 - ratio) + mixer * ratio);
  };

  const toHex = (r, g, b) => {
    return `#${[r, g, b].map(c => c.toString(16).padStart(2, '0')).join('')}`;
  };

  // Shades más claros (mezcla con blanco)
  const lighten = (ratio) => toHex(
    mix(r, 255, ratio),
    mix(g, 255, ratio),
    mix(b, 255, ratio)
  );

  // Shades más oscuros (mezcla con negro)
  const darken = (ratio) => toHex(
    mix(r, 0, ratio),
    mix(g, 0, ratio),
    mix(b, 0, ratio)
  );

  return {
    50: lighten(0.95),
    100: lighten(0.90),
    200: lighten(0.75),
    300: lighten(0.60),
    400: lighten(0.30),
    500: baseColor,      // Color base
    600: darken(0.20),
    700: darken(0.40),
    800: darken(0.60),
    900: darken(0.75),
    950: darken(0.85),
  };
};

/**
 * Convierte RGB a HSL para cálculos más precisos
 * (Implementación completa si se necesita precisión profesional)
 */
export const rgbToHsl = (r, g, b) => {
  r /= 255;
  g /= 255;
  b /= 255;

  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  let h, s, l = (max + min) / 2;

  if (max === min) {
    h = s = 0; // achromatic
  } else {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);

    switch (max) {
      case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
      case g: h = ((b - r) / d + 2) / 6; break;
      case b: h = ((r - g) / d + 4) / 6; break;
    }
  }

  return [h * 360, s * 100, l * 100];
};

/**
 * Convierte HSL a RGB
 */
export const hslToRgb = (h, s, l) => {
  h /= 360;
  s /= 100;
  l /= 100;

  let r, g, b;

  if (s === 0) {
    r = g = b = l; // achromatic
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

  return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
};

export default {
  generateShades,
  rgbToHsl,
  hslToRgb,
};
```

---

### Actualización: `theme/colors.js`

```javascript
// Añadir nuevo helper para neutrals

/**
 * Genera clase Tailwind para colores neutrals del tema
 * 
 * @param {string} type - Tipo de clase ('bg', 'text', 'border')
 * @param {number} shade - Shade del color (50-950)
 * @returns {string} Clase Tailwind (ej: 'bg-neutral-600')
 * 
 * NOTA: Los neutrals ahora cambian según el tema activo
 * 
 * @example
 * getNeutralClass('bg', 100) // → 'bg-neutral-100'
 * getNeutralClass('text', 600) // → 'text-neutral-600'
 */
export const getNeutralClass = (type, shade = 500) => {
  return `${type}-neutral-${shade}`;
};

/**
 * Variante con dark mode
 */
export const getNeutralClassWithDark = (type, lightShade = 100, darkShade = 800) => {
  const base = getNeutralClass(type, lightShade);
  const dark = getNeutralClass(type, darkShade);
  return `${base} dark:${dark}`;
};
```

---

### Actualización: `ThemeContext.jsx`

```javascript
import { createContext, useContext, useState, useEffect } from 'react';
import { getTheme } from './themes';

const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  // Estado para dark mode (ya existe)
  const [isDarkMode, setIsDarkMode] = useState(() => {
    return localStorage.getItem('darkMode') === 'true';
  });

  // ⭐ NUEVO: Estado para tema activo
  const [activeThemeId, setActiveThemeId] = useState(() => {
    return localStorage.getItem('theme') || 'default';
  });

  // Obtener tema activo
  const activeTheme = getTheme(activeThemeId);

  // Cambiar tema
  const changeTheme = (themeId) => {
    setActiveThemeId(themeId);
    localStorage.setItem('theme', themeId);
    
    // Aplicar CSS variables al :root
    applyThemeVariables(getTheme(themeId));
  };

  // Toggle dark mode (ya existe)
  const toggleDarkMode = () => {
    setIsDarkMode(prev => {
      const newValue = !prev;
      localStorage.setItem('darkMode', newValue);
      return newValue;
    });
  };

  // Aplicar variables CSS al documento
  const applyThemeVariables = (theme) => {
    const root = document.documentElement;

    // Aplicar primary colors
    Object.entries(theme.primary).forEach(([shade, color]) => {
      root.style.setProperty(`--color-primary-${shade}`, color);
    });

    // Aplicar neutral colors
    Object.entries(theme.neutral).forEach(([shade, color]) => {
      root.style.setProperty(`--color-neutral-${shade}`, color);
    });

    // Aplicar semantic colors
    root.style.setProperty('--color-success', theme.semantic.success);
    root.style.setProperty('--color-error', theme.semantic.error);
    root.style.setProperty('--color-warning', theme.semantic.warning);
    root.style.setProperty('--color-info', theme.semantic.info);
  };

  // Inicializar tema al montar
  useEffect(() => {
    applyThemeVariables(activeTheme);
  }, [activeThemeId]);

  // Aplicar dark mode class (ya existe)
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  return (
    <ThemeContext.Provider value={{
      isDarkMode,
      toggleDarkMode,
      activeTheme,
      activeThemeId,
      changeTheme,
    }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};
```

---

### Actualización: `tailwind.config.js`

```javascript
export default {
  // ... resto de config
  theme: {
    extend: {
      colors: {
        // ⭐ NUEVO: Usar CSS variables para colores dinámicos
        primary: {
          50: 'var(--color-primary-50, #f0f9ff)',
          100: 'var(--color-primary-100, #e0f2fe)',
          200: 'var(--color-primary-200, #bae6fd)',
          300: 'var(--color-primary-300, #7dd3fc)',
          400: 'var(--color-primary-400, #38bdf8)',
          500: 'var(--color-primary-500, #0ea5e9)',
          600: 'var(--color-primary-600, #0284c7)',
          700: 'var(--color-primary-700, #0369a1)',
          800: 'var(--color-primary-800, #075985)',
          900: 'var(--color-primary-900, #0c4a6e)',
          950: 'var(--color-primary-950, #082f49)',
        },
        
        // ⭐ NUEVO: Neutral scale (reemplaza gray hardcodeado)
        neutral: {
          50: 'var(--color-neutral-50, #f9fafb)',
          100: 'var(--color-neutral-100, #f3f4f6)',
          200: 'var(--color-neutral-200, #e5e7eb)',
          300: 'var(--color-neutral-300, #d1d5db)',
          400: 'var(--color-neutral-400, #9ca3af)',
          500: 'var(--color-neutral-500, #6b7280)',
          600: 'var(--color-neutral-600, #4b5563)',
          700: 'var(--color-neutral-700, #374151)',
          800: 'var(--color-neutral-800, #1f2937)',
          900: 'var(--color-neutral-900, #111827)',
          950: 'var(--color-neutral-950, #030712)',
        },

        // Semantic colors (fijos, no cambian con tema)
        success: {
          // ... (ya existentes)
        },
        error: {
          // ... (ya existentes)
        },
        secondary: {
          // ... (ya existentes)
        },
        accent: {
          // ... (ya existentes)
        },
      },
    },
  },
};
```

---

## 🔄 Plan de Migración de Grays

### Búsqueda y Reemplazo Global

**ANTES**:
```jsx
className="text-gray-600 bg-gray-100 border-gray-200"
```

**DESPUÉS**:
```jsx
className="text-neutral-600 bg-neutral-100 border-neutral-200"
```

### Script de Migración Automática

```powershell
# Reemplazar todas las referencias a gray por neutral
Get-ChildItem frontend/src -Filter *.jsx -Recurse | ForEach-Object {
  $content = Get-Content $_.FullName -Raw
  
  # Reemplazar text-gray-X → text-neutral-X
  $content = $content -replace 'text-gray-(\d+)', 'text-neutral-$1'
  
  # Reemplazar bg-gray-X → bg-neutral-X
  $content = $content -replace 'bg-gray-(\d+)', 'bg-neutral-$1'
  
  # Reemplazar border-gray-X → border-neutral-X
  $content = $content -replace 'border-gray-(\d+)', 'border-neutral-$1'
  
  # Reemplazar ring-gray-X → ring-neutral-X
  $content = $content -replace 'ring-gray-(\d+)', 'ring-neutral-$1'
  
  # Reemplazar divide-gray-X → divide-neutral-X
  $content = $content -replace 'divide-gray-(\d+)', 'divide-neutral-$1'
  
  # Guardar si hubo cambios
  if ($content -ne (Get-Content $_.FullName -Raw)) {
    Set-Content $_.FullName $content -NoNewline
    Write-Host "✓ Migrado: $($_.Name)"
  }
}
```

**Estimado**: ~300 reemplazos automáticos en ~2 minutos

---

## 🎨 Componente: Theme Selector

```jsx
// frontend/src/components/ui/ThemeSelector.jsx
import { useTheme } from '../../theme/ThemeContext';
import { availableThemes } from '../../theme/themes';

export const ThemeSelector = () => {
  const { activeThemeId, changeTheme } = useTheme();

  return (
    <div className="flex gap-2 items-center">
      <span className="text-sm text-neutral-600 dark:text-neutral-400">
        Theme:
      </span>
      
      <div className="flex gap-1">
        {availableThemes.map(theme => (
          <button
            key={theme.id}
            onClick={() => changeTheme(theme.id)}
            className={`
              w-8 h-8 rounded-full border-2 transition-all
              ${activeThemeId === theme.id 
                ? 'border-neutral-900 dark:border-neutral-100 scale-110' 
                : 'border-neutral-300 dark:border-neutral-600'}
            `}
            style={{ backgroundColor: theme.primaryColor }}
            title={theme.name}
            aria-label={`Change theme to ${theme.name}`}
          >
            {activeThemeId === theme.id && (
              <span className="text-white text-xs">✓</span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
};
```

---

## ✅ Beneficios del Nuevo Sistema

### Antes (Sistema Actual)
```jsx
// ❌ Grays hardcodeados - no cambian con tema
<div className="bg-gray-100 text-gray-900 border-gray-200">
```

### Después (Sistema Propuesto)
```jsx
// ✅ Neutrals dinámicos - cambian con tema
<div className="bg-neutral-100 text-neutral-900 border-neutral-200">
```

**Resultado**:
- Tema "Uruguay Blue" → Grays fríos (azulados)
- Tema "Warm Sunset" → Grays cálidos (sepias)
- Tema "Ocean Teal" → Grays neutros-fríos

---

## 📊 Resumen de Esfuerzo

| Tarea | Tiempo Estimado | Archivos |
|-------|-----------------|----------|
| Crear `themes.js` + `themeUtils.js` | 1-2 horas | 2 nuevos |
| Actualizar `ThemeContext.jsx` | 30 min | 1 |
| Actualizar `tailwind.config.js` | 15 min | 1 |
| Script migración gray→neutral | 5 min | - |
| Ejecutar script + validar | 30 min | ~20 |
| Crear `ThemeSelector` component | 45 min | 1 nuevo |
| Testing visual (3 temas × 2 modos) | 1 hora | - |
| Documentación | 30 min | 1 |
| **TOTAL** | **4-5 horas** | **25 archivos** |

---

## 🚀 Roadmap de Implementación

### Fase 1: Infraestructura (1-2 horas)
1. ✅ Crear `theme/themes.js` con 3 temas predefinidos
2. ✅ Crear `theme/themeUtils.js` con función `generateShades`
3. ✅ Actualizar `ThemeContext.jsx` para soportar cambio de tema
4. ✅ Actualizar `tailwind.config.js` con CSS variables

### Fase 2: Migración Gray→Neutral (30 min)
5. ✅ Ejecutar script PowerShell para reemplazo automático
6. ✅ Build y validar que no se rompió nada

### Fase 3: UI para Selección (1 hora)
7. ✅ Crear componente `ThemeSelector`
8. ✅ Integrarlo en Header o Settings
9. ✅ Testing visual de 3 temas

### Fase 4: Documentación (30 min)
10. ✅ Actualizar `THEMING.md` con nuevo sistema
11. ✅ Crear guía de uso para desarrolladores

---

## 🎯 Resultado Final

Con esta arquitectura:

✅ **Cambio de tema afecta TODO**:
- Colores semánticos (primary, success, error)
- Colores neutrals (ex-grays)
- Dark mode funciona en todos los temas

✅ **Extensibilidad**:
- Agregar nuevo tema = definir 2 paletas (primary + neutral)
- Generar tema custom desde color picker
- Persistencia en localStorage

✅ **Mantenibilidad**:
- Un solo lugar para definir temas (`themes.js`)
- Componentes usan helpers (`getNeutralClass`)
- CSS variables permiten cambio dinámico sin rebuild

---

¿Te gusta esta propuesta? ¿Empezamos con la Fase 1 o quieres ajustar algo antes?
