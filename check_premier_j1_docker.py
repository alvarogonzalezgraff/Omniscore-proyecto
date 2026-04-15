import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

# Conexión a Docker PostgreSQL
def get_docker_connection():
    return psycopg2.connect(
        host='localhost',
        port='5433',
        dbname='Omniscore_db',
        user='postgres',
        password='docker_password'
    )

def get_local_connection():
    ROOT_DIR = Path(__file__).resolve().parent
    load_dotenv(ROOT_DIR / ".env")
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        dbname=os.getenv('DB_NAME', 'Omniscore_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', '')
    )

def check_and_save_data():
    try:
        # Primero verificar datos en la base de datos local
        local_conn = get_local_connection()
        local_cursor = local_conn.cursor()
        
        # Obtener ID de Premier League
        local_cursor.execute("SELECT id FROM leagues WHERE name = 'Premier League'")
        premier_result = local_cursor.fetchone()
        
        if not premier_result:
            print("❌ No se encontró la Premier League en la base de datos local")
            return
        
        premier_league_id = premier_result[0]
        
        # Obtener partidos de jornada 1
        local_cursor.execute('''
            SELECT m.id, t1.name as home_team, t2.name as away_team, 
                   m.home_score, m.away_score, m.matchday
            FROM matches m
            JOIN teams t1 ON m.home_team_id = t1.id
            JOIN teams t2 ON m.away_team_id = t2.id
            WHERE m.league_id = %s AND m.matchday = 1
            ORDER BY t1.name
        ''', (premier_league_id,))
        
        matches = local_cursor.fetchall()
        
        # Conectar a Docker
        docker_conn = get_docker_connection()
        docker_cursor = docker_conn.cursor()
        
        print(f'=== GUARDANDO DATOS EN DOCKER ===')
        print(f'Total partidos a procesar: {len(matches)}')
        print()
        
        total_matches = len(matches)
        matches_with_goals = 0
        matches_with_yellow_cards = 0
        matches_with_substitutions = 0
        
        for match in matches:
            match_id, home_team, away_team, home_score, away_score, matchday = match
            print(f'🏆 {home_team} vs {away_team} ({home_score}-{away_score})')
            
            # Obtener y guardar goles
            local_cursor.execute('SELECT player_name, minute, assist_player_name, is_own_goal, is_penalty, team_id FROM goals WHERE match_id = %s', (match_id,))
            goals_data = local_cursor.fetchall()
            
            if goals_data:
                matches_with_goals += 1
                print(f'  ✅ Goles: {len(goals_data)} eventos')
                for goal in goals_data:
                    player_name, minute, assist_player_name, is_own_goal, is_penalty, team_id = goal
                    docker_cursor.execute('''
                        INSERT INTO goals (match_id, team_id, player_name, minute, assist_player_name, is_own_goal, is_penalty)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                    ''', (match_id, team_id, player_name, minute, assist_player_name, is_own_goal, is_penalty))
            else:
                print(f'  ❌ Sin datos de goles')
            
            # Obtener y guardar tarjetas amarillas
            local_cursor.execute("SELECT player_name, minute, card_type, reason, team_id FROM cards WHERE match_id = %s AND card_type = 'Amarilla'", (match_id,))
            cards_data = local_cursor.fetchall()
            
            if cards_data:
                matches_with_yellow_cards += 1
                print(f'  ✅ Tarjetas amarillas: {len(cards_data)}')
                for card in cards_data:
                    player_name, minute, card_type, reason, team_id = card
                    docker_cursor.execute('''
                        INSERT INTO cards (match_id, team_id, player_name, minute, card_type, reason)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                    ''', (match_id, team_id, player_name, minute, card_type, reason))
            else:
                print(f'  ❌ Sin tarjetas amarillas')
            
            # Obtener y guardar cambios
            local_cursor.execute('SELECT player_in, player_out, minute, team_id FROM substitutions WHERE match_id = %s', (match_id,))
            subs_data = local_cursor.fetchall()
            
            if subs_data:
                matches_with_substitutions += 1
                print(f'  ✅ Cambios: {len(subs_data)}')
                for sub in subs_data:
                    player_in, player_out, minute, team_id = sub
                    docker_cursor.execute('''
                        INSERT INTO substitutions (match_id, team_id, player_in, player_out, minute)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                    ''', (match_id, team_id, player_in, player_out, minute))
            else:
                print(f'  ❌ Sin datos de cambios')
            
            print()
        
        # Confirmar cambios en Docker
        docker_conn.commit()
        
        print(f'=== RESUMEN ===')
        print(f'Partidos totales: {total_matches}')
        print(f'Partidos con goles guardados: {matches_with_goals} ({matches_with_goals/total_matches*100:.1f}%)')
        print(f'Partidos con tarjetas amarillas guardadas: {matches_with_yellow_cards} ({matches_with_yellow_cards/total_matches*100:.1f}%)')
        print(f'Partidos con cambios guardados: {matches_with_substitutions} ({matches_with_substitutions/total_matches*100:.1f}%)')
        print()
        print('✅ Datos guardados exitosamente en Docker PostgreSQL')
        
        # Cerrar conexiones
        local_conn.close()
        docker_conn.close()
        
    except Exception as e:
        print(f'❌ Error: {e}')
        if 'docker_conn' in locals():
            docker_conn.rollback()
            docker_conn.close()
        if 'local_conn' in locals():
            local_conn.close()

if __name__ == "__main__":
    check_and_save_data()
