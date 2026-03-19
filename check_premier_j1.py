import sqlite3
import json

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Get all Premier League matches from jornada 1
cursor.execute('''
    SELECT home_team, away_team, home_score, away_score, 
           goals_details, cards, substitutions, injuries
    FROM matches 
    WHERE league = 'Premier League' AND matchday = 'Jornada 1'
    ORDER BY home_team
''')

matches = cursor.fetchall()
print(f'=== PREMIER LEAGUE - JORNADA 1 ===')
print(f'Total partidos encontrados: {len(matches)}')
print()

total_matches = len(matches)
matches_with_goals = 0
matches_with_yellow_cards = 0
matches_with_substitutions = 0

for match in matches:
    home_team, away_team, home_score, away_score, goals_details, cards, substitutions, injuries = match
    print(f'🏆 {home_team} vs {away_team} ({home_score}-{away_score})')
    
    # Check goals
    has_goals = False
    if goals_details and goals_details.strip():
        try:
            goals = json.loads(goals_details) if isinstance(goals_details, str) else goals_details
            if goals and len(goals) > 0:
                has_goals = True
                matches_with_goals += 1
                print(f'  ✅ Goles: {len(goals)} eventos')
                for goal in goals[:3]:  # Show first 3
                    print(f'     - Min {goal.get("minute", "N/A")}: {goal.get("player", "N/A")}')
                if len(goals) > 3:
                    print(f'     ... y {len(goals) - 3} más')
            else:
                print(f'  ❌ Sin datos de goles')
        except:
            print(f'  ❌ Error al procesar datos de goles')
    else:
        print(f'  ❌ Sin datos de goles')
    
    # Check cards
    has_yellow_cards = False
    if cards and cards.strip():
        try:
            card_data = json.loads(cards) if isinstance(cards, str) else cards
            yellow_cards = [c for c in card_data if c.get('type') == 'yellow card']
            if yellow_cards and len(yellow_cards) > 0:
                has_yellow_cards = True
                matches_with_yellow_cards += 1
                print(f'  ✅ Tarjetas amarillas: {len(yellow_cards)}')
                for card in yellow_cards[:2]:
                    print(f'     - Min {card.get("minute", "N/A")}: {card.get("player", "N/A")}')
                if len(yellow_cards) > 2:
                    print(f'     ... y {len(yellow_cards) - 2} más')
            else:
                print(f'  ❌ Sin tarjetas amarillas')
        except:
            print(f'  ❌ Error al procesar datos de tarjetas')
    else:
        print(f'  ❌ Sin datos de tarjetas')
    
    # Check substitutions
    has_substitutions = False
    if substitutions and substitutions.strip():
        try:
            sub_data = json.loads(substitutions) if isinstance(substitutions, str) else substitutions
            if sub_data and len(sub_data) > 0:
                has_substitutions = True
                matches_with_substitutions += 1
                print(f'  ✅ Cambios: {len(sub_data)}')
                for sub in sub_data[:2]:
                    print(f'     - Min {sub.get("minute", "N/A")}: {sub.get("player_out", "N/A")} → {sub.get("player_in", "N/A")}')
                if len(sub_data) > 2:
                    print(f'     ... y {len(sub_data) - 2} más')
            else:
                print(f'  ❌ Sin datos de cambios')
        except:
            print(f'  ❌ Error al procesar datos de cambios')
    else:
        print(f'  ❌ Sin datos de cambios')
    
    print()

print(f'=== RESUMEN ===')
print(f'Partidos totales: {total_matches}')
print(f'Partidos con goles: {matches_with_goals} ({matches_with_goals/total_matches*100:.1f}%)')
print(f'Partidos con tarjetas amarillas: {matches_with_yellow_cards} ({matches_with_yellow_cards/total_matches*100:.1f}%)')
print(f'Partidos con cambios: {matches_with_substitutions} ({matches_with_substitutions/total_matches*100:.1f}%)')

conn.close()
