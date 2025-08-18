import fs from 'fs';
import path from 'path';
import { describe, it, expect } from 'vitest';

const LOCALES_DIR = path.join(__dirname, '..', '..', 'locales');
const BASE_LOCALE = 'es'; // Referencia canónica
const LOCALES = ['en', 'pt']; // Idiomas a comparar contra la base

function flatten(obj, prefix = '', out = {}) {
  if (obj && typeof obj === 'object' && !Array.isArray(obj)) {
    for (const [k, v] of Object.entries(obj)) {
      flatten(v, prefix ? `${prefix}.${k}` : k, out);
    }
  } else {
    out[prefix] = true;
  }
  return out;
}

function loadLocale(code) {
  const file = path.join(LOCALES_DIR, `${code}.json`);
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

const baseData = loadLocale(BASE_LOCALE);
const baseFlat = flatten(baseData);

// Allowlist de claves que intencionalmente pueden faltar (p.ej. aún no traducidas).
// Mantener curta y revisarla periódicamente.
const ALLOW_MISSING = new Set([
  // Ejemplo: 'exchange.currencies_plural.ARS' (si temporal)
]);

// Allowlist de claves extra permitidas en otros idiomas (raro, pero posible).
const ALLOW_EXTRA = new Set([
]);

describe('Arquitectura I18n - Paridad de claves', () => {
  for (const locale of LOCALES) {
    it(`locale '${locale}' no debe tener claves faltantes ni sobrantes`, () => {
      const data = loadLocale(locale);
      const flat = flatten(data);
      const missing = [];
      const extra = [];

      // Claves que existen en base y faltan en este locale
      for (const key of Object.keys(baseFlat)) {
        if (!(key in flat) && !ALLOW_MISSING.has(key)) missing.push(key);
      }
      // Claves que existen en este locale y no en base
      for (const key of Object.keys(flat)) {
        if (!(key in baseFlat) && !ALLOW_EXTRA.has(key)) extra.push(key);
      }

      const messages = [];
      if (missing.length) {
        messages.push(`FALTAN (${missing.length})\n - ` + missing.sort().join('\n - '));
      }
      if (extra.length) {
        messages.push(`EXTRA (${extra.length})\n - ` + extra.sort().join('\n - '));
      }

      const hint = messages.length ? `\nDesfase en locale '${locale}':\n${messages.join('\n\n')}\n` : '';
      expect(messages.length === 0, hint).toBe(true);
    });
  }
});
