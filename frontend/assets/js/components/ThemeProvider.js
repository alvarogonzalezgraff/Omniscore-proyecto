/**
 * ThemeProvider - Componente para aplicar temas visuales
 * Inyecta CSS variables y gestiona la aplicación de configuraciones
 * Enhanced with real-time theme management and persistence
 */

class ThemeProvider {
    constructor() {
        this.settingsStore = null;
        this.themeStore = null;
        this.isInitialized = false;
        this.previewMode = false;
        this.originalSettings = null;
        this.observers = new Set();
        
        this.init();
    }

    /**
     * Inicializa el ThemeProvider
     */
    async init() {
        if (this.isInitialized) return;
        
        try {
            // Wait for stores to be available
            await this.waitForStores();
            
            // Initialize theme store (new system)
            if (window.themeStore) {
                this.themeStore = window.themeStore;
                this.themeStore.subscribe((theme) => {
                    this.onThemeStoreChange(theme);
                });
            }
            
            // Initialize settings store (legacy system)
            if (window.useSettings) {
                this.settingsStore = window.useSettings();
                
                // Suscribirse a cambios
                this.settingsStore.subscribe((settings) => {
                    if (!this.previewMode) {
                        this.applyTheme(settings);
                    }
                });
                
                // Aplicar tema inicial
                this.applyTheme(this.settingsStore.getSettings());
            }
            
            // Set up mutation observer for dynamic content
            this.setupMutationObserver();
            
            this.isInitialized = true;
        } catch (error) {
            console.error('Error initializing ThemeProvider:', error);
            // Retry after delay
            setTimeout(() => this.init(), 100);
        }
    }

    /**
     * Wait for stores to be available
     */
    async waitForStores() {
        const maxWait = 5000; // 5 seconds
        const startTime = Date.now();
        
        while ((!window.useSettings && !window.themeStore) && 
               (Date.now() - startTime) < maxWait) {
            await new Promise(resolve => setTimeout(resolve, 100));
        }
    }

    /**
     * Handle theme store changes (new system)
     */
    onThemeStoreChange(theme) {
        this.applyThemeToDocument(theme);
        this.notifyObservers(theme);
    }

    /**
     * Apply theme directly to document (new system)
     */
    applyThemeToDocument(theme) {
        if (typeof document === 'undefined') return;
        
        const root = document.documentElement;
        const body = document.body;
        
        // Apply CSS custom properties
        this.applyCSSVariables(root, theme);
        
        // Apply theme classes
        this.applyThemeClasses(body, theme);
        
        // Update existing elements
        this.updateExistingElements(theme);
        
        // Emit event
        this.dispatchThemeChange({ theme });
    }

    /**
     * Apply CSS variables from theme object
     */
    applyCSSVariables(root, theme) {
        // Core theme variables
        root.style.setProperty('--bg-primary', theme.backgroundColor);
        root.style.setProperty('--text-primary', theme.textColor);
        root.style.setProperty('--accent-color', theme.accentColor);
        root.style.setProperty('--border-color', theme.borderColor);
        root.style.setProperty('--surface-color', theme.surfaceColor);
        root.style.setProperty('--header-bg', theme.headerBackground);
        root.style.setProperty('--footer-bg', theme.footerBackground);
        
        // Calculate derived colors
        const textColor = this.computeTextColor(theme.backgroundColor, theme.textColor);
        root.style.setProperty('--text-secondary', this.adjustColorBrightness(textColor, 0.7));
        root.style.setProperty('--text-muted', this.adjustColorBrightness(textColor, 0.5));
        root.style.setProperty('--text-inverse', textColor === '#000000' ? '#ffffff' : '#000000');
        
        // Surface colors
        const surfaceColor = this.adjustColorBrightness(theme.backgroundColor, 0.05);
        root.style.setProperty('--bg-surface', surfaceColor);
        root.style.setProperty('--bg-elevated', this.adjustColorBrightness(theme.backgroundColor, 0.1));
        root.style.setProperty('--bg-overlay', this.adjustColorBrightness(theme.backgroundColor, 0.8));
        
        // Typography
        const fontSizes = {
            small: '14px',
            normal: '16px',
            large: '18px',
            'x-large': '20px'
        };
        root.style.setProperty('--font-size-base', fontSizes[theme.fontSize] || '16px');
        
        // Shadows
        const shadowIntensity = this.computeShadowIntensity(theme.backgroundColor);
        root.style.setProperty('--shadow-sm', `0 1px 2px 0 rgba(0, 0, 0, ${shadowIntensity * 0.05})`);
        root.style.setProperty('--shadow-base', `0 1px 3px 0 rgba(0, 0, 0, ${shadowIntensity * 0.1}), 0 1px 2px 0 rgba(0, 0, 0, ${shadowIntensity * 0.06})`);
        root.style.setProperty('--shadow-md', `0 4px 6px -1px rgba(0, 0, 0, ${shadowIntensity * 0.1}), 0 2px 4px -1px rgba(0, 0, 0, ${shadowIntensity * 0.06})`);
    }

    /**
     * Apply theme classes to body
     */
    applyThemeClasses(body, theme) {
        // Clear existing classes
        body.className = body.className.replace(/theme-\w+/g, '');
        body.className = body.className.replace(/font-size-\w+/g, '');
        body.className = body.className.replace(/sidebar-\w+/g, '');
        
        // Add new classes
        body.classList.add(`theme-${theme.theme}`);
        body.classList.add(`font-size-${theme.fontSize}`);
        body.classList.add(`sidebar-${theme.sidebarStyle}`);
    }

    /**
     * Update existing elements with new theme
     */
    updateExistingElements(theme) {
        // Update configuration page elements
        this.updateConfigPageElements(theme);
        
        // Update header elements
        this.updateHeaderElements(theme);
        
        // Update form elements
        this.updateFormElements(theme);
    }

    /**
     * Update configuration page elements
     */
    updateConfigPageElements(theme) {
        // Update main content
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.style.backgroundColor = theme.backgroundColor;
        }
        
        // Update page headers
        const pageHeaders = document.querySelectorAll('.page-header');
        pageHeaders.forEach(header => {
            header.style.backgroundColor = theme.surfaceColor;
            header.style.borderColor = theme.borderColor;
        });
        
        // Update config sections
        const configSections = document.querySelectorAll('.config-section');
        configSections.forEach(section => {
            section.style.backgroundColor = theme.surfaceColor;
            section.style.borderColor = theme.borderColor;
        });
        
        // Update tabs
        const configTabs = document.querySelector('.config-tabs');
        if (configTabs) {
            configTabs.style.backgroundColor = theme.surfaceColor;
            configTabs.style.borderColor = theme.borderColor;
        }
        
        // Update tab buttons
        const tabButtons = document.querySelectorAll('.tab-btn');
        tabButtons.forEach(btn => {
            if (btn.classList.contains('active')) {
                btn.style.color = theme.accentColor;
                btn.style.backgroundColor = this.adjustColorBrightness(theme.accentColor, 0.9);
                btn.style.borderBottom = `2px solid ${theme.accentColor}`;
            } else {
                btn.style.color = this.adjustColorBrightness(theme.textColor, 0.7);
                btn.style.backgroundColor = 'transparent';
            }
        });
    }

    /**
     * Update header elements
     */
    updateHeaderElements(theme) {
        const header = document.querySelector('header');
        if (header) {
            header.style.backgroundColor = theme.headerBackground;
            header.style.borderColor = theme.borderColor;
        }
        
        const logo = document.querySelector('.logo');
        if (logo) {
            logo.style.color = theme.accentColor;
        }
        
        const navLinks = document.querySelectorAll('nav ul li a');
        navLinks.forEach(link => {
            link.style.color = this.adjustColorBrightness(theme.textColor, 0.7);
        });
    }

    /**
     * Update form elements
     */
    updateFormElements(theme) {
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.style.backgroundColor = theme.surfaceColor;
            input.style.borderColor = theme.borderColor;
            input.style.color = theme.textColor;
        });
    }

    /**
     * Set up mutation observer for dynamic content
     */
    setupMutationObserver() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            this.applyThemeToElement(node, this.themeStore?.getCurrentTheme());
                        }
                    });
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        this.observer = observer;
    }

    /**
     * Apply theme to specific element
     */
    applyThemeToElement(element, theme) {
        if (!theme) return;
        
        // Apply based on element type
        if (element.classList.contains('config-section')) {
            element.style.backgroundColor = theme.surfaceColor;
            element.style.borderColor = theme.borderColor;
        } else if (element.classList.contains('tab-btn')) {
            this.applyTabTheme(element, theme);
        }
    }

    /**
     * Apply theme to tab button
     */
    applyTabTheme(tabBtn, theme) {
        if (tabBtn.classList.contains('active')) {
            tabBtn.style.color = theme.accentColor;
            tabBtn.style.backgroundColor = this.adjustColorBrightness(theme.accentColor, 0.9);
        } else {
            tabBtn.style.color = this.adjustColorBrightness(theme.textColor, 0.7);
            tabBtn.style.backgroundColor = 'transparent';
        }
    }

    /**
     * Subscribe to theme changes
     */
    subscribe(callback) {
        this.observers.add(callback);
        return () => this.observers.delete(callback);
    }

    /**
     * Notify observers
     */
    notifyObservers(theme) {
        this.observers.forEach(callback => {
            try {
                callback(theme);
            } catch (error) {
                console.error('Error in theme observer:', error);
            }
        });
    }

    /**
     * Limpia clases previas del body
     */
    clearPreviousClasses(body) {
        const themeClasses = [
            'theme-light', 'theme-dark', 'theme-custom',
            'font-small', 'font-normal', 'font-large', 'font-xlarge',
            'density-compact', 'density-normal', 'density-comfortable',
            'border-none', 'border-small', 'border-normal', 'border-large',
            'no-animations', 'sidebar-collapsed', 'hide-breadcrumbs',
            'sticky-header', 'high-contrast'
        ];
        
        body.classList.remove(...themeClasses);
    }

    /**
     * Aplica variables CSS al elemento :root
     */
    applyCSSVariables(root, theme) {
        // Variables de color
        root.style.setProperty('--bg-primary', theme.backgroundColor);
        root.style.setProperty('--accent-color', theme.accentColor);
        
        // Calcular colores derivados
        const textColor = this.computeTextColor(theme.backgroundColor, theme.textColor);
        root.style.setProperty('--text-primary', textColor);
        root.style.setProperty('--text-secondary', this.adjustColorBrightness(textColor, 0.7));
        root.style.setProperty('--text-muted', this.adjustColorBrightness(textColor, 0.5));
        root.style.setProperty('--text-inverse', textColor === '#000000' ? '#ffffff' : '#000000');
        
        // Colores de superficie
        const surfaceColor = this.adjustColorBrightness(theme.backgroundColor, 0.05);
        root.style.setProperty('--bg-surface', surfaceColor);
        root.style.setProperty('--bg-elevated', this.adjustColorBrightness(theme.backgroundColor, 0.1));
        root.style.setProperty('--bg-overlay', this.adjustColorBrightness(theme.backgroundColor, 0.8));
        
        // Variables de tipografía
        const fontSizes = {
            small: '14px',
            normal: '16px',
            large: '18px',
            'x-large': '20px'
        };
        root.style.setProperty('--font-size-base', fontSizes[theme.fontSize] || '16px');
        root.style.setProperty('--font-size-sm', `calc(${fontSizes[theme.fontSize] || '16px'} * 0.875)`);
        root.style.setProperty('--font-size-lg', `calc(${fontSizes[theme.fontSize] || '16px'} * 1.125)`);
        root.style.setProperty('--font-size-xl', `calc(${fontSizes[theme.fontSize] || '16px'} * 1.25)`);
        
        const fontFamilies = {
            system: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            serif: 'Georgia, "Times New Roman", serif',
            monospace: '"Fira Code", "Courier New", monospace'
        };
        root.style.setProperty('--font-family-base', fontFamilies[theme.fontFamily] || fontFamilies.system);
        
        // Variables de bordes
        const borderRadii = {
            none: '0px',
            small: '4px',
            normal: '8px',
            large: '12px'
        };
        root.style.setProperty('--border-radius-base', borderRadii[theme.borderRadius] || '8px');
        root.style.setProperty('--border-radius-sm', `calc(${borderRadii[theme.borderRadius] || '8px'} * 0.5)`);
        root.style.setProperty('--border-radius-lg', `calc(${borderRadii[theme.borderRadius] || '8px'} * 1.5)`);
        
        // Variables de espaciado
        const densities = {
            compact: '0.5rem',
            normal: '1rem',
            comfortable: '1.5rem'
        };
        root.style.setProperty('--spacing-base', densities[theme.density] || '1rem');
        root.style.setProperty('--spacing-xs', `calc(${densities[theme.density] || '1rem'} * 0.25)`);
        root.style.setProperty('--spacing-sm', `calc(${densities[theme.density] || '1rem'} * 0.5)`);
        root.style.setProperty('--spacing-md', `calc(${densities[theme.density] || '1rem'} * 0.75)`);
        root.style.setProperty('--spacing-lg', `calc(${densities[theme.density] || '1rem'} * 1.5)`);
        root.style.setProperty('--spacing-xl', `calc(${densities[theme.density] || '1rem'} * 2)`);
        
        // Variables de sombras (ajustadas según el tema)
        const shadowIntensity = this.computeShadowIntensity(theme.backgroundColor);
        root.style.setProperty('--shadow-sm', `0 1px 2px 0 rgba(0, 0, 0, ${shadowIntensity * 0.05})`);
        root.style.setProperty('--shadow-base', `0 1px 3px 0 rgba(0, 0, 0, ${shadowIntensity * 0.1}), 0 1px 2px 0 rgba(0, 0, 0, ${shadowIntensity * 0.06})`);
        root.style.setProperty('--shadow-md', `0 4px 6px -1px rgba(0, 0, 0, ${shadowIntensity * 0.1}), 0 2px 4px -1px rgba(0, 0, 0, ${shadowIntensity * 0.06})`);
        root.style.setProperty('--shadow-lg', `0 10px 15px -3px rgba(0, 0, 0, ${shadowIntensity * 0.1}), 0 4px 6px -2px rgba(0, 0, 0, ${shadowIntensity * 0.05})`);
        
        // Variables de transición
        const transitionDuration = theme.enableAnimations !== false ? '0.2s' : '0s';
        root.style.setProperty('--transition-base', `all ${transitionDuration} ease-in-out`);
        root.style.setProperty('--transition-fast', `all ${transitionDuration} ease-in-out`);
        root.style.setProperty('--transition-slow', `all ${parseFloat(transitionDuration) * 2}s ease-in-out`);
    }

    /**
     * Calcula el color de texto apropiado
     */
    computeTextColor(backgroundColor, textColor) {
        if (textColor !== 'auto') {
            return textColor;
        }
        
        const luminance = this.calculateLuminance(backgroundColor);
        return luminance > 0.5 ? '#000000' : '#ffffff';
    }

    /**
     * Calcula la intensidad de sombras según el fondo
     */
    computeShadowIntensity(backgroundColor) {
        const luminance = this.calculateLuminance(backgroundColor);
        return luminance > 0.5 ? 0.1 : 0.3;
    }

    /**
     * Calcula la luminancia de un color
     */
    calculateLuminance(hex) {
        const rgb = this.hexToRgb(hex);
        if (!rgb) return 0.5;
        
        const { r, g, b } = rgb;
        return (0.299 * r + 0.587 * g + 0.114 * b) / 255;
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
     * Aplica clases al body según el tema
     */
    applyBodyClasses(body, settings) {
        const theme = settings.theme;
        
        // Clase de tema principal
        if (theme.backgroundColor === '#ffffff' || theme.backgroundColor === '#f5f5f5') {
            body.classList.add('theme-light');
        } else if (theme.backgroundColor === '#1a1a1a') {
            body.classList.add('theme-dark');
        } else {
            body.classList.add('theme-custom');
        }
        
        // Clases de tipografía
        body.classList.add(`font-${theme.fontSize}`);
        
        // Clases de densidad
        body.classList.add(`density-${theme.density}`);
        
        // Clases de bordes
        body.classList.add(`border-${theme.borderRadius}`);
    }

    /**
     * Aplica configuraciones de layout
     */
    applyLayoutSettings(body, layout) {
        if (layout.sidebarCollapsed) {
            body.classList.add('sidebar-collapsed');
        }
        
        if (!layout.showBreadcrumbs) {
            body.classList.add('hide-breadcrumbs');
        }
        
        if (layout.stickyHeader) {
            body.classList.add('sticky-header');
        }
    }

    /**
     * Aplica configuraciones de accesibilidad
     */
    applyAccessibilitySettings(body, settings) {
        // Animaciones
        if (!settings.layout.enableAnimations || 
            (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches)) {
            body.classList.add('no-animations');
        }
        
        // Alto contraste si es necesario
        if (!this.settingsStore.checkWCAGContrast()) {
            body.classList.add('high-contrast');
        }
    }

    /**
     * Activa el modo preview para cambios en tiempo real
     */
    enablePreviewMode() {
        this.previewMode = true;
        this.originalSettings = this.settingsStore.getSettings();
    }

    /**
     * Desactiva el modo preview y restaura configuración original
     */
    disablePreviewMode() {
        this.previewMode = false;
        if (this.originalSettings) {
            this.applyTheme(this.originalSettings);
            this.originalSettings = null;
        }
    }

    /**
     * Aplica configuración temporal en modo preview
     */
    applyPreviewSettings(previewSettings) {
        if (!this.previewMode) return;
        
        const mergedSettings = { ...this.originalSettings, ...previewSettings };
        this.applyTheme(mergedSettings);
    }

    /**
     * Emite evento de cambio de tema
     */
    dispatchThemeChange(settings) {
        if (typeof window !== 'undefined') {
            const event = new CustomEvent('themechange', {
                detail: { settings }
            });
            window.dispatchEvent(event);
        }
    }

    /**
     * Obtiene las variables CSS actuales
     */
    getCurrentCSSVariables() {
        if (typeof document === 'undefined') return {};
        
        const root = document.documentElement;
        const styles = getComputedStyle(root);
        
        const variables = {};
        for (let i = 0; i < styles.length; i++) {
            const property = styles[i];
            if (property.startsWith('--')) {
                variables[property] = styles.getPropertyValue(property);
            }
        }
        
        return variables;
    }

    /**
     * Exporta configuración actual
     */
    exportSettings() {
        return this.settingsStore.getSettings();
    }

    /**
     * Importa configuración
     */
    importSettings(settings) {
        this.settingsStore.updateSettings(settings);
    }

    /**
     * Resetea a valores por defecto
     */
    resetToDefaults() {
        this.settingsStore.resetToDefaults();
    }
}

// Crear instancia global
let themeProvider = null;

/**
 * Función helper para obtener el ThemeProvider
 */
function getThemeProvider() {
    if (!themeProvider) {
        themeProvider = new ThemeProvider();
    }
    return themeProvider;
}

// Inicializar automáticamente cuando el DOM esté listo
if (typeof window !== 'undefined') {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            getThemeProvider();
        });
    } else {
        getThemeProvider();
    }
    
    window.ThemeProvider = ThemeProvider;
    window.getThemeProvider = getThemeProvider;
    window.themeProvider = getThemeProvider();
}

// Exportar para uso en módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ThemeProvider, getThemeProvider };
}
