import React from 'react';
import { MoonIcon, SunIcon } from '../../icons';

const ThemeToggle = () => {
  const [isDark, setIsDark] = React.useState(false);

  React.useEffect(() => {
    // Initialize from localStorage or system
    const stored = localStorage.getItem('theme');
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initialDark = stored ? stored === 'dark' : prefersDark;
    setIsDark(initialDark);
    document.documentElement.classList.toggle('dark', initialDark);
  }, []);

  const toggle = () => {
    const next = !isDark;
    setIsDark(next);
    document.documentElement.classList.toggle('dark', next);
    localStorage.setItem('theme', next ? 'dark' : 'light');
  };

  return (
    <button
      onClick={toggle}
      aria-label="Toggle theme"
      className="inline-flex items-center justify-center w-9 h-9 rounded-lg border border-gray-200 dark:border-gray-700 bg-white/80 dark:bg-gray-800/80 hover:bg-white hover:shadow-sm transition-all"
    >
      {isDark ? (
        <SunIcon className="w-5 h-5 text-yellow-400" />
      ) : (
        <MoonIcon className="w-5 h-5 text-gray-700" />
      )}
    </button>
  );
};

export default ThemeToggle;
