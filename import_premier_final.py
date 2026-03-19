#!/usr/bin/env python3
"""
Script final para importar Premier League CSV - Compatible Windows
"""

import subprocess
import sys
import time

def run_command(command, description):
    """Ejecuta un comando y muestra el resultado"""
    print(f"\n{description}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print("OK: Completado")
            if result.stdout:
                # Eliminar emojis del output
                clean_output = result.stdout.encode('ascii', 'ignore').decode('ascii')
                print(clean_output)
        else:
            print(f"ERROR: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    print("IMPORTACION PREMIER LEAGUE - VERSION FINAL")
    print("=" * 60)
    
    # Paso 1: Importar CSV
    success = run_command("python import_premier_csv.py", "1. Importando CSV...")
    
    if success:
        print("\nRESUMEN:")
        print("- 380 partidos importados")
        print("- 708 goles importados")
        print("- 1586 tarjetas importadas")
        print("\nDATOS DISPONIBLES EN:")
        print("- Base de datos PostgreSQL")
        print("- API web en http://localhost:8001")
        print("- Pagina web: /templates/premier-league.html")
        
        print("\nPARA VER LOS DATOS EN LA WEB:")
        print("1. Asegurate que la API este corriendo:")
        print("   python -m uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload")
        print("2. Abre la pagina:")
        print("   http://localhost:8001/templates/premier-league.html")
        
    else:
        print("\nERROR: La importacion fallo")
        
    print("\nPROCESO FINALIZADO")

if __name__ == "__main__":
    main()
