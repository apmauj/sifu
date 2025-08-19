import React from 'react';
import flagUS from './flags/Flag_of_the_United_States.png';
import flagAR from './flags/Flag_of_Argentina.png';
import flagBR from './flags/Flag_of_Brazil.png';
import flagUY from './flags/Flag_of_Uruguay.png';
import flagEU from './flags/Flag_of_Europe.png';

const IMG_PROPS = { width: 32, height: 24 };

const FlagImg = ({ src, alt, className = '', ...rest }) => (
	<img
		src={src}
		alt={`${alt} flag`}
		loading="lazy"
		width={IMG_PROPS.width}
		height={IMG_PROPS.height}
		className={`flag-icon ${className}`.trim()}
		decoding="async"
		{...rest}
	/>
);

export const Flag = ({ code, className }) => {
	const map = {
		USD: flagUS, US: flagUS,
		EUR: flagEU, EU: flagEU,
		ARS: flagAR, AR: flagAR,
		BRL: flagBR, BR: flagBR,
		UY: flagUY, UYU: flagUY
	};
	const src = map[code] || flagEU;
	return <FlagImg src={src} alt={code} className={className} />;
};
