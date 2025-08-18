import React from 'react';
import { render } from '@testing-library/react';
import {
  BankIcon,
  ExchangeIcon,
  ChartIcon,
  CalculatorIcon,
  SearchIcon,
  RefreshIcon,
  LoadingIcon,
  RetryIcon,
  TodayIcon,
  WeekIcon,
  SummaryIcon
} from '../../components/icons/SimpleIcons';

describe('SimpleIcons basic render', () => {
  const cases = [
    BankIcon,
    ExchangeIcon,
    ChartIcon,
    CalculatorIcon,
    SearchIcon,
    RefreshIcon,
    LoadingIcon,
    RetryIcon,
    TodayIcon,
    WeekIcon,
    SummaryIcon
  ];

  it('renders all icons without crashing', () => {
    cases.forEach(Icon => {
      const { container, unmount } = render(<Icon data-testid={Icon.name} />);
      // Ensure an svg is present
      expect(container.querySelector('svg')).toBeTruthy();
      unmount();
    });
  });

  it('applies custom className', () => {
    const { container } = render(<BankIcon className="w-10 h-10 custom" />);
    const svg = container.querySelector('svg');
    expect(svg).toHaveClass('w-10', 'h-10', 'custom');
  });
});
