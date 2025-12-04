import React from 'react';

// Reusable circular icon container to keep consistency between single-value cards (UI, UR, etc.)
export const IconCircle = ({ children, size = 64, className = '' }) => {
  const dimension = typeof size === 'number' ? `${size}px` : size;
  return (
    <div
      className={`flex items-center justify-center rounded-full bg-uruguay-blue text-white shadow-sm ${className}`}
      style={{ width: dimension, height: dimension }}
    >
      {children}
    </div>
  );
};

export default IconCircle;
