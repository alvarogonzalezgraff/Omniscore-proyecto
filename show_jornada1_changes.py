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
    
    # Obtener partidos de jornada 1
    cursor.execute('''
        SELECT m.id, t1.name as home_team, t2.name as away_team, 
               m.home_score, m.away_score
        FROM matches m
        JOIN teams t1 ON m.home_team_id = t1.id
        JOIN teams t2 ON m.away_team_id = t2.id
        WHERE m.league_id = %s AND m.matchday = 1
        ORDER BY t1.name
    ''', (premier_league_id,))
    
    matches = cursor.fetchall()
    
    print(f'=== CAMBIOS PREMIER LEAGUE - JORNADA 1 ===')
    print(f'Total partidos: {len(matches)}')
    print()
    
    total_substitutions = 0
    
    for match in matches:
        match_id, home_team, away_team, home_score, away_score = match
        print(f'🏆 {home_team} vs {away_team} ({home_score}-{away_score})')
        
        # Obtener cambios del equipo local
        cursor.execute('''
            SELECT s.player_out, s.player_in, s.minute, t.name as team_name
            FROM substitutions s
            JOIN teams t ON s.team_id = t.id
            WHERE s.match_id = %s AND t.name = %s
            ORDER BY s.minute, s.player_out
        ''', (match_id, home_team))
        
        home_subs = cursor.fetchall()
        
        # Obtener cambios del equipo visitante
        cursor.execute('''
            SELECT s.player_out, s.player_in, s.minute, t.name as team_name
            FROM substitutions s
            JOIN teams t ON s.team_id = t.id
            WHERE s.match_id = %s AND t.name = %s
            ORDER BY s.minute, s.player_out
        ''', (match_id, away_team))
        
        away_subs = cursor.fetchall()
        
        # Eliminar duplicados y mostrar cambios únicos
        unique_home_subs = []
        seen_home = set()
        for sub in home_subs:
            key = (sub[0], sub[1], sub[2])  # player_out, player_in, minute
            if key not in seen_home:
                seen_home.add(key)
                unique_home_subs.append(sub)
        
        unique_away_subs = []
        seen_away = set()
        for sub in away_subs:
            key = (sub[0], sub[1], sub[2])  # player_out, player_in, minute
            if key not in seen_away:
                seen_away.add(key)
                unique_away_subs.append(sub)
        
        print(f'  🔄 Cambios {home_team}:')
        if unique_home_subs:
            for sub in unique_home_subs:
                player_out, player_in, minute, team_name = sub
                print(f'     Min {minute}: {player_out} → {player_in}')
        else:
            print('     Sin cambios registrados')
        
        print(f'  🔄 Cambios {away_team}:')
        if unique_away_subs:
            for sub in unique_away_subs:
                player_out, player_in, minute, team_name = sub
                print(f'     Min {minute}: {player_out} → {player_in}')
        else:
            print('     Sin cambios registrados')
        
        match_subs = len(unique_home_subs) + len(unique_away_subs)
        total_substitutions += match_subs
        print(f'  📊 Total cambios partido: {match_subs}')
        print()
    
    print(f'=== RESUMEN JORNADA 1 ===')
    print(f'Total cambios únicos: {total_substitutions}')
    print(f'Promedio cambios por partido: {total_substitutions/len(matches):.1f}')
    
    # Verificar duplicados
    cursor.execute('''
        SELECT COUNT(*) as total, COUNT(DISTINCT CONCAT(player_out, '-', player_in, '-', minute)) as unicos
        FROM substitutions s
        JOIN matches m ON s.match_id = m.id
        WHERE m.league_id = %s AND m.matchday = 1
    ''', (premier_league_id,))
    
    total, unique = cursor.fetchone()
    print(f'Total registros en BD: {total}')
    print(f'Registros únicos: {unique}')
    if total > unique:
        print(f'Duplicados detectados: {total - unique}')
    
    conn.close()
    
except Exception as e:
    print(f'❌ Error: {e}')
