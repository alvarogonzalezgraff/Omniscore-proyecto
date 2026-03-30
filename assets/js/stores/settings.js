/**
 * Store de Configuración de Apariencia
 * Gestiona la persistencia y estado de las configuraciones visuales
 */

class SettingsStore {
    constructor() {
        this.settings = this.getDefaultSettings();
        this.listeners = [];
        this.storageKey = 'app_settings';
        this.isInitialized = false;
        
        this.init();
    }

    /**
     * Obtiene la configuración por defecto
     */
    getDefaultSettings() {
        return {
            theme: {
                backgroundColor: '#f5f5f5',
                textColor: 'auto',
                accentColor: '#3b82f6',
                fontSize: 'normal',
                fontFamily: 'system',
                borderRadius: 'normal',
                density: 'normal'
            },
            layout: {
                sidebarCollapsed: false,
                showBreadcrumbs: true,
                enableAnimations: true,
                stickyHeader: true
            }
        };
    }

    /**
     * Inicializa el store
     */
    async init() {
        if (this.isInitialized) return;
        
        try {
            // Cargar configuración desde localStorage
            const savedSettings = this.loadFromStorage();
            
            if (savedSettings) {
                // Fusionar con valores por defecto para soportar nuevas propiedades
                this.settings = this.mergeSettings(this.getDefaultSettings(), savedSettings);
            }
            
            // Detectar preferencias del sistema si no hay configuración guardada
            if (!savedSettings) {
                this.detectSystemPreferences();
            }
            
            // Aplicar configuración inicial
            this.applySettings();
            
            this.isInitialized = true;
            this.notifyListeners();
            
        } catch (error) {
            console.error('Error inicializando settings store:', error);
            this.settings = this.getDefaultSettings();
            this.isInitialized = true;
        }
    }

    /**
     * Detecta preferencias del sistema
     */
    detectSystemPreferences() {
        // Detectar tema oscuro/claro
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            this.settings.theme.backgroundColor = '#1a1a1a';
        }
        
        // Detectar preferencia de movimiento reducido
        if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            this.settings.layout.enableAnimations = false;
        }
    }

    /**
     * Fusiona configuraciones (deep merge)
     */
    mergeSettings(defaultSettings, savedSettings) {
        const merged = JSON.parse(JSON.stringify(defaultSettings));
        
        function mergeDeep(target, source) {
            for (const key in source) {
                if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
                    target[key] = target[key] || {};
                    mergeDeep(target[key], source[key]);
                } else {
                    target[key] = source[key];
                }
            }
        }
        
        mergeDeep(merged, savedSettings);
        return merged;
    }

    /**
     * Carga configuración desde localStorage
     */
    loadFromStorage() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            return stored ? JSON.parse(stored) : null;
        } catch (error) {
            console.error('Error cargando settings desde localStorage:', error);
            return null;
        }
    }

    /**
     * Guarda configuración en localStorage
     */
    saveToStorage() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.settings));
            return true;
        } catch (error) {
            console.error('Error guardando settings en localStorage:', error);
            return false;
        }
    }

    /**
     * Aplica las configuraciones actuales
     */
    applySettings() {
        if (typeof document === 'undefined') return;
        
        const root = document.documentElement;
        const body = document.body;
        
        // Aplicar variables CSS
        this.applyCSSVariables(root);
        
        // Aplicar clases al body
        this.applyBodyClasses(body);
        
        // Aplicar configuraciones de layout
        this.applyLayoutSettings(body);
    }

    /**
     * Aplica variables CSS al elemento :root
     */
    applyCSSVariables(root) {
        const theme = this.settings.theme;
        
        // Colores
        root.style.setProperty('--bg-primary', theme.backgroundColor);
        root.style.setProperty('--accent-color', theme.accentColor);
        
        // Texto (auto o específico)
        const textColor = this.getComputedTextColor();
        root.style.setProperty('--text-primary', textColor);
        root.style.setProperty('--text-secondary', this.adjustColorBrightness(textColor, 0.7));
        root.style.setProperty('--text-muted', this.adjustColorBrightness(textColor, 0.5));
        
        // Tipografía
        const fontSizes = {
            small: '14px',
            normal: '16px',
            large: '18px',
            'x-large': '20px'
        };
        root.style.setProperty('--font-size-base', fontSizes[theme.fontSize] || '16px');
        
        const fontFamilies = {
            system: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            serif: 'Georgia, "Times New Roman", serif',
            monospace: '"Fira Code", "Courier New", monospace'
        };
        root.style.setProperty('--font-family-base', fontFamilies[theme.fontFamily] || fontFamilies.system);
        
        // Bordes
        const borderRadii = {
            none: '0px',
            small: '4px',
            normal: '8px',
            large: '12px'
        };
        root.style.setProperty('--border-radius-base', borderRadii[theme.borderRadius] || '8px');
        
        // Densidad
        const densities = {
            compact: '0.5rem',
            normal: '1rem',
            comfortable: '1.5rem'
        };
        root.style.setProperty('--spacing-base', densities[theme.density] || '1rem');
        root.style.setProperty('--spacing-sm', `calc(${densities[theme.density] || '1rem'} * 0.5)`);
        root.style.setProperty('--spacing-lg', `calc(${densities[theme.density] || '1rem'} * 1.5)`);
    }

    /**
     * Calcula el color de texto basado en el fondo
     */
    getComputedTextColor() {
        const theme = this.settings.theme;
        
        if (theme.textColor !== 'auto') {
            return theme.textColor;
        }
        
        // Calcular contraste automático
        const luminance = this.calculateLuminance(theme.backgroundColor);
        return luminance > 0.5 ? '#000000' : '#ffffff';
    }

    /**
     * Calcula la luminancia de un color
     */
    calculateLuminance(hex) {
        const rgb = this.hexToRgb(hex);
        if (!rgb) return 0.5;
        
        const { r, g, b } = rgb;
        const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
        return luminance;
    }

    /**
     * Convierte hex a RGB
     */
    hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : null;
    }

    /**
     * Ajusta el brillo de un color
     */
    adjustColorBrightness(hex, factor) {
        const rgb = this.hexToRgb(hex);
        if (!rgb) return hex;
        
        const { r, g, b } = rgb;
        const adjust = factor > 1 ? 
            (255 - r) * (factor - 1) : 
            r * (1 - factor);
        
        const newR = Math.round(Math.min(255, Math.max(0, r + adjust)));
        const newG = Math.round(Math.min(255, Math.max(0, g + adjust)));
        const newB = Math.round(Math.min(255, Math.max(0, b + adjust)));
        
        return `#${newR.toString(16).padStart(2, '0')}${newG.toString(16).padStart(2, '0')}${newB.toString(16).padStart(2, '0')}`;
    }

    /**
     * Aplica clases al body
     */
    applyBodyClasses(body) {
        const theme = this.settings.theme;
        
        // Clase de tema
        body.classList.remove('theme-light', 'theme-dark', 'theme-custom');
        
        if (theme.backgroundColor === '#ffffff' || theme.backgroundColor === '#f5f5f5') {
            body.classList.add('theme-light');
        } else if (theme.backgroundColor === '#1a1a1a') {
            body.classList.add('theme-dark');
        } else {
            body.classList.add('theme-custom');
        }
        
        // Clases de configuración
        body.classList.remove('font-small', 'font-normal', 'font-large', 'font-xlarge');
        body.classList.add(`font-${theme.fontSize}`);
        
        body.classList.remove('density-compact', 'density-normal', 'density-comfortable');
        body.classList.add(`density-${theme.density}`);
        
        body.classList.remove('border-none', 'border-small', 'border-normal', 'border-large');
        body.classList.add(`border-${theme.borderRadius}`);
        
        if (!theme.layout?.enableAnimations) {
            body.classList.add('no-animations');
        }
    }

    /**
     * Aplica configuraciones de layout
     */
    applyLayoutSettings(body) {
        const layout = this.settings.layout;
        
        // Sidebar colapsado
        if (layout.sidebarCollapsed) {
            body.classList.add('sidebar-collapsed');
        } else {
            body.classList.remove('sidebar-collapsed');
        }
        
        // Breadcrumbs
        if (!layout.showBreadcrumbs) {
            body.classList.add('hide-breadcrumbs');
        } else {
            body.classList.remove('hide-breadcrumbs');
        }
        
        // Header sticky
        if (layout.stickyHeader) {
            body.classList.add('sticky-header');
        } else {
            body.classList.remove('sticky-header');
        }
    }

    /**
     * Actualiza una configuración específica
     */
    updateSetting(path, value) {
        const keys = path.split('.');
        let current = this.settings;
        
        // Navegar al objeto padre
        for (let i = 0; i < keys.length - 1; i++) {
            if (!current[keys[i]]) {
                current[keys[i]] = {};
            }
            current = current[keys[i]];
        }
        
        // Actualizar valor
        current[keys[keys.length - 1]] = value;
        
        // Aplicar cambios
        this.applySettings();
        
        // Guardar en localStorage
        this.saveToStorage();
        
        // Notificar listeners
        this.notifyListeners();
    }

    /**
     * Actualiza múltiples configuraciones
     */
    updateSettings(updates) {
        Object.assign(this.settings, updates);
        this.applySettings();
        this.saveToStorage();
        this.notifyListeners();
    }

    /**
     * Restablece a valores por defecto
     */
    resetToDefaults() {
        this.settings = this.getDefaultSettings();
        this.applySettings();
        this.saveToStorage();
        this.notifyListeners();
    }

    /**
     * Registra un listener para cambios en la configuración
     */
    subscribe(callback) {
        this.listeners.push(callback);
        
        // Retornar función para unsuscribir
        return () => {
            const index = this.listeners.indexOf(callback);
            if (index > -1) {
                this.listeners.splice(index, 1);
            }
        };
    }

    /**
     * Notifica a todos los listeners
     */
    notifyListeners() {
        this.listeners.forEach(callback => {
            try {
                callback(this.settings);
            } catch (error) {
                console.error('Error en listener de settings:', error);
            }
        });
    }

    /**
     * Obtiene el estado actual
     */
    getSettings() {
        return { ...this.settings };
    }

    /**
     * Obtiene una configuración específica
     */
    getSetting(path) {
        const keys = path.split('.');
        let current = this.settings;
        
        for (const key of keys) {
            if (current && typeof current === 'object' && key in current) {
                current = current[key];
            } else {
                return undefined;
            }
        }
        
        return current;
    }

    /**
     * Verifica WCAG compliance para contraste
     */
    checkWCAGContrast() {
        const bgColor = this.settings.theme.backgroundColor;
        const textColor = this.getComputedTextColor();
        
        return this.calculateContrastRatio(bgColor, textColor) >= 4.5;
    }

    /**
     * Calcula ratio de contraste WCAG
     */
    calculateContrastRatio(color1, color2) {
        const rgb1 = this.hexToRgb(color1);
        const rgb2 = this.hexToRgb(color2);
        
        if (!rgb1 || !rgb2) return 1;
        
        const l1 = this.calculateLuminance(color1);
        const l2 = this.calculateLuminance(color2);
        
        const lighter = Math.max(l1, l2);
        const darker = Math.min(l1, l2);
        
        return (lighter + 0.05) / (darker + 0.05);
    }
}

// Crear instancia global
let settingsStore = null;

/**
 * Hook/composable para usar el store de configuración
 */
function useSettings() {
    if (!settingsStore) {
        settingsStore = new SettingsStore();
    }
    return settingsStore;
}

// Exportar para uso en módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SettingsStore, useSettings };
} else {
    window.SettingsStore = SettingsStore;
    window.useSettings = useSettings;
    window.settingsStore = useSettings();
}
