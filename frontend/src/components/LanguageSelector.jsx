import React from 'react';
import { GlobeAltIcon } from '@heroicons/react/24/outline';
import { useI18n } from '../contexts/I18nContext';

const LanguageSelector = () => {
  const { currentLanguage, supportedLanguages, setLanguage, t } = useI18n();

  const languageNames = {
    es: { name: 'Español', flag: '🇺🇾' },
    en: { name: 'English', flag: '🇺🇸' }, 
    pt: { name: 'Português', flag: '🇧🇷' }
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
      <GlobeAltIcon className="w-4 h-4 text-gray-500 dark:text-gray-300" />
      <select
        value={currentLanguage}
        onChange={handleLanguageChange}
        className="text-sm border-gray-300 dark:border-gray-600 rounded-md focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100"
        aria-label={t('common.select_language') || 'Seleccionar idioma'}
      >
        {supportedLanguages.map(lang => (
          <option key={lang} value={lang}>
            {languageNames[lang].flag} {languageNames[lang].name}
          </option>
        ))}
      </select>
    </div>
  );
};

export default LanguageSelector; 