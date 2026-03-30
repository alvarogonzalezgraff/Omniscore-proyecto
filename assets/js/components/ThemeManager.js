/**
 * Gestor de Temas con Variables CSS
 * Sistema de personalización con persistencia y actualización en tiempo real
 */

class ThemeManager {
    constructor() {
        this.currentTheme = this.getStoredTheme() || this.getDefaultTheme();
        this.isPreviewMode = false;
        this.previewTheme = null;
        this.observers = [];
        
        this.init();
    }

    /**
     * Inicializa el gestor
     */
    async init() {
        this.applyTheme(this.currentTheme);
        this.setupSystemThemeListener();
        
        // Intentar cargar desde el servidor si hay usuario autenticado
        await this.loadFromServer();
    }

    /**
     * Obtiene el tema por defecto
     */
    getDefaultTheme() {
        return {
            backgroundColor: '#f5f5f5',
            textColor: 'auto',
            accentColor: '#3b82f6',
            fontSize: 'normal',
            fontFamily: 'system',
            borderRadius: 'normal',
            density: 'normal'
        };
    }

    /**
     * Obtiene el tema almacenado en localStorage
     */
    getStoredTheme() {
        try {
            const stored = localStorage.getItem('omniscore-theme');
            return stored ? JSON.parse(stored) : null;
        } catch (error) {
            console.error('Error loading theme from localStorage:', error);
            return null;
        }
    }

    /**
     * Guarda el tema en localStorage
     */
    saveTheme(theme) {
        try {
            localStorage.setItem('omniscore-theme', JSON.stringify(theme));
        } catch (error) {
            console.error('Error saving theme to localStorage:', error);
        }
    }

    /**
     * Aplica las variables CSS según el tema
     */
    applyTheme(theme) {
        const root = document.documentElement;
        
        // Colores
        root.style.setProperty('--bg-primary', theme.backgroundColor);
        root.style.setProperty('--bg-surface', this.adjustColor(theme.backgroundColor, 10));
        root.style.setProperty('--bg-elevated', this.adjustColor(theme.backgroundColor, 20));
        
        // Texto
        const textColor = this.computeTextColor(theme.backgroundColor, theme.textColor);
        root.style.setProperty('--text-primary', textColor);
        root.style.setProperty('--text-secondary', this.adjustColor(textColor, 30));
        root.style.setProperty('--text-muted', this.adjustColor(textColor, 50));
        
        // Acentos
        root.style.setProperty('--accent-color', theme.accentColor);
        root.style.setProperty('--accent-hover', this.adjustColor(theme.accentColor, -20));
        root.style.setProperty('--border-focus', theme.accentColor);
        
        // Gradientes
        const gradient = this.generateGradient(theme.backgroundColor);
        root.style.setProperty('--bg-gradient', gradient);
        
        // Tipografía
        const fontFamily = this.getFontFamily(theme.fontFamily);
        root.style.setProperty('--font-family-base', fontFamily);
        root.style.setProperty('--font-size-base', this.getFontSize(theme.fontSize));
        
        // Bordes
        const borderRadius = this.getBorderRadius(theme.borderRadius);
        root.style.setProperty('--border-radius-base', borderRadius);
        root.style.setProperty('--border-radius-lg', this.multiplyValue(borderRadius, 1.5));
        
        // Espaciado
        const spacing = this.getSpacing(theme.density);
        root.style.setProperty('--spacing-base', spacing);
        root.style.setProperty('--spacing-lg', this.multiplyValue(spacing, 1.5));
        
        // Notificar a los observadores
        this.notifyObservers(theme);
    }

    /**
     * Actualiza el tema actual
     */
    updateTheme(updates) {
        const newTheme = { ...this.currentTheme, ...updates };
        this.currentTheme = newTheme;
        this.applyTheme(newTheme);
        this.saveTheme(newTheme);
    }

    /**
     * Aplica tema en modo preview
     */
    applyPreviewTheme(theme) {
        this.isPreviewMode = true;
        this.previewTheme = theme;
        this.applyTheme(theme);
    }

    /**
     * Cancela el modo preview
     */
    cancelPreview() {
        this.isPreviewMode = false;
        this.previewTheme = null;
        this.applyTheme(this.currentTheme);
    }

    /**
     * Confirma el tema del preview
     */
    confirmPreview() {
        if (this.previewTheme) {
            this.currentTheme = this.previewTheme;
            this.saveTheme(this.currentTheme);
            this.isPreviewMode = false;
            this.previewTheme = null;
        }
    }

    /**
     * Resetea al tema por defecto
     */
    async resetTheme() {
        const defaultTheme = this.getDefaultTheme();
        this.currentTheme = defaultTheme;
        this.applyTheme(defaultTheme);
        this.saveTheme(defaultTheme);
        
        // También resetear en servidor si está autenticado
        await this.resetOnServer();
    }

    /**
     * Obtiene el tema actual
     */
    getCurrentTheme() {
        return this.isPreviewMode ? this.previewTheme : this.currentTheme;
    }

    /**
     * Exporta el tema
     */
    exportTheme() {
        return JSON.stringify(this.currentTheme, null, 2);
    }

    /**
     * Importa un tema
     */
    importTheme(themeJson) {
        try {
            const theme = JSON.parse(themeJson);
            this.updateTheme(theme);
            return true;
        } catch (error) {
            console.error('Error importing theme:', error);
            return false;
        }
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
     * Ajusta un color (claro/oscuro)
     */
    adjustColor(hex, percent) {
        const rgb = this.hexToRgb(hex);
        if (!rgb) return hex;
        
        const factor = percent > 0 ? 1 + (percent / 100) : 1 - (Math.abs(percent) / 100);
        
        const r = Math.min(255, Math.max(0, Math.round(rgb.r * factor)));
        const g = Math.min(255, Math.max(0, Math.round(rgb.g * factor)));
        const b = Math.min(255, Math.max(0, Math.round(rgb.b * factor)));
        
        return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
    }

    /**
     * Genera un gradiente basado en el color de fondo
     */
    generateGradient(baseColor) {
        const darker = this.adjustColor(baseColor, -30);
        const lighter = this.adjustColor(baseColor, 10);
        return `linear-gradient(135deg, ${darker} 0%, ${lighter} 100%)`;
    }

    /**
     * Obtiene la familia de fuente
     */
    getFontFamily(fontFamily) {
        const families = {
            system: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            serif: 'Georgia, "Times New Roman", serif',
            monospace: '"Fira Code", "Courier New", monospace'
        };
        return families[fontFamily] || families.system;
    }

    /**
     * Obtiene el tamaño de fuente
     */
    getFontSize(fontSize) {
        const sizes = {
            small: '14px',
            normal: '16px',
            large: '18px',
            'x-large': '20px'
        };
        return sizes[fontSize] || '16px';
    }

    /**
     * Obtiene el radio de borde
     */
    getBorderRadius(borderRadius) {
        const radii = {
            none: '0px',
            small: '4px',
            normal: '8px',
            large: '12px'
        };
        return radii[borderRadius] || '8px';
    }

    /**
     * Obtiene el espaciado
     */
    getSpacing(density) {
        const densities = {
            compact: '12px',
            normal: '16px',
            comfortable: '20px'
        };
        return densities[density] || '16px';
    }

    /**
     * Multiplica un valor numérico CSS
     */
    multiplyValue(value, factor) {
        const num = parseFloat(value);
        if (isNaN(num)) return value;
        return `${num * factor}px`;
    }

    /**
     * Escucha cambios en el tema del sistema
     */
    setupSystemThemeListener() {
        if (window.matchMedia) {
            const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
            darkModeQuery.addListener((e) => {
                if (!this.currentTheme.backgroundColor || this.currentTheme.backgroundColor === 'auto') {
                    const systemTheme = e.matches ? 'dark' : 'light';
                    this.applySystemTheme(systemTheme);
                }
            });
        }
    }

    /**
     * Aplica tema del sistema
     */
    applySystemTheme(systemTheme) {
        const systemColors = {
            light: {
                backgroundColor: '#f5f5f5',
                textColor: 'auto'
            },
            dark: {
                backgroundColor: '#1a1a1a',
                textColor: 'auto'
            }
        };
        
        this.updateTheme(systemColors[systemTheme]);
    }

    /**
     * Agrega un observador de cambios de tema
     */
    addObserver(callback) {
        this.observers.push(callback);
    }

    /**
     * Remueve un observador
     */
    removeObserver(callback) {
        this.observers = this.observers.filter(obs => obs !== callback);
    }

    /**
     * Notifica a todos los observadores
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
     * Sincroniza con el servidor (para usuarios autenticados)
     */
    async syncWithServer() {
        // Verificar si hay usuario autenticado
        const token = this.getAuthToken();
        if (!token) return;

        try {
            // Enviar tema al servidor
            const response = await fetch('/api/theme/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(this.currentTheme)
            });

            if (!response.ok) {
                throw new Error('Failed to sync theme with server');
            }

            const result = await response.json();
            console.log('Theme synced with server:', result);
        } catch (error) {
            console.error('Error syncing theme with server:', error);
        }
    }

    /**
     * Carga tema desde el servidor
     */
    async loadFromServer() {
        const token = this.getAuthToken();
        if (!token) return;

        try {
            const response = await fetch('/api/theme/load', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                if (response.status === 401) {
                    // Usuario no autenticado, usar localStorage
                    return;
                }
                throw new Error('Failed to load theme from server');
            }

            const result = await response.json();
            if (result.success && result.theme && Object.keys(result.theme).length > 0) {
                // Combinar con tema actual (servidor tiene prioridad)
                const serverTheme = result.theme;
                this.updateTheme(serverTheme);
                this.saveTheme(serverTheme); // Actualizar localStorage
            }
        } catch (error) {
            console.error('Error loading theme from server:', error);
        }
    }

    /**
     * Resetea tema en servidor
     */
    async resetOnServer() {
        const token = this.getAuthToken();
        if (!token) return;

        try {
            const response = await fetch('/api/theme/reset', {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to reset theme on server');
            }

            console.log('Theme reset on server');
        } catch (error) {
            console.error('Error resetting theme on server:', error);
        }
    }

    /**
     * Obtiene el token de autenticación
     */
    getAuthToken() {
        // Implementar según tu sistema de autenticación
        return document.cookie
            .split('; ')
            .find(row => row.startsWith('access_token='))
            ?.split('=')[1];
    }
}

// Crear instancia global
const themeManager = new ThemeManager();

// Exportar para uso global
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ThemeManager, themeManager };
} else {
    window.ThemeManager = ThemeManager;
    window.themeManager = themeManager;
    window.themeStore = themeManager; // Compatibilidad con código existente
}
