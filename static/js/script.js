// ==============================================================================
// MÓDULO JS: REGISTRO DINÁMICO DE SOLICITUDES (DOM & LOCALSTORAGE)
// ==============================================================================
// Este script gestiona el módulo interactivo de solicitudes rápidas de clientes.
// Funcionalidades clave:
// 1. Manipulación directa del DOM (creación dinámica de tarjetas HTML).
// 2. Persistencia en el navegador mediante la Web Storage API ('localStorage').
// 3. Validación de formularios en el lado del cliente (Frontend).
// 4. Retroalimentación visual asíncrona con spinner de carga y modales de Bootstrap.
// 5. Operaciones de adición y eliminación de elementos en tiempo real.
// ==============================================================================

document.addEventListener("DOMContentLoaded", () => {
    // Referencia al formulario de solicitudes
    const formulario = document.getElementById("formSolicitud");

    // Si el formulario no existe en la página actual, salir de forma segura
    if (!formulario) return;

    // Referencias a los elementos del DOM
    const nombreCliente = document.getElementById("nombreCliente");
    const tipoServicio = document.getElementById("tipoServicio");
    const descripcionSolicitud = document.getElementById("descripcionSolicitud");
    const listaSolicitudes = document.getElementById("listaSolicitudes");
    const totalSolicitudes = document.getElementById("totalSolicitudes");
    const spinner = document.getElementById("spinnerCarga");

    // Clave de almacenamiento en localStorage
    const STORAGE_KEY = "nexodigital_solicitudes";

    // Datos iniciales de demostración si localStorage está vacío
    const ejemplosIniciales = [
        {
            nombre: "Restaurante Sabor Amazónico",
            servicio: "Menú QR",
            descripcion: "Necesitamos digitalizar nuestra carta de platos típicos con código QR para las mesas."
        },
        {
            nombre: "Consultora Contable Gómez",
            servicio: "Página web",
            descripcion: "Sitio web corporativo de 4 secciones con botón directo a WhatsApp."
        }
    ];

    // Cargar datos almacenados previamente o inicializar con los ejemplos
    let solicitudes = [];
    try {
        const dataGuardada = localStorage.getItem(STORAGE_KEY);
        if (dataGuardada) {
            solicitudes = JSON.parse(dataGuardada);
        } else {
            solicitudes = ejemplosIniciales;
            localStorage.setItem(STORAGE_KEY, JSON.stringify(solicitudes));
        }
    } catch (e) {
        solicitudes = ejemplosIniciales;
    }

    // --------------------------------------------------------------------------
    // FUNCIONES DE VALIDACIÓN INDIVIDUAL DE CAMPOS
    // --------------------------------------------------------------------------

    /**
     * Valida que el nombre del cliente contenga al menos 3 caracteres alfabéticos.
     */
    function validarNombre() {
        if (!nombreCliente) return false;
        const valor = nombreCliente.value.trim();
        const patron = /^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]{3,}$/;

        if (!patron.test(valor)) {
            nombreCliente.classList.add("is-invalid");
            nombreCliente.classList.remove("is-valid");
            return false;
        } else {
            nombreCliente.classList.add("is-valid");
            nombreCliente.classList.remove("is-invalid");
            return true;
        }
    }

    /**
     * Valida que se haya seleccionado un tipo de servicio de la lista desplegable.
     */
    function validarServicio() {
        if (!tipoServicio) return false;
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

    /**
     * Valida que la descripción contenga al menos 10 caracteres explicativos.
     */
    function validarDescripcion() {
        if (!descripcionSolicitud) return false;
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

    // --------------------------------------------------------------------------
    // ESCUCHADORES DE EVENTOS DE VALIDACIÓN ('input', 'change', 'blur')
    // --------------------------------------------------------------------------
    if (nombreCliente) {
        nombreCliente.addEventListener("input", validarNombre);
        nombreCliente.addEventListener("blur", validarNombre);
    }

    if (tipoServicio) {
        tipoServicio.addEventListener("change", validarServicio);
        tipoServicio.addEventListener("blur", validarServicio);
    }

    if (descripcionSolicitud) {
        descripcionSolicitud.addEventListener("input", validarDescripcion);
        descripcionSolicitud.addEventListener("blur", validarDescripcion);
    }

    // --------------------------------------------------------------------------
    // RENDERIZADO DE LAS TARJETAS DE SOLICITUDES EN EL DOM
    // --------------------------------------------------------------------------
    /**
     * Limpia y vuelve a generar los elementos visuales de las solicitudes activas.
     */
    window.mostrarSolicitudes = function () {
        if (!listaSolicitudes || !totalSolicitudes) return;

        // Limpiar el contenedor
        listaSolicitudes.innerHTML = "";

        // Si no hay solicitudes, mostrar estado vacío
        if (solicitudes.length === 0) {
            listaSolicitudes.innerHTML = `
                <div class="col-12">
                    <div class="card p-4 text-center border-0 bg-light rounded-4">
                        <i class="bi bi-inbox text-muted fs-1 mb-2"></i>
                        <p class="text-muted mb-0">No hay solicitudes registradas en este momento.</p>
                    </div>
                </div>
            `;
            totalSolicitudes.textContent = "0";
            return;
        }

        // Iterar y crear cada tarjeta de solicitud
        solicitudes.forEach((sol, index) => {
            const columna = document.createElement("div");
            columna.className = "col-md-6 col-lg-4";

            columna.innerHTML = `
                <div class="card h-100 shadow-sm border-0 rounded-4 overflow-hidden">
                    <div class="card-body p-4 d-flex flex-column">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <span class="badge bg-emerald-subtle text-emerald fw-semibold px-2 py-1 small rounded-pill">
                                <i class="bi bi-tag-fill me-1"></i>${sol.servicio}
                            </span>
                            <button type="button" class="btn btn-outline-danger btn-sm rounded-circle" style="width: 32px; height: 32px; padding: 0;" title="Eliminar solicitud" onclick="eliminarSolicitud(${index})">
                                <i class="bi bi-trash-fill"></i>
                            </button>
                        </div>
                        <h5 class="card-title fw-bold text-navy mb-2">${sol.nombre}</h5>
                        <p class="card-text text-muted small flex-grow-1 mb-3">${sol.descripcion}</p>
                        <div class="pt-2 border-top d-flex justify-content-between align-items-center">
                            <small class="text-muted"><i class="bi bi-clock-history me-1"></i>Registrado</small>
                            <span class="badge bg-navy text-white small px-2 py-1">En revisión</span>
                        </div>
                    </div>
                </div>
            `;

            listaSolicitudes.appendChild(columna);
        });

        // Actualizar el contador total en el encabezado
        totalSolicitudes.textContent = solicitudes.length.toString();
    };

    // --------------------------------------------------------------------------
    // FUNCIÓN PARA ELIMINAR UNA SOLICITUD
    // --------------------------------------------------------------------------
    /**
     * Elimina una solicitud del arreglo según su posición y sincroniza con localStorage.
     */
    window.eliminarSolicitud = function (index) {
        if (confirm("¿Estás seguro de que deseas eliminar esta solicitud?")) {
            solicitudes.splice(index, 1);
            try {
                localStorage.setItem(STORAGE_KEY, JSON.stringify(solicitudes));
            } catch (e) {
                console.error("No se pudo guardar en localStorage", e);
            }
            mostrarSolicitudes();
        }
    };

    // --------------------------------------------------------------------------
    // PROCESAMIENTO DEL ENVÍO DEL FORMULARIO DE SOLICITUD
    // --------------------------------------------------------------------------
    formulario.addEventListener("submit", function (e) {
        e.preventDefault();

        const nombreValido = validarNombre();
        const servicioValido = validarServicio();
        const descripcionValida = validarDescripcion();

        // Si algún campo no es válido, mostrar modal de advertencia
        if (!nombreValido || !servicioValido || !descripcionValida) {
            const errorModalEl = document.getElementById("solicitudErrorModal");
            if (errorModalEl && typeof bootstrap !== "undefined") {
                bootstrap.Modal.getOrCreateInstance(errorModalEl).show();
            }
            return;
        }

        // Mostrar indicador de carga (spinner)
        if (spinner) spinner.classList.remove("d-none");

        // Simular un tiempo de respuesta de guardado
        setTimeout(() => {
            if (spinner) spinner.classList.add("d-none");

            // Crear objeto con los datos de la nueva solicitud
            const nuevaSolicitud = {
                nombre: nombreCliente.value.trim(),
                servicio: tipoServicio.value.trim(),
                descripcion: descripcionSolicitud.value.trim()
            };

            // Añadir al inicio de la lista
            solicitudes.unshift(nuevaSolicitud);

            // Persistir en localStorage
            try {
                localStorage.setItem(STORAGE_KEY, JSON.stringify(solicitudes));
            } catch (e) {
                console.error("No se pudo guardar en localStorage", e);
            }

            // Actualizar vista en pantalla
            mostrarSolicitudes();

            // Mostrar modal de confirmación exitosa
            const successModalEl = document.getElementById("solicitudSuccessModal");
            if (successModalEl && typeof bootstrap !== "undefined") {
                bootstrap.Modal.getOrCreateInstance(successModalEl).show();
            }

            // Limpiar formulario y remover clases visuales
            formulario.reset();
            [nombreCliente, tipoServicio, descripcionSolicitud].forEach(campo => {
                if (campo) campo.classList.remove("is-valid", "is-invalid");
            });
        }, 500);
    });

    // Renderizar solicitudes iniciales al cargar la página
    mostrarSolicitudes();
});
