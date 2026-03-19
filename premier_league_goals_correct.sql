-- CONSULTA CORRECTA PARA VER GOLES DE PREMIER LEAGUE EN PGADMIN4
-- La tabla correcta es 'goals', no 'goals_details'

-- 1. VER TODOS LOS GOLES DE PREMIER LEAGUE
SELECT 
    m.id as match_id,
    t1.name as home_team,
    t2.name as away_team,
    m.home_score,
    m.away_score,
    m.matchday,
    m.match_date,
    g.minute,
    g.player_name,
    g.assist_player_name,
    CASE WHEN g.is_penalty THEN 'Sí' ELSE 'No' END as is_penalty,
    CASE WHEN g.is_own_goal THEN 'Sí' ELSE 'No' END as is_own_goal,
    t.name as scoring_team
FROM matches m
JOIN teams t1 ON m.home_team_id = t1.id
JOIN teams t2 ON m.away_team_id = t2.id
JOIN leagues l ON m.league_id = l.id
LEFT JOIN goals g ON m.id = g.match_id
LEFT JOIN teams t ON g.team_id = t.id
WHERE l.name = 'Premier League'
    AND g.player_name IS NOT NULL
ORDER BY m.matchday, m.id, g.minute;

-- 2. VER GOLES POR JORNADA ESPECÍFICA (ejemplo: Jornada 1)
SELECT 
    m.matchday,
    t1.name as home_team,
    t2.name as away_team,
    m.home_score,
    m.away_score,
    STRING_AGG(
        g.minute || '''': '' || g.player_name || 
        CASE WHEN g.assist_player_name IS NOT NULL THEN ' (' || g.assist_player_name || ')' ELSE '' END ||
        CASE WHEN g.is_penalty THEN ' [PEN]' ELSE '' END ||
        CASE WHEN g.is_own_goal THEN ' [OG]' ELSE '' END,
        ', ' ORDER BY g.minute
    ) as goals_details
FROM matches m
JOIN teams t1 ON m.home_team_id = t1.id
JOIN teams t2 ON m.away_team_id = t2.id
JOIN leagues l ON m.league_id = l.id
LEFT JOIN goals g ON m.id = g.match_id
WHERE l.name = 'Premier League'
    AND m.matchday = 1  -- Cambia este número para otras jornadas
GROUP BY m.matchday, t1.name, t2.name, m.home_score, m.away_score, m.id
ORDER BY m.matchday;

-- 3. ESTADÍSTICAS DE GOLES POR JORNADA
SELECT 
    m.matchday,
    COUNT(*) as matches,
    SUM(m.home_score + m.away_score) as total_match_goals,
    COUNT(g.id) as registered_goals,
    COUNT(DISTINCT g.player_name) as unique_scorers
FROM matches m
JOIN leagues l ON m.league_id = l.id
LEFT JOIN goals g ON m.id = g.match_id
WHERE l.name = 'Premier League'
GROUP BY m.matchday
ORDER BY m.matchday;

-- 4. MÁXIMOS GOLEADORES DE PREMIER LEAGUE
SELECT 
    g.player_name,
    t.name as team,
    COUNT(*) as goals,
    STRING_AGG(DISTINCT m.matchday::text, ', ' ORDER BY m.matchday) as matchdays
FROM goals g
JOIN matches m ON g.match_id = m.id
JOIN leagues l ON m.league_id = l.id
LEFT JOIN teams t ON g.team_id = t.id
WHERE l.name = 'Premier League'
    AND NOT g.is_own_goal
GROUP BY g.player_name, t.name
ORDER BY goals DESC, player_name
LIMIT 20;

-- 5. VER GOLES DE UN EQUIPO ESPECÍFICO (ejemplo: Liverpool)
SELECT 
    m.matchday,
    t1.name as home_team,
    t2.name as away_team,
    m.home_score,
    m.away_score,
    g.minute,
    g.player_name,
    g.assist_player_name,
    CASE WHEN g.is_penalty THEN 'Sí' ELSE 'No' END as is_penalty,
    CASE WHEN g.is_own_goal THEN 'Sí' ELSE 'No' END as is_own_goal
FROM matches m
JOIN teams t1 ON m.home_team_id = t1.id
JOIN teams t2 ON m.away_team_id = t2.id
JOIN leagues l ON m.league_id = l.id
JOIN goals g ON m.id = g.match_id
JOIN teams t ON g.team_id = t.id
WHERE l.name = 'Premier League'
    AND t.name = 'Liverpool'
ORDER BY m.matchday, g.minute;
