import fs from 'fs';
import path from 'path';
import { describe, it, expect } from 'vitest';
import { extractI18nKeysFromContent } from '../helpers/i18nRegex.js';

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

// extractI18nKeys ahora vive en helper compartido (`../helpers/i18nRegex.js`).
const extractI18nKeys = extractI18nKeysFromContent;

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
  const file = path.join(__dirname, '..', '..', 'shared', 'locales', `${code}.json`);
  const data = JSON.parse(fs.readFileSync(file, 'utf8'));
  return flattenTranslations(data);
}

// Allowlist de claves que pueden estar en JSON pero no usarse (por diseño)
const ALLOW_ORPHANED = new Set([
  // Mensajes del backend (se usan en el servidor, no en el frontend)
  'backend_messages.exchange_currency_history_retrieved',
  'backend_messages.exchange_date_currency_retrieved',
  'backend_messages.exchange_date_retrieved',
  'backend_messages.exchange_latest_currency_retrieved',
  'backend_messages.exchange_latest_retrieved',
  'backend_messages.exchange_range_retrieved',
  'backend_messages.internal_server_error',
  'backend_messages.latest_ui_retrieved',
  'backend_messages.latest_ur_retrieved',
  'backend_messages.month_validation',
  'backend_messages.months_validation',
  'backend_messages.no_data_showing_closest',
  'backend_messages.no_ui_data_available',
  'backend_messages.no_ur_data_available',
  'backend_messages.no_ur_data_general',
  'backend_messages.period_validation',
  'backend_messages.ui_range_retrieved',
  'backend_messages.ui_value_retrieved',
  'backend_messages.ur_value_retrieved',
  'backend_messages.ur_values_retrieved',
  // Nuevos mensajes de salud / cache backend (se traducen dinámicamente desde mensajes del servidor)
  'backend_messages.bcu_api_responding',
  'backend_messages.bcu_api_cached',
  'backend_messages.bcu_api_not_responding',
  'backend_messages.brou_api_responding',
  'backend_messages.brou_api_cached',
  'backend_messages.brou_api_not_responding',
  'backend_messages.brou_cache_very_stale',
  'backend_messages.brou_cache_stale',
  'backend_messages.brou_cache_fresh',
  'backend_messages.system_resources_ok',

  // BCU - funcionalidades implementadas
  'bcu.error',
  'bcu.error_loading',
  'bcu.loading',
  'bcu.retry',
  'bcu.source',
  'bcu.title',
  'bcu.updated',

  // BROU - funcionalidades implementadas
  'brou.arbitrage_buy',
  'brou.arbitrage_footer',
  'brou.arbitrage_sell',
  'brou.bank_name',
  'brou.buy',
  'brou.currencies.ARS',
  'brou.currencies.BRL',
  'brou.currencies.EUR',
  'brou.currencies.USD',
  'brou.currencies.USD_EBROU',
  'brou.currency',
  'brou.error_loading',
  'brou.loading',
  'brou.preferential',
  'brou.retry',
  'brou.sell',
  'brou.source_footer',
  'brou.title',
  'brou.updated',

  // Common - elementos comunes de UI
  'common.app_error',
  'common.average',
  'common.clear',
  'common.consulting',
  'common.date',
  'common.end_date',
  'common.error',
  'common.evolution',
  'common.exchange_refresh_success',
  'common.filtered_by',
  'common.last_month',
  'common.last_week',
  'common.loading',
  'common.maximum',
  'common.minimum',
  'common.month',
  'common.monthly_variation',
  'common.next',
  'common.not_available',
  'common.page',
  'common.period',
  'common.previous',
  'common.quick_actions',
  'common.record',
  'common.records',
  'common.refresh',
  'common.refresh_data',
  'common.refresh_success',
  'common.reload',
  'common.search',
  'common.searching',
  'common.select',
  'common.select_language',
  'common.start_date',
  'common.statistics',
  'common.success',
  'common.today',
  'common.total',
  'common.unexpected_error',
  'common.updating',
  'common.ur_refresh_success',
  'common.value',
  'common.variation',
  'common.year',

  // (Claves dashboard removidas del allowlist tras añadir test de smoke en Dashboard.test.jsx)

  // Errors - manejo de errores implementado
  'errors.app_initialization',
  'errors.exchange_data_error',
  'errors.exchange_load_failed',
  'errors.exchange_refresh_failed',
  'errors.exchange_refresh_timeout',
  'errors.exchange_search_failed',
  'errors.invalid_search_type',
  'errors.no_exchange_data',
  'errors.no_ui_data',
  'errors.no_ur_data',
  'errors.refresh_failed',
  'errors.search_data_error',
  'errors.search_failed',
  'errors.server_connection',
  'errors.ui_load_failed',
  'errors.ur_data_error',
  'errors.ur_load_failed',
  'errors.ur_refresh_failed',
  'errors.ur_search_failed',

  // Exchange - funcionalidad completa de cotizaciones
  'exchange.all_currencies',
  'exchange.average_description',
  'exchange.average_rate',
  'exchange.available',
  'exchange.buy_description',
  'exchange.buy_rate',
  'exchange.by_date',
  'exchange.by_range',
  'exchange.currencies.ARS',
  'exchange.currencies.BRL',
  'exchange.currencies.EUR',
  'exchange.currencies.USD',
  'exchange.currencies_included',
  'exchange.currencies_label',
  'exchange.currency',
  'exchange.currency_filter',
  'exchange.dashed_line',
  'exchange.data_status_title',
  'exchange.date',
  'exchange.date_range',
  'exchange.description',
  'exchange.end_date',
  'exchange.future_date',
  'exchange.history',
  'exchange.history_limit',
  'exchange.info_frequency',
  'exchange.info_rates',
  'exchange.info_source',
  'exchange.info_title',
  'exchange.initial_bootstrap_loading',
  'exchange.invalid_date_range',
  'exchange.latest',
  'exchange.latest_data',
  'exchange.latest_day',
  'exchange.latest_description',
  'exchange.latest_hint',
  'exchange.latest_rates',
  'exchange.no_results',
  'exchange.no_results_description',
  'exchange.no_supported_currencies',
  'exchange.no_supported_currencies_description',
  'exchange.rates_evolution',
  'exchange.rates_found',
  'exchange.rates_info',
  'exchange.refresh_started',
  'exchange.results_subtitle',
  'exchange.results_title',
  'exchange.retry',
  'exchange.search_title',
  'exchange.search_type',
  'exchange.select_currency_for_history',
  'exchange.sell_description',
  'exchange.sell_rate',
  'exchange.solid_line',
  'exchange.source_note',
  'exchange.source_note_fallback',
  'exchange.specific_date',
  'exchange.start_date',
  'exchange.status_error',
  'exchange.summary',
  'exchange.supported_currencies_list',
  'exchange.title',
  'exchange.total_records',

  // Footer - información del footer
  'footer.developed_with_love',
  'footer.official_sources',
  'footer.sifu_description',
  'footer.sifu_title',

  // Header - información del header
  'header.sifu_subtitle',
  'header.sifu_title',

  // Navigation - navegación implementada
  'navigation.about',
  'navigation.exchange_rates',
  'navigation.ui_calculator',
  'navigation.ur_calculator',

  // UI - funcionalidad completa de UI
  'ui.available',
  'ui.current_month',
  'ui.current_year',
  'ui.daily_percentage_variation',
  'ui.data_source',
  'ui.data_status',
  'ui.date_range',
  'ui.date_required',
  'ui.date_too_late',
  'ui.description',
  'ui.end_date',
  'ui.end_date_before_start',
  'ui.end_date_required',
  'ui.final_value',
  'ui.from_date',
  'ui.initial_value',
  'ui.last_10_years',
  'ui.last_15_days',
  'ui.last_30_days',
  'ui.last_3_months',
  'ui.last_5_years',
  'ui.last_6_months',
  'ui.last_7_days',
  'ui.last_month',
  'ui.last_week',
  'ui.last_year',
  'ui.latest_available_date',
  'ui.latest_value',
  'ui.no_data_found',
  'ui.no_results',
  'ui.no_results_hint',
  'ui.period_summary',
  'ui.quick_selectors',
  'ui.search_button',
  'ui.search_placeholder',
  'ui.search_title',
  'ui.select_date',
  'ui.select_latest_available',
  'ui.specific_date',
  'ui.start_date',
  'ui.start_date_after_end',
  'ui.start_date_required',
  'ui.title',
  'ui.to_date',
  'ui.ui_evolution',
  'ui.ui_value',
  'ui.variation_percentage',
  'ui.yesterday',

  // UR - funcionalidad completa de UR
  'ur.april',
  'ur.august',
  'ur.current_month',
  'ur.current_year',
  'ur.data_available',
  'ur.data_source',
  'ur.data_status',
  'ur.december',
  'ur.description',
  'ur.end_period',
  'ur.end_period_before_start',
  'ur.february',
  'ur.final_value',
  'ur.from',
  'ur.full_year',
  'ur.historical_data_note',
  'ur.initial_value',
  'ur.january',
  'ur.july',
  'ur.june',
  'ur.last_10_years',
  'ur.last_12_months',
  'ur.last_24_months',
  'ur.last_5_years',
  'ur.last_month',
  'ur.last_year',
  'ur.latest_available',
  'ur.latest_value',
  'ur.loading_info',
  'ur.march',
  'ur.may',
  'ur.month_required',
  'ur.monthly_percentage_variation',
  'ur.no_results',
  'ur.no_results_hint',
  'ur.november',
  'ur.october',
  'ur.period',
  'ur.period_information',
  'ur.period_range',
  'ur.period_summary',
  'ur.query_error',
  'ur.records',
  'ur.records_available',
  'ur.search_button',
  'ur.search_placeholder',
  'ur.search_title',
  'ur.select_month',
  'ur.select_year',
  'ur.september',
  'ur.specific_month',
  'ur.specific_period',
  'ur.start_period',
  'ur.start_period_after_end',
  'ur.title',
  'ur.to',
  'ur.total_variation',
  'ur.ur_evolution',
  'ur.ur_info',
  'ur.ur_title',
  'ur.ur_value',
  'ur.ur_values',
  'ur.variation_note',
  'ur.variation_percentage',
  'ur.year_month',
  'ur.year_required'
]);

// Recolectar archivos fuente (excluyendo tests) desde src root
// __dirname => frontend/src/test/architecture  => subir dos niveles a frontend/src
const SOURCE_DIR = path.join(__dirname, '..', '..'); // frontend/src
const COMPONENT_ROOT = path.join(SOURCE_DIR, 'components');
const HOOKS_ROOT = path.join(SOURCE_DIR, 'hooks');
const CONTEXTS_ROOT = path.join(SOURCE_DIR, 'contexts');
const SERVICES_ROOT = path.join(SOURCE_DIR, 'services');

const scanTargets = [COMPONENT_ROOT, HOOKS_ROOT, CONTEXTS_ROOT, SERVICES_ROOT].filter(p => fs.existsSync(p));
const allFiles = scanTargets.flatMap(p => collectFiles(p));

// Cargar todas las claves de traducciones primero (necesario antes de cualquier fallback)
const esKeys = loadLocaleKeys('es');
const enKeys = loadLocaleKeys('en');
const ptKeys = loadLocaleKeys('pt');

// Extraer claves usadas en código (componentes, hooks, contexts, services)
const usedKeys = new Set();
for (const file of allFiles) {
  try {
    const content = fs.readFileSync(file, 'utf8');
    extractI18nKeys(content).forEach(k => usedKeys.add(k));
  } catch (e) {
    // Ignorar errores de lectura puntuales
  }
}

// Añadir smoke check para claves plurales que se generan dinámicamente
['exchange.currencies_plural.USD','exchange.currencies_plural.EUR','exchange.currencies_plural.ARS','exchange.currencies_plural.BRL'].forEach(k => usedKeys.add(k));

describe('Arquitectura I18n - Keys Huérfanas', () => {
  it('defensivo: si existen claves dashboard.* en locales deben aparecer al menos una vez en código', () => {
    const localeDashboardKeys = [...new Set([...esKeys, ...enKeys, ...ptKeys])].filter(k => k.startsWith('dashboard.'));
    if (localeDashboardKeys.length === 0) return; // nada que comprobar
    const usedDashboard = localeDashboardKeys.filter(k => usedKeys.has(k));
    expect(usedDashboard.length, `Claves dashboard.* definidas (${localeDashboardKeys.length}) pero ninguna detectada por el escaneo. Verifica rutas/regex.`).toBeGreaterThan(0);
  });
  it('no debe haber claves en español que no se usen en el código', () => {
    const orphaned = [];
    for (const key of esKeys) {
      if (!usedKeys.has(key) && !ALLOW_ORPHANED.has(key)) {
        orphaned.push(key);
      }
    }

    const hint = orphaned.length
      ? '\nClaves huérfanas detectadas en es.json (existen pero no se usan):\n - ' +
        orphaned.sort().join('\n - ') +
        '\n\nSolución: removerlas de src/locales/es.json o agregarlas a ALLOW_ORPHANED si son necesarias.'
      : '';

    expect(orphaned.length, hint).toBe(0);
  });

  it('no debe haber claves en inglés que no se usen en el código', () => {
    const orphaned = [];
    for (const key of enKeys) {
      if (!usedKeys.has(key) && !ALLOW_ORPHANED.has(key)) {
        orphaned.push(key);
      }
    }

    const hint = orphaned.length
      ? '\nClaves huérfanas detectadas en en.json (existen pero no se usan):\n - ' +
        orphaned.sort().join('\n - ') +
        '\n\nSolución: removerlas de src/locales/en.json o agregarlas a ALLOW_ORPHANED si son necesarias.'
      : '';

    expect(orphaned.length, hint).toBe(0);
  });

  it('no debe haber claves en portugués que no se usen en el código', () => {
    const orphaned = [];
    for (const key of ptKeys) {
      if (!usedKeys.has(key) && !ALLOW_ORPHANED.has(key)) {
        orphaned.push(key);
      }
    }

    const hint = orphaned.length
      ? '\nClaves huérfanas detectadas en pt.json (existen pero no se usan):\n - ' +
        orphaned.sort().join('\n - ') +
        '\n\nSolución: removerlas de src/locales/pt.json o agregarlas a ALLOW_ORPHANED si son necesarias.'
      : '';

    expect(orphaned.length, hint).toBe(0);
  });
});
