import React from 'react';
import { CurrencyDollarIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import LanguageSelector from './LanguageSelector';
import { useI18n } from '../contexts/I18nContext';
import ThemeToggle from './ui/ThemeToggle';

const Header = ({ onRefresh, isRefreshing }) => {
  const { t } = useI18n();
  
  return (
    <header className="sticky top-0 z-20 backdrop-blur bg-white/80 dark:bg-gray-900/70 border-b border-gray-200 dark:border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-10 h-10 bg-uruguay-blue rounded-lg shadow-sm">
              <CurrencyDollarIcon className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {t('header.sifu_title') || 'SIFU'}
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-300">
                {t('header.sifu_subtitle') || 'Sistema de Índices Financieros - Uruguay 🇺🇾'}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <ThemeToggle />
            <LanguageSelector />
            <button
              onClick={onRefresh}
              disabled={isRefreshing}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors duration-200 shadow-sm ${
                isRefreshing
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed dark:bg-gray-800/50 dark:text-gray-500'
                  : 'bg-uruguay-blue text-white hover:bg-blue-700'
              }`}
            >
              <ArrowPathIcon 
                className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} 
              />
              <span>
                {isRefreshing ? t('common.updating') || 'Actualizando...' : t('common.refresh_data') || 'Actualizar Datos'}
              </span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header; 