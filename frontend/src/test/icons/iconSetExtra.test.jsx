import React from 'react';
import { render } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import {
  DateIcon,
  RangeIcon,
  WeekIcon,
  TodayIcon,
  HistoryIcon,
  SummaryIcon,
  RetryIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  GlobeIcon,
  CalendarIcon,
} from '../../shared/components/icons/IconSet.jsx';

// Render the remaining IconSet components not directly covered elsewhere

describe('IconSet extra icons', () => {
  const cases = [
    DateIcon,
    RangeIcon,
    WeekIcon,
    TodayIcon,
    HistoryIcon,
    SummaryIcon,
    RetryIcon,
    TrendingUpIcon,
    TrendingDownIcon,
    GlobeIcon,
    CalendarIcon,
  ];

  it('renders remaining icons without crashing', () => {
    cases.forEach(Cmp => {
      const { container, unmount } = render(<Cmp data-testid={`icon-${Cmp.name}`} />);
      expect(container.querySelector('svg')).toBeTruthy();
      unmount();
    });
  });
});
