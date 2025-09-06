import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';

// Supported languages
const SUPPORTED_LANGUAGES = ['es', 'en', 'pt'];
const DEFAULT_LANGUAGE = 'es';
const FALLBACK_LANGUAGE = 'es';

// Create context
const I18nContext = createContext();

// Hook to use context
export const useI18n = () => {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error('useI18n must be used within an I18nProvider');
  }
  return context;
};

// Helper: deep merge (simple, non-circular) - remote overrides embedded
function deepMerge(base, override) {
  if (!base || typeof base !== 'object') return override;
  if (!override || typeof override !== 'object') return Array.isArray(base) ? [...base] : { ...base };
  const result = Array.isArray(base) ? [...base] : { ...base };
  for (const key of Object.keys(override)) {
    const bv = result[key];
    const ov = override[key];
    if (bv && typeof bv === 'object' && !Array.isArray(bv) && ov && typeof ov === 'object' && !Array.isArray(ov)) {
      result[key] = deepMerge(bv, ov);
    } else {
      result[key] = ov;
    }
  }
  return result;
}

// Preload embedded locales once (Vite eager import)
let EMBEDDED_LOCALES = {};
try {
  const embeddedModules = import.meta.glob('../locales/*.json', { eager: true });
  EMBEDDED_LOCALES = Object.fromEntries(
    Object.entries(embeddedModules).map(([path, mod]) => {
      const name = path.split('/').pop().replace('.json', '');
      return [name, mod.default || mod];
    })
  );
} catch (e) {
  // ignore (tests / build edge)
}

// Context provider
export const I18nProvider = ({ children, forceEmbedded = false }) => {
  const [currentLanguage, setCurrentLanguage] = useState(DEFAULT_LANGUAGE);
  const [translations, setTranslations] = useState(() => {
    if (forceEmbedded) {
      return EMBEDDED_LOCALES[DEFAULT_LANGUAGE] || {};
    }
    return {};
  });
  const [isLoading, setIsLoading] = useState(forceEmbedded ? false : true);
  // Keep a ref to embedded for missing-key checks (avoid re-import cost)
  const embeddedRef = useRef(EMBEDDED_LOCALES);

  // Load translations
  const loadTranslations = useCallback(async (lang) => {
    try {
      setIsLoading(true);
      const cacheBuster = import.meta.env.DEV ? `?t=${Date.now()}` : '';
      const base = import.meta.env.BASE_URL || '/';

      // Posibles ubicaciones (soporta GitHub Pages, rutas relativas y base personalizada)
      const candidates = [
        `${base}i18n/${lang}.json${cacheBuster}`,
        `/sifu/i18n/${lang}.json${cacheBuster}`,
        `/i18n/${lang}.json${cacheBuster}`,
        `i18n/${lang}.json${cacheBuster}`,
      ];

      const fetchFirstOk = async (urls) => {
        for (const url of urls) {
          try {
            const res = await fetch(url, { cache: 'no-cache' });
            if (res.ok) {
              return await res.json();
            }
          } catch (e) {
            // Continúa probando siguientes rutas
          }
        }
        return null;
      };

      let remoteData = await fetchFirstOk(candidates);
      if (!remoteData) {
        console.warn(`⚠️ I18nContext: No se pudo cargar '${lang}'. Probando fallback '${FALLBACK_LANGUAGE}'`);
        const fallbackCandidates = [
          `${base}i18n/${FALLBACK_LANGUAGE}.json${cacheBuster}`,
          `/sifu/i18n/${FALLBACK_LANGUAGE}.json${cacheBuster}`,
          `/i18n/${FALLBACK_LANGUAGE}.json${cacheBuster}`,
          `i18n/${FALLBACK_LANGUAGE}.json${cacheBuster}`,
        ];
        remoteData = await fetchFirstOk(fallbackCandidates);
      }

      // Último recurso: usar traducciones embebidas en el bundle (src/locales)
      const embeddedForLang = embeddedRef.current[lang] || embeddedRef.current[FALLBACK_LANGUAGE] || {};
      let finalData;
      if (remoteData) {
        // Merge: embedded (full source) + remote (runtime overrides / possibly partial)
        finalData = deepMerge(embeddedForLang, remoteData);
      } else {
        finalData = embeddedForLang; // Only embedded available
      }

      if (finalData && Object.keys(finalData).length > 0) {
        setTranslations(finalData);
      } else {
        console.error('❌ I18nContext: No se encontró ningún archivo de traducción');
        setTranslations({});
      }
    } catch (error) {
      console.error('❌ I18nContext: Error loading translations:', error);
      setTranslations({});
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Initialize language
  useEffect(() => {
    if (forceEmbedded) return; // ya inicializado
    const savedLang = (!forceEmbedded) ? localStorage.getItem('sifu-language') : null;
    const initialLang = (savedLang && SUPPORTED_LANGUAGES.includes(savedLang))
      ? savedLang
      : DEFAULT_LANGUAGE;

    setCurrentLanguage(initialLang);
    if (forceEmbedded) {
      const embeddedForLang = embeddedRef.current[initialLang] || embeddedRef.current[FALLBACK_LANGUAGE] || {};
      setTranslations(embeddedForLang);
      setIsLoading(false);
    } else {
      loadTranslations(initialLang);
    }
  }, [loadTranslations, forceEmbedded]);

  // Translation function
  const t = useCallback((key, params = {}) => {
    // If translations are still loading, return the fallback immediately
    if (isLoading || !translations || Object.keys(translations).length === 0) {
      return key;
    }
    
    const keys = key.split('.');
    let value = translations;
    
    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        // Double-check embedded locales to reduce falsos positivos (tests / race conditions)
        const embedded = embeddedRef.current[currentLanguage] || embeddedRef.current[FALLBACK_LANGUAGE] || {};
        let probe = embedded;
        let existsInEmbedded = true;
        for (const kk of keys) {
          if (probe && typeof probe === 'object' && kk in probe) {
            probe = probe[kk];
          } else {
            existsInEmbedded = false;
            break;
          }
        }
        if (!existsInEmbedded) {
          const silence = import.meta.env.VITE_I18N_SILENCE_KNOWN === '1';
          if (!silence) {
            console.warn(`⚠️ I18nContext: Translation key not found: ${key} (lang: ${currentLanguage})`);
          }
        } // else existe en embedded: silencio (clave llegará tras merge remoto si era parcial)
        return key; // Return key if not found (remote or embedded)
      }
    }
    
    // Replace parameters if any
    if (typeof value === 'string' && Object.keys(params).length > 0) {
      return value.replace(/\{(\w+)\}/g, (match, param) => {
        return params[param] || match;
      });
    }
    
    return value;
  }, [translations, currentLanguage, isLoading]);

  // Function to translate backend messages
  const translateBackendMessage = useCallback((message) => {
    // Mapping of backend messages in English to translation keys
    const messagePatterns = [
      {
        pattern: /^UI value for (.+) retrieved successfully$/,
        key: 'backend_messages.ui_value_retrieved',
        params: (match) => ({ date: match[1] })
      },
      {
        pattern: /^Latest UI value retrieved successfully$/,
        key: 'backend_messages.latest_ui_retrieved',
        params: () => ({})
      },
      {
        pattern: /^No UI data available\. Run \/api\/refresh to load data\.$/,
        key: 'backend_messages.no_ui_data_available',
        params: () => ({})
      },
      {
        pattern: /^No data for (.+)\. Showing closest previous value$/,
        key: 'backend_messages.no_data_showing_closest',
        params: (match) => ({ date: match[1] })
      },
      {
        pattern: /^UI values for range (.+) - (.+) retrieved successfully\. (\d+) records found$/,
        key: 'backend_messages.ui_range_retrieved',
        params: (match) => ({ start_date: match[1], end_date: match[2], count: match[3] })
      },
      {
        pattern: /^UR value for (.+) retrieved successfully$/,
        key: 'backend_messages.ur_value_retrieved',
        params: (match) => ({ period: match[1] })
      },
      {
        pattern: /^Latest UR value retrieved successfully$/,
        key: 'backend_messages.latest_ur_retrieved',
        params: () => ({})
      },
      {
        pattern: /^No UR data available for (.+)$/,
        key: 'backend_messages.no_ur_data_available',
        params: (match) => ({ period: match[1] })
      },
      {
        pattern: /^No UR data available$/,
        key: 'backend_messages.no_ur_data_general',
        params: () => ({})
      },
      {
        pattern: /^Retrieved (\d+) UR values for year (.+)$/,
        key: 'backend_messages.ur_values_retrieved',
        params: (match) => ({ count: match[1], period: `año ${match[2]}` })
      },
      {
        pattern: /^Retrieved (\d+) UR values for range (.+) to (.+)$/,
        key: 'backend_messages.ur_values_retrieved',
        params: (match) => ({ count: match[1], period: `rango ${match[2]} a ${match[3]}` })
      },
      {
        pattern: /^Month must be between 1 and 12$/,
        key: 'backend_messages.month_validation',
        params: () => ({})
      },
      {
        pattern: /^Months must be between 1 and 12$/,
        key: 'backend_messages.months_validation',
        params: () => ({})
      },
      {
        pattern: /^Start period must be before or equal to end period$/,
        key: 'backend_messages.period_validation',
        params: () => ({})
      },
      {
        pattern: /^Internal server error$/,
        key: 'backend_messages.internal_server_error',
        params: () => ({})
      },
      // Exchange Rate messages 
      {
        pattern: /^Latest exchange rates retrieved successfully$/,
        key: 'backend_messages.exchange_latest_retrieved',
        params: () => ({})
      },
      {
        pattern: /^Latest exchange rates for ([A-Z]{3}) retrieved successfully$/,
        key: 'backend_messages.exchange_latest_currency_retrieved',
        params: (match) => ({ currency: match[1] })
      },
      {
        pattern: /^Exchange rates for (.+) retrieved successfully$/,
        key: 'backend_messages.exchange_date_retrieved_no_count',
        params: (match) => ({ date: match[1] })
      },
      {
        pattern: /^Exchange rates for (.+) retrieved successfully\. (\d+) records found$/,
        key: 'backend_messages.exchange_date_retrieved',
        params: (match) => ({ date: match[1], count: match[2] })
      },
      {
        pattern: /^([A-Z]{3}) exchange rate for (.+) retrieved successfully$/,
        key: 'backend_messages.exchange_date_currency_retrieved',
        params: (match) => ({ currency: match[1], date: match[2] })
      },
      {
        pattern: /^Exchange rates for range (.+) - (.+) retrieved successfully\. (\d+) records found$/,
        key: 'backend_messages.exchange_range_retrieved',
        params: (match) => ({ start_date: match[1], end_date: match[2], count: match[3] })
      },
      {
        pattern: /^Exchange rates for range (.+) - (.+) retrieved successfully$/,
        key: 'backend_messages.exchange_range_retrieved_no_count',
        params: (match) => ({ start_date: match[1], end_date: match[2] })
      },
      {
        pattern: /^([A-Z]{3}) history retrieved successfully\. (\d+) records found$/,
        key: 'backend_messages.exchange_currency_history_retrieved',
        params: (match) => ({ currency: match[1], count: match[2] })
      },
      {
        pattern: /^Exchange rates for ([A-Z]{3}) retrieved successfully$/,
        key: 'backend_messages.exchange_currency_history_retrieved',
        params: (match) => ({ currency: match[1] })
      },
      {
        pattern: /^Exchange data refreshed successfully$/,
        key: 'backend_messages.exchange_refresh_success',
        params: () => ({})
      },
      {
        pattern: /^Exchange rates refreshed successfully$/,
        key: 'backend_messages.exchange_refresh_success',
        params: () => ({})
      },
      // Health / API status messages
      {
        pattern: /^BCU API responding$/,
        key: 'backend_messages.bcu_api_responding',
        params: () => ({})
      },
      {
        pattern: /^BCU API using cached data$/,
        key: 'backend_messages.bcu_api_cached',
        params: () => ({})
      },
      {
        pattern: /^BCU API not responding$/,
        key: 'backend_messages.bcu_api_not_responding',
        params: () => ({})
      },
      {
        pattern: /^BROU API responding$/,
        key: 'backend_messages.brou_api_responding',
        params: () => ({})
      },
      {
        pattern: /^BROU API using cached data$/,
        key: 'backend_messages.brou_api_cached',
        params: () => ({})
      },
      {
        pattern: /^BROU API not responding$/,
        key: 'backend_messages.brou_api_not_responding',
        params: () => ({})
      },
      {
        pattern: /^BROU cache is very stale \(([\d.]+) minutes old\)$/,
        key: 'backend_messages.brou_cache_very_stale',
        params: (m) => ({ minutes: m[1] })
      },
      {
        pattern: /^BROU cache is stale \(([\d.]+) minutes old\)$/,
        key: 'backend_messages.brou_cache_stale',
        params: (m) => ({ minutes: m[1] })
      },
      {
        pattern: /^BROU cache is fresh \(([\d.]+) minutes old\)$/,
        key: 'backend_messages.brou_cache_fresh',
        params: (m) => ({ minutes: m[1] })
      },
      {
        pattern: /^System resources OK$/,
        key: 'backend_messages.system_resources_ok',
        params: () => ({})
      }
    ];

    // Search for pattern matches
    for (const { pattern, key, params } of messagePatterns) {
      const match = message.match(pattern);
      if (match) {
        const translationParams = params(match);
        return t(key, translationParams);
      }
    }
    
    // If no translation found, return original message
    return message;
  }, [t]);

  // Change language
  const setLanguage = useCallback(async (lang) => {
    if (!SUPPORTED_LANGUAGES.includes(lang)) {
      console.warn(`⚠️ I18nContext: Unsupported language: ${lang}`);
      return;
    }
    
    // Save to localStorage first
    localStorage.setItem('sifu-language', lang);
    
    // Load new translations first, then update language
    if (forceEmbedded) {
      const embeddedForLang = embeddedRef.current[lang] || embeddedRef.current[FALLBACK_LANGUAGE] || {};
      setTranslations(embeddedForLang);
      setCurrentLanguage(lang);
      setIsLoading(false);
    } else {
      await loadTranslations(lang);
      setCurrentLanguage(lang);
    }
  }, [loadTranslations, forceEmbedded]);

  // Force reload translations
  const reloadTranslations = useCallback(async () => {
    if (forceEmbedded) {
      const embeddedForLang = embeddedRef.current[currentLanguage] || embeddedRef.current[FALLBACK_LANGUAGE] || {};
      setTranslations(embeddedForLang);
      setIsLoading(false);
    } else {
      await loadTranslations(currentLanguage);
    }
  }, [loadTranslations, currentLanguage, forceEmbedded]);

  const value = {
    currentLanguage,
    supportedLanguages: SUPPORTED_LANGUAGES,
    isLoading,
    t,
    translateBackendMessage,
    setLanguage,
    reloadTranslations
  };

  return (
    <I18nContext.Provider value={value}>
      {children}
    </I18nContext.Provider>
  );
}; 