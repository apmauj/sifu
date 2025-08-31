import React, { useState, useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { MagnifyingGlassIcon, CalendarIcon } from '../icons';
import { format, parseISO, isValid } from 'date-fns';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import uiService from '../services/api';
import QuickSelectors from './QuickSelectors';
import { useI18n } from '../contexts/I18nContext';
import { getTodayLocal, getDaysAgoLocal } from '../utils/dateUtils';

const SearchForm = ({ onSearch, isLoading }) => {
  const { t } = useI18n();
  const { control, handleSubmit, formState: { errors }, setValue, trigger, getValues } = useForm();

  // ESLint workaround: declare used components with underscore prefix
  const _React = React;
  const _Controller = Controller;
  const _MagnifyingGlassIcon = MagnifyingGlassIcon;
  const _CalendarIcon = CalendarIcon;
  const _DatePicker = DatePicker;
  const _QuickSelectors = QuickSelectors;
  const [searchType, setSearchType] = useState('single');
  const [maxDate, setMaxDate] = useState(''); // Maximum date available in data

  const today = getTodayLocal();

  // Get maximum available date when component loads
  useEffect(() => {
    const fetchMaxDate = async () => {
      try {
        const info = await uiService.getInfo();
        if (info && info.success && info.data && info.data.latest_date) {
          setMaxDate(info.data.latest_date);
        }
      } catch (error) {
        console.error('Error fetching max date:', error);
      }
    };

    fetchMaxDate();
  }, []);

  const onSubmit = (data) => {
    let searchParams = {
      searchType: searchType
    };
    
    if (searchType === 'single') {
      searchParams.date = data.fecha;
    } else {
      searchParams.startDate = data.fechaInicio;
      searchParams.endDate = data.fechaFin;
    }
    
    onSearch(searchParams);
  };

  // Execute search automatically
  const setQuickDate = (fecha) => {
    setValue('fecha', fecha);
    const searchParams = {
      type: 'single',
      fecha
    };
    onSearch(searchParams);
  };

  // Execute search automatically
  const setQuickRange = (fechaInicio, fechaFin) => {
    setValue('fechaInicio', fechaInicio);
    setValue('fechaFin', fechaFin);
    const searchParams = {
      type: 'range',
      fechaInicio,
      fechaFin
    };
    onSearch(searchParams);
  };

  // Use maximum available date if exists, otherwise use current date
  const effectiveMaxDate = maxDate || today;
  // Fix parsing and log for debugging
  let maxDateObj;
  if (maxDate) {
    maxDateObj = parseISO(maxDate);
    if (!isValid(maxDateObj)) {
      console.warn('maxDateObj no es válido:', maxDate, maxDateObj);
      maxDateObj = undefined;
    }
  }

  // Custom clear function that sets default values instead of empty fields
  const handleClear = () => {
    if (searchType === 'single') {
      setValue('fecha', today);
    } else {
      // For range, set a reasonable default range (last 30 days)
      const thirtyDaysAgo = getDaysAgoLocal(30);
      setValue('fechaInicio', thirtyDaysAgo);
      setValue('fechaFin', today);
    }
  };

  return (
    <div className="fade-in">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
          {t('ui.search_title') || 'Consultar Valor de UI'}
        </h2>
        {/* Search type selector */}
        <div className="flex space-x-4 mb-4">
          <label className="flex items-center" htmlFor="searchType-single">
            <input
              type="radio"
              id="searchType-single"
              name="searchType"
              value="single"
              checked={searchType === 'single'}
              onChange={(e) => setSearchType(e.target.value)}
              className="mr-2 text-uruguay-blue focus:ring-uruguay-blue"
            />
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{t('ui.specific_date') || 'Fecha específica'}</span>
          </label>
          <label className="flex items-center" htmlFor="searchType-range">
            <input
              type="radio"
              id="searchType-range"
              name="searchType"
              value="range"
              checked={searchType === 'range'}
              onChange={(e) => setSearchType(e.target.value)}
              className="mr-2 text-uruguay-blue focus:ring-uruguay-blue"
            />
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{t('ui.date_range') || 'Rango de fechas'}</span>
          </label>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {searchType === 'single' ? (
          <div>
            <label htmlFor="fecha" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              <_CalendarIcon className="w-4 h-4 inline mr-1" />
              {t('common.date') || 'Fecha'}
            </label>
            <_Controller
              control={control}
              name="fecha"
              defaultValue={today}
              rules={{
                required: t('ui.date_required') || 'La fecha es requerida',
                validate: (value) => {
                  if (maxDate && value > effectiveMaxDate) {
                    return t('ui.date_too_late') || 'La fecha no puede ser posterior a la última fecha disponible';
                  }
                  return true;
                }
              }}
              render={({ field }) => (
                <_DatePicker
                  {...field}
                  name="fecha"
                  id="fecha"
                  className="input-field"
                  dateFormat="yyyy-MM-dd"
                  selected={field.value ? parseISO(field.value) : null}
                  onChange={date => field.onChange(format(date, 'yyyy-MM-dd'))}
                  minDate={null}
                  // maxDate={maxDateObj}
                  placeholderText={t('ui.select_date') || 'Selecciona una fecha'}
                  showMonthDropdown
                  showYearDropdown
                  dropdownMode="select"
                  todayButton={t('common.today') || 'Hoy'}
                  monthDropdownProps={{ id: 'month-select-fecha', name: 'month-fecha' }}
                  yearDropdownProps={{ id: 'year-select-fecha', name: 'year-fecha' }}
                />
              )}
            />
            {errors.fecha && (
              <p className="mt-1 text-sm text-red-600">{errors.fecha.message}</p>
            )}
            {/* Enhanced quick selectors */}
            <_QuickSelectors
              type="UI"
              mode="single"
              onSingleSelect={setQuickDate}
              maxDate={maxDate}
            />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="fechaInicio" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <_CalendarIcon className="w-4 h-4 inline mr-1" />
                {t('ui.start_date') || 'Fecha inicio'}
              </label>
              <_Controller
                control={control}
                name="fechaInicio"
                defaultValue={today}
                rules={{
                  required: t('ui.start_date_required') || 'La fecha de inicio es requerida',
                  validate: (value) => {
                    if (maxDate && value > effectiveMaxDate) {
                      return t('ui.date_too_late') || 'La fecha no puede ser posterior a la última fecha disponible';
                    }
                    const fechaFin = getValues('fechaFin');
                    if (fechaFin && value > fechaFin) {
                      return t('ui.start_date_after_end') || 'La fecha de inicio no puede ser posterior a la fecha de fin';
                    }
                    return true;
                  }
                }}
                render={({ field }) => (
                  <_DatePicker
                    {...field}
                    name="fechaInicio"
                    id="fechaInicio"
                    className="input-field"
                    dateFormat="yyyy-MM-dd"
                    selected={field.value ? parseISO(field.value) : null}
                    onChange={date => {
                      field.onChange(format(date, 'yyyy-MM-dd'));
                      // Trigger validation of end date when start date changes
                      trigger('fechaFin');
                    }}
                    minDate={null}
                    // maxDate={maxDateObj}
                    placeholderText={t('ui.select_date') || 'Selecciona una fecha'}
                    showMonthDropdown
                    showYearDropdown
                    dropdownMode="select"
                    todayButton={t('common.today') || 'Hoy'}
                    monthDropdownProps={{ id: 'month-select-fechaInicio', name: 'month-fechaInicio' }}
                    yearDropdownProps={{ id: 'year-select-fechaInicio', name: 'year-fechaInicio' }}
                  />
                )}
              />
              {errors.fechaInicio && (
                <p className="mt-1 text-sm text-red-600">{errors.fechaInicio.message}</p>
              )}
            </div>
            <div>
              <label htmlFor="fechaFin" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <_CalendarIcon className="w-4 h-4 inline mr-1" />
                {t('ui.end_date') || 'Fecha fin'}
              </label>
              <_Controller
                control={control}
                name="fechaFin"
                defaultValue={today}
                rules={{
                  required: t('ui.end_date_required') || 'La fecha de fin es requerida',
                  validate: (value) => {
                    if (maxDate && value > effectiveMaxDate) {
                      return t('ui.date_too_late') || 'La fecha no puede ser posterior a la última fecha disponible';
                    }
                    const fechaInicio = getValues('fechaInicio');
                    if (fechaInicio && value < fechaInicio) {
                      return t('ui.end_date_before_start') || 'La fecha de fin no puede ser anterior a la fecha de inicio';
                    }
                    return true;
                  }
                }}
                render={({ field }) => (
                  <_DatePicker
                    {...field}
                    name="fechaFin"
                    id="fechaFin"
                    className="input-field"
                    dateFormat="yyyy-MM-dd"
                    selected={field.value ? parseISO(field.value) : null}
                    onChange={date => {
                      field.onChange(format(date, 'yyyy-MM-dd'));
                      // Trigger validation of start date when end date changes
                      trigger('fechaInicio');
                    }}
                    minDate={null}
                    // maxDate={maxDateObj}
                    placeholderText={t('ui.select_date') || 'Selecciona una fecha'}
                    showMonthDropdown
                    showYearDropdown
                    dropdownMode="select"
                    todayButton={t('common.today') || 'Hoy'}
                    monthDropdownProps={{ id: 'month-select-fechaFin', name: 'month-fechaFin' }}
                    yearDropdownProps={{ id: 'year-select-fechaFin', name: 'year-fechaFin' }}
                  />
                )}
              />
              {errors.fechaFin && (
                <p className="mt-1 text-sm text-red-600">{errors.fechaFin.message}</p>
              )}
            </div>
            {/* Enhanced range quick selectors */}
            <div className="md:col-span-2">
              <_QuickSelectors
                type="UI"
                mode="range"
                onRangeSelect={setQuickRange}
                maxDate={maxDate}
              />
            </div>
          </div>
        )}
        <div className="flex space-x-3 pt-4">
          <button
            type="submit"
            id="submit-btn"
            name="submit"
            disabled={isLoading}
            className={`flex items-center space-x-2 px-6 py-2 rounded-lg font-medium transition-colors duration-200 ${
              isLoading
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-uruguay-blue text-white hover:bg-blue-700'
            }`}
          >
            <_MagnifyingGlassIcon className="w-4 h-4" />
            <span>{isLoading ? (t('common.loading') || 'Consultando...') : (t('common.search') || 'Consultar')}</span>
          </button>
          <button
            type="button"
            id="reset-btn"
            name="reset"
            onClick={handleClear}
            className="btn-secondary"
          >
            {t('common.clear') || 'Limpiar'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default SearchForm; 