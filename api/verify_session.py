from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer
from typing import Optional
from .session_auth import session_cookie_manager, get_session_id_from_token
from .models import User

class SessionVerification:
    def __init__(self):
        self.session_manager = session_cookie_manager
    
    async def __call__(self, request: Request) -> Optional[User]:
        """Verifica la sesión del usuario desde cookies"""
        
        # Obtener token de acceso desde cookies
        access_token = request.cookies.get("access_token")
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se encontró token de acceso",
                headers={"WWW-Authenticate": "Cookie"},
            )
        
        # Verificar token
        payload = self.session_manager.verify_token(access_token, "access")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado",
                headers={"WWW-Authenticate": "Cookie"},
            )
        
        # Obtener información del usuario
        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token malformado",
                headers={"WWW-Authenticate": "Cookie"},
            )
        
        # Obtener usuario desde la base de datos
        from .session_auth import get_user_by_username
        user_data = get_user_by_username(username)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado",
                headers={"WWW-Authenticate": "Cookie"},
            )
        
        # Crear objeto User
        user = User(
            id=user_data["id"],
            username=user_data["username"],
            email=user_data["email"],
            full_name=user_data["full_name"],
            created_at=user_data["created_at"]
        )
        
        # Adjuntar usuario a la request
        request.state.user = user
        
        return user

# Instancia del middleware de verificación
verify_session = SessionVerification()

async def get_current_user_from_cookie(request: Request) -> Optional[User]:
    """Función helper para obtener el usuario actual desde cookies"""
    try:
        return await verify_session(request)
    except HTTPException:
        return None

def require_csrf(request: Request) -> bool:
    """Verifica el token CSRF para operaciones de mutación"""
    
    # Para métodos GET, HEAD, OPTIONS no se requiere CSRF
    if request.method in ["GET", "HEAD", "OPTIONS"]:
        return True
    
    # Obtener CSRF token de headers
    csrf_token_header = request.headers.get("X-CSRF-Token")
    if not csrf_token_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token requerido para esta operación"
        )
    
    # Obtener access token para generar session_id
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se encontró token de acceso"
        )
    
    # Generar session_id y verificar CSRF
    session_id = get_session_id_from_token(access_token)
    if not session_cookie_manager.verify_csrf_token(session_id, csrf_token_header):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token inválido o expirado"
        )
    
    return True

# Middleware para requerir CSRF en mutaciones
async def csrf_protected(request: Request, call_next):
    """Middleware que aplica protección CSRF"""
    
    # Verificar CSRF para métodos que modifican datos
    if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
        # Excluir endpoints de auth del CSRF check
        if not request.url.path.startswith("/api/auth/"):
            require_csrf(request)
    
    response = await call_next(request)
    return response
