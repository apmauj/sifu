import React from 'react';
import { MoonIcon, SunIcon } from '../../icons';
import { useTheme } from '../../contexts/ThemeContext';

const ThemeToggle = () => {
  const { theme, toggleTheme, isDark } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      aria-pressed={isDark}
      title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      className="inline-flex items-center justify-center w-9 h-9 rounded-lg 
                 border border-neutral-200 dark:border-neutral-700 
                 bg-white/80 dark:bg-neutral-800/80 
                 hover:bg-primary-50 dark:hover:bg-primary-950/50
                 hover:border-primary-300 dark:hover:border-primary-700
                 hover:shadow-sm 
                 transition-all duration-200"
    >
      {isDark ? (
        <SunIcon className="w-5 h-5 text-secondary-400 transition-transform hover:rotate-45" />
      ) : (
        <MoonIcon className="w-5 h-5 text-primary-700 transition-transform hover:-rotate-12" />
      )}
    </button>
  );
};

export default ThemeToggle;
