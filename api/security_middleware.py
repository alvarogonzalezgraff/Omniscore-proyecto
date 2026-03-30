from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, List
import time
import hashlib
import secrets
from collections import defaultdict, deque

class CSRFMiddleware(BaseHTTPMiddleware):
    """
    Middleware para protección CSRF
    """
    
    def __init__(self, app, exclude_paths: List[str] = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/api/auth/login",
            "/api/auth/refresh", 
            "/api/auth/logout",
            "/api/auth/csrf-token",
            "/docs",
            "/openapi.json",
            "/redoc"
        ]
        
        # Almacenamiento de tokens CSRF (en producción usar Redis)
        self.csrf_tokens = {}
        
    async def dispatch(self, request: Request, call_next):
        # Verificar si la ruta está excluida
        if self._is_excluded_path(request.url.path):
            return await call_next(request)
        
        # Para métodos seguros (GET, HEAD, OPTIONS) no se requiere CSRF
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return await call_next(request)
        
        # Para métodos que modifican datos, verificar CSRF
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            await self._verify_csrf(request)
        
        return await call_next(request)
    
    def _is_excluded_path(self, path: str) -> bool:
        """Verifica si la ruta está excluida de CSRF"""
        return any(path.startswith(excluded) for excluded in self.exclude_paths)
    
    async def _verify_csrf(self, request: Request):
        """Verifica el token CSRF"""
        # Obtener token del header
        csrf_token = request.headers.get("X-CSRF-Token")
        if not csrf_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token requerido"
            )
        
        # Obtener session_id desde el token de acceso
        access_token = request.cookies.get("access_token")
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de acceso requerido"
            )
        
        # Generar session_id
        session_id = self._generate_session_id(access_token)
        
        # Verificar token
        if not self._is_valid_csrf_token(session_id, csrf_token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token inválido o expirado"
            )
    
    def _generate_session_id(self, token: str) -> str:
        """Genera un ID de sesión a partir del token"""
        return hashlib.sha256(token.encode()).hexdigest()[:16]
    
    def _is_valid_csrf_token(self, session_id: str, token: str) -> bool:
        """Verifica si el token CSRF es válido"""
        if session_id not in self.csrf_tokens:
            return False
        
        token_data = self.csrf_tokens[session_id]
        
        # Verificar expiración
        if time.time() > token_data['expires_at']:
            del self.csrf_tokens[session_id]
            return False
        
        # Verificar token usando comparación segura
        return secrets.compare_digest(token_data['token'], token)
    
    def generate_csrf_token(self, session_id: str) -> str:
        """Genera un nuevo token CSRF"""
        token = secrets.token_urlsafe(32)
        self.csrf_tokens[session_id] = {
            'token': token,
            'expires_at': time.time() + 3600  # 1 hora
        }
        return token
    
    def revoke_csrf_token(self, session_id: str):
        """Revoca un token CSRF"""
        if session_id in self.csrf_tokens:
            del self.csrf_tokens[session_id]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware para rate limiting
    """
    
    def __init__(self, app, requests_per_minute: int = 60, exclude_paths: List[str] = None):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.exclude_paths = exclude_paths or [
            "/docs",
            "/openapi.json",
            "/redoc",
            "/static",
            "/assets"
        ]
        
        # Almacenamiento de solicitudes (en producción usar Redis)
        self.requests = defaultdict(deque)
        
    async def dispatch(self, request: Request, call_next):
        # Verificar si la ruta está excluida
        if self._is_excluded_path(request.url.path):
            return await call_next(request)
        
        # Obtener IP del cliente
        client_ip = self._get_client_ip(request)
        
        # Verificar rate limiting
        if not self._is_allowed(client_ip):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Demasiadas solicitudes. Intente nuevamente más tarde.",
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + 60)
                }
            )
        
        # Registrar solicitud
        self._record_request(client_ip)
        
        # Añadir headers de rate limiting a la respuesta
        response = await call_next(request)
        
        # Calcular solicitudes restantes
        current_requests = len(self.requests[client_ip])
        remaining = max(0, self.requests_per_minute - current_requests)
        
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)
        
        return response
    
    def _is_excluded_path(self, path: str) -> bool:
        """Verifica si la ruta está excluida del rate limiting"""
        return any(path.startswith(excluded) for excluded in self.exclude_paths)
    
    def _get_client_ip(self, request: Request) -> str:
        """Obtiene la IP del cliente"""
        # Verificar headers de proxy
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback a IP directa
        return request.client.host if request.client else "unknown"
    
    def _is_allowed(self, client_ip: str) -> bool:
        """Verifica si la IP tiene permitido hacer más solicitudes"""
        now = time.time()
        
        # Limpiar solicitudes antiguas (más de 1 minuto)
        while self.requests[client_ip] and self.requests[client_ip][0] < now - 60:
            self.requests[client_ip].popleft()
        
        # Verificar si excede el límite
        return len(self.requests[client_ip]) < self.requests_per_minute
    
    def _record_request(self, client_ip: str):
        """Registra una solicitud"""
        self.requests[client_ip].append(time.time())


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware para headers de seguridad
    """
    
    def __init__(self, app):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Añadir headers de seguridad
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy (ajustar según necesidades)
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        response.headers["Content-Security-Policy"] = csp
        
        # Strict-Transport-Security (solo en HTTPS)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        return response


# Instancias globales para uso fácil
csrf_middleware = CSRFMiddleware
rate_limit_middleware = RateLimitMiddleware
security_headers_middleware = SecurityHeadersMiddleware

# Función helper para configurar todos los middlewares de seguridad
def setup_security_middleware(app, 
                           csrf_exclude_paths: List[str] = None,
                           rate_limit_requests_per_minute: int = 60,
                           rate_limit_exclude_paths: List[str] = None):
    """
    Configura todos los middlewares de seguridad en la aplicación FastAPI
    """
    # Headers de seguridad (siempre primero)
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Rate limiting
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=rate_limit_requests_per_minute,
        exclude_paths=rate_limit_exclude_paths
    )
    
    # CSRF protection
    app.add_middleware(
        CSRFMiddleware,
        exclude_paths=csrf_exclude_paths
    )
