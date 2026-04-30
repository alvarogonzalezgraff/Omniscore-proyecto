#!/usr/bin/env python3
"""
Script principal para arrancar la aplicación Omniscore
Inicia el servidor FastAPI con soporte para servir archivos HTML
"""
import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print(">> Iniciando Omniscore - Aplicacion de Apuestas Deportivas")
    print("=" * 60)
    print("")
    print("API: http://localhost:8001/docs")
    print("Web: http://localhost:8001/")
    print("\nPresiona Ctrl+C para detener el servidor\n")
    print("=" * 60)
    
    # Iniciar el servidor uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,  # Auto-reload durante desarrollo
        log_level="info"
    )
