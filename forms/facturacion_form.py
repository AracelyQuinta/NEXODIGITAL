# ==============================================================================
# FORMULARIO: FACTURACIÓN Y COTIZACIONES COMERCIALES
# ==============================================================================
# Gestiona la emisión y edición de comprobantes de venta y propuestas económicas.
# Soporta detalle dinámico de ítems en formato JSON y cálculo de anticipos/saldos.
# ==============================================================================

from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, TextAreaField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class FacturacionForm(FlaskForm):
    """
    Formulario unificado para Facturas de Venta y Cotizaciones Comerciales.
    """
    # Clasificación del comprobante
    tipo = SelectField(
        'Tipo de Documento',
        choices=[
            ('Factura', 'Factura de Venta (Comprobante Fiscal)'),
            ('Cotizacion', 'Cotización / Proforma Comercial')
        ],
        validators=[DataRequired(message='Selecciona el tipo de documento.')]
    )

    # Número secuencial o código identificador
    numero = StringField(
        'N° Documento / Código',
        validators=[
            DataRequired(message='El número de documento es obligatorio.'),
            Length(min=3, max=40, message='Debe contener entre 3 y 40 caracteres.')
        ]
    )

    # Nombre o razón social del cliente receptor
    cliente = StringField(
        'Cliente / Razón Social',
        validators=[
            DataRequired(message='El nombre del cliente es obligatorio.'),
            Length(min=3, max=100, message='Debe contener entre 3 y 100 caracteres.')
        ]
    )

    # Fecha de emisión del documento (formato YYYY-MM-DD)
    fecha = StringField(
        'Fecha de emisión',
        validators=[
            DataRequired(message='La fecha es obligatoria.'),
            Length(min=8, max=10, message='Formato de fecha no válido.')
        ]
    )

    # Plazo de vigencia de la oferta comercial (aplica principalmente para cotizaciones)
    validez = StringField(
        'Vigencia / Plazo de la oferta',
        validators=[
            Optional(),
            Length(max=50, message='Máximo 50 caracteres para la vigencia.')
        ]
    )
    
    # Campo oculto que almacena la lista de servicios/ítems serializada en JSON
    servicios_json = HiddenField('Detalle de Servicios JSON')
    
    # Subtotal calculado antes de impuestos
    subtotal = FloatField(
        'Subtotal ($)',
        validators=[
            Optional(),
            NumberRange(min=0, message='El subtotal no puede ser un valor negativo.')
        ]
    )

    # Valor del IVA (15% vigente en Ecuador)
    iva = FloatField(
        'IVA 15% ($)',
        validators=[
            Optional(),
            NumberRange(min=0, message='El IVA no puede ser un valor negativo.')
        ]
    )

    # Monto total general del documento
    monto = FloatField(
        'Total General ($)',
        validators=[
            DataRequired(message='El monto total es obligatorio.'),
            NumberRange(min=0.01, message='El total debe ser mayor a 0.')
        ]
    )

    # Valor abonado o anticipo entregado por el cliente
    anticipo = FloatField(
        'Anticipo / Abono Recibido ($)',
        validators=[
            Optional(),
            NumberRange(min=0, message='El anticipo no puede ser negativo.')
        ],
        default=0.00
    )

    # Saldo pendiente de cobro contra entrega
    saldo_pendiente = FloatField(
        'Saldo Pendiente / Diferencia ($)',
        validators=[
            Optional(),
            NumberRange(min=0, message='El saldo no puede ser negativo.')
        ],
        default=0.00
    )
    
    # Estado actual del proceso de cobranza o aprobación
    estado = SelectField(
        'Estado del Documento',
        choices=[
            ('Pagada', 'Pagada (Totalmente Cancelada)'),
            ('Pendiente', 'Pendiente (Con Saldo por Cobrar)'),
            ('Aprobada', 'Aprobada por el Cliente (Cotización)'),
            ('En revision', 'En Revisión / Enviada (Cotización)'),
            ('Vencida', 'Vencida / Expirada')
        ],
        validators=[DataRequired(message='Selecciona el estado actual del documento.')]
    )

    # Notas, términos de pago y condiciones comerciales
    notas = TextAreaField(
        'Notas, Términos y Condiciones de Pago',
        validators=[
            Optional(),
            Length(max=400, message='Las notas no pueden exceder 400 caracteres.')
        ]
    )

    # Botón de guardado
    submit = SubmitField('Guardar y Emitir Documento')
