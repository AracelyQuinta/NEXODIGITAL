# UNIVERSIDAD ESTATAL AMAZÓNICA
## FACULTAD DE CIENCIAS DE LA TIERRA
### CARRERA DE TECNOLOGÍAS DE LA INFORMACIÓN

---

# INFORME TÉCNICO Y DOCUMENTACIÓN DEL PROYECTO INTEGRADOR
## TAREAS SEMANA 14 Y SEMANA 15: SISTEMA DE AUTENTICACIÓN, BASE DE DATOS RELACIONAL POSTGRESQL Y CONTROL DE ACCESO BASADO EN ROLES (RBAC)

**Asignatura:** Desarrollo de Aplicaciones Web  
**Nivel Académico:** Cuarto Semestre  
**Período Académico:** 2025 - 2026  
**Proyecto:** Plataforma Web y Sistema de Gestión Comercial "NexoDigital"  

**Integrantes del Equipo de Desarrollo:**
1. **Cinthia Mishel Carrión Serrano**
2. **Aracely Maribel Quintanilla Rumipamba**
3. **Santiago Andrés Lara Caicedo**

**Repositorio del Proyecto:** [GitHub - NexoDigital](https://github.com/AracelyQuinta/NEXODIGITAL)  
**Entorno de Ejecución:** Python 3.11+ / Flask 3.1 / PostgreSQL 14+ / Bootstrap 5.3  

---

## 1. INTRODUCCIÓN Y CONTEXTO DEL PROYECTO

El presente documento recopila de manera integral la arquitectura técnica, diseño de base de datos, implementación de código y validación experimental del sistema web **NexoDigital**. 

NexoDigital es una solución tecnológica desarrollada para impulsar la presencia en internet de microempresas, comercios y profesionales independientes en el Ecuador. La plataforma conjuga un **portal web institucional público** orientado a la captación y presentación comercial de servicios digitales, con un **panel de gestión administrativa (Backoffice)** protegido para la administración de clientes, proveedores, facturación, cotizaciones, analítica de demanda y auditoría de accesos.

En cumplimiento con los requerimientos pedagógicos y curriculares de las **Semanas 14 y 15**, se han integrado:
1. **Semana 14:** Sistema de autenticación de usuarios funcional, almacenamiento seguro de contraseñas mediante hashing criptográfico, persistencia de sesión con Flask-Login, protección de rutas y cierre de sesión.
2. **Semana 15:** Base de datos relacional PostgreSQL con relaciones de claves foráneas, operaciones CRUD completas, consultas complejas con cláusulas JOIN entre 2 y más de 3 tablas para la toma de decisiones, y páginas de error corporativas personalizadas (404, 403, 500).
3. **Ampliación RBAC y Reglas de Negocio:** Sistema de Control de Acceso Basado en Roles (5 roles), IDs automáticos en todas las tablas, clave primaria compuesta en la tabla asociativa `rol_permisos`, 27 permisos granulares, reglas comerciales reforzadas para clientes, flujo de aprobación administrativa de cuentas y trazabilidad total con logs de auditoría.

---

## 2. DESARROLLO DE LA TAREA SEMANA 14: SISTEMA DE AUTENTICACIÓN FUNCIONAL

### 2.1. Registro de Usuarios y Prevención Anti-Bot
El registro de usuarios se implementó en el módulo `forms/usuario_form.py` utilizando **Flask-WTF** y **WTForms**. El formulario captura:
- Nombre de usuario único (`Length(min=3, max=50)`).
- Correo electrónico obligatorio con validación de sintaxis (`Email()`).
- Rol solicitado en el sistema (`SelectField`).
- Contraseña y confirmación de contraseña (`EqualTo()`).
- **Mecanismo CAPTCHA Aritmético Dinámico:** Generado aleatoriamente en el servidor en cada petición (`generar_captcha()`) y verificado contra la sesión antes de procesar el registro, impidiendo la creación masiva de cuentas mediante scripts automatizados o bots maliciosos.

### 2.2. Hashing Criptográfico de Contraseñas (Bcrypt)
En cumplimiento estricto con el principio de que ninguna contraseña debe almacenarse en texto plano:
- Se implementó la librería `bcrypt` en `models.py` (`User.hash_password()`).
- Cada contraseña es transformada con un costo de trabajo (*work factor*) estándar y una semilla criptográfica (*salt*) única de 128 bits generada por el algoritmo Blowfish:
  $$\text{Hash} = \text{Bcrypt}(\text{password}, \text{salt})$$
- La verificación en el inicio de sesión (`User.check_password()`) utiliza comparación en tiempo constante para evitar ataques de temporización (*timing attacks*), admitiendo además verificación por fallback mediante `werkzeug.security` para cuentas legacy.

### 2.3. Gestión de Sesiones y Protección de Rutas (Flask-Login)
- **Inicio de Sesión:** Manejado a través de `login_user(user, remember=...)` en la ruta `/login`. El usuario puede autenticarse indistintamente mediante su **nombre de usuario** o su **correo electrónico**.
- **Sesión Permanente y Caducidad Automática:** Se configuró una ventana de expiración por inactividad de 30 minutos:
  ```python
  app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
  ```
- **Protección de Rutas Privadas:** Todas las rutas internas están decoradas con `@login_required` o con los decoradores personalizados `@role_required` y `@permission_required`. Si un usuario anónimo intenta acceder directamente por URL a `/dashboard`, `/clientes`, `/facturacion`, `/proveedores` o `/estadisticas`, el sistema intercepta la petición, lo redirige a `/login` y almacena el parámetro `next` para retornarlo a su destino original una vez autenticado.
- **Cierre de Sesión Seguro:** La ruta `/logout` destruye la sesión con `logout_user()`, borra las cookies asociadas, registra el evento en los logs de auditoría y redirige a la pantalla de bienvenida.

### 2.4. Seguridad Adicional: Autenticación en Dos Pasos (2FA) y Confirmación de Correo
- **2FA / OTP:** Si el usuario activa la verificación en dos pasos, tras ingresar la contraseña correcta el sistema genera un código numérico temporal de 6 dígitos almacenado de forma efímera y redirige a `/verificar-2fa`.
- **Confirmación de Correo Electrónico:** Simulación funcional de verificación mediante tokens por URL (`/confirmar-email/<token>`), actualizando la columna `email_confirmado = TRUE` en PostgreSQL.

---

## 3. DESARROLLO DE LA TAREA SEMANA 15: BASE DE DATOS RELACIONAL POSTGRESQL Y CONSULTAS AVANZADAS

### 3.1. Arquitectura de Conexión Centralizada
El archivo `conexion/conexion.py` implementa el patrón de conexión centralizado mediante `psycopg2-binary` y `psycopg2.extras.RealDictCursor` (retornando filas como diccionarios clave-valor accesibles por nombre de columna).

Es compatible tanto con el entorno de desarrollo local (mediante variables `.env` individuales: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`) como con entornos de producción en la nube como **Render**, **Neon** o **Supabase** mediante la variable estandarizada `DATABASE_URL`:

```python
def get_db_connection():
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        return psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    # Fallback a credenciales locales
    return psycopg2.connect(...)
```

### 3.2. Modelo Relacional y Normalización
La base de datos cuenta con **14 tablas relacionales** diseñadas bajo la Tercera Forma Normal (3FN), asegurando la integridad referencial y eliminando anomalías de redundancia:

```
  ┌──────────────────┐            ┌──────────────────┐
  │  tipos_negocio   │ 1        N │     clientes     │
  │──────────────────│────────────│──────────────────│
  │ id (PK)          │            │ id (UNIQUE)      │
  │ nombre           │            │ cedula (PK)      │
  └──────────────────┘            │ tipo_negocio_id  │
                                  └─────────┬────────┘
                                            │ 1
                                            │ N
  ┌──────────────────┐            ┌─────────▼────────┐
  │ estados_documento│ 1        N │   facturacion    │
  │──────────────────│────────────│──────────────────│
  │ id (PK)          │            │ id (UNIQUE)      │
  │ nombre           │            │ numero (PK)      │
  └──────────────────┘            │ cliente_cedula   │
                                  │ estado_id        │
                                  └─────────┬────────┘
                                            │ 1
                                            │ N
  ┌──────────────────┐            ┌─────────▼────────┐
  │  tipos_servicio  │ 1        N │ detalle_factura  │
  │──────────────────│────────────│──────────────────│
  │ id (PK)          │            │ id (PK)          │
  │ nombre           │            │ factura_numero   │
  └────────┬─────────┘            │ servicio_id (FK) │
           │ 1                    │ cantidad, total  │
           │ N                    └─────────▲────────┘
  ┌────────▼─────────┐                      │
  │    servicios     │ 1                    │ N
  │──────────────────│──────────────────────┘
  │ id (PK)          │
  │ tipo_servicio_id │
  │ precio_base      │
  │ disponible       │
  └──────────────────┘
```

### 3.3. IDs Automáticos en Todas las Tablas
Para cumplir con el estándar corporativo de identificación unívoca:
- Todas las tablas maestras y secundarias poseen claves primarias autoincrementales (`id SERIAL PRIMARY KEY`).
- En tablas con identificadores tributarios o comerciales (`clientes` con `cedula VARCHAR(20)` y `facturacion` con `numero VARCHAR(30)`), se integró adicionalmente una columna única `id SERIAL UNIQUE`:
  ```sql
  ALTER TABLE clientes ADD COLUMN IF NOT EXISTS id SERIAL UNIQUE;
  ALTER TABLE facturacion ADD COLUMN IF NOT EXISTS id SERIAL UNIQUE;
  ```
- La tabla intermedia `detalle_factura` cuenta con su respectivo `id SERIAL PRIMARY KEY`.

### 3.4. Consultas con Relaciones y Cláusulas JOIN

#### A. Panel de Toma de Decisiones y Ranking de Demanda (`/estadisticas`)
Cumple con creces el requisito de consulta relacional multicapa, vinculando 3 tablas (`detalle_factura`, `servicios` y `tipos_servicio`) mediante agregaciones `SUM()` y agrupamiento:

```sql
SELECT s.nombre AS servicio,
       t.nombre AS categoria,
       SUM(d.cantidad) AS unidades,
       SUM(d.total)    AS ingresos
FROM detalle_factura d
JOIN servicios s      ON d.servicio_id = s.id
JOIN tipos_servicio t ON s.tipo_servicio_id = t.id
GROUP BY s.nombre, t.nombre
ORDER BY unidades DESC;
```

#### B. Directorio de Proveedores Tecnológicos (`/proveedores`)
Combina 3 tablas (`proveedores`, `estados_proveedor` y `categorias_proveedor`) para mostrar nombres legibles en lugar de códigos foráneos:

```sql
SELECT p.*, e.nombre AS estado_nombre, c.nombre AS categoria_nombre
FROM proveedores p
JOIN estados_proveedor e ON p.estado_id = e.id
JOIN categorias_proveedor c ON p.categoria_id = c.id;
```

#### C. Directorio de Clientes Comerciales (`/clientes`)
Combina `clientes` con `tipos_negocio` mediante `clientes.tipo_negocio_id = tipos_negocio.id`.

#### D. Comprobantes de Facturación (`/facturacion/comprobante/<numero>`)
Relaciona `facturacion`, `clientes`, `estados_documento` y `detalle_factura` para la reconstrucción completa del comprobante comercial.

### 3.5. Páginas de Error Personalizadas (404, 403, 500)
Se diseñaron manejadores de error en `app.py` que renderizan vistas corporativas dentro de `templates/base.html`, manteniendo el menú superior, el pie de página institucional y mensajes claros de resolución para el usuario:
- **Error 404 (`templates/404.html`):** Notifica página o recurso no encontrado, ofreciendo botón de retorno al inicio o dashboard.
- **Error 403 (`templates/403.html`):** Notifica acceso denegado por insuficiencia de permisos o rol.
- **Error 500 (`templates/500.html`):** Notifica interrupción técnica en el servidor sin exponer trazas de código o datos sensibles.

---

## 4. SISTEMA DE ROLES, PERMISOS Y REGLAS DE NEGOCIO (RBAC)

### 4.1. Definición de la Tabla Intermedia `rol_permisos` con PRIMARY KEY Compuesta
Para evitar la duplicación de permisos por rol a nivel de base de datos y garantizar la máxima velocidad de indexación, la tabla intermedia relacional `rol_permisos` se definió con **clave primaria compuesta**:

```sql
CREATE TABLE rol_permisos (
    rol_id INT NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permiso_id INT NOT NULL REFERENCES permisos(id) ON DELETE CASCADE,
    PRIMARY KEY (rol_id, permiso_id)
);
```

### 4.2. Catálogo de Permisos Granulares (27 Permisos)
La tabla `permisos` categoriza las acciones permitidas desglosadas por módulo:

| Módulo | Códigos de Permiso Granular |
|---|---|
| **Servicios** | `servicios.ver`, `servicios.crear`, `servicios.editar`, `servicios.eliminar`, `servicios.futuros` |
| **Clientes** | `clientes.ver`, `clientes.crear`, `clientes.editar`, `clientes.eliminar`, `clientes.sensible`, `clientes.propio` |
| **Facturas** | `facturas.ver`, `facturas.crear`, `facturas.editar`, `facturas.eliminar`, `facturas.ver_propias` |
| **Proveedores** | `proveedores.ver`, `proveedores.crear`, `proveedores.editar`, `proveedores.eliminar` |
| **Usuarios** | `usuarios.ver`, `usuarios.crear`, `usuarios.editar`, `usuarios.eliminar`, `usuarios.aprobar` |
| **Reportes** | `reportes.ver`, `reportes.financiero` |

### 4.3. Matriz de Roles y Asignaciones

```
┌─────────────────────────────────┬──────┬──────┬──────┬──────┬─────────┐
│ Módulo / Permiso                │ Admin│ Gest │ Sopo │ Usua │ Cliente │
├─────────────────────────────────┼──────┼──────┼──────┼──────┼─────────┤
│ Catálogo de Servicios (ver)     │  SI  │  SI  │  SI  │  SI  │   SI    │
│ Catálogo de Servicios (crear/ed)│  SI  │  SI  │  NO  │  NO  │   NO    │
│ Catálogo de Servicios (eliminar)│  SI  │  NO  │  NO  │  NO  │   NO    │
│ Ver Servicios Futuros (Próximos)│  SI  │  SI  │  SI  │  SI  │   SI    │
│ Clientes (ver cartera general)  │  SI  │  SI  │  NO  │  SI  │   NO    │
│ Clientes (crear / editar)       │  SI  │  SI  │  NO  │  NO  │   NO    │
│ Clientes (datos sensibles)      │  SI  │  SI  │  NO  │  NO  │   NO    │
│ Clientes (ficha propia)         │  SI  │  NO  │  NO  │  NO  │   SI    │
│ Facturas (ver todas)            │  SI  │  SI  │  NO  │  NO  │   NO    │
│ Facturas (crear / emitir)       │  SI  │  SI  │  NO  │  NO  │   NO    │
│ Facturas (editar)               │  SI  │  SI  │  NO  │  NO  │   NO    │
│ Facturas (eliminar)             │  SI  │  NO  │  NO  │  NO  │   NO    │
│ Facturas (ver propias emitidas) │  SI  │  SI  │  NO  │  NO  │   SI    │
│ Proveedores (ver directorio)    │  SI  │  NO  │  SI  │  NO  │   NO    │
│ Proveedores (crear / editar)    │  SI  │  NO  │  SI  │  NO  │   NO    │
│ Proveedores (eliminar)          │  SI  │  NO  │  NO  │  NO  │   NO    │
│ Usuarios y Roles (administrar)  │  SI  │  NO  │  NO  │  NO  │   NO    │
│ Usuarios (aprobar nuevos admin) │  SI  │  NO  │  NO  │  NO  │   NO    │
│ Estadísticas (ranking demanda)  │  SI  │  SI  │  NO  │  NO  │   SI    │
│ Estadísticas (ingresos totales) │  SI  │  SI  │  NO  │  NO  │   NO    │
└─────────────────────────────────┴──────┴──────┴──────┴──────┴─────────┘
```

### 4.4. Reglas de Negocio Implementadas

#### Regla 1: Acceso Público vs. Miembros Registrados
- **Página Principal (`/`):** Accesible públicamente tanto para usuarios autenticados como para visitantes no registrados.
- **Catálogo de Servicios (`/servicios`):**
  - Visitantes anónimos solo visualizan servicios marcados como disponibles (`disponible = TRUE`).
  - Los usuarios con sesión iniciada (incluyendo el rol `Cliente`) visualizan adicionalmente los **servicios en desarrollo o futuros** con el distintivo gráfico `"Próximamente (Servicio Futuro)"`.

#### Regla 2: Blindaje Comercial para el Rol "Cliente"
- **Prohibición de Emitir/Editar Facturas:** Un Cliente no puede crear, editar ni eliminar facturas o cotizaciones. Los endpoints `/facturacion/nueva`, `/facturacion/editar` y `/facturacion/eliminar` rechazan cualquier intento con un error 403 / redirección preventiva, y los botones de acción se ocultan de su interfaz.
- **Consulta Exclusiva de Comprobantes Propios:** En `/facturacion/comprobante/<numero>`, el servidor verifica que el documento pertenezca al cliente en sesión (mediante correo, cédula o razón social). Si intenta consultar un comprobante ajeno alterando el número en la URL, se bloquea el acceso y se audita el evento como `ACCESO_DENEGADO_COMPROBANTE`.
- **Ocultamiento de Proveedores:** La vista `/proveedores` está restringida para el Cliente.
- **Ranking de Servicios con Privacidad Financiera:** En `/estadisticas`, el Cliente puede analizar el ranking de popularidad de los servicios (`reportes.ver`), pero se oculta la tarjeta de ingresos totales acumulados y la columna de montos facturados (`reportes.financiero`).

#### Regla 3: Flujo de Aprobación de Cuentas por un Administrador Activo
- Para evitar que cualquier usuario externo se otorgue privilegios elevados en el sistema, cuando alguien se registra solicitando un rol interno (`Administrador`, `Gestor de proyectos`, `Soporte técnico`, `Usuario interno`), el registro se crea en estado pendiente (`aprobado = FALSE`).
- Al intentar iniciar sesión, el sistema bloquea el ingreso:
  > *"Tu solicitud de rol [Rol] está pendiente de aprobación por un Administrador activo del sistema."*
- Un Administrador activo ingresa a `/admin/usuarios`, visualiza las solicitudes pendientes y las autoriza con un solo clic (`/admin/aprobar-usuario/<id>`), habilitando inmediatamente el acceso.
- Los usuarios con rol `Cliente` quedan en `aprobado = TRUE` desde el primer instante para permitir su autoservicio comercial.

#### Regla 4: Auditoría y Trazabilidad en PostgreSQL (`logs_actividad`)
Toda acción relevante queda registrada en la tabla `logs_actividad` con fecha, IP, usuario y detalles:
- Inicios de sesión exitosos y bloqueados (`LOGIN_EXITOSO`, `LOGIN_PENDIENTE_APROBACION`).
- Intentos de acceso denegados (`ACCESO_DENEGADO_ROL`, `ACCESO_DENEGADO_PERMISO`, `ACCESO_DENEGADO_COMPROBANTE`).
- Modificaciones administrativas (`REGISTRO_USUARIO`, `APROBAR_ADMINISTRADOR`, `CAMBIO_ROL`).
- Movimientos comerciales (`EMITIR_FACTURA`, `EDITAR_FACTURA`, `ELIMINAR_FACTURA`).

#### Regla 5: Autogeneración Secuencial Atómica para Producción en PostgreSQL
Para operar con estándares de producción de nivel empresarial y concurrencia segura:
- **IDs Primarios:** Todas las tablas relacionales (`solicitudes`, `clientes`, `servicios`, `proveedores`, `facturacion`, `detalle_factura`, etc.) utilizan secuencias dedicadas de PostgreSQL mediante `id SERIAL PRIMARY KEY` (`nextval`).
- **Sincronización Automática (`setval`):** Se implementó una rutina PL/pgSQL al final del despliegue que sincroniza automáticamente el valor de cada secuencia con el `COALESCE(MAX(id), 1)` respectivo, garantizando que nunca se produzca un choque de claves primarias por desalineación de secuencias (`duplicate key value violates unique constraint`).
- **Numeración Comercial de Comprobantes:** Tanto para Facturas (`001-001-XXXX`) como para Cotizaciones (`COT-2026-XXXX`), se implementaron secuencias independientes (`secuencia_facturas`, `secuencia_cotizaciones`) y un disparador (*trigger*) `BEFORE INSERT` denominado `trg_autogenerar_numero` en la tabla `facturacion`. Si el usuario no ingresa un número de comprobante, el motor de PostgreSQL lo asigna de manera atómica, secuencial e inviolable.

### 4.5. Motor de Búsqueda y Filtrado Interactivo de Servicios (Frontend y Backend)
En respuesta al requerimiento de dinamismo y usabilidad comercial, el catálogo de servicios dejó de ser un simple enlistado estático para convertirse en un motor interactivo de búsqueda y filtrado multicriterio:
1. **Buscador en Tiempo Real (Cliente):** Input de búsqueda instantánea con normalización de caracteres (insensible a mayúsculas, minúsculas y tildes mediante expresiones regulares NFD), filtrando en el DOM por nombre, descripción y tecnologías mientras el usuario escribe.
2. **Píldoras y Selectores de Categoría:** Botones rápidos de acceso directo para filtrar por categorías (`Desarrollo Web`, `Marketing Digital`, `Diseño y Catálogos`, `Soporte y Asesoría`), sincronizados dinámicamente con selectores desplegables.
3. **Filtros por Disponibilidad y Ordenamiento:** Capacidad de aislar servicios disponibles vs. servicios futuros (próximamente) y reordenar por precio ascendente, descendente o nombre alfabético.
4. **Respaldo en Servidor (Backend Query Params):** El controlador `/servicios` admite parámetros de consulta (`?q=...&tipo=...`) ejecutando sentencias SQL con `ILIKE` parametrizado, permitiendo compartir enlaces directos o marcadores de búsqueda.
5. **Estado Amigable "Sin Resultados":** Componente visual con sugerencias y botón de restablecimiento rápido cuando no se encuentran coincidencias.

---

## 5. VALIDACIÓN EXPERIMENTAL Y RESULTADOS DE LAS PRUEBAS

Para certificar el correcto funcionamiento de cada componente, se ejecutó la suite de pruebas unitarias y de integración `scratch/test_suite.py` mediante el framework `unittest` de Python.

### 5.1. Resumen de Ejecución de Pruebas

```text
.................
----------------------------------------------------------------------
Ran 17 tests in 10.900s

OK
```
**Resultado Final:** 17 pruebas ejecutadas, 17 pruebas aprobadas (**100% de éxito, 0 fallos, 0 errores**).

### 5.2. Detalle de Casos de Prueba Evaluados

| # | Identificador del Caso de Prueba | Propósito y Requisito Evaluado | Resultado |
|---|---|---|:---:|
| 1 | `test_01_public_access` | Comprueba que la página de inicio (`/`) y catálogo de servicios (`/servicios`) sean accesibles sin iniciar sesión. | **APROBADO** |
| 2 | `test_02_protected_routes_redirect_to_login` | Comprueba que las rutas privadas redirijan a `/login` a los usuarios no autenticados. | **APROBADO** |
| 3 | `test_03_registration_normal_user_auto_approved` | Valida el registro de un Cliente con CAPTCHA, hash Bcrypt y aprobación automática (`aprobado = True`). | **APROBADO** |
| 4 | `test_04_registration_admin_user_pending_approval` | Valida que al solicitar rol Administrador, la cuenta quede pendiente (`aprobado = False`) y no pueda iniciar sesión. | **APROBADO** |
| 5 | `test_05_admin_approval_workflow` | Un Administrador activo aprueba la cuenta y el nuevo usuario puede ingresar exitosamente. | **APROBADO** |
| 6 | `test_06_rbac_access_restrictions` | Verifica que el Cliente tenga prohibido entrar a `/proveedores` y `/clientes`. | **APROBADO** |
| 7 | `test_07_audit_logs_recorded` | Verifica la persistencia de registros de auditoría en la tabla `logs_actividad`. | **APROBADO** |
| 8 | `test_08_semana15_relational_queries_and_joins` | Valida las consultas complejas JOIN de 3+ tablas en estadísticas, clientes y proveedores. | **APROBADO** |
| 9 | `test_09_custom_error_handlers` | Comprueba el renderizado corporativo de los errores HTTP 404 y 500. | **APROBADO** |
| 10 | `test_10_database_auto_ids_and_composite_pk` | Verifica la columna `id SERIAL` en todas las tablas y la PRIMARY KEY compuesta en `rol_permisos (rol_id, permiso_id)`. | **APROBADO** |
| 11 | `test_11_cliente_invoice_creation_prohibited` | Valida que un Cliente tenga bloqueada la emisión, edición y eliminación de facturas. | **APROBADO** |
| 12 | `test_12_cliente_voucher_ownership_and_privacy` | Valida que un Cliente solo pueda ver sus propios comprobantes, bloqueando comprobantes ajenos con log de auditoría. | **APROBADO** |
| 13 | `test_13_services_visibility_anonymous_vs_authenticated` | Comprueba que los servicios futuros solo se muestren a usuarios con sesión activa. | **APROBADO** |
| 14 | `test_14_cliente_financial_privacy_in_statistics` | Valida que el Cliente pueda ver el ranking de servicios pero no los ingresos financieros de la empresa. | **APROBADO** |
| 15 | `test_15_privilege_roles_require_admin_approval` | Valida que cualquier rol interno con privilegios requiera aprobación previa de un Administrador. | **APROBADO** |
| 16 | `test_16_services_search_engine_backend_and_public` | Valida el motor de búsqueda de servicios por palabra clave y filtro por categoría en backend y frontend. | **APROBADO** |
| 17 | `test_17_sequential_ids_and_invoice_autogeneration` | Valida la autogeneración secuencial atómica en PostgreSQL para IDs y códigos de facturación (`001-001-XXXX` y `COT-2026-XXXX`). | **APROBADO** |


---

## 6. GUÍA DE INSTALACIÓN Y REPRODUCCIÓN PASO A PASO

### 6.1. Requisitos Previos
- Python 3.11 o superior instalado.
- Servidor PostgreSQL 14 o superior activo en el puerto 5432.
- Terminal PowerShell o Bash.

### 6.2. Creación del Entorno Virtual e Instalación de Dependencias
```powershell
cd C:\Users\quiar\Documents\GitHub\NEXODIGITAL
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 6.3. Despliegue del Esquema en PostgreSQL
```powershell
psql -U postgres -c "CREATE DATABASE nexodigital;"
psql -U postgres -d nexodigital -f sql\esquema.sql
```

### 6.4. Configuración del Archivo `.env`
Crear el archivo `.env` en la raíz del proyecto basándose en `.env.example`:
```env
SECRET_KEY=nexodigital_clave_secreta_academica_2026
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nexodigital
DB_USER=postgres
DB_PASSWORD=TU_CONTRASENA_POSTGRES
```

### 6.5. Ejecución de la Suite de Pruebas
```powershell
.\venv\Scripts\python.exe scratch\test_suite.py
```

### 6.6. Inicio del Servidor Web
```powershell
python app.py
```
Acceder mediante el navegador web a: `http://127.0.0.1:5000`

**Usuario de Demostración Preconfigurado:**
- **Usuario:** `admin_principal`
- **Contraseña:** `Admin2026.`
- **Rol:** `Administrador`

---

## 7. CONCLUSIONES

1. **Cumplimiento Integral de Objetivos:** Se completaron con éxito todos los requerimientos estipulados para las Semanas 14 y 15, articulando un sistema de login seguro con Bcrypt y Flask-Login, junto con una base de datos PostgreSQL robusta y consultas avanzadas con cláusulas JOIN.
2. **Arquitectura RBAC Escalable:** La separación entre roles, permisos y la tabla intermedia con clave primaria compuesta `(rol_id, permiso_id)` permite otorgar permisos a nivel de micro-operación sin incurrir en redundancias en el código fuente.
3. **Refuerzo de Reglas de Negocio:** La delimitación de responsabilidades garantiza la privacidad de datos: los clientes consultan sus propios comprobantes y servicios futuros sin comprometer datos de facturación empresarial ni proveedores.
4. **Verificación Automatizada Rigurosa:** Las 15 pruebas unitarias e integradas proveen una garantía verificable de estabilidad y seguridad, previniendo regresiones o vulnerabilidades en futuros desarrollos.
