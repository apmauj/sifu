// Fachada central de íconos del sistema (Heroicons)
// Nota: Usamos fallback a <svg> mínimo cuando el mock de pruebas
// no define el ícono solicitado para evitar errores en Vitest.

import * as Outline from '@heroicons/react/24/outline';
import React from 'react';

const makeFallback = (testId) => (props) => React.createElement('svg', { 'data-testid': testId, ...props });

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
// Calendario: reemplazamos el de Heroicons por una versión OpenMoji simplificada inline
// Fuente base: OpenMoji calendar (licencia CC BY-SA 4.0) adaptado y minimizado
export const CalendarIcon = (props) => (
	<svg
		data-testid="calendar-icon"
		viewBox="0 0 72 72"
		fill="none"
		xmlns="http://www.w3.org/2000/svg"
		{...props}
	>
		<rect x="8" y="14" width="56" height="50" rx="4" fill="currentColor" opacity="0.08" />
		<rect x="8" y="20" width="56" height="44" rx="4" stroke="currentColor" strokeWidth="4" fill="none" />
		<line x1="20" y1="10" x2="20" y2="24" stroke="currentColor" strokeWidth="4" strokeLinecap="round" />
		<line x1="52" y1="10" x2="52" y2="24" stroke="currentColor" strokeWidth="4" strokeLinecap="round" />
		<rect x="22" y="32" width="8" height="8" rx="2" fill="currentColor" />
		<rect x="34" y="32" width="8" height="8" rx="2" fill="currentColor" />
		<rect x="46" y="32" width="8" height="8" rx="2" fill="currentColor" />
		<rect x="22" y="44" width="8" height="8" rx="2" fill="currentColor" />
		<rect x="34" y="44" width="8" height="8" rx="2" fill="currentColor" />
		<rect x="46" y="44" width="8" height="8" rx="2" fill="currentColor" />
	</svg>
);

// Bandera de Uruguay (simplificada). Usamos un SVG estilizado para evitar depender del emoji en algunos sistemas.
export const UruguayFlagIcon = (props) => (
	<svg
		data-testid="uruguay-flag-icon"
		viewBox="0 0 640 480"
		xmlns="http://www.w3.org/2000/svg"
		{...props}
	>
		<rect width="640" height="480" fill="#fff" />
		<g fill="#0038a8">
			<rect y="60" width="640" height="60" />
			<rect y="180" width="640" height="60" />
			<rect y="300" width="640" height="60" />
			<rect y="420" width="640" height="60" />
		</g>
		<g transform="translate(100 100) scale(40)">
			<circle r="1" fill="#fcd116" />
			<g stroke="#fcd116" strokeWidth="0.15">
				<line y1="-1.3" y2="1.3" />
				<line x1="-1.3" x2="1.3" />
				<line x1="-0.92" y1="-0.92" x2="0.92" y2="0.92" />
				<line x1="-0.92" y1="0.92" x2="0.92" y2="-0.92" />
			</g>
		</g>
	</svg>
);
export const ClockIcon = Outline.ClockIcon || makeFallback('clock-icon');
export const BanknotesIcon = Outline.BanknotesIcon || makeFallback('banknotes-icon');
export const CurrencyDollarIcon = Outline.CurrencyDollarIcon || makeFallback('currency-dollar-icon');
export const GlobeAltIcon = Outline.GlobeAltIcon || makeFallback('globe-alt-icon');
export const MoonIcon = Outline.MoonIcon || makeFallback('moon-icon');
export const SunIcon = Outline.SunIcon || makeFallback('sun-icon');


