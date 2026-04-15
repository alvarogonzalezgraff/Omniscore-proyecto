import psycopg2

def get_connection():
    return psycopg2.connect(
        host='localhost',
        port='5433',
        dbname='Omniscore_db',
        user='postgres',
        password='1234'
    )

try:
    conn = get_connection()
    cursor = conn.cursor()
    
    print("=== ESTRUCTURA DE LA TABLA GOALS ===")
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'goals' AND table_schema = 'public'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    for col in columns:
        print(f"- {col[0]}: {col[1]} (nullable: {col[2]})")
    
    print("\n=== VERIFICANDO GOLES DE PREMIER LEAGUE ===")
    cursor.execute("""
        SELECT COUNT(*) 
        FROM goals g
        JOIN matches m ON g.match_id = m.id
        JOIN leagues l ON m.league_id = l.id
        WHERE l.name = 'Premier League'
    """)
    count = cursor.fetchone()[0]
    print(f"Total de goles de Premier League: {count}")
    
    if count > 0:
        print("\n=== PRIMEROS 10 GOLES DE PREMIER LEAGUE ===")
        cursor.execute("""
            SELECT 
                g.id,
                t1.name as home_team,
                t2.name as away_team,
                m.matchday,
                g.minute,
                g.player_name,
                g.team_id,
                t.name as scoring_team
            FROM goals g
            JOIN matches m ON g.match_id = m.id
            JOIN teams t1 ON m.home_team_id = t1.id
            JOIN teams t2 ON m.away_team_id = t2.id
            JOIN leagues l ON m.league_id = l.id
            LEFT JOIN teams t ON g.team_id = t.id
            WHERE l.name = 'Premier League'
            ORDER BY m.matchday, g.minute
            LIMIT 10
        """)
        
        goals = cursor.fetchall()
        for goal in goals:
            print(f"ID: {goal[0]}, {goal[1]} vs {goal[2]} (J{goal[3]}), "
                  f"Min: {goal[4]}, Jugador: {goal[5]}, Equipo: {goal[7]}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
