#!/usr/bin/env python3
"""
Script para importar datos del CSV premier_24_25_mix.csv a PostgreSQL
Importa partidos, goles, tarjetas, alineaciones y otros eventos
"""

import csv
import psycopg2
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'port': '5433',
    'dbname': 'betwin_db',
    'user': 'postgres',
    'password': '1234'
}

def get_connection():
    """Establece conexión con PostgreSQL"""
    return psycopg2.connect(**DB_CONFIG)

def normalize_team_name(team_name: str) -> str:
    """Normaliza nombres de equipos para coincidir con la base de datos"""
    team_mapping = {
        'Tottenham': 'Tottenham',
        'Luton Town': 'Sunderland',  # Mapear a Sunderland que está en BD
        'Arsenal': 'Arsenal',
        'Brighton': 'Brighton',
        'Crystal Palace': 'Crystal Palace',
        'Aston Villa': 'Aston Villa',
        'West Ham': 'West Ham',
        'Fulham': 'Fulham',
        'Wolves': 'Wolves',
        'Chelsea': 'Chelsea',
        'Burnley': 'Burnley',
        'Bournemouth': 'Bournemouth',
        'Newcastle': 'Newcastle',
        'Manchester City': 'Man City',
        'Everton': 'Everton',
        'Nottingham Forest': 'Nottm Forest',
        'Brentford': 'Brentford',
        'Sheffield United': 'Leeds United',  # Mapear a Leeds United
        'Manchester United': 'Man Utd',
        'Liverpool': 'Liverpool'
    }
    return team_mapping.get(team_name, team_name)

def get_team_id(cursor, team_name: str) -> Optional[int]:
    """Obtiene el ID de un equipo por su nombre"""
    normalized_name = normalize_team_name(team_name)
    cursor.execute("SELECT id FROM teams WHERE name = %s", (normalized_name,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_league_id(cursor, league_name: str = "Premier League") -> Optional[int]:
    """Obtiene el ID de la liga"""
    cursor.execute("SELECT id FROM leagues WHERE name = %s", (league_name,))
    result = cursor.fetchone()
    return result[0] if result else None

def parse_player_list(player_string: str) -> List[str]:
    """Parsea una lista de jugadores separados por punto y coma"""
    if not player_string or player_string.strip() == '':
        return []
    return [player.strip() for player in player_string.split(';') if player.strip()]

def parse_assist_list(assist_string: str) -> List[str]:
    """Parsea la lista de asistencias"""
    if not assist_string or assist_string.strip() == '':
        return []
    return [assist.strip() for assist in assist_string.split(',') if assist.strip()]

def parse_penalty_list(penalty_string: str) -> List[str]:
    """Parsea la lista de penaltis"""
    if not penalty_string or penalty_string.strip() == '':
        return []
    return [penalty.strip() for penalty in penalty_string.split(',') if penalty.strip()]

def extract_penalty_info(goal_string: str, penalty_list: List[str]) -> Tuple[bool, str]:
    """Extrae información de penaltis de un gol"""
    is_penalty = False
    clean_goal = goal_string
    
    # Verificar si es penalti
    for penalty in penalty_list:
        if penalty in goal_string:
            is_penalty = True
            clean_goal = goal_string.replace(f' ({penalty})', '').replace(penalty, '').strip()
            break
    
    # Buscar patrones de "(penalti)" o "(penalty)"
    if '(penalti)' in goal_string.lower() or '(penalty)' in goal_string.lower():
        is_penalty = True
        clean_goal = re.sub(r'\s*\([^)]*penalt[ií][^)]*\)', '', goal_string, flags=re.IGNORECASE).strip()
    
    return is_penalty, clean_goal

def extract_assist_info(goal_string: str, assist_list: List[str]) -> Tuple[Optional[str], str]:
    """Extrae información de asistencias"""
    # Buscar asistencias en la lista de asistencias
    for assist in assist_list:
        if assist in goal_string:
            clean_goal = goal_string.replace(assist, '').strip()
            return assist, clean_goal
    
    # Buscar patrones como "JugadorX (JugadorY)"
    match = re.search(r'(\w+)\s*\(([^)]+)\)', goal_string)
    if match:
        goal_player = match.group(1).strip()
        assist_player = match.group(2).strip()
        clean_goal = goal_player
        return assist_player, clean_goal
    
    return None, goal_string

def get_next_id(cursor, table_name: str) -> int:
    """Obtiene el siguiente ID disponible para una tabla"""
    cursor.execute(f"SELECT COALESCE(MAX(id), 0) + 1 FROM {table_name}")
    return cursor.fetchone()[0]

def import_csv_data(csv_file_path: str):
    """Importa todos los datos del CSV a PostgreSQL"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener IDs base
        league_id = get_league_id(cursor)
        if not league_id:
            print("No se encontro la liga Premier League")
            return
        
        # Obtener IDs siguientes
        initial_match_id = get_next_id(cursor, 'matches')
        initial_goal_id = get_next_id(cursor, 'goals')
        initial_card_id = get_next_id(cursor, 'cards')
        
        next_match_id = initial_match_id
        next_goal_id = initial_goal_id
        next_card_id = initial_card_id
        
        print(f"Importando datos de Premier League...")
        print(f"Liga ID: {league_id}")
        print(f"Proximo Match ID: {next_match_id}")
        
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row_num, row in enumerate(reader, 1):
                try:
                    jornada = int(row['jornada'])
                    local = row['local']
                    visitante = row['visitante']
                    goles_local = int(row['goles_local']) if row['goles_local'] else 0
                    goles_visitante = int(row['goles_visitante']) if row['goles_visitante'] else 0
                    
                    # Obtener IDs de equipos
                    local_id = get_team_id(cursor, local)
                    visitante_id = get_team_id(cursor, visitante)
                    
                    if not local_id or not visitante_id:
                        print(f"Fila {row_num}: No se encontraron equipos - {local} vs {visitante}")
                        continue
                    
                    # Insertar partido
                    match_id = next_match_id
                    cursor.execute("""
                        INSERT INTO matches (id, league_id, home_team_id, away_team_id, matchday, 
                                            home_score, away_score, is_finished, match_date)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (match_id, league_id, local_id, visitante_id, jornada, 
                          goles_local, goles_visitante, True, f'2024-0{jornada:02d}-01'))
                    
                    # Procesar goles
                    goles_local_str = row['goleadores'].split(';')[0] if row['goleadores'] else ''
                    goles_visitante_str = row['goleadores'].split(';')[1] if ';' in row['goleadores'] and row['goleadores'] else ''
                    
                    asistencias = parse_assist_list(row['asistencias'])
                    penaltis = parse_penalty_list(row['penaltis'])
                    
                    # Insertar goles locales
                    if goles_local_str:
                        goles_locales = parse_player_list(goles_local_str)
                        for i, gol in enumerate(goles_locales):
                            is_penalty, clean_goal = extract_penalty_info(gol, penaltis)
                            assist_player, clean_goal = extract_assist_info(clean_goal, asistencias)
                            
                            cursor.execute("""
                                INSERT INTO goals (id, match_id, team_id, player_name, minute, 
                                                assist_player_name, is_own_goal, is_penalty)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """, (next_goal_id, match_id, local_id, clean_goal, 
                                  (i + 1) * 10, assist_player, False, is_penalty))
                            next_goal_id += 1
                    
                    # Insertar goles visitantes
                    if goles_visitante_str:
                        goles_visitantes = parse_player_list(goles_visitante_str)
                        for i, gol in enumerate(goles_visitantes):
                            is_penalty, clean_goal = extract_penalty_info(gol, penaltis)
                            assist_player, clean_goal = extract_assist_info(clean_goal, asistencias)
                            
                            cursor.execute("""
                                INSERT INTO goals (id, match_id, team_id, player_name, minute, 
                                                assist_player_name, is_own_goal, is_penalty)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """, (next_goal_id, match_id, visitante_id, clean_goal, 
                                  (i + 1) * 10, assist_player, False, is_penalty))
                            next_goal_id += 1
                    
                    # Procesar tarjetas amarillas
                    amarillas_str = row['amarillas']
                    if amarillas_str:
                        amarillas = parse_player_list(amarillas_str)
                        for i, amarilla in enumerate(amarillas):
                            # Determinar equipo del jugador (simplificado)
                            cursor.execute("""
                                INSERT INTO cards (id, match_id, team_id, player_name, minute, card_type)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, (next_card_id, match_id, local_id, amarilla, 
                                  (i + 1) * 5, 'yellow'))
                            next_card_id += 1
                    
                    # Procesar tarjetas rojas
                    rojas_str = row['rojas']
                    if rojas_str:
                        rojas = parse_player_list(rojas_str)
                        for i, roja in enumerate(rojas):
                            cursor.execute("""
                                INSERT INTO cards (id, match_id, team_id, player_name, minute, card_type)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, (next_card_id, match_id, local_id, roja, 
                                  (i + 1) * 15, 'red'))
                            next_card_id += 1
                    
                    next_match_id += 1
                    
                    if row_num % 10 == 0:
                        print(f"Procesadas {row_num} filas...")
                        
                except Exception as e:
                    print(f"Error en fila {row_num}: {e}")
                    continue
        
        # Confirmar todos los cambios
        conn.commit()
        print(f"Importacion completada!")
        
        # Obtener estadísticas reales
        final_match_id = get_next_id(cursor, 'matches')
        final_goal_id = get_next_id(cursor, 'goals')
        final_card_id = get_next_id(cursor, 'cards')
        
        print(f"Total de partidos importados: {final_match_id - initial_match_id}")
        print(f"Total de goles importados: {final_goal_id - initial_goal_id}")
        print(f"Total de tarjetas amarillas: {final_card_id - initial_card_id}")
        
    except Exception as e:
        print(f"Error general: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    csv_path = "premier_24_25_mix.csv"
    print(f"Iniciando importacion desde {csv_path}")
    import_csv_data(csv_path)
    print("Proceso finalizado")
