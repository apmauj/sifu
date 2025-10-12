import React from 'react';
import { getComponentVariant } from '../../theme/colors';

/**
 * Spinner Component
 * 
 * Componente reutilizable para indicadores de carga (loading states)
 * Reemplaza spinners dispersos y asegura consistencia visual
 * 
 * @param {Object} props
 * @param {string} props.variant - Variante de color: 'primary' | 'secondary' | 'white' | 'gray'
 * @param {string} props.size - Tamaño: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
 * @param {string} props.label - Texto opcional junto al spinner
 * @param {boolean} props.center - Si debe centrarse en su contenedor
 * @param {string} props.className - Clases adicionales
 * 
 * @example
 * // Spinner básico
 * <Spinner />
 * 
 * @example
 * // Spinner con etiqueta
 * <Spinner variant="primary" size="lg" label="Cargando datos..." />
 * 
 * @example
 * // Spinner centrado en pantalla
 * <Spinner center size="xl" label="Procesando..." />
 */
const Spinner = ({ 
  variant = 'primary',
  size = 'md',
  label,
  center = false,
  className = '',
  ...props 
}) => {
  // Clases de tamaño
  const sizeClasses = {
    xs: 'w-3 h-3 border-2',
    sm: 'w-4 h-4 border-2',
    md: 'w-6 h-6 border-2',
    lg: 'w-8 h-8 border-3',
    xl: 'w-12 h-12 border-4',
  };

  // Obtener clases de color desde el sistema semántico
  const colorClasses = getComponentVariant('spinner', variant);

  const spinnerElement = (
    <div 
      className={`
        inline-block
        rounded-full
        border-solid
        border-t-transparent
        animate-spin
        ${sizeClasses[size]}
        ${colorClasses}
        ${className}
      `}
      role="status"
      aria-label={label || 'Loading'}
      {...props}
    />
  );

  // Si hay label, mostrar en contenedor flex
  if (label) {
    const containerClasses = center 
      ? 'flex flex-col items-center justify-center gap-3 min-h-[200px]'
      : 'flex items-center gap-3';

    return (
      <div className={containerClasses}>
        {spinnerElement}
        <span className="text-sm text-gray-600 dark:text-gray-400">
          {label}
        </span>
      </div>
    );
  }

  // Si está centrado sin label
  if (center) {
    return (
      <div className="flex items-center justify-center min-h-[200px]">
        {spinnerElement}
      </div>
    );
  }

  return spinnerElement;
};

/**
 * FullPageSpinner
 * Spinner que cubre toda la pantalla con overlay
 */
export const FullPageSpinner = ({ 
  variant = 'primary',
  label = 'Cargando...',
  blur = true,
}) => {
  return (
    <div 
      className={`
        fixed inset-0 z-50
        flex items-center justify-center
        bg-white/80 dark:bg-gray-900/80
        ${blur ? 'backdrop-blur-sm' : ''}
      `}
    >
      <div className="flex flex-col items-center gap-4">
        <Spinner variant={variant} size="xl" />
        <p className="text-lg font-medium text-gray-700 dark:text-gray-300">
          {label}
        </p>
      </div>
    </div>
  );
};

/**
 * InlineSpinner
 * Spinner pequeño para uso inline en textos o botones
 */
export const InlineSpinner = ({ 
  variant = 'primary',
  className = '',
}) => {
  return (
    <Spinner 
      variant={variant} 
      size="sm" 
      className={`align-text-bottom ${className}`}
    />
  );
};

/**
 * SpinnerOverlay
 * Overlay de spinner sobre un contenedor específico (posición relativa)
 */
export const SpinnerOverlay = ({ 
  variant = 'primary',
  label,
  blur = true,
}) => {
  return (
    <div 
      className={`
        absolute inset-0 z-10
        flex items-center justify-center
        bg-white/80 dark:bg-gray-800/80
        ${blur ? 'backdrop-blur-sm' : ''}
        rounded-lg
      `}
    >
      <div className="flex flex-col items-center gap-3">
        <Spinner variant={variant} size="lg" />
        {label && (
          <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
            {label}
          </p>
        )}
      </div>
    </div>
  );
};

/**
 * PulseSpinner
 * Animación de pulso alternativa al spinner rotatorio
 */
export const PulseSpinner = ({ 
  variant = 'primary',
  size = 'md',
  className = '',
}) => {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
  };

  const colorMap = {
    primary: 'bg-primary-600',
    secondary: 'bg-secondary-600',
    white: 'bg-white',
    gray: 'bg-gray-600',
  };

  return (
    <div className={`relative ${sizeClasses[size]} ${className}`}>
      <div 
        className={`
          absolute inset-0 rounded-full 
          ${colorMap[variant]} 
          animate-ping opacity-75
        `}
      />
      <div 
        className={`
          absolute inset-0 rounded-full 
          ${colorMap[variant]}
        `}
      />
    </div>
  );
};

/**
 * DotsSpinner
 * Spinner de puntos animados (estilo "tres puntos")
 */
export const DotsSpinner = ({ 
  variant = 'primary',
  size = 'md',
  className = '',
}) => {
  const dotSizeClasses = {
    sm: 'w-1.5 h-1.5',
    md: 'w-2 h-2',
    lg: 'w-3 h-3',
  };

  const colorMap = {
    primary: 'bg-primary-600',
    secondary: 'bg-secondary-600',
    white: 'bg-white',
    gray: 'bg-gray-600',
  };

  return (
    <div className={`flex items-center gap-1.5 ${className}`}>
      <div 
        className={`
          ${dotSizeClasses[size]} 
          ${colorMap[variant]} 
          rounded-full animate-bounce
        `}
        style={{ animationDelay: '0ms' }}
      />
      <div 
        className={`
          ${dotSizeClasses[size]} 
          ${colorMap[variant]} 
          rounded-full animate-bounce
        `}
        style={{ animationDelay: '150ms' }}
      />
      <div 
        className={`
          ${dotSizeClasses[size]} 
          ${colorMap[variant]} 
          rounded-full animate-bounce
        `}
        style={{ animationDelay: '300ms' }}
      />
    </div>
  );
};

export default Spinner;
