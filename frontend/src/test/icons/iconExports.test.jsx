import React from 'react';
import { render, screen } from '@testing-library/react';
// This import exercises components/icons/index.js re-export barrel
import { ExchangeIcon, BankIcon } from '../../shared/components/icons';

describe('components/icons barrel export', () => {
  it('renders a couple of icons via barrel', () => {
    render(<><ExchangeIcon data-testid="exchange-icon" /><BankIcon data-testid="bank-icon" /></>);
    expect(screen.getByTestId('exchange-icon').tagName.toLowerCase()).toBe('svg');
    expect(screen.getByTestId('bank-icon').tagName.toLowerCase()).toBe('svg');
  });
});
