import os
import time

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()


def get_db_connection():
    """Abre PostgreSQL desde DATABASE_URL o desde las variables locales."""
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
            return psycopg2.connect(
                **parametros,
                cursor_factory=RealDictCursor,
                connect_timeout=10,
                application_name=application_name
            )
        except psycopg2.OperationalError as error:
            ultimo_error = error
            if intento < 2:
                time.sleep(0.5 * (intento + 1))

    raise ultimo_error
