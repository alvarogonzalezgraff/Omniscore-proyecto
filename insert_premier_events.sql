-- CONSULTA CORRECTA PARA INSERTAR EVENTOS DEL PARTIDO BRENTFORD VS CRYSTAL PALACE
-- Adaptada a la estructura de tablas existente en tu base de datos

-- Primero verificar si el partido existe y obtener su ID
SELECT m.id, m.matchday, t1.name as home_team, t2.name as away_team
FROM matches m
JOIN teams t1 ON m.home_team_id = t1.id
JOIN teams t2 ON m.away_team_id = t2.id
JOIN leagues l ON m.league_id = l.id
WHERE l.name = 'Premier League'
    AND t1.name = 'Brentford'
    AND t2.name = 'Crystal Palace'
    AND m.matchday = 1;

-- Insertar tarjetas amarillas en la tabla 'cards'
INSERT INTO cards (match_id, team_id, player_name, minute, card_type)
SELECT 
    m.id,
    CASE 
        WHEN c.player_name IN ('Yoane Wissa') THEN t1.id
        ELSE t2.id
    END as team_id,
    c.player_name,
    c.minute,
    'yellow' as card_type
FROM matches m
JOIN teams t1 ON m.home_team_id = t1.id
JOIN teams t2 ON m.away_team_id = t2.id
JOIN leagues l ON m.league_id = l.id
CROSS JOIN (VALUES 
    ('Yoane Wissa', 20),
    ('Joachim Andersen', 22),
    ('Marc Guehi', 46),
    ('Chris Richards', 58),
    ('Daichi Kamada', 65),
    ('Jordan Ayew', 91)
) c(player_name, minute)
WHERE l.name = 'Premier League'
    AND t1.name = 'Brentford'
    AND t2.name = 'Crystal Palace'
    AND m.matchday = 1;

-- Insertar goles en la tabla 'goals'
INSERT INTO goals (match_id, team_id, player_name, minute, assist_player_name, is_own_goal, is_penalty)
SELECT 
    m.id,
    CASE 
        WHEN g.player_name = 'Ethan Pinnock' THEN t2.id  -- Autogol, cuenta para Crystal Palace
        ELSE t1.id
    END as team_id,
    g.player_name,
    g.minute,
    g.assist_player_name,
    g.is_own_goal,
    g.is_penalty
FROM matches m
JOIN teams t1 ON m.home_team_id = t1.id
JOIN teams t2 ON m.away_team_id = t2.id
JOIN leagues l ON m.league_id = l.id
CROSS JOIN (VALUES 
    ('Bryan Mbeumo', 29, 'Yoane Wissa', false, false),
    ('Ethan Pinnock', 57, NULL, true, false),  -- Autogol
    ('Yoane Wissa', 76, NULL, false, false)
) g(player_name, minute, assist_player_name, is_own_goal, is_penalty)
WHERE l.name = 'Premier League'
    AND t1.name = 'Brentford'
    AND t2.name = 'Crystal Palace'
    AND m.matchday = 1;

-- Verificar los datos insertados
SELECT 
    'Tarjetas Amarillas' as tipo_evento,
    c.player_name,
    c.minute,
    t.name as equipo
FROM cards c
JOIN matches m ON c.match_id = m.id
JOIN teams t ON c.team_id = t.id
WHERE m.id = (SELECT m.id FROM matches m JOIN teams t1 ON m.home_team_id = t1.id JOIN teams t2 ON m.away_team_id = t2.id JOIN leagues l ON m.league_id = l.id WHERE l.name = 'Premier League' AND t1.name = 'Brentford' AND t2.name = 'Crystal Palace' AND m.matchday = 1)

UNION ALL

SELECT 
    'Goles' as tipo_evento,
    g.player_name,
    g.minute,
    t.name as equipo
FROM goals g
JOIN matches m ON g.match_id = m.id
JOIN teams t ON g.team_id = t.id
WHERE m.id = (SELECT m.id FROM matches m JOIN teams t1 ON m.home_team_id = t1.id JOIN teams t2 ON m.away_team_id = t2.id JOIN leagues l ON m.league_id = l.id WHERE l.name = 'Premier League' AND t1.name = 'Brentford' AND t2.name = 'Crystal Palace' AND m.matchday = 1)
ORDER BY tipo_evento, minute;
