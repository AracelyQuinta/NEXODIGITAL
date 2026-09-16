# ==============================================================================
# PROYECTO: NEXODIGITAL - MODELO DE USUARIO (Semana 14: autenticación)
# ==============================================================================
# Define la clase 'Usuario' que Flask-Login utiliza para gestionar la sesión.
# Hereda de UserMixin, que aporta automáticamente los métodos que Flask-Login
# necesita (is_authenticated, get_id(), etc.).
#
# En este sistema, todos los usuarios registrados son administradores del panel
# interno (control total). El público general no tiene cuenta: solo ve la parte
# pública del sitio.
# ==============================================================================

from flask_login import UserMixin


class Usuario(UserMixin):
    """
    Representa a un usuario autenticado (administrador) del sistema.

    Atributos:
        id       -> identificador único (clave primaria en la BD).
        usuario  -> nombre de usuario con el que inicia sesión.
        password -> contraseña ya protegida (hash), tal como se guarda en la BD.
    """

    def __init__(self, id, usuario, password):
        self.id = id
        self.usuario = usuario
        self.password = password

    def get_id(self):
        """Flask-Login guarda este id (como texto) en la sesión."""
        return str(self.id)
