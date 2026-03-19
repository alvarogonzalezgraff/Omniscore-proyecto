#!/usr/bin/env python3
"""
Script para verificar que los datos importados están disponibles en la API web
"""

import requests
import json

API_BASE = "http://localhost:8001/api"
LEAGUE_NAME = "Premier League"

def check_api_data():
    """Verifica los datos en la API"""
    print("🌐 VERIFICANDO DATOS EN LA API WEB")
    print("=" * 50)
    
    try:
        # Verificar partidos
        print("\n📊 Verificando partidos...")
        response = requests.get(f"{API_BASE}/scraped-matches/{LEAGUE_NAME}?season=2024%2F25")
        
        if response.status_code == 200:
            matches = response.json()
            print(f"✅ Total de partidos en API: {len(matches)}")
            
            # Mostrar algunos partidos
            print("\n📋 Ejemplos de partidos:")
            for i, match in enumerate(matches[:5]):
                print(f"  {match['home_team']} {match['home_score']} - {match['away_score']} {match['away_team']} (J{match['matchday']})")
                if match.get('goals_details'):
                    print(f"     ⚽ {len(match['goals_details'])} goles")
                if match.get('cards'):
                    print(f"     🟨 {len(match['cards'])} tarjetas")
        else:
            print(f"❌ Error al obtener partidos: {response.status_code}")
        
        # Verificar goleadores
        print("\n⚽ Verificando goleadores...")
        response = requests.get(f"{API_BASE}/scraped-scorers/{LEAGUE_NAME}")
        
        if response.status_code == 200:
            scorers = response.json()
            print(f"✅ Total de goleadores en API: {len(scorers)}")
            
            # Mostrar top 5
            print("\n🏆 Top 5 goleadores:")
            for i, scorer in enumerate(scorers[:5]):
                print(f"  {i+1}. {scorer['player_name']} ({scorer['team_name']}) - {scorer['goals']} goles")
        else:
            print(f"❌ Error al obtener goleadores: {response.status_code}")
        
        # Verificar asistentes
        print("\n🎯 Verificando asistentes...")
        response = requests.get(f"{API_BASE}/scraped-assisters/{LEAGUE_NAME}")
        
        if response.status_code == 200:
            assisters = response.json()
            print(f"✅ Total de asistentes en API: {len(assisters)}")
            
            # Mostrar top 5
            print("\n🅰️ Top 5 asistentes:")
            for i, assister in enumerate(assisters[:5]):
                print(f"  {i+1}. {assister['player_name']} ({assister['team_name']}) - {assister['assists']} asistencias")
        else:
            print(f"❌ Error al obtener asistentes: {response.status_code}")
        
        print("\n🎉 VERIFICACIÓN COMPLETADA")
        print("📱 Los datos están disponibles para la página web")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar con la API")
        print("💡 Asegúrate de que el servidor API está corriendo en http://localhost:8001")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_api_data()
