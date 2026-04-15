from fastapi import FastAPI, HTTPException, Depends, status, Request, Response
# trigger reload to pick up updated .env for sqlite
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import timedelta
from typing import List, Optional
from pathlib import Path
from sqlalchemy import Integer
from sqlalchemy.orm import aliased
from .models import *
from .database import SessionLocal
from .database_orm import (UserORM, LeagueORM, TeamORM, MatchORM, GoalORM, CardORM,
                            InjuryORM, SubstitutionORM, PenaltyORM, PlayerStatORM,
                            ScrapedDataORM, ScrapedMatchORM,
                            BasketballLeagueORM, BasketballSeasonORM, BasketballTeamORM,
                            BasketballMatchORM, BasketballStandings)
from .cookie_auth import session_cookie_manager, authenticate_user, get_user_by_username
from .auth import get_password_hash
from .config import ALLOWED_ORIGINS, ACCESS_TOKEN_EXPIRE_MINUTES
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .scrapers.manager import start_all_scrapers
from contextlib import asynccontextmanager


# Configurar rutas de archivos
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = BASE_DIR / "images"

app = FastAPI(
    title="Football Leagues API",
    description="API para estadísticas de LaLiga EA Sports, Hypermotion, Bundesliga, Serie A y Premier League",
    version="1.0.0"
)

# Scheduler Setup
scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def start_scheduler():
    start_all_scrapers(scheduler)
    scheduler.start()
    # Run once on startup
    # update_scraped_data_job() # Optional: run synchronously or background

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar SessionMiddleware para cookies
app.add_middleware(
    SessionMiddleware,
    secret_key="Omniscore_session_secret_key_change_in_production",
    session_cookie="Omniscore_session",
    max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convertir a segundos
    same_site="lax",
    https_only=False  # En producción poner True
)

# Configurar templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Montar directorios estáticos
app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")
app.mount("/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")

# ==================== AUTH ENDPOINTS ====================

@app.post("/api/auth/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """Registra un nuevo usuario"""
    with SessionLocal() as session:
        # Verificar si el usuario ya existe
        existing_user = session.query(UserORM).filter(
            (UserORM.username == user.username) | (UserORM.email == user.email)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario o email ya existe"
            )
        
        # Crear usuario
        hashed_password = get_password_hash(user.password)
        new_user = UserORM(
            username=user.username,
            email=user.email,
            password=hashed_password,
            full_name=user.full_name
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        
        return User(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            full_name=new_user.full_name,
            created_at=str(new_user.created_at) if new_user.created_at else None
        )

@app.post("/api/auth/login")
async def login(user_login: UserLogin, request: Request, response: Response):
    """Inicia sesión y establece cookie de sesión"""
    user = authenticate_user(user_login.username, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
        )
    
    # Crear sesión persistente
    session_id = session_cookie_manager.create_session(user)
    
    # Establecer cookie
    response.set_cookie(
        key="Omniscore_session",
        value=session_id,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        path="/",
        samesite="lax",
        httponly=True,
        secure=False  # En producción poner True
    )
    
    # Guardar sesión en request para uso inmediato
    request.session["session_id"] = session_id
    request.session["user"] = user
    
    return {"message": "Login exitoso", "user": {"id": user["id"], "username": user["username"], "email": user["email"], "full_name": user["full_name"]}}

@app.post("/api/auth/logout")
async def logout(request: Request, response: Response):
    """Cierra sesión y elimina cookie"""
    session_id = request.session.get("session_id")
    if session_id:
        session_cookie_manager.remove_session(session_id)
    
    # Eliminar cookie
    response.delete_cookie(
        key="Omniscore_session",
        path="/",
        samesite="lax"
    )
    
    # Limpiar sesión
    request.session.clear()
    
    return {"message": "Logout exitoso"}

@app.post("/api/auth/reset-password")
async def reset_password(data: PasswordReset):
    """Restablecer la contraseña"""
    with SessionLocal() as session:
        user = session.query(UserORM).filter(
            (UserORM.username == data.username) | (UserORM.email == data.username)
        ).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        user.password = get_password_hash(data.new_password)
        session.commit()
        return {"message": "Contraseña actualizada correctamente"}

async def get_current_user(request: Request) -> User:
    """Obtiene el usuario actual desde cookie de sesión"""
    session_id = request.session.get("session_id")
    if not session_id:
        # Verificar si existe en cookie HTTP
        session_id = request.cookies.get("Omniscore_session")
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se encontró sesión activa",
        )
    
    session_data = session_cookie_manager.get_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión expirada o inválida",
        )
    
    user_data = session_data['user_data']
    return User(**user_data)

@app.get("/api/auth/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    """Obtiene la información del usuario actual"""
    return current_user

# ==================== LEAGUES ENDPOINTS ====================

@app.get("/api/leagues", response_model=List[League])
async def get_leagues():
    """Obtiene todas las ligas disponibles"""
    with SessionLocal() as session:
        leagues = session.query(LeagueORM).order_by(LeagueORM.id).all()
        return [{"id": l.id, "name": l.name, "country": l.country} for l in leagues]

@app.get("/api/leagues/{league_id}", response_model=League)
async def get_league(league_id: int):
    """Obtiene una liga específica por ID"""
    with SessionLocal() as session:
        league = session.query(LeagueORM).filter(LeagueORM.id == league_id).first()
        if not league:
            raise HTTPException(status_code=404, detail="Liga no encontrada")
        return {"id": league.id, "name": league.name, "country": league.country}

# ==================== TEAMS ENDPOINTS ====================

@app.get("/api/teams", response_model=List[TeamWithLeague])
async def get_teams(league_id: Optional[int] = None):
    """Obtiene todos los equipos, opcionalmente filtrados por liga"""
    with SessionLocal() as session:
        query = session.query(TeamORM).join(LeagueORM)
        if league_id:
            query = query.filter(TeamORM.league_id == league_id)
        
        # Order by league id then team name
        teams_orm = query.order_by(TeamORM.league_id, TeamORM.name).all()
        
        teams = []
        for t in teams_orm:
            teams.append({
                "id": t.id,
                "league_id": t.league_id,
                "name": t.name,
                "logo_path": t.logo_path,
                "league_name": t.league.name if t.league else "",
                "league_country": t.league.country if t.league else ""
            })
        return teams

@app.get("/api/teams/{team_id}", response_model=TeamWithLeague)
async def get_team(team_id: int):
    """Obtiene un equipo específico por ID"""
    with SessionLocal() as session:
        t = session.query(TeamORM).filter(TeamORM.id == team_id).first()
        if not t:
            raise HTTPException(status_code=404, detail="Equipo no encontrado")
            
        return {
            "id": t.id,
            "league_id": t.league_id,
            "name": t.name,
            "logo_path": t.logo_path,
            "league_name": t.league.name if t.league else "",
            "league_country": t.league.country if t.league else ""
        }

# ==================== MATCHES ENDPOINTS ====================

@app.get("/api/matches", response_model=List[MatchDetail])
async def get_matches(
    league_id: Optional[int] = None,
    matchday: Optional[int] = None,
    team_id: Optional[int] = None
):
    """Obtiene partidos con filtros opcionales"""
    with SessionLocal() as session:
        q = session.query(MatchORM)
        if league_id:
            q = q.filter(MatchORM.league_id == league_id)
        if matchday:
            q = q.filter(MatchORM.matchday == matchday)
        if team_id:
            q = q.filter((MatchORM.home_team_id == team_id) | (MatchORM.away_team_id == team_id))

        matches_orm = q.order_by(MatchORM.matchday, MatchORM.match_date).all()

        def serialize_match(m):
            return {
                "id": m.id, "league_id": m.league_id,
                "home_team_id": m.home_team_id, "away_team_id": m.away_team_id,
                "matchday": m.matchday, "match_date": str(m.match_date) if m.match_date else None,
                "home_score": m.home_score, "away_score": m.away_score,
                "is_finished": m.is_finished,
                "league_name": m.league.name if m.league else "",
                "home_team_name": m.home_team.name if m.home_team else "",
                "away_team_name": m.away_team.name if m.away_team else "",
                "goals": [{"id": g.id, "player_name": g.player_name, "minute": g.minute,
                           "team_id": g.team_id, "assist_player_name": g.assist_player_name,
                           "is_own_goal": g.is_own_goal, "is_penalty": g.is_penalty} for g in sorted(m.goals, key=lambda x: x.minute or 0)],
                "cards": [{"id": c.id, "player_name": c.player_name, "minute": c.minute,
                           "team_id": c.team_id, "card_type": c.card_type, "reason": c.reason} for c in sorted(m.cards, key=lambda x: x.minute or 0)],
                "injuries": [{"id": i.id, "player_name": i.player_name, "minute": i.minute,
                              "team_id": i.team_id, "description": i.description} for i in sorted(m.injuries, key=lambda x: x.minute or 0)],
                "substitutions": [{"id": s.id, "player_in": s.player_in, "player_out": s.player_out,
                                   "minute": s.minute, "team_id": s.team_id} for s in sorted(m.substitutions, key=lambda x: x.minute or 0)],
                "penalties": [{"id": p.id, "player_name": p.player_name, "minute": p.minute,
                               "team_id": p.team_id, "outcome": p.outcome, "description": p.description} for p in sorted(m.penalties, key=lambda x: x.minute or 0)],
            }
        return [serialize_match(m) for m in matches_orm]

@app.get("/api/matches/{match_id}", response_model=MatchDetail)
async def get_match(match_id: int):
    """Obtiene detalles completos de un partido específico"""
    with SessionLocal() as session:
        m = session.query(MatchORM).filter(MatchORM.id == match_id).first()
        if not m:
            raise HTTPException(status_code=404, detail="Partido no encontrado")

        return {
            "id": m.id, "league_id": m.league_id,
            "home_team_id": m.home_team_id, "away_team_id": m.away_team_id,
            "matchday": m.matchday, "match_date": str(m.match_date) if m.match_date else None,
            "home_score": m.home_score, "away_score": m.away_score,
            "is_finished": m.is_finished,
            "league_name": m.league.name if m.league else "",
            "home_team_name": m.home_team.name if m.home_team else "",
            "away_team_name": m.away_team.name if m.away_team else "",
            "goals": [{"id": g.id, "player_name": g.player_name, "minute": g.minute,
                       "team_id": g.team_id, "assist_player_name": g.assist_player_name,
                       "is_own_goal": g.is_own_goal, "is_penalty": g.is_penalty} for g in sorted(m.goals, key=lambda x: x.minute or 0)],
            "cards": [{"id": c.id, "player_name": c.player_name, "minute": c.minute,
                       "team_id": c.team_id, "card_type": c.card_type, "reason": c.reason} for c in sorted(m.cards, key=lambda x: x.minute or 0)],
            "injuries": [{"id": i.id, "player_name": i.player_name, "minute": i.minute,
                          "team_id": i.team_id, "description": i.description} for i in sorted(m.injuries, key=lambda x: x.minute or 0)],
            "substitutions": [{"id": s.id, "player_in": s.player_in, "player_out": s.player_out,
                               "minute": s.minute, "team_id": s.team_id} for s in sorted(m.substitutions, key=lambda x: x.minute or 0)],
            "penalties": [{"id": p.id, "player_name": p.player_name, "minute": p.minute,
                           "team_id": p.team_id, "outcome": p.outcome, "description": p.description} for p in sorted(m.penalties, key=lambda x: x.minute or 0)],
        }

# ==================== STATISTICS ENDPOINTS ====================

@app.get("/api/standings/{league_id}", response_model=List[Standing])
async def get_standings(league_id: int):
    """Obtiene la clasificación de una liga"""
    with SessionLocal() as session:
        # Verificar que la liga existe
        league = session.query(LeagueORM).filter(LeagueORM.id == league_id).first()
        if not league:
            raise HTTPException(status_code=404, detail="Liga no encontrada")

        # Obtener todos los equipos de la liga
        teams = session.query(TeamORM).filter(TeamORM.league_id == league_id).all()

        # Obtener todos los partidos terminados de la liga
        matches = (
            session.query(MatchORM)
            .filter(MatchORM.league_id == league_id, MatchORM.is_finished == True)
            .all()
        )

        # Calcular estadisticas por equipo en Python
        stats = {}
        for t in teams:
            stats[t.id] = {
                "team_id": t.id, "team_name": t.name, "logo": t.logo_path,
                "matches_played": 0, "wins": 0, "draws": 0, "losses": 0,
                "goals_for": 0, "goals_against": 0
            }

        for m in matches:
            home_id, away_id = m.home_team_id, m.away_team_id
            hs, as_ = m.home_score or 0, m.away_score or 0

            if home_id in stats:
                stats[home_id]["matches_played"] += 1
                stats[home_id]["goals_for"] += hs
                stats[home_id]["goals_against"] += as_
                if hs > as_: stats[home_id]["wins"] += 1
                elif hs == as_: stats[home_id]["draws"] += 1
                else: stats[home_id]["losses"] += 1

            if away_id in stats:
                stats[away_id]["matches_played"] += 1
                stats[away_id]["goals_for"] += as_
                stats[away_id]["goals_against"] += hs
                if as_ > hs: stats[away_id]["wins"] += 1
                elif as_ == hs: stats[away_id]["draws"] += 1
                else: stats[away_id]["losses"] += 1

        # Ordenar por puntos, diferencia de goles, goles a favor
        rows = sorted(
            stats.values(),
            key=lambda x: (x["wins"]*3 + x["draws"], x["goals_for"] - x["goals_against"], x["goals_for"]),
            reverse=True
        )

        return [
            {
                "position": i + 1,
                "team_id": r["team_id"],
                "team_name": r["team_name"],
                "matches_played": r["matches_played"],
                "wins": r["wins"],
                "draws": r["draws"],
                "losses": r["losses"],
                "goals_for": r["goals_for"],
                "goals_against": r["goals_against"],
                "goal_difference": r["goals_for"] - r["goals_against"],
                "points": r["wins"]*3 + r["draws"],
            }
            for i, r in enumerate(rows)
        ]

@app.get("/api/top-scorers/{league_id}", response_model=List[TopScorer])
async def get_top_scorers(league_id: int, limit: int = 20):
    """Obtiene los máximos goleadores de una liga"""
    with SessionLocal() as session:
        # Primero comprobar si hay datos en player_stats
        count = session.query(PlayerStatORM).filter(PlayerStatORM.league_id == league_id).count()

        if count > 0:
            rows = (
                session.query(PlayerStatORM)
                .filter(PlayerStatORM.league_id == league_id)
                .order_by(PlayerStatORM.goals.desc(), PlayerStatORM.assists.desc())
                .limit(limit)
                .all()
            )
            return [{"player_name": r.player_name, "team_name": r.team_name, "goals": r.goals, "penalties": 0} for r in rows]
        else:
            # Fallback: calcular desde tabla goals
            from sqlalchemy import func
            rows = (
                session.query(
                    GoalORM.player_name,
                    TeamORM.name.label("team_name"),
                    func.count(GoalORM.id).label("goals"),
                    func.sum(
                        func.cast(GoalORM.is_penalty, Integer)
                    ).label("penalties")
                )
                .join(MatchORM, GoalORM.match_id == MatchORM.id)
                .join(TeamORM, GoalORM.team_id == TeamORM.id)
                .filter(MatchORM.league_id == league_id, GoalORM.is_own_goal == False)
                .group_by(GoalORM.player_name, TeamORM.name)
                .order_by(func.count(GoalORM.id).desc())
                .limit(limit)
                .all()
            )
            return [{"player_name": r.player_name, "team_name": r.team_name, "goals": r.goals or 0, "penalties": r.penalties or 0} for r in rows]

@app.get("/api/top-assisters/{league_id}", response_model=List[TopAssister])
async def get_top_assisters(league_id: int, limit: int = 20):
    """Obtiene los máximos asistentes de una liga"""
    with SessionLocal() as session:
        count = session.query(PlayerStatORM).filter(PlayerStatORM.league_id == league_id).count()

        if count > 0:
            rows = (
                session.query(PlayerStatORM)
                .filter(PlayerStatORM.league_id == league_id)
                .order_by(PlayerStatORM.assists.desc(), PlayerStatORM.goals.desc())
                .limit(limit)
                .all()
            )
            return [{"player_name": r.player_name, "team_name": r.team_name, "assists": r.assists} for r in rows]
        else:
            from sqlalchemy import func
            rows = (
                session.query(
                    GoalORM.assist_player_name.label("player_name"),
                    TeamORM.name.label("team_name"),
                    func.count(GoalORM.id).label("assists")
                )
                .join(MatchORM, GoalORM.match_id == MatchORM.id)
                .join(TeamORM, GoalORM.team_id == TeamORM.id)
                .filter(
                    MatchORM.league_id == league_id,
                    GoalORM.assist_player_name.isnot(None),
                    GoalORM.assist_player_name != ""
                )
                .group_by(GoalORM.assist_player_name, TeamORM.name)
                .order_by(func.count(GoalORM.id).desc())
                .limit(limit)
                .all()
            )
            return [{"player_name": r.player_name, "team_name": r.team_name, "assists": r.assists or 0} for r in rows]

@app.get("/api/player-stats/{player_name}")
async def get_player_stats(player_name: str, league_id: Optional[int] = None):
    """Obtiene estadísticas completas de un jugador"""
    from sqlalchemy import func
    with SessionLocal() as session:
        # Goals y penaltis
        goals_q = session.query(
            func.count(GoalORM.id).label("total_goals"),
            func.sum(func.cast(GoalORM.is_penalty, Integer)).label("penalties")
        ).join(MatchORM, GoalORM.match_id == MatchORM.id).filter(GoalORM.player_name == player_name)
        if league_id:
            goals_q = goals_q.filter(MatchORM.league_id == league_id)
        goals_data = goals_q.one()

        # Asistencias
        assists_q = session.query(
            func.count(GoalORM.id).label("total_assists")
        ).join(MatchORM, GoalORM.match_id == MatchORM.id).filter(GoalORM.assist_player_name == player_name)
        if league_id:
            assists_q = assists_q.filter(MatchORM.league_id == league_id)
        assists_data = assists_q.one()

        # Tarjetas
        cards_q = session.query(
            func.sum(func.cast(CardORM.card_type == 'Amarilla', Integer)).label("yellow_cards"),
            func.sum(func.cast(CardORM.card_type == 'Roja', Integer)).label("red_cards")
        ).join(MatchORM, CardORM.match_id == MatchORM.id).filter(CardORM.player_name == player_name)
        if league_id:
            cards_q = cards_q.filter(MatchORM.league_id == league_id)
        cards_data = cards_q.one()

        return {
            "player_name": player_name,
            "goals": goals_data.total_goals or 0,
            "penalties": goals_data.penalties or 0,
            "assists": assists_data.total_assists or 0,
            "yellow_cards": cards_data.yellow_cards or 0,
            "red_cards": cards_data.red_cards or 0
        }

# ==================== SCRAPED DATA ENDPOINTS ====================

@app.get("/api/scraped-standings/{league_name}")
async def get_scraped_standings(league_name: str):
    """Obtiene la clasificación scrapeada con logos mapeados"""
    with SessionLocal() as session:
        # 1. Obtener datos scrapeados
        scraped_rows = (
            session.query(ScrapedDataORM)
            .filter(ScrapedDataORM.league == league_name)
            .order_by(ScrapedDataORM.position.asc())
            .all()
        )
        # 2. Obtener todos los equipos locales para mapear logos
        local_teams = session.query(TeamORM).all()

        manual_map = {
            'athletic club': 'athletic', 'c.a. osasuna': 'osasuna', 'osasuna': 'osasuna',
            'deportivo alavés': 'alavés', 'alavés': 'alavés',
            'rcd espanyol de barcelona': 'espanyol', 'rcd espanyol': 'espanyol', 'espanyol': 'espanyol',
            'sevilla fc': 'sevilla', 'real betis': 'betis', 'villarreal cf': 'villarreal',
            'villareal': 'villarreal', 'rc celta': 'celta', 'celta de vigo': 'celta', 'celta': 'celta',
            'girona fc': 'girona', 'rayo vallecano': 'rayo', 'real sociedad': 'sociedad',
            'valencia cf': 'valencia', 'getafe cf': 'getafe', 'rcd mallorca': 'mallorca',
            'ud las palmas': 'palmas', 'cd leganés': 'leganés', 'real valladolid': 'valladolid',
            'fc barcelona': 'barcelona', 'atlético de madrid': 'atletico', 'atlético': 'atletico',
            'real madrid': 'real madrid', 'real oviedo': 'oviedo', 'levante ud': 'levante',
            'cologne': 'fc koln', '1. fc köln': 'fc koln', '1. fc koln': 'fc koln',
            'borussia dortmund': 'dortmund', 'rb leipzig': 'leipzig', 'vfb stuttgart': 'stuttgart',
            'bayer leverkusen': 'leverkusen', 'bayer 04 leverkusen': 'leverkusen',
            'borussia mönchengladbach': 'gladbach', 'borussia monchengladbach': 'gladbach', 'gladbach': 'gladbach',
            'eintracht frankfurt': 'frankfurt', 'tsg hoffenheim': 'hoffenheim', 'hoffenheim': 'hoffenheim',
            '1. fc union berlin': 'union berlin', 'union berlin': 'union berlin',
            'sc freiburg': 'freiburg', 'sv werder bremen': 'bremen', 'werder bremen': 'bremen',
            'vfl wolfsburg': 'wolfsburg', 'fc augsburg': 'augsburg', 'augsburg': 'augsburg',
            '1. fsv mainz 05': 'mainz', 'mainz 05': 'mainz', 'mainz': 'mainz',
            'hamburger sv': 'hamburgo', 'fc st. pauli': 'st. pauli', 'st. pauli': 'st. pauli',
            '1. fc heidenheim 1846': 'heidenheim', 'heidenheim': 'heidenheim', 'holstein kiel': 'kiel'
        }

        result = []
        sorted_keys = sorted(manual_map.keys(), key=len, reverse=True)

        for row in scraped_rows:
            scraped_name = row.team_name.lower().strip()
            logo = None
            search_term = None
            for k in sorted_keys:
                if k in scraped_name:
                    search_term = manual_map[k]
                    break

            if search_term:
                if search_term == 'real madrid':
                    logo = next((t.logo_path for t in local_teams if t.name.lower() == 'real madrid'), None)
                elif search_term == 'villarreal':
                    logo = next((t.logo_path for t in local_teams if t.name.lower() == 'villarreal'), None)
                else:
                    logo = next((t.logo_path for t in local_teams if search_term in t.name.lower()), None)

            if not logo:
                for t in local_teams:
                    db_name = t.name.lower()
                    if db_name == 'real madrid' and 'atletico' in scraped_name:
                        continue
                    if db_name in scraped_name or scraped_name in db_name:
                        logo = t.logo_path
                        break

            result.append({
                "id": row.id, "sport": row.sport, "league": row.league, "season": row.season,
                "team_name": row.team_name, "position": row.position, "points": row.points,
                "matches_played": row.matches_played, "wins": row.wins, "draws": row.draws,
                "losses": row.losses, "goals_for": row.goals_for, "goals_against": row.goals_against,
                "goal_diff": row.goal_diff, "form": row.form, "logo": logo
            })
        return result


# ==================== BASKETBALL (NEW DB) ENDPOINTS ====================

@app.get("/api/basket/leagues", response_model=List[BasketballLeague])
async def get_basket_leagues():
    """Obtiene todas las ligas de baloncesto disponibles"""
    with SessionLocal() as session:
        leagues = session.query(BasketballLeagueORM).order_by(BasketballLeagueORM.name).all()
        return [{"id": l.id, "name": l.name, "country": l.country, "level": l.level} for l in leagues]


@app.get("/api/basket/seasons", response_model=List[BasketballSeason])
async def get_basket_seasons(league_id: Optional[int] = None):
    """Obtiene temporadas de baloncesto, opcionalmente filtradas por liga"""
    with SessionLocal() as session:
        q = session.query(BasketballSeasonORM)
        if league_id:
            q = q.filter(BasketballSeasonORM.league_id == league_id)
        seasons = q.order_by(BasketballSeasonORM.season.desc()).all()
        return [{
            "id": s.id, "league_id": s.league_id,
            "season": s.season, "start_date": s.start_date, "end_date": s.end_date
        } for s in seasons]


@app.get("/api/basket/standings", response_model=List[BasketballStanding])
async def get_basket_standings(season_id: int):
    """Obtiene la clasificación para una temporada concreta"""
    with SessionLocal() as session:
        rows = (
            session.query(BasketballStandings, BasketballTeamORM.name)
            .join(BasketballTeamORM, BasketballStandings.team_id == BasketballTeamORM.id)
            .filter(BasketballStandings.season_id == season_id)
            .order_by(BasketballStandings.position.asc(), BasketballTeamORM.name.asc())
            .all()
        )
        return [{
            "position": s.position,
            "team_id": s.team_id,
            "team_name": name,
            "games_played": s.games_played,
            "wins": s.wins,
            "losses": s.losses,
            "points_for": s.points_for,
            "points_against": s.points_against,
            "point_diff": s.point_diff
        } for s, name in rows]


@app.get("/api/basket/matches", response_model=List[BasketballMatch])
async def get_basket_matches(
    season_id: int,
    matchday: Optional[int] = None,
    team_id: Optional[int] = None,
):
    """Obtiene partidos de baloncesto por temporada con filtros opcionales"""
    with SessionLocal() as session:
        q = session.query(BasketballMatchORM).filter(BasketballMatchORM.season_id == season_id)
        if matchday is not None:
            q = q.filter(BasketballMatchORM.matchday == matchday)
        if team_id is not None:
            q = q.filter(
                (BasketballMatchORM.home_team_id == team_id) | (BasketballMatchORM.away_team_id == team_id)
            )
        matches = q.order_by(BasketballMatchORM.matchday.asc(), BasketballMatchORM.match_date.asc()).all()

        result = []
        for m in matches:
            home = session.query(BasketballTeamORM).filter(BasketballTeamORM.id == m.home_team_id).first()
            away = session.query(BasketballTeamORM).filter(BasketballTeamORM.id == m.away_team_id).first()
            result.append({
                "id": m.id, "league_id": m.league_id, "season_id": m.season_id,
                "matchday": m.matchday, "match_date": m.match_date,
                "home_team_id": m.home_team_id, "away_team_id": m.away_team_id,
                "home_team_name": home.name if home else "",
                "away_team_name": away.name if away else "",
                "home_score": m.home_score, "away_score": m.away_score,
                "is_finished": bool(m.is_finished)
            })
        return result

@app.get("/api/scraped-matches/{league_name}")
async def get_scraped_matches(league_name: str, season: str = None):
    """Obtiene los partidos scrapeados/simulados para una liga con detalles completos.
    Si no hay eventos vinculados directamente al scraped_match, hace cruce con MatchORM."""
    with SessionLocal() as session:
        q = session.query(ScrapedMatchORM).filter(ScrapedMatchORM.league == league_name)
        if season:
            q = q.filter(ScrapedMatchORM.season == season)
        else:
            latest = (
                session.query(ScrapedMatchORM.season)
                .filter(ScrapedMatchORM.league == league_name)
                .order_by(ScrapedMatchORM.season.desc())
                .first()
            )
            if latest:
                q = q.filter(ScrapedMatchORM.season == latest[0])

        scraped_list = q.order_by(ScrapedMatchORM.date.desc()).all()
        if not scraped_list:
            return []

        scraped_match_ids = [m.id for m in scraped_list]

        # Batch fetch por IDs de scraped_matches
        cards_by_sid = {}
        subs_by_sid = {}
        inj_by_sid = {}
        goals_by_sid = {}

        for c, tname in session.query(CardORM, TeamORM.name).outerjoin(TeamORM, CardORM.team_id == TeamORM.id).filter(CardORM.match_id.in_(scraped_match_ids)).order_by(CardORM.minute).all():
            cards_by_sid.setdefault(c.match_id, []).append({"player": c.player_name, "type": c.card_type, "minute": c.minute, "reason": c.reason, "team": tname})
        for s, tname in session.query(SubstitutionORM, TeamORM.name).outerjoin(TeamORM, SubstitutionORM.team_id == TeamORM.id).filter(SubstitutionORM.match_id.in_(scraped_match_ids)).order_by(SubstitutionORM.minute).all():
            subs_by_sid.setdefault(s.match_id, []).append({"player_in": s.player_in, "player_out": s.player_out, "minute": s.minute, "team": tname})
        for i, tname in session.query(InjuryORM, TeamORM.name).outerjoin(TeamORM, InjuryORM.team_id == TeamORM.id).filter(InjuryORM.match_id.in_(scraped_match_ids)).order_by(InjuryORM.minute).all():
            inj_by_sid.setdefault(i.match_id, []).append({"player": i.player_name, "minute": i.minute, "description": i.description, "team": tname})
        for g, tname in session.query(GoalORM, TeamORM.name).outerjoin(TeamORM, GoalORM.team_id == TeamORM.id).filter(GoalORM.match_id.in_(scraped_match_ids)).order_by(GoalORM.minute).all():
            goals_by_sid.setdefault(g.match_id, []).append({"player": g.player_name, "minute": g.minute, "is_own": bool(g.is_own_goal), "is_penalty": bool(g.is_penalty), "assist": g.assist_player_name, "team": tname})

        # Cruce con MatchORM (cuando los eventos tienen match_id de matches, no de scraped_matches)
        league_orm = session.query(LeagueORM).filter(LeagueORM.name == league_name).first()
        orm_id_lookup = {}  # (jornada_int, norm_home, norm_away) -> orm_match_id
        cross_goals = {}
        cross_cards = {}
        cross_subs = {}
        cross_inj = {}

        def _n(name):
            s = name.lower().strip()
            for full, short in [
                ('brighton & hove albion', 'brighton'), ('brighton and hove albion', 'brighton'),
                ('manchester city', 'man city'), ('manchester united', 'man utd'),
                ('nottingham forest', 'nottm forest'), ('wolverhampton wanderers', 'wolves'),
                ('wolverhampton', 'wolves'), ('west ham united', 'west ham'),
                ('newcastle united', 'newcastle'), ('tottenham hotspur', 'tottenham'),
                ('afc bournemouth', 'bournemouth'),
            ]:
                if full in s:
                    s = s.replace(full, short)
            return s

        def _jn(matchday_str):
            if not matchday_str:
                return None
            raw = matchday_str.lower().replace('jornada', '').replace('j', '').strip()
            # Manejar formato "Jornada 1.0" -> extraer solo el número antes del punto
            if '.' in raw:
                raw = raw.split('.')[0]
            try:
                return int(raw)
            except ValueError:
                return None

        if league_orm:
            HT = aliased(TeamORM)
            AT = aliased(TeamORM)
            orm_rows = (
                session.query(MatchORM.id, MatchORM.matchday, HT.name, AT.name)
                .join(HT, MatchORM.home_team_id == HT.id)
                .join(AT, MatchORM.away_team_id == AT.id)
                .filter(MatchORM.league_id == league_orm.id)
                .all()
            )
            for oid, jornada, hname, aname in orm_rows:
                orm_id_lookup[(jornada, _n(hname), _n(aname))] = oid

            # Also build a lookup by team pair (ignoring matchday/order) for flexible fallback
            orm_by_teams = {}  # (norm_a, norm_b) -> orm_match_id  (teams alphabetically sorted)
            for (jd, kh, ka), v in orm_id_lookup.items():
                key = tuple(sorted([kh, ka]))
                if key not in orm_by_teams:  # take first encounter
                    orm_by_teams[key] = v

            orm_ids_needed = set()
            for m in scraped_list:
                mid = m.id
                if not goals_by_sid.get(mid) and not cards_by_sid.get(mid) and not subs_by_sid.get(mid):
                    jn = _jn(m.matchday)
                    nh, na = _n(m.home_team), _n(m.away_team)
                    # 1. Exact match: jornada + home + away
                    oid = orm_id_lookup.get((jn, nh, na))
                    # 2. Flexible: any jornada, home+away coincide (partial)
                    if not oid:
                        for (jd, kh, ka), v in orm_id_lookup.items():
                            if (kh == nh or nh in kh or kh in nh) and (ka == na or na in ka or ka in na):
                                oid = v
                                break
                    # 3. Flexible: any jornada, teams match regardless of order
                    if not oid:
                        team_key = tuple(sorted([nh, na]))
                        oid = orm_by_teams.get(team_key)
                    if oid:
                        orm_ids_needed.add(oid)

            if orm_ids_needed:
                oid_list = list(orm_ids_needed)
                for g, tname in session.query(GoalORM, TeamORM.name).outerjoin(TeamORM, GoalORM.team_id == TeamORM.id).filter(GoalORM.match_id.in_(oid_list)).order_by(GoalORM.minute).all():
                    cross_goals.setdefault(g.match_id, []).append({"player": g.player_name, "minute": g.minute, "is_own": bool(g.is_own_goal), "is_penalty": bool(g.is_penalty), "assist": g.assist_player_name, "team": tname})
                for c, tname in session.query(CardORM, TeamORM.name).outerjoin(TeamORM, CardORM.team_id == TeamORM.id).filter(CardORM.match_id.in_(oid_list)).order_by(CardORM.minute).all():
                    cross_cards.setdefault(c.match_id, []).append({"player": c.player_name, "type": c.card_type, "minute": c.minute, "reason": c.reason, "team": tname})
                for s, tname in session.query(SubstitutionORM, TeamORM.name).outerjoin(TeamORM, SubstitutionORM.team_id == TeamORM.id).filter(SubstitutionORM.match_id.in_(oid_list)).order_by(SubstitutionORM.minute).all():
                    cross_subs.setdefault(s.match_id, []).append({"player_in": s.player_in, "player_out": s.player_out, "minute": s.minute, "team": tname})
                for i, tname in session.query(InjuryORM, TeamORM.name).outerjoin(TeamORM, InjuryORM.team_id == TeamORM.id).filter(InjuryORM.match_id.in_(oid_list)).order_by(InjuryORM.minute).all():
                    cross_inj.setdefault(i.match_id, []).append({"player": i.player_name, "minute": i.minute, "description": i.description, "team": tname})

        import json
        result = []
        for m in scraped_list:
            mid = m.id
            rel_goals    = goals_by_sid.get(mid, [])
            rel_cards    = cards_by_sid.get(mid, [])
            rel_subs     = subs_by_sid.get(mid, [])
            rel_injuries = inj_by_sid.get(mid, [])

            # Si no hay eventos directos, usar los del cruce con MatchORM
            if not rel_goals and not rel_cards and not rel_subs and league_orm:
                jn = _jn(m.matchday)
                nh, na = _n(m.home_team), _n(m.away_team)
                # 1. Exact match
                oid = orm_id_lookup.get((jn, nh, na))
                # 2. Any jornada, same home+away
                if not oid:
                    for (jd, kh, ka), v in orm_id_lookup.items():
                        if (kh == nh or nh in kh or kh in nh) and (ka == na or na in ka or ka in na):
                            oid = v
                            break
                # 3. Any jornada, teams match (regardless of home/away order)
                if not oid:
                    team_key = tuple(sorted([nh, na]))
                    oid = orm_by_teams.get(team_key)
                if oid:
                    rel_goals    = cross_goals.get(oid, [])
                    rel_cards    = cross_cards.get(oid, [])
                    rel_subs     = cross_subs.get(oid, [])
                    rel_injuries = cross_inj.get(oid, [])

            # Cards fallback JSON
            if rel_cards:
                cards = rel_cards
            elif m.yellow_cards or m.red_cards:
                cards = []
                try:
                    if m.yellow_cards:
                        for c in json.loads(m.yellow_cards): cards.append({'formatted': c, 'minute': '', 'type': 'Amarilla', 'player': ''})
                    if m.red_cards:
                        for c in json.loads(m.red_cards): cards.append({'formatted': c, 'minute': '', 'type': 'Roja', 'player': ''})
                except: pass
            else:
                cards = []

            # Subs fallback JSON
            if rel_subs:
                subs = rel_subs
            elif m.substitutions:
                try:
                    subs = json.loads(m.substitutions)
                except:
                    subs = []
            else:
                subs = []

            result.append({
                "id": m.id, "league": m.league, "season": m.season,
                "matchday": m.matchday, "date": m.date,
                "home_team": m.home_team, "away_team": m.away_team,
                "home_score": m.home_score, "away_score": m.away_score,
                "is_finished": bool(m.is_finished),
                "scorers": m.scorers, "url": m.url,
                "cards": cards,
                "substitutions": subs,
                "injuries": rel_injuries,
                "goals_details": rel_goals
            })
        return result

@app.get("/api/scraped-scorers/{league_name}")
async def get_scraped_scorers(league_name: str):
    """Obtiene máximos goleadores scrapeados"""
    with SessionLocal() as session:
        rows = (
            session.query(PlayerStatORM)
            .join(LeagueORM, PlayerStatORM.league_id == LeagueORM.id)
            .filter(LeagueORM.name == league_name)
            .order_by(PlayerStatORM.goals.desc(), PlayerStatORM.assists.desc())
            .limit(20)
            .all()
        )
        return [{
            "id": r.id, "league_id": r.league_id, "player_name": r.player_name,
            "team_name": r.team_name, "goals": r.goals, "assists": r.assists,
            "matches_played": r.matches_played
        } for r in rows]

@app.get("/api/scraped-assisters/{league_name}")
async def get_scraped_assisters(league_name: str):
    """Obtiene máximos asistentes scrapeados"""
    with SessionLocal() as session:
        rows = (
            session.query(PlayerStatORM)
            .join(LeagueORM, PlayerStatORM.league_id == LeagueORM.id)
            .filter(LeagueORM.name == league_name)
            .order_by(PlayerStatORM.assists.desc(), PlayerStatORM.goals.desc())
            .limit(20)
            .all()
        )
        return [{
            "id": r.id, "league_id": r.league_id, "player_name": r.player_name,
            "team_name": r.team_name, "goals": r.goals, "assists": r.assists,
            "matches_played": r.matches_played
        } for r in rows]

# ==================== SERIE A ENDPOINTS ====================

@app.post("/api/serie-a/matches")
async def create_serie_a_match(match_data: dict):
    """Crea o actualiza un partido de Serie A con todos los detalles"""
    with SessionLocal() as session:
        try:
            # Comprobar si ya existe el partido
            existing = session.query(ScrapedMatchORM).filter(
                ScrapedMatchORM.league == 'Serie A',
                ScrapedMatchORM.home_team == match_data['home_team'],
                ScrapedMatchORM.away_team == match_data['away_team'],
                ScrapedMatchORM.matchday == match_data['matchday'],
                ScrapedMatchORM.season == match_data.get('season', '24/25')
            ).first()

            if existing:
                match_id = existing.id
                existing.home_score = match_data['home_score']
                existing.away_score = match_data['away_score']
                existing.date = match_data['date']
                existing.is_finished = True
                # Borrar detalles anteriores para evitar duplicados
                session.query(GoalORM).filter(GoalORM.match_id == match_id).delete()
                session.query(CardORM).filter(CardORM.match_id == match_id).delete()
                session.query(SubstitutionORM).filter(SubstitutionORM.match_id == match_id).delete()
                session.query(InjuryORM).filter(InjuryORM.match_id == match_id).delete()
            else:
                new_match = ScrapedMatchORM(
                    league='Serie A',
                    home_team=match_data['home_team'],
                    away_team=match_data['away_team'],
                    home_score=match_data['home_score'],
                    away_score=match_data['away_score'],
                    date=match_data['date'],
                    matchday=match_data['matchday'],
                    season=match_data.get('season', '24/25'),
                    is_finished=True
                )
                session.add(new_match)
                session.flush()  # Para obtener el ID generado
                match_id = new_match.id

            # Insertar goles
            for goal in match_data.get('goals', []):
                session.add(GoalORM(
                    match_id=match_id, player_name=goal['player_name'],
                    minute=goal.get('minute'), is_own_goal=goal.get('is_own_goal', False),
                    is_penalty=goal.get('is_penalty', False), assist_player_name=goal.get('assist_player_name')
                ))

            # Insertar tarjetas
            for card in match_data.get('cards', []):
                session.add(CardORM(
                    match_id=match_id, player_name=card['player_name'],
                    card_type=card['card_type'], minute=card.get('minute'), reason=card.get('reason', 'Falta')
                ))

            # Insertar sustituciones
            for sub in match_data.get('substitutions', []):
                session.add(SubstitutionORM(
                    match_id=match_id, player_in=sub['player_in'],
                    player_out=sub['player_out'], minute=sub.get('minute')
                ))

            # Insertar lesiones
            for injury in match_data.get('injuries', []):
                session.add(InjuryORM(
                    match_id=match_id, player_name=injury['player_name'],
                    minute=injury.get('minute'), description=injury.get('description', 'Lesión')
                ))

            session.commit()
            return {"success": True, "match_id": match_id, "message": "Partido guardado correctamente"}

        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=400, detail=f"Error guardando partido: {str(e)}")

@app.put("/api/serie-a/matches/{match_id}")
async def update_serie_a_match(match_id: int, match_data: dict):
    """Actualiza un partido existente de Serie A sin borrar datos existentes"""
    with SessionLocal() as session:
        try:
            match = session.query(ScrapedMatchORM).filter(
                ScrapedMatchORM.id == match_id,
                ScrapedMatchORM.league == 'Serie A'
            ).first()
            if not match:
                raise HTTPException(status_code=404, detail="Partido no encontrado")

            match.home_score = match_data['home_score']
            match.away_score = match_data['away_score']
            match.date = match_data['date']
            match.is_finished = True

            if 'goals' in match_data:
                session.query(GoalORM).filter(GoalORM.match_id == match_id).delete()
                for goal in match_data['goals']:
                    session.add(GoalORM(
                        match_id=match_id, player_name=goal['player_name'],
                        minute=goal.get('minute'), is_own_goal=goal.get('is_own_goal', False),
                        is_penalty=goal.get('is_penalty', False), assist_player_name=goal.get('assist_player_name')
                    ))

            if 'cards' in match_data:
                session.query(CardORM).filter(CardORM.match_id == match_id).delete()
                for card in match_data['cards']:
                    session.add(CardORM(
                        match_id=match_id, player_name=card['player_name'],
                        card_type=card['card_type'], minute=card.get('minute'), reason=card.get('reason', 'Falta')
                    ))

            if 'substitutions' in match_data:
                session.query(SubstitutionORM).filter(SubstitutionORM.match_id == match_id).delete()
                for sub in match_data['substitutions']:
                    session.add(SubstitutionORM(
                        match_id=match_id, player_in=sub['player_in'],
                        player_out=sub['player_out'], minute=sub.get('minute')
                    ))

            if 'injuries' in match_data:
                session.query(InjuryORM).filter(InjuryORM.match_id == match_id).delete()
                for injury in match_data['injuries']:
                    session.add(InjuryORM(
                        match_id=match_id, player_name=injury['player_name'],
                        minute=injury.get('minute'), description=injury.get('description', 'Lesión')
                    ))

            session.commit()
            return {"success": True, "message": "Partido actualizado correctamente"}

        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=400, detail=f"Error actualizando partido: {str(e)}")


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@app.get("/api/match-details")
async def get_match_details(league: str, home: str, away: str):
    """Obtiene los detalles de un partido con estadísticas globales y mejores anotadores"""
    with SessionLocal() as session:
        # Stats de clasificación scrapeados
        home_stats_orm = session.query(ScrapedDataORM).filter(
            ScrapedDataORM.league == league, ScrapedDataORM.team_name == home
        ).first()
        away_stats_orm = session.query(ScrapedDataORM).filter(
            ScrapedDataORM.league == league, ScrapedDataORM.team_name == away
        ).first()

        def stats_to_dict(s):
            if not s: return None
            return {"id": s.id, "sport": s.sport, "league": s.league, "team_name": s.team_name,
                    "position": s.position, "points": s.points, "matches_played": s.matches_played,
                    "wins": s.wins, "draws": s.draws, "losses": s.losses,
                    "goals_for": s.goals_for, "goals_against": s.goals_against, "goal_diff": s.goal_diff}

        # Top 3 goleadores de cada equipo
        home_scorers = (
            session.query(PlayerStatORM)
            .join(LeagueORM, PlayerStatORM.league_id == LeagueORM.id)
            .filter(LeagueORM.name == league, PlayerStatORM.team_name == home)
            .order_by(PlayerStatORM.goals.desc())
            .limit(3).all()
        )
        away_scorers = (
            session.query(PlayerStatORM)
            .join(LeagueORM, PlayerStatORM.league_id == LeagueORM.id)
            .filter(LeagueORM.name == league, PlayerStatORM.team_name == away)
            .order_by(PlayerStatORM.goals.desc())
            .limit(3).all()
        )

        def scorer_to_dict(r):
            return {"id": r.id, "player_name": r.player_name, "team_name": r.team_name,
                    "goals": r.goals, "assists": r.assists, "matches_played": r.matches_played}

        # Partido más reciente entre los dos equipos
        match_orm = session.query(ScrapedMatchORM).filter(
            ScrapedMatchORM.league == league,
            ScrapedMatchORM.home_team == home,
            ScrapedMatchORM.away_team == away
        ).order_by(ScrapedMatchORM.date.desc()).first()

        match_events = {"goals": [], "cards": [], "substitutions": [], "injuries": []}

        if match_orm:
            mid = match_orm.id
            goals_raw = session.query(GoalORM).filter(GoalORM.match_id == mid).all()
            cards_raw = session.query(CardORM).filter(CardORM.match_id == mid).all()
            subs_raw = session.query(SubstitutionORM).filter(SubstitutionORM.match_id == mid).all()
            injuries_raw = session.query(InjuryORM).filter(InjuryORM.match_id == mid).all()

            PLAYER_TEAMS = {
                "Vinicius Jr": "Real Madrid", "Rodrygo": "Real Madrid", "Toni Kroos": "Real Madrid",
                "Dani Carvajal": "Real Madrid", "Modric": "Real Madrid", "Eder Militao": "Real Madrid",
                "Robert Lewandowski": "Barcelona", "Lamine Yamal": "Barcelona",
                "Araujo": "Barcelona", "Gavi": "Barcelona", "Joao Felix": "Barcelona", "Pedri": "Barcelona"
            }

            def resolve_team(player_name):
                stat = session.query(PlayerStatORM).filter(PlayerStatORM.player_name == player_name).first()
                if stat:
                    return stat.team_name
                return PLAYER_TEAMS.get(player_name, home)

            match_events["goals"] = [
                {"id": g.id, "player_name": g.player_name, "minute": g.minute,
                 "is_own_goal": g.is_own_goal, "is_penalty": g.is_penalty,
                 "assist_player_name": g.assist_player_name, "team_name": resolve_team(g.player_name)}
                for g in goals_raw
            ]
            match_events["cards"] = [
                {"id": c.id, "player_name": c.player_name, "minute": c.minute,
                 "card_type": c.card_type, "reason": c.reason, "team_name": resolve_team(c.player_name)}
                for c in cards_raw
            ]
            match_events["substitutions"] = [
                {"id": s.id, "player_in": s.player_in, "player_out": s.player_out,
                 "minute": s.minute, "team_name": resolve_team(s.player_out)}
                for s in subs_raw
            ]
            match_events["injuries"] = [
                {"id": i.id, "player_name": i.player_name, "minute": i.minute,
                 "description": i.description, "team_name": resolve_team(i.player_name)}
                for i in injuries_raw
            ]

        return {
            "home_team": stats_to_dict(home_stats_orm),
            "away_team": stats_to_dict(away_stats_orm),
            "home_scorers": [scorer_to_dict(r) for r in home_scorers],
            "away_scorers": [scorer_to_dict(r) for r in away_scorers],
            "match_events": match_events
        }

# ==================== ROOT ENDPOINT ====================

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Redirect to login page"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/login", status_code=302)

@app.get("/api")
async def api_info():
    """Endpoint con información de la API"""
    return {
        "message": "Football Leagues API",
        "version": "1.0.0",
        "documentation": "/docs",
        "leagues": ["LaLiga EA Sports", "Hypermotion", "Bundesliga", "Serie A", "Premier League", "NBA", "FIBA World Cup", "Euroliga", "ACB"]
    }

# Rutas para servir páginas HTML
@app.get("/inicio", response_class=HTMLResponse)
async def inicio(request: Request):
    return templates.TemplateResponse(request=request, name="inicio.html", context={"request": request})

@app.get("/deportes", response_class=HTMLResponse)
async def deportes(request: Request):
    return templates.TemplateResponse(request=request, name="deportes.html", context={"request": request})

@app.get("/champions-league", response_class=HTMLResponse)
async def champions_league(request: Request):
    return templates.TemplateResponse(request=request, name="champions-league.html", context={"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="IniciarSesion.html", context={"request": request})

@app.get("/recuperar-contrasena", response_class=HTMLResponse)
async def recuperar_contrasena_page(request: Request):
    return templates.TemplateResponse(request=request, name="recuperar-contrasena.html", context={"request": request})

@app.get("/registro", response_class=HTMLResponse)
async def registro_page(request: Request):
    return templates.TemplateResponse(request=request, name="registro.html", context={"request": request})

@app.get("/configuracion", response_class=HTMLResponse)
async def configuracion_page(request: Request):
    return templates.TemplateResponse(request=request, name="configuracion.html", context={"request": request})

@app.get("/premier-league", response_class=HTMLResponse)
async def premier_league(request: Request):
    return templates.TemplateResponse(request=request, name="premier-league.html", context={"request": request})

@app.get("/serie-a", response_class=HTMLResponse)
async def serie_a(request: Request):
    return templates.TemplateResponse(request=request, name="serie-a.html", context={"request": request})

@app.get("/bundesliga", response_class=HTMLResponse)
async def bundesliga(request: Request):
    return templates.TemplateResponse(request=request, name="bundesliga.html", context={"request": request})

@app.get("/laliga", response_class=HTMLResponse)
async def laliga(request: Request):
    return templates.TemplateResponse(request=request, name="laliga.html", context={"request": request})

@app.get("/liga-hypermotion", response_class=HTMLResponse)
async def liga_hypermotion(request: Request):
    return templates.TemplateResponse(request=request, name="liga-hypermotion.html", context={"request": request})

@app.get("/api-demo", response_class=HTMLResponse)
async def api_demo(request: Request):
    return templates.TemplateResponse(request=request, name="api_demo.html", context={"request": request})

@app.get("/acb", response_class=HTMLResponse)
async def acb_page(request: Request):
    return templates.TemplateResponse(request=request, name="acb.html", context={"request": request})

@app.get("/nba", response_class=HTMLResponse)
async def nba_page(request: Request):
    return templates.TemplateResponse(request=request, name="nba.html", context={"request": request})

@app.get("/euroliga", response_class=HTMLResponse)
async def euroliga_page(request: Request):
    return templates.TemplateResponse(request=request, name="euroliga.html", context={"request": request})

@app.get("/fiba", response_class=HTMLResponse)
async def fiba_page(request: Request):
    return templates.TemplateResponse(request=request, name="fiba.html", context={"request": request})

@app.get("/atp", response_class=HTMLResponse)
async def atp_page(request: Request):
    return templates.TemplateResponse(request=request, name="atp.html", context={"request": request})

@app.get("/wimbledon", response_class=HTMLResponse)
async def wimbledon_page(request: Request):
    return templates.TemplateResponse(request=request, name="wimbledon.html", context={"request": request})

@app.get("/roland-garros", response_class=HTMLResponse)
async def roland_garros_page(request: Request):
    return templates.TemplateResponse(request=request, name="roland-garros.html", context={"request": request})

@app.get("/australian-open", response_class=HTMLResponse)
async def australian_open_page(request: Request):
    return templates.TemplateResponse(request=request, name="australian-open.html", context={"request": request})

@app.get("/us-open", response_class=HTMLResponse)
async def us_open_page(request: Request):
    return templates.TemplateResponse(request=request, name="us-open.html", context={"request": request})

@app.get("/wta", response_class=HTMLResponse)
async def wta_page(request: Request):
    return templates.TemplateResponse(request=request, name="wta.html", context={"request": request})

@app.get("/liga-hypermotion", response_class=HTMLResponse)
async def hypermotion_page(request: Request):
    return templates.TemplateResponse(request=request, name="liga-hypermotion.html", context={"request": request})

@app.get("/premier-league", response_class=HTMLResponse)
async def premier_page(request: Request):
    return templates.TemplateResponse(request=request, name="premier-league.html", context={"request": request})

@app.get("/serie-a", response_class=HTMLResponse)
async def serie_a_page(request: Request):
    return templates.TemplateResponse(request=request, name="serie-a.html", context={"request": request})

@app.get("/bundesliga", response_class=HTMLResponse)
async def bundesliga_page(request: Request):
    return templates.TemplateResponse(request=request, name="bundesliga.html", context={"request": request})

# Paginas del footer
@app.get("/footer/{page}", response_class=HTMLResponse)
async def footer_pages(page: str, request: Request):
    allowed_pages = [
        "sobre-nosotros", "trabaja-con-nosotros", "responsabilidad", 
        "terminos", "faq", "contacto", "guia-apuestas", "metodos-pago", 
        "juego-responsable", "privacidad", "certificaciones", "ayuda-adiccion"
    ]
    if page in allowed_pages:
        from fastapi.responses import RedirectResponse
        return templates.TemplateResponse(request=request, name=f"footer/{page}.html", context={"request": request})
    
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/inicio")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
