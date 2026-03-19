-- CONSULTA PARA VER GOLES DE PREMIER LEAGUE EN PGADMIN4
-- Copia y pega esta consulta en el editor SQL de pgAdmin4

-- 1. VER ESTRUCTURA COMPLETA DE TABLAS RELACIONADAS CON GOLES
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name IN ('matches', 'goals_details', 'events', 'teams', 'leagues')
    AND table_schema = 'public'
ORDER BY table_name, ordinal_position;

-- 2. VER TODOS LOS GOLES DE PREMIER LEAGUE
SELECT 
    m.id as match_id,
    t1.name as home_team,
    t2.name as away_team,
    m.home_score,
    m.away_score,
    m.matchday,
    m.match_date,
    gd.minute,
    gd.player_name,
    gd.assisted_by,
    gd.is_penalty,
    gd.is_own_goal
FROM matches m
JOIN teams t1 ON m.home_team_id = t1.id
JOIN teams t2 ON m.away_team_id = t2.id
JOIN leagues l ON m.league_id = l.id
LEFT JOIN goals_details gd ON m.id = gd.match_id
WHERE l.name = 'Premier League'
    AND gd.player_name IS NOT NULL
ORDER BY m.matchday, m.id, gd.minute;

-- 3. RESUMEN DE GOLES POR EQUIPO Y JORNADA
SELECT 
    m.matchday,
    t1.name as home_team,
    t2.name as away_team,
    m.home_score,
    m.away_score,
    COUNT(gd.id) as total_goals_registered,
    STRING_AGG(
        CASE 
            WHEN gd.player_name IS NOT NULL THEN 
                gd.minute || '''': '' || gd.player_name || 
                CASE WHEN gd.assisted_by IS NOT NULL THEN ' (Assist: ' || gd.assisted_by || ')' ELSE '' END ||
                CASE WHEN gd.is_penalty THEN ' [PEN]' ELSE '' END ||
                CASE WHEN gd.is_own_goal THEN ' [OG]' ELSE '' END
            ELSE NULL 
        END, ', ' ORDER BY gd.minute
    ) as goals_details
FROM matches m
JOIN teams t1 ON m.home_team_id = t1.id
JOIN teams t2 ON m.away_team_id = t2.id
JOIN leagues l ON m.league_id = l.id
LEFT JOIN goals_details gd ON m.id = gd.match_id
WHERE l.name = 'Premier League'
GROUP BY m.matchday, t1.name, t2.name, m.home_score, m.away_score, m.id
ORDER BY m.matchday, t1.name;

-- 4. ESTADÍSTICAS DE GOLES POR JORNADA
SELECT 
    m.matchday,
    COUNT(*) as matches,
    SUM(m.home_score + m.away_score) as total_match_goals,
    COUNT(gd.id) as registered_goals,
    COUNT(DISTINCT gd.player_name) as unique_scorers
FROM matches m
JOIN leagues l ON m.league_id = l.id
LEFT JOIN goals_details gd ON m.id = gd.match_id
WHERE l.name = 'Premier League'
GROUP BY m.matchday
ORDER BY m.matchday;

-- 5. VER GOLES DE UNA JORNADA ESPECÍFICA (ejemplo: Jornada 1)
SELECT 
    m.id as match_id,
    t1.name as home_team,
    t2.name as away_team,
    m.home_score,
    m.away_score,
    gd.minute,
    gd.player_name as scorer,
    gd.assisted_by,
    CASE WHEN gd.is_penalty THEN 'Sí' ELSE 'No' END as is_penalty,
    CASE WHEN gd.is_own_goal THEN 'Sí' ELSE 'No' END as is_own_goal
FROM matches m
JOIN teams t1 ON m.home_team_id = t1.id
JOIN teams t2 ON m.away_team_id = t2.id
JOIN leagues l ON m.league_id = l.id
LEFT JOIN goals_details gd ON m.id = gd.match_id
WHERE l.name = 'Premier League'
    AND m.matchday = 1
    AND gd.player_name IS NOT NULL
ORDER BY m.id, gd.minute;
