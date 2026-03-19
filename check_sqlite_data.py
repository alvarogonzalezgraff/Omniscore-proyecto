import sqlite3

# Conexión a SQLite
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

print('=== ANÁLISIS DE BASE DE DATOS SQLITE ===')
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

# Datos scraped si existen
if 'scraped_matches' in tables:
    cursor.execute('SELECT DISTINCT league, season, COUNT(*) FROM scraped_matches GROUP BY league, season ORDER BY league, season')
    scraped_data = cursor.fetchall()
    print('=== DATOS SCRAPED POR LIGA Y TEMPORADA ===')
    for data in scraped_data:
        print(f'  {data[0]} {data[1]}: {data[2]} partidos')

conn.close()
