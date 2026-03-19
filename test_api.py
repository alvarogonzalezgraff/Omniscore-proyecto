import requests

try:
    response = requests.get('http://localhost:8001/api/standings?league=LaLiga%20EA%20Sports&season=2024/2025')
    print(f'Status Code: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        print(f'Datos encontrados: {len(data)} equipos')
        print()
        print('Top 3 equipos:')
        for team in data[:3]:
            print(f'  {team["position"]}. {team["team_name"]} - {team["points"]} pts')
    else:
        print(f'Error Response: {response.text[:500]}')
        
except Exception as e:
    print(f'Error: {e}')
