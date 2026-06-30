// ===== Formulario de Registro de Solicitudes =====
const formulario = document.getElementById("formSolicitud");
const nombreCliente = document.getElementById("nombreCliente");
const tipoServicio = document.getElementById("tipoServicio");
const descripcionSolicitud = document.getElementById("descripcionSolicitud");
const mensaje = document.getElementById("mensajeValidacion");
const listaSolicitudes = document.getElementById("listaSolicitudes");
const totalSolicitudes = document.getElementById("totalSolicitudes");

// Validación dinámica del campo nombre
function validarNombre() {
    const valor = nombreCliente.value.trim();
    if (valor.length < 3) {
        nombreCliente.classList.add("is-invalid");
        nombreCliente.classList.remove("is-valid");
        return false;
    } else {
        nombreCliente.classList.add("is-valid");
        nombreCliente.classList.remove("is-invalid");
        return true;
    }
}

nombreCliente.addEventListener("input", validarNombre);
nombreCliente.addEventListener("blur", validarNombre);

// Validación dinámica del campo tipo de servicio
function validarServicio() {
    const valor = tipoServicio.value;
    if (valor === "") {
        tipoServicio.classList.add("is-invalid");
        tipoServicio.classList.remove("is-valid");
        return false;
    } else {
        tipoServicio.classList.add("is-valid");
        tipoServicio.classList.remove("is-invalid");
        return true;
    }
}

tipoServicio.addEventListener("input", validarServicio);
tipoServicio.addEventListener("blur", validarServicio);

// Validación dinámica del campo descripción
function validarDescripcion() {
    const valor = descripcionSolicitud.value.trim();
    if (valor.length < 10) {
        descripcionSolicitud.classList.add("is-invalid");
        descripcionSolicitud.classList.remove("is-valid");
        return false;
    } else {
        descripcionSolicitud.classList.add("is-valid");
        descripcionSolicitud.classList.remove("is-invalid");
        return true;
    }
}

descripcionSolicitud.addEventListener("input", validarDescripcion);
descripcionSolicitud.addEventListener("blur", validarDescripcion);

let contadorSolicitudes = 0;

formulario.addEventListener("submit", function (e) {
    e.preventDefault();

    const nombreValido = validarNombre();
    const servicioValido = validarServicio();
    const descripcionValida = validarDescripcion();

    if (!nombreValido || !servicioValido || !descripcionValida) {
        mensaje.innerHTML =
            '<div class="alert alert-danger">Por favor corrige los campos marcados antes de registrar.</div>';
        return;
    }

    const nombre = nombreCliente.value.trim();
    const servicio = tipoServicio.value.trim();
    const descripcion = descripcionSolicitud.value.trim();

    mensaje.innerHTML =
        '<div class="alert alert-success">Solicitud registrada correctamente.</div>';

    const columna = document.createElement("div");
    columna.className = "col-md-6 col-lg-4";

    const tarjeta = document.createElement("div");
    tarjeta.className = "card shadow-sm h-100";

    const cuerpo = document.createElement("div");
    cuerpo.className = "card-body";

    const titulo = document.createElement("h5");
    titulo.className = "card-title";
    titulo.textContent = nombre;

    const subtitulo = document.createElement("h6");
    subtitulo.className = "card-subtitle mb-2 text-muted";
    subtitulo.textContent = servicio;

    const texto = document.createElement("p");
    texto.className = "card-text";
    texto.textContent = descripcion;

    const botonEliminar = document.createElement("button");
    botonEliminar.className = "btn btn-danger btn-sm mt-2";
    botonEliminar.textContent = "Eliminar";

    botonEliminar.addEventListener("click", function () {
        columna.remove();
        contadorSolicitudes--;
        totalSolicitudes.textContent = contadorSolicitudes;
    });

    cuerpo.appendChild(titulo);
    cuerpo.appendChild(subtitulo);
    cuerpo.appendChild(texto);
    cuerpo.appendChild(botonEliminar);

    tarjeta.appendChild(cuerpo);
    columna.appendChild(tarjeta);
    listaSolicitudes.appendChild(columna);

    contadorSolicitudes++;
    totalSolicitudes.textContent = contadorSolicitudes;

    formulario.reset();
    nombreCliente.classList.remove("is-valid", "is-invalid");
    tipoServicio.classList.remove("is-valid", "is-invalid");
    descripcionSolicitud.classList.remove("is-valid", "is-invalid");
});


// ===== Formulario de Contacto =====
const formularioContacto = document.querySelector('#contacto form');
const nombreContacto = document.getElementById("nombre");
const correoContacto = document.getElementById("correo");
const asuntoContacto = document.getElementById("asunto");
const mensajeContacto = document.getElementById("mensaje");

function validarNombreContacto() {
    const valor = nombreContacto.value.trim();
    if (valor.length < 3) {
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

nombreContacto.addEventListener("input", validarNombreContacto);
nombreContacto.addEventListener("blur", validarNombreContacto);

correoContacto.addEventListener("input", validarCorreoContacto);
correoContacto.addEventListener("blur", validarCorreoContacto);

asuntoContacto.addEventListener("input", validarAsuntoContacto);
asuntoContacto.addEventListener("blur", validarAsuntoContacto);

mensajeContacto.addEventListener("input", validarMensajeContacto);
mensajeContacto.addEventListener("blur", validarMensajeContacto);

formularioContacto.addEventListener("submit", function (e) {
    e.preventDefault();

    const nombreOk = validarNombreContacto();
    const correoOk = validarCorreoContacto();
    const asuntoOk = validarAsuntoContacto();
    const mensajeOk = validarMensajeContacto();

    if (!nombreOk || !correoOk || !asuntoOk || !mensajeOk) {
        return;
    }

    alert("¡Mensaje enviado correctamente! Te contactaremos pronto.");
    formularioContacto.reset();
    nombreContacto.classList.remove("is-valid", "is-invalid");
    correoContacto.classList.remove("is-valid", "is-invalid");
    asuntoContacto.classList.remove("is-valid", "is-invalid");
    mensajeContacto.classList.remove("is-valid", "is-invalid");
});