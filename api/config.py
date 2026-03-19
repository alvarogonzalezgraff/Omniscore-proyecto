import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# ==================== DATABASE CONFIGURATION ====================
# Determinar si usar PostgreSQL o SQLite
USE_POSTGRES = os.getenv("USE_POSTGRES", "false").lower() == "true"

if USE_POSTGRES:
    # Configuración PostgreSQL
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "betwin_db")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    
    # URL de conexión a PostgreSQL
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    # Configuración SQLite (fallback)
    DB_PATH = BASE_DIR / "database" / "app.db"
    DATABASE_URL = f"sqlite:///{DB_PATH}"

# Rutas legadas (mantenidas por compatibilidad)
BASKET_DB_PATH = DB_PATH if not USE_POSTGRES else None
TENIS_DB_PATH = DB_PATH if not USE_POSTGRES else None

# ==================== JWT ====================
SECRET_KEY = os.getenv("SECRET_KEY", "tu_clave_secreta_muy_segura_cambiala_en_produccion")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# ==================== CORS ====================
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8001",
    "*"  # En producción, quitar esto y listar solo los orígenes necesarios
]
