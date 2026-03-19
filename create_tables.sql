-- Crear tablas esenciales para la migración

-- Tabla de ligas
CREATE TABLE IF NOT EXISTS leagues (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    country TEXT
);

-- Tabla de equipos
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY,
    league_id INTEGER,
    name TEXT NOT NULL,
    logo_path TEXT
);

-- Tabla de partidos
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY,
    league_id INTEGER,
    home_team_id INTEGER,
    away_team_id INTEGER,
    matchday INTEGER,
    match_date TEXT,
    home_score INTEGER DEFAULT 0,
    away_score INTEGER DEFAULT 0,
    is_finished BOOLEAN DEFAULT FALSE
);

-- Tabla de goles
CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY,
    match_id INTEGER,
    team_id INTEGER,
    player_name TEXT NOT NULL,
    minute INTEGER,
    assist_player_name TEXT,
    is_own_goal BOOLEAN DEFAULT FALSE,
    is_penalty BOOLEAN DEFAULT FALSE
);

-- Tabla de tarjetas
CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY,
    match_id INTEGER,
    team_id INTEGER,
    player_name TEXT NOT NULL,
    minute INTEGER,
    card_type TEXT,
    reason TEXT,
    description TEXT
);

-- Tabla de sustituciones
CREATE TABLE IF NOT EXISTS substitutions (
    id INTEGER PRIMARY KEY,
    match_id INTEGER,
    team_id INTEGER,
    player_in TEXT,
    player_out TEXT,
    minute INTEGER
);

-- Tabla de lesiones
CREATE TABLE IF NOT EXISTS injuries (
    id INTEGER PRIMARY KEY,
    match_id INTEGER,
    team_id INTEGER,
    player_name TEXT,
    minute INTEGER,
    description TEXT
);

-- Tabla de penales
CREATE TABLE IF NOT EXISTS penalties (
    id INTEGER PRIMARY KEY,
    match_id INTEGER,
    team_id INTEGER,
    player_name TEXT,
    minute INTEGER,
    outcome TEXT,
    description TEXT
);

-- Tabla de partidos scraped
CREATE TABLE IF NOT EXISTS scraped_matches (
    id INTEGER PRIMARY KEY,
    league TEXT,
    season TEXT,
    matchday TEXT,
    date TEXT,
    home_team TEXT,
    away_team TEXT,
    home_score INTEGER,
    away_score INTEGER,
    is_finished BOOLEAN,
    scorers TEXT,
    updated_at TEXT,
    assists TEXT,
    yellow_cards TEXT,
    red_cards TEXT,
    substitutions TEXT,
    injuries TEXT,
    url TEXT
);

-- Tabla de datos scraped (clasificación)
CREATE TABLE IF NOT EXISTS scraped_data (
    id INTEGER PRIMARY KEY,
    sport TEXT,
    league TEXT,
    season TEXT,
    team_name TEXT,
    position INTEGER,
    points INTEGER,
    matches_played INTEGER,
    wins INTEGER,
    draws INTEGER,
    losses INTEGER,
    goals_for INTEGER,
    goals_against INTEGER,
    goal_diff INTEGER,
    form TEXT,
    updated_at TEXT
);

-- Tabla de estadísticas de jugadores
CREATE TABLE IF NOT EXISTS player_stats (
    id INTEGER PRIMARY KEY,
    league_id INTEGER,
    player_name TEXT,
    team_name TEXT,
    goals INTEGER,
    assists INTEGER,
    matches_played INTEGER,
    updated_at TEXT
);

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT,
    password TEXT,
    full_name TEXT,
    created_at TEXT
);

-- Tablas de baloncesto
CREATE TABLE IF NOT EXISTS basketball_leagues (
    id INTEGER PRIMARY KEY,
    name TEXT,
    country TEXT,
    level TEXT
);

CREATE TABLE IF NOT EXISTS basketball_seasons (
    id INTEGER PRIMARY KEY,
    league_id INTEGER,
    season TEXT,
    start_date TEXT,
    end_date TEXT
);

CREATE TABLE IF NOT EXISTS basketball_teams (
    id INTEGER PRIMARY KEY,
    league_id INTEGER,
    name TEXT,
    short_name TEXT,
    logo_path TEXT
);

CREATE TABLE IF NOT EXISTS basketball_matches (
    id INTEGER PRIMARY KEY,
    league_id INTEGER,
    season_id INTEGER,
    matchday INTEGER,
    match_date TEXT,
    home_team_id INTEGER,
    away_team_id INTEGER,
    home_score INTEGER,
    away_score INTEGER,
    is_finished BOOLEAN,
    venue TEXT,
    referee TEXT,
    source_url TEXT
);

CREATE TABLE IF NOT EXISTS basketball_players (
    id INTEGER PRIMARY KEY,
    full_name TEXT,
    nationality TEXT,
    birth_date TEXT
);

CREATE TABLE IF NOT EXISTS basketball_standings (
    id INTEGER PRIMARY KEY,
    season_id INTEGER,
    team_id INTEGER,
    position INTEGER,
    games_played INTEGER,
    wins INTEGER,
    losses INTEGER,
    points_for INTEGER,
    points_against INTEGER,
    point_diff INTEGER,
    streak TEXT,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS basketball_player_season_stats (
    id INTEGER PRIMARY KEY,
    season_id INTEGER,
    player_id INTEGER,
    team_id INTEGER,
    points INTEGER,
    assists INTEGER,
    rebounds INTEGER,
    matches_played INTEGER,
    updated_at TEXT
);

-- Tablas de tenis
CREATE TABLE IF NOT EXISTS tennis_tournaments (
    id INTEGER PRIMARY KEY,
    name TEXT,
    tour TEXT,
    category TEXT,
    surface TEXT,
    location TEXT,
    country TEXT,
    official_url TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS tennis_players (
    id INTEGER PRIMARY KEY,
    full_name TEXT
);

CREATE TABLE IF NOT EXISTS tennis_editions (
    id INTEGER PRIMARY KEY,
    tournament_id INTEGER,
    year INTEGER,
    winner_player_id INTEGER,
    runner_up_player_id INTEGER,
    score TEXT,
    notes TEXT,
    source TEXT
);
