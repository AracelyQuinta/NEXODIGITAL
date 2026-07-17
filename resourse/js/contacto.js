// ===== Formulario de Contacto =====
const formularioContacto = document.getElementById("contactoForm");
const resultado = document.getElementById("resultado");

const nombreContacto = document.getElementById("nombre");
const correoContacto = document.getElementById("correo");
const asuntoContacto = document.getElementById("asunto");
const mensajeContacto = document.getElementById("mensaje");

// Validaciones dinámicas
function validarNombreContacto() {
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

function validarCorreoContacto() {
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

function validarAsuntoContacto() {
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

function validarMensajeContacto() {
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

// Eventos dinámicos
[nombreContacto, correoContacto, asuntoContacto, mensajeContacto].forEach(campo => {
    campo.addEventListener("input", () => {
        if (campo === nombreContacto) validarNombreContacto();
        if (campo === correoContacto) validarCorreoContacto();
        if (campo === asuntoContacto) validarAsuntoContacto();
        if (campo === mensajeContacto) validarMensajeContacto();
    });
});

// Submit con alerta + mensaje en pantalla
formularioContacto.addEventListener("submit", function (e) {
    e.preventDefault();

    const nombreOk = validarNombreContacto();
    const correoOk = validarCorreoContacto();
    const asuntoOk = validarAsuntoContacto();
    const mensajeOk = validarMensajeContacto();

    // Actualizacion semana 7
/*
    if (!nombreOk || !correoOk || !asuntoOk || !mensajeOk) {
        resultado.innerHTML = `<div class="alert alert-danger">❌ Por favor corrige los campos marcados.</div>`;
        return;
    }
    //  Alerta emergente
    alert("¡Mensaje enviado correctamente! Te contactaremos pronto.");

    //  Mensaje visible en pantalla
    resultado.innerHTML = `<div class="alert alert-success">✅ Mensaje capturado correctamente. ¡Gracias ${nombreContacto.value.trim()}!</div>`;
*/

        if (!nombreOk || !correoOk || !asuntoOk || !mensajeOk) {
      let modalError = new bootstrap.Modal(document.getElementById("statusErrorsModal"));
      modalError.show();
      return;
    }

    let modalExito = new bootstrap.Modal(document.getElementById("statusSuccessModal"));
    modalExito.show();

    // Limpiar formulario
    formularioContacto.reset();
    [nombreContacto, correoContacto, asuntoContacto, mensajeContacto].forEach(campo => {
        campo.classList.remove("is-valid", "is-invalid");
    });
});
