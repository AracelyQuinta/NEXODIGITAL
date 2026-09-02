import sqlite3
import os

# Ruta a la raíz del proyecto y al archivo de la base de datos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'nexodigital.db')


# Abre y devuelve una conexión a la base de datos
def get_connection():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # permite leer filas como fila['nombre']
    return conn


# Crea las tablas si no existen (se llama una vez al iniciar la app)
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Tabla de clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            negocio TEXT NOT NULL,
            servicio TEXT NOT NULL,
            ciudad TEXT NOT NULL
        )
    ''')

    # Tabla de servicios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servicios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            tiempo_estimado TEXT,
            imagen TEXT,
            descripcion TEXT NOT NULL,
            disponible INTEGER NOT NULL DEFAULT 1
        )
    ''')

    # Tabla de proveedores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proveedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            servicio TEXT NOT NULL,
            sitio TEXT NOT NULL,
            estado TEXT NOT NULL
        )
    ''')

    # Tabla de facturación
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS facturacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            numero TEXT NOT NULL,
            cliente TEXT NOT NULL,
            fecha TEXT NOT NULL,
            validez TEXT,
            servicios_json TEXT,
            subtotal REAL,
            iva REAL,
            monto REAL NOT NULL,
            anticipo REAL DEFAULT 0,
            saldo_pendiente REAL DEFAULT 0,
            estado TEXT NOT NULL,
            notas TEXT
        )
    ''')

    # Si la tabla de clientes está vacía, se insertan los datos de ejemplo
    # (esto solo ocurre la primera vez; después se maneja todo desde el formulario)
    cursor.execute('SELECT COUNT(*) FROM clientes')
    if cursor.fetchone()[0] == 0:
        clientes_iniciales = [
            ('Panadería El Trigal', 'Panadería', 'Página Web + Menú QR', 'Santo Domingo'),
            ('Boutique Bella', 'Tienda de Ropa', 'Catálogo Digital', 'Quito'),
            ('Taller Mecánico RPM', 'Taller Automotriz', 'Formulario de Citas', 'Santo Domingo'),
            ('Café Aroma Amazónico', 'Cafetería', 'Menú QR + WhatsApp', 'Puyo')
        ]
        cursor.executemany(
            'INSERT INTO clientes (nombre, negocio, servicio, ciudad) VALUES (?, ?, ?, ?)',
            clientes_iniciales
        )

    # Si la tabla de servicios está vacía, se insertan los servicios de ejemplo
    cursor.execute('SELECT COUNT(*) FROM servicios')
    if cursor.fetchone()[0] == 0:
        servicios_iniciales = [
            ('Páginas Web para Negocios', 250.00, '5 a 7 días',
             'https://images.unsplash.com/photo-1547658719-da2b51169166',
             'Diseño de sitios web claros, rápidos y adaptados para celulares y computadoras.', 1),
            ('Catálogo Digital de Productos', 120.00, '3 a 4 días',
             'https://images.unsplash.com/photo-1460925895917-afdab827c52f',
             'Muestra tus productos con fotos, precios y botón para hacer pedidos por WhatsApp.', 1),
            ('Menú Digital con Código QR', 65.00, '24 a 48 horas',
             'https://images.unsplash.com/photo-1595079672139-5470887216e9',
             'Menú interactivo para restaurantes y cafeterías accesible escaneando un código QR.', 1),
            ('Formularios de Contacto y Pedidos', 85.00, '2 a 3 días',
             'https://images.unsplash.com/photo-1551288049-bebda4e38f71',
             'Formularios personalizados para recibir solicitudes, cotizaciones y reservas.', 1),
            ('Botón de WhatsApp y Redes Sociales', 45.00, '24 horas',
             'https://images.unsplash.com/photo-1611746872915-64382b5c76da',
             'Integración de enlaces directos a WhatsApp, Instagram, Facebook y TikTok.', 1),
            ('Asesoría y Optimización Web', 110.00, '3 a 5 días',
             'https://images.unsplash.com/photo-1507238691740-187a5b1d37b8',
             'Revisión técnica de páginas web para mejorar su velocidad y accesibilidad.', 0)
        ]
        cursor.executemany(
            '''INSERT INTO servicios (nombre, precio, tiempo_estimado, imagen, descripcion, disponible)
               VALUES (?, ?, ?, ?, ?, ?)''',
            servicios_iniciales
        )

    # Si la tabla de proveedores está vacía, se insertan los proveedores de ejemplo
    cursor.execute('SELECT COUNT(*) FROM proveedores')
    if cursor.fetchone()[0] == 0:
        proveedores_iniciales = [
            ('Hostinger', 'Servidor y Hosting', 'hostinger.com', 'Activo'),
            ('GoDaddy', 'Registro de Dominios', 'godaddy.com', 'Activo'),
            ('Figma', 'Diseño de Interfaces', 'figma.com', 'Activo'),
            ('Cloudflare', 'Certificados SSL y Seguridad', 'cloudflare.com', 'Pendiente')
        ]
        cursor.executemany(
            'INSERT INTO proveedores (nombre, servicio, sitio, estado) VALUES (?, ?, ?, ?)',
            proveedores_iniciales
        )

    conn.commit()  # guarda los cambios
    conn.close()   # cierra la conexión