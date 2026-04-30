/**
 * FooterWrapper - Componente para manejo condicional del footer
 * Oculta el footer en páginas de login pero lo mantiene visible en el resto
 */

class FooterWrapper {
    constructor() {
        this.loginRoutes = [
            '/login',
            '/auth/login', 
            '/signin',
            '/auth/signin',
            '/ingresar',
            '/auth/ingresar'
        ];
        this.init();
    }

    /**
     * Inicializa el wrapper
     */
    init() {
        // Esperar a que el DOM esté listo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupFooter());
        } else {
            this.setupFooter();
        }
    }

    /**
     * Configura el footer según la ruta actual
     */
    setupFooter() {
        const currentPath = window.location.pathname;
        
        if (this.isLoginPage(currentPath)) {
            this.hideFooter();
        } else {
            this.showFooter();
        }
    }

    /**
     * Verifica si la ruta actual es una página de login
     * @param {string} path - Ruta actual
     * @returns {boolean} True si es página de login
     */
    isLoginPage(path) {
        return this.loginRoutes.some(route => {
            // Comparación exacta o si la ruta comienza con la ruta de login
            return path === route || path.startsWith(route + '/');
        });
    }

    /**
     * Oculta el footer
     */
    hideFooter() {
        const footer = document.querySelector('footer');
        if (footer) {
            footer.style.display = 'none';
            
            // Añadir clase al body para CSS adicional si es necesario
            document.body.classList.add('login-page');
        }
    }

    /**
     * Muestra el footer
     */
    showFooter() {
        const footer = document.querySelector('footer');
        if (footer) {
            footer.style.display = '';
            
            // Remover clase del body
            document.body.classList.remove('login-page');
        }
    }

    /**
     * Actualiza el estado del footer (útil para SPAs)
     */
    update() {
        this.setupFooter();
    }

    /**
     * Añade rutas de login adicionales
     * @param {string[]} routes - Nuevas rutas de login
     */
    addLoginRoutes(routes) {
        this.loginRoutes.push(...routes);
    }

    /**
     * Remueve rutas de login
     * @param {string[]} routes - Rutas a remover
     */
    removeLoginRoutes(routes) {
        routes.forEach(route => {
            const index = this.loginRoutes.indexOf(route);
            if (index > -1) {
                this.loginRoutes.splice(index, 1);
            }
        });
    }
}

// Crear instancia global
const footerWrapper = new FooterWrapper();

// Para SPAs, escuchar cambios de ruta
if (typeof window !== 'undefined') {
    // Detectar cambios de URL (para SPAs sin router)
    let currentPath = window.location.pathname;
    
    // Usar MutationObserver para detectar cambios en el history
    const originalPushState = history.pushState;
    const originalReplaceState = history.replaceState;
    
    history.pushState = function(...args) {
        originalPushState.apply(history, args);
        setTimeout(() => footerWrapper.update(), 0);
    };
    
    history.replaceState = function(...args) {
        originalReplaceState.apply(history, args);
        setTimeout(() => footerWrapper.update(), 0);
    };
    
    // Escuchar eventos de navegación
    window.addEventListener('popstate', () => {
        setTimeout(() => footerWrapper.update(), 0);
    });
    
    // Para hash routing
    window.addEventListener('hashchange', () => {
        setTimeout(() => footerWrapper.update(), 0);
    });
}

// Exportar para uso en módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FooterWrapper;
} else {
    window.FooterWrapper = FooterWrapper;
    window.footerWrapper = footerWrapper;
}
