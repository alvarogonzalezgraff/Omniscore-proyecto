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
    
    print("=== ANÁLISIS DE DATOS DUPLICADOS ===")
    
    # Encontrar todos los partidos con goles duplicados
    cursor.execute('''
        SELECT m.id, t1.name as home_team, t2.name as away_team, 
               m.home_score, m.away_score, COUNT(g.id) as goal_count,
               (m.home_score + m.away_score) as expected_goals
        FROM matches m
        JOIN teams t1 ON m.home_team_id = t1.id
        JOIN teams t2 ON m.away_team_id = t2.id
        LEFT JOIN goals g ON m.id = g.match_id
        WHERE m.league_id = 5
        GROUP BY m.id, t1.name, t2.name, m.home_score, m.away_score
        HAVING COUNT(g.id) > (m.home_score + m.away_score)
        ORDER BY goal_count DESC
    ''')
    
    problematic_matches = cursor.fetchall()
    
    if problematic_matches:
        print(f"⚠️ Se encontraron {len(problematic_matches)} partidos con goles duplicados:")
        
        for match in problematic_matches:
            match_id, home_team, away_team, home_score, away_score, goal_count, expected_goals = match
            print(f"\n🏆 {home_team} vs {away_team}: {home_score}-{away_score}")
            print(f"   Goles esperados: {expected_goals}, Goles registrados: {goal_count}")
            print(f"   Duplicados: {goal_count - expected_goals}")
            
            # Ver detalles de los goles para identificar duplicados
            cursor.execute('''
                SELECT g.id, g.minute, g.player_name, t.name as team_name
                FROM goals g
                JOIN teams t ON g.team_id = t.id
                WHERE g.match_id = %s 
                ORDER BY g.minute, g.id
            ''', (match_id,))
            
            goal_details = cursor.fetchall()
            print(f"   Detalles de goles ({len(goal_details)} registros):")
            
            # Agrupar goles similares para identificar duplicados
            goal_groups = {}
            for goal_id, minute, player, team in goal_details:
                key = (minute, player, team)
                if key not in goal_groups:
                    goal_groups[key] = []
                goal_groups[key].append(goal_id)
            
            duplicate_count = 0
            for (minute, player, team), ids in goal_groups.items():
                if len(ids) > 1:
                    duplicate_count += len(ids) - 1
                    print(f"     DUPLICADO: Min {minute} - {player} ({team}) - IDs: {ids}")
                    # Eliminar duplicados, mantener solo el primero
                    for duplicate_id in ids[1:]:
                        cursor.execute('DELETE FROM goals WHERE id = %s', (duplicate_id,))
                        print(f"       Eliminado goal ID: {duplicate_id}")
                else:
                    print(f"     Min {minute}: {player} ({team}) - ID: {ids[0]}")
            
            print(f"   ✅ Se eliminaron {duplicate_count} goles duplicados")
        
        # Verificar tarjetas duplicadas también
        print(f"\n=== VERIFICANDO TARJETAS DUPLICADAS ===")
        cursor.execute('''
            SELECT m.id, t1.name as home_team, t2.name as away_team, 
                   COUNT(c.id) as card_count
            FROM matches m
            JOIN teams t1 ON m.home_team_id = t1.id
            JOIN teams t2 ON m.away_team_id = t2.id
            LEFT JOIN cards c ON m.id = c.match_id
            WHERE m.league_id = 5 AND m.matchday = 1
            GROUP BY m.id, t1.name, t2.name
            HAVING COUNT(c.id) > 15
            ORDER BY card_count DESC
        ''')
        
        high_card_matches = cursor.fetchall()
        
        if high_card_matches:
            print(f"⚠️ Partidos con muchas tarjetas (posibles duplicados):")
            for match in high_card_matches:
                match_id, home_team, away_team, card_count = match
                print(f"   {home_team} vs {away_team}: {card_count} tarjetas")
        else:
            print("✅ No se encontraron partidos con tarjetas excesivas")
    
    else:
        print("✅ No se encontraron partidos con goles duplicados")
    
    # Confirmar los cambios
    conn.commit()
    
    # Verificación final
    print(f"\n=== VERIFICACIÓN FINAL ===")
    cursor.execute('''
        SELECT COUNT(*) FROM goals
    ''')
    total_goals = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT COUNT(*) FROM cards
    ''')
    total_cards = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT COUNT(*) FROM substitutions
    ''')
    total_subs = cursor.fetchone()[0]
    
    print(f"Total después de limpieza:")
    print(f"- Goles: {total_goals}")
    print(f"- Tarjetas: {total_cards}")
    print(f"- Cambios: {total_subs}")
    
    conn.close()
    print("\n✅ Limpieza completada")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    if 'conn' in locals():
        conn.rollback()
