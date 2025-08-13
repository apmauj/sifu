import React from 'react';

export default function Card({ className = '', children }) {
  return (
  <div className={`rounded-2xl border border-gray-200/60 dark:border-gray-800 bg-white dark:bg-gray-800 shadow-sm hover:shadow-md transition-shadow ${className}`}>
      {children}
    </div>
  );
}

export function CardHeader({ title, subtitle, right, className = '' }) {
  return (
  <div className={`px-6 py-5 border-b border-gray-100/80 dark:border-gray-800/60 flex items-start justify-between ${className}`}>
      <div>
        {title && <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{title}</h3>}
        {subtitle && <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">{subtitle}</p>}
      </div>
      {right}
    </div>
  );
}

export function CardBody({ children, className = '' }) {
  return <div className={`px-6 py-5 ${className}`}>{children}</div>;
}
