import React from 'react';
import { render } from '@testing-library/react';
import { OpenMojiIcon } from '../../icons/openmoji/index.jsx';

describe('OpenMojiIcon', () => {
  it('renders calculator icon', () => {
    const { container } = render(<OpenMojiIcon name="calculator" size={32} aria-label="calc" />);
    expect(container.querySelector('svg')).toHaveAttribute('role','img');
  });
  it('returns null for unknown icon', () => {
    const { container } = render(<OpenMojiIcon name="unknown123" />);
    expect(container.firstChild).toBeNull();
  });
});
