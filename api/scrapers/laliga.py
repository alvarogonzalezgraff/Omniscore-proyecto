
import requests
from bs4 import BeautifulSoup
import psycopg2
import os
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Config
from pathlib import Path
from dotenv import load_dotenv
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT_DIR / ".env")

LALIGA_URL = "https://www.laliga.com/laliga-easports/clasificacion"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        dbname=os.getenv('DB_NAME', 'betwin_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', '')
    )

def scrape_laliga_standings():
    logger.info(f"Scraping LaLiga stats from {LALIGA_URL}")
    try:
        response = requests.get(LALIGA_URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        standings = []
        
        # Strategy: Find rows by partial class matching 'styled__StandingTabBody'
        rows = soup.find_all('div', class_=lambda x: x and 'styled__StandingTabBody' in x)
        
        if not rows:
            logger.warning("No rows found with 'styled__StandingTabBody' selector.")
            return []

        logger.info(f"Found {len(rows)} potential rows.")
        
        for row in rows:
            cells = row.find_all('div', class_=lambda x: x and 'styled__Td' in x)
            
            if not cells:
                continue
                
            first_cell_text = cells[0].get_text(strip=True)
            if not first_cell_text.isdigit():
                continue
                
            if len(cells) < 10:
                continue

            try:
                # 0: Pos
                position = int(first_cell_text)
                
                # 1: Team
                team_cell = cells[1]
                team_name_div = team_cell.find('div', class_=lambda x: x and 'shield-desktop' in x)
                if team_name_div:
                    team_name = team_name_div.get_text(strip=True)
                else:
                    team_name = team_cell.get_text(strip=True)
                
                # 2: Pts
                points = int(cells[2].get_text(strip=True))
                
                # 3: PJ
                matches_played = int(cells[3].get_text(strip=True))
                
                # 4: PG (Wins)
                wins = int(cells[4].get_text(strip=True))
                
                # 5: PE (Draws)
                draws = int(cells[5].get_text(strip=True))
                
                # 6: PP (Losses)
                losses = int(cells[6].get_text(strip=True))
                
                # 7: GF
                goals_for = int(cells[7].get_text(strip=True))
                
                # 8: GC
                goals_against = int(cells[8].get_text(strip=True))
                
                # 9: DG
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
            except Exception as e:
                continue
        
        # Return only the first 20 rows (Total standings)
        return standings[:20]

    except Exception as e:
        logger.error(f"Error scraping LaLiga: {e}")
        return []

def update_laliga_job():
    logger.info("Starting LaLiga EA Sports scrape job...")
    data = scrape_laliga_standings()
    
    if not data:
        logger.warning("No data scraped for LaLiga. Skipping DB update.")
        return

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        logger.info("Clearing old LaLiga EA Sports data...")
        cursor.execute("DELETE FROM scraped_data WHERE league = %s", ('LaLiga EA Sports',))
        
        logger.info(f"Inserting {len(data)} rows...")
        for row in data:
            cursor.execute("""
                INSERT INTO scraped_data 
                (sport, league, season, team_name, position, points, matches_played, wins, draws, losses, goals_for, goals_against, goal_diff)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                'Football', 
                'LaLiga EA Sports',
                '25/26',
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
        logger.info("LaLiga scrape job completed successfully.")
        
    except Exception as e:
        logger.error(f"Database error in scrape job: {e}")
