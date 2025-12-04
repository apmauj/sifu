import React from 'react';
import { useI18n } from '../contexts/I18nContext';
import { Flag } from '../icons/flags';

const LanguageSelector = () => {
  const { currentLanguage, supportedLanguages, setLanguage, t } = useI18n();

  const languageNames = {
    es: { name: 'Español', flag: 'UY' },
    en: { name: 'English', flag: 'US' }, 
    pt: { name: 'Português', flag: 'BR' }
  };

  const handleLanguageChange = async (event) => {
    const newLanguage = event.target.value;
    
    try {
      await setLanguage(newLanguage);
    } catch (error) {
      console.error('❌ LanguageSelector: Error cambiando idioma:', error);
    }
  };

  return (
  <div className="flex items-center space-x-2">
      <select
        value={currentLanguage}
        onChange={handleLanguageChange}
        className="text-sm border-neutral-300 dark:border-neutral-600 rounded-md focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-neutral-900 text-neutral-900 dark:text-neutral-100"
        aria-label={t('common.select_language') || 'Seleccionar idioma'}
      >
        {supportedLanguages.map(lang => (
          <option key={lang} value={lang}>
            {languageNames[lang].name}
          </option>
        ))}
      </select>
      {/* Visual flag outside select for current language (consistent size) */}
      <div className="ml-1">
        <Flag code={languageNames[currentLanguage].flag} className="w-6 h-4" />
        <span className="sr-only">{languageNames[currentLanguage].name}</span>
      </div>
    </div>
  );
};

export default LanguageSelector; 