# ==============================================================================
# PROYECTO: NEXODIGITAL - CREAR ADMINISTRADORES (Semana 14)
# ==============================================================================
# Crea los usuarios administradores iniciales del sistema (los "dueños").
# Se ejecuta desde la terminal, una sola vez, para dar de alta al primer admin.
# Después, un admin ya puede crear a sus colaboradores desde la propia web.
#
# CÓMO USARLO:
#   python crear_admin.py
# Te pedirá cuántos admins crear y luego el usuario y contraseña de cada uno.
#
# La contraseña se guarda protegida con hash, igual que en el registro web.
# ==============================================================================

from werkzeug.security import generate_password_hash
from conexion.conexion import get_db_connection


def crear_un_admin(usuario, password):
    """Inserta un administrador en la base de datos con la contraseña protegida."""
    if len(usuario) < 3 or len(password) < 4:
        print(f'  -> "{usuario}": el usuario debe tener 3+ caracteres y la contraseña 4+. Omitido.')
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM usuarios WHERE usuario = %s', (usuario,))
    if cursor.fetchone():
        print(f'  -> "{usuario}" ya existe. Omitido.')
        cursor.close()
        conn.close()
        return

    password_hash = generate_password_hash(password)
    cursor.execute(
        'INSERT INTO usuarios (usuario, password) VALUES (%s, %s)',
        (usuario, password_hash)
    )
    conn.commit()
    cursor.close()
    conn.close()
    print(f'  -> Administrador "{usuario}" creado correctamente.')


def main():
    print("=== Crear administradores de NexoDigital ===")
    try:
        cantidad = int(input("¿Cuántos administradores quieres crear? "))
    except ValueError:
        print("Número no válido.")
        return

    for i in range(1, cantidad + 1):
        print(f"\n--- Administrador {i} ---")
        usuario = input("  Nombre de usuario: ").strip()
        password = input("  Contraseña: ").strip()
        crear_un_admin(usuario, password)

    print("\n¡Listo! Ya pueden iniciar sesión en la web.")


if __name__ == '__main__':
    main()
