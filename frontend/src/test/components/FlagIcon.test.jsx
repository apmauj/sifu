import React from 'react';
import { render } from '@testing-library/react';
import FlagIcon from '../../shared/components/icons/FlagIcon';

describe('FlagIcon', () => {
  it('renders known flag (US)', () => {
    const { container } = render(<FlagIcon country="US" />);
    expect(container.querySelector('svg')).toBeInTheDocument();
  });
  it('falls back to WORLD for unknown code', () => {
    const { container } = render(<FlagIcon country="ZZ" />);
    expect(container.querySelector('svg')).toBeInTheDocument();
  });
});
