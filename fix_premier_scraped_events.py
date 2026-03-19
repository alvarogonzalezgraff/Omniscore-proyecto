"""
Script para vincular los eventos (goles, tarjetas, cambios) de la tabla 'matches'
con los partidos correctos de 'scraped_matches' para Premier League.

El problema: los goles tienen match_id referenciando la tabla 'matches' (IDs ~400),
pero la API busca goles por match_id referenciando 'scraped_matches' (IDs ~5319).
Este script copia los eventos con los IDs correctos de scraped_matches.
"""
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.database import SessionLocal
from api.database_orm import (
    ScrapedMatchORM, MatchORM, LeagueORM, TeamORM,
    GoalORM, CardORM, SubstitutionORM, InjuryORM
)

def normalize_team_name(name):
    """Normaliza nombres de equipos para comparación."""
    name = name.lower().strip()
    replacements = {
        'brighton & hove albion': 'brighton',
        'brighton and hove albion': 'brighton',
        'manchester city': 'man city',
        'manchester united': 'man utd',
        'nottingham forest': 'nottm forest',
        'wolverhampton wanderers': 'wolves',
        'wolverhampton': 'wolves',
        'west ham united': 'west ham',
        'newcastle united': 'newcastle',
        'tottenham hotspur': 'tottenham',
        'afc bournemouth': 'bournemouth',
        'crystal palace': 'crystal palace',
        'leeds united': 'leeds united',
        'aston villa': 'aston villa',
    }
    for full, short in replacements.items():
        if full in name:
            return short
    return name

def teams_match(scraped_name, orm_name):
    """Comprueba si dos nombres de equipo son equivalentes."""
    s = normalize_team_name(scraped_name)
    o = normalize_team_name(orm_name)
    return s == o or s in o or o in s

def run_migration():
    db = SessionLocal()
    try:
        # 1. Obtener la liga Premier League
        pl = db.query(LeagueORM).filter(LeagueORM.name == 'Premier League').first()
        if not pl:
            print("ERROR: No se encontró Premier League en la tabla de ligas")
            return
        print(f"Liga Premier League encontrada, ID={pl.id}")

        # 2. Obtener todos los partidos de MATCHES (tabla ORM)
        orm_matches = db.query(MatchORM).filter(MatchORM.league_id == pl.id).all()
        print(f"Partidos en tabla 'matches': {len(orm_matches)}")

        # 3. Obtener todos los scraped_matches de Premier League
        scraped_matches = db.query(ScrapedMatchORM).filter(
            ScrapedMatchORM.league == 'Premier League'
        ).all()
        print(f"Partidos en tabla 'scraped_matches': {len(scraped_matches)}")

        # 4. Para cada scraped_match, encontrar el match ORM correspondiente
        linked = 0
        not_linked = 0
        total_goals = 0
        total_cards = 0
        total_subs = 0
        total_injuries = 0

        for sm in scraped_matches:
            # Buscar partido ORM que coincida por equipos y jornada
            matched_orm = None

            # Extraer número de jornada del matchday
            jornada_num = None
            if sm.matchday:
                mday = sm.matchday.lower().replace('jornada', '').replace('j', '').strip()
                try:
                    jornada_num = int(mday)
                except ValueError:
                    pass

            for om in orm_matches:
                home_match = teams_match(sm.home_team, om.home_team.name)
                away_match = teams_match(sm.away_team, om.away_team.name)

                if home_match and away_match:
                    # Si tenemos número de jornada, verificar también
                    if jornada_num is None or om.matchday == jornada_num:
                        matched_orm = om
                        break

            if not matched_orm:
                print(f"  NO VINCULADO: {sm.home_team} vs {sm.away_team} (matchday={sm.matchday}, ID={sm.id})")
                not_linked += 1
                continue

            linked += 1

            # 5. Verificar si ya hay eventos vinculados al scraped_match
            existing_goals = db.query(GoalORM).filter(GoalORM.match_id == sm.id).count()
            existing_cards = db.query(CardORM).filter(CardORM.match_id == sm.id).count()
            existing_subs = db.query(SubstitutionORM).filter(SubstitutionORM.match_id == sm.id).count()
            existing_injuries = db.query(InjuryORM).filter(InjuryORM.match_id == sm.id).count()

            if existing_goals > 0 or existing_cards > 0 or existing_subs > 0:
                print(f"  YA TIENE DATOS {sm.home_team} vs {sm.away_team}: goals={existing_goals}, cards={existing_cards}, subs={existing_subs}")
                total_goals += existing_goals
                total_cards += existing_cards
                total_subs += existing_subs
                continue

            # 6. Copiar eventos del match ORM al scraped_match
            orm_goals = db.query(GoalORM).filter(GoalORM.match_id == matched_orm.id).all()
            orm_cards = db.query(CardORM).filter(CardORM.match_id == matched_orm.id).all()
            orm_subs = db.query(SubstitutionORM).filter(SubstitutionORM.match_id == matched_orm.id).all()
            orm_injuries = db.query(InjuryORM).filter(InjuryORM.match_id == matched_orm.id).all()

            # Insertar goles con el ID de scraped_match
            for g in orm_goals:
                new_goal = GoalORM(
                    match_id=sm.id,
                    team_id=g.team_id,
                    player_name=g.player_name,
                    minute=g.minute,
                    assist_player_name=g.assist_player_name,
                    is_own_goal=g.is_own_goal,
                    is_penalty=g.is_penalty
                )
                db.add(new_goal)
            total_goals += len(orm_goals)

            # Insertar tarjetas
            for c in orm_cards:
                new_card = CardORM(
                    match_id=sm.id,
                    team_id=c.team_id,
                    player_name=c.player_name,
                    minute=c.minute,
                    card_type=c.card_type,
                    reason=c.reason
                )
                db.add(new_card)
            total_cards += len(orm_cards)

            # Insertar sustituciones
            for s in orm_subs:
                new_sub = SubstitutionORM(
                    match_id=sm.id,
                    team_id=s.team_id,
                    player_in=s.player_in,
                    player_out=s.player_out,
                    minute=s.minute
                )
                db.add(new_sub)
            total_subs += len(orm_subs)

            # Insertar lesiones
            for i in orm_injuries:
                new_inj = InjuryORM(
                    match_id=sm.id,
                    team_id=i.team_id,
                    player_name=i.player_name,
                    minute=i.minute,
                    description=i.description
                )
                db.add(new_inj)
            total_injuries += len(orm_injuries)

            print(f"  OK: {sm.home_team} vs {sm.away_team} -> ORM match {matched_orm.id} | goals={len(orm_goals)}, cards={len(orm_cards)}, subs={len(orm_subs)}")

        db.commit()
        print()
        print("=" * 50)
        print("MIGRACIÓN COMPLETADA")
        print(f"Partidos vinculados: {linked}")
        print(f"Partidos NO vinculados: {not_linked}")
        print(f"Total goles migrados: {total_goals}")
        print(f"Total tarjetas migradas: {total_cards}")
        print(f"Total sustituciones migradas: {total_subs}")

    except Exception as e:
        db.rollback()
        import traceback
        print("ERROR:", e)
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    run_migration()
