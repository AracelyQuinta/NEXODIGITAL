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
    conn.row_factory = sqlite3.Row       # permite leer filas como fila['nombre']
    conn.execute('PRAGMA foreign_keys = ON')  # SQLite exige activar las FK en cada conexión
    return conn


# Crea las tablas si no existen (se llama una vez al iniciar la app)
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Tabla de categorías de negocio (ej: Panadería, Tienda de Ropa, Cafetería)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tipos_negocio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
        )
    ''')

    # Tabla de clientes: la cédula es la clave primaria real (identificador único
    # y natural de cada persona/negocio). tipo_negocio_id es clave foránea.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            cedula TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            telefono TEXT NOT NULL,
            correo TEXT NOT NULL,
            tipo_negocio_id INTEGER,
            ciudad TEXT NOT NULL,
            FOREIGN KEY (tipo_negocio_id) REFERENCES tipos_negocio (id)
        )
    ''')

    # Tabla de categorías de servicio (ej: Desarrollo Web, Marketing, Diseño)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tipos_servicio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
        )
    ''')

    # Tabla de servicios: cada servicio pertenece a un tipo_servicio (clave foránea)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servicios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_servicio_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            precio_base REAL NOT NULL,
            imagen TEXT,
            descripcion TEXT NOT NULL,
            disponible INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (tipo_servicio_id) REFERENCES tipos_servicio (id)
        )
    ''')

    # Tabla de estados posibles para un proveedor (Activo, Pendiente, Inactivo)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estados_proveedor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
        )
    ''')

    # Tabla de categorías de infraestructura para proveedores (ej: Hosting, Dominios, SSL)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias_proveedor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
        )
    ''')

    # Tabla de proveedores: estado_id y categoria_id son claves foráneas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proveedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria_id INTEGER NOT NULL,
            sitio TEXT NOT NULL,
            estado_id INTEGER NOT NULL,
            FOREIGN KEY (categoria_id) REFERENCES categorias_proveedor (id),
            FOREIGN KEY (estado_id) REFERENCES estados_proveedor (id)
        )
    ''')

    # Tabla de estados posibles para un documento de facturación
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estados_documento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
        )
    ''')

    # Tabla de facturación: numero es la clave primaria real (identificador único
    # y natural de cada documento), igual que cedula lo es para clientes.
    # cliente_cedula y estado_id son claves foráneas hacia sus tablas relacionadas.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS facturacion (
            numero TEXT PRIMARY KEY,
            tipo TEXT NOT NULL,
            cliente_cedula TEXT NOT NULL,
            fecha TEXT NOT NULL,
            validez TEXT,
            subtotal REAL,
            iva REAL,
            monto REAL NOT NULL,
            anticipo REAL DEFAULT 0,
            saldo_pendiente REAL DEFAULT 0,
            estado_id INTEGER NOT NULL,
            notas TEXT,
            FOREIGN KEY (cliente_cedula) REFERENCES clientes (cedula) ON UPDATE CASCADE,
            FOREIGN KEY (estado_id) REFERENCES estados_documento (id)
        )
    ''')

    # Tabla de detalle: cada fila es un servicio dentro de una factura (relación N:M).
    # Se conecta con facturacion mediante su clave primaria real: numero.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detalle_factura (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            factura_numero TEXT NOT NULL,
            servicio_id INTEGER,
            nombre_servicio TEXT NOT NULL,
            cantidad INTEGER NOT NULL DEFAULT 1,
            precio_base REAL NOT NULL DEFAULT 0,
            ajuste REAL NOT NULL DEFAULT 0,
            total REAL NOT NULL,
            FOREIGN KEY (factura_numero) REFERENCES facturacion (numero) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (servicio_id) REFERENCES servicios (id) ON DELETE SET NULL
        )
    ''')

    # --- Datos de ejemplo (solo se insertan una vez, si la tabla está vacía) ---

    cursor.execute('SELECT COUNT(*) FROM tipos_negocio')
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            'INSERT INTO tipos_negocio (nombre) VALUES (?)',
            [('Panadería',), ('Tienda de Ropa',), ('Taller Automotriz',), ('Cafetería',)]
        )

    cursor.execute('SELECT COUNT(*) FROM clientes')
    if cursor.fetchone()[0] == 0:
        clientes_iniciales = [
            ('1700111222', 'Panadería El Trigal', '0991234567', 'trigal@correo.com', 'Panadería', 'Santo Domingo'),
            ('1700333444', 'Boutique Bella', '0987654321', 'bella@correo.com', 'Tienda de Ropa', 'Quito'),
            ('1700555666', 'Taller Mecánico RPM', '0976543210', 'rpm@correo.com', 'Taller Automotriz', 'Santo Domingo'),
            ('1700777888', 'Café Aroma Amazónico', '0965432109', 'aroma@correo.com', 'Cafetería', 'Puyo')
        ]
        for cedula, nombre, tel, correo, nombre_negocio, ciudad in clientes_iniciales:
            tipo_negocio_id = cursor.execute(
                'SELECT id FROM tipos_negocio WHERE nombre = ?', (nombre_negocio,)
            ).fetchone()['id']
            cursor.execute(
                'INSERT INTO clientes (cedula, nombre, telefono, correo, tipo_negocio_id, ciudad) VALUES (?, ?, ?, ?, ?, ?)',
                (cedula, nombre, tel, correo, tipo_negocio_id, ciudad)
            )

    cursor.execute('SELECT COUNT(*) FROM tipos_servicio')
    if cursor.fetchone()[0] == 0:
        tipos_iniciales = [
            ('Desarrollo Web',),
            ('Marketing Digital',),
            ('Diseño y Catálogos',),
            ('Soporte y Asesoría',)
        ]
        cursor.executemany('INSERT INTO tipos_servicio (nombre) VALUES (?)', tipos_iniciales)

    cursor.execute('SELECT COUNT(*) FROM servicios')
    if cursor.fetchone()[0] == 0:
        # tipo_servicio_id: 1=Desarrollo Web, 2=Marketing Digital, 3=Diseño y Catálogos, 4=Soporte y Asesoría
        servicios_iniciales = [
            (1, 'Páginas Web para Negocios', 250.00,
             'https://images.unsplash.com/photo-1547658719-da2b51169166',
             'Diseño de sitios web claros, rápidos y adaptados para celulares y computadoras.', 1),
            (3, 'Catálogo Digital de Productos', 120.00,
             'https://images.unsplash.com/photo-1460925895917-afdab827c52f',
             'Muestra tus productos con fotos, precios y botón para hacer pedidos por WhatsApp.', 1),
            (3, 'Menú Digital con Código QR', 65.00,
             'https://images.unsplash.com/photo-1595079672139-5470887216e9',
             'Menú interactivo para restaurantes y cafeterías accesible escaneando un código QR.', 1),
            (1, 'Formularios de Contacto y Pedidos', 85.00,
             'https://images.unsplash.com/photo-1551288049-bebda4e38f71',
             'Formularios personalizados para recibir solicitudes, cotizaciones y reservas.', 1),
            (2, 'Botón de WhatsApp y Redes Sociales', 45.00,
             'https://images.unsplash.com/photo-1611746872915-64382b5c76da',
             'Integración de enlaces directos a WhatsApp, Instagram, Facebook y TikTok.', 1),
            (4, 'Asesoría y Optimización Web', 110.00,
             'https://images.unsplash.com/photo-1507238691740-187a5b1d37b8',
             'Revisión técnica de páginas web para mejorar su velocidad y accesibilidad.', 0)
        ]
        cursor.executemany(
            '''INSERT INTO servicios (tipo_servicio_id, nombre, precio_base, imagen, descripcion, disponible)
               VALUES (?, ?, ?, ?, ?, ?)''',
            servicios_iniciales
        )

    cursor.execute('SELECT COUNT(*) FROM estados_proveedor')
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            'INSERT INTO estados_proveedor (nombre) VALUES (?)',
            [('Activo',), ('Pendiente',), ('Inactivo',)]
        )

    cursor.execute('SELECT COUNT(*) FROM categorias_proveedor')
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            'INSERT INTO categorias_proveedor (nombre) VALUES (?)',
            [('Servidor y Hosting',), ('Registro de Dominios',), ('Diseño de Interfaces',), ('Certificados SSL y Seguridad',)]
        )

    cursor.execute('SELECT COUNT(*) FROM proveedores')
    if cursor.fetchone()[0] == 0:
        proveedores_iniciales = [
            ('Hostinger', 'Servidor y Hosting', 'hostinger.com', 'Activo'),
            ('GoDaddy', 'Registro de Dominios', 'godaddy.com', 'Activo'),
            ('Figma', 'Diseño de Interfaces', 'figma.com', 'Activo'),
            ('Cloudflare', 'Certificados SSL y Seguridad', 'cloudflare.com', 'Pendiente')
        ]
        for nombre, nombre_cat, sitio, nombre_estado in proveedores_iniciales:
            categoria_id = cursor.execute(
                'SELECT id FROM categorias_proveedor WHERE nombre = ?', (nombre_cat,)
            ).fetchone()['id']
            estado_id = cursor.execute(
                'SELECT id FROM estados_proveedor WHERE nombre = ?', (nombre_estado,)
            ).fetchone()['id']
            cursor.execute(
                'INSERT INTO proveedores (nombre, categoria_id, sitio, estado_id) VALUES (?, ?, ?, ?)',
                (nombre, categoria_id, sitio, estado_id)
            )

    cursor.execute('SELECT COUNT(*) FROM estados_documento')
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            'INSERT INTO estados_documento (nombre) VALUES (?)',
            [('Pagada',), ('Pendiente',), ('Aprobada',), ('En revision',), ('Vencida',)]
        )

    conn.commit()  # guarda los cambios
    conn.close()   # cierra la conexión
