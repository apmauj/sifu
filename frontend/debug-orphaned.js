const fs = require('fs');
const path = require('path');

console.log('Iniciando análisis de keys huérfanas...');

// Función simple para aplanar traducciones
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

try {
  // Cargar traducciones
  const esFile = path.join(__dirname, 'src', 'locales', 'es.json');
  console.log('Cargando archivo:', esFile);
  console.log('Directorio actual:', __dirname);
  console.log('Archivo existe:', fs.existsSync(esFile));
  const esData = JSON.parse(fs.readFileSync(esFile, 'utf8'));
  const esKeys = flattenTranslations(esData);

  console.log('Keys en español encontradas:', esKeys.size);

  // Extraer keys del código
  function extractI18nKeys(content) {
    const regex = /\bt\(\s*['"]([a-zA-Z0-9_.]+)['"]/g;
    const keys = new Set();
    let match;
    while ((match = regex.exec(content)) !== null) {
      keys.add(match[1]);
    }
    return keys;
  }

  // Buscar archivos
  function findFiles(dir, exts = ['.js', '.jsx']) {
    const out = [];
    try {
      const entries = fs.readdirSync(dir, { withFileTypes: true });
      for (const entry of entries) {
        if (entry.name.startsWith('.')) continue;
        const full = path.join(dir, entry.name);
        if (entry.isDirectory()) {
          if (full.includes(path.sep + 'test' + path.sep)) continue;
          if (full.includes(path.sep + '__mocks__' + path.sep)) continue;
          out.push(...findFiles(full, exts));
        } else if (exts.includes(path.extname(entry.name))) {
          out.push(full);
        }
      }
    } catch (e) {
      console.log(`Error leyendo directorio ${dir}:`, e.message);
    }
    return out;
  }

  const srcDir = path.join(__dirname, 'src');
  console.log('Buscando archivos en:', srcDir);
  const allFiles = findFiles(srcDir);
  console.log('Archivos encontrados:', allFiles.length);

  const usedKeys = new Set();
  for (const file of allFiles) {
    try {
      const content = fs.readFileSync(file, 'utf8');
      extractI18nKeys(content).forEach(k => usedKeys.add(k));
    } catch (e) {
      console.log(`Error leyendo ${file}:`, e.message);
    }
  }

  // Añadir smoke check para claves plurales
  ['exchange.currencies_plural.USD','exchange.currencies_plural.EUR','exchange.currencies_plural.ARS','exchange.currencies_plural.BRL'].forEach(k => usedKeys.add(k));

  console.log('Keys usadas en código:', usedKeys.size);

  console.log('\n=== KEYS USADAS EN CÓDIGO ===');
  console.log([...usedKeys].sort().join('\n'));

  console.log('\n=== KEYS HUÉRFANAS EN ESPAÑOL ===');
  const orphaned = [];
  for (const key of esKeys) {
    if (!usedKeys.has(key)) {
      orphaned.push(key);
    }
  }
  console.log(orphaned.sort().join('\n'));
  console.log(`\nTotal huérfanas: ${orphaned.length}`);

} catch (error) {
  console.error('Error general:', error.message);
  console.error(error.stack);
}
