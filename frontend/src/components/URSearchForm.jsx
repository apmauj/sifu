import React, { useState, useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { MagnifyingGlassIcon, CalendarIcon } from '../icons';
import urService from '../services/urService';
import QuickSelectors from './QuickSelectors';
import { useI18n } from '../contexts/I18nContext';
import {
  MONTHS,
  BUTTON_LABELS
} from '../constants';

const URSearchForm = ({ onSearch, isLoading }) => {
  const { t } = useI18n();
  const { control, handleSubmit, formState: { errors }, setValue, watch, reset, trigger, getValues } = useForm();
  const [searchType, setSearchType] = useState('single');
  const [subtype, setSubtype] = useState('month');
  const [urInfo, setURInfo] = useState(null); // Available UR information
  const [loadingInfo, setLoadingInfo] = useState(true); // Loading state for UR info

  const currentYear = new Date().getFullYear();
  const currentMonth = new Date().getMonth() + 1;

  // Get UR information when component loads
  useEffect(() => {
    const fetchURInfo = async () => {
      try {
        setLoadingInfo(true);
        const info = await urService.getInfo();
        if (info && info.success && info.data) {
          setURInfo(info.data);
        } else if (info && info.data) {
          // Sometimes the response doesn't have success flag
          setURInfo(info.data);
        }
      } catch (error) {
        console.error('Error fetching UR info:', error);
      } finally {
        setLoadingInfo(false);
      }
    };

    fetchURInfo();
  }, []);

  const onSubmit = (data) => {
    const searchParams = {
      type: searchType,
      subtype,
      ...data
    };
    onSearch(searchParams);
  };

  const setQuickPeriod = (year, month = null) => {
    if (month) {
      setValue('year', year);
      setValue('month', month);
      setSearchType('single');
      setSubtype('month');
      const searchParams = {
        type: 'single',
        subtype: 'month',
        year,
        month
      };
      onSearch(searchParams);
    } else {
      setValue('year', year);
      setSearchType('single');
      setSubtype('year');
      const searchParams = {
        type: 'single',
        subtype: 'year',
        year
      };
      onSearch(searchParams);
    }
  };

  // Quick selector functions
  const setQuickRange = (startYear, startMonth, endYear, endMonth) => {
    setValue('startYear', startYear);
    setValue('startMonth', startMonth);
    setValue('endYear', endYear);
    setValue('endMonth', endMonth);
    setSearchType('range');
    // Execute search automatically
    const searchParams = {
      type: 'range',
      startYear,
      startMonth,
      endYear,
      endMonth
    };
    onSearch(searchParams);
  };

  const handleQuickURRange = (startYear, startMonth, endYear, endMonth) => {
    // Execute search automatically
    setQuickRange(startYear, startMonth, endYear, endMonth);
  };

  const handleQuickURSingle = (year, month) => {
    // Automatically switch to range mode
    if (month) {
      setQuickPeriod(year, month);
    } else {
      // Execute search automatically
      setQuickPeriod(year);
    }
  };

  // Generate available year options
  const getYearOptions = () => {
    if (!urInfo || !urInfo.date_range) {
      // Fallback: generate years from 1970 to current year
      const years = [];
      for (let year = currentYear; year >= 1970; year--) {
        years.push(year);
      }
      return years;
    }
    
    const { min_year, max_year } = urInfo.date_range;
    const years = [];
    for (let year = max_year; year >= min_year; year--) {
      years.push(year);
    }
    return years;
  };

  const yearOptions = getYearOptions();

  // Helper function to compare periods (year/month combinations)
  const comparePeriods = (year1, month1, year2, month2) => {
    const period1 = parseInt(year1) * 12 + parseInt(month1);
    const period2 = parseInt(year2) * 12 + parseInt(month2);
    return period1 - period2; // Returns negative if period1 < period2, 0 if equal, positive if period1 > period2
  };

  // Custom clear function that sets default values instead of empty fields
  const handleClear = () => {
    if (searchType === 'single') {
      if (subtype === 'month') {
        setValue('year', currentYear);
        setValue('month', currentMonth);
      } else {
        setValue('year', currentYear);
      }
    } else {
      // For range, set a reasonable default range (last year to current)
      setValue('startYear', currentYear - 1);
      setValue('startMonth', 1);
      setValue('endYear', currentYear);
      setValue('endMonth', currentMonth);
    }
  };

  return (
    <div className="fade-in">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
          {t('ur.search_title') || 'Consultar Valor de UR'}
        </h2>
        
        {/* Search type selector */}
        <div className="flex space-x-4 mb-4">
          <label className="flex items-center" htmlFor="searchType-single-ur">
            <input
              type="radio"
              id="searchType-single-ur"
              name="searchType"
              value="single"
              checked={searchType === 'single'}
              onChange={(e) => setSearchType(e.target.value)}
              className="mr-2 text-uruguay-blue focus:ring-uruguay-blue"
            />
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{t('ur.specific_period') || 'Período específico'}</span>
          </label>
          <label className="flex items-center" htmlFor="searchType-range-ur">
            <input
              type="radio"
              id="searchType-range-ur"
              name="searchType"
              value="range"
              checked={searchType === 'range'}
              onChange={(e) => setSearchType(e.target.value)}
              className="mr-2 text-uruguay-blue focus:ring-uruguay-blue"
            />
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{t('ur.period_range') || 'Rango de períodos'}</span>
          </label>
        </div>

        {/* Subtype selector for single search */}
        {searchType === 'single' && (
          <div className="flex space-x-4 mb-4">
            <label className="flex items-center" htmlFor="subtype-month">
              <input
                type="radio"
                id="subtype-month"
                name="subtype"
                value="month"
                checked={subtype === 'month'}
                onChange={(e) => setSubtype(e.target.value)}
                className="mr-2 text-uruguay-blue focus:ring-uruguay-blue"
              />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{t('ur.specific_month') || 'Mes específico'}</span>
            </label>
            <label className="flex items-center" htmlFor="subtype-year">
              <input
                type="radio"
                id="subtype-year"
                name="subtype"
                value="year"
                checked={subtype === 'year'}
                onChange={(e) => setSubtype(e.target.value)}
                className="mr-2 text-uruguay-blue focus:ring-uruguay-blue"
              />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{t('ur.full_year') || 'Año completo'}</span>
            </label>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {searchType === 'single' ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label htmlFor="year" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <CalendarIcon className="w-4 h-4 inline mr-1" />
                {t('common.year') || 'Año'}
              </label>
              <Controller
                control={control}
                name="year"
                defaultValue={currentYear}
                rules={{
                  required: t('ur.year_required') || 'El año es requerido'
                }}
                render={({ field }) => (
                  <select
                    {...field}
                    id="year"
                    className="input-field"
                    disabled={loadingInfo}
                  >
                    <option value="">
                      {loadingInfo 
                        ? (t('common.loading') || 'Cargando...') 
                        : (t('ur.select_year') || 'Selecciona un año')
                      }
                    </option>
                    {yearOptions.map(year => (
                      <option key={year} value={year}>{year}</option>
                    ))}
                  </select>
                )}
              />
              {errors.year && (
                <p className="mt-1 text-sm text-red-600">{errors.year.message}</p>
              )}
            </div>

            {subtype === 'month' && (
              <div>
                <label htmlFor="month" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  <CalendarIcon className="w-4 h-4 inline mr-1" />
                  {t('common.month') || 'Mes'}
                </label>
                <Controller
                  control={control}
                  name="month"
                  defaultValue={currentMonth}
                  rules={{
                    required: t('ur.month_required') || 'El mes es requerido'
                  }}
                  render={({ field }) => (
                    <select
                      {...field}
                      id="month"
                      className="input-field"
                    >
                      <option value="">{t('ur.select_month') || 'Selecciona un mes'}</option>
                      {Array.from({ length: 12 }, (_, i) => i + 1).map(month => (
                        <option key={month} value={month}>
                          {t(`ur.${['january', 'february', 'march', 'april', 'may', 'june', 
                               'july', 'august', 'september', 'october', 'november', 'december'][month - 1]}`) || 
                           ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'][month - 1]}
                        </option>
                      ))}
                    </select>
                  )}
                />
                {errors.month && (
                  <p className="mt-1 text-sm text-red-600">{errors.month.message}</p>
                )}
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-6">
            {/* Start Period Section */}
            <div className="bg-gray-50 dark:bg-gray-700/60 p-4 rounded-lg">
              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center">
                <CalendarIcon className="w-4 h-4 mr-2" />
                {t('ur.start_period') || 'Período inicio'}
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="startYear" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {t('common.year') || 'Año'}
                  </label>
                  <Controller
                    control={control}
                    name="startYear"
                    defaultValue={currentYear - 1}
                    rules={{
                      required: t('ur.year_required') || 'El año es requerido',
                      validate: (value) => {
                        const endYear = getValues('endYear');
                        const startMonth = getValues('startMonth');
                        const endMonth = getValues('endMonth');
                        
                        if (endYear && startMonth && endMonth && value) {
                          const comparison = comparePeriods(value, startMonth, endYear, endMonth);
                          if (comparison > 0) {
                            return t('ur.start_period_after_end') || 'El período de inicio no puede ser posterior al período de fin';
                          }
                        }
                        return true;
                      }
                    }}
                    render={({ field }) => (
                      <select
                        {...field}
                        id="startYear"
                        className="input-field"
                        disabled={loadingInfo}
                        onChange={(e) => {
                          field.onChange(e);
                          // Trigger validation of other period fields
                          trigger(['startMonth', 'endYear', 'endMonth']);
                        }}
                      >
                        <option value="">
                          {loadingInfo 
                            ? (t('common.loading') || 'Cargando...') 
                            : (t('ur.select_year') || 'Selecciona un año')
                          }
                        </option>
                        {yearOptions.map(year => (
                          <option key={year} value={year}>{year}</option>
                        ))}
                      </select>
                    )}
                  />
                  {errors.startYear && (
                    <p className="mt-1 text-sm text-red-600">{errors.startYear.message}</p>
                  )}
                </div>

                <div>
                  <label htmlFor="startMonth" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {t('common.month') || 'Mes'}
                  </label>
                  <Controller
                    control={control}
                    name="startMonth"
                    defaultValue={1}
                    rules={{
                      required: t('ur.month_required') || 'El mes es requerido',
                      validate: (value) => {
                        const startYear = getValues('startYear');
                        const endYear = getValues('endYear');
                        const endMonth = getValues('endMonth');
                        
                        if (startYear && endYear && endMonth && value) {
                          const comparison = comparePeriods(startYear, value, endYear, endMonth);
                          if (comparison > 0) {
                            return t('ur.start_period_after_end') || 'El período de inicio no puede ser posterior al período de fin';
                          }
                        }
                        return true;
                      }
                    }}
                    render={({ field }) => (
                      <select
                        {...field}
                        id="startMonth"
                        className="input-field"
                        onChange={(e) => {
                          field.onChange(e);
                          // Trigger validation of other period fields
                          trigger(['startYear', 'endYear', 'endMonth']);
                        }}
                      >
                        <option value="">{t('ur.select_month') || 'Selecciona un mes'}</option>
                        {Array.from({ length: 12 }, (_, i) => i + 1).map(month => (
                          <option key={month} value={month}>
                            {t(`ur.${['january', 'february', 'march', 'april', 'may', 'june', 
                                 'july', 'august', 'september', 'october', 'november', 'december'][month - 1]}`) || 
                             ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                              'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'][month - 1]}
                          </option>
                        ))}
                      </select>
                    )}
                  />
                  {errors.startMonth && (
                    <p className="mt-1 text-sm text-red-600">{errors.startMonth.message}</p>
                  )}
                </div>
              </div>
            </div>

            {/* End Period Section */}
            <div className="bg-gray-50 dark:bg-gray-700/60 p-4 rounded-lg">
              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center">
                <CalendarIcon className="w-4 h-4 mr-2" />
                {t('ur.end_period') || 'Período fin'}
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="endYear" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {t('common.year') || 'Año'}
                  </label>
                  <Controller
                    control={control}
                    name="endYear"
                    defaultValue={currentYear}
                    rules={{
                      required: t('ur.year_required') || 'El año es requerido',
                      validate: (value) => {
                        const startYear = getValues('startYear');
                        const startMonth = getValues('startMonth');
                        const endMonth = getValues('endMonth');
                        
                        if (startYear && startMonth && endMonth && value) {
                          const comparison = comparePeriods(startYear, startMonth, value, endMonth);
                          if (comparison > 0) {
                            return t('ur.end_period_before_start') || 'El período de fin no puede ser anterior al período de inicio';
                          }
                        }
                        return true;
                      }
                    }}
                    render={({ field }) => (
                      <select
                        {...field}
                        id="endYear"
                        className="input-field"
                        disabled={loadingInfo}
                        onChange={(e) => {
                          field.onChange(e);
                          // Trigger validation of other period fields
                          trigger(['startYear', 'startMonth', 'endMonth']);
                        }}
                      >
                        <option value="">
                          {loadingInfo 
                            ? (t('common.loading') || 'Cargando...') 
                            : (t('ur.select_year') || 'Selecciona un año')
                          }
                        </option>
                        {yearOptions.map(year => (
                          <option key={year} value={year}>{year}</option>
                        ))}
                      </select>
                    )}
                  />
                  {errors.endYear && (
                    <p className="mt-1 text-sm text-red-600">{errors.endYear.message}</p>
                  )}
                </div>

                <div>
                  <label htmlFor="endMonth" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {t('common.month') || 'Mes'}
                  </label>
                  <Controller
                    control={control}
                    name="endMonth"
                    defaultValue={currentMonth}
                    rules={{
                      required: t('ur.month_required') || 'El mes es requerido',
                      validate: (value) => {
                        const startYear = getValues('startYear');
                        const startMonth = getValues('startMonth');
                        const endYear = getValues('endYear');
                        
                        if (startYear && startMonth && endYear && value) {
                          const comparison = comparePeriods(startYear, startMonth, endYear, value);
                          if (comparison > 0) {
                            return t('ur.end_period_before_start') || 'El período de fin no puede ser anterior al período de inicio';
                          }
                        }
                        return true;
                      }
                    }}
                    render={({ field }) => (
                      <select
                        {...field}
                        id="endMonth"
                        className="input-field"
                        onChange={(e) => {
                          field.onChange(e);
                          // Trigger validation of other period fields
                          trigger(['startYear', 'startMonth', 'endYear']);
                        }}
                      >
                        <option value="">{t('ur.select_month') || 'Selecciona un mes'}</option>
                        {Array.from({ length: 12 }, (_, i) => i + 1).map(month => (
                          <option key={month} value={month}>
                            {t(`ur.${['january', 'february', 'march', 'april', 'may', 'june', 
                                 'july', 'august', 'september', 'october', 'november', 'december'][month - 1]}`) || 
                             ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                              'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'][month - 1]}
                          </option>
                        ))}
                      </select>
                    )}
                  />
                  {errors.endMonth && (
                    <p className="mt-1 text-sm text-red-600">{errors.endMonth.message}</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Quick selectors */}
        <QuickSelectors
          type="UR"
          mode={searchType}
          onURSingleSelect={handleQuickURSingle}
          onURRangeSelect={handleQuickURRange}
        />

        <div className="flex flex-col sm:flex-row gap-3 pt-4">
          <button
            type="submit"
            disabled={isLoading}
            className={`flex items-center justify-center space-x-2 px-6 py-2 rounded-lg font-medium transition-colors duration-200 ${
              isLoading
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-uruguay-blue text-white hover:bg-blue-700'
            }`}
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>{t('common.consulting') || 'Consultando...'}</span>
              </>
            ) : (
              <>
                <MagnifyingGlassIcon className="w-4 h-4" />
                <span>{t('ur.search_button') || 'Consultar UR'}</span>
              </>
            )}
          </button>
          <button
            type="button"
            onClick={handleClear}
            className="btn-secondary"
          >
            {t('common.clear') || 'Limpiar'}
          </button>
        </div>

      </form>

  {/* Removed legacy availability line for consistency with UI panel */}
    </div>
  );
};

export default URSearchForm; 