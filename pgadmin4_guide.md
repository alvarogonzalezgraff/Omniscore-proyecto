# Guía para Ver Goles de Premier League en pgAdmin4

## Configuración de Conexión
1. **Servidor**: localhost
2. **Puerto**: 5433
3. **Base de datos**: Omniscore_db
4. **Usuario**: postgres
5. **Contraseña**: 1234

## Pasos para Acceder a los Datos de Goles

### 1. Conectarse a la Base de Datos
- Abre pgAdmin4
- Crea una nueva conexión o usa la existente con los datos arriba
- Navega a `Omniscore_db` > `Schemas` > `public`

### 2. Abrir Editor SQL
- Haz clic derecho en `Omniscore_db`
- Selecciona `Query Tool`
- Esto abrirá un editor SQL donde puedes pegar las consultas

### 3. Consultas Principales para Ver Goles

#### Opción A: Ver Todos los Goles de Premier League
```sql
SELECT 
    t1.name as home_team,
    t2.name as away_team,
    m.home_score,
    m.away_score,
    m.matchday,
    g.minute,
    g.player_name,
    g.assist_player_name,
    CASE WHEN g.is_penalty THEN 'Sí' ELSE 'No' END as penalty,
    CASE WHEN g.is_own_goal THEN 'Sí' ELSE 'No' END as own_goal,
    t.name as scoring_team
FROM matches m
JOIN teams t1 ON m.home_team_id = t1.id
JOIN teams t2 ON m.away_team_id = t2.id
JOIN leagues l ON m.league_id = l.id
LEFT JOIN goals g ON m.id = g.match_id
LEFT JOIN teams t ON g.team_id = t.id
WHERE l.name = 'Premier League'
    AND g.player_name IS NOT NULL
ORDER BY m.matchday, g.minute;
```

#### Opción B: Ver por Jornada Específica
```sql
SELECT 
    m.matchday,
    t1.name as home_team,
    t2.name as away_team,
    m.home_score,
    m.away_score,
    STRING_AGG(
        g.minute || '''': '' || g.player_name || 
        CASE WHEN g.assist_player_name IS NOT NULL THEN ' (' || g.assist_player_name || ')' ELSE '' END,
        ', ' ORDER BY g.minute
    ) as goals
FROM matches m
JOIN teams t1 ON m.home_team_id = t1.id
JOIN teams t2 ON m.away_team_id = t2.id
JOIN leagues l ON m.league_id = l.id
LEFT JOIN goals g ON m.id = g.match_id
WHERE l.name = 'Premier League'
    AND m.matchday = 1  -- Cambia este número para otras jornadas
GROUP BY m.matchday, t1.name, t2.name, m.home_score, m.away_score, m.id
ORDER BY m.matchday;
```

### 4. Navegación en pgAdmin4
- Los resultados aparecerán en la parte inferior del editor
- Puedes exportar resultados a CSV usando el botón de descarga
- Las tablas principales son:
  - `matches` - partidos
  - `goals` - detalles de goles (¡IMPORTANTE: no es goals_details!)
  - `teams` - equipos
  - `leagues` - ligas

### 5. Para Ver Todos los Datos Disponibles
Usa el archivo `premier_league_goals_correct.sql` que contiene todas las consultas necesarias.

## Estructura de Datos
- **matches**: información básica de partidos
- **goals**: detalles específicos de cada gol (¡esta es la tabla correcta!)
- **teams**: información de equipos
- **leagues**: información de ligas (Premier League ID: 5)

## Datos Disponibles
- Total de partidos de Premier League: 150
- Total de goles registrados: 52
- Premier League ID: 5
