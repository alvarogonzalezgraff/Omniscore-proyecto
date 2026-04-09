import json
import sqlite3

# Verificar el JS generado
content = open('assets/js/leagues/premier.js','r',encoding='utf-8').read()
js_data = content.replace('window.leagueData = window.leagueData || {};', '').replace('window.leagueData.premier = ', '').strip().rstrip(';')
data = json.loads(js_data)

print(f"Total jornadas: {len(data['results'])}")
print(f"Total equipos en standings: {len(data['standings'])}")

total_match=0; total_goals=0; total_cards=0; total_subs=0
for jornada in data['results']:
    for fecha in jornada['dates']:
        for m in fecha['matches']:
            total_match += 1
            total_goals += len(m['goals_details'])
            total_cards += len(m['cards'])
            total_subs += len(m['substitutions'])

print(f"Total partidos: {total_match}")
print(f"Total goles: {total_goals}")
print(f"Total tarjetas: {total_cards}")
print(f"Total cambios: {total_subs}")

print("\n--- JORNADA 1 ---")
j1 = data['results'][0]
print(f"Matchweek: {j1['matchweek']}")
for m in j1['dates'][0]['matches'][:3]:
    print(f"  {m['home_team']} {m['home_score']}-{m['away_score']} {m['away_team']} | goals={len(m['goals_details'])}, cards={len(m['cards'])}, subs={len(m['substitutions'])}")
    for g in m['goals_details']:
        print(f"    ⚽ {g['minute']}' {g['player']} ({g['team']})")

# Verificar algún partido con muchas sustituciones duplicadas
print("\n--- VERIFICANDO DUPLICADOS ---")
conn = sqlite3.connect('database/app.db')
c = conn.cursor()
c.execute('''
    SELECT s.match_id, COUNT(*), s.player_in, s.player_out, s.minute
    FROM substitutions s
    JOIN scraped_matches m ON s.match_id = m.id
    WHERE m.league = "Premier League" AND m.season = "2024/25"
    GROUP BY s.match_id, s.team_id, s.player_in, s.player_out, s.minute
    HAVING COUNT(*) > 1
    LIMIT 5
''')
dups = c.fetchall()
print(f"Grupos duplicados en substitutions: {len(dups)}")

c.execute('''
    SELECT COUNT(*) FROM substitutions s
    JOIN scraped_matches m ON s.match_id = m.id
    WHERE m.league = "Premier League" AND m.season = "2024/25"
''')
print(f"Total cambios en DB para 2024/25: {c.fetchone()[0]}")
