"""
Endpoints para gestión de temas y preferencias de usuario
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json

from .auth_endpoints import get_current_user_from_cookie
from .database import SessionLocal
from .database_orm import UserORM

router = APIRouter(prefix="/api/theme", tags=["theme"])

class ThemeRequest(BaseModel):
    backgroundColor: Optional[str] = None
    textColor: Optional[str] = None
    accentColor: Optional[str] = None
    fontSize: Optional[str] = None
    fontFamily: Optional[str] = None
    borderRadius: Optional[str] = None
    density: Optional[str] = None

class ThemeResponse(BaseModel):
    success: bool
    message: str
    theme: Optional[Dict[str, Any]] = None

@router.post("/save", response_model=ThemeResponse)
async def save_theme(
    theme_data: ThemeRequest,
    current_user = Depends(get_current_user_from_cookie)
):
    """
    Guarda las preferencias de tema del usuario autenticado
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no autenticado"
        )
    
    try:
        with SessionLocal() as session:
            user = session.query(UserORM).filter(UserORM.id == current_user.id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )
            
            # Convertir a diccionario y filtrar valores no nulos
            theme_dict = theme_data.dict(exclude_unset=True)
            
            # Obtener preferencias existentes
            current_preferences = {}
            if user.theme_preferences:
                try:
                    current_preferences = json.loads(user.theme_preferences)
                except json.JSONDecodeError:
                    current_preferences = {}
            
            # Actualizar con nuevos valores
            current_preferences.update(theme_dict)
            
            # Guardar en base de datos
            user.theme_preferences = json.dumps(current_preferences)
            session.commit()
            
            return ThemeResponse(
                success=True,
                message="Preferencias de tema guardadas exitosamente",
                theme=current_preferences
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar preferencias: {str(e)}"
        )

@router.get("/load", response_model=ThemeResponse)
async def load_theme(
    current_user = Depends(get_current_user_from_cookie)
):
    """
    Carga las preferencias de tema del usuario autenticado
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no autenticado"
        )
    
    try:
        with SessionLocal() as session:
            user = session.query(UserORM).filter(UserORM.id == current_user.id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )
            
            # Obtener preferencias
            theme_preferences = {}
            if user.theme_preferences:
                try:
                    theme_preferences = json.loads(user.theme_preferences)
                except json.JSONDecodeError:
                    theme_preferences = {}
            
            return ThemeResponse(
                success=True,
                message="Preferencias de tema cargadas exitosamente",
                theme=theme_preferences
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cargar preferencias: {str(e)}"
        )

@router.delete("/reset", response_model=ThemeResponse)
async def reset_theme(
    current_user = Depends(get_current_user_from_cookie)
):
    """
    Restablece las preferencias de tema del usuario
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no autenticado"
        )
    
    try:
        with SessionLocal() as session:
            user = session.query(UserORM).filter(UserORM.id == current_user.id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )
            
            # Limpiar preferencias
            user.theme_preferences = None
            session.commit()
            
            return ThemeResponse(
                success=True,
                message="Preferencias de tema restablecidas",
                theme={}
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al restablecer preferencias: {str(e)}"
        )
