import os
import sqlite3
import asyncio

import httpx

def _project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _db_path(*parts: str) -> str:
    return os.path.join(_project_root(), *parts)


def _tables_in_db(path: str) -> set[str]:
    con = sqlite3.connect(path)
    try:
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return {r[0] for r in cur.fetchall()}
    finally:
        con.close()


def test_db_files_exist():
    assert os.path.exists(_db_path('database', 'app.db'))
    assert os.path.exists(_db_path('database', 'app.db'))
    assert os.path.exists(_db_path('database', 'app.db'))


def test_futbol_db_has_core_tables():
    tables = _tables_in_db(_db_path('database', 'app.db'))
    for t in ['leagues', 'teams', 'matches', 'scraped_data', 'scraped_matches']:
        assert t in tables


def test_basket_db_has_core_tables():
    tables = _tables_in_db(_db_path('database', 'app.db'))
    for t in ['basketball_leagues', 'basketball_seasons', 'basketball_teams', 'basketball_standings']:
        assert t in tables


def test_tenis_db_has_core_tables():
    tables = _tables_in_db(_db_path('database', 'app.db'))
    for t in ['tennis_tournaments', 'tennis_players', 'tennis_editions']:
        assert t in tables


async def _async_get(app, path: str, params: dict | None = None):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url='http://testserver') as client:
        return await client.get(path, params=params)


def _get(app, path: str, params: dict | None = None):
    return asyncio.run(_async_get(app, path, params=params))


def test_api_import_and_basic_endpoints():
    from api.main import app

    r = _get(app, '/api/leagues')
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    r = _get(app, '/api/basket/leagues')
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    r = _get(app, '/api/basket/seasons')
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_basket_standings_endpoint_for_any_season():
    from api.main import app

    seasons = _get(app, '/api/basket/seasons').json()
    assert isinstance(seasons, list)
    assert len(seasons) >= 1

    season_id = seasons[0]['id']
    r = _get(app, '/api/basket/standings', params={'season_id': season_id})
    assert r.status_code == 200
    assert isinstance(r.json(), list)
