/**
 * Sistema de autenticación con cookies de sesión
 * Proporciona funciones para login, logout y peticiones autenticadas
 */

class AuthManager {
    constructor() {
        this.baseURL = window.location.origin;
        this.isRefreshing = false;
        this.refreshPromise = null;
    }

    /**
     * Inicia sesión del usuario
     * @param {Object} credentials - Credenciales del usuario
     * @param {string} credentials.username - Nombre de usuario
     * @param {string} credentials.password - Contraseña
     * @returns {Promise<Object>} Respuesta del servidor
     */
    async login(credentials) {
        try {
            const response = await fetch(`${this.baseURL}/api/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(credentials),
                credentials: 'include' // Importante para cookies
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Error en el login');
            }

            const data = await response.json();
            
            if (data.success) {
                // Guardar datos del usuario en localStorage para acceso rápido
                localStorage.setItem('user', JSON.stringify(data.user));
                return data;
            } else {
                throw new Error(data.message || 'Error en el login');
            }
        } catch (error) {
            console.error('Error en login:', error);
            throw error;
        }
    }

    /**
     * Cierra la sesión del usuario
     * @returns {Promise<Object>} Respuesta del servidor
     */
    async logout() {
        try {
            const response = await fetch(`${this.baseURL}/api/auth/logout`, {
                method: 'POST',
                credentials: 'include'
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Error en el logout');
            }

            const data = await response.json();
            
            // Limpiar datos locales
            localStorage.removeItem('user');
            
            return data;
        } catch (error) {
            console.error('Error en logout:', error);
            // Limpiar datos locales incluso si hay error
            localStorage.removeItem('user');
            throw error;
        }
    }

    /**
     * Refresca el token de acceso automáticamente
     * @returns {Promise<boolean>} True si se refrescó correctamente
     */
    async refreshToken() {
        // Evitar múltiples refresh simultáneos
        if (this.isRefreshing) {
            return this.refreshPromise;
        }

        this.isRefreshing = true;
        this.refreshPromise = this.doRefreshToken();

        try {
            const result = await this.refreshPromise;
            return result;
        } finally {
            this.isRefreshing = false;
            this.refreshPromise = null;
        }
    }

    async doRefreshToken() {
        try {
            const response = await fetch(`${this.baseURL}/api/auth/refresh`, {
                method: 'POST',
                credentials: 'include'
            });

            if (!response.ok) {
                // Si el refresh falla, hacer logout
                await this.logout();
                return false;
            }

            return true;
        } catch (error) {
            console.error('Error refrescando token:', error);
            await this.logout();
            return false;
        }
    }

    /**
     * Realiza una petición autenticada con manejo automático de refresh
     * @param {string} url - URL de la petición
     * @param {Object} options - Opciones de fetch
     * @returns {Promise<Response>} Respuesta de la petición
     */
    async fetchWithAuth(url, options = {}) {
        // Asegurar que se incluyan las cookies
        const fetchOptions = {
            ...options,
            credentials: 'include'
        };

        // Añadir CSRF token para métodos que modifican datos
        if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(options.method?.toUpperCase())) {
            const csrfToken = this.getCSRFToken();
            if (csrfToken) {
                fetchOptions.headers = {
                    ...fetchOptions.headers,
                    'X-CSRF-Token': csrfToken
                };
            }
        }

        try {
            const response = await fetch(url, fetchOptions);

            // Si el token expiró (401), intentar refrescar
            if (response.status === 401) {
                const refreshed = await this.refreshToken();
                
                if (refreshed) {
                    // Reintentar la petición original con nuevo token
                    const newCsrfToken = this.getCSRFToken();
                    if (newCsrfToken && ['POST', 'PUT', 'DELETE', 'PATCH'].includes(options.method?.toUpperCase())) {
                        fetchOptions.headers = {
                            ...fetchOptions.headers,
                            'X-CSRF-Token': newCsrfToken
                        };
                    }
                    
                    return fetch(url, fetchOptions);
                } else {
                    // Redirigir al login si no se pudo refrescar
                    window.location.href = '/login';
                    throw new Error('Sesión expirada. Por favor inicie sesión nuevamente.');
                }
            }

            return response;
        } catch (error) {
            console.error('Error en petición autenticada:', error);
            throw error;
        }
    }

    /**
     * Obtiene el CSRF token de las cookies
     * @returns {string|null} CSRF token
     */
    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrf_token') {
                return decodeURIComponent(value);
            }
        }
        return null;
    }

    /**
     * Verifica si el usuario está autenticado
     * @returns {boolean} True si está autenticado
     */
    isAuthenticated() {
        const user = this.getCurrentUser();
        return !!user;
    }

    /**
     * Obtiene los datos del usuario actual
     * @returns {Object|null} Datos del usuario
     */
    getCurrentUser() {
        try {
            const userStr = localStorage.getItem('user');
            return userStr ? JSON.parse(userStr) : null;
        } catch (error) {
            console.error('Error obteniendo usuario:', error);
            return null;
        }
    }

    /**
     * Obtiene información actualizada del usuario desde el servidor
     * @returns {Promise<Object|null>} Datos del usuario
     */
    async fetchCurrentUser() {
        try {
            const response = await this.fetchWithAuth(`${this.baseURL}/api/auth/me`);
            
            if (response.ok) {
                const user = await response.json();
                localStorage.setItem('user', JSON.stringify(user));
                return user;
            }
            return null;
        } catch (error) {
            console.error('Error obteniendo usuario actual:', error);
            return null;
        }
    }

    /**
     * Obtiene un nuevo CSRF token del servidor
     * @returns {Promise<string|null>} Nuevo CSRF token
     */
    async getNewCSRFToken() {
        try {
            const response = await fetch(`${this.baseURL}/api/auth/csrf-token`, {
                method: 'GET',
                credentials: 'include'
            });

            if (response.ok) {
                const data = await response.json();
                return data.csrf_token;
            }
            return null;
        } catch (error) {
            console.error('Error obteniendo CSRF token:', error);
            return null;
        }
    }

    /**
     * Configura el manejador para detectar cuando las cookies son eliminadas
     */
    setupCookieMonitor() {
        // Monitorear cambios en las cookies cada 30 segundos
        setInterval(() => {
            const accessToken = this.getCookie('access_token');
            if (!accessToken && this.isAuthenticated()) {
                // Si no hay token pero el usuario está marcado como autenticado,
                // limpiar datos locales
                localStorage.removeItem('user');
                window.location.href = '/login';
            }
        }, 30000);
    }

    /**
     * Obtiene una cookie específica
     * @param {string} name - Nombre de la cookie
     * @returns {string|null} Valor de la cookie
     */
    getCookie(name) {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [cookieName, value] = cookie.trim().split('=');
            if (cookieName === name) {
                return decodeURIComponent(value);
            }
        }
        return null;
    }
}

// Crear instancia global
const auth = new AuthManager();

// Exportar para uso en módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = auth;
} else {
    window.auth = auth;
}
