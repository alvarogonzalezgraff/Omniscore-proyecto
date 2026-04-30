// Función de logout para usar con cookies
async function logoutWithCookies() {
    try {
        const response = await fetch('/api/auth/logout', {
            method: 'POST',
            credentials: 'include'  // Importante para cookies
        });
        
        if (response.ok) {
            // Limpiar localStorage
            localStorage.removeItem('currentUser');
            localStorage.removeItem('authToken');
            
            // Redirigir a login
            window.location.href = '/IniciarSesion.html';
        } else {
            console.error('Error al hacer logout');
        }
    } catch (error) {
        console.error('Error de conexión:', error);
        // Forzar logout local
        localStorage.removeItem('currentUser');
        localStorage.removeItem('authToken');
        window.location.href = '/IniciarSesion.html';
    }
}

// Función para verificar si el usuario está autenticado
async function checkAuthStatus() {
    try {
        const response = await fetch('/api/auth/me', {
            credentials: 'include'  // Importante para cookies
        });
        
        if (response.ok) {
            const userData = await response.json();
            // Actualizar localStorage con datos frescos
            localStorage.setItem('currentUser', JSON.stringify({
                id: userData.id,
                username: userData.username,
                email: userData.email,
                full_name: userData.full_name,
                loggedAt: new Date().toISOString()
            }));
            return true;
        } else {
            // Limpiar datos inválidos
            localStorage.removeItem('currentUser');
            localStorage.removeItem('authToken');
            return false;
        }
    } catch (error) {
        console.error('Error verificando autenticación:', error);
        return false;
    }
}

// Función helper para peticiones autenticadas
async function authenticatedFetch(url, options = {}) {
    const defaultOptions = {
        credentials: 'include',  // Siempre incluir cookies
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        }
    };
    
    return fetch(url, { ...defaultOptions, ...options });
}
