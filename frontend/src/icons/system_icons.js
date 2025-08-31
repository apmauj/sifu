// Fachada central de íconos del sistema (Heroicons)
// Nota: Usamos fallback a <svg> mínimo cuando el mock de pruebas
// no define el ícono solicitado para evitar errores en Vitest.

import * as Outline from '@heroicons/react/24/outline';
import React from 'react';
import CalendarOpenMoji from './openmoji/CalendarOpenMoji';
// Reemplazamos la bandera de Uruguay por PNG para simplificar (evitar problemas SVG / parsing)
import flagUruguayPng from './flags/Flag_of_Uruguay.png';

const makeFallback = (testId) => {
  const FallbackIcon = (props) => React.createElement('svg', { 'data-testid': testId, ...props });
  FallbackIcon.displayName = `FallbackIcon(${testId})`;
  return FallbackIcon;
};

export const ArrowPathIcon = Outline.ArrowPathIcon || makeFallback('arrow-path-icon');
export const ArrowDownIcon = Outline.ArrowDownIcon || makeFallback('arrow-down-icon');
export const ArrowUpIcon = Outline.ArrowUpIcon || makeFallback('arrow-up-icon');
export const MinusIcon = Outline.MinusIcon || makeFallback('minus-icon');
export const MagnifyingGlassIcon = Outline.MagnifyingGlassIcon || makeFallback('magnifying-glass-icon');
export const XMarkIcon = Outline.XMarkIcon || makeFallback('x-mark-icon');
export const CheckCircleIcon = Outline.CheckCircleIcon || makeFallback('check-circle-icon');
export const ExclamationCircleIcon = Outline.ExclamationCircleIcon || makeFallback('exclamation-circle-icon');
export const InformationCircleIcon = Outline.InformationCircleIcon || makeFallback('information-circle-icon');
export const ExclamationTriangleIcon = Outline.ExclamationTriangleIcon || makeFallback('exclamation-triangle-icon');
export const ChartBarIcon = Outline.ChartBarIcon || makeFallback('chart-bar-icon');
// OpenMoji custom icons with larger (24px) default size; caller can override via Tailwind className
export const CalendarIcon = ({ className = 'w-6 h-6', ...props }) => React.createElement(CalendarOpenMoji, { className, ...props });
CalendarIcon.displayName = 'CalendarIcon';

export const UruguayFlagIcon = ({ className = 'flag-icon', alt = 'Uruguay', ...props }) =>
	React.createElement('img', {
		src: flagUruguayPng,
		alt: `${alt} flag`,
		'data-testid': 'uruguay-flag-icon',
		loading: 'lazy',
		width: 32,
		height: 24,
		className,
		style: { objectFit: 'cover' },
		decoding: 'async',
		...props
	});
UruguayFlagIcon.displayName = 'UruguayFlagIcon';
export const ClockIcon = Outline.ClockIcon || makeFallback('clock-icon');
export const BanknotesIcon = Outline.BanknotesIcon || makeFallback('banknotes-icon');
export const CurrencyDollarIcon = Outline.CurrencyDollarIcon || makeFallback('currency-dollar-icon');
export const GlobeAltIcon = Outline.GlobeAltIcon || makeFallback('globe-alt-icon');
export const MoonIcon = Outline.MoonIcon || makeFallback('moon-icon');
export const SunIcon = Outline.SunIcon || makeFallback('sun-icon');


