import sqlite3

conn = sqlite3.connect('database/app.db')
c = conn.cursor()

# Ver cuantos scraped_matches de 2024/25 tienen eventos
c.execute('''
    SELECT COUNT(DISTINCT s.id) FROM scraped_matches s
    JOIN goals g ON g.match_id = s.id
    WHERE s.league = "Premier League" AND s.season = "2024/25"
''')
print("Scraped matches 2024/25 con goles:", c.fetchone()[0])

# Ver partidos con goles duplicados
c.execute('''
    SELECT g.match_id, g.minute, g.player_name, g.team_id, COUNT(*)
    FROM goals g
    JOIN scraped_matches m ON g.match_id = m.id
    WHERE m.league = "Premier League" AND m.season = "2024/25"
    GROUP BY g.match_id, g.minute, g.player_name, g.team_id
    HAVING COUNT(*) > 1
    LIMIT 5
''')
dups = c.fetchall()
print(f"\nGrupos de goles duplicados: {len(dups)}")
for d in dups:
    print(f"  match_id={d[0]}, min={d[1]}, player={d[2]}, count={d[4]}")

# Ver sustituciones duplicadas
c.execute('''
    SELECT s.match_id, s.minute, s.player_in, s.player_out, COUNT(*)
    FROM substitutions s
    JOIN scraped_matches m ON s.match_id = m.id
    WHERE m.league = "Premier League" AND m.season = "2024/25"
    GROUP BY s.match_id, s.minute, s.player_in, s.player_out
    HAVING COUNT(*) > 1
    LIMIT 5
''')
dups_subs = c.fetchall()
print(f"\nGrupos de cambios duplicados: {len(dups_subs)}")
for d in dups_subs:
    print(f"  match_id={d[0]}, min={d[1]}, in={d[2]}, out={d[3]}, count={d[4]}")

# Ver cuantos cambios hay en total
c.execute('''
    SELECT COUNT(*) FROM substitutions s
    JOIN scraped_matches m ON s.match_id = m.id
    WHERE m.league = "Premier League" AND m.season = "2024/25"
''')
print(f"\nTotal cambios 2024/25: {c.fetchone()[0]}")

# Ver cuantos cambios tiene un partido concreto
c.execute('''
    SELECT m.home_team, m.away_team, COUNT(s.id)
    FROM substitutions s
    JOIN scraped_matches m ON s.match_id = m.id
    WHERE m.league = "Premier League" AND m.season = "2024/25"
    GROUP BY s.match_id
    ORDER BY COUNT(s.id) DESC
    LIMIT 5
''')
print(f"\nPartidos con mas cambios:")
for r in c.fetchall():
    print(f"  {r[0]} vs {r[1]}: {r[2]} cambios")
