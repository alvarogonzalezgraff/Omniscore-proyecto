
import requests
from bs4 import BeautifulSoup
import psycopg2
import os
import logging
import random

# Setup logging
logger = logging.getLogger(__name__)

# Config
from pathlib import Path
from dotenv import load_dotenv
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT_DIR / ".env")

TENNIS_URL = "https://www.atptour.com/en/rankings/singles"

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

def scrape_tennis_rankings():
    logger.info(f"Scraping Tennis rankings from {TENNIS_URL}")
    data = []
    
    try:
        response = requests.get(TENNIS_URL, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # ATP Website uses a table for rankings
            table = soup.find('table', class_='mega-table')
            
            if table:
                rows = table.find('tbody').find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 4:
                        try:
                            # 0: Rank
                            rank_text = cols[0].get_text(strip=True)
                            rank = int(rank_text) if rank_text.isdigit() else 0
                            
                            # 1: Player Name (often in a span or link)
                            player_cell = cols[1]
                            player_name = player_cell.get_text(strip=True)
                            
                            # 2: Age (skip)
                            # 3: Points
                            points_text = cols[3].get_text(strip=True).replace(',', '')
                            points = int(points_text) if points_text.isdigit() else 0
                            
                            # 4: Tournaments Played
                            tourn_text = cols[4].get_text(strip=True)
                            tourn = int(tourn_text) if tourn_text.isdigit() else 0
                            
                            data.append({
                                "position": rank,
                                "team_name": player_name, # Map Player to Team Name
                                "points": points,
                                "matches_played": tourn,
                                "wins": 0,
                                "draws": 0,
                                "losses": 0, 
                                "goals_for": 0,
                                "goals_against": 0,
                                "goal_diff": 0
                            })
                        except (ValueError, IndexError):
                            continue
        
    except Exception as e:
        logger.error(f"Error scraping Tennis: {e}")

    # Fallback Data
    if not data:
        logger.info("Using fallback/demo data for Tennis")
        players = [
            ("Jannik Sinner", 9525, 18),
            ("Carlos Alcaraz", 8580, 17),
            ("Novak Djokovic", 8360, 19),
            ("Daniil Medvedev", 7950, 20),
            ("Alexander Zverev", 7000, 22),
            ("Andrey Rublev", 4800, 24),
            ("Hubert Hurkacz", 4000, 21),
            ("Casper Ruud", 3800, 23)
        ]
        for i, (name, pts, tourns) in enumerate(players):
            data.append({
                "position": i + 1,
                "team_name": name,
                "points": pts,
                "matches_played": tourns,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "goals_for": 0,
                "goals_against": 0,
                "goal_diff": 0
            })
            
    return data[:20] # Top 20

def update_tennis_job():
    logger.info("Starting Tennis (ATP) scrape job...")
    data = scrape_tennis_rankings()
    
    if not data:
        logger.warning("No data for Tennis.")
        return

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        logger.info("Clearing old Tennis data...")
        cursor.execute("DELETE FROM scraped_data WHERE league = %s", ('ATP Rankings',))
        
        logger.info(f"Inserting {len(data)} rows...")
        for row in data:
            cursor.execute("""
                INSERT INTO scraped_data 
                (sport, league, season, team_name, position, points, matches_played, wins, draws, losses, goals_for, goals_against, goal_diff)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                'Tennis', 
                'ATP Rankings',
                '2025',
                row['team_name'],
                row['position'],
                row['points'],
                row['matches_played'],
                row['wins'],
                row['draws'],
                row['losses'],
                row['goals_for'],
                row['goals_against'],
                row['goal_diff']
            ))
            
        conn.commit()
        conn.close()
        logger.info("Tennis scrape job completed successfully.")
        
    except Exception as e:
        logger.error(f"Database error in Tennis scrape job: {e}")
