-- CONSULTA SIMPLE PARA INSERTAR EVENTOS USANDO IDs CORRECTOS

-- Obtener IDs base
SELECT 
    (SELECT COALESCE(MAX(id), 0) FROM cards) as max_card_id,
    (SELECT COALESCE(MAX(id), 0) FROM goals) as max_goal_id;

-- Insertar tarjetas amarillas una por una con IDs incrementales
INSERT INTO cards (id, match_id, team_id, player_name, minute, card_type) VALUES 
    (38165, 564, (SELECT id FROM teams WHERE name = 'Nottm Forest'), 'Yoane Wissa', 20, 'yellow'),
    (38166, 564, (SELECT id FROM teams WHERE name = 'Crystal Palace'), 'Joachim Andersen', 22, 'yellow'),
    (38167, 564, (SELECT id FROM teams WHERE name = 'Crystal Palace'), 'Marc Guehi', 46, 'yellow'),
    (38168, 564, (SELECT id FROM teams WHERE name = 'Crystal Palace'), 'Chris Richards', 58, 'yellow'),
    (38169, 564, (SELECT id FROM teams WHERE name = 'Crystal Palace'), 'Daichi Kamada', 65, 'yellow'),
    (38170, 564, (SELECT id FROM teams WHERE name = 'Crystal Palace'), 'Jordan Ayew', 91, 'yellow');

-- Insertar goles una por una con IDs incrementales
INSERT INTO goals (id, match_id, team_id, player_name, minute, assist_player_name, is_own_goal, is_penalty) VALUES 
    (31143, 564, (SELECT id FROM teams WHERE name = 'Nottm Forest'), 'Bryan Mbeumo', 29, 'Yoane Wissa', false, false),
    (31144, 564, (SELECT id FROM teams WHERE name = 'Crystal Palace'), 'Ethan Pinnock', 57, NULL, true, false),
    (31145, 564, (SELECT id FROM teams WHERE name = 'Nottm Forest'), 'Yoane Wissa', 76, NULL, false, false);

-- Verificar todos los eventos del partido
SELECT 
    CASE 
        WHEN c.player_name IS NOT NULL THEN 'Tarjeta Amarilla'
        WHEN g.player_name IS NOT NULL THEN 'Gol'
    END as tipo_evento,
    COALESCE(c.player_name, g.player_name) as player_name,
    COALESCE(c.minute, g.minute) as minute,
    COALESCE(t.name, t2.name) as equipo
FROM matches m
LEFT JOIN cards c ON m.id = c.match_id
LEFT JOIN goals g ON m.id = g.match_id
LEFT JOIN teams t ON c.team_id = t.id
LEFT JOIN teams t2 ON g.team_id = t2.id
WHERE m.id = 564
    AND (c.player_name IS NOT NULL OR g.player_name IS NOT NULL)
ORDER BY COALESCE(c.minute, g.minute);
