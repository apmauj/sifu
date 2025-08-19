// OpenMoji Flag Uruguay (U+1F1FA U+1F1FE) - adapted for React
// Attribution: OpenMoji – the open-source emoji and icon project. License: CC BY-SA 4.0
import React from 'react';

const FlagUruguayOpenMoji = ({ className, ...rest }) => (
  <svg
    className={className}
    data-testid="uruguay-flag-icon"
    viewBox="0 0 72 48"
    xmlns="http://www.w3.org/2000/svg"
    role="img"
    aria-label="Uruguay"
    {...rest}
  >
    <rect width="72" height="48" fill="white" stroke="#000" strokeWidth="1" />
    {[1,3,5,7].map(i => (
      <rect key={i} y={i*6} width={72} height={6} fill="#3B88C3" />
    ))}
    <circle cx="14" cy="14" r="6" fill="#FCD116" stroke="#000" strokeWidth="1" />
    {[0,45,90,135].map(a => (
      <line
        key={a}
        x1={14}
        y1={14}
        x2={14 + 8*Math.cos(a*Math.PI/180)}
        y2={14 + 8*Math.sin(a*Math.PI/180)}
        stroke="#FCD116"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
    ))}
  </svg>
);

export default FlagUruguayOpenMoji;
