import React from 'react';

export default function Card({ className = '', children }) {
  return (
    <div className={`rounded-2xl 
                     border border-neutral-200/60 dark:border-neutral-700/40 
                     bg-white dark:bg-neutral-800 
                     shadow-sm hover:shadow-md 
                     transition-shadow duration-200 
                     ${className}`}>
      {children}
    </div>
  );
}

export function CardHeader({ title, subtitle, right, className = '' }) {
  return (
    <div className={`px-6 py-5 
                     border-b border-neutral-100/80 dark:border-neutral-700/60 
                     flex items-start justify-between 
                     ${className}`}>
      <div>
        {title && (
          <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-50">
            {title}
          </h3>
        )}
        {subtitle && (
          <p className="mt-1 text-sm text-neutral-600 dark:text-neutral-400">
            {subtitle}
          </p>
        )}
      </div>
      {right}
    </div>
  );
}

export function CardBody({ children, className = '' }) {
  return <div className={`px-6 py-5 ${className}`}>{children}</div>;
}
