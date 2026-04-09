import sqlite3

def check_and_fix():
    conn = sqlite3.connect('database/app.db')
    cursor = conn.cursor()
    
    # Identify Premier League ID
    cursor.execute("SELECT id FROM leagues WHERE name LIKE '%Premier%'")
    row = cursor.fetchone()
    if not row:
        print("Premier League not found")
        return
    league_id = row[0]
    print(f"Premier League ID: {league_id}")
    
    # GOALS duplicates based on (match_id, minute, team_id, player_name)
    cursor.execute("""
        SELECT match_id, minute, team_id, player_name, COUNT(*), GROUP_CONCAT(id)
        FROM goals
        WHERE match_id IN (SELECT id FROM matches WHERE league_id = ?)
        GROUP BY match_id, minute, team_id, player_name
        HAVING COUNT(*) > 1
    """, (league_id,))
    duplicated_goals = cursor.fetchall()
    
    # CARDS duplicates
    cursor.execute("""
        SELECT match_id, minute, team_id, player_name, card_type, COUNT(*), GROUP_CONCAT(id)
        FROM cards
        WHERE match_id IN (SELECT id FROM matches WHERE league_id = ?)
        GROUP BY match_id, minute, team_id, player_name, card_type
        HAVING COUNT(*) > 1
    """, (league_id,))
    duplicated_cards = cursor.fetchall()
    
    # SUBSTITUTIONS duplicates
    cursor.execute("""
        SELECT match_id, minute, team_id, player_out, player_in, COUNT(*), GROUP_CONCAT(id)
        FROM substitutions
        WHERE match_id IN (SELECT id FROM matches WHERE league_id = ?)
        GROUP BY match_id, minute, team_id, player_out, player_in
        HAVING COUNT(*) > 1
    """, (league_id,))
    duplicated_subs = cursor.fetchall()
    
    print(f"Found {len(duplicated_goals)} duplicated goal groups")
    print(f"Found {len(duplicated_cards)} duplicated card groups")
    print(f"Found {len(duplicated_subs)} duplicated substitution groups")
    
    # See if there are events with NULL or 'Desconocido' player_name
    cursor.execute("SELECT COUNT(*) FROM goals WHERE player_name IS NULL OR player_name = '' OR player_name LIKE '%Desconocido%'")
    print("Goals with no player:", cursor.fetchone()[0])
    
    cursor.execute("SELECT COUNT(*) FROM cards WHERE player_name IS NULL OR player_name = '' OR player_name LIKE '%Desconocido%'")
    print("Cards with no player:", cursor.fetchone()[0])

if __name__ == '__main__':
    check_and_fix()
