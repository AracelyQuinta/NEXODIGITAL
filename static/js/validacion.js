// ==============================================================================
// PROYECTO: NEXODIGITAL - VALIDACIÓN EN VIVO DE FORMULARIOS (Semana 14)
// ==============================================================================
// Muestra mensajes de ayuda MIENTRAS el usuario escribe, sin esperar al botón.
// Es una ayuda visual del lado del cliente (navegador). La validación de verdad
// sigue en el servidor con Flask-WTF; esto solo mejora la experiencia.
// ==============================================================================

document.addEventListener('DOMContentLoaded', function () {

    // ------------------------------------------------------------------
    // Utilidad: muestra u oculta un mensaje de error bajo un campo.
    // ------------------------------------------------------------------
    function marcarError(campo, mensaje) {
        campo.classList.add('is-invalid');
        campo.classList.remove('is-valid');
        // Buscar o crear el contenedor del mensaje justo después del campo.
        let feedback = campo.parentElement.querySelector('.invalid-feedback.js-feedback');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback js-feedback d-block';
            campo.parentElement.appendChild(feedback);
        }
        feedback.textContent = mensaje;
        feedback.style.display = 'block';
    }

    function marcarOk(campo) {
        campo.classList.remove('is-invalid');
        campo.classList.add('is-valid');
        const feedback = campo.parentElement.querySelector('.invalid-feedback.js-feedback');
        if (feedback) feedback.style.display = 'none';
    }

    function limpiar(campo) {
        campo.classList.remove('is-invalid', 'is-valid');
        const feedback = campo.parentElement.querySelector('.invalid-feedback.js-feedback');
        if (feedback) feedback.style.display = 'none';
    }

    // ------------------------------------------------------------------
    // Campo USUARIO: mínimo 3 caracteres.
    // ------------------------------------------------------------------
    const usuario = document.getElementById('usuario');
    if (usuario) {
        usuario.addEventListener('input', function () {
            const v = usuario.value.trim();
            if (v.length === 0) { limpiar(usuario); return; }
            if (v.length < 3) {
                marcarError(usuario, 'El usuario debe tener al menos 3 caracteres.');
            } else {
                marcarOk(usuario);
            }
        });
    }

    // ------------------------------------------------------------------
    // Campo CONTRASEÑA: mínimo 4 caracteres.
    // ------------------------------------------------------------------
    const password = document.getElementById('password');
    if (password) {
        password.addEventListener('input', function () {
            const v = password.value;
            if (v.length === 0) { limpiar(password); return; }
            if (v.length < 4) {
                marcarError(password, 'La contraseña debe tener al menos 4 caracteres.');
            } else {
                marcarOk(password);
            }
            // Si ya hay algo escrito en confirmar, revalidar la coincidencia.
            if (confirmar && confirmar.value.length > 0) comprobarCoincidencia();
        });
    }

    // ------------------------------------------------------------------
    // Campo CONFIRMAR: debe coincidir con la contraseña.
    // ------------------------------------------------------------------
    const confirmar = document.getElementById('confirmar');
    function comprobarCoincidencia() {
        if (!confirmar) return;
        const v = confirmar.value;
        if (v.length === 0) { limpiar(confirmar); return; }
        if (password && v !== password.value) {
            marcarError(confirmar, 'Las contraseñas no coinciden.');
        } else {
            marcarOk(confirmar);
        }
    }
    if (confirmar) {
        confirmar.addEventListener('input', comprobarCoincidencia);
    }

});
