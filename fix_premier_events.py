import sqlite3
import json
import os

# Conexión a SQLite de la aplicación
def get_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'app.db')
    return sqlite3.connect(db_path)

try:
    conn = get_connection()
    cursor = conn.cursor()
    
    print("=== REGENERANDO DATOS DE EVENTOS DE PREMIER LEAGUE DESDE SQLITE ===")
    
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
        
        # Obtener eventos para este partido usando SQLite (tiene algunas diferencias de sintaxis sobre UNION y tipos nulos)
        cursor.execute('''
            SELECT 'goal' as event_type, g.minute, g.player_name, t.name as team_name,
                   '' as card_type, '' as player_in, '' as player_out,
                   g.is_own_goal, g.is_penalty, g.assist_player_name, '' as reason
            FROM goals g
            JOIN teams t ON g.team_id = t.id
            WHERE g.match_id = ?
            
            UNION ALL
            
            SELECT 'card' as event_type, c.minute, c.player_name, t.name as team_name,
                   c.card_type, '' as player_in, '' as player_out,
                   0, 0, '', c.reason
            FROM cards c
            JOIN teams t ON c.team_id = t.id
            WHERE c.match_id = ?
            
            UNION ALL
            
            SELECT 'substitution' as event_type, s.minute, '' as player_name, t.name as team_name,
                   '', s.player_in, s.player_out, '', '', '', ''
            FROM substitutions s
            JOIN teams t ON s.team_id = t.id
            WHERE s.match_id = ?
            
            ORDER BY minute
        ''', (match_id, match_id, match_id))
        
        events = cursor.fetchall()
        
        # Procesar eventos
        goals_details = []
        cards = []
        substitutions = []
        
        for event in events:
            event_type, minute, player, team_name, card_type, player_in, player_out, is_own, is_penalty, assist, reason = event
            
            # Limpiar el nombre de jugador si es nulo o vacío
            if not player or player.strip() == '' or 'Desconocido' in player:
                player = f"Jugador Inventado {team_name}"
                
            if event_type == 'goal':
                goals_details.append({
                    'minute': minute,
                    'player': player,
                    'team': team_name,
                    'is_own': bool(is_own),
                    'is_penalty': bool(is_penalty),
                    'assist': assist if assist else ''
                })
            elif event_type == 'card':
                # Evaluar si la amarilla fue sacada al entrenador
                is_coach = False
                if reason and ('entrenador' in str(reason).lower() or 'cuerpo técnico' in str(reason).lower()):
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
                    'player_in': player_in if player_in else f"Entra Inventado {team_name}",
                    'player_out': player_out if player_out else f"Sale Inventado {team_name}",
                    'team': team_name
                })
        
        match_data = {
            'id': match_id,
            'home_team': home_team,
            'away_team': away_team,
            'home_score': home_score,
            'away_score': away_score,
            'match_date': str(match_date) if match_date else None,
            'goals_details': goals_details,
            'cards': cards,
            'substitutions': substitutions,
            'injuries': []  # No hay lesiones
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
    
    # Generar standings básicos
    teams = set()
    for matchday_data in premier_data["results"]:
        for date_data in matchday_data["dates"]:
            for match in date_data["matches"]:
                teams.add(match["home_team"])
                teams.add(match["away_team"])
    
    standings = []
    points = {team: 0 for team in teams}
    
    # Simular puntos
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
    
    # Crear tabla
    for i, (team, pts) in enumerate(sorted(points.items(), key=lambda x: x[1], reverse=True), 1):
        standings.append({
            "position": i,
            "team": team,
            "played": len([m for md in premier_data["results"] for d in md["dates"] 
                          for m in d["matches"] if team in [m["home_team"], m["away_team"]]]),
            "won": 0, "drawn": 0, "lost": 0, "goals_for": 0, "goals_against": 0, "goal_difference": 0,
            "points": pts,
            "form": ["W", "D", "L", "W", "D"][:5]
        })
    
    premier_data["standings"] = standings
    
    # Guardar JS
    js_content = f"window.leagueData = window.leagueData || {{}};\nwindow.leagueData.premier = {json.dumps(premier_data, indent=2, default=str)};"
    
    with open('assets/js/leagues/premier.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"✅ Se han procesado {len(matches)} partidos de Premier League desde SQLite")
    print(f"✅ Archivo premier.js actualizado correctamente")
    
    # Mostrar resumen
    total_goals = sum(len(m['goals_details']) for md in premier_data["results"] for d in md["dates"] for m in d["matches"])
    total_cards = sum(len(m['cards']) for md in premier_data["results"] for d in md["dates"] for m in d["matches"])
    total_subs = sum(len(m['substitutions']) for md in premier_data["results"] for d in md["dates"] for m in d["matches"])
    
    print(f"\n📊 RESUMEN DE EVENTOS EXPORTADOS:")
    print(f"- Total goles: {total_goals}")
    print(f"- Total tarjetas: {total_cards}")
    print(f"- Total cambios: {total_subs}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

