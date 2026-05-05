import sqlite3

db_path = r'C:\Users\pc\Desktop\Omniscore-proyecto\backend\database\app.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("=" * 60)
print("BASE DE DATOS: app.db (SQLite)")
print("=" * 60)

# 1. Ver ligas
c.execute('SELECT id, name, country FROM leagues ORDER BY id;')
rows = c.fetchall()
print("\n=== LIGAS REGISTRADAS ===")
for r in rows:
    print(f"  ID {r[0]:>3} | {r[1]:<25} | {r[2]}")

# 2. Equipos Serie A (tabla teams)
print("\n=== EQUIPOS SERIE A (tabla 'teams') ===")
c.execute('''
    SELECT t.id, t.name, t.logo_path
    FROM teams t
    JOIN leagues l ON t.league_id = l.id
    WHERE l.id = 4
    ORDER BY t.name;
''')
rows = c.fetchall()
print(f"Total: {len(rows)} equipos\n")
for r in rows:
    logo = r[2] if r[2] else 'None'
    print(f"  ID: {r[0]:<4} | Equipo: {r[1]:<20} | Logo: {logo}")

# 3. Verificar tablas existentes
c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
all_tables = [t[0] for t in c.fetchall()]
print(f"\n=== TABLAS EN LA BASE DE DATOS ({len(all_tables)}) ===")
print(f"  {', '.join(all_tables)}")

# 3b. Equipos en scraped_data si existe
if 'scraped_data' in all_tables:
    print("\n=== DATOS SCRAPED (scraped_data) ===")
    c.execute('PRAGMA table_info(scraped_data);')
    cols = c.fetchall()
    print(f"Columnas: {[col[1] for col in cols]}")
    c.execute("SELECT id, sport, league, season, team_name, position, points, matches_played, wins, draws, losses, goals_for, goals_against, goal_diff, form, updated_at FROM scraped_data WHERE league = 'Serie A' LIMIT 5;")
    rows = c.fetchall()
    for r in rows:
        print(f"  {r}")
else:
    print("\n[No existe tabla 'scraped_data']")

# 3c. Equipos en standings si existe
if 'standings' in all_tables:
    print("\n=== EQUIPOS SERIE A EN standings ===")
    c.execute('''
        SELECT team_name, position, points, matches_played, wins, draws, losses, goals_for, goals_against, goal_diff
        FROM standings
        WHERE league_name = 'Serie A'
        ORDER BY position;
    ''')
    rows = c.fetchall()
    print(f"Total: {len(rows)} equipos\n")
    for r in rows:
        print(f"  Pos {r[1]:>2} | {r[0]:<20} | Pts: {r[2]:>3} | PJ: {r[3]:>2} | V:{r[4]} E:{r[5]} D:{r[6]} | GF:{r[7]} GC:{r[8]} DG:{r[9]}")
else:
    print("\n[No existe tabla 'standings']")

# 4. Partidos de Serie A registrados
if 'scraped_matches' in all_tables:
    print("\n=== PARTIDOS SERIE A EN scraped_matches ===")
    c.execute('''
        SELECT COUNT(*) FROM scraped_matches WHERE league_name = 'Serie A';
    ''')
    count = c.fetchone()[0]
    print(f"Total partidos scrapeados: {count}")

    if count > 0:
        c.execute('''
            SELECT DISTINCT matchday FROM scraped_matches
            WHERE league_name = 'Serie A'
            ORDER BY CAST(REPLACE(matchday, 'Jornada ', '') AS INTEGER);
        ''')
        jornadas = [r[0] for r in c.fetchall()]
        print(f"Jornadas disponibles: {len(jornadas)}")
        print(f"  {', '.join(jornadas[:10])}{'...' if len(jornadas) > 10 else ''}")
        
        c.execute('''
            SELECT home_team, away_team, home_score, away_score, matchday, date
            FROM scraped_matches
            WHERE league_name = 'Serie A'
            ORDER BY date DESC
            LIMIT 5;
        ''')
        print("\nUltimos 5 partidos:")
        for r in c.fetchall():
            print(f"  {r[4]} | {r[0]} {r[2]}-{r[3]} {r[1]} | {r[5]}")
else:
    print("\n[No existe tabla 'scraped_matches']")

# 5. Top goleadores Serie A
if 'scraped_scorers' in all_tables:
    print("\n=== TOP GOLEADORES SERIE A (scraped_scorers) ===")
    c.execute('''
        SELECT player_name, team_name, goals
        FROM scraped_scorers
        WHERE league_name = 'Serie A'
        ORDER BY goals DESC, player_name
        LIMIT 10;
    ''')
    rows = c.fetchall()
    for i, r in enumerate(rows, 1):
        print(f"  {i:>2}. {r[0]:<25} | {r[1]:<20} | {r[2]} goles")
else:
    print("\n[No existe tabla 'scraped_scorers']")

# 6. Tabla matches (datos principales)
if 'matches' in all_tables:
    print("\n=== PARTIDOS EN 'matches' (tabla principal) ===")
    c.execute('''
        SELECT COUNT(*) FROM matches m
        JOIN teams ht ON m.home_team_id = ht.id
        JOIN leagues l ON ht.league_id = l.id
        WHERE l.id = 4;
    ''')
    count = c.fetchone()[0]
    print(f"Total partidos en tabla matches: {count}")

conn.close()
print("\n" + "=" * 60)
print("FIN DEL REPORTE")
print("=" * 60)
