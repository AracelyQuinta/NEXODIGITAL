from flask import Flask, render_template

app = Flask(__name__)


# Ruta principal
@app.route('/')
def inicio():

    # Variable simple
    mensaje = "Soluciones digitales para hacer crecer tu negocio"

    # Diccionario con información de Nexo Digital
    empresa = {
        "nombre": "Nexo Digital",
        "ubicacion": "Quito - Ecuador",
        "modalidad": "Atención 100% en línea"
    }

    return render_template(
        'index.html',
        mensaje=mensaje,
        empresa=empresa
    )


# Módulo de Servicios
@app.route('/servicios')
def servicios():

    lista_servicios = [
        {
            "nombre": "Diseño web",
            "descripcion": "Creamos sitios web modernos, atractivos y adaptables a diferentes dispositivos.",
            "disponible": True
        },
        {
            "nombre": "Catálogos digitales",
            "descripcion": "Diseñamos catálogos digitales para presentar productos y servicios de forma profesional.",
            "disponible": True
        },
        {
            "nombre": "Formularios digitales",
            "descripcion": "Creamos formularios para contacto, pedidos, reservas y solicitudes.",
            "disponible": True
        },
        {
            "nombre": "Códigos QR",
            "descripcion": "Generamos códigos QR para facilitar el acceso a información y servicios.",
            "disponible": True
        },
        {
            "nombre": "Integración con WhatsApp",
            "descripcion": "Integramos WhatsApp para facilitar la comunicación directa con los clientes.",
            "disponible": True
        },
        {
            "nombre": "Accesibilidad web",
            "descripcion": "Aplicamos herramientas que ayudan a mejorar la accesibilidad de los sitios web.",
            "disponible": False
        }
    ]

    return render_template(
        'servicios.html',
        servicios=lista_servicios
    )


# Módulo de Proveedores
@app.route('/proveedores')
def proveedores():

    lista_proveedores = [
        {
            "nombre": "Hostinger",
            "servicio": "Hosting web",
            "sitio": "hostinger.com",
            "estado": "Activo"
        },
        {
            "nombre": "GoDaddy",
            "servicio": "Dominios",
            "sitio": "godaddy.com",
            "estado": "Activo"
        },
        {
            "nombre": "Figma",
            "servicio": "Licencia de diseño",
            "sitio": "figma.com",
            "estado": "Activo"
        },
        {
            "nombre": "Cloudflare",
            "servicio": "Seguridad y CDN",
            "sitio": "cloudflare.com",
            "estado": "Pendiente"
        }
    ]

    return render_template(
        'proveedores.html',
        proveedores=lista_proveedores
    )


# Módulo de Clientes
@app.route('/clientes')
def clientes():

    lista_clientes = [
        {
            "nombre": "Panadería El Trigal",
            "negocio": "Panadería",
            "servicio": "Página web + Menú QR",
            "ciudad": "Santo Domingo"
        },
        {
            "nombre": "Boutique Bella",
            "negocio": "Tienda de ropa",
            "servicio": "Catálogo digital",
            "ciudad": "Quito"
        },
        {
            "nombre": "Taller Mecánico RPM",
            "negocio": "Servicios automotrices",
            "servicio": "Formulario de citas",
            "ciudad": "Santo Domingo"
        },
        {
            "nombre": "Café Aroma",
            "negocio": "Cafetería",
            "servicio": "Menú QR + Redes",
            "ciudad": "Ambato"
        }
    ]

    return render_template(
        'clientes.html',
        clientes=lista_clientes
    )


# Módulo de Facturación
@app.route('/facturacion')
def facturacion():

    lista_facturas = [
        {
            "numero": "001-001-0001",
            "cliente": "Panadería El Trigal",
            "fecha": "2026-01-15",
            "monto": 350.00,
            "estado": "Pagada"
        },
        {
            "numero": "001-001-0002",
            "cliente": "Boutique Bella",
            "fecha": "2026-02-03",
            "monto": 220.00,
            "estado": "Pagada"
        },
        {
            "numero": "001-001-0003",
            "cliente": "Taller Mecánico RPM",
            "fecha": "2026-02-20",
            "monto": 180.00,
            "estado": "Pendiente"
        },
        {
            "numero": "001-001-0004",
            "cliente": "Café Aroma",
            "fecha": "2026-03-10",
            "monto": 400.00,
            "estado": "Vencida"
        }
    ]

    return render_template(
        'facturacion.html',
        facturas=lista_facturas
    )


# Punto de entrada
if __name__ == '__main__':
    app.run(debug=True)