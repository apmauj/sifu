import { createContext, useContext, useEffect, useState } from 'react';
import { getTheme } from '../theme/themes';

/**
 * Theme Context
 * Manages light/dark theme state AND color theme (default/warm/cool) across the application
 * Persists both preferences in localStorage
 */

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState('light');
  const [mounted, setMounted] = useState(false);
  
  // ⭐ NUEVO: Estado para el tema de color activo (default/warm/cool)
  const [activeThemeId, setActiveThemeId] = useState('default');
  const [activeThemeConfig, setActiveThemeConfig] = useState(getTheme('default'));

  // Initialize theme from localStorage or system preference
  useEffect(() => {
    const stored = localStorage.getItem('theme');
    const prefersDark = window.matchMedia && 
                       window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    const initialTheme = stored || (prefersDark ? 'dark' : 'light');
    setTheme(initialTheme);
    
    // Apply theme to document
    if (initialTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    
    // ⭐ NUEVO: Inicializar tema de color desde localStorage
    const storedColorTheme = localStorage.getItem('colorTheme') || 'default';
    setActiveThemeId(storedColorTheme);
    const themeConfig = getTheme(storedColorTheme);
    setActiveThemeConfig(themeConfig);
    applyThemeVariables(themeConfig);
    
    setMounted(true);
  }, []);

  // Listen to system theme changes
  useEffect(() => {
    if (!mounted) return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleChange = (e) => {
      // Only auto-switch if user hasn't manually set preference
      if (!localStorage.getItem('theme')) {
        const newTheme = e.matches ? 'dark' : 'light';
        setTheme(newTheme);
        document.documentElement.classList.toggle('dark', e.matches);
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [mounted]);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.classList.toggle('dark', newTheme === 'dark');
  };

  const setThemeExplicit = (newTheme) => {
    if (newTheme !== 'light' && newTheme !== 'dark') {
      console.warn(`Invalid theme: ${newTheme}. Must be 'light' or 'dark'.`);
      return;
    }
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.classList.toggle('dark', newTheme === 'dark');
  };

  /**
   * ⭐ NUEVO: Cambia el tema de color (default/warm/cool)
   * Aplica CSS variables al documento para cambio dinámico
   * 
   * @param {string} themeId - ID del tema ('default', 'warm', 'cool')
   */
  const changeColorTheme = (themeId) => {
    const themeConfig = getTheme(themeId);
    setActiveThemeId(themeId);
    setActiveThemeConfig(themeConfig);
    localStorage.setItem('colorTheme', themeId);
    applyThemeVariables(themeConfig);
  };

  /**
   * ⭐ NUEVO: Aplica variables CSS al :root del documento
   * Esto permite que Tailwind use var(--color-primary-500) dinámicamente
   * 
   * @param {Object} themeConfig - Configuración del tema
   */
  const applyThemeVariables = (themeConfig) => {
    const root = document.documentElement;

    // Aplicar primary colors (10 shades: 50-950)
    Object.entries(themeConfig.primary).forEach(([shade, color]) => {
      root.style.setProperty(`--color-primary-${shade}`, color);
    });

    // Aplicar neutral colors (10 shades: 50-950)
    Object.entries(themeConfig.neutral).forEach(([shade, color]) => {
      root.style.setProperty(`--color-neutral-${shade}`, color);
    });

    // Aplicar semantic colors (success, error, warning, info)
    if (themeConfig.semantic) {
      Object.entries(themeConfig.semantic).forEach(([name, color]) => {
        root.style.setProperty(`--color-${name}`, color);
      });
    }
  };

  const value = {
    // Dark mode (existente)
    theme,
    toggleTheme,
    setTheme: setThemeExplicit,
    isDark: theme === 'dark',
    isLight: theme === 'light',
    
    // ⭐ NUEVO: Color theme
    activeThemeId,
    activeTheme: activeThemeConfig,
    changeColorTheme,
  };

  // Prevent flash of unstyled content
  if (!mounted) {
    return null;
  }

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

export default ThemeContext;
