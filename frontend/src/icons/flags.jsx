import React from 'react';

const baseProps = {
	role: 'img',
	focusable: 'false',
	'aria-hidden': 'true',
	width: 24,
	height: 18,
	viewBox: '0 0 24 18'
};

export const USFlag = (props) => (
	<svg {...baseProps} {...props}>
		<rect width="24" height="18" fill="#b22234" />
		{[...Array(6)].map((_, i) => (
			<rect key={i} y={i * 3 + 1.5} width="24" height="1" fill="#fff" />
		))}
		<rect width="10.5" height="7.5" fill="#3c3b6e" />
		{[...Array(9)].map((_, i) => (
			<circle key={i} cx={1.2 + (i % 3) * 3.5} cy={1 + Math.floor(i / 3) * 1.5} r={0.35} fill="#fff" />
		))}
	</svg>
);

export const ARFlag = (props) => (
	<svg {...baseProps} {...props}>
		<rect width="24" height="18" fill="#74acdf" />
		<rect y={6} width="24" height="6" fill="#fff" />
		<circle cx={12} cy={9} r={2} fill="#f6b40e" />
	</svg>
);

export const BRFlag = (props) => (
	<svg {...baseProps} {...props}>
		<rect width="24" height="18" fill="#009b3a" />
		<polygon points="12,3 21,9 12,15 3,9" fill="#ffdf00" />
		<circle cx={12} cy={9} r={3.5} fill="#002776" />
	</svg>
);

export const UYFlag = (props) => (
	<svg {...baseProps} {...props}>
		<rect width="24" height="18" fill="#fff" />
		{[...Array(4)].map((_, i) => (
			<rect key={i} y={(i * 2 + 1) * 2} width="24" height="2" fill="#0038a8" />
		))}
		<rect width="8" height="8" fill="#fff" />
		<circle cx={4} cy={4} r={2.5} fill="#f1c40f" />
	</svg>
);

export const EUFlag = (props) => (
	<svg {...baseProps} {...props}>
		<rect width="24" height="18" fill="#003399" />
		{[...Array(12)].map((_, i) => (
			<circle key={i} cx={12 + Math.cos((i * 30) * Math.PI/180) * 5} cy={9 + Math.sin((i * 30) * Math.PI/180) * 5} r={0.9} fill="#ffcc00" />
		))}
	</svg>
);

export const Flag = ({ code, className }) => {
	const map = { USD: USFlag, US: USFlag, EUR: EUFlag, EU: EUFlag, ARS: ARFlag, AR: ARFlag, BRL: BRFlag, BR: BRFlag, UY: UYFlag, UYU: UYFlag };
	const Cmp = map[code] || EUFlag;
	return <Cmp className={className} />;
};
