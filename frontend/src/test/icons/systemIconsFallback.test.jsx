import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

// Helper to create a proxy that returns undefined for any property (so || fallback triggers)
const emptyModuleFactory = () => {
  return new Proxy({}, {
    get: () => undefined,
    has: () => true // pretend property exists to avoid Vitest warning
  });
};

// We need to reset module registry so we can mock heroicons as empty to trigger fallbacks

describe('system_icons fallbacks', () => {
  it('uses fallback <svg> when heroicons exports are missing', async () => {
    vi.resetModules();
    vi.doMock('@heroicons/react/24/outline', () => emptyModuleFactory());
    const icons = await import('../../shared/icons/system_icons.js');
    const { ArrowPathIcon, ArrowDownIcon, MinusIcon, GlobeAltIcon } = icons;
    render(<>
      <ArrowPathIcon />
      <ArrowDownIcon />
      <MinusIcon />
      <GlobeAltIcon />
    </>);
    expect(screen.getByTestId('arrow-path-icon')).toBeInTheDocument();
    expect(screen.getByTestId('arrow-down-icon')).toBeInTheDocument();
    expect(screen.getByTestId('minus-icon')).toBeInTheDocument();
    expect(screen.getByTestId('globe-alt-icon')).toBeInTheDocument();
  });

  it('prefers real heroicon export when available (no fallback testId)', async () => {
    vi.resetModules();
    vi.doMock('@heroicons/react/24/outline', () => {
      const real = {
        ArrowPathIcon: (props) => React.createElement('svg', { 'data-testid': 'real-arrow-path', ...props })
      };
      return new Proxy(real, {
        get: (target, prop) => target[prop],
        has: () => true // report presence to avoid Vitest missing export error
      });
    });
    const icons = await import('../../shared/icons/system_icons.js');
    const { ArrowPathIcon, ArrowUpIcon } = icons;
    render(<>
      <ArrowPathIcon />
      <ArrowUpIcon />
    </>);
    expect(screen.getByTestId('real-arrow-path')).toBeInTheDocument();
    expect(screen.getByTestId('arrow-up-icon')).toBeInTheDocument();
  });
});
