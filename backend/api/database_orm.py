from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# ==================== USERS ====================
class UserORM(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    created_at = Column(DateTime)

# ==================== FOOTBALL ====================
class LeagueORM(Base):
    __tablename__ = 'leagues'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    country = Column(String(255), nullable=False)

    teams = relationship("TeamORM", back_populates="league")
    matches = relationship("MatchORM", back_populates="league")
    player_stats = relationship("PlayerStatORM", back_populates="league")

class TeamORM(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True, autoincrement=True)
    league_id = Column(Integer, ForeignKey('leagues.id'))
    name = Column(String(255), nullable=False)
    logo_path = Column(String(255))

    league = relationship("LeagueORM", back_populates="teams")
    home_matches = relationship("MatchORM", foreign_keys='MatchORM.home_team_id', back_populates="home_team")
    away_matches = relationship("MatchORM", foreign_keys='MatchORM.away_team_id', back_populates="away_team")

class MatchORM(Base):
    __tablename__ = 'matches'

    id = Column(Integer, primary_key=True, autoincrement=True)
    league_id = Column(Integer, ForeignKey('leagues.id'))
    home_team_id = Column(Integer, ForeignKey('teams.id'))
    away_team_id = Column(Integer, ForeignKey('teams.id'))
    matchday = Column(Integer)
    match_date = Column(DateTime)
    home_score = Column(Integer, default=0)
    away_score = Column(Integer, default=0)
    is_finished = Column(Boolean, default=False)

    league = relationship("LeagueORM", back_populates="matches")
    home_team = relationship("TeamORM", foreign_keys=[home_team_id], back_populates="home_matches")
    away_team = relationship("TeamORM", foreign_keys=[away_team_id], back_populates="away_matches")

    goals = relationship("GoalORM", back_populates="match")
    cards = relationship("CardORM", back_populates="match")
    injuries = relationship("InjuryORM", back_populates="match")
    substitutions = relationship("SubstitutionORM", back_populates="match")
    penalties = relationship("PenaltyORM", back_populates="match")

class GoalORM(Base):
    __tablename__ = 'goals'

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey('matches.id'))
    team_id = Column(Integer, ForeignKey('teams.id'))
    player_name = Column(String(255), nullable=False)
    minute = Column(Integer)
    assist_player_name = Column(String(255))
    is_own_goal = Column(Boolean, default=False)
    is_penalty = Column(Boolean, default=False)

    match = relationship("MatchORM", back_populates="goals")

class CardORM(Base):
    __tablename__ = 'cards'

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey('matches.id'))
    team_id = Column(Integer, ForeignKey('teams.id'))
    player_name = Column(String(255), nullable=False)
    minute = Column(Integer)
    card_type = Column(String(50))
    reason = Column(Text)
    description = Column(Text)

    match = relationship("MatchORM", back_populates="cards")

class InjuryORM(Base):
    __tablename__ = 'injuries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey('matches.id'))
    team_id = Column(Integer, ForeignKey('teams.id'))
    player_name = Column(String(255), nullable=False)
    minute = Column(Integer)
    description = Column(Text)

    match = relationship("MatchORM", back_populates="injuries")

class SubstitutionORM(Base):
    __tablename__ = 'substitutions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey('matches.id'))
    team_id = Column(Integer, ForeignKey('teams.id'))
    player_in = Column(String(255), nullable=False)
    player_out = Column(String(255), nullable=False)
    minute = Column(Integer)

    match = relationship("MatchORM", back_populates="substitutions")

class PenaltyORM(Base):
    __tablename__ = 'penalties'

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey('matches.id'))
    team_id = Column(Integer, ForeignKey('teams.id'))
    player_name = Column(String(255))
    minute = Column(Integer)
    outcome = Column(String(50))
    description = Column(Text)

    match = relationship("MatchORM", back_populates="penalties")

class PlayerStatORM(Base):
    __tablename__ = 'player_stats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    league_id = Column(Integer, ForeignKey('leagues.id'))
    player_name = Column(String(255), nullable=False)
    team_name = Column(String(255), nullable=False)
    goals = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    matches_played = Column(Integer, default=0)
    updated_at = Column(DateTime)

    league = relationship("LeagueORM", back_populates="player_stats")

class ScrapedDataORM(Base):
    __tablename__ = 'scraped_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sport = Column(String(50), nullable=False)
    league = Column(String(100), nullable=False)
    season = Column(String(50))
    team_name = Column(String(255), nullable=False)
    position = Column(Integer)
    points = Column(Integer)
    matches_played = Column(Integer)
    wins = Column(Integer)
    draws = Column(Integer)
    losses = Column(Integer)
    goals_for = Column(Integer)
    goals_against = Column(Integer)
    goal_diff = Column(Integer)
    form = Column(String(50))
    updated_at = Column(DateTime)

class ScrapedMatchORM(Base):
    __tablename__ = 'scraped_matches'

    id = Column(Integer, primary_key=True, autoincrement=True)
    league = Column(String(100), nullable=False)
    season = Column(String(50))
    matchday = Column(String(50))
    date = Column(String(50))
    home_team = Column(String(255), nullable=False)
    away_team = Column(String(255), nullable=False)
    home_score = Column(Integer)
    away_score = Column(Integer)
    is_finished = Column(Boolean, default=False)
    scorers = Column(Text)
    updated_at = Column(DateTime)
    assists = Column(Text)
    yellow_cards = Column(Text)
    red_cards = Column(Text)
    substitutions = Column(Text)
    injuries = Column(Text)
    url = Column(Text)

# ==================== BASKETBALL ====================
class BasketballLeagueORM(Base):
    __tablename__ = 'basketball_leagues'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    country = Column(String(255))
    level = Column(String(50))

class BasketballSeasonORM(Base):
    __tablename__ = 'basketball_seasons'
    __table_args__ = (UniqueConstraint('league_id', 'season'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    league_id = Column(Integer, ForeignKey('basketball_leagues.id'), nullable=False)
    season = Column(String(50), nullable=False)
    start_date = Column(String(50))
    end_date = Column(String(50))

class BasketballTeamORM(Base):
    __tablename__ = 'basketball_teams'
    __table_args__ = (UniqueConstraint('league_id', 'name'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    league_id = Column(Integer, ForeignKey('basketball_leagues.id'), nullable=False)
    name = Column(String(255), nullable=False)
    short_name = Column(String(100))
    logo_path = Column(String(255))

class BasketballPlayerORM(Base):
    __tablename__ = 'basketball_players'

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(255), unique=True, nullable=False)
    nationality = Column(String(100))
    birth_date = Column(String(50))

class BasketballMatchORM(Base):
    __tablename__ = 'basketball_matches'
    __table_args__ = (UniqueConstraint('season_id', 'home_team_id', 'away_team_id', 'matchday'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    league_id = Column(Integer, ForeignKey('basketball_leagues.id'), nullable=False)
    season_id = Column(Integer, ForeignKey('basketball_seasons.id'), nullable=False)
    matchday = Column(Integer)
    match_date = Column(String(50))
    home_team_id = Column(Integer, ForeignKey('basketball_teams.id'), nullable=False)
    away_team_id = Column(Integer, ForeignKey('basketball_teams.id'), nullable=False)
    home_score = Column(Integer, default=0)
    away_score = Column(Integer, default=0)
    is_finished = Column(Boolean, default=False)
    venue = Column(String(255))
    referee = Column(String(255))
    source_url = Column(Text)

class BasketballStandings(Base):
    __tablename__ = 'basketball_standings'
    __table_args__ = (UniqueConstraint('season_id', 'team_id'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    season_id = Column(Integer, ForeignKey('basketball_seasons.id', ondelete='CASCADE'), nullable=False)
    team_id = Column(Integer, ForeignKey('basketball_teams.id'), nullable=False)
    position = Column(Integer)
    games_played = Column(Integer)
    wins = Column(Integer)
    losses = Column(Integer)
    points_for = Column(Integer)
    points_against = Column(Integer)
    point_diff = Column(Integer)
    streak = Column(String(50))
    updated_at = Column(String(50))

# ==================== TENNIS ====================
class TennisTournamentORM(Base):
    __tablename__ = 'tennis_tournaments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    tour = Column(String(50), nullable=False)
    category = Column(String(50))
    surface = Column(String(50))
    location = Column(String(255))
    country = Column(String(100))
    official_url = Column(Text)
    created_at = Column(DateTime)

class TennisPlayerORM(Base):
    __tablename__ = 'tennis_players'

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(255), unique=True, nullable=False)

class TennisEditionORM(Base):
    __tablename__ = 'tennis_editions'
    __table_args__ = (UniqueConstraint('tournament_id', 'year'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    tournament_id = Column(Integer, ForeignKey('tennis_tournaments.id', ondelete='CASCADE'), nullable=False)
    year = Column(Integer, nullable=False)
    winner_player_id = Column(Integer, ForeignKey('tennis_players.id'))
    runner_up_player_id = Column(Integer, ForeignKey('tennis_players.id'))
    score = Column(String(100))
    notes = Column(Text)
    source = Column(Text)
