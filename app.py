# ==============================================================================
# PROYECTO: NEXODIGITAL - SOLUCIONES WEB Y COMERCIALES
# Control Principal de la Aplicación Flask (Backend)
# ==============================================================================
# Este archivo contiene la configuración central del servidor, las estructuras
# de datos simuladas en memoria y los controladores (rutas y vistas) que gestionan
# la lógica de negocio para:
# 1. Página de inicio y presentación de la empresa
# 2. Catálogo y gestión de Servicios (CRUD)
# 3. Directorio de Proveedores e infraestructura (CRUD)
# 4. Directorio de Clientes y cartera comercial (CRUD)
# 5. Emisión de Facturas y Cotizaciones con cálculo en vivo de anticipos y saldos
# ==============================================================================

import json
from datetime import date
from flask import Flask, render_template, redirect, url_for, flash, request

# Importación de clases de formularios creadas con Flask-WTF
from forms.cliente_form import ClienteForm
from forms.servicio_form import ServicioForm
from forms.proveedor_form import ProveedorForm
from forms.facturacion_form import FacturacionForm

# ------------------------------------------------------------------------------
# INICIALIZACIÓN DE LA APLICACIÓN FLASK
# ------------------------------------------------------------------------------
app = Flask(__name__)

# Clave secreta para la protección de sesiones y seguridad contra ataques CSRF en formularios
app.config['SECRET_KEY'] = 'nexodigital_clave_secreta_2026'


# ------------------------------------------------------------------------------
# BASE DE DATOS EN MEMORIA (LISTAS DE DICCIONARIOS)
# ------------------------------------------------------------------------------
# En entornos educativos, almacenar los datos en listas en memoria permite aprender
# el ciclo de vida de peticiones HTTP, operaciones CRUD y plantillas Jinja2
# sin la complejidad inicial de configurar un motor SQL externo.
# ------------------------------------------------------------------------------

# 1. Lista de Servicios Web y Productos Digitales
lista_servicios = [
    {
        "nombre": "Páginas Web para Negocios",
        "descripcion": "Diseño de sitios web claros, rápidos y adaptados para celulares y computadoras.",
        "precio": 250.00,
        "tiempo_estimado": "5 a 7 días",
        "imagen": "https://images.unsplash.com/photo-1547658719-da2b51169166",
        "disponible": True
    },
    {
        "nombre": "Catálogo Digital de Productos",
        "descripcion": "Muestra tus productos con fotos, precios y botón para hacer pedidos por WhatsApp.",
        "precio": 120.00,
        "tiempo_estimado": "3 a 4 días",
        "imagen": "https://images.unsplash.com/photo-1460925895917-afdab827c52f",
        "disponible": True
    },
    {
        "nombre": "Menú Digital con Código QR",
        "descripcion": "Menú interactivo para restaurantes y cafeterías accesible escaneando un código QR.",
        "precio": 65.00,
        "tiempo_estimado": "24 a 48 horas",
        "imagen": "https://images.unsplash.com/photo-1595079672139-5470887216e9",
        "disponible": True
    },
    {
        "nombre": "Formularios de Contacto y Pedidos",
        "descripcion": "Formularios personalizados para recibir solicitudes, cotizaciones y reservas de clientes.",
        "precio": 85.00,
        "tiempo_estimado": "2 a 3 días",
        "imagen": "https://images.unsplash.com/photo-1551288049-bebda4e38f71",
        "disponible": True
    },
    {
        "nombre": "Botón de WhatsApp y Redes Sociales",
        "descripcion": "Integración de enlaces directos a WhatsApp, Instagram, Facebook y TikTok en tu web.",
        "precio": 45.00,
        "tiempo_estimado": "24 horas",
        "imagen": "https://images.unsplash.com/photo-1611746872915-64382b5c76da",
        "disponible": True
    },
    {
        "nombre": "Asesoría y Optimización Web",
        "descripcion": "Revisión técnica de páginas web para mejorar su velocidad de carga y accesibilidad.",
        "precio": 110.00,
        "tiempo_estimado": "3 a 5 días",
        "imagen": "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8",
        "disponible": False
    }
]

# 2. Lista de Proveedores de Infraestructura y Servicios Cloud
lista_proveedores = [
    {"nombre": "Hostinger", "servicio": "Servidor y Hosting", "sitio": "hostinger.com", "estado": "Activo"},
    {"nombre": "GoDaddy", "servicio": "Registro de Dominios", "sitio": "godaddy.com", "estado": "Activo"},
    {"nombre": "Figma", "servicio": "Diseño de Interfaces", "sitio": "figma.com", "estado": "Activo"},
    {"nombre": "Cloudflare", "servicio": "Certificados SSL y Seguridad", "sitio": "cloudflare.com", "estado": "Pendiente"}
]

# 3. Lista de Clientes Registrados
lista_clientes = [
    {"nombre": "Panadería El Trigal", "negocio": "Panadería", "servicio": "Página Web + Menú QR", "ciudad": "Santo Domingo"},
    {"nombre": "Boutique Bella", "negocio": "Tienda de Ropa", "servicio": "Catálogo Digital", "ciudad": "Quito"},
    {"nombre": "Taller Mecánico RPM", "negocio": "Taller Automotriz", "servicio": "Formulario de Citas", "ciudad": "Santo Domingo"},
    {"nombre": "Café Aroma Amazónico", "negocio": "Cafetería", "servicio": "Menú QR + WhatsApp", "ciudad": "Puyo"}
]

# 4. Lista de Documentos Comerciales (Facturas y Cotizaciones)
lista_facturas = [
    {
        "tipo": "Factura",
        "numero": "001-001-0001",
        "cliente": "Panadería El Trigal",
        "fecha": "2026-01-15",
        "validez": "30 días",
        "servicios_detalle": [
            {"servicio": "Páginas Web para Negocios", "precio": 250.00, "cantidad": 1, "ajuste": 0.00, "total": 250.00},
            {"servicio": "Menú Digital con Código QR", "precio": 65.00, "cantidad": 1, "ajuste": 0.00, "total": 65.00}
        ],
        "subtotal": 315.00,
        "iva": 47.25,
        "monto": 362.25,
        "anticipo": 362.25,
        "saldo_pendiente": 0.00,
        "estado": "Pagada",
        "notas": "Trabajo entregado con dominio y hosting activo por 1 año."
    },
    {
        "tipo": "Cotizacion",
        "numero": "COT-2026-0042",
        "cliente": "Boutique Bella",
        "fecha": "2026-02-18",
        "validez": "15 días",
        "servicios_detalle": [
            {"servicio": "Catálogo Digital de Productos", "precio": 120.00, "cantidad": 1, "ajuste": 0.00, "total": 120.00},
            {"servicio": "Botón de WhatsApp y Redes Sociales", "precio": 45.00, "cantidad": 1, "ajuste": 0.00, "total": 45.00}
        ],
        "subtotal": 165.00,
        "iva": 24.75,
        "monto": 189.75,
        "anticipo": 100.00,
        "saldo_pendiente": 89.75,
        "estado": "Aprobada",
        "notas": "Anticipo de  recibido. El saldo de .75 se cancela al entregar el catálogo."
    },
    {
        "tipo": "Cotizacion",
        "numero": "COT-2026-0043",
        "cliente": "Taller Mecánico RPM",
        "fecha": "2026-02-20",
        "validez": "15 días",
        "servicios_detalle": [
            {"servicio": "Formularios de Contacto y Pedidos", "precio": 85.00, "cantidad": 1, "ajuste": 15.00, "total": 100.00}
        ],
        "subtotal": 100.00,
        "iva": 15.00,
        "monto": 115.00,
        "anticipo": 0.00,
        "saldo_pendiente": 115.00,
        "estado": "En revision",
        "notas": "Se incluye recargo de  por búsqueda de repuestos mediante número de placa."
    },
    {
        "tipo": "Factura",
        "numero": "001-001-0002",
        "cliente": "Café Aroma Amazónico",
        "fecha": "2026-03-10",
        "validez": "15 días",
        "servicios_detalle": [
            {"servicio": "Menú Digital con Código QR", "precio": 65.00, "cantidad": 2, "ajuste": 0.00, "total": 130.00},
            {"servicio": "Botón de WhatsApp y Redes Sociales", "precio": 45.00, "cantidad": 1, "ajuste": 0.00, "total": 45.00}
        ],
        "subtotal": 175.00,
        "iva": 26.25,
        "monto": 201.25,
        "anticipo": 100.00,
        "saldo_pendiente": 101.25,
        "estado": "Pendiente",
        "notas": "Factura pendiente con saldo de .25."
    }
]


# ==============================================================================
# RUTAS PÚBLICAS Y VISTAS GENERALES
# ==============================================================================

@app.route('/')
def inicio():
    """
    Ruta raíz del sitio web.
    Renderiza la vista principal con información de la empresa, catálogo destacado,
    video institucional, formulario de contacto y módulo JS de solicitudes.
    """
    mensaje = "Soluciones digitales para hacer crecer tu negocio"
    empresa = {
        "nombre": "Nexo Digital",
        "ubicacion": "Quito / Puyo - Ecuador",
        "modalidad": "Atención 100% en línea"
    }
    return render_template('index.html', mensaje=mensaje, empresa=empresa, servicios=lista_servicios)


@app.route('/servicios')
@app.route('/servicio')
def servicios():
    """
    Ruta del catálogo completo de servicios.
    Renderiza la tarjeta de cada servicio disponible o próximo a lanzarse.
    """
    return render_template('servicios.html', servicios=lista_servicios)


@app.route('/proveedores')
def proveedores():
    """
    Ruta del directorio de proveedores tecnológicos.
    Lista herramientas de hosting, dominios y diseño utilizadas por la empresa.
    """
    return render_template('proveedores.html', proveedores=lista_proveedores)


@app.route('/clientes')
def clientes():
    """
    Ruta del directorio de clientes comerciales.
    Muestra la tabla de negocios asociados y sus soluciones contratadas.
    """
    return render_template('clientes.html', clientes=lista_clientes)


@app.route('/facturacion')
def facturacion():
    """
    Ruta principal del panel comercial de Facturación y Cotizaciones.
    Lista todos los documentos con desglose de totales, anticipos y saldos pendientes.
    """
    return render_template('facturacion.html', facturas=lista_facturas)


# ==============================================================================
# MÓDULO CRUD: CLIENTES
# ==============================================================================

@app.route('/clientes/nuevo', methods=['GET', 'POST'])
def nuevo_cliente():
    """
    Crea y registra un nuevo cliente en el sistema.
    - GET: Renderiza el formulario vacío.
    - POST: Valida los campos ingresados y añade el cliente a la lista.
    """
    form = ClienteForm()
    if form.validate_on_submit():
        lista_clientes.append({
            "nombre": form.nombre.data.strip(),
            "negocio": form.negocio.data.strip(),
            "servicio": form.servicio.data.strip(),
            "ciudad": form.ciudad.data.strip()
        })
        flash('Cliente registrado correctamente.', 'success')
        return redirect(url_for('clientes'))
    return render_template('formulario_cliente.html', form=form, editando=False)


@app.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    """
    Edita la información de un cliente existente por su índice (ID).
    - GET: Carga la información actual en el formulario.
    - POST: Actualiza los campos tras pasar la validación.
    """
    if id < 0 or id >= len(lista_clientes):
        flash('El cliente seleccionado no existe.', 'danger')
        return redirect(url_for('clientes'))
    
    cliente = lista_clientes[id]
    form = ClienteForm(data=cliente) if request.method == 'GET' else ClienteForm()
    
    if form.validate_on_submit():
        lista_clientes[id] = {
            "nombre": form.nombre.data.strip(),
            "negocio": form.negocio.data.strip(),
            "servicio": form.servicio.data.strip(),
            "ciudad": form.ciudad.data.strip()
        }
        flash(f'Cliente "{form.nombre.data.strip()}" actualizado correctamente.', 'success')
        return redirect(url_for('clientes'))
    
    return render_template('formulario_cliente.html', form=form, editando=True, id=id)


@app.route('/clientes/eliminar/<int:id>', methods=['POST', 'GET'])
def eliminar_cliente(id):
    """
    Elimina un cliente de la lista en memoria según su índice.
    """
    if 0 <= id < len(lista_clientes):
        nombre = lista_clientes[id]['nombre']
        lista_clientes.pop(id)
        flash(f'Cliente "{nombre}" eliminado correctamente.', 'success')
    else:
        flash('El cliente seleccionado no existe.', 'danger')
    return redirect(url_for('clientes'))


# ==============================================================================
# MÓDULO CRUD: SERVICIOS
# ==============================================================================

@app.route('/servicios/nuevo', methods=['GET', 'POST'])
@app.route('/servicio/nuevo', methods=['GET', 'POST'])
def nuevo_servicio():
    """
    Registra un nuevo servicio en el catálogo.
    Asigna una imagen y tiempo estimado por defecto si no son proporcionados.
    """
    form = ServicioForm()
    if form.validate_on_submit():
        imagen_url = form.imagen.data.strip() if form.imagen.data and form.imagen.data.strip() else "https://images.unsplash.com/photo-1460925895917-afdab827c52f"
        tiempo = form.tiempo_estimado.data.strip() if form.tiempo_estimado.data and form.tiempo_estimado.data.strip() else "2 a 5 días"

        lista_servicios.append({
            "nombre": form.nombre.data.strip(),
            "descripcion": form.descripcion.data.strip(),
            "precio": float(form.precio.data),
            "tiempo_estimado": tiempo,
            "imagen": imagen_url,
            "disponible": form.disponible.data
        })
        flash('Servicio registrado correctamente.', 'success')
        return redirect(url_for('servicios'))
    return render_template('formulario_servicio.html', form=form, editando=False)


@app.route('/servicios/editar/<int:id>', methods=['GET', 'POST'])
@app.route('/servicio/editar/<int:id>', methods=['GET', 'POST'])
def editar_servicio(id):
    """
    Edita un servicio existente identificado por su índice.
    """
    if id < 0 or id >= len(lista_servicios):
        flash('El servicio seleccionado no existe.', 'danger')
        return redirect(url_for('servicios'))
    
    servicio = lista_servicios[id]
    form = ServicioForm(data=servicio) if request.method == 'GET' else ServicioForm()
    
    if form.validate_on_submit():
        imagen_url = form.imagen.data.strip() if form.imagen.data and form.imagen.data.strip() else servicio.get("imagen", "https://images.unsplash.com/photo-1460925895917-afdab827c52f")
        tiempo = form.tiempo_estimado.data.strip() if form.tiempo_estimado.data and form.tiempo_estimado.data.strip() else "2 a 5 días"

        lista_servicios[id] = {
            "nombre": form.nombre.data.strip(),
            "descripcion": form.descripcion.data.strip(),
            "precio": float(form.precio.data),
            "tiempo_estimado": tiempo,
            "imagen": imagen_url,
            "disponible": form.disponible.data
        }
        flash(f'Servicio "{form.nombre.data.strip()}" actualizado correctamente.', 'success')
        return redirect(url_for('servicios'))
    
    return render_template('formulario_servicio.html', form=form, editando=True, id=id)


@app.route('/servicios/eliminar/<int:id>', methods=['POST', 'GET'])
@app.route('/servicio/eliminar/<int:id>', methods=['POST', 'GET'])
def eliminar_servicio(id):
    """
    Elimina un servicio del catálogo en memoria.
    """
    if 0 <= id < len(lista_servicios):
        nombre = lista_servicios[id]['nombre']
        lista_servicios.pop(id)
        flash(f'Servicio "{nombre}" eliminado correctamente.', 'success')
    else:
        flash('El servicio seleccionado no existe.', 'danger')
    return redirect(url_for('servicios'))


# ==============================================================================
# MÓDULO CRUD: PROVEEDORES
# ==============================================================================

@app.route('/proveedores/nuevo', methods=['GET', 'POST'])
def nuevo_proveedor():
    """
    Registra un nuevo proveedor de servicios o infraestructura.
    """
    form = ProveedorForm()
    if form.validate_on_submit():
        lista_proveedores.append({
            "nombre": form.nombre.data.strip(),
            "servicio": form.servicio.data.strip(),
            "sitio": form.sitio.data.strip(),
            "estado": form.estado.data
        })
        flash('Proveedor registrado correctamente.', 'success')
        return redirect(url_for('proveedores'))
    return render_template('formulario_proveedor.html', form=form, editando=False)


@app.route('/proveedores/editar/<int:id>', methods=['GET', 'POST'])
def editar_proveedor(id):
    """
    Modifica los datos de un proveedor existente.
    """
    if id < 0 or id >= len(lista_proveedores):
        flash('El proveedor seleccionado no existe.', 'danger')
        return redirect(url_for('proveedores'))
    
    proveedor = lista_proveedores[id]
    form = ProveedorForm(data=proveedor) if request.method == 'GET' else ProveedorForm()
    
    if form.validate_on_submit():
        lista_proveedores[id] = {
            "nombre": form.nombre.data.strip(),
            "servicio": form.servicio.data.strip(),
            "sitio": form.sitio.data.strip(),
            "estado": form.estado.data
        }
        flash(f'Proveedor "{form.nombre.data.strip()}" actualizado correctamente.', 'success')
        return redirect(url_for('proveedores'))
    
    return render_template('formulario_proveedor.html', form=form, editando=True, id=id)


@app.route('/proveedores/eliminar/<int:id>', methods=['POST', 'GET'])
def eliminar_proveedor(id):
    """
    Elimina un proveedor de la lista en memoria.
    """
    if 0 <= id < len(lista_proveedores):
        nombre = lista_proveedores[id]['nombre']
        lista_proveedores.pop(id)
        flash(f'Proveedor "{nombre}" eliminado correctamente.', 'success')
    else:
        flash('El proveedor seleccionado no existe.', 'danger')
    return redirect(url_for('proveedores'))


# ==============================================================================
# MÓDULO CRUD: FACTURACIÓN Y COTIZACIONES INTELIGENTES
# ==============================================================================

@app.route('/facturacion/nueva', methods=['GET', 'POST'])
def nueva_factura():
    """
    Emite un nuevo documento comercial (Factura o Cotización).
    - Permite cargar automáticamente ítems desde el catálogo de servicios.
    - Calcula en tiempo real: Subtotal, IVA (15%), Total, Anticipo y Saldo Pendiente.
    - Serializa la lista de servicios en un campo oculto JSON (servicios_json).
    """
    form = FacturacionForm()
    tipo_solicitado = request.args.get('tipo', 'Cotizacion' if request.args.get('servicio_id') is not None else 'Factura')
    
    # Inicialización de valores predeterminados para la petición GET
    if request.method == 'GET':
        form.tipo.data = tipo_solicitado
        if tipo_solicitado == 'Cotizacion':
            form.numero.data = f"COT-2026-{len(lista_facturas) + 1:04d}"
            form.validez.data = "15 días"
            form.estado.data = "En revision"
        else:
            form.numero.data = f"001-001-{len(lista_facturas) + 1:04d}"
            form.validez.data = "30 días"
            form.estado.data = "Pendiente"
        form.fecha.data = str(date.today())
        form.anticipo.data = 0.00
        form.saldo_pendiente.data = 0.00

    # Procesamiento y validación del formulario al enviar con POST
    if form.validate_on_submit():
        servicios_detalle = []
        if form.servicios_json.data:
            try:
                servicios_detalle = json.loads(form.servicios_json.data)
            except Exception:
                servicios_detalle = []

        # Cálculos de valores monetarios con protección contra nulos
        subtotal_val = float(form.subtotal.data) if form.subtotal.data is not None else float(form.monto.data)
        iva_val = float(form.iva.data) if form.iva.data is not None else round(subtotal_val * 0.15, 2)
        total_val = float(form.monto.data)
        anticipo_val = float(form.anticipo.data) if form.anticipo.data is not None else 0.00
        saldo_val = float(form.saldo_pendiente.data) if form.saldo_pendiente.data is not None else max(0.0, total_val - anticipo_val)
        
        tipo_doc = form.tipo.data
        estado_final = form.estado.data

        # Si una factura se emite con saldo 0, se clasifica automáticamente como 'Pagada'
        if tipo_doc == 'Factura' and saldo_val <= 0 and estado_final == 'Pendiente':
            estado_final = 'Pagada'

        lista_facturas.append({
            "tipo": tipo_doc,
            "numero": form.numero.data.strip(),
            "cliente": form.cliente.data.strip(),
            "fecha": str(form.fecha.data),
            "validez": form.validez.data.strip() if form.validez.data else "15 días",
            "servicios_detalle": servicios_detalle,
            "subtotal": subtotal_val,
            "iva": iva_val,
            "monto": total_val,
            "anticipo": anticipo_val,
            "saldo_pendiente": saldo_val,
            "estado": estado_final,
            "notas": form.notas.data.strip() if form.notas.data else ("Propuesta emitida por NexoDigital." if tipo_doc == 'Cotizacion' else "Comprobante emitido por NexoDigital.")
        })
        
        nombre_doc = "Cotización" if tipo_doc == 'Cotizacion' else "Factura"
        flash(f'{nombre_doc} "{form.numero.data}" guardada correctamente.', 'success')
        return redirect(url_for('facturacion'))
        
    return render_template(
        'formulario_facturacion.html',
        form=form,
        editando=False,
        servicios_catalogo=lista_servicios,
        clientes_registrados=lista_clientes,
        servicio_seleccionado_id=request.args.get('servicio_id', type=int)
    )


@app.route('/facturacion/editar/<int:id>', methods=['GET', 'POST'])
def editar_factura(id):
    """
    Edita un documento comercial (Factura o Cotización) existente.
    """
    if id < 0 or id >= len(lista_facturas):
        flash('El documento seleccionado no existe.', 'danger')
        return redirect(url_for('facturacion'))
    
    factura = lista_facturas[id]
    form = FacturacionForm(data=factura) if request.method == 'GET' else FacturacionForm()

    if request.method == 'GET' and 'servicios_detalle' in factura:
        form.servicios_json.data = json.dumps(factura['servicios_detalle'])

    if form.validate_on_submit():
        servicios_detalle = []
        if form.servicios_json.data:
            try:
                servicios_detalle = json.loads(form.servicios_json.data)
            except Exception:
                servicios_detalle = factura.get('servicios_detalle', [])

        subtotal_val = float(form.subtotal.data) if form.subtotal.data is not None else float(form.monto.data)
        iva_val = float(form.iva.data) if form.iva.data is not None else round(subtotal_val * 0.15, 2)
        total_val = float(form.monto.data)
        anticipo_val = float(form.anticipo.data) if form.anticipo.data is not None else 0.00
        saldo_val = float(form.saldo_pendiente.data) if form.saldo_pendiente.data is not None else max(0.0, total_val - anticipo_val)
        tipo_doc = form.tipo.data

        lista_facturas[id] = {
            "tipo": tipo_doc,
            "numero": form.numero.data.strip(),
            "cliente": form.cliente.data.strip(),
            "fecha": str(form.fecha.data),
            "validez": form.validez.data.strip() if form.validez.data else "15 días",
            "servicios_detalle": servicios_detalle,
            "subtotal": subtotal_val,
            "iva": iva_val,
            "monto": total_val,
            "anticipo": anticipo_val,
            "saldo_pendiente": saldo_val,
            "estado": form.estado.data,
            "notas": form.notas.data.strip() if form.notas.data else "Documento generado por NexoDigital."
        }
        nombre_doc = "Cotización" if tipo_doc == 'Cotizacion' else "Factura"
        flash(f'{nombre_doc} "{form.numero.data}" actualizada correctamente.', 'success')
        return redirect(url_for('facturacion'))
    
    return render_template(
        'formulario_facturacion.html',
        form=form,
        editando=True,
        id=id,
        servicios_catalogo=lista_servicios,
        clientes_registrados=lista_clientes,
        detalle_existente=factura.get('servicios_detalle', [])
    )


@app.route('/facturacion/eliminar/<int:id>', methods=['POST', 'GET'])
def eliminar_factura(id):
    """
    Elimina un documento comercial de la lista.
    """
    if 0 <= id < len(lista_facturas):
        doc = lista_facturas[id]
        tipo_str = "Cotización" if doc.get('tipo') == 'Cotizacion' else "Factura"
        numero = doc['numero']
        lista_facturas.pop(id)
        flash(f'{tipo_str} "{numero}" eliminada correctamente.', 'success')
    else:
        flash('El documento seleccionado no existe.', 'danger')
    return redirect(url_for('facturacion'))


@app.route('/facturacion/comprobante/<int:id>')
def ver_comprobante(id):
    """
    Genera la vista limpia e imprimible del comprobante o cotización.
    Optimizado con estilos CSS para impresión (@media print) o guardado en PDF.
    """
    if id < 0 or id >= len(lista_facturas):
        flash('El documento seleccionado no existe.', 'danger')
        return redirect(url_for('facturacion'))
    
    factura = lista_facturas[id]
    return render_template('comprobante_factura.html', factura=factura, id=id)


# ==============================================================================
# PUNTO DE ENTRADA PRINCIPAL DE LA APLICACIÓN
# ==============================================================================
if __name__ == '__main__':
    # Ejecuta el servidor de desarrollo local con recarga automática y depurador activo
    app.run(debug=True)
