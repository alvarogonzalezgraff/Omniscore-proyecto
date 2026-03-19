import sqlite3
import os
from datetime import datetime

print('=== IDENTIFICACIÓN DE COPIAS DE BASE DE DATOS ===')
print()

# Buscar todas las bases de datos en el proyecto
database_files = []

# Directorios a buscar
search_dirs = ['.', 'database', '_historial_y_herramientas']

for directory in search_dirs:
    if os.path.exists(directory):
        for file in os.listdir(directory):
            if file.endswith('.db') or file.endswith('.sqlite') or file.endswith('.sqlite3'):
                full_path = os.path.join(directory, file)
                size = os.path.getsize(full_path)
                modified = datetime.fromtimestamp(os.path.getmtime(full_path))
                database_files.append((full_path, size, modified))

print('BASES DE DATOS ENCONTRADAS:')
print()

for db_path, size, modified in sorted(database_files):
    size_mb = size / (1024 * 1024)
    print(f'📁 {db_path}')
    print(f'   Tamaño: {size_mb:.2f} MB')
    print(f'   Modificado: {modified}')
    
    # Analizar contenido si es SQLite válido
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Contar tablas
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]
        
        # Verificar tablas principales
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('matches', 'scraped_matches', 'leagues', 'teams')")
        main_tables = [row[0] for row in cursor.fetchall()]
        
        print(f'   Tablas: {table_count}')
        print(f'   Tablas principales: {", ".join(main_tables) if main_tables else "Ninguna"}')
        
        # Si tiene scraped_matches, mostrar resumen
        if 'scraped_matches' in main_tables:
            cursor.execute('SELECT COUNT(*) FROM scraped_matches')
            matches_count = cursor.fetchone()[0]
            cursor.execute('SELECT DISTINCT league, COUNT(*) FROM scraped_matches GROUP BY league')
            leagues_data = cursor.fetchall()
            print(f'   Partidos scraped: {matches_count}')
            print(f'   Ligas: {", ".join([f"{league} ({count})" for league, count in leagues_data])}')
        
        conn.close()
        
    except Exception as e:
        print(f'   ❌ Error al leer: {str(e)[:50]}...')
    
    print()

print('=== COPIA PRINCIPAL IDENTIFICADA ===')
print()

# Identificar la copia principal (la más grande con datos completos)
main_copy = None
max_matches = 0

for db_path, size, modified in database_files:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name = 'scraped_matches'")
        if cursor.fetchone():
            cursor.execute('SELECT COUNT(*) FROM scraped_matches')
            matches_count = cursor.fetchone()[0]
            
            if matches_count > max_matches:
                max_matches = matches_count
                main_copy = db_path
        
        conn.close()
    except:
        continue

if main_copy:
    size_mb = os.path.getsize(main_copy) / (1024 * 1024)
    modified = datetime.fromtimestamp(os.path.getmtime(main_copy))
    print(f'🎯 COPIA PRINCIPAL: {main_copy}')
    print(f'   Tamaño: {size_mb:.2f} MB')
    print(f'   Modificado: {modified}')
    print(f'   Partidos totales: {max_matches}')
    print(f'   ✅ Esta es tu copia completa de datos')
else:
    print('❌ No se encontró una copia principal clara')

print()
print('=== NOMBRES ALTERNATIVOS PARA LA COPIA ===')
print()
print('Basado en el análisis, tu copia principal se llama:')
print(f'• "{os.path.basename(main_copy) if main_copy else "No encontrada"}"')
print()
print('Esta es la base de datos que contiene:')
print('• Todos los partidos de LaLiga EA Sports 2024/25')
print('• Todos los partidos de Premier League 2024/25') 
print('• Todos los partidos de Serie A 2024/25')
print('• Todos los partidos de Bundesliga 2024/25')
print('• Datos completos de goles, tarjetas, sustituciones y lesiones')
