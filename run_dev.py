#!/usr/bin/env python3
"""
Script de desarrollo para Omniscore con opciones de recarga controlada
"""
import uvicorn
import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Servidor de desarrollo Omniscore")
    parser.add_argument("--no-reload", action="store_true", 
                       help="Desactivar recarga automática (mantiene sesiones)")
    parser.add_argument("--port", type=int, default=8001,
                       help="Puerto del servidor (default: 8001)")
    parser.add_argument("--host", default="0.0.0.0",
                       help="Host del servidor (default: 0.0.0.0)")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print(">> Omniscore - Modo Desarrollo")
    print("=" * 60)
    print(f"API: http://{args.host}:{args.port}/docs")
    print(f"Web: http://{args.host}:{args.port}/")
    print(f"Recarga automática: {'Desactivada' if args.no_reload else 'Activada'}")
    if not args.no_reload:
        print("⚠️  Las sesiones se cerrarán al modificar el backend")
        print("💡 Usa --no-reload para mantener sesiones activas")
    print("\nPresiona Ctrl+C para detener el servidor")
    print("=" * 60)
    
    # Iniciar servidor con configuración especificada
    uvicorn.run(
        "api.main:app",
        host=args.host,
        port=args.port,
        reload=not args.no_reload,
        log_level="info"
    )

if __name__ == "__main__":
    main()
