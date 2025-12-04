// OpenMoji Calendar (U+1F4C5) - adapted for React
// Attribution: OpenMoji – the open-source emoji and icon project. License: CC BY-SA 4.0
import React from 'react';

const CalendarOpenMoji = ({ className, ...rest }) => (
  <svg
    className={className}
    data-testid="calendar-icon"
    viewBox="0 0 72 72"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
    {...rest}
  >
    <rect x="12" y="16" width="48" height="44" rx="4" fill="white" stroke="#000" strokeWidth="2" />
    <rect x="12" y="16" width="48" height="12" rx="4" fill="#EA5A47" stroke="#000" strokeWidth="2" />
    <line x1="24" y1="10" x2="24" y2="22" stroke="#000" strokeWidth="2.5" strokeLinecap="round" />
    <line x1="48" y1="10" x2="48" y2="22" stroke="#000" strokeWidth="2.5" strokeLinecap="round" />
    {[0,1,2].map(i => (
      <rect key={'t'+i} x={22 + i*10} y={36} width={6} height={6} rx={1.5} fill="#EA5A47" />
    ))}
    {[0,1,2].map(i => (
      <rect key={'b'+i} x={22 + i*10} y={48} width={6} height={6} rx={1.5} fill="#EA5A47" opacity={0.7} />
    ))}
  </svg>
);

export default CalendarOpenMoji;
