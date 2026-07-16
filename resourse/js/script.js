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

// arreglo para solicitudes
let solicitudes = [];

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

    solicitudes.push({ nombre, servicio, descripcion }); //guarda en el arreglo

    mensaje.innerHTML =
        '<div class="alert alert-success">Solicitud registrada correctamente.</div>';

    mostrarSolicitudes(); // renderizacion de todo el arreglo

    formulario.reset();
    nombreCliente.classList.remove("is-valid", "is-invalid");
    tipoServicio.classList.remove("is-valid", "is-invalid");
    descripcionSolicitud.classList.remove("is-valid", "is-invalid");
});


// ===== Muestra la solicitudes =====
function mostrarSolicitudes() {
  listaSolicitudes.innerHTML = "";

  if (solicitudes.length === 0) {
    listaSolicitudes.innerHTML = "<p class='text-danger'>No hay solicitudes registradas.</p>";
    totalSolicitudes.textContent = 0;
    return;
  }

  solicitudes.forEach((sol, index) => {
    const columna = document.createElement("div");
    columna.className = "col-md-6 col-lg-4";

    const tarjeta = document.createElement("div");
    tarjeta.className = "card shadow-sm h-100";

    tarjeta.innerHTML = `
      <div class="card-body">
        <h5 class="card-title">${sol.nombre}</h5>
        <h6 class="card-subtitle mb-2 text-muted">${sol.servicio}</h6>
        <p class="card-text">${sol.descripcion}</p>
        <button class="btn btn-danger btn-sm mt-2" onclick="eliminarSolicitud(${index})">Eliminar</button>
      </div>
    `;

    columna.appendChild(tarjeta);
    listaSolicitudes.appendChild(columna);
  });

  totalSolicitudes.textContent = solicitudes.length;
}


// ===== Elimina solicitudes =====
function eliminarSolicitud(index) {
    solicitudes.splice(index, 1); // elimina del arreglo
    mostrarSolicitudes();         // vuelve a renderizar
}


