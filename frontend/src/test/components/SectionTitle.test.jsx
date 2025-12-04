import React from 'react';
import { render, screen } from '@testing-library/react';
import SectionTitle from '../../shared/components/ui/SectionTitle';

describe('SectionTitle', () => {
  it('renders title and subtitle', () => {
    render(<SectionTitle title="Main Title" subtitle="Sub text" />);
    expect(screen.getByText('Main Title')).toBeInTheDocument();
    expect(screen.getByText('Sub text')).toBeInTheDocument();
  });

  it('renders only title when no subtitle', () => {
    render(<SectionTitle title="Only Title" />);
    expect(screen.getByText('Only Title')).toBeInTheDocument();
  });
});
