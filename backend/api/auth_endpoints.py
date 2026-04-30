from fastapi import APIRouter, HTTPException, status, Request, Response, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from datetime import timedelta
from typing import Dict, Any, Optional
import time

from .session_auth import (
    session_cookie_manager, 
    authenticate_user, 
    get_user_by_username,
    get_session_id_from_token
)
from .verify_session import get_current_user_from_cookie

# Rate limiting simple (en producción usar Redis)
login_attempts = {}
RATE_LIMIT = 5  # 5 intentos por minuto
RATE_WINDOW = 60  # 60 segundos

router = APIRouter(prefix="/api/auth", tags=["authentication"])

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    user: Optional[Dict[str, Any]] = None

class RefreshResponse(BaseModel):
    success: bool
    message: str

class LogoutResponse(BaseModel):
    success: bool
    message: str

def check_rate_limit(client_ip: str) -> bool:
    """Verifica el rate limiting para login"""
    now = time.time()
    
    # Limpiar intentos antiguos
    if client_ip in login_attempts:
        login_attempts[client_ip] = [
            attempt_time for attempt_time in login_attempts[client_ip]
            if now - attempt_time < RATE_WINDOW
        ]
    else:
        login_attempts[client_ip] = []
    
    # Verificar si excede el límite
    if len(login_attempts[client_ip]) >= RATE_LIMIT:
        return False
    
    # Registrar intento actual
    login_attempts[client_ip].append(now)
    return True

@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request, 
    response: Response, 
    credentials: LoginRequest
):
    """
    Endpoint de login que establece cookies de sesión
    """
    client_ip = request.client.host
    
    # Rate limiting
    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos de login. Intente nuevamente en 1 minuto."
        )
    
    # Validar credenciales
    user = authenticate_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Cookie"},
        )
    
    # Crear tokens
    access_token = session_cookie_manager.create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=15)
    )
    
    refresh_token = session_cookie_manager.create_refresh_token(
        data={"sub": user["username"]}
    )
    
    # Generar CSRF token
    session_id = get_session_id_from_token(access_token)
    csrf_token = session_cookie_manager.generate_csrf_token(session_id)
    
    # Establecer cookies
    session_cookie_manager.set_auth_cookies(
        response, 
        access_token, 
        refresh_token, 
        csrf_token
    )
    
    # Preparar respuesta sin información sensible
    user_response = {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "full_name": user["full_name"]
    }
    
    return LoginResponse(
        success=True,
        message="Login exitoso",
        user=user_response
    )

@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(request: Request, response: Response):
    """
    Endpoint para refrescar el token de acceso
    """
    # Obtener refresh token desde cookies
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se encontró refresh token"
        )
    
    # Verificar refresh token
    payload = session_cookie_manager.verify_token(refresh_token, "refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado"
        )
    
    # Obtener información del usuario
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token malformado"
        )
    
    user = get_user_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
    
    # Crear nuevo access token
    new_access_token = session_cookie_manager.create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=15)
    )
    
    # Generar nuevo CSRF token
    session_id = get_session_id_from_token(new_access_token)
    new_csrf_token = session_cookie_manager.generate_csrf_token(session_id)
    
    # Actualizar cookies
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        max_age=900,  # 15 minutos
        httponly=True,
        secure=False,  # En producción debe ser True
        samesite="strict",
        path="/"
    )
    
    response.set_cookie(
        key="csrf_token",
        value=new_csrf_token,
        max_age=3600,  # 1 hora
        httponly=False,
        secure=False,  # En producción debe ser True
        samesite="strict",
        path="/"
    )
    
    return RefreshResponse(
        success=True,
        message="Token refrescado exitosamente"
    )

@router.post("/logout", response_model=LogoutResponse)
async def logout(request: Request, response: Response):
    """
    Endpoint para cerrar sesión y limpiar cookies
    """
    # Obtener access token para limpiar sesión
    access_token = request.cookies.get("access_token")
    if access_token:
        session_id = get_session_id_from_token(access_token)
        # Limpiar CSRF token si existe
        if session_id in session_cookie_manager.csrf_tokens:
            del session_cookie_manager.csrf_tokens[session_id]
    
    # Limpiar cookies
    session_cookie_manager.clear_auth_cookies(response)
    
    return LogoutResponse(
        success=True,
        message="Sesión cerrada exitosamente"
    )

@router.get("/me")
async def get_current_user(request: Request):
    """
    Endpoint para obtener información del usuario actual
    """
    user = await get_current_user_from_cookie(request)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado"
        )
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name
    }

@router.get("/csrf-token")
async def get_csrf_token(request: Request, response: Response):
    """
    Endpoint para obtener un nuevo CSRF token
    """
    # Obtener access token
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se encontró token de acceso"
        )
    
    # Generar nuevo CSRF token
    session_id = get_session_id_from_token(access_token)
    csrf_token = session_cookie_manager.generate_csrf_token(session_id)
    
    # Actualizar cookie CSRF
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        max_age=3600,  # 1 hora
        httponly=False,
        secure=False,  # En producción debe ser True
        samesite="strict",
        path="/"
    )
    
    return {"csrf_token": csrf_token}
