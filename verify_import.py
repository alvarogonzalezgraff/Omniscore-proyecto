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
    
    print("=== VERIFICANDO DATOS IMPORTADOS ===")
    
    # Verificar partidos
    cursor.execute("""
        SELECT COUNT(*) FROM matches 
        WHERE league_id = 5 AND id >= 1252
    """)
    matches_count = cursor.fetchone()[0]
    print(f"📈 Partidos importados: {matches_count}")
    
    # Verificar goles
    cursor.execute("""
        SELECT COUNT(*) FROM goals g
        JOIN matches m ON g.match_id = m.id
        WHERE m.league_id = 5 AND m.id >= 1252
    """)
    goals_count = cursor.fetchone()[0]
    print(f"⚽ Goles importados: {goals_count}")
    
    # Verificar tarjetas
    cursor.execute("""
        SELECT COUNT(*) FROM cards c
        JOIN matches m ON c.match_id = m.id
        WHERE m.league_id = 5 AND m.id >= 1252
    """)
    cards_count = cursor.fetchone()[0]
    print(f"🟨 Tarjetas importadas: {cards_count}")
    
    # Mostrar algunos ejemplos
    print("\n=== EJEMPLOS DE PARTIDOS IMPORTADOS ===")
    cursor.execute("""
        SELECT m.id, t1.name as home, t2.name as away, m.home_score, m.away_score, m.matchday
        FROM matches m
        JOIN teams t1 ON m.home_team_id = t1.id
        JOIN teams t2 ON m.away_team_id = t2.id
        WHERE m.league_id = 5 AND m.id >= 1252
        ORDER BY m.id
        LIMIT 5
    """)
    
    matches = cursor.fetchall()
    for match in matches:
        print(f"ID {match[0]}: {match[1]} {match[3]} - {match[4]} {match[2]} (J{match[5]})")
    
    print("\n=== EJEMPLOS DE GOLES ===")
    cursor.execute("""
        SELECT g.player_name, g.minute, t.name as team
        FROM goals g
        JOIN matches m ON g.match_id = m.id
        JOIN teams t ON g.team_id = t.id
        WHERE m.league_id = 5 AND m.id >= 1252
        ORDER BY g.minute
        LIMIT 5
    """)
    
    goals = cursor.fetchall()
    for goal in goals:
        print(f"⚽ {goal[0]} (min {goal[1]}) - {goal[2]}")
    
    conn.close()
    print("\n✅ Verificación completada")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
