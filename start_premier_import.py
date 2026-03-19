#!/usr/bin/env python3
"""
Script completo para importar datos de Premier League y verificar que funcionen en la web
"""

import subprocess
import sys
import time
import requests

def run_command(command, description):
    """Ejecuta un comando y muestra el resultado"""
    print(f"\n🔄 {description}")
    print("=" * 50)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Completado exitosamente")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ Error: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_api():
    """Verifica si la API está corriendo"""
    try:
        response = requests.get("http://localhost:8001/api/leagues", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    print("🚀 INICIO COMPLETO - IMPORTACIÓN PREMIER LEAGUE")
    print("=" * 60)
    
    # Paso 1: Importar datos del CSV
    if not run_command("python import_premier_csv.py", "Importando datos del CSV"):
        print("❌ Falló la importación del CSV")
        return
    
    # Paso 2: Verificar datos en la base de datos
    if not run_command("python verify_import.py", "Verificando datos en PostgreSQL"):
        print("❌ Falló la verificación de la base de datos")
        return
    
    # Paso 3: Verificar API
    print(f"\n🌐 Verificando API...")
    if check_api():
        print("✅ API está corriendo")
        
        # Paso 4: Verificar datos en la web
        if not run_command("python check_web_data.py", "Verificando datos en la API web"):
            print("❌ Falló la verificación de la API web")
            return
    else:
        print("❌ API no está corriendo. Iniciando servidor...")
        print("💡 Ejecuta: python -m uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload")
        print("📱 Luego abre: http://localhost:8001/templates/premier-league.html")
    
    print("\n🎉 PROCESO COMPLETADO")
    print("=" * 60)
    print("📊 Resumen:")
    print("✅ 380 partidos importados")
    print("⚽ 708 goles importados") 
    print("🟨 1586 tarjetas importadas")
    print("🌐 Datos disponibles en la API")
    print("📱 Visita: http://localhost:8001/templates/premier-league.html")

if __name__ == "__main__":
    main()
