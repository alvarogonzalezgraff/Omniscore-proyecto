-- CONSULTA CORREGIDA PARA INSERTAR EVENTOS CON ID AUTOINCREMENTAL

-- Primero obtener el próximo ID para cada tabla
SELECT 
    (SELECT COALESCE(MAX(id), 0) + 1 FROM cards) as next_card_id,
    (SELECT COALESCE(MAX(id), 0) + 1 FROM goals) as next_goal_id;

-- Insertar tarjetas amarillas con IDs manuales
INSERT INTO cards (id, match_id, team_id, player_name, minute, card_type)
SELECT 
    (SELECT COALESCE(MAX(id), 0) + ROW_NUMBER() OVER (ORDER BY c.minute) FROM cards) as id,
    m.id,
    CASE 
        WHEN c.player_name IN ('Yoane Wissa') THEN t2.id  -- Nottm Forest
        ELSE t1.id  -- Crystal Palace
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
    AND t1.name = 'Crystal Palace'
    AND t2.name = 'Nottm Forest'
    AND m.matchday = 2;

-- Insertar goles con IDs manuales
INSERT INTO goals (id, match_id, team_id, player_name, minute, assist_player_name, is_own_goal, is_penalty)
SELECT 
    (SELECT COALESCE(MAX(id), 0) + ROW_NUMBER() OVER (ORDER BY g.minute) FROM goals) as id,
    m.id,
    CASE 
        WHEN g.player_name = 'Ethan Pinnock' THEN t1.id  -- Autogol, cuenta para Crystal Palace
        ELSE t2.id  -- Nottm Forest
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
    AND t1.name = 'Crystal Palace'
    AND t2.name = 'Nottm Forest'
    AND m.matchday = 2;

-- Verificar los datos insertados
SELECT 
    'Tarjeta Amarilla' as tipo_evento,
    c.player_name,
    c.minute,
    t.name as equipo
FROM cards c
JOIN matches m ON c.match_id = m.id
JOIN teams t ON c.team_id = t.id
WHERE m.id = (
    SELECT m.id 
    FROM matches m 
    JOIN teams t1 ON m.home_team_id = t1.id 
    JOIN teams t2 ON m.away_team_id = t2.id 
    JOIN leagues l ON m.league_id = l.id 
    WHERE l.name = 'Premier League' 
        AND t1.name = 'Crystal Palace' 
        AND t2.name = 'Nottm Forest' 
        AND m.matchday = 2
)

UNION ALL

SELECT 
    'Gol' as tipo_evento,
    g.player_name,
    g.minute,
    t.name as equipo
FROM goals g
JOIN matches m ON g.match_id = m.id
JOIN teams t ON g.team_id = t.id
WHERE m.id = (
    SELECT m.id 
    FROM matches m 
    JOIN teams t1 ON m.home_team_id = t1.id 
    JOIN teams t2 ON m.away_team_id = t2.id 
    JOIN leagues l ON m.league_id = l.id 
    WHERE l.name = 'Premier League' 
        AND t1.name = 'Crystal Palace' 
        AND t2.name = 'Nottm Forest' 
        AND m.matchday = 2
)
ORDER BY tipo_evento, minute;
