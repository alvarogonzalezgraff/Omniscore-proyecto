#!/usr/bin/env python3
"""
Script para probar que la web muestra correctamente los datos importados
"""

import requests
import json

def test_web_display():
    """Prueba que los datos se muestran correctamente en la web"""
    print("🧪 PROBANDO VISUALIZACIÓN WEB")
    print("=" * 50)
    
    try:
        # Obtener partidos
        response = requests.get("http://localhost:8001/api/scraped-matches/Premier%20League?season=2024%2F25")
        
        if response.status_code == 200:
            matches = response.json()
            print(f"✅ Total de partidos: {len(matches)}")
            
            # Buscar un partido con muchos eventos
            test_match = None
            for match in matches:
                if (match.get('goals_details') and len(match['goals_details']) > 0) or \
                   (match.get('cards') and len(match['cards']) > 0):
                    test_match = match
                    break
            
            if test_match:
                print(f"\n📋 Partido de prueba:")
                print(f"   {test_match['home_team']} {test_match['home_score']} - {test_match['away_score']} {test_match['away_team']}")
                print(f"   Jornada: {test_match['matchday']}")
                
                print(f"\n⚽ Goles ({len(test_match.get('goals_details', []))}):")
                for i, goal in enumerate(test_match.get('goals_details', [])[:5]):
                    print(f"   {i+1}. {goal['player']} (min {goal['minute']})")
                    if goal.get('assist'):
                        print(f"      Asistencia: {goal['assist']}")
                    if goal.get('is_penalty'):
                        print(f"      ⚠️ Penalti")
                
                print(f"\n🟨 Tarjetas ({len(test_match.get('cards', []))}):")
                for i, card in enumerate(test_match.get('cards', [])[:5]):
                    icon = "🟥" if card['type'] == 'Roja' else "🟨"
                    print(f"   {i+1}. {icon} {card['player']} (min {card['minute']})")
                
                print(f"\n🔄 Cambios ({len(test_match.get('substitutions', []))}):")
                for i, sub in enumerate(test_match.get('substitutions', [])[:3]):
                    print(f"   {i+1}. {sub['player_in']} ⬆ {sub['player_out']} ⬇ (min {sub['minute']})")
                
                print(f"\n✅ DATOS LISTOS PARA VISUALIZAR")
                print(f"📱 Abre: http://localhost:8001/templates/premier-league.html")
                print(f"🔍 Busca el partido y haz clic en 'Ver detalles completos'")
                
            else:
                print("⚠️ No se encontró partido con eventos para probar")
        else:
            print(f"❌ Error al obtener partidos: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_web_display()
