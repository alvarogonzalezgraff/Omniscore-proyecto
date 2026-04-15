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
        print("❌ No se encontró Premier League en la base de datos")
        exit()
    
    premier_league_id = premier_result[0]
    print(f"✅ Premier League ID: {premier_league_id}")
    
    # Verificar todos los partidos de Premier League
    cursor.execute('''
        SELECT m.id, t1.name as home_team, t2.name as away_team, 
               m.home_score, m.away_score, m.matchday, m.match_date
        FROM matches m
        JOIN teams t1 ON m.home_team_id = t1.id
        JOIN teams t2 ON m.away_team_id = t2.id
        WHERE m.league_id = %s
        ORDER BY m.matchday, t1.name
    ''', (premier_league_id,))
    
    matches = cursor.fetchall()
    print(f"\n=== TODOS LOS PARTIDOS PREMIER LEAGUE ===")
    print(f"Total partidos: {len(matches)}")
    
    jornadas = {}
    for match in matches:
        match_id, home_team, away_team, home_score, away_score, matchday, date = match
        if matchday not in jornadas:
            jornadas[matchday] = []
        jornadas[matchday].append({
            'id': match_id,
            'home': home_team,
            'away': away_team,
            'score': f"{home_score}-{away_score}",
            'date': match[6]
        })
    
    for jornada in sorted(jornadas.keys()):
        print(f"\n📅 JORNADA {jornada}:")
        for match in jornadas[jornada]:
            print(f"   {match['home']} vs {match['away']} ({match['score']}) - {match['date']}")
    
    # Análisis detallado de eventos por jornada
    print(f"\n=== ANÁLISIS DETALLADO DE EVENTOS ===")
    
    for jornada in sorted(jornadas.keys()):
        print(f"\n🏆 JORNADA {jornada}:")
        total_goals = 0
        total_cards = 0
        total_subs = 0
        total_injuries = 0
        
        for match in jornadas[jornada]:
            match_id = match['id']
            
            # Contar eventos específicos
            cursor.execute('SELECT COUNT(*) FROM goals WHERE match_id = %s', (match_id,))
            goals = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM cards WHERE match_id = %s", (match_id,))
            cards = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM substitutions WHERE match_id = %s', (match_id,))
            subs = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM injuries WHERE match_id = %s', (match_id,))
            injuries = cursor.fetchone()[0]
            
            total_goals += goals
            total_cards += cards
            total_subs += subs
            total_injuries += injuries
            
            print(f"   {match['home']} vs {match['away']}:")
            print(f"     Goles: {goals}, Tarjetas: {cards}, Cambios: {subs}, Lesiones: {injuries}")
            
            # Verificar detalles de goles si hay demasiados
            if goals > 10:
                cursor.execute('SELECT minute, player_name, team_name FROM goals WHERE match_id = %s LIMIT 5', (match_id,))
                goal_samples = cursor.fetchall()
                print(f"     ⚠️ MUESTRAS DE GOLES ({goals} total):")
                for minute, player, team in goal_samples:
                    print(f"       Min {minute}: {player} ({team})")
        
        print(f"   📊 TOTALES JORNADA {jornada}:")
        print(f"     Goles: {total_goals}, Tarjetas: {total_cards}, Cambios: {total_subs}, Lesiones: {total_injuries}")
    
    # Verificar si hay datos duplicados
    print(f"\n=== VERIFICACIÓN DE DUPLICADOS ===")
    
    # Revisar goles duplicados
    cursor.execute('''
        SELECT match_id, COUNT(*) as count
        FROM goals
        GROUP BY match_id
        HAVING COUNT(*) > 10
        ORDER BY count DESC
        LIMIT 10
    ''')
    
    high_goal_matches = cursor.fetchall()
    if high_goal_matches:
        print("⚠️ PARTIDOS CON MUCHOS GOLES (posibles duplicados):")
        for match_id, count in high_goal_matches:
            cursor.execute('''
                SELECT t1.name, t2.name 
                FROM matches m
                JOIN teams t1 ON m.home_team_id = t1.id
                JOIN teams t2 ON m.away_team_id = t2.id
                WHERE m.id = %s
            ''', (match_id,))
            teams = cursor.fetchone()
            print(f"   {teams[0]} vs {teams[1]}: {count} goles")
    
    conn.close()
    print("\n✅ Diagnóstico completado")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
