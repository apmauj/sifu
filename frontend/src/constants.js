// Formatos de fecha
export const DATE_FORMAT_YYYYMMDD = "yyyy-MM-dd";
export const DATE_FORMAT_DDMMYYYY = "dd/MM/yyyy";

// URLs oficiales de las fuentes
export const OFFICIAL_URLS = {
  INE: "https://www.ine.gub.uy",
  BHU: "https://www.bhu.com.uy", 
  BCU: "https://www.bcu.gub.uy"
};

// Textos repetidos
export const APP_TITLE = "SIFU - Sistema de Índices Financieros del Uruguay";
export const NO_RESULTS_MESSAGE = "No hay resultados para mostrar";
export const NO_RESULTS_HINT = "Utiliza el formulario de arriba para consultar índices financieros";
export const ERROR_FETCH = "Error al consultar los datos";
export const DATA_SOURCE_LABEL = "Fuente: Instituto Nacional de Estadística (INE)";

// Etiquetas de botones expandidas
export const BUTTON_LABELS = {
  // UI - Fechas específicas
  today: "Hoy",
  yesterday: "Ayer",
  lastWeek: "Hace una semana",
  lastMonth: "Hace un mes",
  lastAvailable: "Última fecha disponible",
  
  // UI - Rangos de fechas
  last7Days: "Últimos 7 días",
  last15Days: "Últimos 15 días",
  last30Days: "Últimos 30 días",
  last3Months: "Últimos 3 meses",
  last6Months: "Últimos 6 meses",
  lastYear: "Último año",
  currentMonth: "Mes actual",
  currentYear: "Año actual",
  lastMonthAvailable: "Último mes disponible",
  
  // UR - Períodos específicos
  currentMonthUR: "Mes actual",
  lastMonthUR: "Mes anterior",
  currentYearUR: "Año actual",
  lastYearUR: "Año anterior",
  last5YearsUR: "Últimos 5 años",
  last10YearsUR: "Últimos 10 años",
  
  // UR - Rangos de períodos
  last3MonthsUR: "Últimos 3 meses",
  last6MonthsUR: "Últimos 6 meses",
  last12MonthsUR: "Últimos 12 meses",
  last24MonthsUR: "Últimos 24 meses",
  
  // Acciones generales
  search: "Consultar",
  clear: "Limpiar",
  updating: "Actualizando...",
  update: "Actualizar Datos"
};

// Meses en español
export const MONTHS = [
  "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
];

// Configuración de selectores rápidos
export const QUICK_SELECTORS = {
  UI: {
    SINGLE: [
      { key: 'today', label: BUTTON_LABELS.today, days: 0 },
      { key: 'yesterday', label: BUTTON_LABELS.yesterday, days: 1 },
      { key: 'lastWeek', label: BUTTON_LABELS.lastWeek, days: 7 },
      { key: 'lastMonth', label: BUTTON_LABELS.lastMonth, days: 30 }
    ],
    RANGE: [
      { key: 'last7Days', label: BUTTON_LABELS.last7Days, startDays: 7, endDays: 0 },
      { key: 'last15Days', label: BUTTON_LABELS.last15Days, startDays: 15, endDays: 0 },
      { key: 'last30Days', label: BUTTON_LABELS.last30Days, startDays: 30, endDays: 0 },
      { key: 'last3Months', label: BUTTON_LABELS.last3Months, startDays: 90, endDays: 0 },
      { key: 'last6Months', label: BUTTON_LABELS.last6Months, startDays: 180, endDays: 0 },
      { key: 'lastYear', label: BUTTON_LABELS.lastYear, startDays: 365, endDays: 0 }
    ]
  },
  UR: {
    SINGLE: [
      { key: 'current_month', label: BUTTON_LABELS.currentMonthUR, months: 0 },
      { key: 'last_month', label: BUTTON_LABELS.lastMonthUR, months: 1 },
      { key: 'current_year', label: BUTTON_LABELS.currentYearUR, years: 0 },
      { key: 'last_year', label: BUTTON_LABELS.lastYearUR, years: 1 }
    ],
    RANGE: [
      { key: 'last_12_months', label: BUTTON_LABELS.last12MonthsUR, months: 12 },
      { key: 'last_24_months', label: BUTTON_LABELS.last24MonthsUR, months: 24 },
      { key: 'last_5_years', label: BUTTON_LABELS.last5YearsUR, years: 5 },
      { key: 'last_10_years', label: BUTTON_LABELS.last10YearsUR, years: 10 }
    ]
  }
};

// Toast notifications
export const TOAST_DURATION = 3000; // 3 segundos

// Otros
export const CURRENCY = "UYU";
export const CURRENCY_LOCALE = "es-UY";
export const CURRENCY_DECIMALS = 4; 