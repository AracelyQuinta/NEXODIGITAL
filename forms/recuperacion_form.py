from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Regexp


class SolicitarRecuperacionForm(FlaskForm):
    identificador = StringField(
        'Correo electrónico o nombre de usuario',
        validators=[DataRequired(message='Ingresa tu correo o nombre de usuario.'), Length(max=150)]
    )
    submit = SubmitField('Enviar PIN')


class VerificarPinForm(FlaskForm):
    pin = StringField(
        'PIN de seguridad',
        validators=[
            DataRequired(message='Ingresa el PIN recibido por correo.'),
            Regexp(r'^\d{6}$', message='El PIN debe contener exactamente 6 dígitos.')
        ]
    )
    submit = SubmitField('Verificar PIN')


class NuevaPasswordForm(FlaskForm):
    password = PasswordField(
        'Nueva contraseña',
        validators=[
            DataRequired(message='Ingresa una nueva contraseña.'),
            Length(min=8, message='La contraseña debe tener al menos 8 caracteres.'),
            Regexp(
                r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[^A-Za-z\d]).{8,}$',
                message='Usa mayúscula, minúscula, número y símbolo.'
            )
        ]
    )
    confirmar_password = PasswordField(
        'Confirmar nueva contraseña',
        validators=[
            DataRequired(message='Confirma la nueva contraseña.'),
            EqualTo('password', message='Las contraseñas no coinciden.')
        ]
    )
    submit = SubmitField('Cambiar contraseña')
