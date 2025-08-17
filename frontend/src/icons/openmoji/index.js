// Minimal OpenMoji colored SVG React components (inlined) for selected icons.
// Source: OpenMoji (https://openmoji.org) – Licensed under CC BY-SA 4.0
// If adding more, keep footprint small and only export what is used.

import React from 'react';

function toSize(s) { return s || 24; }
const baseProps = (props) => ({
  width: toSize(props.size),
  height: toSize(props.size),
  role: 'img',
  'aria-hidden': props['aria-label'] ? undefined : true,
  ...props
});

export const OMCalculator = (props={}) => (
  <svg {...baseProps(props)} viewBox="0 0 72 72">
    <rect x="12" y="12" width="48" height="48" rx="6" fill="#d0cfce" stroke="#000" strokeWidth="2" />
    <rect x="20" y="20" width="32" height="32" fill="#fff" stroke="#000" strokeWidth="1.5" />
    <line x1="28" y1="28" x2="44" y2="28" stroke="#000" strokeWidth="2" />
    <line x1="28" y1="36" x2="44" y2="36" stroke="#000" strokeWidth="2" />
    <line x1="28" y1="44" x2="44" y2="44" stroke="#000" strokeWidth="2" />
  </svg>
);

export const OMBank = (props={}) => (
  <svg {...baseProps(props)} viewBox="0 0 72 72">
    <rect x="10" y="30" width="52" height="30" fill="#d0cfce" stroke="#000" strokeWidth="2" />
    <polygon points="36,14 10,30 62,30" fill="#9b9b9a" stroke="#000" strokeWidth="2" />
    <rect x="20" y="38" width="8" height="14" fill="#fff" stroke="#000" />
    <rect x="32" y="38" width="8" height="14" fill="#fff" stroke="#000" />
    <rect x="44" y="38" width="8" height="14" fill="#fff" stroke="#000" />
  </svg>
);

export const OMChartUp = (props={}) => (
  <svg {...baseProps(props)} viewBox="0 0 72 72">
    <rect x="12" y="12" width="48" height="48" fill="#fff" stroke="#000" strokeWidth="2" />
    <polyline points="20,48 30,36 38,40 50,24" fill="none" stroke="#1f9d55" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
    <polyline points="46,24 50,24 50,28" fill="none" stroke="#1f9d55" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

export const OMCurrencyExchange = (props={}) => (
  <svg {...baseProps(props)} viewBox="0 0 72 72">
    <circle cx="24" cy="36" r="12" fill="#fcea2b" stroke="#000" strokeWidth="2" />
    <text x="24" y="41" fontSize="14" textAnchor="middle" fontFamily="monospace" fill="#000">$</text>
    <circle cx="48" cy="36" r="12" fill="#92d3f5" stroke="#000" strokeWidth="2" />
    <text x="48" y="41" fontSize="14" textAnchor="middle" fontFamily="monospace" fill="#000">€</text>
    <path d="M18 22 L14 18 M18 22 L22 18" stroke="#000" strokeWidth="2" strokeLinecap="round" />
    <path d="M54 50 L50 54 M54 50 L58 54" stroke="#000" strokeWidth="2" strokeLinecap="round" />
  </svg>
);

export const OMUiUnit = OMCalculator; // alias if needed

// Simple flag examples (UY, US, EU) — add others as needed
export const FlagUY = (props={}) => (
  <svg {...baseProps(props)} viewBox="0 0 72 72">
    <rect width="72" height="48" y="12" fill="#fff" stroke="#000" />
    <g fill="#1e50a0">
      <rect y="18" width="72" height="4" />
      <rect y="26" width="72" height="4" />
      <rect y="34" width="72" height="4" />
      <rect y="42" width="72" height="4" />
      <rect y="50" width="72" height="4" />
    </g>
    <circle cx="12" cy="24" r="8" fill="#fcea2b" stroke="#000" />
  </svg>
);

export const FlagUS = (props={}) => (
  <svg {...baseProps(props)} viewBox="0 0 72 72">
    <rect width="72" height="48" y="12" fill="#b22234" stroke="#000" />
    <g fill="#fff">
      <rect y="18" width="72" height="4" />
      <rect y="26" width="72" height="4" />
      <rect y="34" width="72" height="4" />
      <rect y="42" width="72" height="4" />
      <rect y="50" width="72" height="4" />
    </g>
    <rect x="0" y="12" width="28" height="20" fill="#3c3b6e" />
  </svg>
);

export const FlagEU = (props={}) => (
  <svg {...baseProps(props)} viewBox="0 0 72 72">
    <rect width="72" height="48" y="12" fill="#003399" stroke="#000" />
    <g fill="#ffcc00">
      {Array.from({length:12}).map((_,i)=>{
        const angle = (i/12)*Math.PI*2; const cx=36+14*Math.cos(angle); const cy=36+14*Math.sin(angle); return <circle key={i} cx={cx} cy={cy} r={2}/>;})}
    </g>
  </svg>
);

export const openMojiMap = {
  calculator: OMCalculator,
  bank: OMBank,
  chartUp: OMChartUp,
  exchange: OMCurrencyExchange,
  ui: OMUiUnit,
  flagUY: FlagUY,
  flagUS: FlagUS,
  flagEU: FlagEU,
};

export const OpenMojiIcon = ({ name, size=24, ...rest }) => {
  const Cmp = openMojiMap[name];
  if (!Cmp) return null;
  return <Cmp size={size} {...rest} />;
};
