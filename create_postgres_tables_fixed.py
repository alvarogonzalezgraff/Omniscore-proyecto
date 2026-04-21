import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor

print('=== CREANDO TABLAS EN POSTGRESQL DOCKER (CORREGIDO) ===')
print()

# 1. Conexión a SQLite (para obtener estructura)
sqlite_conn = sqlite3.connect('database/app.db')
sqlite_cursor = sqlite_conn.cursor()
print('✅ Conectado a SQLite para obtener estructura')

# 2. Conexión a PostgreSQL Docker
pg_conn = psycopg2.connect(
    host='localhost',
    port=5433,
    database='Omniscore_db',
    user='postgres',
    password='1234'
)
pg_cursor = pg_conn.cursor()
print('✅ Conectado a PostgreSQL Docker')

# Limpiar cualquier transacción pendiente
pg_conn.rollback()
print()

# 3. Función para convertir tipo SQLite a PostgreSQL
def sqlite_to_postgres_type(sqlite_type, table_name, column_name):
    sqlite_type = sqlite_type.upper()
    
    # Casos especiales para columnas conocidas
    if column_name == 'is_finished':
        return 'BOOLEAN'
    elif column_name == 'is_own_goal':
        return 'BOOLEAN'
    elif column_name == 'is_penalty':
        return 'BOOLEAN'
    elif column_name in ['is_createdb', 'usesuper', 'userepl', 'usebypassrls']:
        return 'BOOLEAN'
    
    # Conversión general
    if 'INTEGER' in sqlite_type or 'INT' in sqlite_type:
        return 'INTEGER'
    elif 'TEXT' in sqlite_type or 'VARCHAR' in sqlite_type or 'CHAR' in sqlite_type:
        return 'TEXT'
    elif 'REAL' in sqlite_type or 'FLOAT' in sqlite_type or 'DOUBLE' in sqlite_type:
        return 'REAL'
    elif 'BLOB' in sqlite_type:
        return 'BYTEA'
    elif 'BOOLEAN' in sqlite_type:
        return 'BOOLEAN'
    else:
        return 'TEXT'

# 4. Función para procesar valor por defecto
def process_default_value(default_val, pg_type, column_name):
    if default_val is None:
        return None
    
    # Casos especiales para booleanos
    if pg_type == 'BOOLEAN':
        if default_val == 0 or default_val == '0':
            return 'FALSE'
        elif default_val == 1 or default_val == '1':
            return 'TRUE'
        else:
            return str(default_val)
    
    # Para otros tipos
    if isinstance(default_val, str):
        if default_val.startswith("'") or default_val.startswith('"'):
            return default_val
        else:
            return f"'{default_val}'"
    
    return str(default_val)

# 5. Obtener y crear tablas
print('📋 CREANDO ESTRUCTURA DE TABLAS:')
print('-' * 50)

# Tablas principales a crear en orden lógico
tables_to_create = [
    'leagues', 'teams', 'matches', 'goals', 'cards', 
    'substitutions', 'injuries', 'penalties', 'scraped_matches',
    'scraped_data', 'player_stats', 'users',
    'basketball_leagues', 'basketball_seasons', 'basketball_teams',
    'basketball_matches', 'basketball_players', 'basketball_standings',
    'basketball_player_season_stats', 'tennis_tournaments', 
    'tennis_players', 'tennis_editions'
]

created_tables = 0
error_tables = 0

for table_name in tables_to_create:
    try:
        # Verificar si existe en SQLite
        sqlite_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if not sqlite_cursor.fetchone():
            print(f'⚠️ Tabla {table_name} no existe en SQLite - omitiendo')
            continue
        
        # Obtener estructura de la tabla
        sqlite_cursor.execute(f"PRAGMA table_info({table_name})")
        columns = sqlite_cursor.fetchall()
        
        if not columns:
            print(f'⚠️ Tabla {table_name} vacía en SQLite - omitiendo')
            continue
        
        print(f'📋 Creando tabla: {table_name}')
        
        # Construir CREATE TABLE
        create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
        
        primary_keys = []
        column_definitions = []
        
        for col in columns:
            col_id, col_name, col_type, not_null, default_val, is_pk = col
            
            pg_type = sqlite_to_postgres_type(col_type, table_name, col_name)
            
            # Construir definición de columna
            col_def = f'    {col_name} {pg_type}'
            
            if not_null == 1:
                col_def += ' NOT NULL'
            
            # Procesar valor por defecto
            processed_default = process_default_value(default_val, pg_type, col_name)
            if processed_default is not None:
                col_def += f' DEFAULT {processed_default}'
            
            if is_pk == 1:
                primary_keys.append(col_name)
            
            column_definitions.append(col_def)
        
        # Añadir clave primaria si existe
        if primary_keys:
            column_definitions.append(f'    PRIMARY KEY ({", ".join(primary_keys)})')
        
        create_sql += ',\n'.join(column_definitions)
        create_sql += '\n);'
        
        # Debug: mostrar SQL para tablas problemáticas
        if table_name in ['matches', 'goals', 'cards']:
            print(f'   🔍 SQL para {table_name}:')
            print(f'   {create_sql[:200]}...')
        
        # Ejecutar CREATE TABLE
        pg_cursor.execute(create_sql)
        pg_conn.commit()
        
        print(f'   ✅ Tabla {table_name} creada con {len(columns)} columnas')
        created_tables += 1
        
    except Exception as e:
        print(f'   ❌ Error creando tabla {table_name}: {e}')
        error_tables += 1
        # Rollback para limpiar transacción
        pg_conn.rollback()

print()

# 6. Confirmar creación de tablas
print('🔍 VERIFICANDO TABLAS CREADAS:')
print('-' * 50)

try:
    pg_cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
    pg_tables = [row[0] for row in pg_cursor.fetchall()]
    
    print(f'Tablas creadas en PostgreSQL: {len(pg_tables)}')
    for table in pg_tables:
        print(f'  ✅ {table}')
except Exception as e:
    print(f'❌ Error verificando tablas: {e}')

print()

# 7. Resumen
print('📋 RESUMEN DE CREACIÓN DE TABLAS:')
print('=' * 50)
print(f'✅ Tablas creadas exitosamente: {created_tables}')
print(f'❌ Errores: {error_tables}')

try:
    print(f'📊 Total tablas en PostgreSQL: {len(pg_tables)}')
except:
    print('📊 No se pudo verificar el total de tablas')

if created_tables > 0:
    print()
    print('🎉 ¡ESTRUCTURA DE BASE DE DATOS CREADA!')
    print('✅ Ahora puedes ejecutar la migración de datos')
    print('🔍 Ejecuta: python migrate_appdb_to_docker.py')
else:
    print()
    print('❌ No se pudieron crear tablas')
    print('🔍 Revisa los errores arriba')

# Cerrar conexiones
sqlite_conn.close()
pg_conn.close()
print()
print('✅ Conexiones cerradas')
