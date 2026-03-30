#!/usr/bin/env python3
"""
Script para resetear completamente el estado de sesión durante el desarrollo.
Elimina cookies del servidor y archivos de sesión persistente.
"""

import os
import json
from pathlib import Path

def reset_session_state():
    """Elimina todos los archivos de sesión y cookies persistentes"""
    
    # Rutas a los archivos de sesión
    base_path = Path(__file__).parent
    sessions_file = base_path / "_historial_y_herramientas" / "active_sessions.json"
    cookies_file = base_path / "_historial_y_herramientas" / "cookie_sessions.json"
    
    removed_files = []
    
    # Eliminar archivo de sesiones activas
    if sessions_file.exists():
        sessions_file.unlink()
        removed_files.append(str(sessions_file))
        print(f"[OK] Eliminado: {sessions_file}")
    
    # Eliminar archivo de cookies
    if cookies_file.exists():
        cookies_file.unlink()
        removed_files.append(str(cookies_file))
        print(f"[OK] Eliminado: {cookies_file}")
    
    if removed_files:
        print(f"\n[RESET] Sesión reseteada. Se eliminaron {len(removed_files)} archivos.")
        print("Ahora puedes probar el flujo de login desde cero.")
    else:
        print("[INFO] No se encontraron archivos de sesión para eliminar.")
    
    return len(removed_files) > 0

if __name__ == "__main__":
    reset_session_state()
