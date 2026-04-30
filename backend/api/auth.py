from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .database import get_db, dict_from_row, SessionLocal
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from .models import User
from .database_orm import UserORM
from .session_manager import session_manager

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica que la contraseña coincida con el hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera un hash de la contraseña"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_access_token_with_session(data: dict, user_data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT y lo registra en el gestor de sesiones"""
    token = create_access_token(data, expires_delta)
    username = data.get("sub")
    if username:
        session_manager.add_session(token, username, user_data)
    return token

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
    if not verify_password(password, user["password"]):
        return False
    return user

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Obtiene el usuario actual desde el token JWT con persistencia de sesión"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        # Si el JWT es inválido, verificar si existe en sesiones persistentes
        session_data = session_manager.get_session(token)
        if session_data:
            # Extender sesión y retornar usuario
            session_manager.extend_session(token)
            user_data = session_data['user_data']
            return User(**user_data)
        raise credentials_exception
    
    # Primero verificar en sesiones persistentes (más rápido)
    session_data = session_manager.get_session(token)
    if session_data:
        session_manager.extend_session(token)
        user_data = session_data['user_data']
        return User(**user_data)
    
    # Si no está en sesiones, verificar en base de datos
    user = get_user_by_username(username)
    if user is None:
        raise credentials_exception
    
    # Guardar en sesiones para futuros reinicios
    session_manager.add_session(token, username, user)
    return User(**user)
