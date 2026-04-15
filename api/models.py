from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Auth Models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    created_at: Optional[str] = None

class PasswordReset(BaseModel):
    username: str
    new_password: str

# League Models
class League(BaseModel):
    id: int
    name: str
    country: str

# Team Models
class Team(BaseModel):
    id: int
    league_id: int
    name: str
    logo_path: Optional[str] = None

class TeamWithLeague(Team):
    league_name: str
    league_country: str

# Match Models
class Match(BaseModel):
    id: int
    league_id: int
    home_team_id: int
    away_team_id: int
    matchday: int
    match_date: Optional[str] = None
    home_score: int
    away_score: int
    is_finished: bool

class MatchDetail(Match):
    league_name: str
    home_team_name: str
    away_team_name: str
    goals: List[dict] = []
    cards: List = []
    injuries: List = []
    substitutions: List = []
    penalties: List = []

# Statistics Models
class TopScorer(BaseModel):
    player_name: str
    team_name: str
    goals: int
    penalties: int = 0

class TopAssister(BaseModel):
    player_name: str
    team_name: str
    assists: int

class Standing(BaseModel):
    position: int
    team_name: str
    team_id: int
    matches_played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int

# Goal Model
class Goal(BaseModel):
    id: int
    match_id: int
    team_id: int
    player_name: str
    minute: Optional[int] = None
    assist_player_name: Optional[str] = None
    is_own_goal: bool = False
    is_penalty: bool = False

# Card Model
class Card(BaseModel):
    id: int
    match_id: int
    team_id: int
    player_name: str
    minute: Optional[int] = None
    card_type: str
    reason: Optional[str] = None

# Injury Model
class Injury(BaseModel):
    id: int
    match_id: int
    team_id: int
    player_name: str
    minute: Optional[int] = None
    description: Optional[str] = None

# Substitution Model
class Substitution(BaseModel):
    id: int
    match_id: int
    team_id: int
    player_in: str
    player_out: str
    minute: Optional[int] = None

# Penalty Model
class Penalty(BaseModel):
    id: int
    match_id: int
    team_id: int
    player_name: Optional[str] = None
    minute: Optional[int] = None
    outcome: str
    description: Optional[str] = None


# ==================== BASKETBALL MODELS ====================

class BasketballLeague(BaseModel):
    id: int
    name: str
    country: Optional[str] = None
    level: Optional[str] = None


class BasketballSeason(BaseModel):
    id: int
    league_id: int
    season: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class BasketballStanding(BaseModel):
    position: Optional[int] = None
    team_id: int
    team_name: str
    games_played: Optional[int] = None
    wins: Optional[int] = None
    losses: Optional[int] = None
    points_for: Optional[int] = None
    points_against: Optional[int] = None
    point_diff: Optional[int] = None


class BasketballMatch(BaseModel):
    id: int
    league_id: int
    season_id: int
    matchday: Optional[int] = None
    match_date: Optional[str] = None
    home_team_id: int
    away_team_id: int
    home_team_name: str
    away_team_name: str
    home_score: int
    away_score: int
    is_finished: bool
