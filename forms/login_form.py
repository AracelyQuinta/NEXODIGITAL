from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    """
    Formulario de inicio de sesión (Semana 14).
    Solicita el nombre de usuario y la contraseña para validar las credenciales
    contra la tabla 'usuarios' de la base de datos.
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
            DataRequired(message='La contraseña es obligatoria.')
        ]
    )

    submit = SubmitField('Iniciar sesión')
