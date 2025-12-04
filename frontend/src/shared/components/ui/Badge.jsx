import React from 'react';
import { getComponentVariant } from '../../theme/colors';

/**
 * Badge Component
 * 
 * Componente reutilizable para mostrar badges/etiquetas con colores semánticos
 * Reemplaza todas las instancias inline de badges dispersas en la app
 * 
 * @param {Object} props
 * @param {string} props.variant - Variante semántica: 'success' | 'error' | 'warning' | 'info' | 'neutral' | 'primary'
 * @param {React.ReactNode} props.children - Contenido del badge
 * @param {string} props.size - Tamaño: 'sm' | 'md' | 'lg'
 * @param {string} props.className - Clases adicionales
 * @param {boolean} props.rounded - Si debe ser completamente redondeado (pill shape)
 * 
 * @example
 * // Badge de éxito
 * <Badge variant="success">Fresh</Badge>
 * 
 * @example
 * // Badge de error pequeño
 * <Badge variant="error" size="sm">Failed</Badge>
 * 
 * @example
 * // Badge personalizado
 * <Badge variant="info" rounded className="ml-2">New</Badge>
 */
const Badge = ({ 
  variant = 'neutral', 
  children, 
  size = 'md',
  className = '',
  rounded = true,
  ...props 
}) => {
  // Obtener clases de color desde el sistema semántico
  const colorClasses = getComponentVariant('badge', variant);
  
  // Clases de tamaño
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base',
  };

  // Clases de forma
  const shapeClasses = rounded ? 'rounded-full' : 'rounded';

  return (
    <span
      className={`
        inline-flex items-center justify-center
        font-medium
        transition-colors duration-200
        ${colorClasses}
        ${sizeClasses[size]}
        ${shapeClasses}
        ${className}
      `}
      {...props}
    >
      {children}
    </span>
  );
};

/**
 * Badge con ícono
 * Variante del Badge que incluye un ícono a la izquierda
 */
export const BadgeWithIcon = ({ 
  variant = 'neutral', 
  icon, 
  children, 
  ...props 
}) => {
  return (
    <Badge variant={variant} {...props}>
      {icon && <span className="mr-1">{icon}</span>}
      {children}
    </Badge>
  );
};

/**
 * Badge de contador
 * Variante optimizada para mostrar números (notificaciones, contadores)
 */
export const CountBadge = ({ 
  count = 0, 
  variant = 'primary',
  max = 99,
  ...props 
}) => {
  const displayCount = count > max ? `${max}+` : count;
  
  return (
    <Badge 
      variant={variant} 
      size="sm" 
      rounded 
      {...props}
    >
      {displayCount}
    </Badge>
  );
};

/**
 * Badge de estado (con punto de color)
 * Útil para indicar estados online/offline, activo/inactivo
 */
export const StatusBadge = ({ 
  variant = 'success',
  label,
  showDot = true,
  ...props 
}) => {
  return (
    <Badge variant={variant} {...props}>
      {showDot && (
        <span className="w-2 h-2 rounded-full bg-current mr-1.5 animate-pulse" />
      )}
      {label}
    </Badge>
  );
};

export default Badge;
