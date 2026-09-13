-- ==============================================================================
-- PROYECTO: NEXODIGITAL - ESQUEMA DE LA BASE DE DATOS (PostgreSQL)
-- ==============================================================================
-- Este archivo permite volver a crear toda la estructura de la base de datos
-- 'nexodigital' desde cero, junto con sus datos iniciales.
--
-- Uso en pgAdmin:  crear la base 'nexodigital', abrir el Query Tool sobre ella,
--                  pegar este archivo y ejecutar (F5).
-- Uso en terminal: psql -U postgres -d nexodigital -f sql/esquema.sql
--
-- Todas las tablas tienen PRIMARY KEY y las relaciones se establecen con
-- FOREIGN KEY, garantizando la integridad referencial del modelo.
-- ==============================================================================
 
-- ============================
-- CREACIÓN DE TABLAS
-- ============================
 
CREATE TABLE tipos_negocio (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE
);
 
CREATE TABLE clientes (
    cedula VARCHAR(20) PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    correo VARCHAR(150) NOT NULL,
    tipo_negocio_id INT REFERENCES tipos_negocio(id),
    ciudad VARCHAR(100) NOT NULL
);
 
CREATE TABLE tipos_servicio (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE
);
 
CREATE TABLE servicios (
    id SERIAL PRIMARY KEY,
    tipo_servicio_id INT NOT NULL REFERENCES tipos_servicio(id),
    nombre VARCHAR(150) NOT NULL,
    precio_base NUMERIC(12,2) NOT NULL,
    imagen TEXT,
    descripcion TEXT NOT NULL,
    disponible BOOLEAN NOT NULL DEFAULT TRUE
);
 
CREATE TABLE estados_proveedor (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);
 
CREATE TABLE categorias_proveedor (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE
);
 
CREATE TABLE proveedores (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    categoria_id INT NOT NULL REFERENCES categorias_proveedor(id),
    sitio VARCHAR(150) NOT NULL,
    estado_id INT NOT NULL REFERENCES estados_proveedor(id)
);
 
CREATE TABLE estados_documento (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);
 
CREATE TABLE facturacion (
    numero VARCHAR(30) PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    cliente_cedula VARCHAR(20) NOT NULL REFERENCES clientes(cedula) ON UPDATE CASCADE,
    fecha DATE NOT NULL,
    validez VARCHAR(50),
    subtotal NUMERIC(12,2),
    iva NUMERIC(12,2),
    monto NUMERIC(12,2) NOT NULL,
    anticipo NUMERIC(12,2) DEFAULT 0,
    saldo_pendiente NUMERIC(12,2) DEFAULT 0,
    estado_id INT NOT NULL REFERENCES estados_documento(id),
    notas TEXT
);
 
CREATE TABLE detalle_factura (
    id SERIAL PRIMARY KEY,
    factura_numero VARCHAR(30) NOT NULL REFERENCES facturacion(numero) ON DELETE CASCADE ON UPDATE CASCADE,
    servicio_id INT REFERENCES servicios(id) ON DELETE SET NULL,
    nombre_servicio VARCHAR(150) NOT NULL,
    cantidad INT NOT NULL DEFAULT 1,
    precio_base NUMERIC(12,2) NOT NULL DEFAULT 0,
    ajuste NUMERIC(12,2) NOT NULL DEFAULT 0,
    total NUMERIC(12,2) NOT NULL
);
 
-- ============================
-- DATOS INICIALES
-- ============================
 
INSERT INTO tipos_negocio (nombre) VALUES
('Panadería'), ('Tienda de Ropa'), ('Taller Automotriz'), ('Cafetería');
 
INSERT INTO clientes (cedula, nombre, telefono, correo, tipo_negocio_id, ciudad) VALUES
('1700111222', 'Panadería El Trigal', '0991234567', 'trigal@correo.com', 1, 'Santo Domingo'),
('1700333444', 'Boutique Bella', '0987654321', 'bella@correo.com', 2, 'Quito'),
('1700555666', 'Taller Mecánico RPM', '0976543210', 'rpm@correo.com', 3, 'Santo Domingo'),
('1700777888', 'Café Aroma Amazónico', '0965432109', 'aroma@correo.com', 4, 'Puyo');
 
INSERT INTO tipos_servicio (nombre) VALUES
('Desarrollo Web'), ('Marketing Digital'), ('Diseño y Catálogos'), ('Soporte y Asesoría');
 
INSERT INTO servicios (tipo_servicio_id, nombre, precio_base, imagen, descripcion, disponible) VALUES
(1, 'Páginas Web para Negocios', 250.00, 'https://images.unsplash.com/photo-1547658719-da2b51169166', 'Diseño de sitios web claros, rápidos y adaptados para celulares y computadoras.', TRUE),
(3, 'Catálogo Digital de Productos', 120.00, 'https://images.unsplash.com/photo-1460925895917-afdab827c52f', 'Muestra tus productos con fotos, precios y botón para hacer pedidos por WhatsApp.', TRUE),
(3, 'Menú Digital con Código QR', 65.00, 'https://images.unsplash.com/photo-1595079672139-5470887216e9', 'Menú interactivo para restaurantes y cafeterías accesible escaneando un código QR.', TRUE),
(1, 'Formularios de Contacto y Pedidos', 85.00, 'https://images.unsplash.com/photo-1551288049-bebda4e38f71', 'Formularios personalizados para recibir solicitudes, cotizaciones y reservas.', TRUE),
(2, 'Botón de WhatsApp y Redes Sociales', 45.00, 'https://images.unsplash.com/photo-1611746872915-64382b5c76da', 'Integración de enlaces directos a WhatsApp, Instagram, Facebook y TikTok.', TRUE),
(4, 'Asesoría y Optimización Web', 110.00, 'https://images.unsplash.com/photo-1507238691740-187a5b1d37b8', 'Revisión técnica de páginas web para mejorar su velocidad y accesibilidad.', FALSE);
 
INSERT INTO estados_proveedor (nombre) VALUES
('Activo'), ('Pendiente'), ('Inactivo');
 
INSERT INTO categorias_proveedor (nombre) VALUES
('Servidor y Hosting'), ('Registro de Dominios'), ('Diseño de Interfaces'), ('Certificados SSL y Seguridad');
 
INSERT INTO proveedores (nombre, categoria_id, sitio, estado_id) VALUES
('Hostinger', 1, 'hostinger.com', 1),
('GoDaddy', 2, 'godaddy.com', 1),
('Figma', 3, 'figma.com', 1),
('Cloudflare', 4, 'cloudflare.com', 2);
 
INSERT INTO estados_documento (nombre) VALUES
('Pagada'), ('Pendiente'), ('Aprobada'), ('En revision'), ('Vencida');