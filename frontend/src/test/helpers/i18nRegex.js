// Centralized helper for extracting i18n keys: t('namespace.key') or t("namespace.key")
// Keep pattern intentionally strict to avoid false positives with dynamic expressions.
export const I18N_T_CALL_REGEX = /\bt\(\s*['"]([a-zA-Z0-9_.]+)['"]/g;

export function extractI18nKeysFromContent(content) {
  const keys = new Set();
  let m;
  while ((m = I18N_T_CALL_REGEX.exec(content)) !== null) keys.add(m[1]);
  return keys;
}
