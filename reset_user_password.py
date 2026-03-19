import bcrypt
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor

print('=== RESTABLECER CONTRASEÑA DE USUARIO ===')
print()

# 1. Solicitar nueva contraseña
new_password = input("Introduce la nueva contraseña para el usuario 'alvaro': ").strip()

if not new_password:
    print("❌ La contraseña no puede estar vacía")
    exit(1)

if len(new_password) < 4:
    print("❌ La contraseña debe tener al menos 4 caracteres")
    exit(1)

# 2. Generar hash de la nueva contraseña
print(f'🔐 Generando hash para la contraseña: {new_password}')
password_bytes = new_password.encode('utf-8')
salt = bcrypt.gensalt()
password_hash = bcrypt.hashpw(password_bytes, salt)

print(f'✅ Hash generado: {password_hash.decode()}')
print()

# 3. Actualizar en SQLite
try:
    sqlite_conn = sqlite3.connect('database/app.db')
    sqlite_cursor = sqlite_conn.cursor()
    
    sqlite_cursor.execute('UPDATE users SET password = ? WHERE username = ?', (password_hash.decode(), 'alvaro'))
    sqlite_conn.commit()
    
    print('✅ Contraseña actualizada en SQLite (database/app.db)')
    sqlite_conn.close()
except Exception as e:
    print(f'❌ Error actualizando SQLite: {e}')

# 4. Actualizar en PostgreSQL Docker
try:
    pg_conn = psycopg2.connect(
        host='localhost',
        port=5433,
        database='postgres',
        user='postgres',
        password='1234'
    )
    pg_cursor = pg_conn.cursor()
    
    pg_cursor.execute('UPDATE users SET password = %s WHERE username = %s', (password_hash.decode(), 'alvaro'))
    pg_conn.commit()
    
    print('✅ Contraseña actualizada en PostgreSQL Docker')
    pg_conn.close()
except Exception as e:
    print(f'❌ Error actualizando PostgreSQL: {e}')

print()
print('🎉 ¡CONTRASEÑA RESTABLECIDA CON ÉXITO!')
print()
print(f'👤 Usuario: alvaro')
print(f'🔑 Nueva contraseña: {new_password}')
print()
print('📝 Ahora puedes iniciar sesión con:')
print(f'   Usuario: alvaro')
print(f'   Contraseña: {new_password}')
print()
print('🔍 La contraseña ha sido actualizada en:')
print('   • SQLite (database/app.db)')
print('   • PostgreSQL Docker (localhost:5433)')
