import psycopg2
from psycopg2.extras import RealDictCursor

# Conexión a PostgreSQL
conn = psycopg2.connect(
    host='localhost',
    database='postgres',
    user='postgres',
    password='1234'
)
cursor = conn.cursor(cursor_factory=RealDictCursor)

print('=== ANÁLISIS DETALLADO DE DATOS DE FÚTBOL ===')
print()

# 1. Ligas disponibles
cursor.execute('SELECT * FROM leagues ORDER BY id')
leagues = cursor.fetchall()
print('LIGAS DISPONIBLES:')
for league in leagues:
    print(f'  ID {league["id"]}: {league["name"]} ({league["country"]})')

print()
print('=== ANÁLISIS POR LIGA ===')
print()

# 2. Análisis detallado por liga
for league in leagues:
    league_id = league['id']
    league_name = league['name']
    
    print(f'📊 {league_name} (ID: {league_id})')
    print('-' * 50)
    
    # Equipos
    cursor.execute('SELECT COUNT(*) as count FROM teams WHERE league_id = %s', (league_id,))
    teams_count = cursor.fetchone()['count']
    print(f'  Equipos: {teams_count}')
    
    # Partidos
    cursor.execute('SELECT COUNT(*) as count FROM matches WHERE league_id = %s', (league_id,))
    matches_count = cursor.fetchone()['count']
    print(f'  Partidos totales: {matches_count}')
    
    # Goles
    cursor.execute('SELECT COUNT(*) as count FROM goals WHERE match_id IN (SELECT id FROM matches WHERE league_id = %s)', (league_id,))
    goals_count = cursor.fetchone()['count']
    print(f'  Goles: {goals_count}')
    
    # Tarjetas
    cursor.execute('SELECT COUNT(*) as count FROM cards WHERE match_id IN (SELECT id FROM matches WHERE league_id = %s)', (league_id,))
    cards_count = cursor.fetchone()['count']
    print(f'  Tarjetas: {cards_count}')
    
    # Cambios
    cursor.execute('SELECT COUNT(*) as count FROM substitutions WHERE match_id IN (SELECT id FROM matches WHERE league_id = %s)', (league_id,))
    subs_count = cursor.fetchone()['count']
    print(f'  Cambios: {subs_count}')
    
    # Lesiones
    cursor.execute('SELECT COUNT(*) as count FROM injuries WHERE match_id IN (SELECT id FROM matches WHERE league_id = %s)', (league_id,))
    injuries_count = cursor.fetchone()['count']
    print(f'  Lesiones: {injuries_count}')
    
    # Jornadas
    cursor.execute('SELECT DISTINCT matchday FROM matches WHERE league_id = %s ORDER BY matchday', (league_id,))
    matchdays = [row[0] for row in cursor.fetchall()]
    print(f'  Jornadas: {len(matchdays)} ({matchdays[0] if matchdays else "N/A"} - {matchdays[-1] if matchdays else "N/A"})')
    
    # Fechas de partidos
    cursor.execute('SELECT MIN(match_date) as first_date, MAX(match_date) as last_date FROM matches WHERE league_id = %s', (league_id,))
    dates = cursor.fetchone()
    if dates['first_date']:
        print(f'  Periodo: {dates["first_date"]} - {dates["last_date"]}')
    
    print()

# 3. Datos scraped
cursor.execute('SELECT DISTINCT league, season, COUNT(*) as matches FROM scraped_matches GROUP BY league, season ORDER BY league, season')
scraped_data = cursor.fetchall()
print('=== DATOS SCRAPED POR LIGA Y TEMPORADA ===')
for data in scraped_data:
    print(f'  {data["league"]} {data["season"]}: {data["matches"]} partidos')

# 4. Verificar temporadas completas
print()
print('=== VERIFICACIÓN DE TEMPORADAS COMPLETAS ===')
print()

for league in leagues:
    league_id = league['id']
    league_name = league['name']
    
    # Verificar scraped_matches para esta liga
    cursor.execute('SELECT DISTINCT season, COUNT(*) as matches FROM scraped_matches WHERE league = %s GROUP BY season ORDER BY season', (league_name,))
    seasons = cursor.fetchall()
    
    if seasons:
        print(f'🏆 {league_name}:')
        for season in seasons:
            season_name = season['season']
            matches_count = season['matches']
            
            # Para LaLiga, una temporada completa debería tener ~380 partidos (20 equipos * 19 jornadas * 2)
            # Para Premier, similar
            # Para Bundesliga, ~306 partidos (18 equipos)
            
            expected_matches = 380  # Estándar para ligas de 20 equipos
            if 'Bundesliga' in league_name:
                expected_matches = 306
            
            completion = (matches_count / expected_matches) * 100
            status = "✅ COMPLETA" if completion >= 95 else "⚠️ PARCIAL" if completion >= 50 else "❌ INCOMPLETA"
            
            print(f'  Temporada {season_name}: {matches_count}/{expected_matches} partidos ({completion:.1f}%) {status}')
        print()

conn.close()
