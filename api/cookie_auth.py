"""
Sistema de autenticación basado en cookies de sesión para Omniscore
Reemplaza el sistema JWT por cookies tradicionales con persistencia.
"""
import secrets
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional
from fastapi import HTTPException, status, Request, Response
from fastapi.security import HTTPBearer
from .config import ACCESS_TOKEN_EXPIRE_MINUTES
from .database import SessionLocal
from .database_orm import UserORM

class SessionCookieManager:
    def __init__(self):
        self.sessions_file = Path(__file__).parent.parent / "_historial_y_herramientas" / "cookie_sessions.json"
        self.sessions: Dict[str, Dict] = {}
        self.load_sessions()
    
    def load_sessions(self):
        """Carga sesiones activas desde archivo"""
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Filtrar sesiones expiradas
                    current_time = datetime.utcnow()
                    self.sessions = {
                        session_id: session_data 
                        for session_id, session_data in data.items()
                        if datetime.fromisoformat(session_data['expires_at']) > current_time
                    }
                self.save_sessions()  # Limpiar sesiones expiradas
            except (json.JSONDecodeError, KeyError, ValueError):
                self.sessions = {}
        else:
            # Crear directorio si no existe
            self.sessions_file.parent.mkdir(exist_ok=True)
            self.sessions = {}
    
    def save_sessions(self):
        """Guarda sesiones activas a archivo"""
        try:
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(self.sessions, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando sesiones: {e}")
    
    def create_session(self, user_data: Dict) -> str:
        """Crea una nueva sesión y retorna el session ID"""
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        self.sessions[session_id] = {
            'user_data': user_data,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': expires_at.isoformat(),
            'last_accessed': datetime.utcnow().isoformat()
        }
        self.save_sessions()
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Obtiene datos de sesión por ID"""
        session_data = self.sessions.get(session_id)
        if not session_data:
            return None
        
        # Verificar si la sesión ha expirado
        expires_at = datetime.fromisoformat(session_data['expires_at'])
        if datetime.utcnow() > expires_at:
            self.remove_session(session_id)
            return None
        
        # Actualizar último acceso y extender sesión
        session_data['last_accessed'] = datetime.utcnow().isoformat()
        self.extend_session(session_id)
        return session_data
    
    def remove_session(self, session_id: str):
        """Elimina una sesión"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self.save_sessions()
    
    def extend_session(self, session_id: str, minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES):
        """Extiende la duración de una sesión"""
        session_data = self.sessions.get(session_id)
        if session_data:
            new_expires_at = datetime.utcnow() + timedelta(minutes=minutes)
            session_data['expires_at'] = new_expires_at.isoformat()
            session_data['last_accessed'] = datetime.utcnow().isoformat()
            self.save_sessions()
            return True
        return False
    
    def cleanup_expired_sessions(self):
        """Limpia sesiones expiradas"""
        current_time = datetime.utcnow()
        expired_sessions = [
            session_id for session_id, session_data in self.sessions.items()
            if datetime.fromisoformat(session_data['expires_at']) <= current_time
        ]
        for session_id in expired_sessions:
            self.remove_session(session_id)
    
    def get_active_sessions_count(self) -> int:
        """Obtiene número de sesiones activas"""
        self.cleanup_expired_sessions()
        return len(self.sessions)

# Instancia global del gestor de sesiones
session_cookie_manager = SessionCookieManager()

# Funciones de compatibilidad para migración desde JWT
def get_user_by_username(username: str):
    """Obtiene un usuario por nombre de usuario"""
    with SessionLocal() as session:
        user = session.query(UserORM).filter(UserORM.username == username).first()
        if user:
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "password": user.password,
                "full_name": user.full_name,
                "created_at": str(user.created_at) if user.created_at else None
            }
        return None

def authenticate_user(username: str, password: str):
    """Autentica un usuario"""
    user = get_user_by_username(username)
    if not user:
        return False
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    if not pwd_context.verify(password, user["password"]):
        return False
    return user
