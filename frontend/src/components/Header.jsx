import React from 'react';
import { CurrencyDollarIcon } from '@heroicons/react/24/outline';
import { UruguayFlagIcon } from '../icons/system_icons';
import LanguageSelector from './LanguageSelector';
import { useI18n } from '../contexts/I18nContext';
import ThemeToggle from './ui/ThemeToggle';
import ThemeSelector from './ui/ThemeSelector';

const Header = () => {
  const { t } = useI18n();
  
  return (
    <header className="sticky top-0 z-20 bg-white dark:bg-neutral-900 border-b border-neutral-200 dark:border-neutral-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-10 h-10 bg-uruguay-blue rounded-lg shadow-sm">
              <CurrencyDollarIcon className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
                {t('header.sifu_title') || 'SIFU'}
              </h1>
              <p className="flex items-center gap-1 text-sm text-neutral-600 dark:text-neutral-300">
                <span>{t('header.sifu_subtitle') || 'Sistema de Índices Financieros - Uruguay'}</span>
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <ThemeSelector />
            <div className="h-6 w-px bg-neutral-300 dark:bg-neutral-600" />
            <ThemeToggle />
            <LanguageSelector />
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header; 