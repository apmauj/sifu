// Sistema de internacionalización (i18n)
class I18n {
    constructor() {
        this.currentLanguage = 'es'; // Idioma por defecto
        this.translations = {};
        this.supportedLanguages = ['es', 'en', 'pt'];
        this.fallbackLanguage = 'es';
    }

    async init() {
        // Cargar idioma desde localStorage si existe, sino usar español por defecto
        const savedLang = localStorage.getItem('sifu-language');
        if (savedLang && this.supportedLanguages.includes(savedLang)) {
            this.currentLanguage = savedLang;
        } else {
            this.currentLanguage = 'es'; // Siempre español por defecto
        }

        // Cargar traducciones
        await this.loadTranslations();
        
        // Aplicar traducciones iniciales
        this.applyTranslations();
        
        // Configurar selector de idioma
        this.setupLanguageSelector();
    }

    async loadTranslations() {
        try {
            const response = await fetch(`/static/i18n/${this.currentLanguage}.json`);
            if (response.ok) {
                this.translations = await response.json();
            } else {
                // Fallback al idioma por defecto
                const fallbackResponse = await fetch(`/static/i18n/${this.fallbackLanguage}.json`);
                this.translations = await fallbackResponse.json();
            }
        } catch (error) {
            console.error('Error loading translations:', error);
            this.translations = {}; // Fallback vacío
        }
    }

    t(key, params = {}) {
        const keys = key.split('.');
        let value = this.translations;
        
        for (const k of keys) {
            if (value && typeof value === 'object' && k in value) {
                value = value[k];
            } else {
                console.warn(`Translation key not found: ${key}`);
                return key; // Devolver la clave si no se encuentra
            }
        }
        
        // Reemplazar parámetros si los hay
        if (typeof value === 'string' && Object.keys(params).length > 0) {
            return value.replace(/\{(\w+)\}/g, (match, param) => {
                return params[param] || match;
            });
        }
        
        return value;
    }

    // Función para traducir mensajes del backend
    translateBackendMessage(message) {
        // Mapeo de mensajes del backend en inglés a claves de traducción
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
            }
        ];

        // Buscar coincidencia con los patrones
        for (const { pattern, key, params } of messagePatterns) {
            const match = message.match(pattern);
            if (match) {
                const translationParams = params(match);
                return this.t(key, translationParams);
            }
        }
        
        // Si no encuentra traducción, devuelve el mensaje original
        return message;
    }

    async setLanguage(lang) {
        if (!this.supportedLanguages.includes(lang)) {
            console.warn(`Unsupported language: ${lang}`);
            return;
        }

        this.currentLanguage = lang;
        localStorage.setItem('sifu-language', lang);
        
        await this.loadTranslations();
        this.applyTranslations();
        
        // Actualizar selector de idioma
        const selector = document.getElementById('language-selector');
        if (selector) {
            selector.value = lang;
        }
    }

    applyTranslations() {
        // Aplicar traducciones a elementos con data-i18n
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translation = this.t(key);
            
            if (element.tagName === 'INPUT' && (element.type === 'submit' || element.type === 'button')) {
                element.value = translation;
            } else if (element.tagName === 'INPUT' && element.type === 'text') {
                element.placeholder = translation;
            } else if (element.tagName === 'OPTION') {
                element.textContent = translation;
            } else {
                element.textContent = translation;
            }
        });

        // Aplicar traducciones a elementos con data-i18n-placeholder
        document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
            const key = element.getAttribute('data-i18n-placeholder');
            element.placeholder = this.t(key);
        });

        // Aplicar traducciones a elementos con data-i18n-title
        document.querySelectorAll('[data-i18n-title]').forEach(element => {
            const key = element.getAttribute('data-i18n-title');
            element.title = this.t(key);
        });

        // Actualizar arrays de meses
        this.updateMonthsArray();
        
        // Actualizar selectores de meses
        this.updateMonthSelectors();
    }

    updateMonthsArray() {
        // Actualizar el array global MONTHS
        if (window.MONTHS) {
            window.MONTHS = [
                this.t('months.1'), this.t('months.2'), this.t('months.3'),
                this.t('months.4'), this.t('months.5'), this.t('months.6'),
                this.t('months.7'), this.t('months.8'), this.t('months.9'),
                this.t('months.10'), this.t('months.11'), this.t('months.12')
            ];
        }
    }

    updateMonthSelectors() {
        // Actualizar todos los selectores de meses
        const monthSelectors = ['ur-month', 'ur-month-start', 'ur-month-end'];
        
        monthSelectors.forEach(selectorId => {
            const selector = document.getElementById(selectorId);
            if (selector) {
                const currentValue = selector.value;
                selector.innerHTML = '';
                
                for (let i = 1; i <= 12; i++) {
                    const option = document.createElement('option');
                    option.value = i;
                    option.textContent = this.t(`months.${i}`);
                    selector.appendChild(option);
                }
                
                // Restaurar el valor seleccionado
                if (currentValue) {
                    selector.value = currentValue;
                }
            }
        });
    }

    setupLanguageSelector() {
        // No crear selector automáticamente, usar el del HTML
        // El selector del HTML usa onclick="changeLanguage()" en lugar de event listener
    }

    createLanguageSelector() {
        const selector = document.createElement('select');
        selector.id = 'language-selector';
        selector.className = 'form-select form-select-sm';
        selector.style.width = 'auto';
        selector.style.display = 'inline-block';
        
        const languages = [
            { code: 'es', name: 'Español', flag: '🇺🇾' },
            { code: 'en', name: 'English', flag: '🇺🇸' },
            { code: 'pt', name: 'Português', flag: '🇧🇷' }
        ];
        
        languages.forEach(lang => {
            const option = document.createElement('option');
            option.value = lang.code;
            option.textContent = `${lang.flag} ${lang.name}`;
            selector.appendChild(option);
        });
        
        // Agregar al header
        const header = document.querySelector('.header');
        if (header) {
            const langContainer = document.createElement('div');
            langContainer.className = 'language-selector-container';
            langContainer.style.position = 'absolute';
            langContainer.style.top = '1rem';
            langContainer.style.right = '1rem';
            langContainer.appendChild(selector);
            header.style.position = 'relative';
            header.appendChild(langContainer);
        }
        
        return selector;
    }

    getCurrentLanguage() {
        return this.currentLanguage;
    }

    getSupportedLanguages() {
        return this.supportedLanguages;
    }
}

// Instancia global
const i18n = new I18n();

// Funciones globales para acceso desde HTML
function setLanguage(lang) {
    return i18n.setLanguage(lang);
}

function getCurrentLanguage() {
    return i18n.getCurrentLanguage();
}

function t(key, params = {}) {
    return i18n.t(key, params);
}

function translateBackendMessage(message) {
    return i18n.translateBackendMessage(message);
}

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => i18n.init());
} else {
    i18n.init();
}

// Exportar para uso global
window.i18n = i18n; 