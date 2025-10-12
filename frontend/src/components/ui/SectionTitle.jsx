import React from 'react';

const SectionTitle = ({ title, subtitle, className = '' }) => (
  <div className={`mb-6 ${className}`}>
    <h2 className="text-xl font-semibold text-neutral-900">{title}</h2>
    {subtitle && <p className="mt-1 text-sm text-neutral-600">{subtitle}</p>}
  </div>
);

export default SectionTitle;
