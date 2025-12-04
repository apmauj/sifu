import React from 'react';
import { render } from '@testing-library/react';
import * as Open from '../../shared/icons/openmoji/index.jsx';

// Cover the mapping object and OpenMojiIcon dynamic resolution path

describe('openmoji index.js mapping', () => {
  it('exports mapping with expected keys', () => {
    const expected = ['calculator','bank','chartUp','exchange','ui','flagUY','flagUS','flagEU'];
    expected.forEach(k => {
      expect(Open.openMojiMap[k]).toBeTruthy();
    });
  });

  it('OpenMojiIcon renders null for unknown name', () => {
  const { container } = render(React.createElement(Open.OpenMojiIcon, { name: 'does-not-exist' }));
    expect(container.firstChild).toBeNull();
  });

  it('OpenMojiIcon renders svg for known name', () => {
  const { container } = render(React.createElement(Open.OpenMojiIcon, { name: 'calculator', 'data-testid': 'om-icon' }));
    expect(container.querySelector('svg')).toBeTruthy();
  });
});
