#!/usr/bin/env python3
"""
Script para mostrar los goles de la jornada 1 de Premier League
desde la base de datos Docker PostgreSQL
"""

import psycopg2
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_premier_league_j1_goals():
    """Obtener todos los goles de la jornada 1 de Premier League"""
    
    # Conexión a la base de datos Docker
    conn = psycopg2.connect(
        host="localhost",
        port="5433",
        database="Omniscore_db",
        user="postgres",
        password="docker_password"
    )
    
    cursor = conn.cursor()
    
    try:
        # Query para obtener goles de jornada 1
        query = """
        SELECT 
            m.id as match_id,
            t1.name as home_team,
            t2.name as away_team,
            m.home_score,
            m.away_score,
            m.match_date,
            t3.name as scoring_team,
            g.player_name,
            g.minute,
            g.assist_player_name,
            g.is_penalty,
            g.is_own_goal
        FROM matches m
        JOIN teams t1 ON m.home_team_id = t1.id
        JOIN teams t2 ON m.away_team_id = t2.id
        JOIN goals g ON m.id = g.match_id
        JOIN teams t3 ON g.team_id = t3.id
        WHERE m.league_id = (SELECT id FROM leagues WHERE name = 'Premier League')
        AND m.matchday = 1
        ORDER BY m.match_date, m.id, g.minute
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        return results
        
    finally:
        cursor.close()
        conn.close()

def display_goals():
    """Mostrar los goles de forma organizada"""
    
    goals = get_premier_league_j1_goals()
    
    if not goals:
        print("No se encontraron goles para la jornada 1 de Premier League")
        return
    
    print("=" * 80)
    print("GOLES JORNADA 1 - PREMIER LEAGUE")
    print("=" * 80)
    
    current_match = None
    
    for goal in goals:
        match_id = goal[0]
        home_team = goal[1]
        away_team = goal[2]
        home_score = goal[3]
        away_score = goal[4]
        match_date = goal[5]
        scoring_team = goal[6]
        player_name = goal[7]
        minute = goal[8]
        assist = goal[9]
        is_penalty = goal[10]
        is_own_goal = goal[11]
        
        # Mostrar información del partido solo una vez
        if current_match != match_id:
            print(f"\n{home_team} {home_score} - {away_score} {away_team}")
            print(f"Fecha: {match_date.strftime('%Y-%m-%d')}")
            print("-" * 50)
            current_match = match_id
        
        # Mostrar información del gol
        goal_type = ""
        if is_penalty:
            goal_type = " (PEN)"
        elif is_own_goal:
            goal_type = " (EN PUERTA PROPIA)"
        
        assist_text = f" (Asistencia: {assist})" if assist else ""
        
        print(f"  {minute}' - {scoring_team}: {player_name}{goal_type}{assist_text}")

def save_to_database():
    """Guardar los datos en un formato estructurado para fácil acceso"""
    
    goals = get_premier_league_j1_goals()
    
    # Conexión para guardar datos procesados
    conn = psycopg2.connect(
        host="localhost",
        port="5433",
        database="Omniscore_db",
        user="postgres",
        password="docker_password"
    )
    
    cursor = conn.cursor()
    
    try:
        # Crear tabla si no existe para guardar goles estructurados
        create_table_query = """
        CREATE TABLE IF NOT EXISTS premier_j1_goals_summary (
            id SERIAL PRIMARY KEY,
            match_id INTEGER,
            home_team VARCHAR(255),
            away_team VARCHAR(255),
            home_score INTEGER,
            away_score INTEGER,
            match_date TIMESTAMP,
            scoring_team VARCHAR(255),
            player_name VARCHAR(255),
            minute INTEGER,
            assist_player_name VARCHAR(255),
            is_penalty BOOLEAN DEFAULT FALSE,
            is_own_goal BOOLEAN DEFAULT FALSE,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        cursor.execute(create_table_query)
        
        # Limpiar datos anteriores
        cursor.execute("DELETE FROM premier_j1_goals_summary")
        
        # Insertar datos actuales
        insert_query = """
        INSERT INTO premier_j1_goals_summary 
        (match_id, home_team, away_team, home_score, away_score, match_date, 
         scoring_team, player_name, minute, assist_player_name, is_penalty, is_own_goal)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.executemany(insert_query, goals)
        conn.commit()
        
        print(f"Se han guardado {len(goals)} goles en la tabla premier_j1_goals_summary")
        
    except Exception as e:
        conn.rollback()
        print(f"Error al guardar datos: {e}")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Obteniendo goles de la jornada 1 de Premier League...")
    
    # Mostrar goles
    display_goals()
    
    # Guardar en base de datos
    print("\nGuardando datos en base de datos...")
    save_to_database()
    
    print("\nProceso completado!")
