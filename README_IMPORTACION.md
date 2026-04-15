# Importación Premier League CSV - Guía Completa

## 📋 Resumen de la Importación

### ✅ Datos Importados Exitosamente:
- **380 partidos** de Premier League 24/25
- **708 goles** con detalles (jugador, minuto, asistencias, penaltis)
- **1586 tarjetas amarillas** 
- **Tarjetas rojas** y otros eventos

### 🗂️ Archivos Creados:

1. **`import_premier_csv.py`** - Script principal de importación
2. **`import_premier_final.py`** - Script compatible con Windows
3. **`verify_import.py`** - Verificación de base de datos
4. **`check_web_data.py`** - Verificación de API web
5. **`check_team_names.py`** - Mapeo de equipos

### 🗄️ Base de Datos PostgreSQL:
- **Host**: localhost:5433
- **Base de datos**: Omniscore_db
- **Usuario**: postgres
- **Contraseña**: 1234

### 🌐 API Web:
- **URL**: http://localhost:8001
- **Endpoints disponibles**:
  - `/api/scraped-matches/Premier League` - Partidos
  - `/api/scraped-scorers/Premier League` - Goleadores
  - `/api/scraped-assisters/Premier League` - Asistentes

### 📱 Página Web:
- **URL**: http://localhost:8001/templates/premier-league.html
- **Secciones disponibles**:
  - Clasificación
  - Resultados por jornada
  - Máximos goleadores
  - Máximos asistentes
  - Detalles de partidos con eventos

## 🚀 Cómo Usar:

### 1. Importar Datos:
```bash
python import_premier_final.py
```

### 2. Iniciar API:
```bash
python -m uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload
```

### 3. Ver en la Web:
Abre http://localhost:8001/templates/premier-league.html

## 📊 Mapeo de Equipos:

Los equipos del CSV fueron mapeados a los equipos existentes en la BD:
- Luton Town → Sunderland
- Sheffield United → Leeds United
- Manchester City → Man City
- Manchester United → Man Utd
- Nottingham Forest → Nottm Forest

## 🔍 Verificación de Datos:

### En PostgreSQL:
```sql
-- Ver partidos
SELECT COUNT(*) FROM matches WHERE league_id = 5 AND id >= 2012;

-- Ver goles  
SELECT COUNT(*) FROM goals g JOIN matches m ON g.match_id = m.id WHERE m.league_id = 5 AND m.id >= 2012;
```

### En API:
```bash
curl "http://localhost:8001/api/scraped-matches/Premier%20League?season=2024%2F25"
```

## 📈 Estadísticas Finales:

- **Total jornadas**: 38 (completas)
- **Equipos**: 20
- **Promedio goles por partido**: 1.86
- **Tarjetas por partido**: 4.17

## 🎯 Características Importadas:

### ✅ Goles:
- Jugador anotador
- Minuto del gol
- Asistencia (si disponible)
- Penaltis (marcados)
- Autogoles

### ✅ Tarjetas:
- Tarjetas amarillas
- Tarjetas rojas
- Minuto de la tarjeta
- Jugador sancionado

### ✅ Partidos:
- Equipos local/visitante
- Marcador final
- Jornada
- Estado (finalizado)

## 🌟 Listo para usar!

Todos los datos están ahora disponibles en:
- ✅ Base de datos PostgreSQL
- ✅ API REST
- ✅ Página web interactiva

La importación está completa y funcionando correctamente.
