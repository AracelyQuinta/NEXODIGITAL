# ==============================================================================
# PROYECTO: NEXODIGITAL - CONEXIÓN CENTRALIZADA A POSTGRESQL
# ==============================================================================
# SEGURIDAD: la contraseña NO se escribe aquí. Se lee del archivo ".env"
# (que NO se sube a GitHub gracias al .gitignore). Así el código puede subirse
# al repositorio sin exponer la contraseña real.
#
# ==============================================================================

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Carga las variables definidas en el archivo .env (si existe).
load_dotenv()


def get_db_connection():
    """
    Crea y retorna una conexión a la base de datos PostgreSQL.
    Permite dos modos:
    1. Si existe la variable DATABASE_URL (Render, Neon, Supabase en la nube),
       se conecta directamente mediante la URL de conexión.
    2. En local, lee las variables individuales definidas en el archivo .env.

    Se usa RealDictCursor para que las filas se puedan leer por el nombre de la
    columna, por ejemplo: fila['nombre'].
    """
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        # Algunos proveedores como Render usan 'postgres://' en vez de 'postgresql://'
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        return conn

    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        dbname=os.getenv('DB_NAME', 'nexodigital'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', ''),
        cursor_factory=RealDictCursor
    )
    return conn
