import React from 'react';
import { format, subDays, subMonths, startOfMonth, endOfMonth, startOfYear, endOfYear } from 'date-fns';
import { useI18n } from '../contexts/I18nContext';
import { getTodayLocal, getDaysAgoLocal, formatDateLocal } from '../utils/dateUtils';
import { DATE_FORMAT_YYYYMMDD, QUICK_SELECTORS } from '../constants';

const QuickSelectors = ({
  type, // 'UI' or 'UR'
  mode, // 'single' or 'range'
  onSingleSelect, // Function for single selection: (date) => void
  onRangeSelect, // Function for range selection: (startDate, endDate) => void
  onURSingleSelect, // Function for single UR: (year, month) => void
  onURRangeSelect, // Function for UR range: (startYear, startMonth, endYear, endMonth) => void
  maxDate, // Maximum available date
  className = ""
}) => {
  const { t, currentLanguage } = useI18n();

  const today = new Date();
  const currentYear = today.getFullYear();
  const currentMonth = today.getMonth() + 1; // getMonth() returns 0-11

  // Function to calculate UI dates using local timezone
  const calculateUIDate = (daysBack) => {
    return getDaysAgoLocal(daysBack);
  };

  // Function to calculate UI date range using local timezone
  const calculateUIRange = (startDaysBack, endDaysBack = 0) => {
    return {
      start: getDaysAgoLocal(startDaysBack),
      end: getDaysAgoLocal(endDaysBack)
    };
  };

  // Function to calculate single UR period (month only - no years in SINGLE mode)
  const calculateURSingle = (selector) => {
    if (selector.months !== undefined) {
      if (selector.months === 0) {
        // Current month
        return {
          year: currentYear,
          month: currentMonth
        };
      } else {
        // Months back
        const targetDate = subMonths(today, selector.months);
        return {
          year: targetDate.getFullYear(),
          month: targetDate.getMonth() + 1
        };
      }
    }
    
    // Default fallback (should not reach here with proper config)
    return {
      year: currentYear,
      month: currentMonth
    };
  };

  // Function to calculate UR range
  const calculateURRange = (selector) => {
    if (selector.months !== undefined) {
      const monthsBack = selector.months;
      const startDate = subMonths(today, monthsBack);
      return {
        startYear: startDate.getFullYear(),
        startMonth: startDate.getMonth() + 1,
        endYear: currentYear,
        endMonth: currentMonth
      };
    }
    
    if (selector.years !== undefined) {
      const yearsBack = selector.years;
      return {
        startYear: currentYear - yearsBack,
        startMonth: 1,
        endYear: currentYear,
        endMonth: currentMonth
      };
    }
    
    // Default fallback
    return {
      startYear: currentYear,
      startMonth: 1,
      endYear: currentYear,
      endMonth: currentMonth
    };
  };

  // Handle UI selector click
  const handleUIClick = (selector) => {
    if (mode === 'single') {
      const date = calculateUIDate(selector.days);
      onSingleSelect?.(date);
    } else {
      const range = calculateUIRange(selector.startDays, selector.endDays);
      onRangeSelect?.(range.start, range.end);
    }
  };

  // Handle UR selector click
  const handleURClick = (selector) => {
    if (mode === 'single') {
      // In SINGLE mode, all selectors are month-based (no year selectors anymore)
      const single = calculateURSingle(selector);
      onURSingleSelect?.(single.year, single.month);
    } else {
      // In RANGE mode, calculate and execute range query
      const range = calculateURRange(selector);
      onURRangeSelect?.(range.startYear, range.startMonth, range.endYear, range.endMonth);
    }
  };

  // Get selectors based on type and mode
  const getSelectors = () => {
    if (type === 'UI') {
      return mode === 'single' ? QUICK_SELECTORS.UI.SINGLE : QUICK_SELECTORS.UI.RANGE;
    } else {
      return mode === 'single' ? QUICK_SELECTORS.UR.SINGLE : QUICK_SELECTORS.UR.RANGE;
    }
  };

  // Function to translate selector labels
  const translateLabel = (selector) => {
    // Mapping of selector keys to translation keys
    const labelMap = {
      // UI Single selectors
      'today': 'common.today',
      'yesterday': 'ui.yesterday',
      'lastWeek': 'ui.last_week',
      'lastMonth': 'ui.last_month',
      
      // UI Range selectors
      'last7Days': 'ui.last_7_days',
      'last15Days': 'ui.last_15_days',
      'last30Days': 'ui.last_30_days',
      'last3Months': 'ui.last_3_months',
      'last6Months': 'ui.last_6_months',
      'lastYear': 'ui.last_year',
      
      // UR Single selectors
      'current_month': 'ur.current_month',
      'last_month': 'ur.last_month',
      'current_year': 'ur.current_year',
      'last_year': 'ur.last_year',
      
      // UR Range selectors
      'last_12_months': 'ur.last_12_months',
      'last_24_months': 'ur.last_24_months',
      'last_5_years': 'ur.last_5_years',
      'last_10_years': 'ur.last_10_years'
    };

    const translationKey = labelMap[selector.key];
    if (translationKey) {
      return t(translationKey) || selector.label;
    }
    
    return selector.label;
  };

  const selectors = getSelectors();

  // Add maximum date selector for UI if available
  const getMaxDateSelector = () => {
    if (type === 'UI' && maxDate && mode === 'single') {
      return {
        key: 'latest_available',
        label: t('ui.latest_available_date') || 'Última fecha disponible',
        isSpecial: true
      };
    }
    return null;
  };

  const maxDateSelector = getMaxDateSelector();

  return (
    <div className={`mt-3 ${className}`}>
      <div className="flex flex-wrap gap-2">
        {selectors.map((selector) => (
          <button
            key={selector.key}
            type="button"
            onClick={() => type === 'UI' ? handleUIClick(selector) : handleURClick(selector)}
            className="text-xs px-3 py-1 bg-neutral-100 hover:bg-neutral-200 dark:bg-neutral-700 dark:hover:bg-neutral-600 rounded-full transition-colors duration-200 border border-neutral-300 hover:border-neutral-400 dark:border-neutral-600 dark:hover:border-neutral-500 dark:text-neutral-100 whitespace-nowrap"
            title={`${t('common.select') || 'Seleccionar'} ${translateLabel(selector).toLowerCase()}`}
          >
            {translateLabel(selector)}
          </button>
        ))}
      
        {/* Selector especial para fecha máxima disponible */}
        {maxDateSelector && (
          <button
            key={maxDateSelector.key}
            type="button"
            onClick={() => onSingleSelect?.(maxDate)}
            className="text-xs px-3 py-1 bg-blue-100 hover:bg-blue-200 dark:bg-blue-900/40 dark:hover:bg-blue-900/60 rounded-full transition-colors duration-200 border border-blue-300 hover:border-blue-400 dark:border-blue-800 dark:hover:border-blue-700 dark:text-blue-200 whitespace-nowrap"
            title={t('ui.select_latest_available') || 'Seleccionar la última fecha disponible con datos'}
          >
            {maxDateSelector.label}
          </button>
        )}
      </div>
    </div>
  );
};

export default QuickSelectors; 