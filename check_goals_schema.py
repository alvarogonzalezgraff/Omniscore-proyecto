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
    
    # Verificar estructura de la tabla goals
    cursor.execute('''
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'goals' AND table_schema = 'public'
        ORDER BY ordinal_position
    ''')
    
    columns = cursor.fetchall()
    print("=== ESTRUCTURA DE LA TABLA GOALS ===")
    for col in columns:
        print(f"- {col[0]}: {col[1]} (nullable: {col[2]})")
    
    print("\n=== VERIFICANDO GOLES DUPLICADOS ===")
    
    # Verificar goles en partidos específicos con números altos
    cursor.execute('''
        SELECT m.id, t1.name as home_team, t2.name as away_team, 
               m.home_score, m.away_score, COUNT(g.id) as goal_count
        FROM matches m
        JOIN teams t1 ON m.home_team_id = t1.id
        JOIN teams t2 ON m.away_team_id = t2.id
        LEFT JOIN goals g ON m.id = g.match_id
        WHERE m.league_id = 5 AND m.matchday = 1
        GROUP BY m.id, t1.name, t2.name, m.home_score, m.away_score
        HAVING COUNT(g.id) > (m.home_score + m.away_score)
        ORDER BY goal_count DESC
    ''')
    
    problematic_matches = cursor.fetchall()
    
    if problematic_matches:
        print("⚠️ PARTIDOS CON MÁS GOLES REGISTRADOS QUE EL MARCADOR:")
        for match in problematic_matches:
            match_id, home_team, away_team, home_score, away_score, goal_count = match
            expected_goals = home_score + away_score
            print(f"   {home_team} vs {away_team}: {home_score}-{away_score} (esperado: {expected_goals}, registrado: {goal_count})")
            
            # Ver detalles de estos goles
            cursor.execute('''
                SELECT minute, player_name, home_team, away_team
                FROM goals 
                WHERE match_id = %s 
                ORDER BY minute
                LIMIT 10
            ''', (match_id,))
            
            goal_details = cursor.fetchall()
            print(f"     Primeros 10 goles:")
            for i, goal in enumerate(goal_details, 1):
                minute, player, home_team, away_team = goal
                print(f"       {i}. Min {minute}: {player} ({home_team} vs {away_team})")
            print()
    else:
        print("✅ No se encontraron partidos con goles excedentes")
    
    conn.close()
    print("\n✅ Verificación completada")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
