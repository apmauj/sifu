import { useTheme } from '../../contexts/ThemeContext';
import { availableThemes } from '../../theme/themes';

/**
 * ThemeSelector - Selector de tema de color (default/warm/cool)
 * 
 * Muestra botones circulares con el color primary de cada tema.
 * Permite cambiar entre temas predefinidos.
 * El tema activo se marca con un checkmark y escala aumentada.
 */
const ThemeSelector = () => {
  const { activeThemeId, changeColorTheme } = useTheme();

  return (
    <div className="flex items-center gap-3">
      <span className="text-sm font-medium text-neutral-600 dark:text-neutral-400">
        Theme:
      </span>
      
      <div className="flex gap-2">
        {availableThemes.map(theme => {
          const isActive = activeThemeId === theme.id;
          
          return (
            <button
              key={theme.id}
              onClick={() => changeColorTheme(theme.id)}
              className={`
                w-9 h-9 rounded-full border-2 transition-all duration-200
                flex items-center justify-center
                hover:scale-110 active:scale-95
                focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-neutral-400
                dark:focus:ring-offset-neutral-900
                ${isActive 
                  ? 'border-neutral-900 dark:border-neutral-100 scale-110 shadow-lg' 
                  : 'border-neutral-300 dark:border-neutral-600 hover:border-neutral-400 dark:hover:border-neutral-500'
                }
              `}
              style={{ backgroundColor: theme.primaryColor }}
              title={theme.description}
              aria-label={`Change theme to ${theme.name}`}
              aria-pressed={isActive}
            >
              {isActive && (
                <svg
                  className="w-5 h-5 text-white drop-shadow-md"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={3}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              )}
            </button>
          );
        })}
      </div>
      
      {/* Tooltip con nombre del tema activo */}
      <span className="text-xs text-neutral-500 dark:text-neutral-400 hidden sm:inline">
        {availableThemes.find(t => t.id === activeThemeId)?.name}
      </span>
    </div>
  );
};

export default ThemeSelector;
