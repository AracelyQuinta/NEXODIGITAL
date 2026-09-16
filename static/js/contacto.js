// ==============================================================================
// MÓDULO JS: VALIDACIÓN DEL FORMULARIO DE CONTACTO
// ==============================================================================
// Este script se encarga de:
// 1. Escuchar los eventos del formulario de contacto en tiempo real ('input' y 'blur').
// 2. Validar campos mediante expresiones regulares (Regex) y reglas de longitud.
// 3. Modificar las clases CSS de Bootstrap ('is-valid' / 'is-invalid') para retroalimentación visual.
// 4. Mostrar modales interactivos de Bootstrap ante éxito o error.
// ==============================================================================

document.addEventListener("DOMContentLoaded", () => {
    // Referencia al formulario de contacto
    const formularioContacto = document.getElementById("contactoForm");

    // Si el formulario no está presente en la página actual, salir de forma segura
    if (!formularioContacto) return;

    // Referencias a los campos de entrada
    const nombreContacto = document.getElementById("nombre");
    const correoContacto = document.getElementById("correo");
    const asuntoContacto = document.getElementById("asunto");
    const mensajeContacto = document.getElementById("mensaje");

    // --------------------------------------------------------------------------
    // FUNCIONES DE VALIDACIÓN
    // --------------------------------------------------------------------------

    /**
     * Valida que el nombre contenga al menos 3 caracteres y solo letras/espacios.
     */
    function validarNombreContacto() {
        if (!nombreContacto) return false;
        const valor = nombreContacto.value.trim();
        const patron = /^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]{3,}$/;

        if (!patron.test(valor)) {
            nombreContacto.classList.add("is-invalid");
            nombreContacto.classList.remove("is-valid");
            return false;
        } else {
            nombreContacto.classList.add("is-valid");
            nombreContacto.classList.remove("is-invalid");
            return true;
        }
    }

    /**
     * Valida el formato estándar de correo electrónico (usuario@dominio.extension).
     */
    function validarCorreoContacto() {
        if (!correoContacto) return false;
        const valor = correoContacto.value.trim();
        const patron = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!patron.test(valor)) {
            correoContacto.classList.add("is-invalid");
            correoContacto.classList.remove("is-valid");
            return false;
        } else {
            correoContacto.classList.add("is-valid");
            correoContacto.classList.remove("is-invalid");
            return true;
        }
    }

    /**
     * Valida que el asunto tenga una longitud mínima de 5 caracteres.
     */
    function validarAsuntoContacto() {
        if (!asuntoContacto) return false;
        const valor = asuntoContacto.value.trim();

        if (valor.length < 5) {
            asuntoContacto.classList.add("is-invalid");
            asuntoContacto.classList.remove("is-valid");
            return false;
        } else {
            asuntoContacto.classList.add("is-valid");
            asuntoContacto.classList.remove("is-invalid");
            return true;
        }
    }

    /**
     * Valida que el mensaje contenga al menos 10 caracteres explicativos.
     */
    function validarMensajeContacto() {
        if (!mensajeContacto) return false;
        const valor = mensajeContacto.value.trim();

        if (valor.length < 10) {
            mensajeContacto.classList.add("is-invalid");
            mensajeContacto.classList.remove("is-valid");
            return false;
        } else {
            mensajeContacto.classList.add("is-valid");
            mensajeContacto.classList.remove("is-invalid");
            return true;
        }
    }

    // --------------------------------------------------------------------------
    // ASIGNACIÓN DE EVENTOS EN TIEMPO REAL ('input' y 'blur')
    // --------------------------------------------------------------------------
    [nombreContacto, correoContacto, asuntoContacto, mensajeContacto].forEach(campo => {
        if (!campo) return;
        campo.addEventListener("input", () => {
            if (campo === nombreContacto) validarNombreContacto();
            if (campo === correoContacto) validarCorreoContacto();
            if (campo === asuntoContacto) validarAsuntoContacto();
            if (campo === mensajeContacto) validarMensajeContacto();
        });
        campo.addEventListener("blur", () => {
            if (campo === nombreContacto) validarNombreContacto();
            if (campo === correoContacto) validarCorreoContacto();
            if (campo === asuntoContacto) validarAsuntoContacto();
            if (campo === mensajeContacto) validarMensajeContacto();
        });
    });

    // --------------------------------------------------------------------------
    // PROCESAMIENTO DEL EVENTO 'submit'
    // --------------------------------------------------------------------------
    formularioContacto.addEventListener("submit", function (e) {
        const nombreOk = validarNombreContacto();
        const correoOk = validarCorreoContacto();
        const asuntoOk = validarAsuntoContacto();
        const mensajeOk = validarMensajeContacto();

        // Si algún campo no pasa la validación del navegador, se detiene el envío
        // y se muestra el modal de error (validación del lado del cliente).
        if (!nombreOk || !correoOk || !asuntoOk || !mensajeOk) {
            e.preventDefault();
            const modalEl = document.getElementById("statusErrorsModal");
            if (modalEl && typeof bootstrap !== "undefined") {
                const modalError = bootstrap.Modal.getOrCreateInstance(modalEl);
                modalError.show();
            }
            return;
        }

        // Si todo es válido, NO se previene el envío: el formulario se envía al
        // servidor (ruta /contacto), que guarda la solicitud en la base de datos
        // y muestra un mensaje de confirmación. El servidor es la fuente real.
    });
});
