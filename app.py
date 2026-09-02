# ==============================================================================
# PROYECTO: NEXODIGITAL - SOLUCIONES WEB Y COMERCIALES
# Control Principal de la Aplicación Flask (Backend)
# ==============================================================================
# Este archivo contiene la configuración central del servidor y los controladores
# (rutas y vistas) que gestionan la lógica de negocio para:
# 1. Página de inicio y presentación de la empresa
# 2. Catálogo y gestión de Servicios (CRUD) - persistencia en SQLite
# 3. Directorio de Proveedores e infraestructura (CRUD) - persistencia en SQLite
# 4. Directorio de Clientes y cartera comercial (CRUD) - persistencia en SQLite
# 5. Emisión de Facturas y Cotizaciones (CRUD) - persistencia en SQLite
# ==============================================================================

import json
from datetime import date
from flask import Flask, render_template, redirect, url_for, flash, request

# Importación de clases de formularios creadas con Flask-WTF
from forms.cliente_form import ClienteForm
from forms.servicio_form import ServicioForm
from forms.proveedor_form import ProveedorForm
from forms.facturacion_form import FacturacionForm

# Módulo propio de conexión y creación de tablas SQLite
import db

# ------------------------------------------------------------------------------
# INICIALIZACIÓN DE LA APLICACIÓN FLASK
# ------------------------------------------------------------------------------
app = Flask(__name__)

# Clave secreta para la protección de sesiones y seguridad contra ataques CSRF en formularios
app.config['SECRET_KEY'] = 'nexodigital_clave_secreta_2026'

# Crea las tablas en SQLite si todavía no existen (clientes, servicios, proveedores, facturacion)
db.init_db()


# ==============================================================================
# RUTAS PÚBLICAS Y VISTAS GENERALES
# ==============================================================================

@app.route('/')
def inicio():
    """
    Ruta raíz del sitio web.
    Renderiza la vista principal con información de la empresa y catálogo destacado.
    """
    mensaje = "Soluciones digitales para hacer crecer tu negocio"
    empresa = {
        "nombre": "Nexo Digital",
        "ubicacion": "Quito / Puyo - Ecuador",
        "modalidad": "Atención 100% en línea"
    }
    conn = db.get_connection()
    servicios_destacados = conn.execute('SELECT * FROM servicios').fetchall()
    conn.close()
    return render_template('index.html', mensaje=mensaje, empresa=empresa, servicios=servicios_destacados)


@app.route('/servicio')
def servicios():
    """
    Ruta del catálogo completo de servicios, leyendo desde SQLite.
    """
    conn = db.get_connection()
    lista_servicios = conn.execute('SELECT * FROM servicios').fetchall()
    conn.close()
    return render_template('servicios.html', servicios=lista_servicios)


@app.route('/proveedores')
def proveedores():
    """
    Ruta del directorio de proveedores tecnológicos, leyendo desde SQLite.
    """
    conn = db.get_connection()
    lista_proveedores = conn.execute('SELECT * FROM proveedores').fetchall()
    conn.close()
    return render_template('proveedores.html', proveedores=lista_proveedores)


@app.route('/clientes')
def clientes():
    """
    Ruta del directorio de clientes comerciales, leyendo desde SQLite.
    """
    conn = db.get_connection()
    lista_clientes = conn.execute('SELECT * FROM clientes').fetchall()
    conn.close()
    return render_template('clientes.html', clientes=lista_clientes)


@app.route('/facturacion')
def facturacion():
    """
    Ruta principal del panel comercial de Facturación y Cotizaciones.
    Lee los documentos desde SQLite y convierte servicios_json a lista.
    """
    conn = db.get_connection()
    filas = conn.execute('SELECT * FROM facturacion').fetchall()
    conn.close()

    lista_facturas = []
    for f in filas:
        doc = dict(f)
        doc['servicios_detalle'] = json.loads(doc['servicios_json']) if doc['servicios_json'] else []
        lista_facturas.append(doc)

    return render_template('facturacion.html', facturas=lista_facturas)


# ==============================================================================
# MÓDULO CRUD: CLIENTES
# ==============================================================================

@app.route('/clientes/nuevo', methods=['GET', 'POST'])
def nuevo_cliente():
    """
    Crea y registra un nuevo cliente en el sistema.
    - GET: Renderiza el formulario vacío.
    - POST: Valida los campos ingresados y guarda el cliente en SQLite.
    """
    form = ClienteForm()
    if form.validate_on_submit():
        conn = db.get_connection()
        conn.execute(
            'INSERT INTO clientes (nombre, negocio, servicio, ciudad) VALUES (?, ?, ?, ?)',
            (form.nombre.data.strip(), form.negocio.data.strip(),
             form.servicio.data.strip(), form.ciudad.data.strip())
        )
        conn.commit()
        conn.close()
        flash('Cliente registrado correctamente.', 'success')
        return redirect(url_for('clientes'))
    return render_template('formulario_cliente.html', form=form, editando=False)


@app.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    """
    Edita la información de un cliente existente identificado por su id de SQLite.
    - GET: Carga la información actual en el formulario.
    - POST: Actualiza los campos tras pasar la validación.
    """
    conn = db.get_connection()
    cliente = conn.execute('SELECT * FROM clientes WHERE id = ?', (id,)).fetchone()

    if cliente is None:
        conn.close()
        flash('El cliente seleccionado no existe.', 'danger')
        return redirect(url_for('clientes'))

    form = ClienteForm(data=dict(cliente)) if request.method == 'GET' else ClienteForm()

    if form.validate_on_submit():
        conn.execute(
            'UPDATE clientes SET nombre=?, negocio=?, servicio=?, ciudad=? WHERE id=?',
            (form.nombre.data.strip(), form.negocio.data.strip(),
             form.servicio.data.strip(), form.ciudad.data.strip(), id)
        )
        conn.commit()
        conn.close()
        flash(f'Cliente "{form.nombre.data.strip()}" actualizado correctamente.', 'success')
        return redirect(url_for('clientes'))

    conn.close()
    return render_template('formulario_cliente.html', form=form, editando=True, id=id)


@app.route('/clientes/eliminar/<int:id>', methods=['POST', 'GET'])
def eliminar_cliente(id):
    """
    Elimina un cliente de SQLite según su id.
    """
    conn = db.get_connection()
    cliente = conn.execute('SELECT * FROM clientes WHERE id = ?', (id,)).fetchone()

    if cliente is None:
        conn.close()
        flash('El cliente seleccionado no existe.', 'danger')
        return redirect(url_for('clientes'))

    conn.execute('DELETE FROM clientes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash(f'Cliente "{cliente["nombre"]}" eliminado correctamente.', 'success')
    return redirect(url_for('clientes'))


# ==============================================================================
# MÓDULO CRUD: SERVICIOS
# ==============================================================================

@app.route('/servicio/nuevo', methods=['GET', 'POST'])
def nuevo_servicio():
    """
    Registra un nuevo servicio en el catálogo, guardándolo en SQLite.
    Asigna una imagen y tiempo estimado por defecto si no son proporcionados.
    """
    form = ServicioForm()
    if form.validate_on_submit():
        imagen_url = form.imagen.data.strip() if form.imagen.data and form.imagen.data.strip() else "https://images.unsplash.com/photo-1460925895917-afdab827c52f"
        tiempo = form.tiempo_estimado.data.strip() if form.tiempo_estimado.data and form.tiempo_estimado.data.strip() else "2 a 5 días"

        conn = db.get_connection()
        conn.execute(
            '''INSERT INTO servicios (nombre, precio, tiempo_estimado, imagen, descripcion, disponible)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (form.nombre.data.strip(), float(form.precio.data), tiempo,
             imagen_url, form.descripcion.data.strip(), int(form.disponible.data))
        )
        conn.commit()
        conn.close()
        flash('Servicio registrado correctamente.', 'success')
        return redirect(url_for('servicios'))
    return render_template('formulario_servicio.html', form=form, editando=False)


@app.route('/servicios/editar/<int:id>', methods=['GET', 'POST'])
@app.route('/servicio/editar/<int:id>', methods=['GET', 'POST'])
def editar_servicio(id):
    """
    Edita un servicio existente identificado por su id real de SQLite.
    """
    conn = db.get_connection()
    servicio = conn.execute('SELECT * FROM servicios WHERE id = ?', (id,)).fetchone()

    if servicio is None:
        conn.close()
        flash('El servicio seleccionado no existe.', 'danger')
        return redirect(url_for('servicios'))

    form = ServicioForm(data=dict(servicio)) if request.method == 'GET' else ServicioForm()

    if form.validate_on_submit():
        imagen_url = form.imagen.data.strip() if form.imagen.data and form.imagen.data.strip() else servicio['imagen']
        tiempo = form.tiempo_estimado.data.strip() if form.tiempo_estimado.data and form.tiempo_estimado.data.strip() else "2 a 5 días"

        conn.execute(
            '''UPDATE servicios SET nombre=?, precio=?, tiempo_estimado=?, imagen=?, descripcion=?, disponible=?
               WHERE id=?''',
            (form.nombre.data.strip(), float(form.precio.data), tiempo,
             imagen_url, form.descripcion.data.strip(), int(form.disponible.data), id)
        )
        conn.commit()
        conn.close()
        flash(f'Servicio "{form.nombre.data.strip()}" actualizado correctamente.', 'success')
        return redirect(url_for('servicios'))

    conn.close()
    return render_template('formulario_servicio.html', form=form, editando=True, id=id)


@app.route('/servicios/eliminar/<int:id>', methods=['POST', 'GET'])
@app.route('/servicio/eliminar/<int:id>', methods=['POST', 'GET'])
def eliminar_servicio(id):
    """
    Elimina un servicio del catálogo en SQLite.
    """
    conn = db.get_connection()
    servicio = conn.execute('SELECT * FROM servicios WHERE id = ?', (id,)).fetchone()

    if servicio is None:
        conn.close()
        flash('El servicio seleccionado no existe.', 'danger')
        return redirect(url_for('servicios'))

    conn.execute('DELETE FROM servicios WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash(f'Servicio "{servicio["nombre"]}" eliminado correctamente.', 'success')
    return redirect(url_for('servicios'))


# ==============================================================================
# MÓDULO CRUD: PROVEEDORES
# ==============================================================================

@app.route('/proveedores/nuevo', methods=['GET', 'POST'])
def nuevo_proveedor():
    """
    Registra un nuevo proveedor de servicios o infraestructura en SQLite.
    """
    form = ProveedorForm()
    if form.validate_on_submit():
        conn = db.get_connection()
        conn.execute(
            'INSERT INTO proveedores (nombre, servicio, sitio, estado) VALUES (?, ?, ?, ?)',
            (form.nombre.data.strip(), form.servicio.data.strip(),
             form.sitio.data.strip(), form.estado.data)
        )
        conn.commit()
        conn.close()
        flash('Proveedor registrado correctamente.', 'success')
        return redirect(url_for('proveedores'))
    return render_template('formulario_proveedor.html', form=form, editando=False)


@app.route('/proveedores/editar/<int:id>', methods=['GET', 'POST'])
def editar_proveedor(id):
    """
    Modifica los datos de un proveedor existente en SQLite.
    """
    conn = db.get_connection()
    proveedor = conn.execute('SELECT * FROM proveedores WHERE id = ?', (id,)).fetchone()

    if proveedor is None:
        conn.close()
        flash('El proveedor seleccionado no existe.', 'danger')
        return redirect(url_for('proveedores'))

    form = ProveedorForm(data=dict(proveedor)) if request.method == 'GET' else ProveedorForm()

    if form.validate_on_submit():
        conn.execute(
            'UPDATE proveedores SET nombre=?, servicio=?, sitio=?, estado=? WHERE id=?',
            (form.nombre.data.strip(), form.servicio.data.strip(),
             form.sitio.data.strip(), form.estado.data, id)
        )
        conn.commit()
        conn.close()
        flash(f'Proveedor "{form.nombre.data.strip()}" actualizado correctamente.', 'success')
        return redirect(url_for('proveedores'))

    conn.close()
    return render_template('formulario_proveedor.html', form=form, editando=True, id=id)


@app.route('/proveedores/eliminar/<int:id>', methods=['POST', 'GET'])
def eliminar_proveedor(id):
    """
    Elimina un proveedor de SQLite.
    """
    conn = db.get_connection()
    proveedor = conn.execute('SELECT * FROM proveedores WHERE id = ?', (id,)).fetchone()

    if proveedor is None:
        conn.close()
        flash('El proveedor seleccionado no existe.', 'danger')
        return redirect(url_for('proveedores'))

    conn.execute('DELETE FROM proveedores WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash(f'Proveedor "{proveedor["nombre"]}" eliminado correctamente.', 'success')
    return redirect(url_for('proveedores'))


# ==============================================================================
# MÓDULO CRUD: FACTURACIÓN
# ==============================================================================

@app.route('/facturacion/nueva', methods=['GET', 'POST'])
def nueva_factura():
    """
    Emite un nuevo documento comercial (Factura o Cotización) y lo guarda en SQLite.
    - Permite cargar automáticamente ítems desde el catálogo de servicios.
    - Calcula en tiempo real: Subtotal, IVA (15%), Total, Anticipo y Saldo Pendiente.
    - Serializa la lista de servicios en un campo oculto JSON (servicios_json).
    """
    form = FacturacionForm()
    tipo_solicitado = request.args.get('tipo', 'Cotizacion' if request.args.get('servicio_id') is not None else 'Factura')

    conn = db.get_connection()

    # Inicialización de valores predeterminados para la petición GET
    if request.method == 'GET':
        total_docs = conn.execute('SELECT COUNT(*) FROM facturacion').fetchone()[0]
        form.tipo.data = tipo_solicitado
        if tipo_solicitado == 'Cotizacion':
            form.numero.data = f"COT-2026-{total_docs + 1:04d}"
            form.validez.data = "15 días"
            form.estado.data = "En revision"
        else:
            form.numero.data = f"001-001-{total_docs + 1:04d}"
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

        notas_final = form.notas.data.strip() if form.notas.data else (
            "Propuesta emitida por NexoDigital." if tipo_doc == 'Cotizacion' else "Comprobante emitido por NexoDigital."
        )

        conn.execute(
            '''INSERT INTO facturacion
               (tipo, numero, cliente, fecha, validez, servicios_json, subtotal, iva, monto, anticipo, saldo_pendiente, estado, notas)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (tipo_doc, form.numero.data.strip(), form.cliente.data.strip(), str(form.fecha.data),
             form.validez.data.strip() if form.validez.data else "15 días",
             json.dumps(servicios_detalle), subtotal_val, iva_val, total_val,
             anticipo_val, saldo_val, estado_final, notas_final)
        )
        conn.commit()
        conn.close()

        nombre_doc = "Cotización" if tipo_doc == 'Cotizacion' else "Factura"
        flash(f'{nombre_doc} "{form.numero.data}" guardada correctamente.', 'success')
        return redirect(url_for('facturacion'))

    servicios_catalogo = conn.execute('SELECT * FROM servicios').fetchall()
    clientes_registrados = conn.execute('SELECT * FROM clientes').fetchall()
    conn.close()

    return render_template(
        'formulario_facturacion.html',
        form=form,
        editando=False,
        servicios_catalogo=servicios_catalogo,
        clientes_registrados=clientes_registrados,
        servicio_seleccionado_id=request.args.get('servicio_id', type=int)
    )


@app.route('/facturacion/editar/<int:id>', methods=['GET', 'POST'])
def editar_factura(id):
    """
    Edita un documento comercial (Factura o Cotización) existente en SQLite.
    """
    conn = db.get_connection()
    fila = conn.execute('SELECT * FROM facturacion WHERE id = ?', (id,)).fetchone()

    if fila is None:
        conn.close()
        flash('El documento seleccionado no existe.', 'danger')
        return redirect(url_for('facturacion'))

    factura = dict(fila)
    factura['servicios_detalle'] = json.loads(factura['servicios_json']) if factura['servicios_json'] else []

    form = FacturacionForm(data=factura) if request.method == 'GET' else FacturacionForm()

    if request.method == 'GET':
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
        notas_final = form.notas.data.strip() if form.notas.data else "Documento generado por NexoDigital."

        conn.execute(
            '''UPDATE facturacion SET
               tipo=?, numero=?, cliente=?, fecha=?, validez=?, servicios_json=?,
               subtotal=?, iva=?, monto=?, anticipo=?, saldo_pendiente=?, estado=?, notas=?
               WHERE id=?''',
            (tipo_doc, form.numero.data.strip(), form.cliente.data.strip(), str(form.fecha.data),
             form.validez.data.strip() if form.validez.data else "15 días",
             json.dumps(servicios_detalle), subtotal_val, iva_val, total_val,
             anticipo_val, saldo_val, form.estado.data, notas_final, id)
        )
        conn.commit()
        conn.close()

        nombre_doc = "Cotización" if tipo_doc == 'Cotizacion' else "Factura"
        flash(f'{nombre_doc} "{form.numero.data}" actualizada correctamente.', 'success')
        return redirect(url_for('facturacion'))

    servicios_catalogo = conn.execute('SELECT * FROM servicios').fetchall()
    clientes_registrados = conn.execute('SELECT * FROM clientes').fetchall()
    conn.close()

    return render_template(
        'formulario_facturacion.html',
        form=form,
        editando=True,
        id=id,
        servicios_catalogo=servicios_catalogo,
        clientes_registrados=clientes_registrados,
        detalle_existente=factura['servicios_detalle']
    )


@app.route('/facturacion/eliminar/<int:id>', methods=['POST', 'GET'])
def eliminar_factura(id):
    """
    Elimina un documento comercial de SQLite.
    """
    conn = db.get_connection()
    fila = conn.execute('SELECT * FROM facturacion WHERE id = ?', (id,)).fetchone()

    if fila is None:
        conn.close()
        flash('El documento seleccionado no existe.', 'danger')
        return redirect(url_for('facturacion'))

    tipo_str = "Cotización" if fila['tipo'] == 'Cotizacion' else "Factura"
    numero = fila['numero']

    conn.execute('DELETE FROM facturacion WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash(f'{tipo_str} "{numero}" eliminada correctamente.', 'success')
    return redirect(url_for('facturacion'))


@app.route('/facturacion/comprobante/<int:id>')
def ver_comprobante(id):
    """
    Genera la vista limpia e imprimible del comprobante o cotización.
    Optimizado con estilos CSS para impresión (@media print) o guardado en PDF.
    """
    conn = db.get_connection()
    fila = conn.execute('SELECT * FROM facturacion WHERE id = ?', (id,)).fetchone()
    conn.close()

    if fila is None:
        flash('El documento seleccionado no existe.', 'danger')
        return redirect(url_for('facturacion'))

    factura = dict(fila)
    factura['servicios_detalle'] = json.loads(factura['servicios_json']) if factura['servicios_json'] else []

    return render_template('comprobante_factura.html', factura=factura, id=id)


# ==============================================================================
# PUNTO DE ENTRADA PRINCIPAL DE LA APLICACIÓN
# ==============================================================================
if __name__ == '__main__':
    # Ejecuta el servidor de desarrollo local con recarga automática y depurador activo
    app.run(debug=True)