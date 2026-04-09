import sqlite3

conn = sqlite3.connect('database/app.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT m.id, (SELECT name FROM teams WHERE id = m.home_team_id), 
           (SELECT name FROM teams WHERE id = m.away_team_id),
           m.home_score, m.away_score, COUNT(g.id)
    FROM matches m
    LEFT JOIN goals g ON m.id = g.match_id
    WHERE m.league_id = 5
    GROUP BY m.id
    ORDER BY COUNT(g.id) DESC
    LIMIT 10
''')

print("Partidos con más goles registrados:")
for row in cursor.fetchall():
    print(row)

cursor.execute('''
    SELECT m.id, COUNT(c.id)
    FROM matches m
    LEFT JOIN cards c ON m.id = c.match_id
    WHERE m.league_id = 5
    GROUP BY m.id
    ORDER BY COUNT(c.id) DESC
    LIMIT 10
''')

print("\nPartidos con más tarjetas registradas:")
for row in cursor.fetchall():
    print(row)

cursor.execute('''
    SELECT COUNT(*) FROM goals WHERE match_id IN (SELECT id FROM matches WHERE league_id = 5)
''')
print("Total goles Premier:", cursor.fetchone()[0])
