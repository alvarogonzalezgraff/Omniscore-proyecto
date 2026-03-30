/**
 * Componente AuthGuard para proteger rutas y componentes
 * Verifica autenticación antes de permitir acceso al contenido
 */

class AuthGuard {
    constructor(options = {}) {
        this.options = {
            loginPath: '/login',
            redirectToLogin: true,
            loadingComponent: null,
            unauthorizedComponent: null,
            ...options
        };
        
        this.auth = null;
        this.isInitialized = false;
    }

    /**
     * Inicializa el AuthGuard
     */
    async initialize() {
        if (this.isInitialized) return;
        
        // Esperar a que useAuth esté disponible
        if (typeof window !== 'undefined' && window.useAuth) {
            this.auth = window.useAuth();
            this.isInitialized = true;
        } else {
            // Reintentar después de un corto tiempo
            setTimeout(() => this.initialize(), 100);
        }
    }

    /**
     * Verifica si el usuario está autenticado
     * @returns {boolean} True si está autenticado
     */
    isAuthenticated() {
        return this.auth?.isAuthenticated || false;
    }

    /**
     * Obtiene el usuario actual
     * @returns {Object|null} Datos del usuario
     */
    getUser() {
        return this.auth?.user || null;
    }

    /**
     * Protege una ruta o componente
     * @param {Function|HTMLElement} component - Componente a proteger
     * @param {Object} options - Opciones adicionales
     * @returns {Promise<HTMLElement>} Componente protegido o redirección
     */
    async protect(component, options = {}) {
        await this.initialize();
        
        const mergedOptions = { ...this.options, ...options };
        
        // Si está cargando, mostrar componente de carga
        if (this.auth?.isLoading) {
            return this.renderLoading(mergedOptions);
        }
        
        // Si no está autenticado, redirigir o mostrar no autorizado
        if (!this.isAuthenticated()) {
            if (mergedOptions.redirectToLogin) {
                this.redirectToLogin(mergedOptions);
                return null;
            } else {
                return this.renderUnauthorized(mergedOptions);
            }
        }
        
        // Si está autenticado, renderizar el componente
        return this.renderComponent(component, mergedOptions);
    }

    /**
     * Renderiza el componente protegido
     * @param {Function|HTMLElement} component - Componente a renderizar
     * @param {Object} options - Opciones
     * @returns {HTMLElement} Componente renderizado
     */
    renderComponent(component, options) {
        if (typeof component === 'function') {
            return component(this.getUser());
        }
        
        if (component instanceof HTMLElement) {
            return component;
        }
        
        throw new Error('El componente debe ser una función o un HTMLElement');
    }

    /**
     * Renderiza componente de carga
     * @param {Object} options - Opciones
     * @returns {HTMLElement} Componente de carga
     */
    renderLoading(options) {
        if (options.loadingComponent) {
            return options.loadingComponent;
        }
        
        // Componente de carga por defecto
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'auth-loading';
        loadingDiv.innerHTML = `
            <div style="display: flex; justify-content: center; align-items: center; height: 100vh;">
                <div style="text-align: center;">
                    <div style="border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 20px;"></div>
                    <p>Verificando autenticación...</p>
                </div>
            </div>
            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        `;
        
        return loadingDiv;
    }

    /**
     * Renderiza componente no autorizado
     * @param {Object} options - Opciones
     * @returns {HTMLElement} Componente no autorizado
     */
    renderUnauthorized(options) {
        if (options.unauthorizedComponent) {
            return options.unauthorizedComponent;
        }
        
        // Componente no autorizado por defecto
        const unauthorizedDiv = document.createElement('div');
        unauthorizedDiv.className = 'auth-unauthorized';
        unauthorizedDiv.innerHTML = `
            <div style="display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f8f9fa;">
                <div style="text-align: center; padding: 40px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h2 style="color: #dc3545; margin-bottom: 20px;">Acceso Denegado</h2>
                    <p style="margin-bottom: 20px;">No tienes permisos para acceder a esta página.</p>
                    <button onclick="window.location.href='${options.loginPath}'" style="background-color: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer;">
                        Iniciar Sesión
                    </button>
                </div>
            </div>
        `;
        
        return unauthorizedDiv;
    }

    /**
     * Redirige a la página de login
     * @param {Object} options - Opciones
     */
    redirectToLogin(options) {
        const currentPath = window.location.pathname;
        const loginUrl = `${options.loginPath}?redirect=${encodeURIComponent(currentPath)}`;
        window.location.href = loginUrl;
    }

    /**
     * Crea un middleware para proteger rutas
     * @param {Object} options - Opciones
     * @returns {Function} Middleware
     */
    middleware(options = {}) {
        return async (req, res, next) => {
            await this.initialize();
            
            if (!this.isAuthenticated()) {
                if (options.redirectToLogin !== false) {
                    return res.redirect(options.loginPath || this.options.loginPath);
                } else {
                    return res.status(401).json({ error: 'No autorizado' });
                }
            }
            
            next();
        };
    }

    /**
     * Decora una función para requerir autenticación
     * @param {Function} fn - Función a proteger
     * @param {Object} options - Opciones
     * @returns {Function} Función protegida
     */
    protectFunction(fn, options = {}) {
        return async (...args) => {
            await this.initialize();
            
            if (!this.isAuthenticated()) {
                if (options.throwError !== false) {
                    throw new Error('No autenticado');
                }
                return null;
            }
            
            return fn(...args, this.getUser());
        };
    }

    /**
     * Verifica roles específicos
     * @param {string|string[]} roles - Roles requeridos
     * @returns {boolean} True si el usuario tiene los roles
     */
    hasRole(roles) {
        if (!this.isAuthenticated()) return false;
        
        const userRoles = this.getUser()?.roles || [];
        const requiredRoles = Array.isArray(roles) ? roles : [roles];
        
        return requiredRoles.some(role => userRoles.includes(role));
    }

    /**
     * Verifica permisos específicos
     * @param {string|string[]} permissions - Permisos requeridos
     * @returns {boolean} True si el usuario tiene los permisos
     */
    hasPermission(permissions) {
        if (!this.isAuthenticated()) return false;
        
        const userPermissions = this.getUser()?.permissions || [];
        const requiredPermissions = Array.isArray(permissions) ? permissions : [permissions];
        
        return requiredPermissions.some(permission => userPermissions.includes(permission));
    }

    /**
     * Protege componente con verificación de roles
     * @param {Function|HTMLElement} component - Componente a proteger
     * @param {string|string[]} roles - Roles requeridos
     * @param {Object} options - Opciones adicionales
     * @returns {Promise<HTMLElement>} Componente protegido
     */
    protectWithRoles(component, roles, options = {}) {
        return this.protect(component, {
            ...options,
            beforeRender: () => {
                if (!this.hasRole(roles)) {
                    if (options.unauthorizedComponent) {
                        return options.unauthorizedComponent;
                    }
                    
                    const unauthorizedDiv = document.createElement('div');
                    unauthorizedDiv.innerHTML = `
                        <div style="text-align: center; padding: 40px;">
                            <h2>Acceso Denegado</h2>
                            <p>No tienes los roles necesarios para acceder a esta página.</p>
                        </div>
                    `;
                    return unauthorizedDiv;
                }
                return null;
            }
        });
    }
}

// Crear instancia global
const authGuard = new AuthGuard();

// Función helper para uso rápido
function createAuthGuard(options) {
    return new AuthGuard(options);
}

// Para uso global
if (typeof window !== 'undefined') {
    window.AuthGuard = AuthGuard;
    window.authGuard = authGuard;
    window.createAuthGuard = createAuthGuard;
}

// Exportar para uso en módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AuthGuard, authGuard, createAuthGuard };
}
