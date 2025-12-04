import React from 'react';
import { getComponentVariant } from '../../theme/colors';

/**
 * Button Component
 * 
 * Componente reutilizable de botón con variantes semánticas centralizadas
 * Reemplaza botones dispersos y asegura consistencia visual
 * 
 * @param {Object} props
 * @param {string} props.variant - Variante: 'primary' | 'secondary' | 'danger' | 'ghost' | 'success'
 * @param {string} props.size - Tamaño: 'sm' | 'md' | 'lg'
 * @param {boolean} props.fullWidth - Si debe ocupar todo el ancho
 * @param {boolean} props.loading - Muestra spinner y desactiva el botón
 * @param {React.ReactNode} props.leftIcon - Ícono a la izquierda
 * @param {React.ReactNode} props.rightIcon - Ícono a la derecha
 * @param {React.ReactNode} props.children - Contenido del botón
 * @param {boolean} props.disabled - Si el botón está deshabilitado
 * @param {string} props.className - Clases adicionales
 * 
 * @example
 * // Botón primario básico
 * <Button variant="primary">Guardar</Button>
 * 
 * @example
 * // Botón con ícono y loading
 * <Button variant="secondary" leftIcon={<Icon />} loading>
 *   Procesando...
 * </Button>
 * 
 * @example
 * // Botón peligroso
 * <Button variant="danger" size="sm" onClick={handleDelete}>
 *   Eliminar
 * </Button>
 */
const Button = ({ 
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  loading = false,
  leftIcon,
  rightIcon,
  children,
  disabled = false,
  className = '',
  type = 'button',
  ...props 
}) => {
  // Obtener clases de color desde el sistema semántico
  const colorClasses = getComponentVariant('button', variant);
  
  // Clases de tamaño
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  // Clases de ancho
  const widthClasses = fullWidth ? 'w-full' : '';

  // Spinner para estado de loading
  const Spinner = () => (
    <svg 
      className="animate-spin h-4 w-4" 
      xmlns="http://www.w3.org/2000/svg" 
      fill="none" 
      viewBox="0 0 24 24"
    >
      <circle 
        className="opacity-25" 
        cx="12" 
        cy="12" 
        r="10" 
        stroke="currentColor" 
        strokeWidth="4"
      />
      <path 
        className="opacity-75" 
        fill="currentColor" 
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );

  return (
    <button
      type={type}
      disabled={disabled || loading}
      className={`
        inline-flex items-center justify-center gap-2
        font-medium rounded-lg
        transition-all duration-200
        disabled:opacity-50 disabled:cursor-not-allowed
        focus:outline-none focus:ring-2 focus:ring-offset-2
        ${colorClasses}
        ${sizeClasses[size]}
        ${widthClasses}
        ${className}
      `}
      {...props}
    >
      {loading ? (
        <>
          <Spinner />
          {children}
        </>
      ) : (
        <>
          {leftIcon && <span className="flex-shrink-0">{leftIcon}</span>}
          {children}
          {rightIcon && <span className="flex-shrink-0">{rightIcon}</span>}
        </>
      )}
    </button>
  );
};

/**
 * ButtonGroup
 * Agrupa múltiples botones con bordes compartidos
 */
export const ButtonGroup = ({ 
  children,
  className = '',
  ...props 
}) => {
  return (
    <div 
      className={`inline-flex rounded-lg shadow-sm ${className}`}
      role="group"
      {...props}
    >
      {React.Children.map(children, (child, index) => {
        if (!React.isValidElement(child)) return child;
        
        const isFirst = index === 0;
        const isLast = index === React.Children.count(children) - 1;
        
        return React.cloneElement(child, {
          className: `
            ${child.props.className || ''}
            ${!isFirst ? '-ml-px' : ''}
            ${!isFirst && !isLast ? 'rounded-none' : ''}
            ${isFirst ? 'rounded-r-none' : ''}
            ${isLast ? 'rounded-l-none' : ''}
          `,
        });
      })}
    </div>
  );
};

/**
 * IconButton
 * Botón optimizado para contener solo un ícono (cuadrado)
 */
export const IconButton = ({ 
  icon,
  variant = 'ghost',
  size = 'md',
  'aria-label': ariaLabel,
  className = '',
  ...props 
}) => {
  const sizeClasses = {
    sm: 'p-1.5',
    md: 'p-2',
    lg: 'p-3',
  };

  const colorClasses = getComponentVariant('button', variant);

  return (
    <button
      aria-label={ariaLabel}
      className={`
        inline-flex items-center justify-center
        rounded-lg
        transition-all duration-200
        disabled:opacity-50 disabled:cursor-not-allowed
        focus:outline-none focus:ring-2 focus:ring-offset-2
        ${colorClasses}
        ${sizeClasses[size]}
        ${className}
      `}
      {...props}
    >
      {icon}
    </button>
  );
};

/**
 * LinkButton
 * Botón estilizado como enlace
 */
export const LinkButton = ({ 
  children,
  className = '',
  ...props 
}) => {
  return (
    <button
      className={`
        inline-flex items-center gap-1
        text-primary-600 hover:text-primary-700
        dark:text-primary-400 dark:hover:text-primary-300
        underline-offset-2 hover:underline
        transition-colors duration-200
        disabled:opacity-50 disabled:cursor-not-allowed
        ${className}
      `}
      {...props}
    >
      {children}
    </button>
  );
};

export default Button;
