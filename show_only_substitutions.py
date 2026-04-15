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
            ORDER BY s.minute
        ''', (match_id, home_team))
        
        home_subs = cursor.fetchall()
        
        # Obtener cambios del equipo visitante
        cursor.execute('''
            SELECT s.player_out, s.player_in, s.minute, t.name as team_name
            FROM substitutions s
            JOIN teams t ON s.team_id = t.id
            WHERE s.match_id = %s AND t.name = %s
            ORDER BY s.minute
        ''', (match_id, away_team))
        
        away_subs = cursor.fetchall()
        
        print(f'  🔄 Cambios {home_team}:')
        for sub in home_subs:
            player_out, player_in, minute, team_name = sub
            print(f'     Min {minute}: {player_out} → {player_in}')
        
        print(f'  🔄 Cambios {away_team}:')
        for sub in away_subs:
            player_out, player_in, minute, team_name = sub
            print(f'     Min {minute}: {player_out} → {player_in}')
        
        match_subs = len(home_subs) + len(away_subs)
        total_substitutions += match_subs
        print(f'  📊 Total cambios partido: {match_subs}')
        print()
    
    print(f'=== RESUMEN ===')
    print(f'Total cambios en jornada 1: {total_substitutions}')
    print(f'Promedio cambios por partido: {total_substitutions/len(matches):.1f}')
    
    conn.close()
    
except Exception as e:
    print(f'❌ Error: {e}')
