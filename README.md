# Omniscore - Aplicación de Apuestas Deportivas

Aplicación web para consultar estadísticas de ligas de fútbol europeas.

## 🚀 Instalación

1. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

## ▶️ Cómo ejecutar la aplicación

Simplemente ejecuta el script `run.py` desde la raíz del proyecto:

```bash
python run.py
```

O alternativamente:

```bash
python3 run.py
```

## 🌐 Acceso a la aplicación

Una vez iniciado el servidor, podrás acceder a:

- **Página de inicio**: http://localhost:8000/
- **Documentación API**: http://localhost:8000/docs
- **Información API**: http://localhost:8000/api

### Páginas disponibles:

- `/` o `/inicio` - Página principal
- `/deportes` - Listado de deportes
- `/login` - Iniciar sesión
- `/registro` - Registro de usuario
- `/premier-league` - Estadísticas Premier League
- `/serie-a` - Estadísticas Serie A
- `/bundesliga` - Estadísticas Bundesliga
- `/laliga` - Estadísticas LaLiga EA Sports
- `/liga-hypermotion` - Estadísticas Liga Hypermotion
- `/api-demo` - Demo de la API

## 📁 Estructura del proyecto

```
proyecto segundo año/
├── run.py                 # Script principal para iniciar la aplicación
├── requirements.txt       # Dependencias del proyecto
├── templates/             # Archivos HTML de la aplicación
│   ├── inicio.html
│   ├── deportes.html
│   ├── IniciarSesion.html
│   ├── registro.html
│   ├── premier-league.html
│   ├── serie-a.html
│   ├── bundesliga.html
│   ├── laliga.html
│   ├── liga-hypermotion.html
│   └── api_demo.html
├── api/                   # Backend FastAPI
│   ├── main.py           # Aplicación principal
│   ├── models.py         # Modelos de datos
│   ├── database.py       # Conexión a BD
│   ├── auth.py           # Autenticación
│   ├── config.py         # Configuración
│   └── requirements.txt  # Dependencias (copia)
├── assets/               # Archivos estáticos CSS/JS
├── images/               # Imágenes
└── database/             # Base de datos SQLite
    └── app.db
```

## 🔧 Desarrollo

El servidor se ejecuta con auto-reload activado, por lo que cualquier cambio en el código se reflejará automáticamente sin necesidad de reiniciar el servidor.

## 🛑 Detener el servidor

Presiona `Ctrl+C` en la terminal donde se está ejecutando el servidor.
