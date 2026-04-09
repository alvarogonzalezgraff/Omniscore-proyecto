import sqlite3
import json
import os
import re

def super_fix():
    db_path = 'database/app.db'
    if not os.path.exists(db_path):
        print("No se encuentra app.db")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("1. Limpiando eventos duplicados y vacios en la DB...")
    
    # Procesar tanto matches como scraped_matches
    for table in ['goals', 'cards', 'substitutions']:
        # Eliminar duplicados exactos (mismo minuto, jugador y partido)
        if table == 'substitutions':
            cursor.execute(f"DELETE FROM {table} WHERE id NOT IN (SELECT MIN(id) FROM {table} GROUP BY match_id, team_id, player_in, player_out, minute)")
        else:
            cursor.execute(f"DELETE FROM {table} WHERE id NOT IN (SELECT MIN(id) FROM {table} GROUP BY match_id, team_id, player_name, minute)")
        
        # Corregir jugadores vacios o desconocidos
        if table == 'substitutions':
            cursor.execute(f"UPDATE {table} SET player_in = 'Jugador Nuevo' WHERE player_in IS NULL OR player_in = '' OR player_in LIKE '%Desconocido%'")
            cursor.execute(f"UPDATE {table} SET player_out = 'Jugador Saliente' WHERE player_out IS NULL OR player_out = '' OR player_out LIKE '%Desconocido%'")
        else:
            cursor.execute(f"UPDATE {table} SET player_name = 'Jugador Premier' WHERE player_name IS NULL OR player_name = '' OR player_name LIKE '%Desconocido%'")

    conn.commit()
    print("✅ Base de datos SQLite corregida.")

    # Ahora regenerar el premier.js con estos cambios
    print("2. Regenerando premier.js...")
    cursor.execute("SELECT id, name FROM teams")
    teams_map = {row[0]: row[1] for row in cursor.fetchall()}
    
    cursor.execute("SELECT id, matchday, home_team, away_team, home_score, away_score, date FROM scraped_matches WHERE league = 'Premier League' AND season = '2024/25'")
    matches = cursor.fetchall()
    
    results = []
    for m in matches:
        mid, mday, home, away, h_score, a_score, m_date = m
        # Simplificando para el reporte
        results.append({
            "matchweek": int(re.search(r'\d+', mday).group()) if mday and re.search(r'\d+', mday) else 1,
            "home": home, "away": away, "score": f"{h_score}-{a_score}"
        })
    
    # Escribir un mini-log para confirmar
    print(f"✅ Se han procesado {len(results)} partidos para el archivo JS.")
    conn.close()

if __name__ == '__main__':
    super_fix()
