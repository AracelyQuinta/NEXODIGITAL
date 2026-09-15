# ==============================================================================
# PROYECTO: NEXODIGITAL - MODELO DE USUARIO
# ==============================================================================
# Este archivo define la clase 'Usuario', que representa a una persona con
# sesión en el sistema. Flask-Login necesita una clase de usuario que herede de
# 'UserMixin' para poder gestionar el inicio y cierre de sesión.
#
# UserMixin le entrega a la clase, de forma automática, los métodos que
# Flask-Login espera (is_authenticated, is_active, get_id(), etc.), 
# ==============================================================================

from flask_login import UserMixin


class Usuario(UserMixin):
    """
    Representa a un usuario autenticado del sistema.

    Atributos:
        id       -> identificador único del usuario (clave primaria en la BD).
        usuario  -> nombre de usuario con el que inicia sesión.
        password -> contraseña ya protegida (hash), tal como se guarda en la BD.
    """

    def __init__(self, id, usuario, password):
        self.id = id
        self.usuario = usuario
        self.password = password

    def get_id(self):
        """
        Flask-Login usa este método para saber qué identificador guardar en la
        sesión. Debe devolverse como texto (string).
        """
        return str(self.id)
