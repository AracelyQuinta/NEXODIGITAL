# ==============================================================================
# FORMULARIO: REGISTRO Y EDICIÓN DE CLIENTES
# ==============================================================================
# Define la estructura de campos y validaciones para registrar clientes y
# emprendimientos comerciales en la plataforma.
# ==============================================================================

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class ClienteForm(FlaskForm):
    """
    Formulario para la gestión de clientes de NexoDigital.
    Hereda de FlaskForm para incluir protección automática CSRF.
    """
    # Nombre o razón social del cliente
    nombre = StringField(
        'Nombre del cliente o negocio',
        validators=[
            DataRequired(message='El nombre del cliente es obligatorio.'),
            Length(min=3, max=100, message='Debe contener entre 3 y 100 caracteres.')
        ]
    )

    # Giro o actividad económica del cliente
    negocio = StringField(
        'Tipo de negocio o actividad',
        validators=[
            DataRequired(message='El tipo de negocio es obligatorio.'),
            Length(min=3, max=100, message='Debe contener entre 3 y 100 caracteres.')
        ]
    )

    # Servicio o paquete digital contratado
    servicio = StringField(
        'Servicio contratado',
        validators=[
            DataRequired(message='Especifica el servicio acordado con el cliente.'),
            Length(min=3, max=100, message='Debe contener entre 3 y 100 caracteres.')
        ]
    )

    # Ciudad o localidad del cliente
    ciudad = StringField(
        'Ciudad / Localidad',
        validators=[
            DataRequired(message='La ciudad es obligatoria.'),
            Length(min=3, max=50, message='Debe contener entre 3 y 50 caracteres.')
        ]
    )

    # Botón de envío
    submit = SubmitField('Guardar cliente')
