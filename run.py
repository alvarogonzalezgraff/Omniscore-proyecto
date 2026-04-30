#!/usr/bin/env python3
import os
import sys
import subprocess

if __name__ == "__main__":
    # Cambiamos el directorio de trabajo a backend para que las rutas relativas funcionen
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
    os.chdir(backend_dir)
    
    # Ejecutar el run.py original dentro de backend
    try:
        sys.exit(subprocess.call([sys.executable, "run.py"] + sys.argv[1:]))
    except KeyboardInterrupt:
        pass
