import sqlite3
import json

db_path = 'database/app.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check how many events exist attached to scraped_matches for Premier League
cursor.execute('''
    SELECT COUNT(*) FROM goals g 
    JOIN scraped_matches m ON g.match_id = m.id 
    WHERE m.league = "Premier League"
''')
print("Goals in scraped_matches:", cursor.fetchone()[0])

cursor.execute('''
    SELECT COUNT(*) FROM cards c 
    JOIN scraped_matches m ON c.match_id = m.id 
    WHERE m.league = "Premier League"
''')
print("Cards in scraped_matches:", cursor.fetchone()[0])
