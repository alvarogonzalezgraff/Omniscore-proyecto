-- MOSTRAR SOLO LOS EVENTOS NUEVOS INSERTADOS

-- Tarjetas amarillas nuevas (IDs 38165-38170)
SELECT 
    'Tarjeta Amarilla' as tipo_evento,
    c.player_name,
    c.minute,
    t.name as equipo
FROM cards c
JOIN teams t ON c.team_id = t.id
WHERE c.id BETWEEN 38165 AND 38170
ORDER BY c.minute;

-- Goles nuevos (IDs 31143-31145)
SELECT 
    'Gol' as tipo_evento,
    g.player_name,
    g.minute,
    t.name as equipo,
    g.assist_player_name as asistente,
    CASE WHEN g.is_own_goal THEN 'Sí' ELSE 'No' END as autogol,
    CASE WHEN g.is_penalty THEN 'Sí' ELSE 'No' END as penalty
FROM goals g
JOIN teams t ON g.team_id = t.id
WHERE g.id BETWEEN 31143 AND 31145
ORDER BY g.minute;
