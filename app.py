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
# Persistencia de datos: SQLite, mediante el módulo db.py (conexión y tablas).
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

# Módulo propio de conexión y creación de tablas SQLite
import db

# ------------------------------------------------------------------------------
# INICIALIZACIÓN DE LA APLICACIÓN FLASK
# ------------------------------------------------------------------------------
app = Flask(__name__)

# Clave secreta para la protección de sesiones y seguridad contra ataques CSRF en formularios
app.config['SECRET_KEY'] = 'nexodigital_clave_secreta_2026'

# Crea las tablas en SQLite si todavía no existen
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
    servicios_destacados = conn.execute('''
        SELECT s.*, t.nombre AS tipo_nombre
        FROM servicios s
        JOIN tipos_servicio t ON s.tipo_servicio_id = t.id
    ''').fetchall()
    conn.close()
    return render_template('index.html', mensaje=mensaje, empresa=empresa, servicios=servicios_destacados)


@app.route('/servicio')
def servicios():
    """
    Ruta del catálogo completo de servicios.
    Usa JOIN para mostrar el nombre de la categoría (tipo_servicio) de cada servicio.
    """
    conn = db.get_connection()
    lista_servicios = conn.execute('''
        SELECT s.*, t.nombre AS tipo_nombre
        FROM servicios s
        JOIN tipos_servicio t ON s.tipo_servicio_id = t.id
    ''').fetchall()
    conn.close()
    return render_template('servicios.html', servicios=lista_servicios)


@app.route('/proveedores')
def proveedores():
    """
    Ruta del directorio de proveedores tecnológicos.
    Usa JOIN con estados_proveedor y categorias_proveedor para mostrar los nombres relacionados.
    """
    conn = db.get_connection()
    lista_proveedores = conn.execute('''
        SELECT p.*, e.nombre AS estado_nombre, c.nombre AS categoria_nombre
        FROM proveedores p
        JOIN estados_proveedor e ON p.estado_id = e.id
        JOIN categorias_proveedor c ON p.categoria_id = c.id
    ''').fetchall()
    conn.close()
    return render_template('proveedores.html', proveedores=lista_proveedores)


@app.route('/clientes')
def clientes():
    """
    Ruta del directorio de clientes comerciales.
    Usa JOIN con tipos_negocio para mostrar el nombre de la categoría de negocio.
    """
    conn = db.get_connection()
    lista_clientes = conn.execute('''
        SELECT c.*, t.nombre AS negocio_nombre
        FROM clientes c
        JOIN tipos_negocio t ON c.tipo_negocio_id = t.id
    ''').fetchall()
    conn.close()
    return render_template('clientes.html', clientes=lista_clientes)


@app.route('/facturacion')
def facturacion():
    """
    Ruta principal del panel comercial de Facturación y Cotizaciones.
    Usa JOIN con clientes y estados_documento para mostrar los nombres relacionados,
    y agrega el conteo de servicios incluidos en cada documento.
    """
    conn = db.get_connection()
    filas = conn.execute('''
        SELECT f.*, c.nombre AS cliente_nombre, e.nombre AS estado_nombre
        FROM facturacion f
        JOIN clientes c ON f.cliente_cedula = c.cedula
        JOIN estados_documento e ON f.estado_id = e.id
        ORDER BY f.numero DESC
    ''').fetchall()

    lista_facturas = []
    for f in filas:
        doc = dict(f)
        conteo = conn.execute(
            'SELECT COUNT(*) FROM detalle_factura WHERE factura_numero = ?', (doc['numero'],)
        ).fetchone()[0]
        doc['servicios_detalle'] = [None] * conteo  # solo se usa para |length en la plantilla
        lista_facturas.append(doc)

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
    conn = db.get_connection()
    tipos_negocio = conn.execute('SELECT * FROM tipos_negocio ORDER BY nombre').fetchall()

    form = ClienteForm()
    form.tipo_negocio_id.choices = [(t['id'], t['nombre']) for t in tipos_negocio]

    if form.validate_on_submit():
        existente = conn.execute('SELECT * FROM clientes WHERE cedula = ?', (form.cedula.data.strip(),)).fetchone()
        if existente is not None:
            conn.close()
            flash('Ya existe un cliente registrado con esa cédula.', 'danger')
            return render_template('formulario_cliente.html', form=form, editando=False)

        conn.execute(
            '''INSERT INTO clientes (cedula, nombre, telefono, correo, tipo_negocio_id, ciudad)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (form.cedula.data.strip(), form.nombre.data.strip(), form.telefono.data.strip(),
             form.correo.data.strip(), form.tipo_negocio_id.data, form.ciudad.data.strip())
        )
        conn.commit()
        conn.close()
        flash('Cliente registrado correctamente.', 'success')
        return redirect(url_for('clientes'))

    conn.close()
    return render_template('formulario_cliente.html', form=form, editando=False)


@app.route('/clientes/editar/<cedula>', methods=['GET', 'POST'])
def editar_cliente(cedula):
    """
    Edita la información de un cliente existente identificado por su cédula (PK).
    La cédula no se modifica desde este formulario, ya que otras tablas dependen de ella.
    """
    conn = db.get_connection()
    cliente = conn.execute('SELECT * FROM clientes WHERE cedula = ?', (cedula,)).fetchone()

    if cliente is None:
        conn.close()
        flash('El cliente seleccionado no existe.', 'danger')
        return redirect(url_for('clientes'))

    tipos_negocio = conn.execute('SELECT * FROM tipos_negocio ORDER BY nombre').fetchall()

    form = ClienteForm(data=dict(cliente)) if request.method == 'GET' else ClienteForm()
    form.tipo_negocio_id.choices = [(t['id'], t['nombre']) for t in tipos_negocio]
    if request.method == 'GET':
        form.tipo_negocio_id.data = cliente['tipo_negocio_id']

    if form.validate_on_submit():
        conn.execute(
            '''UPDATE clientes SET nombre=?, telefono=?, correo=?, tipo_negocio_id=?, ciudad=?
               WHERE cedula=?''',
            (form.nombre.data.strip(), form.telefono.data.strip(),
             form.correo.data.strip(), form.tipo_negocio_id.data, form.ciudad.data.strip(), cedula)
        )
        conn.commit()
        conn.close()
        flash(f'Cliente "{form.nombre.data.strip()}" actualizado correctamente.', 'success')
        return redirect(url_for('clientes'))

    conn.close()
    return render_template('formulario_cliente.html', form=form, editando=True, cedula=cedula)


@app.route('/clientes/eliminar/<cedula>', methods=['POST', 'GET'])
def eliminar_cliente(cedula):
    """
    Elimina un cliente de SQLite según su cédula, siempre que no tenga facturas asociadas.
    """
    conn = db.get_connection()
    cliente = conn.execute('SELECT * FROM clientes WHERE cedula = ?', (cedula,)).fetchone()

    if cliente is None:
        conn.close()
        flash('El cliente seleccionado no existe.', 'danger')
        return redirect(url_for('clientes'))

    facturas_asociadas = conn.execute(
        'SELECT COUNT(*) FROM facturacion WHERE cliente_cedula = ?', (cedula,)
    ).fetchone()[0]

    if facturas_asociadas > 0:
        conn.close()
        flash(f'No se puede eliminar a "{cliente["nombre"]}" porque tiene {facturas_asociadas} factura(s) o cotización(es) registradas.', 'danger')
        return redirect(url_for('clientes'))

    conn.execute('DELETE FROM clientes WHERE cedula = ?', (cedula,))
    conn.commit()
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
    conn = db.get_connection()
    lista_tipos = conn.execute('SELECT * FROM tipos_negocio ORDER BY nombre').fetchall()
    conn.close()
    return render_template('tipos_negocio.html', tipos=lista_tipos)


@app.route('/tipos-negocio/nuevo', methods=['GET', 'POST'])
def nuevo_tipo_negocio():
    """
    Registra una nueva categoría de tipo de negocio.
    """
    form = TipoNegocioForm()
    if form.validate_on_submit():
        conn = db.get_connection()
        conn.execute('INSERT INTO tipos_negocio (nombre) VALUES (?)', (form.nombre.data.strip(),))
        conn.commit()
        conn.close()
        flash('Tipo de negocio registrado correctamente.', 'success')
        return redirect(url_for('tipos_negocio'))
    return render_template('formulario_tipo_negocio.html', form=form, editando=False)


@app.route('/tipos-negocio/editar/<int:id>', methods=['GET', 'POST'])
def editar_tipo_negocio(id):
    """
    Edita el nombre de una categoría de tipo de negocio existente.
    """
    conn = db.get_connection()
    tipo = conn.execute('SELECT * FROM tipos_negocio WHERE id = ?', (id,)).fetchone()

    if tipo is None:
        conn.close()
        flash('El tipo de negocio seleccionado no existe.', 'danger')
        return redirect(url_for('tipos_negocio'))

    form = TipoNegocioForm(data=dict(tipo)) if request.method == 'GET' else TipoNegocioForm()

    if form.validate_on_submit():
        conn.execute('UPDATE tipos_negocio SET nombre=? WHERE id=?', (form.nombre.data.strip(), id))
        conn.commit()
        conn.close()
        flash(f'Tipo de negocio "{form.nombre.data.strip()}" actualizado correctamente.', 'success')
        return redirect(url_for('tipos_negocio'))

    conn.close()
    return render_template('formulario_tipo_negocio.html', form=form, editando=True, id=id)


@app.route('/tipos-negocio/eliminar/<int:id>', methods=['POST', 'GET'])
def eliminar_tipo_negocio(id):
    """
    Elimina un tipo de negocio, siempre que ningún cliente lo esté usando.
    """
    conn = db.get_connection()
    tipo = conn.execute('SELECT * FROM tipos_negocio WHERE id = ?', (id,)).fetchone()

    if tipo is None:
        conn.close()
        flash('El tipo de negocio seleccionado no existe.', 'danger')
        return redirect(url_for('tipos_negocio'))

    en_uso = conn.execute('SELECT COUNT(*) FROM clientes WHERE tipo_negocio_id = ?', (id,)).fetchone()[0]
    if en_uso > 0:
        conn.close()
        flash(f'No se puede eliminar "{tipo["nombre"]}" porque hay clientes asignados a esta categoría.', 'danger')
        return redirect(url_for('tipos_negocio'))

    conn.execute('DELETE FROM tipos_negocio WHERE id = ?', (id,))
    conn.commit()
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
    conn = db.get_connection()
    lista_tipos = conn.execute('SELECT * FROM tipos_servicio ORDER BY nombre').fetchall()
    conn.close()
    return render_template('tipos_servicio.html', tipos=lista_tipos)


@app.route('/tipos-servicio/nuevo', methods=['GET', 'POST'])
def nuevo_tipo_servicio():
    """
    Registra una nueva categoría de servicio.
    """
    form = TipoServicioForm()
    if form.validate_on_submit():
        conn = db.get_connection()
        conn.execute('INSERT INTO tipos_servicio (nombre) VALUES (?)', (form.nombre.data.strip(),))
        conn.commit()
        conn.close()
        flash('Categoría registrada correctamente.', 'success')
        return redirect(url_for('tipos_servicio'))
    return render_template('formulario_tipo_servicio.html', form=form, editando=False)


@app.route('/tipos-servicio/editar/<int:id>', methods=['GET', 'POST'])
def editar_tipo_servicio(id):
    """
    Edita el nombre de una categoría de servicio existente.
    """
    conn = db.get_connection()
    tipo = conn.execute('SELECT * FROM tipos_servicio WHERE id = ?', (id,)).fetchone()

    if tipo is None:
        conn.close()
        flash('La categoría seleccionada no existe.', 'danger')
        return redirect(url_for('tipos_servicio'))

    form = TipoServicioForm(data=dict(tipo)) if request.method == 'GET' else TipoServicioForm()

    if form.validate_on_submit():
        conn.execute('UPDATE tipos_servicio SET nombre=? WHERE id=?', (form.nombre.data.strip(), id))
        conn.commit()
        conn.close()
        flash(f'Categoría "{form.nombre.data.strip()}" actualizada correctamente.', 'success')
        return redirect(url_for('tipos_servicio'))

    conn.close()
    return render_template('formulario_tipo_servicio.html', form=form, editando=True, id=id)


@app.route('/tipos-servicio/eliminar/<int:id>', methods=['POST', 'GET'])
def eliminar_tipo_servicio(id):
    """
    Elimina una categoría de servicio, siempre que ningún servicio la esté usando.
    """
    conn = db.get_connection()
    tipo = conn.execute('SELECT * FROM tipos_servicio WHERE id = ?', (id,)).fetchone()

    if tipo is None:
        conn.close()
        flash('La categoría seleccionada no existe.', 'danger')
        return redirect(url_for('tipos_servicio'))

    en_uso = conn.execute('SELECT COUNT(*) FROM servicios WHERE tipo_servicio_id = ?', (id,)).fetchone()[0]
    if en_uso > 0:
        conn.close()
        flash(f'No se puede eliminar "{tipo["nombre"]}" porque hay servicios asignados a esta categoría.', 'danger')
        return redirect(url_for('tipos_servicio'))

    conn.execute('DELETE FROM tipos_servicio WHERE id = ?', (id,))
    conn.commit()
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
    conn = db.get_connection()
    tipos = conn.execute('SELECT * FROM tipos_servicio ORDER BY nombre').fetchall()

    form = ServicioForm()
    form.tipo_servicio_id.choices = [(t['id'], t['nombre']) for t in tipos]

    if form.validate_on_submit():
        imagen_url = form.imagen.data.strip() if form.imagen.data and form.imagen.data.strip() else "https://images.unsplash.com/photo-1460925895917-afdab827c52f"

        conn.execute(
            '''INSERT INTO servicios (tipo_servicio_id, nombre, precio_base, imagen, descripcion, disponible)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (form.tipo_servicio_id.data, form.nombre.data.strip(), float(form.precio.data),
             imagen_url, form.descripcion.data.strip(), int(form.disponible.data))
        )
        conn.commit()
        conn.close()
        flash('Servicio registrado correctamente.', 'success')
        return redirect(url_for('servicios'))

    conn.close()
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

    tipos = conn.execute('SELECT * FROM tipos_servicio ORDER BY nombre').fetchall()

    datos_form = dict(servicio)
    datos_form['precio'] = servicio['precio_base']  # el form usa 'precio', la BD usa 'precio_base'

    form = ServicioForm(data=datos_form) if request.method == 'GET' else ServicioForm()
    form.tipo_servicio_id.choices = [(t['id'], t['nombre']) for t in tipos]
    if request.method == 'GET':
        form.tipo_servicio_id.data = servicio['tipo_servicio_id']

    if form.validate_on_submit():
        imagen_url = form.imagen.data.strip() if form.imagen.data and form.imagen.data.strip() else servicio['imagen']

        conn.execute(
            '''UPDATE servicios SET tipo_servicio_id=?, nombre=?, precio_base=?, imagen=?, descripcion=?, disponible=?
               WHERE id=?''',
            (form.tipo_servicio_id.data, form.nombre.data.strip(), float(form.precio.data),
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
    conn = db.get_connection()
    estados = conn.execute('SELECT * FROM estados_proveedor ORDER BY id').fetchall()
    categorias = conn.execute('SELECT * FROM categorias_proveedor ORDER BY nombre').fetchall()

    form = ProveedorForm()
    form.estado_id.choices = [(e['id'], e['nombre']) for e in estados]
    form.categoria_id.choices = [(c['id'], c['nombre']) for c in categorias]

    if form.validate_on_submit():
        conn.execute(
            'INSERT INTO proveedores (nombre, categoria_id, sitio, estado_id) VALUES (?, ?, ?, ?)',
            (form.nombre.data.strip(), form.categoria_id.data,
             form.sitio.data.strip(), form.estado_id.data)
        )
        conn.commit()
        conn.close()
        flash('Proveedor registrado correctamente.', 'success')
        return redirect(url_for('proveedores'))

    conn.close()
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

    estados = conn.execute('SELECT * FROM estados_proveedor ORDER BY id').fetchall()
    categorias = conn.execute('SELECT * FROM categorias_proveedor ORDER BY nombre').fetchall()

    form = ProveedorForm(data=dict(proveedor)) if request.method == 'GET' else ProveedorForm()
    form.estado_id.choices = [(e['id'], e['nombre']) for e in estados]
    form.categoria_id.choices = [(c['id'], c['nombre']) for c in categorias]
    if request.method == 'GET':
        form.estado_id.data = proveedor['estado_id']
        form.categoria_id.data = proveedor['categoria_id']

    if form.validate_on_submit():
        conn.execute(
            'UPDATE proveedores SET nombre=?, categoria_id=?, sitio=?, estado_id=? WHERE id=?',
            (form.nombre.data.strip(), form.categoria_id.data,
             form.sitio.data.strip(), form.estado_id.data, id)
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
# MÓDULO CRUD: CATEGORÍAS DE PROVEEDOR
# ==============================================================================

@app.route('/categorias-proveedor')
def categorias_proveedor():
    """
    Lista las categorías de infraestructura disponibles para clasificar proveedores.
    """
    conn = db.get_connection()
    lista_categorias = conn.execute('SELECT * FROM categorias_proveedor ORDER BY nombre').fetchall()
    conn.close()
    return render_template('categorias_proveedor.html', categorias=lista_categorias)


@app.route('/categorias-proveedor/nueva', methods=['GET', 'POST'])
def nueva_categoria_proveedor():
    """
    Registra una nueva categoría de proveedor.
    """
    form = CategoriaProveedorForm()
    if form.validate_on_submit():
        conn = db.get_connection()
        conn.execute('INSERT INTO categorias_proveedor (nombre) VALUES (?)', (form.nombre.data.strip(),))
        conn.commit()
        conn.close()
        flash('Categoría registrada correctamente.', 'success')
        return redirect(url_for('categorias_proveedor'))
    return render_template('formulario_categoria_proveedor.html', form=form, editando=False)


@app.route('/categorias-proveedor/editar/<int:id>', methods=['GET', 'POST'])
def editar_categoria_proveedor(id):
    """
    Edita el nombre de una categoría de proveedor existente.
    """
    conn = db.get_connection()
    categoria = conn.execute('SELECT * FROM categorias_proveedor WHERE id = ?', (id,)).fetchone()

    if categoria is None:
        conn.close()
        flash('La categoría seleccionada no existe.', 'danger')
        return redirect(url_for('categorias_proveedor'))

    form = CategoriaProveedorForm(data=dict(categoria)) if request.method == 'GET' else CategoriaProveedorForm()

    if form.validate_on_submit():
        conn.execute('UPDATE categorias_proveedor SET nombre=? WHERE id=?', (form.nombre.data.strip(), id))
        conn.commit()
        conn.close()
        flash(f'Categoría "{form.nombre.data.strip()}" actualizada correctamente.', 'success')
        return redirect(url_for('categorias_proveedor'))

    conn.close()
    return render_template('formulario_categoria_proveedor.html', form=form, editando=True, id=id)


@app.route('/categorias-proveedor/eliminar/<int:id>', methods=['POST', 'GET'])
def eliminar_categoria_proveedor(id):
    """
    Elimina una categoría de proveedor, siempre que ningún proveedor la esté usando.
    """
    conn = db.get_connection()
    categoria = conn.execute('SELECT * FROM categorias_proveedor WHERE id = ?', (id,)).fetchone()

    if categoria is None:
        conn.close()
        flash('La categoría seleccionada no existe.', 'danger')
        return redirect(url_for('categorias_proveedor'))

    en_uso = conn.execute('SELECT COUNT(*) FROM proveedores WHERE categoria_id = ?', (id,)).fetchone()[0]
    if en_uso > 0:
        conn.close()
        flash(f'No se puede eliminar "{categoria["nombre"]}" porque hay proveedores asignados a esta categoría.', 'danger')
        return redirect(url_for('categorias_proveedor'))

    conn.execute('DELETE FROM categorias_proveedor WHERE id = ?', (id,))
    conn.commit()
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

    conn = db.get_connection()

    clientes_registrados = conn.execute('SELECT * FROM clientes ORDER BY nombre').fetchall()
    form.cliente_cedula.choices = [(c['cedula'], c['nombre']) for c in clientes_registrados]

    estados = conn.execute('SELECT * FROM estados_documento ORDER BY id').fetchall()
    form.estado_id.choices = [(e['id'], e['nombre']) for e in estados]
    id_por_nombre = {e['nombre']: e['id'] for e in estados}

    if request.method == 'GET':
        total_docs = conn.execute('SELECT COUNT(*) FROM facturacion').fetchone()[0]
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
        existente = conn.execute('SELECT * FROM facturacion WHERE numero = ?', (numero_limpio,)).fetchone()
        if existente is not None:
            servicios_catalogo = conn.execute('SELECT * FROM servicios').fetchall()
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

        conn.execute(
            '''INSERT INTO facturacion
               (numero, tipo, cliente_cedula, fecha, validez, subtotal, iva, monto, anticipo, saldo_pendiente, estado_id, notas)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (numero_limpio, tipo_doc, form.cliente_cedula.data, str(form.fecha.data),
             form.validez.data.strip() if form.validez.data else "15 días",
             subtotal_val, iva_val, total_val, anticipo_val, saldo_val, estado_id_final, notas_final)
        )

        for item in servicios_detalle:
            conn.execute(
                '''INSERT INTO detalle_factura (factura_numero, servicio_id, nombre_servicio, cantidad, precio_base, ajuste, total)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (numero_limpio, item.get('id'), item.get('servicio', 'Servicio'),
                 int(item.get('cantidad', 1)), float(item.get('precio', 0)),
                 float(item.get('ajuste', 0)), float(item.get('total', item.get('precio', 0))))
            )

        conn.commit()
        conn.close()

        nombre_doc = "Cotización" if tipo_doc == 'Cotizacion' else "Factura"
        flash(f'{nombre_doc} "{numero_limpio}" guardada correctamente.', 'success')
        return redirect(url_for('facturacion'))

    servicios_catalogo = conn.execute('SELECT * FROM servicios').fetchall()
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
    conn = db.get_connection()
    fila = conn.execute('SELECT * FROM facturacion WHERE numero = ?', (numero,)).fetchone()

    if fila is None:
        conn.close()
        flash('El documento seleccionado no existe.', 'danger')
        return redirect(url_for('facturacion'))

    factura = dict(fila)
    detalle_actual = conn.execute('SELECT * FROM detalle_factura WHERE factura_numero = ?', (numero,)).fetchall()
    factura['servicios_detalle'] = [
        {'id': d['servicio_id'], 'servicio': d['nombre_servicio'], 'cantidad': d['cantidad'],
         'precio': d['precio_base'], 'ajuste': d['ajuste'], 'total': d['total']}
        for d in detalle_actual
    ]

    clientes_registrados = conn.execute('SELECT * FROM clientes ORDER BY nombre').fetchall()
    estados = conn.execute('SELECT * FROM estados_documento ORDER BY id').fetchall()

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

        conn.execute(
            '''UPDATE facturacion SET
               tipo=?, cliente_cedula=?, fecha=?, validez=?,
               subtotal=?, iva=?, monto=?, anticipo=?, saldo_pendiente=?, estado_id=?, notas=?
               WHERE numero=?''',
            (tipo_doc, form.cliente_cedula.data, str(form.fecha.data),
             form.validez.data.strip() if form.validez.data else "15 días",
             subtotal_val, iva_val, total_val, anticipo_val, saldo_val, form.estado_id.data, notas_final, numero)
        )

        conn.execute('DELETE FROM detalle_factura WHERE factura_numero = ?', (numero,))
        for item in servicios_detalle:
            conn.execute(
                '''INSERT INTO detalle_factura (factura_numero, servicio_id, nombre_servicio, cantidad, precio_base, ajuste, total)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (numero, item.get('id'), item.get('servicio', 'Servicio'),
                 int(item.get('cantidad', 1)), float(item.get('precio', 0)),
                 float(item.get('ajuste', 0)), float(item.get('total', item.get('precio', 0))))
            )

        conn.commit()
        conn.close()

        nombre_doc = "Cotización" if tipo_doc == 'Cotizacion' else "Factura"
        flash(f'{nombre_doc} "{numero}" actualizada correctamente.', 'success')
        return redirect(url_for('facturacion'))

    servicios_catalogo = conn.execute('SELECT * FROM servicios').fetchall()
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
    conn = db.get_connection()
    fila = conn.execute('SELECT * FROM facturacion WHERE numero = ?', (numero,)).fetchone()

    if fila is None:
        conn.close()
        flash('El documento seleccionado no existe.', 'danger')
        return redirect(url_for('facturacion'))

    tipo_str = "Cotización" if fila['tipo'] == 'Cotizacion' else "Factura"

    conn.execute('DELETE FROM facturacion WHERE numero = ?', (numero,))
    conn.commit()
    conn.close()

    flash(f'{tipo_str} "{numero}" eliminada correctamente.', 'success')
    return redirect(url_for('facturacion'))


@app.route('/facturacion/comprobante/<numero>')
def ver_comprobante(numero):
    """
    Genera la vista imprimible del comprobante, identificado por su número (PK).
    """
    conn = db.get_connection()
    fila = conn.execute('''
        SELECT f.*, c.nombre AS cliente_nombre, e.nombre AS estado_nombre
        FROM facturacion f
        JOIN clientes c ON f.cliente_cedula = c.cedula
        JOIN estados_documento e ON f.estado_id = e.id
        WHERE f.numero = ?
    ''', (numero,)).fetchone()

    if fila is None:
        conn.close()
        flash('El documento seleccionado no existe.', 'danger')
        return redirect(url_for('facturacion'))

    factura = dict(fila)
    detalle = conn.execute('SELECT * FROM detalle_factura WHERE factura_numero = ?', (numero,)).fetchall()
    conn.close()

    factura['servicios_detalle'] = [
        {'id': d['servicio_id'], 'servicio': d['nombre_servicio'], 'cantidad': d['cantidad'],
         'precio': d['precio_base'], 'ajuste': d['ajuste'], 'total': d['total']}
        for d in detalle
    ]

    return render_template('comprobante_factura.html', factura=factura, numero=numero)


# ==============================================================================
# PUNTO DE ENTRADA PRINCIPAL DE LA APLICACIÓN
# ==============================================================================
if __name__ == '__main__':
    # Ejecuta el servidor de desarrollo local con recarga automática y depurador activo
    app.run(debug=True)
