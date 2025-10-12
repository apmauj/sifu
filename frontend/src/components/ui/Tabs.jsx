import React from 'react';

export const Tabs = ({ value, onChange, children, className = '' }) => (
  <div className={`flex items-center gap-2 overflow-x-auto ${className}`} role="tablist">
    {React.Children.map(children, (child) =>
      React.cloneElement(child, {
        active: child.props.value === value,
        onClick: () => onChange(child.props.value),
      })
    )}
  </div>
);

export const Tab = ({ value, active, onClick, icon: Icon, children }) => (
  <button
    role="tab"
    aria-selected={active}
    onClick={onClick}
    className={`group relative inline-flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium transition-all
      ${active
        ? 'text-blue-700 bg-blue-50 ring-1 ring-inset ring-blue-200'
        : 'text-neutral-600 hover:text-neutral-900 hover:bg-neutral-50'}
    `}
  >
    {Icon && <Icon className={`w-4 h-4 ${active ? 'text-blue-700' : 'text-neutral-500 group-hover:text-neutral-700'}`} />}
    <span>{children}</span>
  </button>
);
