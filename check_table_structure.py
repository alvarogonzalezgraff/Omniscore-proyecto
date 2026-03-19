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
    
    print("=== ESTRUCTURA TABLA CARDS ===")
    cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'cards' AND table_schema = 'public'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    for col in columns:
        print(f"- {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
    
    print("\n=== ESTRUCTURA TABLA GOALS ===")
    cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'goals' AND table_schema = 'public'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    for col in columns:
        print(f"- {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
    
    print("\n=== VERIFICANDO SECUENCIAS ===")
    cursor.execute("""
        SELECT sequence_name, start_value, increment_by, last_value
        FROM information_schema.sequences 
        WHERE sequence_schema = 'public'
        ORDER BY sequence_name
    """)
    
    sequences = cursor.fetchall()
    for seq in sequences:
        print(f"- {seq[0]}: start={seq[1]}, increment={seq[2]}, last={seq[3]}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
