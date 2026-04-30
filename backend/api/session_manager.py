"""
Gestor de sesiones con persistencia para mantener la autenticación
a través de reinicios del servidor en desarrollo.
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Set
from .config import ACCESS_TOKEN_EXPIRE_MINUTES

class SessionManager:
    def __init__(self):
        self.sessions_file = Path(__file__).parent.parent / "_historial_y_herramientas" / "active_sessions.json"
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
                        token: session_data 
                        for token, session_data in data.items()
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
    
    def add_session(self, token: str, username: str, user_data: Dict):
        """Añade una nueva sesión"""
        expires_at = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        self.sessions[token] = {
            'username': username,
            'user_data': user_data,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': expires_at.isoformat(),
            'last_accessed': datetime.utcnow().isoformat()
        }
        self.save_sessions()
    
    def get_session(self, token: str) -> Optional[Dict]:
        """Obtiene datos de sesión por token"""
        session_data = self.sessions.get(token)
        if not session_data:
            return None
        
        # Verificar si la sesión ha expirado
        expires_at = datetime.fromisoformat(session_data['expires_at'])
        if datetime.utcnow() > expires_at:
            self.remove_session(token)
            return None
        
        # Actualizar último acceso
        session_data['last_accessed'] = datetime.utcnow().isoformat()
        self.save_sessions()
        return session_data
    
    def remove_session(self, token: str):
        """Elimina una sesión"""
        if token in self.sessions:
            del self.sessions[token]
            self.save_sessions()
    
    def cleanup_expired_sessions(self):
        """Limpia sesiones expiradas"""
        current_time = datetime.utcnow()
        expired_tokens = [
            token for token, session_data in self.sessions.items()
            if datetime.fromisoformat(session_data['expires_at']) <= current_time
        ]
        for token in expired_tokens:
            self.remove_session(token)
    
    def extend_session(self, token: str, minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES):
        """Extiende la duración de una sesión"""
        session_data = self.sessions.get(token)
        if session_data:
            new_expires_at = datetime.utcnow() + timedelta(minutes=minutes)
            session_data['expires_at'] = new_expires_at.isoformat()
            session_data['last_accessed'] = datetime.utcnow().isoformat()
            self.save_sessions()
            return True
        return False
    
    def get_active_sessions_count(self) -> int:
        """Obtiene número de sesiones activas"""
        self.cleanup_expired_sessions()
        return len(self.sessions)

# Instancia global del gestor de sesiones
session_manager = SessionManager()