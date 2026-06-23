const formulario = document.getElementById("formSolicitud");
const nombreCliente = document.getElementById("nombreCliente");
const tipoServicio = document.getElementById("tipoServicio");
const descripcionSolicitud = document.getElementById("descripcionSolicitud");
const mensaje = document.getElementById("mensajeValidacion");
const listaSolicitudes = document.getElementById("listaSolicitudes");
const totalSolicitudes = document.getElementById("totalSolicitudes");

let contadorSolicitudes = 0;

formulario.addEventListener("submit", function (e) {
    e.preventDefault();

    const nombre = nombreCliente.value.trim();
    const servicio = tipoServicio.value.trim();
    const descripcion = descripcionSolicitud.value.trim();

    if (nombre === "" || servicio === "" || descripcion === "") {
        mensaje.innerHTML =
            '<div class="alert alert-danger">Todos los campos son obligatorios.</div>';
        return;
    }

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
});
