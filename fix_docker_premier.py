import psycopg2

def get_connection():
    try:
        return psycopg2.connect(host='localhost', port='5433', dbname='Omniscore_db', user='postgres', password='1234')
    except:
        return psycopg2.connect(host='localhost', port='5433', dbname='Omniscore_db', user='postgres', password='docker_password')

def run_fix():
    print("=== FIXING PREMIER LEAGUE DATA IN DOCKER POSTGRES ===")
    try:
        conn = get_connection()
        conn.autocommit = False
        cursor = conn.cursor()
        
        # Identify Premier League ID
        cursor.execute("SELECT id FROM leagues WHERE name LIKE '%Premier%'")
        row = cursor.fetchone()
        if not row:
            print("Premier League not found")
            return
        league_id = row[0]
        
        # 1. Provide Invented Players
        print("1. Fixing missing player names (Invented Players)...")
        for table in ['goals', 'cards', 'substitutions']:
            player_col = 'player_name'
            if table == 'substitutions':
                player_cols = ['player_in', 'player_out']
            else:
                player_cols = ['player_name']
                
            for col in player_cols:
                cursor.execute(f'''
                    UPDATE {table} t
                    SET {col} = 'Jugador Inventado ' || (SELECT name FROM teams tr WHERE tr.id = t.team_id)
                    WHERE 
                        t.match_id IN (SELECT id FROM matches WHERE league_id = %s)
                        AND (t.{col} IS NULL OR TRIM(t.{col}) = '' OR t.{col} ILIKE '%%Desconocido%%')
                ''', (league_id,))
                if cursor.rowcount > 0:
                    print(f"   Updated {cursor.rowcount} empty players in {table}.{col}")
        
        # 2. Delete Duplicates
        print("\n2. Removing Duplicates...")
        
        # Delete duplicate goals
        cursor.execute('''
            DELETE FROM goals WHERE id IN (
                SELECT id FROM (
                    SELECT id, ROW_NUMBER() OVER (PARTITION BY match_id, team_id, player_name, minute ORDER BY id) as rn
                    FROM goals
                    WHERE match_id IN (SELECT id FROM matches WHERE league_id = %s)
                ) t WHERE t.rn > 1
            )
        ''', (league_id,))
        print(f"   Removed {cursor.rowcount} duplicate goals.")

        # Delete duplicate cards
        cursor.execute('''
            DELETE FROM cards WHERE id IN (
                SELECT id FROM (
                    SELECT id, ROW_NUMBER() OVER (PARTITION BY match_id, team_id, player_name, minute, card_type ORDER BY id) as rn
                    FROM cards
                    WHERE match_id IN (SELECT id FROM matches WHERE league_id = %s)
                ) t WHERE t.rn > 1
            )
        ''', (league_id,))
        print(f"   Removed {cursor.rowcount} duplicate cards.")
        
        # Delete duplicate substitutions
        cursor.execute('''
            DELETE FROM substitutions WHERE id IN (
                SELECT id FROM (
                    SELECT id, ROW_NUMBER() OVER (PARTITION BY match_id, team_id, player_in, player_out, minute ORDER BY id) as rn
                    FROM substitutions
                    WHERE match_id IN (SELECT id FROM matches WHERE league_id = %s)
                ) t WHERE t.rn > 1
            )
        ''', (league_id,))
        print(f"   Removed {cursor.rowcount} duplicate substitutions.")

        conn.commit()
        print("\n✅ All duplicates removed and players named correctly!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run_fix()
