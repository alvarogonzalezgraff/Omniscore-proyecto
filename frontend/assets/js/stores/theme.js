/**
 * Global Theme Management System
 * Manages application-wide theme state with real-time updates and persistence
 */

class ThemeStore {
    constructor() {
        this.listeners = new Set();
        this.currentTheme = this.getDefaultTheme();
        this.isInitialized = false;
        
        // Initialize immediately
        this.init();
    }

    /**
     * Default theme configuration
     */
    getDefaultTheme() {
        return {
            theme: 'default',
            backgroundColor: '#f8fafc',
            textColor: '#1f2937',
            accentColor: '#3b82f6',
            sidebarStyle: 'default',
            fontSize: 'normal',
            borderColor: '#e5e7eb',
            surfaceColor: '#ffffff',
            headerBackground: '#ffffff',
            footerBackground: '#1f2937'
        };
    }

    /**
     * Initialize theme store
     */
    async init() {
        if (this.isInitialized) return;
        
        try {
            // Load saved theme from localStorage
            const savedTheme = this.loadFromLocalStorage();
            if (savedTheme) {
                this.currentTheme = { ...this.currentTheme, ...savedTheme };
            }
            
            // Apply theme immediately
            this.applyTheme(this.currentTheme);
            
            this.isInitialized = true;
            this.notifyListeners();
            
        } catch (error) {
            console.error('Error initializing theme store:', error);
        }
    }

    /**
     * Load theme from localStorage
     */
    loadFromLocalStorage() {
        try {
            const stored = localStorage.getItem('Omniscore_theme');
            return stored ? JSON.parse(stored) : null;
        } catch (error) {
            console.warn('Error loading theme from localStorage:', error);
            return null;
        }
    }

    /**
     * Save theme to localStorage
     */
    saveToLocalStorage(theme) {
        try {
            localStorage.setItem('Omniscore_theme', JSON.stringify(theme));
        } catch (error) {
            console.warn('Error saving theme to localStorage:', error);
        }
    }

    /**
     * Apply theme to the document
     */
    applyTheme(themeConfig) {
        const root = document.documentElement;
        const body = document.body;
        
        // Apply CSS custom properties
        const cssVars = {
            '--bg-primary': themeConfig.backgroundColor,
            '--text-primary': themeConfig.textColor,
            '--accent-color': themeConfig.accentColor,
            '--border-color': themeConfig.borderColor,
            '--surface-color': themeConfig.surfaceColor,
            '--header-bg': themeConfig.headerBackground,
            '--footer-bg': themeConfig.footerBackground
        };
        
        Object.entries(cssVars).forEach(([property, value]) => {
            root.style.setProperty(property, value);
        });
        
        // Apply theme classes to body
        body.className = body.className.replace(/theme-\w+/g, '');
        body.classList.add(`theme-${themeConfig.theme}`);
        
        // Apply font size
        body.className = body.className.replace(/font-size-\w+/g, '');
        body.classList.add(`font-size-${themeConfig.fontSize}`);
        
        // Apply sidebar style
        body.className = body.className.replace(/sidebar-\w+/g, '');
        body.classList.add(`sidebar-${themeConfig.sidebarStyle}`);
        
        // Store current theme
        this.currentTheme = { ...this.currentTheme, ...themeConfig };
    }

    /**
     * Update theme with new configuration
     */
    updateTheme(updates) {
        const newTheme = { ...this.currentTheme, ...updates };
        
        // Apply immediately
        this.applyTheme(newTheme);
        
        // Save to localStorage
        this.saveToLocalStorage(newTheme);
        
        // Optional: Save to backend if user is logged in
        this.saveToBackend(newTheme);
        
        // Notify listeners
        this.notifyListeners();
        
        return newTheme;
    }

    /**
     * Save theme to backend (if user is authenticated)
     */
    async saveToBackend(theme) {
        try {
            // Check if user is logged in
            const currentUser = this.getCurrentUser();
            if (!currentUser) return;
            
            // Send to backend API
            const response = await fetch('/api/user/theme', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ theme })
            });
            
            if (!response.ok) {
                throw new Error('Failed to save theme to backend');
            }
            
        } catch (error) {
            console.warn('Error saving theme to backend:', error);
        }
    }

    /**
     * Get current authenticated user
     */
    getCurrentUser() {
        try {
            const userStr = localStorage.getItem('currentUser');
            return userStr ? JSON.parse(userStr) : null;
        } catch (error) {
            return null;
        }
    }

    /**
     * Get current theme
     */
    getCurrentTheme() {
        return this.currentTheme;
    }

    /**
     * Reset theme to defaults
     */
    resetTheme() {
        const defaultTheme = this.getDefaultTheme();
        this.updateTheme(defaultTheme);
        return defaultTheme;
    }

    /**
     * Subscribe to theme changes
     */
    subscribe(callback) {
        this.listeners.add(callback);
        
        // Return unsubscribe function
        return () => {
            this.listeners.delete(callback);
        };
    }

    /**
     * Notify all listeners of theme changes
     */
    notifyListeners() {
        this.listeners.forEach(callback => {
            try {
                callback(this.currentTheme);
            } catch (error) {
                console.error('Error in theme listener:', error);
            }
        });
    }

    /**
     * Export theme configuration
     */
    exportTheme() {
        return JSON.stringify(this.currentTheme, null, 2);
    }

    /**
     * Import theme configuration
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
     * Get predefined themes
     */
    getPredefinedThemes() {
        return {
            default: {
                theme: 'default',
                backgroundColor: '#f8fafc',
                textColor: '#1f2937',
                accentColor: '#3b82f6',
                sidebarStyle: 'default',
                fontSize: 'normal',
                borderColor: '#e5e7eb',
                surfaceColor: '#ffffff',
                headerBackground: '#ffffff',
                footerBackground: '#1f2937'
            },
            light: {
                theme: 'light',
                backgroundColor: '#ffffff',
                textColor: '#000000',
                accentColor: '#3b82f6',
                sidebarStyle: 'default',
                fontSize: 'normal',
                borderColor: '#e5e7eb',
                surfaceColor: '#ffffff',
                headerBackground: '#ffffff',
                footerBackground: '#f8fafc'
            },
            dark: {
                theme: 'dark',
                backgroundColor: '#0f172a',
                textColor: '#f8fafc',
                accentColor: '#3b82f6',
                sidebarStyle: 'default',
                fontSize: 'normal',
                borderColor: '#1f2937',
                surfaceColor: '#1e293b',
                headerBackground: '#1e293b',
                footerBackground: '#0f172a'
            },
            minimal: {
                theme: 'minimal',
                backgroundColor: '#ffffff',
                textColor: '#1a1a1a',
                accentColor: '#000000',
                sidebarStyle: 'minimal',
                fontSize: 'normal',
                borderColor: '#d1d5db',
                surfaceColor: '#ffffff',
                headerBackground: '#ffffff',
                footerBackground: '#f9fafb'
            }
        };
    }

    /**
     * Apply predefined theme
     */
    applyPredefinedTheme(themeName) {
        const themes = this.getPredefinedThemes();
        const theme = themes[themeName];
        
        if (theme) {
            this.updateTheme(theme);
            return theme;
        }
        
        throw new Error(`Theme '${themeName}' not found`);
    }
}

// Create global instance
const themeStore = new ThemeStore();

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ThemeStore, themeStore };
} else {
    window.ThemeStore = ThemeStore;
    window.themeStore = themeStore;
}

// Helper function for easy access
window.useTheme = () => themeStore;
