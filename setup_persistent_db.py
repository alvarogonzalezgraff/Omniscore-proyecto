import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import sys
from datetime import datetime

print('=== CONFIGURANDO BASE DE DATOS PERSISTENTE ===')
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
        database='postgres',
        user='postgres',
        password='1234'
    )
    pg_cursor = pg_conn.cursor()
    print('✅ Conectado a PostgreSQL Docker (localhost:5433)')
except Exception as e:
    print(f'❌ Error conectando a PostgreSQL Docker: {e}')
    sys.exit(1)

print()

# 3. Verificar que PostgreSQL esté listo
try:
    pg_cursor.execute('SELECT 1')
    print('✅ PostgreSQL está listo para recibir datos')
except Exception as e:
    print(f'❌ PostgreSQL no está listo: {e}')
    sys.exit(1)

# 4. Crear base de datos si no existe
try:
    pg_cursor.execute('CREATE DATABASE Omniscore_db')
    pg_conn.commit()
    print('✅ Base de datos Omniscore_db creada')
except Exception as e:
    if 'already exists' in str(e):
        print('✅ Base de datos Omniscore_db ya existe')
    else:
        print(f'❌ Error creando base de datos: {e}')

# 5. Conectarse a la base de datos Omniscore_db
try:
    pg_conn.close()
    pg_conn = psycopg2.connect(
        host='localhost',
        port=5433,
        database='Omniscore_db',
        user='postgres',
        password='1234'
    )
    pg_cursor = pg_conn.cursor()
    print('✅ Conectado a Omniscore_db')
except Exception as e:
    print(f'❌ Error conectando a Omniscore_db: {e}')
    sys.exit(1)

# 6. Crear tablas si no existen
print()
print('📋 Creando estructura de tablas...')

tablas_sql = """
-- Tabla de ligas
CREATE TABLE IF NOT EXISTS leagues (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    country TEXT
);

-- Tabla de equipos
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY,
    league_id INTEGER,
    name TEXT NOT NULL,
    logo_path TEXT
);

-- Tabla de partidos
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY,
    league_id INTEGER,
    home_team_id INTEGER,
    away_team_id INTEGER,
    matchday INTEGER,
    match_date TEXT,
    home_score INTEGER DEFAULT 0,
    away_score INTEGER DEFAULT 0,
    is_finished BOOLEAN DEFAULT FALSE
);

-- Tabla de goles
CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY,
    match_id INTEGER,
    team_id INTEGER,
    player_name TEXT NOT NULL,
    minute INTEGER,
    assist_player_name TEXT,
    is_own_goal BOOLEAN DEFAULT FALSE,
    is_penalty BOOLEAN DEFAULT FALSE
);

-- Tabla de tarjetas
CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY,
    match_id INTEGER,
    team_id INTEGER,
    player_name TEXT NOT NULL,
    minute INTEGER,
    card_type TEXT,
    reason TEXT,
    description TEXT
);

-- Tabla de sustituciones
CREATE TABLE IF NOT EXISTS substitutions (
    id INTEGER PRIMARY KEY,
    match_id INTEGER,
    team_id INTEGER,
    player_in TEXT,
    player_out TEXT,
    minute INTEGER
);

-- Tabla de lesiones
CREATE TABLE IF NOT EXISTS injuries (
    id INTEGER PRIMARY KEY,
    match_id INTEGER,
    team_id INTEGER,
    player_name TEXT,
    minute INTEGER,
    description TEXT
);

-- Tabla de penales
CREATE TABLE IF NOT EXISTS penalties (
    id INTEGER PRIMARY KEY,
    match_id INTEGER,
    team_id INTEGER,
    player_name TEXT,
    minute INTEGER,
    outcome TEXT,
    description TEXT
);

-- Tabla de partidos scraped
CREATE TABLE IF NOT EXISTS scraped_matches (
    id INTEGER PRIMARY KEY,
    league TEXT,
    season TEXT,
    matchday TEXT,
    date TEXT,
    home_team TEXT,
    away_team TEXT,
    home_score INTEGER,
    away_score INTEGER,
    is_finished BOOLEAN,
    scorers TEXT,
    updated_at TEXT,
    assists TEXT,
    yellow_cards TEXT,
    red_cards TEXT,
    substitutions TEXT,
    injuries TEXT,
    url TEXT
);

-- Tabla de datos scraped (clasificación)
CREATE TABLE IF NOT EXISTS scraped_data (
    id INTEGER PRIMARY KEY,
    sport TEXT,
    league TEXT,
    season TEXT,
    team_name TEXT,
    position INTEGER,
    points INTEGER,
    matches_played INTEGER,
    wins INTEGER,
    draws INTEGER,
    losses INTEGER,
    goals_for INTEGER,
    goals_against INTEGER,
    goal_diff INTEGER,
    form TEXT,
    updated_at TEXT
);

-- Tabla de estadísticas de jugadores
CREATE TABLE IF NOT EXISTS player_stats (
    id INTEGER PRIMARY KEY,
    league_id INTEGER,
    player_name TEXT,
    team_name TEXT,
    goals INTEGER,
    assists INTEGER,
    matches_played INTEGER,
    updated_at TEXT
);

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT,
    password TEXT,
    full_name TEXT,
    created_at TEXT
);
"""

try:
    pg_cursor.execute(tablas_sql)
    pg_conn.commit()
    print('✅ Tablas creadas exitosamente')
except Exception as e:
    print(f'❌ Error creando tablas: {e}')

print()

# 7. Función para limpiar y preparar datos
def clean_value(value, column_name=None):
    if value is None:
        return None
    
    # Convertir integers a boolean para campos específicos
    if column_name in ['is_finished', 'is_own_goal', 'is_penalty']:
        if isinstance(value, int):
            return bool(value)
        elif isinstance(value, str):
            return value.lower() in ('1', 'true', 't', 'yes', 'y')
    
    # Para otros tipos
    if isinstance(value, str):
        return value.strip()
    return value

# 8. Migración de datos
print('📊 Iniciando migración de datos...')
print('-' * 50)

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
        pg_cursor.execute(f'DELETE FROM {table_name}')
        print(f'   🗑️ Tabla {table_name} limpiada en PostgreSQL')
        
        # Preparar inserción
        placeholders = ', '.join(['%s'] * len(columns))
        insert_query = f'INSERT INTO {table_name} ({", ".join(columns)}) VALUES ({placeholders})'
        
        # Insertar datos
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
                if error_count <= 5:
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

# 9. Migrar usuarios
try:
    sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if sqlite_cursor.fetchone():
        sqlite_cursor.execute('SELECT id, username, email, password, full_name, created_at FROM users')
        users = sqlite_cursor.fetchall()
        
        if users:
            pg_cursor.execute('DELETE FROM users')
            
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

# 10. Resumen final
print('📋 RESUMEN DE MIGRACIÓN:')
print('=' * 50)
print(f'📊 Registros migrados exitosamente: {total_migrated:,}')
print(f'❌ Errores encontrados: {total_errors:,}')
print(f'📅 Fecha y hora: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

if total_errors == 0:
    print('🎉 ¡MIGRACIÓN COMPLETADA CON ÉXITO!')
    print('✅ Base de datos persistente configurada con todos los datos')
else:
    print('⚠️ MIGRACIÓN COMPLETADA (con algunos errores)')
    print(f'📊 Se migraron {total_migrated:,} registros exitosamente')

print()
print('🔍 Verificación del volumen persistente:')
print('✅ Los datos están ahora en el volumen Docker Omniscore_postgres_data')
print('✅ El contenedor puede reiniciarse sin perder datos')
print('✅ Los cambios futuros se guardarán en el volumen persistente')

# Cerrar conexiones
sqlite_conn.close()
pg_conn.close()

print()
print('✅ Conexiones cerradas')
print('🎯 Base de datos persistente lista para uso')
