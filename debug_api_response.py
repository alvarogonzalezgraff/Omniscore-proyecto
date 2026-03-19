import requests
import json

API_BASE = "http://localhost:8001/api"
LEAGUE_NAME = "Premier League"

def debug_api_response():
    """Depura la respuesta de la API para ver la estructura exacta"""
    print("🔍 DEPURANDO RESPUESTA DE LA API")
    print("=" * 50)
    
    try:
        # Obtener partidos
        response = requests.get(f"{API_BASE}/scraped-matches/{LEAGUE_NAME}?season=2024%2F25")
        
        if response.status_code == 200:
            matches = response.json()
            print(f"✅ Total de partidos: {len(matches)}")
            
            # Mostrar estructura del primer partido
            if matches:
                first_match = matches[0]
                print(f"\n📋 Estructura del primer partido:")
                print(f"   ID: {first_match.get('id')}")
                print(f"   Equipos: {first_match.get('home_team')} vs {first_match.get('away_team')}")
                print(f"   Marcador: {first_match.get('home_score')} - {first_match.get('away_score')}")
                
                print(f"\n⚽ Goles (goals_details):")
                goals = first_match.get('goals_details', [])
                print(f"   Cantidad: {len(goals)}")
                if goals:
                    for i, goal in enumerate(goals[:3]):
                        print(f"   Gol {i+1}: {goal}")
                
                print(f"\n🟨 Tarjetas (cards):")
                cards = first_match.get('cards', [])
                print(f"   Cantidad: {len(cards)}")
                if cards:
                    for i, card in enumerate(cards[:3]):
                        print(f"   Tarjeta {i+1}: {card}")
                
                print(f"\n🔄 Cambios (substitutions):")
                subs = first_match.get('substitutions', [])
                print(f"   Cantidad: {len(subs)}")
                if subs:
                    for i, sub in enumerate(subs[:2]):
                        print(f"   Cambio {i+1}: {sub}")
                
                print(f"\n🚑 Lesiones (injuries):")
                injuries = first_match.get('injuries', [])
                print(f"   Cantidad: {len(injuries)}")
                if injuries:
                    for i, injury in enumerate(injuries[:2]):
                        print(f"   Lesión {i+1}: {injury}")
                
                # Guardar ejemplo completo en archivo
                with open('api_response_example.json', 'w', encoding='utf-8') as f:
                    json.dump(first_match, f, indent=2, ensure_ascii=False)
                print(f"\n💾 Estructura completa guardada en: api_response_example.json")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_api_response()
