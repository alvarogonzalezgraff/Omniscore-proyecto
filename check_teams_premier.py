import psycopg2

def get_connection():
    return psycopg2.connect(
        host='localhost',
        port='5433',
        dbname='betwin_db',
        user='postgres',
        password='1234'
    )

try:
    conn = get_connection()
    cursor = conn.cursor()
    
    print("=== EQUIPOS DE PREMIER LEAGUE EN LA BASE DE DATOS ===")
    cursor.execute("""
        SELECT DISTINCT t1.name as home_team, t2.name as away_team, m.matchday
        FROM matches m
        JOIN teams t1 ON m.home_team_id = t1.id
        JOIN teams t2 ON m.away_team_id = t2.id
        JOIN leagues l ON m.league_id = l.id
        WHERE l.name = 'Premier League'
        ORDER BY m.matchday, t1.name
    """)
    
    matches = cursor.fetchall()
    print(f"Total de partidos de Premier League: {len(matches)}")
    
    for match in matches[:20]:  # Mostrar primeros 20
        print(f"J{match[2]}: {match[0]} vs {match[1]}")
    
    print("\n=== BUSCANDO EQUIPOS CON 'Brentford' o 'Crystal' ===")
    cursor.execute("""
        SELECT DISTINCT t.name
        FROM teams t
        JOIN matches m ON (t.id = m.home_team_id OR t.id = m.away_team_id)
        JOIN leagues l ON m.league_id = l.id
        WHERE l.name = 'Premier League'
            AND (t.name ILIKE '%brentford%' OR t.name ILIKE '%crystal%')
        ORDER BY t.name
    """)
    
    teams = cursor.fetchall()
    for team in teams:
        print(f"Equipo encontrado: {team[0]}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
