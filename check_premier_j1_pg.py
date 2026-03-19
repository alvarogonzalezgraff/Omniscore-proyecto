import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(ROOT_DIR / ".env")

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        dbname=os.getenv('DB_NAME', 'betwin_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', '')
    )

conn = get_db_connection()
cursor = conn.cursor()

# Get Premier League ID
cursor.execute("SELECT id FROM leagues WHERE name = 'Premier League'")
premier_result = cursor.fetchone()

if not premier_result:
    print("❌ No se encontró la Premier League en la base de datos")
    exit()

premier_league_id = premier_result[0]

# Get all Premier League matches from jornada 1
cursor.execute('''
    SELECT m.id, t1.name as home_team, t2.name as away_team, 
           m.home_score, m.away_score, m.matchday
    FROM matches m
    JOIN teams t1 ON m.home_team_id = t1.id
    JOIN teams t2 ON m.away_team_id = t2.id
    WHERE m.league_id = %s AND m.matchday = 1
    ORDER BY t1.name
''', (premier_league_id,))

matches = cursor.fetchall()
print(f'=== PREMIER LEAGUE - JORNADA 1 ===')
print(f'Total partidos encontrados: {len(matches)}')
print()

total_matches = len(matches)
matches_with_goals = 0
matches_with_yellow_cards = 0
matches_with_substitutions = 0

for match in matches:
    match_id, home_team, away_team, home_score, away_score, matchday = match
    print(f'🏆 {home_team} vs {away_team} ({home_score}-{away_score})')
    
    # Check goals
    cursor.execute('SELECT COUNT(*) FROM goals WHERE match_id = %s', (match_id,))
    goals_count = cursor.fetchone()[0]
    if goals_count > 0:
        matches_with_goals += 1
        print(f'  ✅ Goles: {goals_count} eventos')
        cursor.execute('SELECT player_name, minute FROM goals WHERE match_id = %s LIMIT 3', (match_id,))
        for goal in cursor.fetchall():
            print(f'     - Min {goal[1]}: {goal[0]}')
    else:
        print(f'  ❌ Sin datos de goles')
    
    # Check yellow cards
    cursor.execute("SELECT COUNT(*) FROM cards WHERE match_id = %s AND card_type = 'Amarilla'", (match_id,))
    yellow_cards_count = cursor.fetchone()[0]
    if yellow_cards_count > 0:
        matches_with_yellow_cards += 1
        print(f'  ✅ Tarjetas amarillas: {yellow_cards_count}')
        cursor.execute('SELECT player_name, minute FROM cards WHERE match_id = %s AND card_type = %s LIMIT 2', (match_id, 'Amarilla'))
        for card in cursor.fetchall():
            print(f'     - Min {card[1]}: {card[0]}')
    else:
        print(f'  ❌ Sin tarjetas amarillas')
    
    # Check substitutions
    cursor.execute('SELECT COUNT(*) FROM substitutions WHERE match_id = %s', (match_id,))
    subs_count = cursor.fetchone()[0]
    if subs_count > 0:
        matches_with_substitutions += 1
        print(f'  ✅ Cambios: {subs_count}')
        cursor.execute('SELECT player_out, player_in, minute FROM substitutions WHERE match_id = %s LIMIT 2', (match_id,))
        for sub in cursor.fetchall():
            print(f'     - Min {sub[2]}: {sub[0]} → {sub[1]}')
    else:
        print(f'  ❌ Sin datos de cambios')
    
    print()

print(f'=== RESUMEN ===')
print(f'Partidos totales: {total_matches}')
print(f'Partidos con goles: {matches_with_goals} ({matches_with_goals/total_matches*100:.1f}%)')
print(f'Partidos con tarjetas amarillas: {matches_with_yellow_cards} ({matches_with_yellow_cards/total_matches*100:.1f}%)')
print(f'Partidos con cambios: {matches_with_substitutions} ({matches_with_substitutions/total_matches*100:.1f}%)')

conn.close()
