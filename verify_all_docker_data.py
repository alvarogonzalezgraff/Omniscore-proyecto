import psycopg2

# Conexión a Docker PostgreSQL
def get_docker_connection():
    return psycopg2.connect(
        host='localhost',
        port='5433',
        dbname='Omniscore_db',
        user='postgres',
        password='docker_password'
    )

try:
    conn = get_docker_connection()
    cursor = conn.cursor()
    
    # Obtener ID de Premier League
    cursor.execute("SELECT id FROM leagues WHERE name = 'Premier League'")
    premier_result = cursor.fetchone()
    
    if not premier_result:
        print("❌ No se encontró la Premier League en la base de datos Docker")
        exit()
    
    premier_league_id = premier_result[0]
    
    # Obtener estadísticas generales por jornada
    cursor.execute('''
        SELECT m.matchday, COUNT(*) as partidos,
               COUNT(DISTINCT CASE WHEN g.id IS NOT NULL THEN m.id END) as partidos_con_goles,
               COUNT(g.id) as total_goles,
               COUNT(DISTINCT CASE WHEN c.id IS NOT NULL THEN m.id END) as partidos_con_tarjetas,
               COUNT(CASE WHEN c.card_type = 'Amarilla' THEN 1 END) as total_tarjetas_amarillas,
               COUNT(DISTINCT CASE WHEN s.id IS NOT NULL THEN m.id END) as partidos_con_cambios,
               COUNT(s.id) as total_cambios
        FROM matches m
        LEFT JOIN goals g ON m.id = g.match_id
        LEFT JOIN cards c ON m.id = c.match_id
        LEFT JOIN substitutions s ON m.id = s.match_id
        WHERE m.league_id = %s
        GROUP BY m.matchday
        ORDER BY m.matchday
    ''', (premier_league_id,))
    
    jornada_stats = cursor.fetchall()
    
    print(f'=== VERIFICACIÓN COMPLETA PREMIER LEAGUE EN DOCKER ===')
    print()
    
    total_partidos = 0
    total_goles = 0
    total_tarjetas_amarillas = 0
    total_cambios = 0
    partidos_con_goles = 0
    partidos_con_tarjetas = 0
    partidos_con_cambios = 0
    
    for stats in jornada_stats:
        matchday, partidos, p_con_goles, goles, p_con_tarjetas, tarjetas_amarillas, p_con_cambios, cambios = stats
        
        print(f'=== JORNADA {matchday} ===')
        print(f'Partidos: {partidos}')
        print(f'Goles: {goles} ({p_con_goles}/{partidos} partidos con goles)')
        print(f'Tarjetas amarillas: {tarjetas_amarillas} ({p_con_tarjetas}/{partidos} partidos con tarjetas)')
        print(f'Cambios: {cambios} ({p_con_cambios}/{partidos} partidos con cambios)')
        
        if goles > 0:
            # Mostrar detalles de partidos con goles
            cursor.execute('''
                SELECT t1.name as home_team, t2.name as away_team, m.home_score, m.away_score,
                       COUNT(g.id) as goles_partido
                FROM matches m
                JOIN teams t1 ON m.home_team_id = t1.id
                JOIN teams t2 ON m.away_team_id = t2.id
                LEFT JOIN goals g ON m.id = g.match_id
                WHERE m.league_id = %s AND m.matchday = %s
                GROUP BY m.id, t1.name, t2.name, m.home_score, m.away_score
                HAVING COUNT(g.id) > 0
                ORDER BY t1.name
            ''', (premier_league_id, matchday))
            
            partidos_con_goles_detalle = cursor.fetchall()
            print(f'  Partidos con goles:')
            for partido in partidos_con_goles_detalle:
                home_team, away_team, home_score, away_score, goles_partido = partido
                print(f'    🏆 {home_team} vs {away_team} ({home_score}-{away_score}) - {goles_partido} goles')
        
        print()
        
        # Acumular totales
        total_partidos += partidos
        total_goles += goles
        total_tarjetas_amarillas += tarjetas_amarillas
        total_cambios += cambios
        partidos_con_goles += p_con_goles
        partidos_con_tarjetas += p_con_tarjetas
        partidos_con_cambios += p_con_cambios
    
    print(f'=== RESUMEN GENERAL PREMIER LEAGUE EN DOCKER ===')
    print(f'Total partidos: {total_partidos}')
    print(f'Partidos con goles: {partidos_con_goles} ({partidos_con_goles/total_partidos*100:.1f}%)')
    print(f'Partidos con tarjetas amarillas: {partidos_con_tarjetas} ({partidos_con_tarjetas/total_partidos*100:.1f}%)')
    print(f'Partidos con cambios: {partidos_con_cambios} ({partidos_con_cambios/total_partidos*100:.1f}%)')
    print(f'Total goles: {total_goles}')
    print(f'Total tarjetas amarillas: {total_tarjetas_amarillas}')
    print(f'Total cambios: {total_cambios}')
    print()
    
    # Mostrar algunos ejemplos de datos guardados
    print('=== EJEMPLOS DE DATOS GUARDADOS ===')
    
    # Ejemplos de goles
    cursor.execute('''
        SELECT t1.name as home_team, t2.name as away_team, g.player_name, g.minute, g.assist_player_name
        FROM matches m
        JOIN teams t1 ON m.home_team_id = t1.id
        JOIN teams t2 ON m.away_team_id = t2.id
        JOIN goals g ON m.id = g.match_id
        WHERE m.league_id = %s AND g.match_id IN (
            SELECT match_id FROM goals WHERE match_id = m.id LIMIT 1
        )
        ORDER BY g.minute
        LIMIT 5
    ''', (premier_league_id,))
    
    goles_ejemplo = cursor.fetchall()
    print('🥅 Ejemplos de goles:')
    for goal in goles_ejemplo:
        home_team, away_team, player, minute, assist = goal
        assist_str = f' (asist: {assist})' if assist else ''
        print(f'   {player} min {minute} en {home_team} vs {away_team}{assist_str}')
    
    # Ejemplos de tarjetas amarillas
    cursor.execute('''
        SELECT t1.name as home_team, t2.name as away_team, c.player_name, c.minute, c.reason
        FROM matches m
        JOIN teams t1 ON m.home_team_id = t1.id
        JOIN teams t2 ON m.away_team_id = t2.id
        JOIN cards c ON m.id = c.match_id
        WHERE m.league_id = %s AND c.card_type = 'Amarilla'
        ORDER BY c.minute
        LIMIT 5
    ''', (premier_league_id,))
    
    tarjetas_ejemplo = cursor.fetchall()
    print('🟨 Ejemplos de tarjetas amarillas:')
    for card in tarjetas_ejemplo:
        home_team, away_team, player, minute, reason = card
        reason_str = f' - {reason}' if reason else ''
        print(f'   {player} min {minute} en {home_team} vs {away_team}{reason_str}')
    
    # Ejemplos de cambios
    cursor.execute('''
        SELECT t1.name as home_team, t2.name as away_team, s.player_out, s.player_in, s.minute
        FROM matches m
        JOIN teams t1 ON m.home_team_id = t1.id
        JOIN teams t2 ON m.away_team_id = t2.id
        JOIN substitutions s ON m.id = s.match_id
        WHERE m.league_id = %s
        ORDER BY s.minute
        LIMIT 5
    ''', (premier_league_id,))
    
    cambios_ejemplo = cursor.fetchall()
    print('🔄 Ejemplos de cambios:')
    for sub in cambios_ejemplo:
        home_team, away_team, player_out, player_in, minute = sub
        print(f'   {player_out} → {player_in} min {minute} en {home_team} vs {away_team}')
    
    print()
    print('✅ Verificación completada - Datos listos para consultar')
    
    conn.close()
    
except Exception as e:
    print(f'❌ Error: {e}')
