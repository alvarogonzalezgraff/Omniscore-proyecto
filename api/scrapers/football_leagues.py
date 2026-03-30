
import requests
from bs4 import BeautifulSoup
import psycopg2
import os
import logging
import random
from datetime import datetime, timedelta

# Setup logging
logger = logging.getLogger(__name__)

# Config
from pathlib import Path
from dotenv import load_dotenv
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT_DIR / ".env")

# URLs
HYPERMOTION_URL = "https://www.laliga.com/laliga-hypermotion/clasificacion"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

from api.config import USE_POSTGRES, DB_PATH
import sqlite3

class SQLiteCursorWrapper:
    def __init__(self, cursor):
        self.cursor = cursor
    def execute(self, sql, params=None):
        if params is not None:
            sql = sql.replace('%s', '?')
        return self.cursor.execute(sql, params or ())
    def fetchall(self): return self.cursor.fetchall()
    def fetchone(self): return self.cursor.fetchone()
    def close(self): self.cursor.close()

class SQLiteConnWrapper:
    def __init__(self, conn):
        self.conn = conn
    def cursor(self): return SQLiteCursorWrapper(self.conn.cursor())
    def commit(self): self.conn.commit()
    def close(self): self.conn.close()

def get_db_connection():
    if USE_POSTGRES:
        import psycopg2
        return psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            dbname=os.getenv('DB_NAME', 'betwin_db'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '')
        )
    else:
        conn = sqlite3.connect(str(DB_PATH))
        return SQLiteConnWrapper(conn)

# --- Generic Scraper for LaLiga-based pages (Hypermotion) ---
def scrape_laliga_site(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        standings = []
        
        rows = soup.find_all('div', class_=lambda x: x and 'styled__StandingTabBody' in x)
        
        for row in rows:
            cells = row.find_all('div', class_=lambda x: x and 'styled__Td' in x)
            if not cells or len(cells) < 10: continue
                
            first_cell_text = cells[0].get_text(strip=True)
            if not first_cell_text.isdigit(): continue

            try:
                position = int(first_cell_text)
                
                team_cell = cells[1]
                team_name_div = team_cell.find('div', class_=lambda x: x and 'shield-desktop' in x)
                team_name = team_name_div.get_text(strip=True) if team_name_div else team_cell.get_text(strip=True)
                
                points = int(cells[2].get_text(strip=True))
                matches_played = int(cells[3].get_text(strip=True))
                wins = int(cells[4].get_text(strip=True))
                draws = int(cells[5].get_text(strip=True))
                losses = int(cells[6].get_text(strip=True))
                goals_for = int(cells[7].get_text(strip=True))
                goals_against = int(cells[8].get_text(strip=True))
                goal_diff = int(cells[9].get_text(strip=True))
                
                standings.append({
                    "position": position,
                    "team_name": team_name,
                    "points": points,
                    "matches_played": matches_played,
                    "wins": wins,
                    "draws": draws,
                    "losses": losses,
                    "goals_for": goals_for,
                    "goals_against": goals_against,
                    "goal_diff": goal_diff
                })
            except:
                continue
                
        return standings[:22]
    except Exception as e:
        logger.error(f"Error scraping LaLiga site: {e}")
        return []

# --- Data Generators ---

def get_premier_data():
    teams = ["Liverpool", "Manchester City", "Arsenal", "Aston Villa", "Chelsea", "Tottenham", "Newcastle", "Manchester United", "West Ham", "Brighton", "Wolves", "Bournemouth", "Fulham", "Brentford", "Crystal Palace", "Nottm Forest", "Everton", "Luton Town", "Burnley", "Sheffield Utd"]
    return generate_full_league_data(teams, "Premier League")

def get_serie_a_data():
    teams = ["Inter", "Juventus", "Milan", "Atalanta", "Bologna", "Roma", "Napoli", "Fiorentina", "Lazio", "Torino", "Monza", "Genoa", "Lecce", "Empoli", "Frosinone", "Udinese", "Sassuolo", "Verona", "Cagliari", "Salernitana"]
    return generate_full_league_data(teams, "Serie A")

def get_bundesliga_data():
    teams = ["Leverkusen", "Bayern Munich", "Stuttgart", "Dortmund", "Leipzig", "Frankfurt", "Hoffenheim", "Freiburg", "Heidenheim", "Augsburg", "Werder Bremen", "Wolfsburg", "Gladbach", "Union Berlin", "Bochum", "Mainz", "Köln", "Darmstadt"]
    return generate_full_league_data(teams, "Bundesliga")

def get_hypermotion_fallback():
    teams = ["Leganés", "Valladolid", "Eibar", "Espanyol", "Sporting", "Oviedo", "Racing", "Elche", "Ferrol", "Burgos", "Levante", "Tenerife", "Zaragoza", "Eldense", "Huesca", "Cartagena", "Mirandés", "Albacete", "Alcorcón", "Villarreal B", "Andorra", "Amorebieta"]
    return generate_full_league_data(teams, "Liga Hypermotion")

def generate_full_league_data(teams, league_name):
    # 1. Standings
    standings = []
    for i, team in enumerate(teams):
        wins = max(0, 25 - i + random.randint(-2, 2))
        draws = random.randint(2, 8)
        losses = max(0, 38 - wins - draws) if len(teams) > 18 else max(0, 34 - wins - draws)
        gf = wins * 2 + draws + random.randint(5, 20)
        ga = losses * 1.5 + draws + random.randint(5, 20)
        
        standings.append({
            "position": i + 1,
            "team_name": team,
            "points": wins * 3 + draws,
            "matches_played": wins + draws + losses,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "goals_for": int(gf),
            "goals_against": int(ga),
            "goal_diff": int(gf - ga)
        })

    # 2. Results (Latest Matchday)
    matches = []
    shuffled_teams = teams.copy()
    random.shuffle(shuffled_teams)
    
    matchday_num = random.randint(20, 25)
    
    for i in range(0, len(shuffled_teams), 2):
        if i + 1 < len(shuffled_teams):
            home = shuffled_teams[i]
            away = shuffled_teams[i+1]
            matches.append({
                "league": league_name,
                "season": "25/26",
                "matchday": f"Jornada {matchday_num}",
                "date": (datetime.now() - timedelta(days=random.randint(0, 3))).strftime("%Y-%m-%d"),
                "home_team": home,
                "away_team": away,
                "home_score": random.randint(0, 4),
                "away_score": random.randint(0, 3),
                "is_finished": True,
                "scorers": "Simulated"
            })

    # 3. Scorers & Assisters
    scorers = []
    assisters = []
    
    # Generate some fake player names based on league mostly
    fake_names = ["Player A", "Player B", "Player C", "Star Striker", "Midfield Maestro", "Winger X", "Forward Y"]
    
    for i in range(10):
         scorers.append({
             "player_name": f"{random.choice(['John', 'Davide', 'Hans', 'Luis'])} {random.choice(['Smith', 'Rossi', 'Müller', 'Garcia'])}",
             "team_name": random.choice(teams),
             "goals": random.randint(10, 25),
             "assists": random.randint(0, 5)
         })
         assisters.append({
             "player_name": f"{random.choice(['Paul', 'Marco', 'Stefan', 'Pedro'])} {random.choice(['Jones', 'Bianchi', 'Schmidt', 'Lopez'])}",
             "team_name": random.choice(teams),
             "goals": random.randint(0, 5),
             "assists": random.randint(8, 15)
         })

    return {
        "standings": standings,
        "matches": matches,
        "scorers": scorers,
        "assisters": assisters
    }

# --- Update Jobs ---

def update_hypermotion_job():
    logger.info("Starting Liga Hypermotion scrape...")
    standings = scrape_laliga_site(HYPERMOTION_URL)
    
    if standings:
        # If real standings scraped, generate mock other data using team names from scraped data
        teams = [s['team_name'] for s in standings]
        full_data = generate_full_league_data(teams, "Liga Hypermotion")
        full_data['standings'] = standings # Keep real standings
    else:
        logger.info("Using fallback for Hypermotion")
        full_data = get_hypermotion_fallback()
        
    save_all_data(full_data, "Liga Hypermotion")

def update_premier_job():
    logger.info("Starting Premier League update... SKIPPED to preserve manual J3 data")
    # data = get_premier_data()
    # save_all_data(data, "Premier League")

def update_serie_a_job():
    logger.info("Starting Serie A update... SKIPPED to preserve manual data")
    # data = get_serie_a_data()
    # save_all_data(data, "Serie A")

def update_bundesliga_job():
    logger.info("Starting Bundesliga update... SKIPPED to preserve manual data")
    # data = get_bundesliga_data()
    # save_all_data(data, "Bundesliga")

# --- Save Functions ---

def save_all_data(data, league_name):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Save Standings
        cursor.execute("DELETE FROM scraped_data WHERE league = %s", (league_name,))
        for row in data['standings']:
            cursor.execute("""
                INSERT INTO scraped_data 
                (sport, league, season, team_name, position, points, matches_played, wins, draws, losses, goals_for, goals_against, goal_diff)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, ('Football', league_name, '25/26', row['team_name'], row['position'], row['points'], row['matches_played'], row['wins'], row['draws'], row['losses'], row['goals_for'], row['goals_against'], row['goal_diff']))
            
        # 2. Save Matches
        cursor.execute("DELETE FROM scraped_matches WHERE league = %s", (league_name,))
        for m in data['matches']:
            cursor.execute("""
                INSERT INTO scraped_matches (league, season, matchday, date, home_team, away_team, home_score, away_score, is_finished, scorers)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (m['league'], m['season'], m['matchday'], m['date'], m['home_team'], m['away_team'], m['home_score'], m['away_score'], m['is_finished'], m['scorers']))
            
        # 3. Save Player Stats
        # Get league_id
        cursor.execute("SELECT id FROM leagues WHERE name = %s", (league_name,))
        res = cursor.fetchone()
        if res:
            league_id = res[0]
            # Clear old stats for this league
            cursor.execute("DELETE FROM player_stats WHERE league_id = %s", (league_id,))
            
            # Combine scorers and assisters to avoid duplicates if possible, or just insert straightforwardly
            # For simplicity, we just insert. If a player is both, they might appear twice or we should merge.
            # Merging logic:
            players = {}
            for p in data['scorers']:
                key = (p['player_name'], p['team_name'])
                players[key] = {'goals': p['goals'], 'assists': p['assists']}
            
            for p in data['assisters']:
                key = (p['player_name'], p['team_name'])
                if key in players:
                    players[key]['assists'] = p['assists'] # Update assists
                else:
                    players[key] = {'goals': p['goals'], 'assists': p['assists']}
            
            for (p_name, t_name), stats in players.items():
                cursor.execute("""
                    INSERT INTO player_stats (league_id, player_name, team_name, goals, assists, matches_played)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (league_id, p_name, t_name, stats['goals'], stats['assists'], random.randint(15, 22)))
        
        conn.commit()
        conn.close()
        logger.info(f"{league_name} full data updated successfully.")
        
    except Exception as e:
        logger.error(f"Error updating {league_name}: {e}")
