import fs from 'fs';
import path from 'path';
import { describe, it, expect } from 'vitest';

// Helper para recorrer árbol de directorios y obtener archivos fuente
function collectFiles(dir, exts = ['.js', '.jsx']) {
  const out = [];
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    if (entry.name.startsWith('.')) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      // Excluir carpetas de tests y locales para evitar duplicidad
      if (full.includes(path.sep + 'test' + path.sep)) continue;
      if (full.includes(path.sep + '__mocks__' + path.sep)) continue;
      out.push(...collectFiles(full, exts));
    } else if (exts.includes(path.extname(entry.name))) {
      out.push(full);
    }
  }
  return out;
}

function extractI18nKeys(fileContent) {
  // Regex simple: t('some.key') o t("some.key") - ignora plantillas y concatenaciones
  const regex = /\bt\(\s*['"]([a-zA-Z0-9_.]+)['"]/g;
  const keys = new Set();
  let match;
  while ((match = regex.exec(fileContent)) !== null) {
    keys.add(match[1]);
  }
  return keys;
}

function hasNestedKey(obj, keyPath) {
  const parts = keyPath.split('.');
  let ref = obj;
  for (const p of parts) {
    if (ref == null || typeof ref !== 'object' || !(p in ref)) return false;
    ref = ref[p];
  }
  return true;
}

// Allowlist opcional de claves dinámicas que se construyen en runtime y no podemos detectar
const ALLOWLIST = new Set([
  // (vacío por ahora)
]);

// Ruta al archivo de traducciones principal (producción)
const ES_JSON_PATH = path.join(__dirname, '..', '..', 'shared', 'locales', 'es.json');

// Cargar traducciones reales
const translations = JSON.parse(fs.readFileSync(ES_JSON_PATH, 'utf8'));

// Recolectar archivos fuente (excluyendo tests) desde src root
const SRC_ROOT = path.join(__dirname, '..', '..');
const SOURCE_DIR = path.join(SRC_ROOT, '..'); // subir a src/
const COMPONENT_ROOT = path.join(SOURCE_DIR, 'components');
const SHARED_ROOT = path.join(SOURCE_DIR, 'shared');
const HOOKS_ROOT = path.join(SHARED_ROOT, 'hooks');
const CONTEXTS_ROOT = path.join(SHARED_ROOT, 'contexts');
const SERVICES_ROOT = path.join(SOURCE_DIR, 'services');

const scanTargets = [COMPONENT_ROOT, HOOKS_ROOT, CONTEXTS_ROOT, SERVICES_ROOT].filter(p => fs.existsSync(p));

const allFiles = scanTargets.flatMap(p => collectFiles(p));

// Extraer claves usadas
const usedKeys = new Set();
for (const file of allFiles) {
  try {
    const content = fs.readFileSync(file, 'utf8');
    extractI18nKeys(content).forEach(k => usedKeys.add(k));
  } catch (e) {
    // Ignorar errores de lectura puntuales
  }
}

// Añadir un smoke check explícito para las claves plurales que recién agregamos
['exchange.currencies_plural.USD','exchange.currencies_plural.EUR','exchange.currencies_plural.ARS','exchange.currencies_plural.BRL'].forEach(k => usedKeys.add(k));

describe('Arquitectura I18n - Consistencia de claves', () => {
  it('todas las claves detectadas en código tienen traducción en es.json', () => {
    const missing = [];
    for (const key of usedKeys) {
      if (ALLOWLIST.has(key)) continue;
      if (!hasNestedKey(translations, key)) {
        missing.push(key);
      }
    }

    const hint = missing.length
      ? '\nClaves faltantes detectadas: \n - ' + missing.sort().join('\n - ') + '\n\nSolución: agregarlas en src/locales/es.json (y otros idiomas si aplica).'
      : '';

    expect(missing.length, hint).toBe(0);
  });
});
