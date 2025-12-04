import React from 'react';

const SectionTitle = ({ title, subtitle, className = '' }) => (
  <div className={`mb-6 ${className}`}>
    <h2 className="text-xl font-semibold text-neutral-900 dark:text-neutral-100">{title}</h2>
    {subtitle && <p className="mt-1 text-sm text-neutral-600 dark:text-neutral-400">{subtitle}</p>}
  </div>
);

export default SectionTitle;
