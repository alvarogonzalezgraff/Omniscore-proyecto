#!/usr/bin/env python3
"""
Script de migración corregido para SQLite a PostgreSQL
"""
import sqlite3
from sqlalchemy import create_engine, text
from api.config import DATABASE_URL
import json

def convert_row_for_postgres(row, table_name):
    """Convierte una fila de SQLite al formato correcto para PostgreSQL"""
    if table_name == 'goals':
        # Convertir integers 0/1 a booleanos para is_own_goal e is_penalty
        return (
            row[0],  # id
            row[1],  # match_id
            row[2],  # team_id
            row[3],  # player_name
            row[4],  # minute
            row[5],  # assist_player_name
            bool(row[6]) if row[6] is not None else False,  # is_own_goal
            bool(row[7]) if row[7] is not None else False   # is_penalty
        )
    elif table_name == 'cards':
        return row  # No hay booleanos aquí
    elif table_name == 'substitutions':
        return row  # No hay booleanos aquí
    elif table_name == 'injuries':
        return row  # No hay booleanos aquí
    else:
        return row

def migrate_table_fixed(sqlite_conn, pg_engine, table_name):
    """Migra una tabla con conversión de tipos correcta"""
    
    try:
        # Obtener datos de SQLite
        cursor = sqlite_conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        if not rows:
            print(f"  {table_name}: Sin datos para migrar")
            return
        
        # Obtener nombres de columnas
        cursor.execute(f"PRAGMA table_info({table_name})")
        sqlite_columns = [col[1] for col in cursor.fetchall()]
        
        # Limpiar tabla en PostgreSQL primero
        with pg_engine.connect() as conn:
            try:
                conn.execute(text(f"DELETE FROM {table_name}"))
                conn.commit()
                print(f"  {table_name}: Tabla limpiada en PostgreSQL")
            except Exception as e:
                print(f"  {table_name}: Error limpiando tabla - {e}")
        
        # Insertar datos convertidos
        with pg_engine.connect() as conn:
            placeholders = ', '.join(['%s'] * len(sqlite_columns))
            insert_sql = f"INSERT INTO {table_name} ({', '.join(sqlite_columns)}) VALUES ({placeholders})"
            
            success_count = 0
            error_count = 0
            
            for row in rows:
                try:
                    # Convertir fila al formato correcto
                    converted_row = convert_row_for_postgres(row, table_name)
                    conn.execute(text(insert_sql), converted_row)
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    if error_count <= 5:  # Mostrar solo primeros 5 errores
                        print(f"    Error insertando fila {row[0]}: {e}")
            
            conn.commit()
        
        print(f"  ✅ {table_name}: {success_count} registros migrados, {error_count} errores")
        
    except Exception as e:
        print(f"  ❌ Error migrando {table_name}: {e}")

def main():
    print("=== MIGRACIÓN CORREGIDA DE SQLITE A POSTGRESQL ===")
    
    # Conexiones
    sqlite_conn = sqlite3.connect('database/app.db')
    pg_engine = create_engine(DATABASE_URL)
    
    try:
        # Probar conexión a PostgreSQL
        with pg_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Conexión a PostgreSQL establecida")
        
        # Tablas a migrar (solo las problemáticas)
        tables_to_migrate = ['goals', 'cards', 'substitutions', 'injuries']
        
        # Migrar cada tabla
        for table in tables_to_migrate:
            migrate_table_fixed(sqlite_conn, pg_engine, table)
        
        print("\n✅ Migración corregida completada")
        
        # Verificar datos migrados
        print("\n=== VERIFICACIÓN FINAL ===")
        with pg_engine.connect() as conn:
            for table in tables_to_migrate:
                try:
                    # Contar en PostgreSQL
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    pg_count = result.fetchone()[0]
                    
                    # Contar en SQLite
                    cursor = sqlite_conn.cursor()
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    sqlite_count = cursor.fetchone()[0]
                    
                    diff = sqlite_count - pg_count
                    status = "✅" if diff == 0 else "❌"
                    print(f"{status} {table}: SQLite={sqlite_count}, PostgreSQL={pg_count}, Diferencia={diff}")
                    
                except Exception as e:
                    print(f"  {table}: ❌ Error al verificar: {e}")
        
    except Exception as e:
        print(f"❌ Error en migración: {e}")
    finally:
        sqlite_conn.close()

if __name__ == "__main__":
    main()
