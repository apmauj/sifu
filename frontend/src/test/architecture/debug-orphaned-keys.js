import fs from 'fs';
import path from 'path';

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

function flattenTranslations(obj, prefix = '', out = new Set()) {
  if (obj && typeof obj === 'object' && !Array.isArray(obj)) {
    for (const [k, v] of Object.entries(obj)) {
      flattenTranslations(v, prefix ? `${prefix}.${k}` : k, out);
    }
  } else {
    out.add(prefix);
  }
  return out;
}

function loadLocaleKeys(code) {
  const file = path.join(__dirname, '..', '..', 'locales', `${code}.json`);
  const data = JSON.parse(fs.readFileSync(file, 'utf8'));
  return flattenTranslations(data);
}

// Recolectar archivos fuente (excluyendo tests) desde src root
const SRC_ROOT = path.join(__dirname, '..', '..');
const SOURCE_DIR = path.join(SRC_ROOT, '..'); // subir a src/
const COMPONENT_ROOT = path.join(SOURCE_DIR, 'components');
const HOOKS_ROOT = path.join(SOURCE_DIR, 'hooks');
const CONTEXTS_ROOT = path.join(SOURCE_DIR, 'contexts');
const SERVICES_ROOT = path.join(SOURCE_DIR, 'services');

const scanTargets = [COMPONENT_ROOT, HOOKS_ROOT, CONTEXTS_ROOT, SERVICES_ROOT].filter(p => fs.existsSync(p));
const allFiles = scanTargets.flatMap(p => collectFiles(p));

// Extraer claves usadas en código
const usedKeys = new Set();
for (const file of allFiles) {
  try {
    const content = fs.readFileSync(file, 'utf8');
    extractI18nKeys(content).forEach(k => usedKeys.add(k));
  } catch (e) {
    // Ignorar errores de lectura puntuales
  }
}

// Añadir smoke check para claves plurales
['exchange.currencies_plural.USD','exchange.currencies_plural.EUR','exchange.currencies_plural.ARS','exchange.currencies_plural.BRL'].forEach(k => usedKeys.add(k));

// Cargar todas las claves de traducciones
const esKeys = loadLocaleKeys('es');
const enKeys = loadLocaleKeys('en');
const ptKeys = loadLocaleKeys('pt');

console.log('=== KEYS USADAS EN CÓDIGO ===');
console.log([...usedKeys].sort().join('\n'));

console.log('\n=== KEYS HUÉRFANAS EN ESPAÑOL ===');
const orphanedEs = [];
for (const key of esKeys) {
  if (!usedKeys.has(key)) {
    orphanedEs.push(key);
  }
}
console.log(orphanedEs.sort().join('\n'));

console.log('\n=== KEYS HUÉRFANAS EN INGLÉS ===');
const orphanedEn = [];
for (const key of enKeys) {
  if (!usedKeys.has(key)) {
    orphanedEn.push(key);
  }
}
console.log(orphanedEn.sort().join('\n'));

console.log('\n=== KEYS HUÉRFANAS EN PORTUGUÉS ===');
const orphanedPt = [];
for (const key of ptKeys) {
  if (!usedKeys.has(key)) {
    orphanedPt.push(key);
  }
}
console.log(orphanedPt.sort().join('\n'));
