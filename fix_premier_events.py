import psycopg2
import json

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
    
    print("=== CORRIGIENDO DATOS DE EVENTOS DE PREMIER LEAGUE ===")
    
    # Obtener todos los partidos de Premier League con sus eventos
    cursor.execute('''
        SELECT 
            m.id,
            m.matchday,
            t1.name as home_team,
            t2.name as away_team,
            m.home_score,
            m.away_score,
            m.match_date
        FROM matches m
        JOIN teams t1 ON m.home_team_id = t1.id
        JOIN teams t2 ON m.away_team_id = t2.id
        WHERE m.league_id = 5
        ORDER BY m.matchday, t1.name
    ''')
    
    matches = cursor.fetchall()
    
    premier_data = {
        "name": "Premier League",
        "standings": [],
        "results": []
    }
    
    # Agrupar partidos por jornada
    jornadas = {}
    for match in matches:
        match_id, matchday, home_team, away_team, home_score, away_score, match_date = match
        if matchday not in jornadas:
            jornadas[matchday] = []
        
        # Obtener eventos para este partido
        cursor.execute('''
            SELECT 'goal' as event_type, g.minute, g.player_name, t.name as team_name,
                   NULL as card_type, NULL as player_in, NULL as player_out,
                   g.is_own_goal, g.is_penalty, g.assist_player_name, NULL as reason
            FROM goals g
            JOIN teams t ON g.team_id = t.id
            WHERE g.match_id = %s
            
            UNION ALL
            
            SELECT 'card' as event_type, c.minute, c.player_name, t.name as team_name,
                   c.card_type, NULL as player_in, NULL as player_out,
                   NULL, NULL, NULL, c.reason
            FROM cards c
            JOIN teams t ON c.team_id = t.id
            WHERE c.match_id = %s
            
            UNION ALL
            
            SELECT 'substitution' as event_type, s.minute, s.player_out, t.name as team_name,
                   NULL, s.player_in, s.player_out, NULL, NULL, NULL, NULL
            FROM substitutions s
            JOIN teams t ON s.team_id = t.id
            WHERE s.match_id = %s
            
            ORDER BY minute
        ''', (match_id, match_id, match_id))
        
        events = cursor.fetchall()
        
        # Procesar eventos
        goals_details = []
        cards = []
        substitutions = []
        
        for event in events:
            event_type, minute, player, team_name, card_type, player_in, player_out, is_own, is_penalty, assist, reason = event
            
            if event_type == 'goal':
                goals_details.append({
                    'minute': minute,
                    'player': player,
                    'team': team_name,
                    'is_own': is_own,
                    'is_penalty': is_penalty,
                    'assist': assist if assist else ''
                })
            elif event_type == 'card':
                # Evaluar si la amarilla fue sacada al entrenador
                is_coach = False
                if reason and ('entrenador' in reason.lower() or 'cuerpo técnico' in reason.lower()):
                    is_coach = True
                
                cards.append({
                    'minute': minute,
                    'player': player,
                    'team': team_name,
                    'type': card_type,
                    'reason': reason if reason else '',
                    'is_coach': is_coach
                })
            elif event_type == 'substitution':
                substitutions.append({
                    'minute': minute,
                    'player_in': player_in,
                    'player_out': player_out,
                    'team': team_name
                })
        
        match_data = {
            'id': match_id,
            'home_team': home_team,
            'away_team': away_team,
            'home_score': home_score,
            'away_score': away_score,
            'match_date': match_date.strftime('%Y-%m-%d') if match_date else None,
            'goals_details': goals_details,
            'cards': cards,
            'substitutions': substitutions,
            'injuries': []  # No hay lesiones en la base de datos
        }
        
        jornadas[matchday].append(match_data)
    
    # Convertir al formato esperado
    for matchday in sorted(jornadas.keys()):
        premier_data["results"].append({
            "matchweek": matchday,
            "dates": [{
                "date": jornadas[matchday][0]["match_date"] if jornadas[matchday] else "2025-01-01",
                "matches": jornadas[matchday]
            }]
        })
    
    # Generar standings básicos (ordenados por puntos simulados)
    teams = set()
    for matchday_data in premier_data["results"]:
        for date_data in matchday_data["dates"]:
            for match in date_data["matches"]:
                teams.add(match["home_team"])
                teams.add(match["away_team"])
    
    standings = []
    points = {team: 0 for team in teams}
    
    # Simular puntos basados en resultados
    for matchday_data in premier_data["results"]:
        for date_data in matchday_data["dates"]:
            for match in date_data["matches"]:
                home = match["home_team"]
                away = match["away_team"]
                home_score = match["home_score"]
                away_score = match["away_score"]
                
                if home_score > away_score:
                    points[home] += 3
                elif away_score > home_score:
                    points[away] += 3
                else:
                    points[home] += 1
                    points[away] += 1
    
    # Crear tabla de posiciones
    for i, (team, pts) in enumerate(sorted(points.items(), key=lambda x: x[1], reverse=True), 1):
        standings.append({
            "position": i,
            "team": team,
            "played": len([m for md in premier_data["results"] for d in md["dates"] 
                          for m in d["matches"] if team in [m["home_team"], m["away_team"]]]),
            "won": 0,  # Simplificado
            "drawn": 0,  # Simplificado
            "lost": 0,  # Simplificado
            "goals_for": 0,  # Simplificado
            "goals_against": 0,  # Simplificado
            "goal_difference": 0,  # Simplificado
            "points": pts,
            "form": ["W", "D", "L", "W", "D"][:5]  # Simplificado
        })
    
    premier_data["standings"] = standings
    
    # Guardar el archivo JavaScript corregido
    js_content = f"window.leagueData = window.leagueData || {{}};\nwindow.leagueData.premier = {json.dumps(premier_data, indent=2, default=str)};"
    
    with open('c:/Users/pc/Desktop/proyecto/assets/js/leagues/premier.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"✅ Se han corregido {len(matches)} partidos de Premier League")
    print(f"✅ Archivo premier.js actualizado con datos correctos de eventos")
    
    # Mostrar resumen
    total_goals = sum(len(m['goals_details']) for md in premier_data["results"] for d in md["dates"] for m in d["matches"])
    total_cards = sum(len(m['cards']) for md in premier_data["results"] for d in md["dates"] for m in d["matches"])
    total_subs = sum(len(m['substitutions']) for md in premier_data["results"] for d in md["dates"] for m in d["matches"])
    
    print(f"\n📊 RESUMEN DE EVENTOS:")
    print(f"- Total goles: {total_goals}")
    print(f"- Total tarjetas: {total_cards}")
    print(f"- Total cambios: {total_subs}")
    
    conn.close()
    print("\n✅ Corrección completada")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    if 'conn' in locals():
        conn.rollback()
