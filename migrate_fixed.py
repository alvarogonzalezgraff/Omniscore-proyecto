import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import sys
from datetime import datetime

print('=== MIGRACIÓN CORREGIDA DE APP.DB A DOCKER POSTGRES ===')
print()

# 1. Conexión a SQLite (origen)
try:
    sqlite_conn = sqlite3.connect('database/app.db')
    sqlite_cursor = sqlite_conn.cursor()
    print('✅ Conectado a SQLite (database/app.db)')
except Exception as e:
    print(f'❌ Error conectando a SQLite: {e}')
    sys.exit(1)

# 2. Conexión a PostgreSQL Docker (destino)
try:
    pg_conn = psycopg2.connect(
        host='localhost',
        port=5433,
        database='Omniscore_db',
        user='postgres',
        password='1234'
    )
    pg_cursor = pg_conn.cursor()
    print('✅ Conectado a PostgreSQL Docker (localhost:5433)')
except Exception as e:
    print(f'❌ Error conectando a PostgreSQL Docker: {e}')
    sys.exit(1)

print()

import re

# 3. Función para limpiar y preparar datos
def clean_value(value, column_name=None):
    if value is None:
        return None
    
    # Convertir integers a boolean para campos específicos
    if column_name in ['is_finished', 'is_own_goal', 'is_penalty']:
        if isinstance(value, int):
            return bool(value)
        elif isinstance(value, str):
            return value.lower() in ('1', 'true', 't', 'yes', 'y')
            
    # Fix dates
    if column_name in ['match_date', 'date', 'updated_at', 'start_date', 'end_date', 'birth_date', 'created_at']:
        if isinstance(value, str):
            value = value.strip()
            # If it's DD/MM/YYYY
            match = re.match(r'^(\d{2})/(\d{2})/(\d{4})(.*)$', value)
            if match:
                value = f"{match.group(3)}-{match.group(2)}-{match.group(1)}{match.group(4)}"
            
    # Para otros tipos
    if isinstance(value, str):
        return value.strip()
    return value


# 4. Migración de tablas principales con manejo especial
print('📊 INICIANDO MIGRACIÓN CORREGIDA:')
print('-' * 50)

# Tablas que necesitan manejo especial para booleanos
boolean_tables = {
    'matches': ['is_finished'],
    'goals': ['is_own_goal', 'is_penalty'],
    'scraped_matches': ['is_finished'],
    'basketball_matches': ['is_finished']
}

# Tablas a migrar
tables_to_migrate = [
    ('leagues', 'id', ['id', 'name', 'country']),
    ('teams', 'id', ['id', 'league_id', 'name', 'logo_path']),
    ('matches', 'id', ['id', 'league_id', 'home_team_id', 'away_team_id', 'matchday', 'match_date', 'home_score', 'away_score', 'is_finished']),
    ('goals', 'id', ['id', 'match_id', 'team_id', 'player_name', 'minute', 'assist_player_name', 'is_own_goal', 'is_penalty']),
    ('cards', 'id', ['id', 'match_id', 'team_id', 'player_name', 'minute', 'card_type', 'reason', 'description']),
    ('substitutions', 'id', ['id', 'match_id', 'team_id', 'player_in', 'player_out', 'minute']),
    ('injuries', 'id', ['id', 'match_id', 'team_id', 'player_name', 'minute', 'description']),
    ('penalties', 'id', ['id', 'match_id', 'team_id', 'player_name', 'minute', 'outcome', 'description']),
    ('scraped_matches', 'id', ['id', 'league', 'season', 'matchday', 'date', 'home_team', 'away_team', 'home_score', 'away_score', 'is_finished', 'scorers', 'updated_at', 'assists', 'yellow_cards', 'red_cards', 'substitutions', 'injuries', 'url']),
    ('scraped_data', 'id', ['id', 'sport', 'league', 'season', 'team_name', 'position', 'points', 'matches_played', 'wins', 'draws', 'losses', 'goals_for', 'goals_against', 'goal_diff', 'form', 'updated_at']),
    ('player_stats', 'id', ['id', 'league_id', 'player_name', 'team_name', 'goals', 'assists', 'matches_played', 'updated_at'])
]

total_migrated = 0
total_errors = 0

for table_name, primary_key, columns in tables_to_migrate:
    print(f'📋 Migrando tabla: {table_name}')
    
    try:
        # Verificar si existe en SQLite
        sqlite_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if not sqlite_cursor.fetchone():
            print(f'   ⚠️ Tabla {table_name} no existe en SQLite - omitiendo')
            continue
        
        # Obtener datos de SQLite
        sqlite_cursor.execute(f'SELECT {", ".join(columns)} FROM {table_name}')
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print(f'   ⚠️ Tabla {table_name} vacía - omitiendo')
            continue
        
        print(f'   📥 Obtenidos {len(rows)} registros de SQLite')
        
        # Limpiar tabla destino en PostgreSQL
        pg_cursor.execute(f'TRUNCATE TABLE {table_name} CASCADE')
        print(f'   🗑️ Tabla {table_name} limpiada en PostgreSQL')
        
        # Preparar inserción
        placeholders = ', '.join(['%s'] * len(columns))
        insert_query = f'INSERT INTO {table_name} ({", ".join(columns)}) VALUES ({placeholders})'
        
        # Insertar datos con manejo especial para booleanos
        migrated_count = 0
        error_count = 0
        
        for row in rows:
            try:
                # Limpiar valores con manejo especial para booleanos
                clean_row = []
                for i, value in enumerate(row):
                    column_name = columns[i] if i < len(columns) else None
                    clean_row.append(clean_value(value, column_name))
                
                pg_cursor.execute(insert_query, clean_row)
                migrated_count += 1
            except Exception as e:
                error_count += 1
                if error_count <= 5:  # Mostrar solo primeros 5 errores
                    print(f'      ❌ Error en registro {migrated_count + error_count}: {str(e)[:100]}')
        
        pg_conn.commit()
        
        print(f'   ✅ Migrados: {migrated_count:,} registros')
        if error_count > 0:
            print(f'   ❌ Errores: {error_count:,} registros')
        
        total_migrated += migrated_count
        total_errors += error_count
        
    except Exception as e:
        print(f'   ❌ Error general migrando {table_name}: {e}')
        total_errors += 1
        pg_conn.rollback()
    
    print()

# 5. Migración de tablas de baloncesto
print('🏀 MIGRANDO DATOS DE BALONCESTO:')
print('-' * 50)

basketball_tables = [
    ('basketball_leagues', 'id', ['id', 'name', 'country', 'level']),
    ('basketball_seasons', 'id', ['id', 'league_id', 'season', 'start_date', 'end_date']),
    ('basketball_teams', 'id', ['id', 'league_id', 'name', 'short_name', 'logo_path']),
    ('basketball_matches', 'id', ['id', 'league_id', 'season_id', 'matchday', 'match_date', 'home_team_id', 'away_team_id', 'home_score', 'away_score', 'is_finished', 'venue', 'referee', 'source_url']),
    ('basketball_players', 'id', ['id', 'full_name', 'nationality', 'birth_date']),
    ('basketball_standings', 'id', ['id', 'season_id', 'team_id', 'position', 'games_played', 'wins', 'losses', 'points_for', 'points_against', 'point_diff', 'streak', 'updated_at']),
    ('basketball_player_season_stats', 'id', ['id', 'season_id', 'player_id', 'team_id', 'points', 'assists', 'rebounds', 'matches_played', 'updated_at'])
]

for table_name, primary_key, columns in basketball_tables:
    print(f'📋 Migrando tabla: {table_name}')
    
    try:
        sqlite_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if not sqlite_cursor.fetchone():
            print(f'   ⚠️ Tabla {table_name} no existe en SQLite - omitiendo')
            continue
        
        sqlite_cursor.execute(f'SELECT {", ".join(columns)} FROM {table_name}')
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print(f'   ⚠️ Tabla {table_name} vacía - omitiendo')
            continue
        
        print(f'   📥 Obtenidos {len(rows)} registros')
        
        pg_cursor.execute(f'TRUNCATE TABLE {table_name} CASCADE')
        
        placeholders = ', '.join(['%s'] * len(columns))
        insert_query = f'INSERT INTO {table_name} ({", ".join(columns)}) VALUES ({placeholders})'
        
        migrated_count = 0
        for row in rows:
            try:
                clean_row = []
                for i, value in enumerate(row):
                    column_name = columns[i] if i < len(columns) else None
                    clean_row.append(clean_value(value, column_name))
                
                pg_cursor.execute(insert_query, clean_row)
                migrated_count += 1
            except Exception as e:
                total_errors += 1
        
        pg_conn.commit()
        print(f'   ✅ Migrados: {migrated_count:,} registros')
        total_migrated += migrated_count
        
    except Exception as e:
        print(f'   ❌ Error migrando {table_name}: {e}')
        total_errors += 1
        pg_conn.rollback()
    
    print()

# 6. Migración de tablas de tenis
print('🎾 MIGRANDO DATOS DE TENIS:')
print('-' * 50)

tennis_tables = [
    ('tennis_tournaments', 'id', ['id', 'name', 'tour', 'category', 'surface', 'location', 'country', 'official_url', 'created_at']),
    ('tennis_players', 'id', ['id', 'full_name']),
    ('tennis_editions', 'id', ['id', 'tournament_id', 'year', 'winner_player_id', 'runner_up_player_id', 'score', 'notes', 'source'])
]

for table_name, primary_key, columns in tennis_tables:
    print(f'📋 Migrando tabla: {table_name}')
    
    try:
        sqlite_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if not sqlite_cursor.fetchone():
            print(f'   ⚠️ Tabla {table_name} no existe en SQLite - omitiendo')
            continue
        
        sqlite_cursor.execute(f'SELECT {", ".join(columns)} FROM {table_name}')
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print(f'   ⚠️ Tabla {table_name} vacía - omitiendo')
            continue
        
        print(f'   📥 Obtenidos {len(rows)} registros')
        
        pg_cursor.execute(f'TRUNCATE TABLE {table_name} CASCADE')
        
        placeholders = ', '.join(['%s'] * len(columns))
        insert_query = f'INSERT INTO {table_name} ({", ".join(columns)}) VALUES ({placeholders})'
        
        migrated_count = 0
        for row in rows:
            try:
                clean_row = []
                for i, value in enumerate(row):
                    column_name = columns[i] if i < len(columns) else None
                    clean_row.append(clean_value(value, column_name))
                
                pg_cursor.execute(insert_query, clean_row)
                migrated_count += 1
            except Exception as e:
                total_errors += 1
        
        pg_conn.commit()
        print(f'   ✅ Migrados: {migrated_count:,} registros')
        total_migrated += migrated_count
        
    except Exception as e:
        print(f'   ❌ Error migrando {table_name}: {e}')
        total_errors += 1
        pg_conn.rollback()
    
    print()

# 7. Migración de usuarios
print('👤 MIGRANDO USUARIOS:')
print('-' * 50)

try:
    sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if sqlite_cursor.fetchone():
        sqlite_cursor.execute('SELECT id, username, email, password, full_name, created_at FROM users')
        users = sqlite_cursor.fetchall()
        
        if users:
            pg_cursor.execute('TRUNCATE TABLE users CASCADE')
            
            for user in users:
                pg_cursor.execute('''
                    INSERT INTO users (id, username, email, password, full_name, created_at) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', user)
            
            pg_conn.commit()
            print(f'✅ Migrados: {len(users)} usuarios')
            total_migrated += len(users)
        else:
            print('⚠️ No hay usuarios para migrar')
    else:
        print('⚠️ Tabla users no existe en SQLite')
        
except Exception as e:
    print(f'❌ Error migrando usuarios: {e}')
    total_errors += 1

print()

# 8. Resumen final
print('📋 RESUMEN DE MIGRACIÓN CORREGIDA:')
print('=' * 50)
print(f'📊 Registros migrados exitosamente: {total_migrated:,}')
print(f'❌ Errores encontrados: {total_errors:,}')
print(f'📅 Fecha y hora: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

if total_errors == 0:
    print('🎉 ¡MIGRACIÓN COMPLETADA CON ÉXITO!')
    print('✅ Todos los datos han sido transferidos a Docker PostgreSQL')
else:
    print('⚠️ MIGRACIÓN COMPLETADA (con algunos errores)')
    print(f'📊 Se migraron {total_migrated:,} registros exitosamente')
    if total_errors > 0:
        print(f'❌ {total_errors:,} registros tuvieron errores (principalmente booleanos)')

print()
print('🔍 VERIFICACIÓN POST-MIGRACIÓN:')
print('Puedes verificar los datos migrados con:')
print('  docker exec -it Omniscore_postgres psql -U postgres -d postgres -c "SELECT COUNT(*) FROM leagues;"')
print('  docker exec -it Omniscore_postgres psql -U postgres -d postgres -c "SELECT COUNT(*) FROM scraped_matches;"')

# Cerrar conexiones
sqlite_conn.close()
pg_conn.close()

print()
print('✅ Conexiones cerradas')
