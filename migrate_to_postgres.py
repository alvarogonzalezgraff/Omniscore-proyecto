#!/usr/bin/env python3
"""
Script para migrar datos de SQLite a PostgreSQL
"""
import sqlite3
import os
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import sys

# Importar configuración
from api.config import DATABASE_URL

def get_sqlite_connection():
    """Conexión a la base de datos SQLite"""
    return sqlite3.connect('database/app.db')

def get_postgres_engine():
    """Motor de conexión a PostgreSQL"""
    return create_engine(DATABASE_URL)

def create_postgres_tables(engine):
    """Crea las tablas en PostgreSQL si no existen"""
    
    # Definición de tablas principales
    tables_sql = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            full_name VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        """
        CREATE TABLE IF NOT EXISTS leagues (
            id INTEGER PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            country VARCHAR(50)
        )
        """,
        
        """
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY,
            league_id INTEGER REFERENCES leagues(id),
            name VARCHAR(100) NOT NULL,
            logo_path VARCHAR(255)
        )
        """,
        
        """
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY,
            league_id INTEGER REFERENCES leagues(id),
            home_team_id INTEGER REFERENCES teams(id),
            away_team_id INTEGER REFERENCES teams(id),
            matchday INTEGER,
            match_date TIMESTAMP,
            home_score INTEGER,
            away_score INTEGER,
            is_finished BOOLEAN DEFAULT FALSE
        )
        """,
        
        """
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY,
            match_id INTEGER REFERENCES matches(id),
            team_id INTEGER REFERENCES teams(id),
            player_name VARCHAR(100),
            minute INTEGER,
            assist_player_name VARCHAR(100),
            is_own_goal BOOLEAN DEFAULT FALSE,
            is_penalty BOOLEAN DEFAULT FALSE
        )
        """,
        
        """
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY,
            match_id INTEGER REFERENCES matches(id),
            team_id INTEGER REFERENCES teams(id),
            player_name VARCHAR(100),
            minute INTEGER,
            card_type VARCHAR(20),
            reason VARCHAR(255),
            description TEXT
        )
        """,
        
        """
        CREATE TABLE IF NOT EXISTS substitutions (
            id INTEGER PRIMARY KEY,
            match_id INTEGER REFERENCES matches(id),
            team_id INTEGER REFERENCES teams(id),
            player_in VARCHAR(100),
            player_out VARCHAR(100),
            minute INTEGER
        )
        """,
        
        """
        CREATE TABLE IF NOT EXISTS injuries (
            id INTEGER PRIMARY KEY,
            match_id INTEGER REFERENCES matches(id),
            team_id INTEGER REFERENCES teams(id),
            player_name VARCHAR(100),
            minute INTEGER,
            description TEXT
        )
        """,
        
        """
        CREATE TABLE IF NOT EXISTS penalties (
            id INTEGER PRIMARY KEY,
            match_id INTEGER REFERENCES matches(id),
            team_id INTEGER REFERENCES teams(id),
            player_name VARCHAR(100),
            minute INTEGER,
            outcome VARCHAR(50),
            description TEXT
        )
        """,
        
        """
        CREATE TABLE IF NOT EXISTS scraped_data (
            id INTEGER PRIMARY KEY,
            sport VARCHAR(50),
            league VARCHAR(100),
            season VARCHAR(20),
            team_name VARCHAR(100),
            position INTEGER,
            points INTEGER,
            matches_played INTEGER,
            wins INTEGER,
            draws INTEGER,
            losses INTEGER,
            goals_for INTEGER,
            goals_against INTEGER,
            goal_diff INTEGER,
            form VARCHAR(50),
            updated_at TIMESTAMP
        )
        """,
        
        """
        CREATE TABLE IF NOT EXISTS player_stats (
            id INTEGER PRIMARY KEY,
            league_id INTEGER REFERENCES leagues(id),
            player_name VARCHAR(100),
            team_name VARCHAR(100),
            goals INTEGER DEFAULT 0,
            assists INTEGER DEFAULT 0,
            matches_played INTEGER DEFAULT 0,
            updated_at TIMESTAMP
        )
        """,
        
        """
        CREATE TABLE IF NOT EXISTS scraped_matches (
            id INTEGER PRIMARY KEY,
            league VARCHAR(100),
            season VARCHAR(20),
            matchday VARCHAR(50),
            date DATE,
            home_team VARCHAR(100),
            away_team VARCHAR(100),
            home_score INTEGER,
            away_score INTEGER,
            is_finished BOOLEAN DEFAULT FALSE,
            scorers TEXT,
            updated_at TIMESTAMP,
            assists TEXT,
            yellow_cards TEXT,
            red_cards TEXT,
            substitutions TEXT,
            injuries TEXT,
            url TEXT
        )
        """
    ]
    
    with engine.connect() as conn:
        for table_sql in tables_sql:
            try:
                conn.execute(text(table_sql))
                conn.commit()
            except Exception as e:
                print(f"⚠️ Error al crear tabla: {e}")
    
    print("✅ Tablas creadas en PostgreSQL")

def migrate_table(sqlite_conn, pg_engine, table_name, columns_map=None):
    """Migra una tabla específica de SQLite a PostgreSQL"""
    
    if columns_map is None:
        columns_map = {}
    
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
        
        # Mapear columnas si es necesario
        pg_columns = [columns_map.get(col, col) for col in sqlite_columns]
        
        # Insertar en PostgreSQL
        with pg_engine.connect() as conn:
            placeholders = ', '.join(['%s'] * len(pg_columns))
            insert_sql = f"INSERT INTO {table_name} ({', '.join(pg_columns)}) VALUES ({placeholders})"
            
            for row in rows:
                try:
                    conn.execute(text(insert_sql), row)
                except Exception as e:
                    print(f"    ⚠️ Error insertando fila en {table_name}: {e}")
                    continue
            
            conn.commit()
        
        print(f"  ✅ {table_name}: {len(rows)} registros migrados")
        
    except Exception as e:
        print(f"  ❌ Error migrando {table_name}: {e}")

def main():
    print("=== MIGRACIÓN DE SQLITE A POSTGRESQL ===")
    
    # Verificar que SQLite existe
    if not os.path.exists('database/app.db'):
        print("❌ Base de datos SQLite no encontrada")
        return
    
    # Conexiones
    sqlite_conn = get_sqlite_connection()
    pg_engine = get_postgres_engine()
    
    try:
        # Probar conexión a PostgreSQL
        with pg_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Conexión a PostgreSQL establecida")
        
        # Crear tablas
        create_postgres_tables(pg_engine)
        
        # Tablas a migrar (en orden de dependencia)
        tables_to_migrate = [
            'users',
            'leagues', 
            'teams',
            'matches',
            'goals',
            'cards',
            'substitutions',
            'injuries',
            'penalties',
            'scraped_data',
            'player_stats',
            'scraped_matches'
        ]
        
        # Migrar cada tabla
        for table in tables_to_migrate:
            migrate_table(sqlite_conn, pg_engine, table)
        
        print("\n✅ Migración completada")
        
        # Verificar datos migrados
        print("\n=== VERIFICACIÓN DE DATOS ===")
        with pg_engine.connect() as conn:
            for table in tables_to_migrate:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.fetchone()[0]
                    print(f"  {table}: {count} registros")
                except Exception as e:
                    print(f"  {table}: ❌ Error al verificar: {e}")
        
    except Exception as e:
        print(f"❌ Error en migración: {e}")
    finally:
        sqlite_conn.close()

if __name__ == "__main__":
    main()
