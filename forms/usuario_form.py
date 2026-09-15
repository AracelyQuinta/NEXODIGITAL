from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo


class UsuarioForm(FlaskForm):
    """
    Formulario para registrar un nuevo usuario del sistema (Semana 14).
    Pide el nombre de usuario y la contraseña (dos veces, para confirmar que
    coinciden). La contraseña se protegerá con hash ANTES de guardarla.
    """
    usuario = StringField(
        'Usuario',
        validators=[
            DataRequired(message='El nombre de usuario es obligatorio.'),
            Length(min=3, max=50, message='Debe tener entre 3 y 50 caracteres.')
        ]
    )

    password = PasswordField(
        'Contraseña',
        validators=[
            DataRequired(message='La contraseña es obligatoria.'),
            Length(min=4, message='La contraseña debe tener al menos 4 caracteres.')
        ]
    )

    # Segundo campo de contraseña: debe ser igual al anterior (EqualTo lo valida).
    confirmar = PasswordField(
        'Confirmar contraseña',
        validators=[
            DataRequired(message='Debes confirmar la contraseña.'),
            EqualTo('password', message='Las contraseñas no coinciden.')
        ]
    )

    submit = SubmitField('Registrar usuario')
