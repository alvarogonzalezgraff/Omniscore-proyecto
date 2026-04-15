# Guía de Migración - JWT a Cookies de Sesión

## 🔄 Cambio Completado: Autenticación con Cookies

Hemos migrado exitosamente el sistema de autenticación de **JWT tokens** a **cookies de sesión** para mayor seguridad y simplicidad.

## 📋 Cambios Realizados

### 🔧 Backend (API)

#### 1. **Nuevo Sistema de Autenticación**
- **Archivo**: `api/cookie_auth.py` - Gestor de cookies de sesión
- **Persistencia**: Sesiones guardadas en `_historial_y_herramientas/cookie_sessions.json`
- **Seguridad**: Session IDs únicos con expiración automática

#### 2. **Endpoints Actualizados**
```python
# Antes (JWT)
POST /api/auth/login -> {"access_token": "...", "token_type": "bearer"}

# Ahora (Cookies)
POST /api/auth/login -> {"message": "Login exitoso", "user": {...}}
POST /api/auth/logout -> {"message": "Logout exitoso"}
GET /api/auth/me -> User data (requiere cookie)
```

#### 3. **SessionMiddleware Configurado**
```python
app.add_middleware(
    SessionMiddleware,
    secret_key="Omniscore_session_secret_key_change_in_production",
    session_cookie="Omniscore_session",
    max_age=1800,  # 30 minutos
    httponly=True,
    samesite="lax"
)
```

### 🎨 Frontend (HTML/JS)

#### 1. **Login Actualizado**
- **Archivo**: `templates/IniciarSesion.html`
- **Cambio**: Usa `credentials: 'include'` en fetch
- **Resultado**: Cookies gestionadas automáticamente por el navegador

#### 2. **Nuevo Helper JS**
- **Archivo**: `assets/js/auth_cookies.js`
- **Funciones**: `logoutWithCookies()`, `checkAuthStatus()`, `authenticatedFetch()`

## 🚀 Uso del Nuevo Sistema

### **Para Desarrolladores**

#### Login (Frontend):
```javascript
const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',  // 🍪 Automáticamente maneja cookies
    body: JSON.stringify({ username, password })
});
```

#### Peticiones Autenticadas:
```javascript
// Sin necesidad de headers Authorization
const data = await fetch('/api/auth/me', {
    credentials: 'include'
});
```

#### Logout:
```javascript
await fetch('/api/auth/logout', {
    method: 'POST',
    credentials: 'include'
});
```

### **Para Usuarios**

#### ✅ **Beneficios**
- **Más seguro**: Cookies HTTP-only, no accesibles desde JavaScript
- **Automático**: El navegador maneja las cookies
- **Persistente**: Sesiones sobreviven reinicios del servidor
- **Simple**: Sin necesidad de gestionar tokens manualmente

#### 🔒 **Características de Seguridad**
- **HttpOnly**: Las cookies no son accesibles desde JavaScript
- **SameSite**: Protección contra CSRF
- **Expiración**: 30 minutos con extensión automática
- **Limpieza**: Sesiones expiradas eliminadas automáticamente

## 📁 Archivos Modificados

### **Nuevos Archivos**
- ✅ `api/cookie_auth.py` - Sistema de cookies
- ✅ `assets/js/auth_cookies.js` - Helpers frontend

### **Modificados**
- ✅ `api/main.py` - Endpoints y middleware
- ✅ `templates/IniciarSesion.html` - Login actualizado
- ✅ `requirements.txt` - Sin cambios (FastAPI ya incluye SessionMiddleware)

### **Mantenidos para Compatibilidad**
- 🔧 `api/auth.py` - Funciones hash y validación
- 🔧 `api/session_manager.py` - Sistema JWT anterior (como backup)

## 🛠️ Configuración

### **Variables de Entorno**
```env
ACCESS_TOKEN_EXPIRE_MINUTES=30  # Ahora usado para cookies también
```

### **Archivo de Sesiones**
- **Ubicación**: `_historial_y_herramientas/cookie_sessions.json`
- **Formato**: JSON con session_id y datos de usuario
- **Limpieza**: Automática al iniciar servidor

## 🔄 Migración desde Sistema Antiguo

### **Si tenías JWT guardados:**
1. Los usuarios deberán iniciar sesión nuevamente
2. El localStorage `authToken` se limpia automáticamente
3. Las sesiones nuevas usan cookies

### **Compatibilidad:**
- El frontend mantiene `currentUser` en localStorage para UI
- Los endpoints protegidos funcionan igual
- No se requiere cambios en otras partes del código

## 🧪 Pruebas y Verificación

### **Probar el Nuevo Sistema:**
```bash
# 1. Iniciar servidor
python run_dev.py --no-reload

# 2. Probar login
curl -X POST "http://localhost:8001/api/auth/login" \
     -H "Content-Type: application/json" \
     -c cookies.txt \
     -d '{"username":"tu_usuario","password":"tu_password"}'

# 3. Probar endpoint protegido
curl -X GET "http://localhost:8001/api/auth/me" \
     -b cookies.txt

# 4. Probar logout
curl -X POST "http://localhost:8001/api/auth/logout" \
     -b cookies.txt \
     -c cookies.txt
```

## 🚨 Consideraciones de Producción

### **Cambios Recomendados:**
1. **Secret Key**: Cambiar `secret_key` en SessionMiddleware
2. **HTTPS**: Configurar `secure=True` en producción
3. **Domain**: Especificar dominio si es necesario
4. **Cleanup**: Implementar limpieza periódica de sesiones

### **Ejemplo Producción:**
```python
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY"),  # Variable de entorno
    session_cookie="Omniscore_session",
    max_age=1800,
    httponly=True,
    samesite="strict",
    secure=True,  # Solo en HTTPS
    domain=".tudominio.com"  # Opcional
)
```

## 🎯 Resumen de Beneficios

✅ **Más Seguro**: Cookies HTTP-only vs tokens en localStorage  
✅ **Más Simple**: Sin gestión manual de tokens  
✅ **Más Persistente**: Sesiones sobreviven reinicios  
✅ **Más Estándar**: Align con prácticas web modernas  
✅ **Más Mantenible**: Código más limpio y legible  

**El sistema está listo para uso inmediato con todas las ventajas de seguridad y persistencia.**
