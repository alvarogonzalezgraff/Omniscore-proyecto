/**
 * Script de inicialización del sistema de temas
 * Debe cargarse antes que los componentes que usan temas
 */

(function() {
    'use strict';
    
    // Esperar a que el DOM esté listo
    function initThemeSystem() {
        if (window.themeManager) {
            console.log('Theme system already initialized');
            return;
        }
        
        // Crear instancia del gestor de temas
        if (window.ThemeManager) {
            window.themeManager = new window.ThemeManager();
            window.themeStore = window.themeManager; // Compatibilidad
            console.log('Theme system initialized successfully');
        } else {
            console.error('ThemeManager class not found');
        }
    }
    
    // Inicializar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initThemeSystem);
    } else {
        initThemeSystem();
    }
    
    // También inicializar si se carga dinámicamente
    if (window.addEventListener) {
        window.addEventListener('load', function() {
            if (!window.themeManager) {
                initThemeSystem();
            }
        });
    }
})();
