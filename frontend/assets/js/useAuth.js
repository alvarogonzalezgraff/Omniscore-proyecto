/**
 * Hook/composable useAuth para manejo de autenticación
 * Proporciona estado y métodos de autenticación reactivos
 */

class UseAuth {
    constructor() {
        this.user = null;
        this.isAuthenticated = false;
        this.isLoading = true;
        this.listeners = [];
        
        // Inicializar estado
        this.initializeAuth();
        
        // Configurar monitoreo de cookies
        if (typeof window !== 'undefined') {
            window.auth?.setupCookieMonitor();
        }
    }

    /**
     * Inicializa el estado de autenticación
     */
    async initializeAuth() {
        try {
            // Verificar si hay usuario en localStorage
            const storedUser = window.auth?.getCurrentUser();
            
            if (storedUser) {
                this.user = storedUser;
                this.isAuthenticated = true;
                
                // Verificar con el servidor que la sesión sigue activa
                const currentUser = await window.auth?.fetchCurrentUser();
                if (currentUser) {
                    this.user = currentUser;
                } else {
                    // Si no se puede verificar, limpiar estado
                    this.user = null;
                    this.isAuthenticated = false;
                    localStorage.removeItem('user');
                }
            }
        } catch (error) {
            console.error('Error inicializando autenticación:', error);
            this.user = null;
            this.isAuthenticated = false;
        } finally {
            this.isLoading = false;
            this.notifyListeners();
        }
    }

    /**
     * Registra un listener para cambios en el estado de autenticación
     * @param {Function} callback - Función a ejecutar cuando cambie el estado
     * @returns {Function} Función para eliminar el listener
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
     * Notifica a todos los listeners sobre cambios en el estado
     */
    notifyListeners() {
        this.listeners.forEach(callback => {
            try {
                callback({
                    user: this.user,
                    isAuthenticated: this.isAuthenticated,
                    isLoading: this.isLoading
                });
            } catch (error) {
                console.error('Error en listener de autenticación:', error);
            }
        });
    }

    /**
     * Inicia sesión del usuario
     * @param {Object} credentials - Credenciales del usuario
     * @returns {Promise<Object>} Resultado del login
     */
    async login(credentials) {
        this.isLoading = true;
        this.notifyListeners();

        try {
            const result = await window.auth?.login(credentials);
            
            if (result?.success) {
                this.user = result.user;
                this.isAuthenticated = true;
                
                // Disparar evento de login exitoso
                this.dispatchEvent('auth:login', { user: this.user });
            }
            
            return result;
        } catch (error) {
            console.error('Error en login:', error);
            throw error;
        } finally {
            this.isLoading = false;
            this.notifyListeners();
        }
    }

    /**
     * Cierra la sesión del usuario
     * @returns {Promise<Object>} Resultado del logout
     */
    async logout() {
        this.isLoading = true;
        this.notifyListeners();

        try {
            const result = await window.auth?.logout();
            
            // Limpiar estado local independientemente del resultado
            const previousUser = this.user;
            this.user = null;
            this.isAuthenticated = false;
            
            // Disparar evento de logout
            this.dispatchEvent('auth:logout', { previousUser });
            
            return result;
        } catch (error) {
            console.error('Error en logout:', error);
            // Asegurarse de limpiar estado incluso si hay error
            this.user = null;
            this.isAuthenticated = false;
            throw error;
        } finally {
            this.isLoading = false;
            this.notifyListeners();
        }
    }

    /**
     * Actualiza los datos del usuario
     * @returns {Promise<Object|null>} Datos actualizados del usuario
     */
    async updateUser() {
        try {
            const updatedUser = await window.auth?.fetchCurrentUser();
            
            if (updatedUser) {
                this.user = updatedUser;
                this.notifyListeners();
                
                // Disparar evento de actualización
                this.dispatchEvent('auth:user-updated', { user: this.user });
            }
            
            return updatedUser;
        } catch (error) {
            console.error('Error actualizando usuario:', error);
            return null;
        }
    }

    /**
     * Verifica si el usuario tiene un rol específico
     * @param {string} role - Rol a verificar
     * @returns {boolean} True si el usuario tiene el rol
     */
    hasRole(role) {
        return this.user?.roles?.includes(role) || false;
    }

    /**
     * Verifica si el usuario tiene un permiso específico
     * @param {string} permission - Permiso a verificar
     * @returns {boolean} True si el usuario tiene el permiso
     */
    hasPermission(permission) {
        return this.user?.permissions?.includes(permission) || false;
    }

    /**
     * Dispara un evento personalizado
     * @param {string} eventName - Nombre del evento
     * @param {Object} detail - Detalles del evento
     */
    dispatchEvent(eventName, detail) {
        if (typeof window !== 'undefined') {
            const event = new CustomEvent(eventName, { detail });
            window.dispatchEvent(event);
        }
    }

    /**
     * Obtiene el estado actual de autenticación
     * @returns {Object} Estado actual
     */
    getState() {
        return {
            user: this.user,
            isAuthenticated: this.isAuthenticated,
            isLoading: this.isLoading
        };
    }

    /**
     * Reinicia el estado de autenticación
     */
    reset() {
        this.user = null;
        this.isAuthenticated = false;
        this.isLoading = false;
        this.notifyListeners();
    }
}

// Crear instancia global
let authInstance = null;

/**
 * Hook/composable useAuth
 * @returns {UseAuth} Instancia del manejador de autenticación
 */
function useAuth() {
    if (!authInstance) {
        authInstance = new UseAuth();
    }
    return authInstance;
}

// Para React-like components
if (typeof window !== 'undefined') {
    window.useAuth = useAuth;
    
    // Auto-inicializar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            useAuth();
        });
    } else {
        useAuth();
    }
}

// Para Vue-like composition API
if (typeof Vue !== 'undefined') {
    Vue.mixin({
        beforeCreate() {
            this.$auth = useAuth();
        }
    });
}

// Exportar para uso en módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { useAuth, UseAuth };
}
