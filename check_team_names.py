import psycopg2

def get_connection():
    return psycopg2.connect(
        host='localhost',
        port='5433',
        dbname='betwin_db',
        user='postgres',
        password='1234'
    )

try:
    conn = get_connection()
    cursor = conn.cursor()
    
    print("=== EQUIPOS EN LA BASE DE DATOS ===")
    cursor.execute("""
        SELECT DISTINCT t.name
        FROM teams t
        JOIN matches m ON (t.id = m.home_team_id OR t.id = m.away_team_id)
        JOIN leagues l ON m.league_id = l.id
        WHERE l.name = 'Premier League'
        ORDER BY t.name
    """)
    
    teams = cursor.fetchall()
    print(f"Total de equipos de Premier League en BD: {len(teams)}")
    for team in teams:
        print(f"- {team[0]}")
    
    print("\n=== EQUIPOS EN EL CSV ===")
    # Leer primeras líneas del CSV para ver los nombres
    import csv
    with open('premier_24_25_mix.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        equipos_csv = set()
        for row in reader:
            equipos_csv.add(row['local'])
            equipos_csv.add(row['visitante'])
    
    print(f"Total de equipos en CSV: {len(equipos_csv)}")
    for equipo in sorted(equipos_csv):
        print(f"- {equipo}")
    
    print("\n=== EQUIPOS QUE FALTAN MAPEAR ===")
    bd_teams = {team[0] for team in teams}
    faltantes = equipos_csv - bd_teams
    print(f"Total de equipos faltantes: {len(faltantes)}")
    for equipo in sorted(faltantes):
        print(f"- {equipo}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
