import sqlite3

# Conexión a SQLite
conn = sqlite3.connect('database/app.db')
cursor = conn.cursor()

print('=== VERIFICACIÓN DE COMPLETITUD DE DATOS SCRAPED ===')
print()

# Datos scraped por liga y temporada
cursor.execute('SELECT DISTINCT league, season, COUNT(*) as matches FROM scraped_matches GROUP BY league, season ORDER BY league, season')
scraped_data = cursor.fetchall()

print('DATOS SCRAPED POR LIGA Y TEMPORADA:')
print()

for data in scraped_data:
    league = data[0]
    season = data[1]
    matches_count = data[2]
    
    # Determinar partidos esperados por liga
    if 'Premier League' in league:
        expected_matches = 380  # 20 equipos
    elif 'LaLiga EA Sports' in league:
        expected_matches = 380  # 20 equipos
    elif 'Bundesliga' in league:
        expected_matches = 306  # 18 equipos
    elif 'Serie A' in league:
        expected_matches = 380  # 20 equipos
    elif 'Champions' in league:
        expected_matches = 189  # Variable, pero típico
    elif 'Liga Hypermotion' in league:
        expected_matches = 462  # 22 equipos
    else:
        expected_matches = 380  # Estándar
    
    completion = (matches_count / expected_matches) * 100
    
    if completion >= 95:
        status = "✅ COMPLETA"
    elif completion >= 50:
        status = "⚠️ PARCIAL"
    else:
        status = "❌ INCOMPLETA"
    
    print(f'🏆 {league} {season}:')
    print(f'   Partidos: {matches_count}/{expected_matches} ({completion:.1f}%) {status}')
    
    # Verificar rango de jornadas
    cursor.execute('SELECT MIN(matchday), MAX(matchday) FROM scraped_matches WHERE league = ? AND season = ?', (league, season))
    jornada_range = cursor.fetchone()
    if jornada_range[0]:
        print(f'   Jornadas: {jornada_range[0]} - {jornada_range[1]}')
    
    print()

print('=== ANÁLISIS DE DATOS ESTRUCTURADOS ===')
print()

# Comparar con datos estructurados
cursor.execute('SELECT * FROM leagues')
leagues = cursor.fetchall()

for league in leagues:
    league_id = league[0]
    league_name = league[1]
    
    # Partidos estructurados
    cursor.execute('SELECT COUNT(*) FROM matches WHERE league_id = ?', (league_id,))
    structured_matches = cursor.fetchone()[0]
    
    # Partidos scraped para esta liga (todas las temporadas)
    cursor.execute('SELECT COUNT(*) FROM scraped_matches WHERE league = ?', (league_name,))
    scraped_matches = cursor.fetchone()[0]
    
    print(f'📊 {league_name}:')
    print(f'   Datos estructurados: {structured_matches} partidos')
    print(f'   Datos scraped: {scraped_matches} partidos')
    
    if scraped_matches > structured_matches:
        print(f'   ✅ Tienes más datos scraped que estructurados')
    elif structured_matches > 0:
        print(f'   ⚠️ Tienes datos estructurados pero menos scraped')
    else:
        print(f'   ❌ No tienes datos estructurados para esta liga')
    
    print()

print('=== RECOMENDACIÓN ===')
print()

# Verificar qué ligas tienen datos completos
complete_leagues = []
for data in scraped_data:
    league = data[0]
    season = data[1]
    matches_count = data[2]
    
    if 'Premier League' in league or 'LaLiga EA Sports' in league:
        expected_matches = 380
    elif 'Bundesliga' in league:
        expected_matches = 306
    elif 'Serie A' in league:
        expected_matches = 380
    else:
        continue
    
    completion = (matches_count / expected_matches) * 100
    if completion >= 95:
        complete_leagues.append(f'{league} {season}')

if complete_leagues:
    print('✅ LIGAS CON DATOS COMPLETOS DISPONIBLES:')
    for league in complete_leagues:
        print(f'   - {league}')
    print()
    print('🎯 ¡Sí, tienes copias completas de datos! Puedes usar estas ligas/temporadas.')
else:
    print('⚠️ No hay ligas con 100% de datos completos, pero tienes muchas con datos parciales muy completos.')

conn.close()
