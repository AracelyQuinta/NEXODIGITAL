# ==============================================================================
# PAQUETE FORMS - NEXODIGITAL
# ==============================================================================
# Este archivo convierte el directorio 'forms' en un paquete Python importable.
# Expone las clases de formularios construidas sobre Flask-WTF / WTForms para
# facilitar su importación directa en app.py y otros módulos del proyecto.
# ==============================================================================

from forms.cliente_form import ClienteForm
from forms.servicio_form import ServicioForm
from forms.proveedor_form import ProveedorForm
from forms.facturacion_form import FacturacionForm

__all__ = ['ClienteForm', 'ServicioForm', 'ProveedorForm', 'FacturacionForm']
