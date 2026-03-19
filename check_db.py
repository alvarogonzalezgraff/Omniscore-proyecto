#!/usr/bin/env python3
import sqlite3
import os

def check_sqlite_db():
    """Verifica la base de datos SQLite original"""
    db_path = 'database/app.db'
    
    if not os.path.exists(db_path):
        print(f"❌ La base de datos {db_path} no existe")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Obtener todas las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("=== BASE DE DATOS SQLITE ORIGINAL ===")
        print(f"Tablas encontradas: {len(tables)}")
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  {table_name}: {count} registros")
            
            # Mostrar algunos datos de ejemplo para cada tabla
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            rows = cursor.fetchall()
            if rows:
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [col[1] for col in cursor.fetchall()]
                print(f"    Columnas: {columns}")
                print(f"    Ejemplo: {rows[0]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error al leer SQLite: {e}")

def check_postgres_connection():
    """Verifica la conexión a PostgreSQL"""
    try:
        from api.config import DATABASE_URL
        from sqlalchemy import create_engine, text
        
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Obtener tablas
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = result.fetchall()
            
            print("\n=== BASE DE DATOS POSTGRESQL ===")
            print(f"Tablas encontradas: {len(tables)}")
            
            for table in tables:
                table_name = table[0]
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = result.fetchone()[0]
                    print(f"  {table_name}: {count} registros")
                    
                    # Mostrar estructura de la tabla
                    result = conn.execute(text(f"""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = '{table_name}'
                        ORDER BY ordinal_position
                    """))
                    columns = result.fetchall()
                    if columns:
                        print(f"    Columnas: {[col[0] for col in columns]}")
                    
                    # Mostrar un ejemplo
                    result = conn.execute(text(f"SELECT * FROM {table_name} LIMIT 1"))
                    row = result.fetchone()
                    if row:
                        print(f"    Ejemplo: {row}")
                        
                except Exception as e:
                    print(f"  {table_name}: ❌ Error al consultar: {e}")
            
        print("\n✅ Conexión a PostgreSQL exitosa")
        return True
        
    except Exception as e:
        print(f"\n❌ Error de conexión a PostgreSQL: {e}")
        return False

if __name__ == "__main__":
    check_sqlite_db()
    check_postgres_connection()
