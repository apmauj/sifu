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
// Calendario (OpenMoji simplificado) sin JSX para evitar parse errors en .js
export const CalendarIcon = (props) => React.createElement(
	'svg',
	{ 'data-testid': 'calendar-icon', viewBox: '0 0 72 72', xmlns: 'http://www.w3.org/2000/svg', ...props },
	[
		// Marco
		React.createElement('rect', { key: 'frame', x: 8, y: 14, width: 56, height: 50, rx: 6, fill: '#FFFFFF', stroke: '#3B82F6', strokeWidth: 3 }),
		// Barra superior (estilo OpenMoji color)
		React.createElement('rect', { key: 'bar', x: 8, y: 14, width: 56, height: 14, rx: 6, fill: '#2563EB' }),
		// Aros
		React.createElement('rect', { key: 'ring1', x: 20-2, y: 10, width: 4, height: 10, rx: 2, fill: '#1E3A8A' }),
		React.createElement('rect', { key: 'ring2', x: 52-2, y: 10, width: 4, height: 10, rx: 2, fill: '#1E3A8A' }),
		// Celdas (dos filas x 3)
		...[22,34,46].map((x,i) => React.createElement('rect', { key: 'top'+i, x, y:34, width:8, height:8, rx:2, fill:'#2563EB', opacity:0.25 })),
		...[22,34,46].map((x,i) => React.createElement('rect', { key: 'bot'+i, x, y:46, width:8, height:8, rx:2, fill:'#2563EB', opacity:0.25 })),
	]
);

// Bandera de Uruguay (simplificada) sin JSX
export const UruguayFlagIcon = (props) => React.createElement(
	'svg',
	{ 'data-testid': 'uruguay-flag-icon', viewBox: '0 0 640 480', xmlns: 'http://www.w3.org/2000/svg', ...props },
	[
		React.createElement('rect', { key: 'bg', width: 640, height: 480, fill: '#fff' }),
		React.createElement('g', { key: 'stripes', fill: '#0038a8' }, [60,180,300,420].map((y,i) => React.createElement('rect', { key: 's'+i, y, width:640, height:60 }))),
		React.createElement('g', { key: 'sunGroup', transform: 'translate(100 100) scale(40)' }, [
			React.createElement('circle', { key: 'sun', r: 1, fill: '#fcd116' }),
			React.createElement('g', { key: 'rays', stroke: '#fcd116', strokeWidth: 0.15 }, [
				React.createElement('line', { key: 'ry1', y1: -1.3, y2: 1.3 }),
				React.createElement('line', { key: 'ry2', x1: -1.3, x2: 1.3 }),
				React.createElement('line', { key: 'ry3', x1: -0.92, y1: -0.92, x2: 0.92, y2: 0.92 }),
				React.createElement('line', { key: 'ry4', x1: -0.92, y1: 0.92, x2: 0.92, y2: -0.92 }),
			])
		])
	]
);
export const ClockIcon = Outline.ClockIcon || makeFallback('clock-icon');
export const BanknotesIcon = Outline.BanknotesIcon || makeFallback('banknotes-icon');
export const CurrencyDollarIcon = Outline.CurrencyDollarIcon || makeFallback('currency-dollar-icon');
export const GlobeAltIcon = Outline.GlobeAltIcon || makeFallback('globe-alt-icon');
export const MoonIcon = Outline.MoonIcon || makeFallback('moon-icon');
export const SunIcon = Outline.SunIcon || makeFallback('sun-icon');


