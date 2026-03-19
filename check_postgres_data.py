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
    
    print("=== VERIFICANDO LIGAS DISPONIBLES ===")
    cursor.execute("SELECT id, name FROM leagues ORDER BY id")
    leagues = cursor.fetchall()
    for league in leagues:
        print(f"ID: {league[0]}, Nombre: {league[1]}")
    
    print("\n=== VERIFICANDO TABLAS DISPONIBLES ===")
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """)
    tables = cursor.fetchall()
    for table in tables:
        print(f"- {table[0]}")
    
    print("\n=== VERIFICANDO SI EXISTE goals_details ===")
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'goals_details'
        )
    """)
    exists = cursor.fetchone()[0]
    print(f"Tabla goals_details existe: {exists}")
    
    if exists:
        cursor.execute("SELECT COUNT(*) FROM goals_details")
        count = cursor.fetchone()[0]
        print(f"Total de registros en goals_details: {count}")
    
    print("\n=== VERIFICANDO PARTIDOS TOTALES ===")
    cursor.execute("SELECT COUNT(*) FROM matches")
    total_matches = cursor.fetchone()[0]
    print(f"Total de partidos en matches: {total_matches}")
    
    print("\n=== VERIFICANDO PARTIDOS POR LIGA ===")
    cursor.execute("""
        SELECT l.name, COUNT(m.id) as match_count
        FROM leagues l
        LEFT JOIN matches m ON l.id = m.league_id
        GROUP BY l.id, l.name
        ORDER BY match_count DESC
    """)
    matches_by_league = cursor.fetchall()
    for league_name, count in matches_by_league:
        print(f"{league_name}: {count} partidos")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
