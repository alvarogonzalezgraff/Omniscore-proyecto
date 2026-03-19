#!/usr/bin/env python3
"""
Script para verificar que los datos se muestran correctamente en la aplicación
"""
import requests
import json
from datetime import datetime

def test_api_endpoints():
    """Prueba los endpoints principales de la API"""
    
    base_url = "http://localhost:8001"
    
    endpoints = [
        "/api/leagues",
        "/api/teams", 
        "/api/matches",
        "/api/standings",
        "/api/scraped-data"
    ]
    
    print("=== VERIFICACIÓN DE ENDPOINTS DE LA API ===")
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {endpoint}: {len(data) if isinstance(data, list) else 'OK'} registros")
                
                # Mostrar algunos datos de ejemplo
                if isinstance(data, list) and len(data) > 0:
                    print(f"   Ejemplo: {json.dumps(data[0], indent=2, ensure_ascii=False)[:200]}...")
                    
            else:
                print(f"❌ {endpoint}: Error {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint}: No se puede conectar al servidor")
            return False
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    
    return True

def test_specific_data():
    """Verifica datos específicos que podrían faltar"""
    
    base_url = "http://localhost:8001"
    
    print("\n=== VERIFICACIÓN DE DATOS ESPECÍFICOS ===")
    
    # Verificar ligas
    try:
        response = requests.get(f"{base_url}/api/leagues")
        if response.status_code == 200:
            leagues = response.json()
            print(f"✅ Ligas encontradas: {len(leagues)}")
            
            # Verificar LaLiga
            laliga = next((l for l in leagues if "LaLiga" in l.get("name", "")), None)
            if laliga:
                print(f"✅ LaLiga encontrada: ID {laliga['id']}")
                
                # Verificar equipos de LaLiga
                teams_response = requests.get(f"{base_url}/api/teams?league_id={laliga['id']}")
                if teams_response.status_code == 200:
                    teams = teams_response.json()
                    print(f"✅ Equipos LaLiga: {len(teams)}")
                    
                    # Verificar partidos
                    matches_response = requests.get(f"{base_url}/api/matches?league_id={laliga['id']}")
                    if matches_response.status_code == 200:
                        matches = matches_response.json()
                        print(f"✅ Partidos LaLiga: {len(matches)}")
                        
                        # Verificar detalles de un partido
                        if len(matches) > 0:
                            match_id = matches[0]['id']
                            
                            # Verificar goles
                            goals_response = requests.get(f"{base_url}/api/matches/{match_id}/goals")
                            if goals_response.status_code == 200:
                                goals = goals_response.json()
                                print(f"✅ Goles partido {match_id}: {len(goals)}")
                            
                            # Verificar tarjetas
                            cards_response = requests.get(f"{base_url}/api/matches/{match_id}/cards")
                            if cards_response.status_code == 200:
                                cards = cards_response.json()
                                print(f"✅ Tarjetas partido {match_id}: {len(cards)}")
                            
                            # Verificar cambios
                            subs_response = requests.get(f"{base_url}/api/matches/{match_id}/substitutions")
                            if subs_response.status_code == 200:
                                subs = subs_response.json()
                                print(f"✅ Cambios partido {match_id}: {len(subs)}")
                    else:
                        print(f"❌ Error obteniendo partidos: {matches_response.status_code}")
                else:
                    print(f"❌ Error obteniendo equipos: {teams_response.status_code}")
            else:
                print("❌ LaLiga no encontrada")
        else:
            print(f"❌ Error obteniendo ligas: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en verificación: {e}")

def check_missing_data():
    """Verifica si hay datos que podrían estar faltando"""
    
    print("\n=== VERIFICACIÓN DE DATOS FALTANTES ===")
    
    # Aquí podrías agregar verificaciones específicas
    # basándote en los datos que sabes que deberían existir
    
    expected_data = {
        "LaLiga EA Sports": "debería tener ~20 equipos",
        "Premier League": "debería tener ~20 equipos", 
        "Bundesliga": "debería tener ~18 equipos",
        "Serie A": "debería tener ~20 equipos",
        "Ligue 1": "debería tener ~18 equipos"
    }
    
    base_url = "http://localhost:8001"
    
    try:
        response = requests.get(f"{base_url}/api/leagues")
        if response.status_code == 200:
            leagues = response.json()
            league_names = [l.get("name", "") for l in leagues]
            
            for expected_league, description in expected_data.items():
                if expected_league in league_names:
                    print(f"✅ {expected_league}: encontrada")
                else:
                    print(f"❌ {expected_league}: NO encontrada - {description}")
                    
    except Exception as e:
        print(f"❌ Error verificando ligas: {e}")

if __name__ == "__main__":
    print("Iniciando verificación de datos...")
    print("Asegúrate de que el servidor API está corriendo en http://localhost:8001")
    print()
    
    # Test API endpoints
    if test_api_endpoints():
        # Test specific data
        test_specific_data()
        
        # Check for missing data
        check_missing_data()
    
    print("\nVerificación completada.")
