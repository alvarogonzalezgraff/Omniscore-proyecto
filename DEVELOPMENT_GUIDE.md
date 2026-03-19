# Guía de Desarrollo - BetWin

## Gestión de Sesiones y Reinicios del Servidor

### 🚀 Problema Resuelto
Al hacer cambios en el backend, el servidor se reinicia (`reload=True`) y las sesiones de usuario se cerraban. Ahora tienes persistencia de sesiones.

### 🛠️ Soluciones Implementadas

#### 1. **Sistema de Persistencia de Sesiones**
- **SessionManager**: Guarda sesiones activas en archivo JSON
- **Recuperación automática**: Al reiniciar, recupera sesiones no expiradas
- **Limpieza automática**: Elimina sesiones expiradas

#### 2. **Modos de Desarrollo**
- **Con recarga**: Ideal para desarrollo frontend (las sesiones persisten)
- **Sin recarga**: Ideal para desarrollo backend (sin interrupciones)

### 📋 Comandos de Uso

#### Opción A: Script Interactivo (Recomendado)
```bash
# Windows
start_dev.bat

# Se mostrará menú con opciones:
# 1. Desarrollo con recarga automática
# 2. Desarrollo sin recarga (mantiene sesiones)
# 3. Producción
```

#### Opción B: Comandos Directos
```bash
# Desarrollo normal (con recarga, sesiones persistentes)
python run_dev.py

# Desarrollo sin recarga (sin interrupciones)
python run_dev.py --no-reload

# Puerto personalizado
python run_dev.py --port 8080 --no-reload
```

#### Opción C: Método Original (Modificado)
```bash
# Ahora tiene persistencia de sesiones incorporada
python run.py
```

### 🔄 Flujo de Trabajo Recomendado

#### Para Desarrollo Frontend:
1. Usa: `start_dev.bat` → Opción 1
2. Modifica HTML/CSS/JS libremente
3. Las sesiones se mantienen gracias al SessionManager

#### Para Desarrollo Backend:
1. Usa: `start_dev.bat` → Opción 2  
2. Modifica Python sin interrupciones
3. Reinicia manualmente cuando necesites cambios

#### Para Desarrollo Mixto:
1. Usa: `start_dev.bat` → Opción 1
2. El SessionManager mantiene tus sesiones
3. Recarga automática para cambios rápidos

### 🔧 Configuración de Sesiones

#### Archivo de Sesiones
- **Ubicación**: `_historial_y_herramientas/active_sessions.json`
- **Formato**: JSON con tokens, usuarios y fechas de expiración
- **Limpieza**: Automática al iniciar y cada acceso

#### Tiempos de Sesión
- **Duración**: 30 minutos (configurable en `.env`)
- **Extensión**: Automática al usar la API
- **Expiración**: Limpieza automática

### 🛡️ Seguridad

#### Tokens JWT
- **Validación doble**: JWT + SessionManager
- **Recuperación**: Si JWT falla, busca en sesiones persistentes
- **Extensión**: Renueva automáticamente la sesión

#### Mejoras de Seguridad
- Las sesiones expiran automáticamente
- Limpieza de sesiones inválidas
- Persistencia solo en desarrollo (configurable)

### 📁 Archivos Modificados

#### Nuevos Archivos:
- `api/session_manager.py` - Gestor de sesiones persistente
- `run_dev.py` - Script de desarrollo mejorado
- `start_dev.bat` - Interfaz de desarrollo fácil

#### Modificados:
- `api/auth.py` - Integración con SessionManager
- `api/main.py` - Login con persistencia

### 🚨 Buenas Prácticas

#### 1. **Entorno de Desarrollo**
```bash
# Activa el entorno virtual
venv\Scripts\activate

# Instala dependencias si es necesario
pip install -r requirements.txt
```

#### 2. **Variables de Entorno**
```env
# .env
ACCESS_TOKEN_EXPIRE_MINUTES=30  # Duración de sesión
SECRET_KEY=tu_clave_única_segura
```

#### 3. **Limpieza Regular**
```bash
# Limpiar caché y archivos temporales
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
```

#### 4. **Backups de Sesiones**
- El sistema mantiene backup automático de sesiones
- No necesitas manualmente guardar tokens

### 🔍 Solución de Problemas

#### Sesión no persiste:
1. Verifica que `_historial_y_herramientas/active_sessions.json` exista
2. Revisa permisos de escritura del directorio
3. Limpia el archivo y vuelve a iniciar sesión

#### Error al cargar sesiones:
1. Elimina `active_sessions.json`
2. Reinicia el servidor
3. Vuelve a iniciar sesión

#### Token inválido después de reinicio:
1. El SessionManager debería recuperarlo automáticamente
2. Si no funciona, limpia sesiones y vuelve a login

### 🎯 Resumen

✅ **Sesiones persistentes** través de reinicios  
✅ **Desarrollo flexible** con/sin recarga  
✅ **Seguridad mantenida** con expiración automática  
✅ **Fácil uso** con scripts interactivos  
✅ **Buenas prácticas** incorporadas  

Ahora puedes desarrollar sin preocuparte por perder tu sesión al modificar el backend.
