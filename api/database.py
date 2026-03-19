from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from .config import DATABASE_URL

# Motor de PostgreSQL
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,       # Comprueba la conexión antes de usarla
    pool_size=10,             # Conexiones en el pool
    max_overflow=20,          # Conexiones adicionales permitidas
    echo=False                # Pon True para ver SQL en consola (debug)
)

_SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class SessionLocal:
    """
    Wrapper que permite usar SessionLocal() como context manager:
        with SessionLocal() as session:
            ...
    Equivalente al patrón usado en el main.py existente.
    """
    def __new__(cls):
        # Devuelve directamente una sesión (compatible con 'with SessionLocal() as s:')
        return _SessionFactory()


def get_session():
    """Dependencia FastAPI para obtener una sesión de BD."""
    db = _SessionFactory()
    try:
        yield db
    finally:
        db.close()


def get_db():
    """Alias de get_session para compatibilidad con código existente."""
    db = _SessionFactory()
    try:
        yield db
    finally:
        db.close()


def dict_from_row(row):
    """Convierte una fila (Row de SQLAlchemy) en un diccionario."""
    if row is None:
        return None
    return row._asdict() if hasattr(row, '_asdict') else dict(row)


def list_from_rows(rows):
    """Convierte múltiples filas en una lista de diccionarios."""
    return [dict_from_row(row) for row in rows]


def test_connection():
    """Verifica que la conexión a PostgreSQL funciona."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Conexión a PostgreSQL exitosa.")
        return True
    except Exception as e:
        print(f"❌ Error de conexión a PostgreSQL: {e}")
        return False
