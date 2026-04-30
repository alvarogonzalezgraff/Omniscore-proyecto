from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Request, Response
from fastapi.responses import JSONResponse
from .database import get_db, dict_from_row, SessionLocal
from .config import SECRET_KEY, ALGORITHM
from .models import User
from .database_orm import UserORM
import secrets
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SessionCookieManager:
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.csrf_tokens = {}  # Almacenamiento temporal para tokens CSRF
        
    def generate_csrf_token(self, session_id: str) -> str:
        """Genera un token CSRF para una sesión"""
        token = secrets.token_urlsafe(32)
        self.csrf_tokens[session_id] = {
            'token': token,
            'expires_at': datetime.utcnow() + timedelta(hours=1)
        }
        return token
    
    def verify_csrf_token(self, session_id: str, token: str) -> bool:
        """Verifica un token CSRF"""
        if session_id not in self.csrf_tokens:
            return False
        
        csrf_data = self.csrf_tokens[session_id]
        if datetime.utcnow() > csrf_data['expires_at']:
            del self.csrf_tokens[session_id]
            return False
        
        return secrets.compare_digest(csrf_data['token'], token)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Crea un token JWT de acceso"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)  # 15 min por defecto
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: dict) -> str:
        """Crea un token JWT de refresco"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)  # 7 días por defecto
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Verifica un token JWT y retorna el payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verificar tipo de token
            if payload.get("type") != token_type:
                return None
                
            # Verificar expiración
            exp = payload.get("exp")
            if exp and datetime.utcnow().timestamp() > exp:
                return None
                
            return payload
        except JWTError:
            return None
    
    def set_auth_cookies(self, response: Response, access_token: str, refresh_token: str, csrf_token: str):
        """Establece las cookies de autenticación"""
        # Cookie de acceso (15 min, HttpOnly, Secure, SameSite=Strict)
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=900,  # 15 minutos
            httponly=True,
            secure=False,  # En producción debe ser True
            samesite="strict",
            path="/"
        )
        
        # Cookie de refresco (7 días, HttpOnly, Secure, SameSite=Strict)
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=604800,  # 7 días
            httponly=True,
            secure=False,  # En producción debe ser True
            samesite="strict",
            path="/"
        )
        
        # Cookie CSRF (accesible por JS, 1 hora)
        response.set_cookie(
            key="csrf_token",
            value=csrf_token,
            max_age=3600,  # 1 hora
            httponly=False,
            secure=False,  # En producción debe ser True
            samesite="strict",
            path="/"
        )
    
    def clear_auth_cookies(self, response: Response):
        """Limpia las cookies de autenticación"""
        response.delete_cookie(key="access_token", path="/")
        response.delete_cookie(key="refresh_token", path="/")
        response.delete_cookie(key="csrf_token", path="/")

# Instancia global del gestor de cookies
session_cookie_manager = SessionCookieManager()

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
    if not pwd_context.verify(password, user["password"]):
        return False
    return user

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica que la contraseña coincida con el hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_session_id_from_token(token: str) -> str:
    """Genera un ID de sesión único a partir del token"""
    return hashlib.sha256(token.encode()).hexdigest()[:16]
