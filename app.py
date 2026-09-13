# ==============================================================================
# PROYECTO: NEXODIGITAL - SOLUCIONES WEB Y COMERCIALES
# Control Principal de la Aplicación Flask (Backend)
# ==============================================================================
# Este archivo contiene la configuración central del servidor y los controladores
# (rutas y vistas) que gestionan la lógica de negocio para:
# 1. Página de inicio y presentación de la empresa
# 2. Catálogo y gestión de Servicios (CRUD) y sus Categorías (CRUD)
# 3. Directorio de Proveedores e infraestructura (CRUD)
# 4. Directorio de Clientes y cartera comercial (CRUD)
# 5. Emisión de Facturas y Cotizaciones (CRUD) con detalle relacional real
#
# Persistencia de datos: PostgreSQL, mediante conexion/conexion.py (conexión centralizada).
# Todas las tablas están relacionadas mediante claves primarias y foráneas:
#   clientes  <--(cliente_cedula)--  facturacion  --(factura_numero)-->  detalle_factura
#   tipos_servicio <--(tipo_servicio_id)--  servicios  <--(servicio_id)--  detalle_factura
# ==============================================================================

import json
from datetime import date
from flask import Flask, render_template, redirect, url_for, flash, request

# Importación de clases de formularios creadas con Flask-WTF
from forms.cliente_form import ClienteForm
from forms.tipo_negocio_form import TipoNegocioForm
from forms.servicio_form import ServicioForm
from forms.tipo_servicio_form import TipoServicioForm
from forms.proveedor_form import ProveedorForm
from forms.categoria_proveedor_form import CategoriaProveedorForm
from forms.facturacion_form import FacturacionForm

# Módulo propio de conexión centralizada a PostgreSQL (carpeta conexion/)
from conexion.conexion import get_db_connection

# ------------------------------------------------------------------------------
# INICIALIZACIÓN DE LA APLICACIÓN FLASK
# ------------------------------------------------------------------------------
app = Flask(__name__)

# Clave secreta para la protección de sesiones y seguridad contra ataques CSRF en formularios
app.config['SECRET_KEY'] = 'nexodigital_clave_secreta_2026'

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
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.*, t.nombre AS tipo_nombre
        FROM servicios s
        JOIN tipos_servicio t ON s.tipo_servicio_id = t.id
    ''')
    servicios_destacados = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', mensaje=mensaje, empresa=empresa, servicios=servicios_destacados)


@app.route('/servicio')
def servicios():
    """
    Ruta del catálogo completo de servicios.
    Usa JOIN para mostrar el nombre de la categoría (tipo_servicio) de cada servicio.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.*, t.nombre AS tipo_nombre
        FROM servicios s
        JOIN tipos_servicio t ON s.tipo_servicio_id = t.id
    ''')
    lista_servicios = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('servicios.html', servicios=lista_servicios)


@app.route('/proveedores')
def proveedores():
    """
    Ruta del directorio de proveedores tecnológicos.
    Usa JOIN con estados_proveedor y categorias_proveedor para mostrar los nombres relacionados.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.*, e.nombre AS estado_nombre, c.nombre AS categoria_nombre
        FROM proveedores p
        JOIN estados_proveedor e ON p.estado_id = e.id
        JOIN categorias_proveedor c ON p.categoria_id = c.id
    ''')
    lista_proveedores = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('proveedores.html', proveedores=lista_proveedores)


@app.route('/clientes')
def clientes():
    """
    Ruta del directorio de clientes comerciales.
    Usa JOIN con tipos_negocio para mostrar el nombre de la categoría de negocio.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.*, t.nombre AS negocio_nombre
        FROM clientes c
        JOIN tipos_negocio t ON c.tipo_negocio_id = t.id
    ''')
    lista_clientes = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('clientes.html', clientes=lista_clientes)


@app.route('/facturacion')
def facturacion():
    """
    Ruta principal del panel comercial de Facturación y Cotizaciones.
    Usa JOIN con clientes y estados_documento para mostrar los nombres relacionados,
    y agrega el conteo de servicios incluidos en cada documento.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT f.*, c.nombre AS cliente_nombre, e.nombre AS estado_nombre
        FROM facturacion f
        JOIN clientes c ON f.cliente_cedula = c.cedula
        JOIN estados_documento e ON f.estado_id = e.id
        ORDER BY f.numero DESC
    ''')
    filas = cursor.fetchall()

    lista_facturas = []
    for f in filas:
        doc = dict(f)
        cursor.execute(
            'SELECT COUNT(*) AS total FROM detalle_factura WHERE factura_numero = %s', (doc['numero'],)
        )
        conteo = cursor.fetchone()['total']
        doc['servicios_detalle'] = [None] * conteo  # solo se usa para |length en la plantilla
        lista_facturas.append(doc)

    cursor.close()
    conn.close()
    return render_template('facturacion.html', facturas=lista_facturas)


# ==============================================================================
# MÓDULO CRUD: CLIENTES
# ==============================================================================

@app.route('/clientes/nuevo', methods=['GET', 'POST'])
def nuevo_cliente():
    """
    Crea y registra un nuevo cliente en el sistema. La cédula es la clave primaria.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tipos_negocio ORDER BY nombre')
    tipos_negocio = cursor.fetchall()

    form = ClienteForm()
    form.tipo_negocio_id.choices = [(t['id'], t['nombre']) for t in tipos_negocio]

    if form.validate_on_submit():
        cursor.execute('SELECT * FROM clientes WHERE cedula = %s', (form.cedula.data.strip(),))
        existente = cursor.fetchone()
        if existente is not None:
            cursor.close()
            conn.close()
            flash('Ya existe un cliente registrado con esa cédula.', 'danger')
            return render_template('formulario_cliente.html', form=form, editando=False)

        cursor.execute(
            '''INSERT INTO clientes (cedula, nombre, telefono, correo, tipo_negocio_id, ciudad)
               VALUES (%s, %s, %s, %s, %s, %s)''',
            (form.cedula.data.strip(), form.nombre.data.strip(), form.telefono.data.strip(),
             form.correo.data.strip(), form.tipo_negocio_id.data, form.ciudad.data.strip())
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash('Cliente registrado correctamente.', 'success')
        return redirect(url_for('clientes'))

    cursor.close()
    conn.close()
    return render_template('formulario_cliente.html', form=form, editando=False)


@app.route('/clientes/editar/<cedula>', methods=['GET', 'POST'])
def editar_cliente(cedula):
    """
    Edita la información de un cliente existente identificado por su cédula (PK).
    La cédula no se modifica desde este formulario, ya que otras tablas dependen de ella.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clientes WHERE cedula = %s', (cedula,))
    cliente = cursor.fetchone()

    if cliente is None:
        cursor.close()
        conn.close()
        flash('El cliente seleccionado no existe.', 'danger')
        return redirect(url_for('clientes'))

    cursor.execute('SELECT * FROM tipos_negocio ORDER BY nombre')
    tipos_negocio = cursor.fetchall()

    form = ClienteForm(data=dict(cliente)) if request.method == 'GET' else ClienteForm()
    form.tipo_negocio_id.choices = [(t['id'], t['nombre']) for t in tipos_negocio]
    if request.method == 'GET':
        form.tipo_negocio_id.data = cliente['tipo_negocio_id']

    if form.validate_on_submit():
        cursor.execute(
            '''UPDATE clientes SET nombre=%s, telefono=%s, correo=%s, tipo_negocio_id=%s, ciudad=%s
               WHERE cedula=%s''',
            (form.nombre.data.strip(), form.telefono.data.strip(),
             form.correo.data.strip(), form.tipo_negocio_id.data, form.ciudad.data.strip(), cedula)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash(f'Cliente "{form.nombre.data.strip()}" actualizado correctamente.', 'success')
        return redirect(url_for('clientes'))

    cursor.close()
    conn.close()
    return render_template('formulario_cliente.html', form=form, editando=True, cedula=cedula)


@app.route('/clientes/eliminar/<cedula>', methods=['POST', 'GET'])
def eliminar_cliente(cedula):
    """
    Elimina un cliente de PostgreSQL según su cédula, siempre que no tenga facturas asociadas.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clientes WHERE cedula = %s', (cedula,))
    cliente = cursor.fetchone()

    if cliente is None:
        cursor.close()
        conn.close()
        flash('El cliente seleccionado no existe.', 'danger')
        return redirect(url_for('clientes'))

    cursor.execute(
        'SELECT COUNT(*) AS total FROM facturacion WHERE cliente_cedula = %s', (cedula,)
    )
    facturas_asociadas = cursor.fetchone()['total']

    if facturas_asociadas > 0:
        cursor.close()
        conn.close()
        flash(f'No se puede eliminar a "{cliente["nombre"]}" porque tiene {facturas_asociadas} factura(s) o cotización(es) registradas.', 'danger')
        return redirect(url_for('clientes'))

    cursor.execute('DELETE FROM clientes WHERE cedula = %s', (cedula,))
    conn.commit()
    cursor.close()
    conn.close()
    flash(f'Cliente "{cliente["nombre"]}" eliminado correctamente.', 'success')
    return redirect(url_for('clientes'))


# ==============================================================================
# MÓDULO CRUD: TIPOS DE NEGOCIO (categorías de clientes)
# ==============================================================================

@app.route('/tipos-negocio')
def tipos_negocio():
    """
    Lista las categorías de tipo de negocio disponibles para clasificar clientes.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tipos_negocio ORDER BY nombre')
    lista_tipos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('tipos_negocio.html', tipos=lista_tipos)


@app.route('/tipos-negocio/nuevo', methods=['GET', 'POST'])
def nuevo_tipo_negocio():
    """
    Registra una nueva categoría de tipo de negocio.
    """
    form = TipoNegocioForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO tipos_negocio (nombre) VALUES (%s)', (form.nombre.data.strip(),))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Tipo de negocio registrado correctamente.', 'success')
        return redirect(url_for('tipos_negocio'))
    return render_template('formulario_tipo_negocio.html', form=form, editando=False)


@app.route('/tipos-negocio/editar/<int:id>', methods=['GET', 'POST'])
def editar_tipo_negocio(id):
    """
    Edita el nombre de una categoría de tipo de negocio existente.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tipos_negocio WHERE id = %s', (id,))
    tipo = cursor.fetchone()

    if tipo is None:
        cursor.close()
        conn.close()
        flash('El tipo de negocio seleccionado no existe.', 'danger')
        return redirect(url_for('tipos_negocio'))

    form = TipoNegocioForm(data=dict(tipo)) if request.method == 'GET' else TipoNegocioForm()

    if form.validate_on_submit():
        cursor.execute('UPDATE tipos_negocio SET nombre=%s WHERE id=%s', (form.nombre.data.strip(), id))
        conn.commit()
        cursor.close()
        conn.close()
        flash(f'Tipo de negocio "{form.nombre.data.strip()}" actualizado correctamente.', 'success')
        return redirect(url_for('tipos_negocio'))

    cursor.close()
    conn.close()
    return render_template('formulario_tipo_negocio.html', form=form, editando=True, id=id)


@app.route('/tipos-negocio/eliminar/<int:id>', methods=['POST', 'GET'])
def eliminar_tipo_negocio(id):
    """
    Elimina un tipo de negocio, siempre que ningún cliente lo esté usando.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tipos_negocio WHERE id = %s', (id,))
    tipo = cursor.fetchone()

    if tipo is None:
        cursor.close()
        conn.close()
        flash('El tipo de negocio seleccionado no existe.', 'danger')
        return redirect(url_for('tipos_negocio'))

    cursor.execute('SELECT COUNT(*) AS total FROM clientes WHERE tipo_negocio_id = %s', (id,))
    en_uso = cursor.fetchone()['total']
    if en_uso > 0:
        cursor.close()
        conn.close()
        flash(f'No se puede eliminar "{tipo["nombre"]}" porque hay clientes asignados a esta categoría.', 'danger')
        return redirect(url_for('tipos_negocio'))

    cursor.execute('DELETE FROM tipos_negocio WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash(f'Tipo de negocio "{tipo["nombre"]}" eliminado correctamente.', 'success')
    return redirect(url_for('tipos_negocio'))


# ==============================================================================
# MÓDULO CRUD: TIPOS DE SERVICIO (categorías)
# ==============================================================================

@app.route('/tipos-servicio')
def tipos_servicio():
    """
    Lista las categorías de servicio disponibles en el catálogo.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tipos_servicio ORDER BY nombre')
    lista_tipos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('tipos_servicio.html', tipos=lista_tipos)


@app.route('/tipos-servicio/nuevo', methods=['GET', 'POST'])
def nuevo_tipo_servicio():
    """
    Registra una nueva categoría de servicio.
    """
    form = TipoServicioForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO tipos_servicio (nombre) VALUES (%s)', (form.nombre.data.strip(),))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Categoría registrada correctamente.', 'success')
        return redirect(url_for('tipos_servicio'))
    return render_template('formulario_tipo_servicio.html', form=form, editando=False)


@app.route('/tipos-servicio/editar/<int:id>', methods=['GET', 'POST'])
def editar_tipo_servicio(id):
    """
    Edita el nombre de una categoría de servicio existente.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tipos_servicio WHERE id = %s', (id,))
    tipo = cursor.fetchone()

    if tipo is None:
        cursor.close()
        conn.close()
        flash('La categoría seleccionada no existe.', 'danger')
        return redirect(url_for('tipos_servicio'))

    form = TipoServicioForm(data=dict(tipo)) if request.method == 'GET' else TipoServicioForm()

    if form.validate_on_submit():
        cursor.execute('UPDATE tipos_servicio SET nombre=%s WHERE id=%s', (form.nombre.data.strip(), id))
        conn.commit()
        cursor.close()
        conn.close()
        flash(f'Categoría "{form.nombre.data.strip()}" actualizada correctamente.', 'success')
        return redirect(url_for('tipos_servicio'))

    cursor.close()
    conn.close()
    return render_template('formulario_tipo_servicio.html', form=form, editando=True, id=id)


@app.route('/tipos-servicio/eliminar/<int:id>', methods=['POST', 'GET'])
def eliminar_tipo_servicio(id):
    """
    Elimina una categoría de servicio, siempre que ningún servicio la esté usando.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tipos_servicio WHERE id = %s', (id,))
    tipo = cursor.fetchone()

    if tipo is None:
        cursor.close()
        conn.close()
        flash('La categoría seleccionada no existe.', 'danger')
        return redirect(url_for('tipos_servicio'))

    cursor.execute('SELECT COUNT(*) AS total FROM servicios WHERE tipo_servicio_id = %s', (id,))
    en_uso = cursor.fetchone()['total']
    if en_uso > 0:
        cursor.close()
        conn.close()
        flash(f'No se puede eliminar "{tipo["nombre"]}" porque hay servicios asignados a esta categoría.', 'danger')
        return redirect(url_for('tipos_servicio'))

    cursor.execute('DELETE FROM tipos_servicio WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash(f'Categoría "{tipo["nombre"]}" eliminada correctamente.', 'success')
    return redirect(url_for('tipos_servicio'))


# ==============================================================================
# MÓDULO CRUD: SERVICIOS
# ==============================================================================

@app.route('/servicio/nuevo', methods=['GET', 'POST'])
def nuevo_servicio():
    """
    Registra un nuevo servicio en el catálogo, asociado a una categoría (tipo_servicio_id).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tipos_servicio ORDER BY nombre')
    tipos = cursor.fetchall()

    form = ServicioForm()
    form.tipo_servicio_id.choices = [(t['id'], t['nombre']) for t in tipos]

    if form.validate_on_submit():
        imagen_url = form.imagen.data.strip() if form.imagen.data and form.imagen.data.strip() else "https://images.unsplash.com/photo-1460925895917-afdab827c52f"

        cursor.execute(
            '''INSERT INTO servicios (tipo_servicio_id, nombre, precio_base, imagen, descripcion, disponible)
               VALUES (%s, %s, %s, %s, %s, %s)''',
            (form.tipo_servicio_id.data, form.nombre.data.strip(), float(form.precio.data),
             imagen_url, form.descripcion.data.strip(), form.disponible.data)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash('Servicio registrado correctamente.', 'success')
        return redirect(url_for('servicios'))

    cursor.close()
    conn.close()
    return render_template('formulario_servicio.html', form=form, editando=False)


@app.route('/servicios/editar/<int:id>', methods=['GET', 'POST'])
@app.route('/servicio/editar/<int:id>', methods=['GET', 'POST'])
def editar_servicio(id):
    """
    Edita un servicio existente identificado por su id real de PostgreSQL.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM servicios WHERE id = %s', (id,))
    servicio = cursor.fetchone()

    if servicio is None:
        cursor.close()
        conn.close()
        flash('El servicio seleccionado no existe.', 'danger')
        return redirect(url_for('servicios'))

    cursor.execute('SELECT * FROM tipos_servicio ORDER BY nombre')
    tipos = cursor.fetchall()

    datos_form = dict(servicio)
    datos_form['precio'] = servicio['precio_base']  # el form usa 'precio', la BD usa 'precio_base'

    form = ServicioForm(data=datos_form) if request.method == 'GET' else ServicioForm()
    form.tipo_servicio_id.choices = [(t['id'], t['nombre']) for t in tipos]
    if request.method == 'GET':
        form.tipo_servicio_id.data = servicio['tipo_servicio_id']

    if form.validate_on_submit():
        imagen_url = form.imagen.data.strip() if form.imagen.data and form.imagen.data.strip() else servicio['imagen']

        cursor.execute(
            '''UPDATE servicios SET tipo_servicio_id=%s, nombre=%s, precio_base=%s, imagen=%s, descripcion=%s, disponible=%s
               WHERE id=%s''',
            (form.tipo_servicio_id.data, form.nombre.data.strip(), float(form.precio.data),
             imagen_url, form.descripcion.data.strip(), form.disponible.data, id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash(f'Servicio "{form.nombre.data.strip()}" actualizado correctamente.', 'success')
        return redirect(url_for('servicios'))

    cursor.close()
    conn.close()
    return render_template('formulario_servicio.html', form=form, editando=True, id=id)


@app.route('/servicios/eliminar/<int:id>', methods=['POST', 'GET'])
@app.route('/servicio/eliminar/<int:id>', methods=['POST', 'GET'])
def eliminar_servicio(id):
    """
    Elimina un servicio del catálogo en PostgreSQL.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM servicios WHERE id = %s', (id,))
    servicio = cursor.fetchone()

    if servicio is None:
        cursor.close()
        conn.close()
        flash('El servicio seleccionado no existe.', 'danger')
        return redirect(url_for('servicios'))

    cursor.execute('DELETE FROM servicios WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash(f'Servicio "{servicio["nombre"]}" eliminado correctamente.', 'success')
    return redirect(url_for('servicios'))


# ==============================================================================
# MÓDULO CRUD: PROVEEDORES
# ==============================================================================

@app.route('/proveedores/nuevo', methods=['GET', 'POST'])
def nuevo_proveedor():
    """
    Registra un nuevo proveedor de servicios o infraestructura en PostgreSQL.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM estados_proveedor ORDER BY id')
    estados = cursor.fetchall()
    cursor.execute('SELECT * FROM categorias_proveedor ORDER BY nombre')
    categorias = cursor.fetchall()

    form = ProveedorForm()
    form.estado_id.choices = [(e['id'], e['nombre']) for e in estados]
    form.categoria_id.choices = [(c['id'], c['nombre']) for c in categorias]

    if form.validate_on_submit():
        cursor.execute(
            'INSERT INTO proveedores (nombre, categoria_id, sitio, estado_id) VALUES (%s, %s, %s, %s)',
            (form.nombre.data.strip(), form.categoria_id.data,
             form.sitio.data.strip(), form.estado_id.data)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash('Proveedor registrado correctamente.', 'success')
        return redirect(url_for('proveedores'))

    cursor.close()
    conn.close()
    return render_template('formulario_proveedor.html', form=form, editando=False)


@app.route('/proveedores/editar/<int:id>', methods=['GET', 'POST'])
def editar_proveedor(id):
    """
    Modifica los datos de un proveedor existente en PostgreSQL.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM proveedores WHERE id = %s', (id,))
    proveedor = cursor.fetchone()

    if proveedor is None:
        cursor.close()
        conn.close()
        flash('El proveedor seleccionado no existe.', 'danger')
        return redirect(url_for('proveedores'))

    cursor.execute('SELECT * FROM estados_proveedor ORDER BY id')
    estados = cursor.fetchall()
    cursor.execute('SELECT * FROM categorias_proveedor ORDER BY nombre')
    categorias = cursor.fetchall()

    form = ProveedorForm(data=dict(proveedor)) if request.method == 'GET' else ProveedorForm()
    form.estado_id.choices = [(e['id'], e['nombre']) for e in estados]
    form.categoria_id.choices = [(c['id'], c['nombre']) for c in categorias]
    if request.method == 'GET':
        form.estado_id.data = proveedor['estado_id']
        form.categoria_id.data = proveedor['categoria_id']

    if form.validate_on_submit():
        cursor.execute(
            'UPDATE proveedores SET nombre=%s, categoria_id=%s, sitio=%s, estado_id=%s WHERE id=%s',
            (form.nombre.data.strip(), form.categoria_id.data,
             form.sitio.data.strip(), form.estado_id.data, id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash(f'Proveedor "{form.nombre.data.strip()}" actualizado correctamente.', 'success')
        return redirect(url_for('proveedores'))

    cursor.close()
    conn.close()
    return render_template('formulario_proveedor.html', form=form, editando=True, id=id)


@app.route('/proveedores/eliminar/<int:id>', methods=['POST', 'GET'])
def eliminar_proveedor(id):
    """
    Elimina un proveedor de PostgreSQL.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM proveedores WHERE id = %s', (id,))
    proveedor = cursor.fetchone()

    if proveedor is None:
        cursor.close()
        conn.close()
        flash('El proveedor seleccionado no existe.', 'danger')
        return redirect(url_for('proveedores'))

    cursor.execute('DELETE FROM proveedores WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash(f'Proveedor "{proveedor["nombre"]}" eliminado correctamente.', 'success')
    return redirect(url_for('proveedores'))


# ==============================================================================
# MÓDULO CRUD: CATEGORÍAS DE PROVEEDOR
# ==============================================================================

@app.route('/categorias-proveedor')
def categorias_proveedor():
    """
    Lista las categorías de infraestructura disponibles para clasificar proveedores.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM categorias_proveedor ORDER BY nombre')
    lista_categorias = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('categorias_proveedor.html', categorias=lista_categorias)


@app.route('/categorias-proveedor/nueva', methods=['GET', 'POST'])
def nueva_categoria_proveedor():
    """
    Registra una nueva categoría de proveedor.
    """
    form = CategoriaProveedorForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO categorias_proveedor (nombre) VALUES (%s)', (form.nombre.data.strip(),))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Categoría registrada correctamente.', 'success')
        return redirect(url_for('categorias_proveedor'))
    return render_template('formulario_categoria_proveedor.html', form=form, editando=False)


@app.route('/categorias-proveedor/editar/<int:id>', methods=['GET', 'POST'])
def editar_categoria_proveedor(id):
    """
    Edita el nombre de una categoría de proveedor existente.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM categorias_proveedor WHERE id = %s', (id,))
    categoria = cursor.fetchone()

    if categoria is None:
        cursor.close()
        conn.close()
        flash('La categoría seleccionada no existe.', 'danger')
        return redirect(url_for('categorias_proveedor'))

    form = CategoriaProveedorForm(data=dict(categoria)) if request.method == 'GET' else CategoriaProveedorForm()

    if form.validate_on_submit():
        cursor.execute('UPDATE categorias_proveedor SET nombre=%s WHERE id=%s', (form.nombre.data.strip(), id))
        conn.commit()
        cursor.close()
        conn.close()
        flash(f'Categoría "{form.nombre.data.strip()}" actualizada correctamente.', 'success')
        return redirect(url_for('categorias_proveedor'))

    cursor.close()
    conn.close()
    return render_template('formulario_categoria_proveedor.html', form=form, editando=True, id=id)


@app.route('/categorias-proveedor/eliminar/<int:id>', methods=['POST', 'GET'])
def eliminar_categoria_proveedor(id):
    """
    Elimina una categoría de proveedor, siempre que ningún proveedor la esté usando.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM categorias_proveedor WHERE id = %s', (id,))
    categoria = cursor.fetchone()

    if categoria is None:
        cursor.close()
        conn.close()
        flash('La categoría seleccionada no existe.', 'danger')
        return redirect(url_for('categorias_proveedor'))

    cursor.execute('SELECT COUNT(*) AS total FROM proveedores WHERE categoria_id = %s', (id,))
    en_uso = cursor.fetchone()['total']
    if en_uso > 0:
        cursor.close()
        conn.close()
        flash(f'No se puede eliminar "{categoria["nombre"]}" porque hay proveedores asignados a esta categoría.', 'danger')
        return redirect(url_for('categorias_proveedor'))

    cursor.execute('DELETE FROM categorias_proveedor WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash(f'Categoría "{categoria["nombre"]}" eliminada correctamente.', 'success')
    return redirect(url_for('categorias_proveedor'))


# ==============================================================================
# MÓDULO CRUD: FACTURACIÓN
# ==============================================================================

@app.route('/facturacion/nueva', methods=['GET', 'POST'])
def nueva_factura():
    """
    Emite un nuevo documento comercial (Factura o Cotización).
    El cliente se selecciona de una lista real (cliente_cedula), y cada servicio
    incluido se guarda como una fila propia en detalle_factura.
    """
    form = FacturacionForm()
    tipo_solicitado = request.args.get('tipo', 'Cotizacion' if request.args.get('servicio_id') is not None else 'Factura')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM clientes ORDER BY nombre')
    clientes_registrados = cursor.fetchall()
    form.cliente_cedula.choices = [(c['cedula'], c['nombre']) for c in clientes_registrados]

    cursor.execute('SELECT * FROM estados_documento ORDER BY id')
    estados = cursor.fetchall()
    form.estado_id.choices = [(e['id'], e['nombre']) for e in estados]
    id_por_nombre = {e['nombre']: e['id'] for e in estados}

    if request.method == 'GET':
        cursor.execute('SELECT COUNT(*) AS total FROM facturacion')
        total_docs = cursor.fetchone()['total']
        form.tipo.data = tipo_solicitado
        if tipo_solicitado == 'Cotizacion':
            form.numero.data = f"COT-2026-{total_docs + 1:04d}"
            form.validez.data = "15 días"
            form.estado_id.data = id_por_nombre.get('En revision')
        else:
            form.numero.data = f"001-001-{total_docs + 1:04d}"
            form.validez.data = "30 días"
            form.estado_id.data = id_por_nombre.get('Pendiente')
        form.fecha.data = str(date.today())
        form.anticipo.data = 0.00
        form.saldo_pendiente.data = 0.00

    if form.validate_on_submit():
        numero_limpio = form.numero.data.strip()
        cursor.execute('SELECT * FROM facturacion WHERE numero = %s', (numero_limpio,))
        existente = cursor.fetchone()
        if existente is not None:
            cursor.execute('SELECT * FROM servicios')
            servicios_catalogo = cursor.fetchall()
            cursor.close()
            conn.close()
            flash(f'Ya existe un documento con el número "{numero_limpio}". Usa un número distinto.', 'danger')
            return render_template(
                'formulario_facturacion.html', form=form, editando=False,
                servicios_catalogo=servicios_catalogo, clientes_registrados=clientes_registrados,
                servicio_seleccionado_id=request.args.get('servicio_id', type=int)
            )

        servicios_detalle = []
        if form.servicios_json.data:
            try:
                servicios_detalle = json.loads(form.servicios_json.data)
            except Exception:
                servicios_detalle = []

        subtotal_val = float(form.subtotal.data) if form.subtotal.data is not None else float(form.monto.data)
        iva_val = float(form.iva.data) if form.iva.data is not None else round(subtotal_val * 0.15, 2)
        total_val = float(form.monto.data)
        anticipo_val = float(form.anticipo.data) if form.anticipo.data is not None else 0.00
        saldo_val = float(form.saldo_pendiente.data) if form.saldo_pendiente.data is not None else max(0.0, total_val - anticipo_val)

        tipo_doc = form.tipo.data
        estado_id_final = form.estado_id.data
        if tipo_doc == 'Factura' and saldo_val <= 0 and estado_id_final == id_por_nombre.get('Pendiente'):
            estado_id_final = id_por_nombre.get('Pagada')

        notas_final = form.notas.data.strip() if form.notas.data else (
            "Propuesta emitida por NexoDigital." if tipo_doc == 'Cotizacion' else "Comprobante emitido por NexoDigital."
        )

        cursor.execute(
            '''INSERT INTO facturacion
               (numero, tipo, cliente_cedula, fecha, validez, subtotal, iva, monto, anticipo, saldo_pendiente, estado_id, notas)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
            (numero_limpio, tipo_doc, form.cliente_cedula.data, str(form.fecha.data),
             form.validez.data.strip() if form.validez.data else "15 días",
             subtotal_val, iva_val, total_val, anticipo_val, saldo_val, estado_id_final, notas_final)
        )

        for item in servicios_detalle:
            cursor.execute(
                '''INSERT INTO detalle_factura (factura_numero, servicio_id, nombre_servicio, cantidad, precio_base, ajuste, total)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                (numero_limpio, item.get('id'), item.get('servicio', 'Servicio'),
                 int(item.get('cantidad', 1)), float(item.get('precio', 0)),
                 float(item.get('ajuste', 0)), float(item.get('total', item.get('precio', 0))))
            )

        conn.commit()
        cursor.close()
        conn.close()

        nombre_doc = "Cotización" if tipo_doc == 'Cotizacion' else "Factura"
        flash(f'{nombre_doc} "{numero_limpio}" guardada correctamente.', 'success')
        return redirect(url_for('facturacion'))

    cursor.execute('SELECT * FROM servicios')
    servicios_catalogo = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template(
        'formulario_facturacion.html',
        form=form,
        editando=False,
        servicios_catalogo=servicios_catalogo,
        clientes_registrados=clientes_registrados,
        servicio_seleccionado_id=request.args.get('servicio_id', type=int)
    )


@app.route('/facturacion/editar/<numero>', methods=['GET', 'POST'])
def editar_factura(numero):
    """
    Edita un documento comercial existente, identificado por su número (clave primaria).
    El número no se modifica desde este formulario, ya que detalle_factura depende de él.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM facturacion WHERE numero = %s', (numero,))
    fila = cursor.fetchone()

    if fila is None:
        cursor.close()
        conn.close()
        flash('El documento seleccionado no existe.', 'danger')
        return redirect(url_for('facturacion'))

    factura = dict(fila)
    cursor.execute('SELECT * FROM detalle_factura WHERE factura_numero = %s', (numero,))
    detalle_actual = cursor.fetchall()
    factura['servicios_detalle'] = [
        {'id': d['servicio_id'], 'servicio': d['nombre_servicio'], 'cantidad': d['cantidad'],
         'precio': d['precio_base'], 'ajuste': d['ajuste'], 'total': d['total']}
        for d in detalle_actual
    ]

    cursor.execute('SELECT * FROM clientes ORDER BY nombre')
    clientes_registrados = cursor.fetchall()
    cursor.execute('SELECT * FROM estados_documento ORDER BY id')
    estados = cursor.fetchall()

    form = FacturacionForm(data=factura) if request.method == 'GET' else FacturacionForm()
    form.cliente_cedula.choices = [(c['cedula'], c['nombre']) for c in clientes_registrados]
    form.estado_id.choices = [(e['id'], e['nombre']) for e in estados]

    if request.method == 'GET':
        form.cliente_cedula.data = factura['cliente_cedula']
        form.estado_id.data = factura['estado_id']
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

        cursor.execute(
            '''UPDATE facturacion SET
               tipo=%s, cliente_cedula=%s, fecha=%s, validez=%s,
               subtotal=%s, iva=%s, monto=%s, anticipo=%s, saldo_pendiente=%s, estado_id=%s, notas=%s
               WHERE numero=%s''',
            (tipo_doc, form.cliente_cedula.data, str(form.fecha.data),
             form.validez.data.strip() if form.validez.data else "15 días",
             subtotal_val, iva_val, total_val, anticipo_val, saldo_val, form.estado_id.data, notas_final, numero)
        )

        cursor.execute('DELETE FROM detalle_factura WHERE factura_numero = %s', (numero,))
        for item in servicios_detalle:
            cursor.execute(
                '''INSERT INTO detalle_factura (factura_numero, servicio_id, nombre_servicio, cantidad, precio_base, ajuste, total)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                (numero, item.get('id'), item.get('servicio', 'Servicio'),
                 int(item.get('cantidad', 1)), float(item.get('precio', 0)),
                 float(item.get('ajuste', 0)), float(item.get('total', item.get('precio', 0))))
            )

        conn.commit()
        cursor.close()
        conn.close()

        nombre_doc = "Cotización" if tipo_doc == 'Cotizacion' else "Factura"
        flash(f'{nombre_doc} "{numero}" actualizada correctamente.', 'success')
        return redirect(url_for('facturacion'))

    cursor.execute('SELECT * FROM servicios')
    servicios_catalogo = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template(
        'formulario_facturacion.html',
        form=form,
        editando=True,
        numero=numero,
        servicios_catalogo=servicios_catalogo,
        clientes_registrados=clientes_registrados,
        detalle_existente=factura['servicios_detalle']
    )


@app.route('/facturacion/eliminar/<numero>', methods=['POST', 'GET'])
def eliminar_factura(numero):
    """
    Elimina un documento comercial identificado por su número. El detalle asociado
    se borra automáticamente gracias a ON DELETE CASCADE en detalle_factura.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM facturacion WHERE numero = %s', (numero,))
    fila = cursor.fetchone()

    if fila is None:
        cursor.close()
        conn.close()
        flash('El documento seleccionado no existe.', 'danger')
        return redirect(url_for('facturacion'))

    tipo_str = "Cotización" if fila['tipo'] == 'Cotizacion' else "Factura"

    cursor.execute('DELETE FROM facturacion WHERE numero = %s', (numero,))
    conn.commit()
    cursor.close()
    conn.close()

    flash(f'{tipo_str} "{numero}" eliminada correctamente.', 'success')
    return redirect(url_for('facturacion'))


@app.route('/facturacion/comprobante/<numero>')
def ver_comprobante(numero):
    """
    Genera la vista imprimible del comprobante, identificado por su número (PK).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT f.*, c.nombre AS cliente_nombre, e.nombre AS estado_nombre
        FROM facturacion f
        JOIN clientes c ON f.cliente_cedula = c.cedula
        JOIN estados_documento e ON f.estado_id = e.id
        WHERE f.numero = %s
    ''', (numero,))
    fila = cursor.fetchone()

    if fila is None:
        cursor.close()
        conn.close()
        flash('El documento seleccionado no existe.', 'danger')
        return redirect(url_for('facturacion'))

    factura = dict(fila)
    cursor.execute('SELECT * FROM detalle_factura WHERE factura_numero = %s', (numero,))
    detalle = cursor.fetchall()
    cursor.close()
    conn.close()

    factura['servicios_detalle'] = [
        {'id': d['servicio_id'], 'servicio': d['nombre_servicio'], 'cantidad': d['cantidad'],
         'precio': d['precio_base'], 'ajuste': d['ajuste'], 'total': d['total']}
        for d in detalle
    ]

    return render_template('comprobante_factura.html', factura=factura, numero=numero)



# ==============================================================================
# MÓDULO: PANEL DE ESTADÍSTICAS (solo lectura)
# ==============================================================================
# Panel de resultados para la toma de decisiones del negocio. Muestra qué
# servicios son los más solicitados, usando una consulta RELACIONADA entre dos
# tablas (detalle_factura y servicios) mediante la clave foránea servicio_id.
# Cumple el requisito de "consulta relacionada entre dos tablas con JOIN".

@app.route('/estadisticas')
def estadisticas():
    """
    Panel de resultados del negocio. Calcula, a partir de las facturas reales:
      - El ranking de servicios más solicitados (JOIN detalle_factura + servicios).
      - Totales generales (servicios vendidos e ingresos estimados).
    Es una vista de SOLO LECTURA: no agrega, edita ni elimina datos.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Consulta relacionada (JOIN) entre detalle_factura y servicios mediante la
    # clave foránea servicio_id. Se agrupa por servicio y se ordena del más
    # solicitado al menos solicitado.
    cursor.execute('''
        SELECT s.nombre AS servicio,
               t.nombre AS categoria,
               SUM(d.cantidad) AS unidades,
               SUM(d.total)    AS ingresos
        FROM detalle_factura d
        JOIN servicios s      ON d.servicio_id = s.id
        JOIN tipos_servicio t ON s.tipo_servicio_id = t.id
        GROUP BY s.nombre, t.nombre
        ORDER BY unidades DESC
    ''')
    ranking = cursor.fetchall()

    # Totales generales para las tarjetas resumen del panel.
    cursor.execute('''
        SELECT COALESCE(SUM(cantidad), 0) AS total_unidades,
               COALESCE(SUM(total), 0)    AS total_ingresos
        FROM detalle_factura
    ''')
    fila_totales = cursor.fetchone()

    cursor.close()
    conn.close()

    # El servicio más solicitado es el primero del ranking (si existe).
    servicio_top = ranking[0]['servicio'] if ranking else 'Sin datos aún'
    # La unidad máxima sirve para dibujar el ancho de las barras en la plantilla.
    max_unidades = ranking[0]['unidades'] if ranking else 0

    return render_template(
        'estadisticas.html',
        ranking=ranking,
        total_unidades=fila_totales['total_unidades'],
        total_ingresos=fila_totales['total_ingresos'],
        servicio_top=servicio_top,
        max_unidades=max_unidades
    )


# ==============================================================================
# PUNTO DE ENTRADA PRINCIPAL DE LA APLICACIÓN
# ==============================================================================
if __name__ == '__main__':
    # Ejecuta el servidor de desarrollo local con recarga automática y depurador activo
    app.run(debug=True)
