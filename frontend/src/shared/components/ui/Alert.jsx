import React from 'react';
import { getComponentVariant } from '../../theme/colors';

/**
 * Alert Component
 * 
 * Componente reutilizable para mostrar alertas/notificaciones con colores semánticos
 * Reemplaza todas las instancias inline de alertas dispersas en la app
 * 
 * @param {Object} props
 * @param {string} props.variant - Variante semántica: 'success' | 'error' | 'warning' | 'info'
 * @param {string} props.title - Título del alert (opcional)
 * @param {React.ReactNode} props.children - Contenido del alert
 * @param {React.ReactNode} props.icon - Ícono personalizado (opcional)
 * @param {Function} props.onClose - Callback para cerrar el alert (muestra botón X si se provee)
 * @param {string} props.className - Clases adicionales
 * 
 * @example
 * // Alert simple
 * <Alert variant="success">Operación exitosa</Alert>
 * 
 * @example
 * // Alert con título y cierre
 * <Alert variant="error" title="Error" onClose={() => {}}>
 *   No se pudo completar la operación
 * </Alert>
 * 
 * @example
 * // Alert con ícono personalizado
 * <Alert variant="warning" icon="⚠️" title="Advertencia">
 *   Los datos pueden estar desactualizados
 * </Alert>
 */
const Alert = ({ 
  variant = 'info', 
  title,
  children, 
  icon,
  onClose,
  className = '',
  ...props 
}) => {
  // Obtener clases de color desde el sistema semántico
  const colorClasses = getComponentVariant('alert', variant);
  
  // Íconos por defecto según variante
  const defaultIcons = {
    success: '✓',
    error: '⚠️',
    warning: '⚠️',
    info: 'ℹ️',
  };

  const displayIcon = icon !== undefined ? icon : defaultIcons[variant];

  return (
    <div
      className={`
        flex items-start gap-3
        p-4 rounded-lg border
        transition-all duration-200
        ${colorClasses}
        ${className}
      `}
      role="alert"
      {...props}
    >
      {/* Ícono */}
      {displayIcon && (
        <div className="flex-shrink-0 text-lg leading-none mt-0.5">
          {displayIcon}
        </div>
      )}

      {/* Contenido */}
      <div className="flex-1 min-w-0">
        {title && (
          <h3 className="text-sm font-semibold mb-1">
            {title}
          </h3>
        )}
        <div className="text-sm">
          {children}
        </div>
      </div>

      {/* Botón de cierre */}
      {onClose && (
        <button
          onClick={onClose}
          className="flex-shrink-0 ml-2 -mr-1 p-1 rounded 
                     hover:bg-black/5 dark:hover:bg-white/5 
                     transition-colors duration-150"
          aria-label="Cerrar"
        >
          <svg 
            className="w-4 h-4" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M6 18L18 6M6 6l12 12" 
            />
          </svg>
        </button>
      )}
    </div>
  );
};

/**
 * Alert compacto
 * Variante más pequeña para notificaciones inline
 */
export const CompactAlert = ({ 
  variant = 'info',
  children,
  icon,
  ...props 
}) => {
  const colorClasses = getComponentVariant('alert', variant);

  return (
    <div
      className={`
        flex items-center gap-2
        px-3 py-2 rounded-md border text-sm
        ${colorClasses}
      `}
      role="alert"
      {...props}
    >
      {icon && <span className="flex-shrink-0">{icon}</span>}
      <span className="flex-1">{children}</span>
    </div>
  );
};

/**
 * Alert con lista
 * Para mostrar múltiples errores o mensajes
 */
export const ListAlert = ({ 
  variant = 'error',
  title = 'Se encontraron los siguientes problemas:',
  items = [],
  ...props 
}) => {
  if (items.length === 0) return null;

  return (
    <Alert variant={variant} title={title} {...props}>
      <ul className="list-disc list-inside space-y-1 mt-2">
        {items.map((item, index) => (
          <li key={index}>{item}</li>
        ))}
      </ul>
    </Alert>
  );
};

/**
 * Alert de carga
 * Para mostrar procesos en curso
 */
export const LoadingAlert = ({ 
  variant = 'info',
  children = 'Cargando...',
  ...props 
}) => {
  return (
    <Alert 
      variant={variant} 
      icon={
        <div className="animate-spin rounded-full h-4 w-4 border-2 border-current border-t-transparent" />
      }
      {...props}
    >
      {children}
    </Alert>
  );
};

export default Alert;
