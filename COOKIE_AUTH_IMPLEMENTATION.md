# Sistema de Autenticación con Cookies de Sesión

## Overview

Se ha implementado un sistema completo de autenticación basado en cookies de sesión que coexiste con el sistema existente sin modificar archivos ya existentes.

## 📁 Archivos Nuevos Creados

### Backend (API)
```
api/
├── session_auth.py          # Gestor de cookies de sesión y tokens JWT
├── verify_session.py        # Middleware de verificación de sesión
├── auth_endpoints.py        # Endpoints de autenticación (login, refresh, logout)
└── security_middleware.py   # Middleware de seguridad (CSRF, Rate Limiting, Security Headers)
```

### Frontend (Assets)
```
assets/js/
├── auth.js          # Librería principal de autenticación
├── useAuth.js       # Hook/composable para manejo de estado
└── AuthGuard.js     # Componente para proteger rutas y componentes
```

## 🔧 Variables de Entorno Requeridas

Añadir a tu archivo `.env`:

```env
# JWT Configuration (ya existentes, asegurar que estén configuradas)
SECRET_KEY=tu_clave_secreta_muy_segura_cambiala_en_produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Opcional: Rate limiting personalizado
RATE_LIMIT_REQUESTS_PER_MINUTE=60
```

## 🚀 Instrucciones de Integración

### Backend - Integración en `main.py`

Añadir las siguientes importaciones y configuración **SIN modificar la lógica existente**:

```python
# Añadir estas importaciones al inicio de main.py
from .auth_endpoints import router as auth_router
from .security_middleware import setup_security_middleware

# Después de crear la instancia de FastAPI, añadir:
app.include_router(auth_router)

# Configurar middlewares de seguridad (después de los CORS existentes)
setup_security_middleware(
    app,
    csrf_exclude_paths=[
        "/api/auth/login",
        "/api/auth/refresh", 
        "/api/auth/logout",
        "/api/auth/csrf-token",
        "/docs",
        "/openapi.json",
        "/redoc"
    ],
    rate_limit_requests_per_minute=60,
    rate_limit_exclude_paths=[
        "/docs",
        "/openapi.json",
        "/redoc",
        "/static",
        "/assets"
    ]
)
```

### Proteger Rutas Existentes

Para proteger rutas existentes sin modificar su lógica, añadir el middleware de verificación:

```python
from .verify_session import verify_session

# Ejemplo: proteger una ruta existente
@app.get("/api/ruta-protegida")
async def ruta_protegida(user: User = Depends(verify_session)):
    # La lógica existente permanece igual
    # 'user' está disponible automáticamente
    return {"message": "Acceso concedido", "user": user.username}
```

### Frontend - Integración en HTML

Añadir los scripts en tus plantillas HTML (antes de closing body tag):

```html
<!-- En templates/base.html o similar -->
<script src="/assets/js/auth.js"></script>
<script src="/assets/js/useAuth.js"></script>
<script src="/assets/js/AuthGuard.js"></script>

<!-- Opcional: inicialización automática -->
<script>
// Inicializar autenticación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    const auth = useAuth();
    
    // Escuchar cambios de autenticación
    auth.subscribe((state) => {
        if (state.isAuthenticated) {
            console.log('Usuario autenticado:', state.user);
        } else {
            console.log('Usuario no autenticado');
        }
    });
});
</script>
```

## 📋 Uso Práctico

### Login de Usuario

```javascript
// Formulario de login
async function handleLogin(event) {
    event.preventDefault();
    
    const credentials = {
        username: document.getElementById('username').value,
        password: document.getElementById('password').value
    };
    
    try {
        const result = await auth.login(credentials);
        if (result.success) {
            alert('Login exitoso');
            window.location.href = '/dashboard';
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}
```

### Petición Autenticada

```javascript
// Usar fetchWithAuth para peticiones autenticadas
async function fetchUserData() {
    try {
        const response = await auth.fetchWithAuth('/api/user/profile', {
            method: 'GET'
        });
        
        const data = await response.json();
        console.log('Datos del usuario:', data);
    } catch (error) {
        console.error('Error:', error);
    }
}
```

### Proteger Componentes

```javascript
// Proteger un componente
const protectedComponent = authGuard.protect(
    (user) => {
        // Componente que solo se muestra si está autenticado
        return `<h1>Bienvenido ${user.full_name}</h1>`;
    }
);

// Insertar en el DOM
document.getElementById('protected-area').appendChild(protectedComponent);
```

### Hook useAuth

```javascript
// Usar el hook en tu aplicación
const auth = useAuth();

// Verificar estado
if (auth.isAuthenticated) {
    console.log('Usuario actual:', auth.user);
} else {
    console.log('No autenticado');
}

// Login
await auth.login({ username: 'user', password: 'pass' });

// Logout
await auth.logout();
```

## 🔒 Características de Seguridad

### ✅ Cookies Seguras
- **HttpOnly**: No accesibles via JavaScript
- **Secure**: Solo transmitidas por HTTPS (en producción)
- **SameSite=Strict**: Protección contra CSRF
- **Expiración automática**: Access token 15 min, Refresh token 7 días

### ✅ CSRF Protection
- Tokens CSRF generados por sesión
- Verificación automática en mutaciones (POST, PUT, DELETE)
- Exclusión de endpoints seguros

### ✅ Rate Limiting
- 60 solicitudes por minuto por IP (configurable)
- Headers informativos (X-RateLimit-*)
- Exclusión de rutas estáticas

### ✅ Security Headers
- Content Security Policy (CSP)
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- Strict-Transport-Security (HTTPS)

## 🔄 Flujo de Autenticación

1. **Login**: Usuario envía credenciales a `/api/auth/login`
2. **Response**: Server establece cookies (access_token, refresh_token, csrf_token)
3. **Peticiones**: Client incluye cookies automáticamente
4. **CSRF**: Para mutaciones, client incluye X-CSRF-Token header
5. **Refresh**: Si access_token expira, se refresca automáticamente
6. **Logout**: Client llama a `/api/auth/logout` para limpiar cookies

## 🛠️ Endpoints Disponibles

```
POST /api/auth/login        - Iniciar sesión
POST /api/auth/refresh      - Refrescar token de acceso
POST /api/auth/logout       - Cerrar sesión
GET  /api/auth/me          - Obtener usuario actual
GET  /api/auth/csrf-token  - Obtener nuevo CSRF token
```

## 📝 Consideraciones Importantes

### En Producción
- Cambiar `secure=False` a `secure=True` en cookies
- Usar HTTPS obligatoriamente
- Configurar SECRET_KEY robusta
- Considerar Redis para almacenamiento de sesiones/CSRF tokens

### Compatibilidad
- **NO modifica** archivos existentes del backend
- **NO altera** lógica de negocio actual
- **NO interfiere** con sistema de autenticación existente
- Coexiste perfectamente con el sistema actual

### Testing
```bash
# Probar login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"username": "tu_usuario", "password": "tu_password"}'

# Probar ruta protegida
curl -X GET http://localhost:8000/api/auth/me \
  -b cookies.txt
```

## 🚨 Notas de Seguridad

- Las credenciales nunca se almacenan en localStorage
- Los tokens JWT tienen expiración corta (15 min)
- El refresh token tiene expiración larga (7 días)
- Todos los tokens se verifican en cada petición
- Rate limiting previene ataques de fuerza bruta

## 🔄 Mantenimiento

- Monitorear logs de intentos fallidos
- Rotar SECRET_KEY periódicamente
- Actualizar dependencias de seguridad
- Revisar configuración de CORS en producción

---

**Este sistema proporciona autenticación robusta y segura sin afectar la funcionalidad existente de tu aplicación.**
