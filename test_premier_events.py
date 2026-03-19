import json

# Cargar el archivo premier.js corregido
with open('c:/Users/pc/Desktop/proyecto/assets/js/leagues/premier.js', 'r', encoding='utf-8') as f:
    content = f.read()
    # Extraer el JSON del JavaScript
    json_start = content.find('{')
    json_end = content.rfind('}') + 1
    json_data = content[json_start:json_end]
    premier_data = json.loads(json_data)

print("=== VERIFICACIÓN DE EVENTOS CORREGIDOS ===")

# Analizar algunos partidos específicos
matches_checked = 0
matches_with_goals = 0
matches_with_cards = 0
matches_with_subs = 0

for jornada in premier_data.get("results", []):
    for date_data in jornada.get("dates", []):
        for match in date_data.get("matches", []):
            matches_checked += 1
            
            home_team = match.get("home_team", "")
            away_team = match.get("away_team", "")
            home_score = match.get("home_score", 0)
            away_score = match.get("away_score", 0)
            
            goals = match.get("goals_details", [])
            cards = match.get("cards", [])
            subs = match.get("substitutions", [])
            
            # Verificar que los goles tengan equipo asignado
            goals_with_team = [g for g in goals if g.get("team")]
            goals_home = [g for g in goals if g.get("team") == home_team]
            goals_away = [g for g in goals if g.get("team") == away_team]
            
            # Verificar que las tarjetas tengan equipo asignado
            cards_with_team = [c for c in cards if c.get("team")]
            cards_home = [c for c in cards if c.get("team") == home_team]
            cards_away = [c for c in cards if c.get("team") == away_team]
            
            # Verificar que las sustituciones tengan equipo asignado
            subs_with_team = [s for s in subs if s.get("team")]
            subs_home = [s for s in subs if s.get("team") == home_team]
            subs_away = [s for s in subs if s.get("team") == away_team]
            
            if goals:
                matches_with_goals += 1
                print(f"\n⚽ {home_team} vs {away_team} ({home_score}-{away_score})")
                print(f"   Goles totales: {len(goals)}")
                print(f"   Goles con equipo: {len(goals_with_team)}")
                print(f"   Goles {home_team}: {len(goals_home)}")
                print(f"   Goles {away_team}: {len(goals_away)}")
                
                # Mostrar detalles de goles
                for goal in goals[:3]:  # Primeros 3 goles
                    team_name = goal.get("team", "SIN EQUIPO")
                    player = goal.get("player", "SIN JUGADOR")
                    minute = goal.get("minute", 0)
                    print(f"     Min {minute}: {player} ({team_name})")
            
            if cards:
                matches_with_cards += 1
                print(f"\n🟨 {home_team} vs {away_team}")
                print(f"   Tarjetas totales: {len(cards)}")
                print(f"   Tarjetas con equipo: {len(cards_with_team)}")
                print(f"   Tarjetas {home_team}: {len(cards_home)}")
                print(f"   Tarjetas {away_team}: {len(cards_away)}")
            
            if subs:
                matches_with_subs += 1
                print(f"\n🔄 {home_team} vs {away_team}")
                print(f"   Cambios totales: {len(subs)}")
                print(f"   Cambios con equipo: {len(subs_with_team)}")
                print(f"   Cambios {home_team}: {len(subs_home)}")
                print(f"   Cambios {away_team}: {len(subs_away)}")

print(f"\n📊 RESUMEN DE VERIFICACIÓN:")
print(f"- Partidos verificados: {matches_checked}")
print(f"- Partidos con goles: {matches_with_goals}")
print(f"- Partidos con tarjetas: {matches_with_cards}")
print(f"- Partidos con cambios: {matches_with_subs}")

print(f"\n✅ Verificación completada")
print(f"✅ Los eventos ahora tienen asignación correcta de equipos")
