import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

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

// Context provider
export const I18nProvider = ({ children }) => {
  const [currentLanguage, setCurrentLanguage] = useState(DEFAULT_LANGUAGE);
  const [translations, setTranslations] = useState({});
  const [isLoading, setIsLoading] = useState(true);

  // Load translations
  const loadTranslations = useCallback(async (lang) => {
    try {
      setIsLoading(true);
      
      // En Vite, los archivos en public/ se sirven desde la raíz
      const cacheBuster = process.env.NODE_ENV === 'development' ? `?t=${Date.now()}` : '';
      const translationUrl = `/i18n/${lang}.json${cacheBuster}`;
      
      const response = await fetch(translationUrl);
      
      if (response.ok) {
        const data = await response.json();
        setTranslations(data);
      } else {
        console.warn(`⚠️ I18nContext: No se pudo cargar ${lang}, usando fallback`);
        const fallbackUrl = `/i18n/${FALLBACK_LANGUAGE}.json${cacheBuster}`;
        const fallbackResponse = await fetch(fallbackUrl);
        const fallbackData = await fallbackResponse.json();
        setTranslations(fallbackData);
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
    const savedLang = localStorage.getItem('sifu-language');
    const initialLang = (savedLang && SUPPORTED_LANGUAGES.includes(savedLang)) 
      ? savedLang 
      : DEFAULT_LANGUAGE;
    
    setCurrentLanguage(initialLang);
    loadTranslations(initialLang);
  }, [loadTranslations]);

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
        console.warn(`⚠️ I18nContext: Translation key not found: ${key} (lang: ${currentLanguage})`);
        return key; // Return key if not found
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
        pattern: /^([A-Z]{3}) history retrieved successfully\. (\d+) records found$/,
        key: 'backend_messages.exchange_currency_history_retrieved',
        params: (match) => ({ currency: match[1], count: match[2] })
      },
      {
        pattern: /^Exchange rates for ([A-Z]{3}) retrieved successfully$/,
        key: 'backend_messages.exchange_currency_history_retrieved',
        params: (match) => ({ currency: match[1] })
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
    await loadTranslations(lang);
    setCurrentLanguage(lang);
  }, [loadTranslations]);

  // Force reload translations
  const reloadTranslations = useCallback(async () => {
    await loadTranslations(currentLanguage);
  }, [loadTranslations, currentLanguage]);

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