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
        ? 'text-blue-700 dark:text-blue-300 bg-blue-50 dark:bg-blue-950/30 ring-1 ring-inset ring-blue-200 dark:ring-blue-800'
        : 'text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-neutral-100 hover:bg-neutral-100 dark:hover:bg-neutral-700'}
    `}
  >
    {Icon && <Icon className={`w-4 h-4 ${active ? 'text-blue-700 dark:text-blue-300' : 'text-neutral-500 dark:text-neutral-400 group-hover:text-neutral-700 dark:group-hover:text-neutral-300'}`} />}
    <span>{children}</span>
  </button>
);
