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
    
    print("=== VERIFICACIÓN DE LESIONES EN PREMIER LEAGUE ===")
    
    # Obtener ID de Premier League
    cursor.execute("SELECT id FROM leagues WHERE name = 'Premier League'")
    premier_result = cursor.fetchone()
    
    if not premier_result:
        print("❌ No se encontró Premier League en la base de datos")
        exit()
    
    premier_league_id = premier_result[0]
    
    # Verificar lesiones por jornada
    cursor.execute('''
        SELECT m.matchday, COUNT(m.id) as matches_count, COUNT(i.id) as injuries_count
        FROM matches m
        LEFT JOIN injuries i ON m.id = i.match_id
        WHERE m.league_id = %s
        GROUP BY m.matchday
        ORDER BY m.matchday
    ''', (premier_league_id,))
    
    jornada_injuries = cursor.fetchall()
    
    print("Lesiones por jornada:")
    total_injuries = 0
    for matchday, matches_count, injuries_count in jornada_injuries:
        print(f"  Jornada {matchday}: {matches_count} partidos, {injuries_count} lesiones")
        total_injuries += injuries_count
    
    print(f"\nTotal lesiones en Premier League: {total_injuries}")
    
    # Verificar partidos específicos con lesiones
    cursor.execute('''
        SELECT m.id, t1.name as home_team, t2.name as away_team, 
               m.matchday, COUNT(i.id) as injury_count
        FROM matches m
        JOIN teams t1 ON m.home_team_id = t1.id
        JOIN teams t2 ON m.away_team_id = t2.id
        LEFT JOIN injuries i ON m.id = i.match_id
        WHERE m.league_id = %s AND i.id IS NOT NULL
        GROUP BY m.id, t1.name, t2.name, m.matchday
        HAVING COUNT(i.id) > 0
        ORDER BY m.matchday, t1.name
    ''', (premier_league_id,))
    
    matches_with_injuries = cursor.fetchall()
    
    if matches_with_injuries:
        print(f"\n📋 Partidos con lesiones ({len(matches_with_injuries)} partidos):")
        for match in matches_with_injuries:
            match_id, home_team, away_team, matchday, injury_count = match
            print(f"  Jornada {matchday}: {home_team} vs {away_team} - {injury_count} lesiones")
            
            # Mostrar detalles de las lesiones
            cursor.execute('''
                SELECT minute, player_name, description
                FROM injuries
                WHERE match_id = %s
                ORDER BY minute
            ''', (match_id,))
            
            injuries = cursor.fetchall()
            for minute, player, description in injuries:
                print(f"    Min {minute}: {player} - {description}")
    else:
        print("\n📋 No se encontraron lesiones registradas en ningún partido")
    
    # Verificar estructura de la tabla injuries
    cursor.execute('''
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'injuries' AND table_schema = 'public'
        ORDER BY ordinal_position
    ''')
    
    columns = cursor.fetchall()
    print(f"\n=== ESTRUCTURA DE LA TABLA INJURIES ===")
    for col in columns:
        print(f"- {col[0]}: {col[1]} (nullable: {col[2]})")
    
    conn.close()
    print("\n✅ Verificación completada")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
