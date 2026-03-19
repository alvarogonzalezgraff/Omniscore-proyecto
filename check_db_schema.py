import psycopg2

# Conexión a Docker PostgreSQL
def get_docker_connection():
    return psycopg2.connect(
        host='localhost',
        port='5433',
        dbname='betwin_db',
        user='postgres',
        password='1234'
    )

try:
    conn = get_docker_connection()
    cursor = conn.cursor()
    
    # Verificar estructura de la tabla matches
    cursor.execute('''
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'matches' AND table_schema = 'public'
        ORDER BY ordinal_position
    ''')
    
    columns = cursor.fetchall()
    print("=== ESTRUCTURA DE LA TABLA MATCHES ===")
    for col in columns:
        print(f"- {col[0]}: {col[1]} (nullable: {col[2]})")
    
    print("\n=== VERIFICANDO DATOS DE PREMIER LEAGUE ===")
    
    # Obtener ID de Premier League
    cursor.execute("SELECT id FROM leagues WHERE name = 'Premier League'")
    premier_result = cursor.fetchone()
    
    if premier_result:
        premier_league_id = premier_result[0]
        print(f"✅ Premier League ID: {premier_league_id}")
        
        # Verificar partidos sin la columna date
        cursor.execute('''
            SELECT m.id, t1.name as home_team, t2.name as away_team, 
                   m.home_score, m.away_score, m.matchday
            FROM matches m
            JOIN teams t1 ON m.home_team_id = t1.id
            JOIN teams t2 ON m.away_team_id = t2.id
            WHERE m.league_id = %s
            ORDER BY m.matchday, t1.name
            LIMIT 5
        ''', (premier_league_id,))
        
        matches = cursor.fetchall()
        print(f"\nPrimeros 5 partidos de Premier League:")
        for match in matches:
            match_id, home_team, away_team, home_score, away_score, matchday = match
            print(f"   ID: {match_id}, {home_team} vs {away_team} ({home_score}-{away_score}), Jornada: {matchday}")
    
    conn.close()
    print("\n✅ Verificación completada")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
