import sqlite3

# Conexión a SQLite
conn = sqlite3.connect('database/app.db')
cursor = conn.cursor()

print('=== INFORMACIÓN DE USUARIOS ===')
print()

# Obtener todos los usuarios
cursor.execute('SELECT username, full_name, password, created_at FROM users')
users = cursor.fetchall()

print('Usuarios encontrados:')
for user in users:
    username, full_name, password, created_at = user
    print(f'Usuario: {username}')
    print(f'Nombre completo: {full_name}')
    print(f'Contraseña (encriptada): {password}')
    print(f'Creado: {created_at}')
    print('-' * 40)

print()
print('🔍 NOTA SOBRE LAS CONTRASEÑAS:')
print('Las contraseñas están encriptadas con bcrypt (hash $2b$12$...)')
print('No es posible recuperar la contraseña original en texto plano.')
print('Solo se puede verificar si una contraseña coincide con el hash.')
print()

# Verificar si hay archivos de configuración que puedan tener la contraseña
import os
config_files = ['.env', 'config.py', 'api/config.py']

for config_file in config_files:
    if os.path.exists(config_file):
        print(f'📁 Revisando archivo: {config_file}')
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'alvaro' in content.lower() or 'password' in content.lower():
                    print('   ⚠️ Contenido relevante encontrado:')
                    lines = content.split('\n')
                    for line in lines:
                        if 'alvaro' in line.lower() or 'password' in line.lower():
                            print(f'   {line.strip()}')
                else:
                    print('   ✅ Sin información relevante')
        except Exception as e:
            print(f'   ❌ Error leyendo archivo: {e}')
        print()

conn.close()
