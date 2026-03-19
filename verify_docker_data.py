import psycopg2

# Conexión a Docker PostgreSQL
def get_docker_connection():
    return psycopg2.connect(
        host='localhost',
        port='5433',
        dbname='betwin_db',
        user='postgres',
        password='docker_password'
    )

try:
    conn = get_docker_connection()
    cursor = conn.cursor()
    
    # Verificar tablas y datos
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = cursor.fetchall()
    print("=== TABLAS EN DOCKER POSTGRESQL ===")
    for table in tables:
        print(f"- {table[0]}")
    print()
    
    # Verificar datos de Premier League Jornada 1
    cursor.execute("SELECT id FROM leagues WHERE name = 'Premier League'")
    premier_result = cursor.fetchone()
    
    if premier_result:
        premier_league_id = premier_result[0]
        
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
        print(f"=== PARTIDOS PREMIER LEAGUE JORNADA 1 EN DOCKER ===")
        print(f"Total partidos: {len(matches)}")
        print()
        
        for match in matches:
            match_id, home_team, away_team, home_score, away_score = match
            print(f"🏆 {home_team} vs {away_team} ({home_score}-{away_score})")
            
            # Contar goles
            cursor.execute('SELECT COUNT(*) FROM goals WHERE match_id = %s', (match_id,))
            goals_count = cursor.fetchone()[0]
            
            # Contar tarjetas amarillas
            cursor.execute("SELECT COUNT(*) FROM cards WHERE match_id = %s AND card_type = 'Amarilla'", (match_id,))
            yellow_cards_count = cursor.fetchone()[0]
            
            # Contar cambios
            cursor.execute('SELECT COUNT(*) FROM substitutions WHERE match_id = %s', (match_id,))
            subs_count = cursor.fetchone()[0]
            
            print(f"   Goles: {goals_count}, Tarjetas amarillas: {yellow_cards_count}, Cambios: {subs_count}")
            print()
    
    # Estadísticas generales
    cursor.execute('SELECT COUNT(*) FROM goals')
    total_goals = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM cards WHERE card_type = 'Amarilla'")
    total_yellow_cards = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM substitutions')
    total_substitutions = cursor.fetchone()[0]
    
    print("=== ESTADÍSTICAS GENERALES EN DOCKER ===")
    print(f"Total goles: {total_goals}")
    print(f"Total tarjetas amarillas: {total_yellow_cards}")
    print(f"Total cambios: {total_substitutions}")
    
    conn.close()
    print("\n✅ Verificación completada")
    
except Exception as e:
    print(f"❌ Error: {e}")
