# ⚡ NEXODIGITAL - Soluciones Web y Plataforma Comercial

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Flask%203.1-black.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/Database-PostgreSQL%2014%2B-336791.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![UI](https://img.shields.io/badge/UI-Bootstrap%205.3-purple.svg?logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![Security](https://img.shields.io/badge/Security-Bcrypt%20%7C%20RBAC%20%7C%202FA-success.svg)]()
[![Status](https://img.shields.io/badge/Tests-17%2F17%20Passing%20(100%25)-brightgreen.svg)]()

Plataforma web institucional y sistema de gestión comercial integral para el emprendimiento tecnológico **NexoDigital**, desarrollado como parte del Proyecto Integrador de la carrera.

---

## 👥 Información Académica y Créditos del Proyecto

- **Institución:** Universidad Estatal Amazónica (UEA) — Sede Puyo / Quito
- **Nivel Académico:** Cuarto Semestre
- **Asignatura:** Desarrollo de Aplicaciones Web
- **Autores:**
  - **Cinthia Mishel Carrión Serrano**
  - **Aracely Maribel Quintanilla Rumipamba**
  - **Santiago Andrés Lara Caicedo**

---

## 📋 Cumplimiento de Objetivos Curriculares

### 🔐 Semana 14: Sistema de Autenticación y Seguridad
1. **Registro de Usuarios con Verificación Humana**: Formulario WTForms (`UsuarioForm`) con validaciones de campos obligatorios, formato de correo electrónico, contraseñas seguras y **CAPTCHA aritmético dinámico** para prevenir registros automatizados por bots.
2. **Almacenamiento Criptográfico Seguro**: Hashing irreversible con **Bcrypt** (`$2b$`), garantizando que ninguna contraseña se almacene en texto plano en la base de datos PostgreSQL.
3. **Gestión de Sesiones**: Implementado con **Flask-Login** (`UserMixin`, `login_user`, `logout_user`, `@login_required`, `current_user`). Control de caducidad automática tras 30 minutos de inactividad (`PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)`).
4. **Protección de Rutas Privadas**: Rutas internas inaccesibles para visitantes anónimos, redirigiendo automáticamente a `/login` con mensajes flash informativos.
5. **Autenticación en Dos Pasos (2FA)**: Soporte para códigos de verificación temporal OTP de 6 dígitos (`/verificar-2fa`).
6. **Simulación de Confirmación de Correo**: Mecanismo de activación y validación de correo electrónico (`/confirmar-email/<token>`).

### 🗄️ Semana 15: Base de Datos Relacional y Consultas Multitabla
1. **Motor Relacional PostgreSQL**: Conexión centralizada en `conexion/conexion.py` compatible con entornos locales (`.env`) y despliegues en la nube (**Render** vía `DATABASE_URL`).
2. **Modelo Entidad-Relación Consistente**: 15 tablas interconectadas con claves primarias (`PK`), claves foráneas (`FK`), reglas de integridad referencial (`ON DELETE CASCADE`, `ON DELETE SET NULL`) y restricciones `UNIQUE`.
3. **IDs Automáticos y Secuenciales para Producción**: Cada tabla de entidad cuenta con una columna `id SERIAL PRIMARY KEY` autogenerativa (`nextval`), con bloque de sincronización automática `setval` al final del esquema para evitar colisiones de clave duplicada.
4. **Autonumeración Atómica con Triggers**: La numeración comercial de facturas (`001-001-XXXX`) y cotizaciones (`COT-2026-XXXX`) es generada de forma atómica y concurrente mediante secuencias dedicadas y un trigger PostgreSQL `BEFORE INSERT`.
5. **Consultas con Cláusulas JOIN**:
   - `estadisticas`: Consulta relacionada entre `detalle_factura JOIN servicios JOIN tipos_servicio` para generar el ranking de demanda y cálculo de demanda proporcional.
   - `clientes`: Consulta `clientes JOIN tipos_negocio` para categorización comercial.
   - `proveedores`: Consulta `proveedores JOIN categorias_proveedor JOIN estados_proveedor`.
   - `facturacion` y comprobantes: Consulta `facturacion JOIN clientes JOIN estados_documento JOIN detalle_factura`.
6. **Motor de Búsqueda y Filtrado de Servicios**: Buscador interactivo en tiempo real con soporte multicriterio (palabras clave, normalización sin tildes, filtros de categorías en píldoras, disponibilidad y ordenamiento), respaldado por consultas parametrizadas con `ILIKE` en el backend.
7. **Páginas de Error Corporativas**: Manejadores personalizados para **404** (No encontrado), **403** (Acceso prohibido) y **500** (Error interno del servidor) que mantienen la identidad visual y barra de navegación institucional.


---

## 🛡️ Sistema de Control de Acceso Basado en Roles (RBAC)

El sistema implementa una arquitectura RBAC completa en la base de datos PostgreSQL mediante las tablas `roles`, `permisos` y la tabla intermedia `rol_permisos` con **PRIMARY KEY compuesta `(rol_id, permiso_id)`**.

```
  ┌──────────┐          ┌────────────────┐          ┌──────────┐
  │  ROLES   │1       N │  ROL_PERMISOS  │ N       1│ PERMISOS │
  │──────────│──────────│────────────────│──────────│──────────│
  │ id (PK)  │          │ rol_id (PK,FK) │          │ id (PK)  │
  │ nombre   │          │ permiso_id(PK) │          │ codigo   │
  └──────────┘          └────────────────┘          └──────────┘
```

### 1. Definición de los 5 Roles del Sistema

| Rol | Alcance y Fronteras de Acceso |
|---|---|
| **Administrador** | **Acceso total**: gestión integral de usuarios, asignación de roles, aprobación de solicitudes administrativas, catálogo de servicios, cartera de clientes, proveedores, facturación, estadísticas y visualización de logs de auditoría. |
| **Gestor de proyectos** | **Gestión comercial y operativa**: acceso a clientes, proyectos, facturación, cotizaciones, ranking y estadísticas financieras. **Sin acceso a gestión de usuarios ni infraestructura**. |
| **Soporte técnico** | **Infraestructura técnica**: directorio de proveedores tecnológicos, estados de servicio y soporte. **Sin acceso a datos sensibles ni facturación de clientes**. |
| **Usuario interno** | **Operaciones asignadas**: acceso al catálogo operativo de servicios y listado general de clientes. Datos mínimos necesarios. |
| **Cliente** | **Portal de autoservicio**: consulta exclusiva de sus facturas y cotizaciones contratadas, ranking de demanda de servicios y catálogo de servicios futuros. **Sin acceso a proveedores, facturas de terceros ni métricas financieras internas**. |

### 2. Matriz de Permisos Granulares (27 Permisos Activos)

Los permisos están tipificados por módulo y acción:
- **Servicios:** `servicios.ver`, `servicios.crear`, `servicios.editar`, `servicios.eliminar`, `servicios.futuros`.
- **Clientes:** `clientes.ver`, `clientes.crear`, `clientes.editar`, `clientes.eliminar`, `clientes.sensible`, `clientes.propio`.
- **Facturas y Cotizaciones:** `facturas.ver`, `facturas.crear`, `facturas.editar`, `facturas.eliminar`, `facturas.ver_propias`.
- **Proveedores:** `proveedores.ver`, `proveedores.crear`, `proveedores.editar`, `proveedores.eliminar`.
- **Usuarios y Roles:** `usuarios.ver`, `usuarios.crear`, `usuarios.editar`, `usuarios.eliminar`, `usuarios.aprobar`.
- **Reportes:** `reportes.ver`, `reportes.financiero`.

---

## ⚖️ Reglas de Negocio Reforzadas (Frontend, Backend y Base de Datos)

1. **Acceso Público vs. Privado**:
   - Visitantes no autenticados pueden ver libremente la página de inicio (`/`) y los servicios que ya están disponibles (`disponible = TRUE`).
   - Los servicios en desarrollo o futuros ("Próximamente" / `disponible = FALSE`) **únicamente se revelan a usuarios con sesión activa**.
2. **Restricciones Comerciales para Clientes**:
   - **Facturación protegida**: Un Cliente **NO** puede crear (`/facturacion/nueva`), editar (`/facturacion/editar`) ni eliminar facturas o cotizaciones (bloqueado por los decoradores `@role_required` y `@permission_required`, además de botones ocultos en las plantillas).
   - **Privacidad estricta de comprobantes**: Al acceder a `/facturacion/comprobante/<numero>`, el backend valida que la factura haya sido emitida a nombre o cédula del cliente autenticado. Si intenta consultar un documento ajeno, se bloquea la vista y se audita el intento en `logs_actividad`.
   - **Directorio de proveedores oculto**: La ruta `/proveedores` está restringida para el Cliente; el enlace se retira de su menú y el acceso directo genera denegación.
   - **Privacidad financiera en estadísticas**: En `/estadisticas`, el Cliente puede ver el ranking de demanda de servicios para conocer cuáles son las soluciones más populares, pero **se le ocultan los balances financieros y los ingresos totales del negocio**.
3. **Flujo Obligatorio de Aprobación de Roles**:
   - Para asumir roles internos con privilegios (`Administrador`, `Gestor de proyectos`, `Soporte técnico`, `Usuario interno`), el registro se crea en estado inactivo para login (`aprobado = FALSE`).
   - El sistema impide su acceso hasta que un **Administrador activo** revise y apruebe la solicitud en `/admin/usuarios`.
   - Los registros con rol `Cliente` quedan en `aprobado = TRUE` automáticamente para permitir su autoservicio inmediato.
4. **Auditoría Detallada de Eventos**:
   - La tabla `logs_actividad` registra cada acción crítica: `LOGIN_EXITOSO`, `LOGIN_BLOQUEADO`, `LOGIN_PENDIENTE_APROBACION`, `REGISTRO_USUARIO`, `APROBAR_ADMINISTRADOR`, `CAMBIO_ROL`, `ACCESO_DENEGADO_ROL`, `ACCESO_DENEGADO_PERMISO`, `ACCESO_DENEGADO_COMPROBANTE`, `EMITIR_FACTURA`, `EDITAR_FACTURA`, etc.

---

## 🧪 Suite de Pruebas Automatizadas (15/15 Casos Aprobados)

El proyecto incluye una suite completa en `scratch/test_suite.py` ejecutada mediante `unittest`:

```text
...............
----------------------------------------------------------------------
Ran 15 tests in 12.253s

OK
```

| # | Prueba | Requisito Validado | Resultado |
|---|---|---|:---:|
| 1 | `test_01_public_access` | Acceso público libre a `/` y `/servicios` sin autenticación | **PASS** |
| 2 | `test_02_protected_routes_redirect_to_login` | Redirección a `/login` para rutas privadas con usuario anónimo | **PASS** |
| 3 | `test_03_registration_normal_user_auto_approved` | Registro de rol Cliente con CAPTCHA: aprobado automáticamente y hash Bcrypt | **PASS** |
| 4 | `test_04_registration_admin_user_pending_approval` | Registro de Administrador queda pendiente (`aprobado = False`) y bloquea login | **PASS** |
| 5 | `test_05_admin_approval_workflow` | Un Administrador activo aprueba la cuenta y el nuevo usuario ya puede ingresar | **PASS** |
| 6 | `test_06_rbac_access_restrictions` | Restricciones de rutas por rol (Cliente no entra a `/proveedores` ni `/clientes`) | **PASS** |
| 7 | `test_07_audit_logs_recorded` | Registro de eventos y auditoría en `logs_actividad` | **PASS** |
| 8 | `test_08_semana15_relational_queries_and_joins` | Consultas JOIN multicapa (3+ tablas) en estadísticas, clientes y proveedores | **PASS** |
| 9 | `test_09_custom_error_handlers` | Renderizado correcto de plantillas corporativas de error (404, 500) | **PASS** |
| 10 | `test_10_database_auto_ids_and_composite_pk` | Columnas `id SERIAL` en todas las tablas y PK compuesta en `rol_permisos` | **PASS** |
| 11 | `test_11_cliente_invoice_creation_prohibited` | Bloqueo estricto para que un Cliente no pueda crear, editar ni borrar facturas | **PASS** |
| 12 | `test_12_cliente_voucher_ownership_and_privacy` | Validación de propiedad de comprobantes y bloqueo con log de auditoría | **PASS** |
| 13 | `test_13_services_visibility_anonymous_vs_authenticated` | Servicios futuros ocultos para anónimos y visibles ("Próximamente") para usuarios | **PASS** |
| 14 | `test_14_cliente_financial_privacy_in_statistics` | Cliente ve ranking pero no ingresos financieros; Administrador ve ambos | **PASS** |
| 15 | `test_15_privilege_roles_require_admin_approval` | Roles con privilegios (Gestor, Soporte, etc.) quedan bloqueados hasta aprobación | **PASS** |
| 16 | `test_16_services_search_engine_backend_and_public` | Motor de búsqueda de servicios por texto y categoría en backend y frontend | **PASS** |
| 17 | `test_17_sequential_ids_and_invoice_autogeneration` | Autogeneración secuencial atómica en PostgreSQL de IDs y números de factura | **PASS** |

Para ejecutar las pruebas:
```powershell
.\venv\Scripts\python.exe scratch\test_suite.py
```


---

## 🚀 Guía de Instalación y Despliegue Local

### 1. Clonar el repositorio y preparar el entorno
```powershell
cd C:\Users\quiar\Documents\GitHub\NEXODIGITAL
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configurar la Base de Datos PostgreSQL
Desde pgAdmin 4 o terminal PowerShell:
```powershell
psql -U postgres -c "CREATE DATABASE nexodigital;"
psql -U postgres -d nexodigital -f sql\esquema.sql
```

### 3. Configurar Variables de Entorno (`.env`)
Copiar [.env.example](.env.example) a `.env`:
```env
SECRET_KEY=clave_secreta_nexodigital_2026_segura
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nexodigital
DB_USER=postgres
DB_PASSWORD=TU_CONTRASENA_REAL
```

*(En Render, Neon o Supabase solo debes configurar la variable de entorno `DATABASE_URL`)*.

### 4. Iniciar el Servidor de Desarrollo
```powershell
python app.py
```
Abre en tu navegador: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🔑 Credenciales de Acceso para Pruebas

El esquema SQL preconfigura un Administrador activo para evaluar el sistema:

- **Usuario:** `admin_principal`
- **Contraseña:** `Admin2026.`
- **Rol:** `Administrador` (Acceso total y gestor de aprobaciones)

---

## 📁 Arquitectura y Estructura del Código

```text
NEXODIGITAL/
├── app.py                      # Rutas, decoradores RBAC, reglas de negocio y lógica Flask
├── models.py                   # Modelos relacionales Usuario, Role, Permiso, ActivityLog
├── requirements.txt            # Dependencias del proyecto (Flask, psycopg2, bcrypt, wtforms, etc.)
├── conexion/
│   └── conexion.py             # Conexión centralizada a PostgreSQL (Local y Render DATABASE_URL)
├── forms/                      # Formularios Flask-WTF con validación en servidor
│   ├── cliente_form.py
│   ├── facturacion_form.py     # Autonumeración correlativa secuencial
│   ├── login_form.py
│   ├── proveedor_form.py
│   ├── servicio_form.py
│   ├── usuario_form.py         # Registro con CAPTCHA aritmético
│   └── dos_factores_form.py
├── sql/
│   └── esquema.sql             # Tablas, IDs autoincrementales, PK compuesta y 27 permisos
├── static/
│   ├── css/estilo.css          # Paleta corporativa (Navy/Emerald/Mint) y WCAG AAA
│   └── js/script.js            # Interacciones frontend
├── templates/                  # Plantillas Jinja2 modulares
│   ├── base.html               # Estructura base responsive
│   ├── index.html              # Página de inicio institucional pública
│   ├── servicios.html          # Catálogo público con visualización condicional de futuros
│   ├── dashboard.html          # Panel de control métrico por rol
│   ├── estadisticas.html       # Ranking de demanda con privacidad financiera
│   ├── facturacion.html        # Listado con botones condicionales por rol
│   ├── comprobante_factura.html# Comprobante con validación de propiedad
│   ├── admin_usuarios.html     # Matriz visual de permisos y aprobador de cuentas
│   ├── admin_logs.html         # Visor de logs de auditoría
│   ├── 403.html / 404.html / 500.html # Páginas de error corporativas
│   └── components/
│       ├── navbar.html         # Navegación dinámica adaptativa según rol
│       └── footer.html         # Pie de página institucional con créditos UEA
└── scratch/
    └── test_suite.py           # Suite automatizada de 15 pruebas unitarias y de integración
```
