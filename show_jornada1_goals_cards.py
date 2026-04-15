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
        print("❌ No se encontró la Premier League en la base de datos Docker")
        exit()
    
    premier_league_id = premier_result[0]
    
    # Obtener partidos de jornada 1
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
    
    print(f'=== GOLES Y TARJETAS PREMIER LEAGUE - JORNADA 1 ===')
    print(f'Total partidos: {len(matches)}')
    print()
    
    total_goals = 0
    total_yellow_cards = 0
    total_red_cards = 0
    
    for match in matches:
        match_id, home_team, away_team, home_score, away_score = match
        print(f'🏆 {home_team} vs {away_team} ({home_score}-{away_score})')
        
        # Obtener goles
        cursor.execute('''
            SELECT g.player_name, g.minute, g.assist_player_name, g.is_own_goal, g.is_penalty, t.name as team_name
            FROM goals g
            JOIN teams t ON g.team_id = t.id
            WHERE g.match_id = %s
            ORDER BY g.minute
        ''', (match_id,))
        
        goals_data = cursor.fetchall()
        unique_goals = []
        seen_goals = set()
        
        for goal in goals_data:
            key = (goal[0], goal[1], goal[4])  # player_name, minute, is_penalty
            if key not in seen_goals:
                seen_goals.add(key)
                unique_goals.append(goal)
        
        if unique_goals:
            print(f'  ⚽ GOLES ({len(unique_goals)}):')
            for goal in unique_goals:
                player_name, minute, assist_player_name, is_own_goal, is_penalty, team_name = goal
                goal_type = ""
                if is_own_goal:
                    goal_type = " (en propia puerta)"
                elif is_penalty:
                    goal_type = " (penalti)"
                
                assist_str = f" - Asist: {assist_player_name}" if assist_player_name else ""
                print(f'     Min {minute}: {player_name} ({team_name}){goal_type}{assist_str}')
            total_goals += len(unique_goals)
        else:
            print(f'  ❌ Sin goles')
        
        # Obtener tarjetas amarillas
        cursor.execute('''
            SELECT c.player_name, c.minute, c.reason, t.name as team_name
            FROM cards c
            JOIN teams t ON c.team_id = t.id
            WHERE c.match_id = %s AND c.card_type = 'Amarilla'
            ORDER BY c.minute
        ''', (match_id,))
        
        yellow_cards_data = cursor.fetchall()
        unique_yellow_cards = []
        seen_yellow = set()
        
        for card in yellow_cards_data:
            key = (card[0], card[1])  # player_name, minute
            if key not in seen_yellow:
                seen_yellow.add(key)
                unique_yellow_cards.append(card)
        
        if unique_yellow_cards:
            print(f'  🟨 TARJETAS AMARILLAS ({len(unique_yellow_cards)}):')
            for card in unique_yellow_cards:
                player_name, minute, reason, team_name = card
                reason_str = f" - {reason}" if reason else ""
                print(f'     Min {minute}: {player_name} ({team_name}){reason_str}')
            total_yellow_cards += len(unique_yellow_cards)
        else:
            print(f'  ❌ Sin tarjetas amarillas')
        
        # Obtener tarjetas rojas
        cursor.execute('''
            SELECT c.player_name, c.minute, c.reason, t.name as team_name
            FROM cards c
            JOIN teams t ON c.team_id = t.id
            WHERE c.match_id = %s AND c.card_type = 'Roja'
            ORDER BY c.minute
        ''', (match_id,))
        
        red_cards_data = cursor.fetchall()
        unique_red_cards = []
        seen_red = set()
        
        for card in red_cards_data:
            key = (card[0], card[1])  # player_name, minute
            if key not in seen_red:
                seen_red.add(key)
                unique_red_cards.append(card)
        
        if unique_red_cards:
            print(f'  🟥 TARJETAS ROJAS ({len(unique_red_cards)}):')
            for card in unique_red_cards:
                player_name, minute, reason, team_name = card
                reason_str = f" - {reason}" if reason else ""
                print(f'     Min {minute}: {player_name} ({team_name}){reason_str}')
            total_red_cards += len(unique_red_cards)
        
        print()
    
    print(f'=== RESUMEN JORNADA 1 ===')
    print(f'Total goles: {total_goals}')
    print(f'Total tarjetas amarillas: {total_yellow_cards}')
    print(f'Total tarjetas rojas: {total_red_cards}')
    
    # Verificar duplicados
    cursor.execute('''
        SELECT 
            COUNT(*) as total_goals,
            COUNT(DISTINCT CONCAT(player_name, '-', minute)) as unique_goals
        FROM goals g
        JOIN matches m ON g.match_id = m.id
        WHERE m.league_id = %s AND m.matchday = 1
    ''', (premier_league_id,))
    
    total_goals_db, unique_goals_db = cursor.fetchone()
    print(f'Goles en BD: {total_goals_db} (únicos: {unique_goals_db})')
    
    cursor.execute('''
        SELECT 
            COUNT(*) as total_cards,
            COUNT(DISTINCT CONCAT(player_name, '-', minute)) as unique_cards
        FROM cards c
        JOIN matches m ON c.match_id = m.id
        WHERE m.league_id = %s AND m.matchday = 1 AND c.card_type = 'Amarilla'
    ''', (premier_league_id,))
    
    total_cards_db, unique_cards_db = cursor.fetchone()
    print(f'Tarjetas amarillas en BD: {total_cards_db} (únicas: {unique_cards_db})')
    
    conn.close()
    
except Exception as e:
    print(f'❌ Error: {e}')
