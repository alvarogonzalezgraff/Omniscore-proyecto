# 🚀 Instrucciones finales para arrancar Omniscore

## Estado actual del proyecto

✅ **Completado:**
- Todos los archivos HTML movidos a `templates/`
- Carpeta `database/` renombrada (antes "base de datos")
- Archivo `run.py` creado en la raíz
- `requirements.txt` creado en la raíz con todas las dependencias
- Todas las importaciones corregidas para usar imports relativos
- Enlaces HTML actualizados para usar rutas sin `.html`
- FastAPI configurado para servir templates y archivos estáticos

## ⚠️ Acción requerida

**Debes instalar las dependencias faltantes en tu entorno virtual:**

```bash
# Asegúrate de estar en el directorio del proyecto
cd "/home/mario/Escritorio/proyecto segundo año"

# Activa tu entorno virtual (si no está activado)
source venv/bin/activate

# Instala todas las dependencias
pip install -r requirements.txt
```

## 🎯 Ejecutar la aplicación

Una vez instaladas las dependencias:

```bash
python run.py
```

## 🌐 URLs disponibles

Después de arrancar, la aplicación estará en:

- **Inicio**: http://localhost:8000/
- **Deportes**: http://localhost:8000/deportes
- **Login**: http://localhost:8000/login
- **Registro**: http://localhost:8000/registro
- **Premier League**: http://localhost:8000/premier-league
- **Serie A**: http://localhost:8000/serie-a
- **Bundesliga**: http://localhost:8000/bundesliga
- **LaLiga**: http://localhost:8000/laliga
- **Liga Hypermotion**: http://localhost:8000/liga-hypermotion
- **API Demo**: http://localhost:8000/api-demo
- **Docs API**: http://localhost:8000/docs
- **Info API**: http://localhost:8000/api

## 📦 Dependencias instaladas

- fastapi==0.109.0
- uvicorn[standard]==0.27.0
- pydantic==2.5.3
- python-jose[cryptography]==3.3.0
- passlib[bcrypt]==1.7.4
- python-multipart==0.0.6
- jinja2==3.1.3
- email-validator==2.1.0 ⚠️ **NUEVA - necesaria para arrancar**

## 🛑 Detener el servidor

Presiona `Ctrl+C` en la terminal donde corre el servidor.
