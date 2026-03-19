import sqlite3
import sys
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv
load_dotenv(ROOT_DIR / ".env")

import psycopg2
from psycopg2.extras import execute_values

SQLITE_PATH = ROOT_DIR / "database" / "app.db"

PG_HOST     = os.getenv("DB_HOST", "localhost")
PG_PORT     = os.getenv("DB_PORT", "5432")
PG_DB       = os.getenv("DB_NAME", "betwin_db")
PG_USER     = os.getenv("DB_USER", "postgres")
PG_PASSWORD = os.getenv("DB_PASSWORD", "")

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id         SERIAL PRIMARY KEY,
    username   VARCHAR(255) NOT NULL UNIQUE,
    email      VARCHAR(255) NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,
    full_name  VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS leagues (
    id      SERIAL PRIMARY KEY,
    name    VARCHAR(255) NOT NULL UNIQUE,
    country VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS teams (
    id        SERIAL PRIMARY KEY,
    league_id INTEGER REFERENCES leagues(id),
    name      VARCHAR(255) NOT NULL,
    logo_path VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS matches (
    id           SERIAL PRIMARY KEY,
    league_id    INTEGER REFERENCES leagues(id),
    home_team_id INTEGER REFERENCES teams(id),
    away_team_id INTEGER REFERENCES teams(id),
    matchday     INTEGER,
    match_date   TIMESTAMP,
    home_score   INTEGER DEFAULT 0,
    away_score   INTEGER DEFAULT 0,
    is_finished  BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS goals (
    id                SERIAL PRIMARY KEY,
    match_id          INTEGER REFERENCES matches(id),
    team_id           INTEGER REFERENCES teams(id),
    player_name       VARCHAR(255) NOT NULL,
    minute            INTEGER,
    assist_player_name VARCHAR(255),
    is_own_goal       BOOLEAN DEFAULT FALSE,
    is_penalty        BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS cards (
    id          SERIAL PRIMARY KEY,
    match_id    INTEGER REFERENCES matches(id),
    team_id     INTEGER REFERENCES teams(id),
    player_name VARCHAR(255) NOT NULL,
    minute      INTEGER,
    card_type   VARCHAR(50)  CHECK(card_type IN ('Amarilla', 'Roja', 'Doble Amarilla')),
    reason      TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS injuries (
    id          SERIAL PRIMARY KEY,
    match_id    INTEGER REFERENCES matches(id),
    team_id     INTEGER REFERENCES teams(id),
    player_name VARCHAR(255) NOT NULL,
    minute      INTEGER,
    description TEXT
);

CREATE TABLE IF NOT EXISTS substitutions (
    id         SERIAL PRIMARY KEY,
    match_id   INTEGER REFERENCES matches(id),
    team_id    INTEGER REFERENCES teams(id),
    player_in  VARCHAR(255) NOT NULL,
    player_out VARCHAR(255) NOT NULL,
    minute     INTEGER
);

CREATE TABLE IF NOT EXISTS penalties (
    id          SERIAL PRIMARY KEY,
    match_id    INTEGER REFERENCES matches(id),
    team_id     INTEGER REFERENCES teams(id),
    player_name VARCHAR(255),
    minute      INTEGER,
    outcome     VARCHAR(50) CHECK(outcome IN ('Gol', 'Fallado', 'Parado', 'No Pitado', 'Revision VAR')),
    description TEXT
);

CREATE TABLE IF NOT EXISTS scraped_data (
    id             SERIAL PRIMARY KEY,
    sport          VARCHAR(50)  NOT NULL,
    league         VARCHAR(100) NOT NULL,
    season         VARCHAR(50),
    team_name      VARCHAR(255) NOT NULL,
    position       INTEGER,
    points         INTEGER,
    matches_played INTEGER,
    wins           INTEGER,
    draws          INTEGER,
    losses         INTEGER,
    goals_for      INTEGER,
    goals_against  INTEGER,
    goal_diff      INTEGER,
    form           VARCHAR(50),
    updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS player_stats (
    id             SERIAL PRIMARY KEY,
    league_id      INTEGER DEFAULT 1 REFERENCES leagues(id),
    player_name    VARCHAR(255) NOT NULL,
    team_name      VARCHAR(255) NOT NULL,
    goals          INTEGER DEFAULT 0,
    assists        INTEGER DEFAULT 0,
    matches_played INTEGER DEFAULT 0,
    updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scraped_matches (
    id           SERIAL PRIMARY KEY,
    league       VARCHAR(100) NOT NULL,
    season       VARCHAR(50),
    matchday     VARCHAR(50),
    date         VARCHAR(50),
    home_team    VARCHAR(255) NOT NULL,
    away_team    VARCHAR(255) NOT NULL,
    home_score   INTEGER,
    away_score   INTEGER,
    is_finished  BOOLEAN DEFAULT FALSE,
    scorers      TEXT,
    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assists      TEXT,
    yellow_cards TEXT,
    red_cards    TEXT,
    substitutions TEXT,
    injuries     TEXT,
    url          TEXT
);

CREATE TABLE IF NOT EXISTS basketball_leagues (
    id      SERIAL PRIMARY KEY,
    name    VARCHAR(255) NOT NULL UNIQUE,
    country VARCHAR(255),
    level   VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS basketball_seasons (
    id         SERIAL PRIMARY KEY,
    league_id  INTEGER NOT NULL REFERENCES basketball_leagues(id),
    season     VARCHAR(50) NOT NULL,
    start_date VARCHAR(50),
    end_date   VARCHAR(50),
    UNIQUE(league_id, season)
);

CREATE TABLE IF NOT EXISTS basketball_teams (
    id         SERIAL PRIMARY KEY,
    league_id  INTEGER NOT NULL REFERENCES basketball_leagues(id),
    name       VARCHAR(255) NOT NULL,
    short_name VARCHAR(100),
    logo_path  VARCHAR(255),
    UNIQUE(league_id, name)
);

CREATE TABLE IF NOT EXISTS basketball_players (
    id          SERIAL PRIMARY KEY,
    full_name   VARCHAR(255) NOT NULL UNIQUE,
    nationality VARCHAR(100),
    birth_date  VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS basketball_matches (
    id           SERIAL PRIMARY KEY,
    league_id    INTEGER NOT NULL REFERENCES basketball_leagues(id),
    season_id    INTEGER NOT NULL REFERENCES basketball_seasons(id),
    matchday     INTEGER,
    match_date   VARCHAR(50),
    home_team_id INTEGER NOT NULL REFERENCES basketball_teams(id),
    away_team_id INTEGER NOT NULL REFERENCES basketball_teams(id),
    home_score   INTEGER DEFAULT 0,
    away_score   INTEGER DEFAULT 0,
    is_finished  BOOLEAN DEFAULT FALSE,
    venue        VARCHAR(255),
    referee      VARCHAR(255),
    source_url   TEXT,
    UNIQUE(season_id, home_team_id, away_team_id, matchday)
);

CREATE TABLE IF NOT EXISTS basketball_team_match_stats (
    id         SERIAL PRIMARY KEY,
    match_id   INTEGER NOT NULL REFERENCES basketball_matches(id) ON DELETE CASCADE,
    team_id    INTEGER NOT NULL REFERENCES basketball_teams(id),
    points     INTEGER,
    rebounds   INTEGER,
    assists    INTEGER,
    steals     INTEGER,
    blocks     INTEGER,
    turnovers  INTEGER,
    fouls      INTEGER,
    fgm        INTEGER,
    fga        INTEGER,
    tpm        INTEGER,
    tpa        INTEGER,
    ftm        INTEGER,
    fta        INTEGER,
    UNIQUE(match_id, team_id)
);

CREATE TABLE IF NOT EXISTS basketball_player_match_stats (
    id         SERIAL PRIMARY KEY,
    match_id   INTEGER NOT NULL REFERENCES basketball_matches(id) ON DELETE CASCADE,
    team_id    INTEGER NOT NULL REFERENCES basketball_teams(id),
    player_id  INTEGER NOT NULL REFERENCES basketball_players(id),
    minutes    VARCHAR(10),
    points     INTEGER,
    rebounds   INTEGER,
    assists    INTEGER,
    steals     INTEGER,
    blocks     INTEGER,
    turnovers  INTEGER,
    fouls      INTEGER,
    fgm        INTEGER,
    fga        INTEGER,
    tpm        INTEGER,
    tpa        INTEGER,
    ftm        INTEGER,
    fta        INTEGER,
    plus_minus INTEGER,
    UNIQUE(match_id, player_id)
);

CREATE TABLE IF NOT EXISTS basketball_standings (
    id              SERIAL PRIMARY KEY,
    season_id       INTEGER NOT NULL REFERENCES basketball_seasons(id) ON DELETE CASCADE,
    team_id         INTEGER NOT NULL REFERENCES basketball_teams(id),
    position        INTEGER,
    games_played    INTEGER,
    wins            INTEGER,
    losses          INTEGER,
    points_for      INTEGER,
    points_against  INTEGER,
    point_diff      INTEGER,
    streak          VARCHAR(50),
    updated_at      VARCHAR(50) DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(season_id, team_id)
);

CREATE TABLE IF NOT EXISTS basketball_player_season_stats (
    id             SERIAL PRIMARY KEY,
    season_id      INTEGER NOT NULL REFERENCES basketball_seasons(id) ON DELETE CASCADE,
    player_id      INTEGER NOT NULL REFERENCES basketball_players(id),
    team_id        INTEGER REFERENCES basketball_teams(id),
    points         INTEGER DEFAULT 0,
    assists        INTEGER DEFAULT 0,
    rebounds       INTEGER DEFAULT 0,
    matches_played INTEGER DEFAULT 0,
    updated_at     VARCHAR(50) DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(season_id, player_id)
);

CREATE TABLE IF NOT EXISTS tennis_tournaments (
    id           SERIAL PRIMARY KEY,
    name         VARCHAR(255) NOT NULL UNIQUE,
    tour         VARCHAR(50)  NOT NULL,
    category     VARCHAR(50),
    surface      VARCHAR(50),
    location     VARCHAR(255),
    country      VARCHAR(100),
    official_url TEXT,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tennis_players (
    id        SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS tennis_editions (
    id                  SERIAL PRIMARY KEY,
    tournament_id       INTEGER NOT NULL REFERENCES tennis_tournaments(id) ON DELETE CASCADE,
    year                INTEGER NOT NULL,
    winner_player_id    INTEGER REFERENCES tennis_players(id),
    runner_up_player_id INTEGER REFERENCES tennis_players(id),
    score               VARCHAR(100),
    notes               TEXT,
    source              TEXT,
    UNIQUE(tournament_id, year)
);
"""

MIGRATION_ORDER = [
    "users",
    "leagues",
    "teams",
    "matches",
    "goals",
    "cards",
    "injuries",
    "substitutions",
    "penalties",
    "scraped_data",
    "player_stats",
    "scraped_matches",
    "basketball_leagues",
    "basketball_seasons",
    "basketball_teams",
    "basketball_players",
    "basketball_matches",
    "basketball_team_match_stats",
    "basketball_player_match_stats",
    "basketball_standings",
    "basketball_player_season_stats",
    "tennis_tournaments",
    "tennis_players",
    "tennis_editions",
]


def create_postgres_db_if_not_exists():
    try:
        conn = psycopg2.connect(
            host=PG_HOST, port=PG_PORT,
            user=PG_USER, password=PG_PASSWORD,
            database="postgres"
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (PG_DB,))
        if cur.fetchone() is None:
            cur.execute(f'CREATE DATABASE "{PG_DB}"')
            print(f"[OK] Base de datos '{PG_DB}' creada.")
        else:
            print(f"[INFO] Base de datos '{PG_DB}' ya existe.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] Error creando la base de datos: {e}")
        sys.exit(1)


def connect_postgres():
    try:
        conn = psycopg2.connect(
            host=PG_HOST, port=PG_PORT,
            user=PG_USER, password=PG_PASSWORD,
            database=PG_DB
        )
        return conn
    except Exception as e:
        print(f"[ERROR] Error conectando a PostgreSQL: {e}")
        sys.exit(1)


def connect_sqlite():
    if not SQLITE_PATH.exists():
        print(f"[ERROR] No se encontro el archivo SQLite: {SQLITE_PATH}")
        sys.exit(1)
    conn = sqlite3.connect(str(SQLITE_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def create_tables(pg_conn):
    print("\n[*] Creando tablas en PostgreSQL...")
    cur = pg_conn.cursor()
    cur.execute(CREATE_TABLES_SQL)
    pg_conn.commit()
    cur.close()
    print("[OK] Tablas creadas correctamente.")


def migrate_table(sqlite_conn, pg_conn, table_name):
    sqlite_cur = sqlite_conn.cursor()
    pg_cur = pg_conn.cursor()

    try:
        if table_name in ("goals", "cards", "injuries", "substitutions", "penalties"):
            sqlite_cur.execute(f"SELECT * FROM {table_name} WHERE match_id IN (SELECT id FROM matches)")
        else:
            sqlite_cur.execute(f"SELECT * FROM {table_name}")
    except sqlite3.OperationalError:
        print(f"  [SKIP] Tabla '{table_name}' no existe en SQLite.")
        return 0

    rows = sqlite_cur.fetchall()
    if not rows:
        print(f"  [SKIP] Tabla '{table_name}' vacia.")
        return 0

    columns = [desc[0] for desc in sqlite_cur.description]
    col_list = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))

    data = []
    for row in rows:
        row_dict = dict(row)
        converted = []
        for col in columns:
            val = row_dict[col]
            if col in ("is_finished", "is_own_goal", "is_penalty"):
                val = bool(val) if val is not None else False
            converted.append(val)
        data.append(tuple(converted))

    insert_sql = f"""
        INSERT INTO {table_name} ({col_list})
        VALUES ({placeholders})
        ON CONFLICT DO NOTHING
    """

    try:
        execute_values(pg_cur, insert_sql.replace(
            f"VALUES ({placeholders})", "VALUES %s"
        ), data, template=f"({placeholders})")
        pg_conn.commit()
    except Exception as e:
        pg_conn.rollback()
        print(f"  [ERROR] Error insertando en '{table_name}': {e}")
        return 0

    try:
        pg_cur.execute(
            f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), "
            f"COALESCE(MAX(id), 1)) FROM {table_name}"
        )
        pg_conn.commit()
    except Exception:
        pass

    return len(data)


def run_migration():
    print("=" * 60)
    print("  MIGRACION SQLite -> PostgreSQL")
    print("=" * 60)
    print(f"\nOrigen  : {SQLITE_PATH}")
    print(f"Destino : postgresql://{PG_USER}@{PG_HOST}:{PG_PORT}/{PG_DB}\n")

    create_postgres_db_if_not_exists()

    sqlite_conn = connect_sqlite()
    pg_conn = connect_postgres()
    print("[OK] Conexiones establecidas.")

    create_tables(pg_conn)

    print("\n[*] Migrando datos...\n")
    total_rows = 0
    for table in MIGRATION_ORDER:
        count = migrate_table(sqlite_conn, pg_conn, table)
        if count > 0:
            print(f"  [OK] {table:<40} -> {count:>6} filas")
        total_rows += count

    sqlite_conn.close()
    pg_conn.close()

    print(f"\n{'=' * 60}")
    print(f"  MIGRACION COMPLETADA - {total_rows} filas totales migradas")
    print("=" * 60)


if __name__ == "__main__":
    run_migration()
