# API de Ligas de Fútbol ⚽

API RESTful para consultar estadísticas de las principales ligas europeas:
- LaLiga EA Sports
- Liga Hypermotion  
- Bundesliga
- Serie A
- Premier League

## 🚀 Instalación

1. **Instalar dependencias:**
```bash
cd api
pip install -r requirements.txt
```

2. **Migrar datos a la base de datos:**
```bash
python migrate_data.py
```

3. **Iniciar el servidor:**
```bash
python main.py
```

O con uvicorn directamente:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📖 Documentación

Una vez iniciado el servidor, accede a la documentación interactiva:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🔌 Endpoints Principales

### Autenticación
- `POST /api/auth/register` - Registrar nuevo usuario
- `POST /api/auth/login` - Iniciar sesión (obtiene token JWT)
- `GET /api/auth/me` - Obtener información del usuario actual

### Ligas
- `GET /api/leagues` - Listar todas las ligas
- `GET /api/leagues/{league_id}` - Obtener una liga específica

### Equipos
- `GET /api/teams?league_id={id}` - Listar equipos (filtrable por liga)
- `GET /api/teams/{team_id}` - Obtener un equipo específico

### Partidos
- `GET /api/matches?league_id={id}&matchday={num}&team_id={id}` - Listar partidos con filtros
- `GET /api/matches/{match_id}` - Obtener detalles completos de un partido

### Estadísticas
- `GET /api/standings/{league_id}` - Clasificación de una liga
- `GET /api/top-scorers/{league_id}?limit={n}` - Máximos goleadores
- `GET /api/top-assisters/{league_id}?limit={n}` - Máximos asistentes
- `GET /api/player-stats/{player_name}?league_id={id}` - Estadísticas de un jugador

## 🔐 Autenticación

Para endpoints protegidos, incluye el token JWT en las cabeceras:

```
Authorization: Bearer {tu_token_jwt}
```

## 📝 Ejemplos de Uso

### Registrar un usuario
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario",
    "email": "usuario@example.com",
    "password": "contraseña123",
    "full_name": "Nombre Completo"
  }'
```

### Iniciar sesión
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario",
    "password": "contraseña123"
  }'
```

### Obtener clasificación de LaLiga (ID: 1)
```bash
curl http://localhost:8000/api/standings/1
```

### Obtener goleadores de la Premier League (ID: 5)
```bash
curl http://localhost:8000/api/top-scorers/5?limit=10
```

### Obtener partidos de una jornada específica
```bash
curl http://localhost:8000/api/matches?league_id=1&matchday=22
```

## 🔧 Configuración

Edita `config.py` para cambiar:
- Secreto JWT
- Orígenes CORS permitidos
- Tiempo de expiración del token

## 📂 Estructura del Proyecto

```
api/
├── main.py           # Aplicación principal FastAPI
├── models.py         # Modelos Pydantic
├── database.py       # Conexión a BD
├── auth.py           # Sistema de autenticación
├── config.py         # Configuración
├── migrate_data.py   # Script de migración
├── requirements.txt  # Dependencias
└── README.md         # Este archivo
```

## ⚠️ Notas Importantes

1. **Seguridad:** Cambia el `SECRET_KEY` en `config.py` antes de usar en producción
2. **CORS:** Los orígenes están abiertos (`*`), restringe según tu frontend
3. **Base de Datos:** La BD está en `../base de datos/app.db`

## 🐛 Solución de Problemas

### Error de conexión a la BD
Asegúrate de haber ejecutado el script `crear_base_datos.py` primero:
```bash
cd "base de datos"
python crear_base_datos.py
```

### Error de módulos
Reinstala las dependencias:
```bash
pip install -r requirements.txt --upgrade
```
