import sqlite3

# Conexión a SQLite en database/app.db
conn = sqlite3.connect('database/app.db')
cursor = conn.cursor()

print('=== ANÁLISIS DE BASE DE DATOS APP.DB ===')
print()

# Tablas disponibles
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print(f'Tablas encontradas: {len(tables)}')
for table in sorted(tables):
    print(f'  - {table}')

print()

# Verificar datos principales de fútbol
main_tables = ['leagues', 'teams', 'matches', 'goals', 'cards', 'substitutions', 'injuries']

for table in main_tables:
    if table in tables:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        count = cursor.fetchone()[0]
        print(f'{table}: {count} registros')
    else:
        print(f'{table}: No existe')

print()

# Análisis por ligas (si existe tabla leagues)
if 'leagues' in tables:
    cursor.execute('SELECT * FROM leagues')
    leagues = cursor.fetchall()
    print('=== LIGAS DISPONIBLES ===')
    for league in leagues:
        print(f'  ID {league[0]}: {league[1]} ({league[2]})')

print()

# Análisis detallado si hay datos
if 'matches' in tables and 'leagues' in tables:
    print('=== ANÁLISIS DETALLADO POR LIGA ===')
    cursor.execute('SELECT * FROM leagues')
    leagues = cursor.fetchall()
    
    for league in leagues:
        league_id = league[0]
        league_name = league[1]
        
        print(f'📊 {league_name} (ID: {league_id})')
        print('-' * 40)
        
        # Equipos
        if 'teams' in tables:
            cursor.execute('SELECT COUNT(*) FROM teams WHERE league_id = ?', (league_id,))
            teams_count = cursor.fetchone()[0]
            print(f'  Equipos: {teams_count}')
        
        # Partidos
        cursor.execute('SELECT COUNT(*) FROM matches WHERE league_id = ?', (league_id,))
        matches_count = cursor.fetchone()[0]
        print(f'  Partidos: {matches_count}')
        
        # Goles
        if 'goals' in tables:
            cursor.execute('SELECT COUNT(*) FROM goals WHERE match_id IN (SELECT id FROM matches WHERE league_id = ?)', (league_id,))
            goals_count = cursor.fetchone()[0]
            print(f'  Goles: {goals_count}')
        
        # Tarjetas
        if 'cards' in tables:
            cursor.execute('SELECT COUNT(*) FROM cards WHERE match_id IN (SELECT id FROM matches WHERE league_id = ?)', (league_id,))
            cards_count = cursor.fetchone()[0]
            print(f'  Tarjetas: {cards_count}')
        
        print()

# Datos scraped si existen
if 'scraped_matches' in tables:
    cursor.execute('SELECT DISTINCT league, season, COUNT(*) FROM scraped_matches GROUP BY league, season ORDER BY league, season')
    scraped_data = cursor.fetchall()
    print('=== DATOS SCRAPED POR LIGA Y TEMPORADA ===')
    for data in scraped_data:
        print(f'  {data[0]} {data[1]}: {data[2]} partidos')

conn.close()
