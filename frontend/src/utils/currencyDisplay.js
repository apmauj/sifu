// Centralized currency display configuration for panels (BCU, BROU, others)
// Provides symbol, flag code, translated name and optional special flags.
// Panels can override base symbol/name via PANEL_OVERRIDES.

export const getCurrencyDisplayMap = (t, panel = 'bcu') => {
  const base = {
    USD: { symbol: 'US$', flag: 'USD', nameKey: 'exchange.currencies.USD', defaultName: 'Dólar USA' },
    EUR: { symbol: '€', flag: 'EUR', nameKey: 'exchange.currencies.EUR', defaultName: 'Euro' },
    ARS: { symbol: 'AR$', flag: 'ARS', nameKey: 'exchange.currencies.ARS', defaultName: 'Peso Arg.' },
    BRL: { symbol: 'R$', flag: 'BRL', nameKey: 'exchange.currencies.BRL', defaultName: 'Real' },
  };

  const overrides = {
    // BROU panel has its own wording namespace and keeps generic '$' for USD/ARS; adds USD_EBROU special row
    brou: {
      USD: { symbol: '$', nameKey: 'brou.currencies.USD' },
      USD_EBROU: { symbol: '$', flag: 'USD', nameKey: 'brou.currencies.USD_EBROU', defaultName: 'Dólar eBROU', special: true },
  EUR: { symbol: '$', nameKey: 'brou.currencies.EUR' },
      ARS: { symbol: '$', nameKey: 'brou.currencies.ARS' },
  BRL: { symbol: '$', nameKey: 'brou.currencies.BRL' },
    },
    // BCU (exchange rate) panel just ensures name keys under exchange namespace; symbols from base
    bcu: {
      USD: { nameKey: 'exchange.currencies.USD' },
      EUR: { nameKey: 'exchange.currencies.EUR' },
      ARS: { nameKey: 'exchange.currencies.ARS' },
      BRL: { nameKey: 'exchange.currencies.BRL' },
    },
  };

  const panelOverrides = overrides[panel] || {};
  const result = {};
  // Merge base + overrides
  for (const code of Object.keys(base)) {
    const merged = { ...base[code], ...(panelOverrides[code] || {}) };
    result[code] = {
      symbol: merged.symbol,
      flag: merged.flag,
      special: merged.special,
      name: t(merged.nameKey) || merged.defaultName || code,
    };
  }
  // Add panel-only currencies (e.g., USD_EBROU)
  for (const code of Object.keys(panelOverrides)) {
    if (result[code]) continue;
    const ov = panelOverrides[code];
    result[code] = {
      symbol: ov.symbol || ov.symbol === '' ? ov.symbol : '$',
      flag: ov.flag || code,
      special: ov.special,
      name: t(ov.nameKey) || ov.defaultName || code,
    };
  }
  return result;
};

export default getCurrencyDisplayMap;
