import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path('.').resolve()
load_dotenv(ROOT_DIR / '.env')

conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5433'),
    dbname=os.getenv('DB_NAME', 'Omniscore_db'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', '')
)

cursor = conn.cursor()

# Verificar equipos de Premier League
cursor.execute('SELECT id, name FROM teams WHERE league_id = 5 ORDER BY id')
teams = cursor.fetchall()

print('=== EQUIPOS PREMIER LEAGUE ===')
for team_id, name in teams:
    print(f'Team ID {team_id}: {name}')

# Verificar si hay goles con team_id que no coincide con home/away team
cursor.execute('''
    SELECT g.match_id, g.team_id, g.player_name, m.home_team_id, m.away_team_id
    FROM goals g
    JOIN matches m ON g.match_id = m.id
    WHERE m.league_id = 5 AND g.match_id = 547
    LIMIT 10
''')

goals_mismatch = cursor.fetchall()
print('\n=== VERIFICACIÓN DE TEAM_ID EN GOLES (PARTIDO 547) ===')
for goal in goals_mismatch:
    match_id, goal_team_id, player, home_id, away_id = goal
    print(f'Gol de {player}: team_id={goal_team_id}, home_id={home_id}, away_id={away_id}')

# Verificar equipos específicos del partido 547
cursor.execute('''
    SELECT m.home_team_id, m.away_team_id, t1.name as home_name, t2.name as away_name
    FROM matches m
    JOIN teams t1 ON m.home_team_id = t1.id
    JOIN teams t2 ON m.away_team_id = t2.id
    WHERE m.id = 547
''')

match_info = cursor.fetchone()
if match_info:
    home_id, away_id, home_name, away_name = match_info
    print(f'\nPartido 547: {home_name} (ID: {home_id}) vs {away_name} (ID: {away_id})')

conn.close()
