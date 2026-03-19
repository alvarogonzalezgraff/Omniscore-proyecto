import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

# Conexión a base de datos local
def get_local_connection():
    ROOT_DIR = Path(__file__).resolve().parent
    load_dotenv(ROOT_DIR / ".env")
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        dbname=os.getenv('DB_NAME', 'betwin_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', '')
    )

# Conexión a Docker PostgreSQL
def get_docker_connection():
    return psycopg2.connect(
        host='localhost',
        port='5433',
        dbname='betwin_db',
        user='postgres',
        password='docker_password'
    )

def check_all_premier_league():
    try:
        # Conectar a base de datos local
        local_conn = get_local_connection()
        local_cursor = local_conn.cursor()
        
        # Obtener ID de Premier League
        local_cursor.execute("SELECT id FROM leagues WHERE name = 'Premier League'")
        premier_result = local_cursor.fetchone()
        
        if not premier_result:
            print("❌ No se encontró la Premier League en la base de datos local")
            return
        
        premier_league_id = premier_result[0]
        
        # Obtener todos los partidos de Premier League
        local_cursor.execute('''
            SELECT m.id, t1.name as home_team, t2.name as away_team, 
                   m.home_score, m.away_score, m.matchday, m.match_date
            FROM matches m
            JOIN teams t1 ON m.home_team_id = t1.id
            JOIN teams t2 ON m.away_team_id = t2.id
            WHERE m.league_id = %s
            ORDER BY m.matchday, t1.name
        ''', (premier_league_id,))
        
        matches = local_cursor.fetchall()
        
        print(f'=== ANÁLISIS COMPLETO PREMIER LEAGUE ===')
        print(f'Total partidos encontrados: {len(matches)}')
        print()
        
        # Estadísticas generales
        total_matches = len(matches)
        matches_with_goals = 0
        matches_with_yellow_cards = 0
        matches_with_substitutions = 0
        total_goals = 0
        total_yellow_cards = 0
        total_substitutions = 0
        
        # Agrupar por jornada
        matchdays = {}
        for match in matches:
            match_id, home_team, away_team, home_score, away_score, matchday, match_date = match
            if matchday not in matchdays:
                matchdays[matchday] = []
            matchdays[matchday].append(match)
        
        print(f'Jornadas encontradas: {sorted(matchdays.keys())}')
        print()
        
        # Analizar cada jornada
        for jornada_num in sorted(matchdays.keys()):
            jornada_matches = matchdays[jornada_num]
            print(f'=== JORNADA {jornada_num} ===')
            print(f'Partidos: {len(jornada_matches)}')
            
            jornada_goals = 0
            jornada_yellow_cards = 0
            jornada_substitutions = 0
            jornada_matches_with_goals = 0
            jornada_matches_with_yellow_cards = 0
            jornada_matches_with_substitutions = 0
            
            for match in jornada_matches:
                match_id, home_team, away_team, home_score, away_score, matchday, match_date = match
                
                # Contar goles
                local_cursor.execute('SELECT COUNT(*) FROM goals WHERE match_id = %s', (match_id,))
                goals_count = local_cursor.fetchone()[0]
                if goals_count > 0:
                    jornada_matches_with_goals += 1
                    matches_with_goals += 1
                    total_goals += goals_count
                jornada_goals += goals_count
                
                # Contar tarjetas amarillas
                local_cursor.execute("SELECT COUNT(*) FROM cards WHERE match_id = %s AND card_type = 'Amarilla'", (match_id,))
                yellow_cards_count = local_cursor.fetchone()[0]
                if yellow_cards_count > 0:
                    jornada_matches_with_yellow_cards += 1
                    matches_with_yellow_cards += 1
                    total_yellow_cards += yellow_cards_count
                jornada_yellow_cards += yellow_cards_count
                
                # Contar cambios
                local_cursor.execute('SELECT COUNT(*) FROM substitutions WHERE match_id = %s', (match_id,))
                subs_count = local_cursor.fetchone()[0]
                if subs_count > 0:
                    jornada_matches_with_substitutions += 1
                    matches_with_substitutions += 1
                    total_substitutions += subs_count
                jornada_substitutions += subs_count
            
            print(f'  Goles: {jornada_goals} ({jornada_matches_with_goals}/{len(jornada_matches)} partidos)')
            print(f'  Tarjetas amarillas: {jornada_yellow_cards} ({jornada_matches_with_yellow_cards}/{len(jornada_matches)} partidos)')
            print(f'  Cambios: {jornada_substitutions} ({jornada_matches_with_substitutions}/{len(jornada_matches)} partidos)')
            print()
        
        print(f'=== RESUMEN GENERAL PREMIER LEAGUE ===')
        print(f'Total partidos: {total_matches}')
        print(f'Partidos con goles: {matches_with_goals} ({matches_with_goals/total_matches*100:.1f}%)')
        print(f'Partidos con tarjetas amarillas: {matches_with_yellow_cards} ({matches_with_yellow_cards/total_matches*100:.1f}%)')
        print(f'Partidos con cambios: {matches_with_substitutions} ({matches_with_substitutions/total_matches*100:.1f}%)')
        print(f'Total goles: {total_goals}')
        print(f'Total tarjetas amarillas: {total_yellow_cards}')
        print(f'Total cambios: {total_substitutions}')
        print()
        
        local_conn.close()
        return matches, premier_league_id
        
    except Exception as e:
        print(f'❌ Error: {e}')
        return None, None

def save_all_to_docker(matches, premier_league_id):
    try:
        # Conectar a base de datos local para obtener datos
        local_conn = get_local_connection()
        local_cursor = local_conn.cursor()
        
        # Conectar a Docker
        docker_conn = get_docker_connection()
        docker_cursor = docker_conn.cursor()
        
        print(f'=== GUARDANDO TODA LA PREMIER LEAGUE EN DOCKER ===')
        print(f'Total partidos a procesar: {len(matches)}')
        print()
        
        # Limpiar datos existentes de Premier League en Docker
        print('Limpiando datos existentes en Docker...')
        
        # Obtener match_ids de Premier League en Docker
        docker_cursor.execute('''
            SELECT m.id FROM matches m
            WHERE m.league_id = (SELECT id FROM leagues WHERE name = 'Premier League')
        ''')
        docker_match_ids = [row[0] for row in docker_cursor.fetchall()]
        
        # Eliminar datos relacionados
        if docker_match_ids:
            placeholders = ','.join(['%s'] * len(docker_match_ids))
            docker_cursor.execute(f'DELETE FROM goals WHERE match_id IN ({placeholders})', docker_match_ids)
            docker_cursor.execute(f'DELETE FROM cards WHERE match_id IN ({placeholders})', docker_match_ids)
            docker_cursor.execute(f'DELETE FROM substitutions WHERE match_id IN ({placeholders})', docker_match_ids)
            docker_cursor.execute(f'DELETE FROM injuries WHERE match_id IN ({placeholders})', docker_match_ids)
            print(f'Eliminados datos de {len(docker_match_ids)} partidos existentes')
        
        # Guardar todos los partidos y datos
        total_goals_saved = 0
        total_yellow_cards_saved = 0
        total_substitutions_saved = 0
        
        for i, match in enumerate(matches, 1):
            match_id, home_team, away_team, home_score, away_score, matchday, match_date = match
            
            if i % 10 == 0 or i == len(matches):
                print(f'Procesando partido {i}/{len(matches)}...')
            
            # Obtener y guardar goles
            local_cursor.execute('SELECT player_name, minute, assist_player_name, is_own_goal, is_penalty, team_id FROM goals WHERE match_id = %s', (match_id,))
            goals_data = local_cursor.fetchall()
            
            for goal in goals_data:
                player_name, minute, assist_player_name, is_own_goal, is_penalty, team_id = goal
                docker_cursor.execute('''
                    INSERT INTO goals (match_id, team_id, player_name, minute, assist_player_name, is_own_goal, is_penalty)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (match_id, team_id, player_name, minute, assist_player_name, is_own_goal, is_penalty))
                total_goals_saved += 1
            
            # Obtener y guardar tarjetas
            local_cursor.execute('SELECT player_name, minute, card_type, reason, team_id FROM cards WHERE match_id = %s', (match_id,))
            cards_data = local_cursor.fetchall()
            
            for card in cards_data:
                player_name, minute, card_type, reason, team_id = card
                docker_cursor.execute('''
                    INSERT INTO cards (match_id, team_id, player_name, minute, card_type, reason)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (match_id, team_id, player_name, minute, card_type, reason))
                if card_type == 'Amarilla':
                    total_yellow_cards_saved += 1
            
            # Obtener y guardar cambios
            local_cursor.execute('SELECT player_in, player_out, minute, team_id FROM substitutions WHERE match_id = %s', (match_id,))
            subs_data = local_cursor.fetchall()
            
            for sub in subs_data:
                player_in, player_out, minute, team_id = sub
                docker_cursor.execute('''
                    INSERT INTO substitutions (match_id, team_id, player_in, player_out, minute)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (match_id, team_id, player_in, player_out, minute))
                total_substitutions_saved += 1
        
        # Confirmar cambios
        docker_conn.commit()
        
        print(f'=== DATOS GUARDADOS EN DOCKER ===')
        print(f'Total goles guardados: {total_goals_saved}')
        print(f'Total tarjetas amarillas guardadas: {total_yellow_cards_saved}')
        print(f'Total cambios guardados: {total_substitutions_saved}')
        print()
        print('✅ Todos los datos de Premier League guardados exitosamente en Docker')
        
        # Cerrar conexiones
        local_conn.close()
        docker_conn.close()
        
    except Exception as e:
        print(f'❌ Error guardando en Docker: {e}')
        if 'docker_conn' in locals():
            docker_conn.rollback()
            docker_conn.close()
        if 'local_conn' in locals():
            local_conn.close()

if __name__ == "__main__":
    matches, premier_league_id = check_all_premier_league()
    if matches:
        save_all_to_docker(matches, premier_league_id)
