import React from 'react';

// Legacy FlagIcon removido (usar Flag de icons/flags.jsx)

export const BankIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg viewBox="0 0 24 24" className={className} fill="currentColor" {...props}>
    <path d="M12 2L2 7v10c0 5.55 3.84 9.74 9 11 5.16-1.26 9-5.45 9-11V7l-10-5zM12 15c-1.4 0-2.8-1.1-2.8-2.5V11c0-1.4 1.4-2.5 2.8-2.5s2.8 1.1 2.8 2.5v1.5c0 1.4-1.4 2.5-2.8 2.5z"/>
  </svg>
);

export const ExchangeIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg viewBox="0 0 24 24" className={className} fill="currentColor" {...props}>
    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
  </svg>
);

export const ChartIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg viewBox="0 0 24 24" className={className} fill="currentColor" {...props}>
    <path d="M3.5 18.49l6-6.01 4 4L22 6.92l-1.41-1.41-7.09 7.97-4-4L2 16.99z"/>
  </svg>
);

export const CalculatorIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg viewBox="0 0 24 24" className={className} fill="currentColor" {...props}>
    <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/>
  </svg>
);

export const SearchIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg viewBox="0 0 24 24" className={className} fill="currentColor" {...props}>
    <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
  </svg>
);

export const RefreshIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg viewBox="0 0 24 24" className={className} fill="currentColor" {...props}>
    <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
  </svg>
);

export const LoadingIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg viewBox="0 0 24 24" className={`animate-spin ${className}`} fill="currentColor" {...props}>
    <path d="M12 4V2A10 10 0 0 0 2 12h2a8 8 0 0 1 8-8Z"/>
  </svg>
);

export const RetryIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg viewBox="0 0 24 24" className={className} fill="currentColor" {...props}>
    <path d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/>
  </svg>
);

export const TodayIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg viewBox="0 0 24 24" className={className} fill="currentColor" {...props}>
    <path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z"/>
  </svg>
);

export const WeekIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg viewBox="0 0 24 24" className={className} fill="currentColor" {...props}>
    <path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11z"/>
  </svg>
);

export const SummaryIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg viewBox="0 0 24 24" className={className} fill="currentColor" {...props}>
    <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/>
  </svg>
); 