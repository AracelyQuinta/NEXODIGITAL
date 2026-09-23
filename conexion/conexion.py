import os
import time

import psycopg2
from flask import g, has_app_context
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()


def get_db_connection():
    """Obtiene una conexión activa y la registra para el cierre automático."""
    if has_app_context():
        conexion_actual = getattr(g, 'nexo_db_connection', None)
        if conexion_actual is not None and not conexion_actual.closed:
            return conexion_actual

    db_url = os.getenv('DATABASE_URL')
    parametros = {}
    application_name = 'nexodigital-web'

    if db_url:
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        parametros['dsn'] = db_url
    else:
        application_name = 'nexodigital-local'
        parametros = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'dbname': os.getenv('DB_NAME', 'nexodigital'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', ''),
        }

    ultimo_error = None
    for intento in range(3):
        try:
            conexion = psycopg2.connect(
                **parametros,
                cursor_factory=RealDictCursor,
                connect_timeout=10,
                application_name=application_name
            )
            if has_app_context():
                g.nexo_db_connection = conexion
            return conexion
        except psycopg2.OperationalError as error:
            ultimo_error = error
            if intento < 2:
                time.sleep(0.5 * (intento + 1))

    raise ultimo_error


def close_db_connection(exception=None):
    """Cierra la conexión de la solicitud al finalizar el contexto Flask."""
    conexion = getattr(g, 'nexo_db_connection', None)
    if conexion is not None and not conexion.closed:
        conexion.close()
    g.nexo_db_connection = None
