# Flujo Headhunter: creación de clientes asignados, vacantes y parametrización

Documento orientado al código de **atsatiempo**: rol **Cliente Headhunter** (`tipo_cliente = '2'`), clientes **asignados** (`tipo_cliente = '3'`), modelo **`Cli064AsignacionCliente`** y pantallas de configuración.

---

## 1. Conceptos y datos maestros

### Tipos de cliente (`TIPO_CLIENTE_STATIC`)

Definidos en `applications/services/choices.py` y campo `Cli051Cliente.tipo_cliente`:

| Código | Significado |
|--------|-------------|
| `'1'` | Cliente Standard |
| `'2'` | Cliente Headhunter |
| `'3'` | Cliente asignado a un Headhunter |

En login, la sesión expone `tipo_cliente` como texto: `Standard`, `Headhunter` o `Asignado` (`loginView.login_view`).

### Asignaciones (`Cli064AsignacionCliente`)

- **`id_cliente_maestro`**: en el flujo headhunter es el **Cliente Headhunter** (la empresa que gestiona).
- **`id_cliente_asignado`**: la empresa final (**Cliente asignado**, típicamente tipo `'3'`).
- **`tipo_asignacion`** (`TIPO_ASIGNACION_STATIC`):
  - `'1'` — Asignación Cliente (p. ej. cliente estándar bajo cliente sistema `1000`).
  - `'2'` — **Asignación Headhunter** (vínculo maestro headhunter → cliente asignado).

Restricción: la pareja `(id_cliente_maestro, id_cliente_asignado)` es única.

---

## 2. Alta del Cliente Headhunter (cuenta “maestra”)

### 2.1 Desde administración ATS

**Ruta:** `/cliente/crear/`  
**Nombre:** `clientes:cliente_crear`  
**Vista:** `applications.cliente.views.admin_views.crear_cliente`  
**Permiso:** `acceso_admin`

Formulario **`ClienteForm`**: al guardar (`ClienteForm.save()` en `ClienteForms.py`):

1. Crea **`Cli051Cliente`** con el **`tipo_cliente`** elegido en el formulario (debe ser `'2'` para Headhunter).
2. Crea **`Cli064AsignacionCliente`** con `id_cliente_maestro = Cli051Cliente id 1000`, `id_cliente_asignado` = nuevo cliente, **`tipo_asignacion = '1'`**, estado activo.

Listado y creación rápida también en **`/cliente/listar/`** — `clientes:cliente_ver` (misma lógica de formulario en POST).

### 2.2 Usuario de acceso (portal)

El usuario de portal para clientes es **grupo 3** (`UsuarioBase`, `acceso_cliente`). Puede crearse por flujos de **alta de cliente** del portal interno (`ClienteAdminView.cliente_listar` en `cliente/listar`) u otros procesos de usuarios internos; debe quedar **`cliente_id_051`** apuntando al registro **`Cli051Cliente`** del Headhunter.

> Registro público de empresa (`/registro/empresa`, `company_registration`) crea cliente **Standard** (`tipo_cliente='1'`) y asignación con maestro `1000`, no Headhunter.

---

## 3. Crear o vincular un “cliente asignado” desde el Headhunter

**Ruta:** `/cliente/asignados/`  
**Nombre:** `clientes:client_headhunter_asignados`  
**Vista:** `applications.cliente.views.client_views.client_headhunter_assigned`  
**Permiso:** `acceso_cliente`  
**Plantilla:** `admin/client/client_user/headhunter/client_headhunter_assigned.html`

Flujo:

1. Se usa la sesión **`cliente_id`** del usuario logueado (debe ser el **cliente maestro Headhunter**).
2. Formulario **`ClienteFormAsignacionCliente`** (NIT, razón social, ciudad, actividad económica, contacto, correo, teléfono, perfil empresarial, logo opcional, periodicidad de pago, colaboradores, datos de contacto/cargo, etc.).
3. **Por NIT:**
   - Si ya existe **`Cli051Cliente`** con ese NIT → se reutiliza.
   - Si no existe → se crea con **`tipo_cliente = 3`** (Cliente asignado Headhunter).
4. Si no existe aún **`Cli064AsignacionCliente`** entre maestro (sesión) y asignado:
   - Se crea con **`tipo_asignacion = '2'`** y estado activo.
5. Si la asignación ya existía → mensaje de advertencia.

**APIs de apoyo** (`applications/cliente/views/api_views.py`):

- **`POST /cliente/api/buscar_cliente_nit/`** — `clientes:api_buscar_cliente_nit`  
  Busca cliente por NIT para precargar datos en modal/UI.
- **`POST /cliente/api/verificar_asignacion/`** — `clientes:api_verificar_asignacion`  
  Indica si ya hay asignación activa entre `cliente_id` y `cliente_maestro_id`.

### 3.1 Equivalencia desde admin ATS

**Ruta:** `/cliente/detalle/asignados/<pk>/` — `clientes:client_detail_assigned`  
**Vista:** `admin_views.client_detail_assigned` — **`acceso_admin`**

Permite asociar clientes a un maestro cuyo id es **`pk`** (útil para soporte). Al crear cliente nuevo vía `get_or_create` el código usa **`tipo_cliente: 1`** en `defaults` (convención distinta al flujo self-service headhunter); la asignación sigue siendo **`tipo_asignacion = '2'`**.

---

## 4. Vacantes bajo relación Headhunter → cliente asignado

### 4.1 Listado global de vacantes de clientes asignados

**Ruta:** `/vacante/clientes/`  
**Nombre:** `vacantes:vacantes_detalle_cliente_headhunter`  
**Vista:** `applications.vacante.views.client_views.vacancy_client_assigned`

Filtra vacantes donde:

- `asignacion_cliente_id_064__id_cliente_maestro = cliente_id` (sesión),
- `asignacion_cliente_id_064__tipo_asignacion = '2'`.

Desde la tabla se enlaza la edición y gestión con **`id_cliente_asignado`** de la vacante:

- Editar: `vacantes:vacantes_editar_propias` — `/vacante/mis_vacantes/editar/<pk_cliente>/<vacante_id>/`
- Gestionar: `vacantes:vacantes_gestion_propias` — `/vacante/mis_vacantes/gestionar/<pk_cliente>/<vacante_id>/`

### 4.2 Listado “mis vacantes” por cliente asignado (por `pk`)

**Ruta:** `/vacante/mis_vacantes/<pk>/` — `vacantes:vacantes_propias`  
**Vista:** `applications.vacante.views.admin_views.list_vacanty_from_client`

Si **`grupo_id == 3`** (usuario cliente en portal):

- Busca asignaciones **`Cli064AsignacionCliente`** con `id_cliente_asignado=pk`, `id_cliente_maestro=cliente_id` de sesión, **`tipo_asignacion='2'`**.
- Muestra solo vacantes ligadas a esas asignaciones (no debe ver vacantes de otros headhunters para el mismo NIT sin asignación correcta).

### 4.3 Creación / edición de vacante y `Cli064AsignacionCliente`

En `applications/vacante/views/admin_views.py`, **`_asignacion_cliente_para_vacante_desde_admin`**:

- **Grupo 3 (sesión cliente / Headhunter):**  
  `id_cliente_maestro` = `request.session['cliente_id']`,  
  `id_cliente_asignado` = `pk` del cliente para el que se crea la vacante,  
  defaults **`tipo_asignacion = '2'`**.
- **Otros (p. ej. admin):** maestro id **1000**, **`tipo_asignacion = '1'`** (mismo patrón que cliente estándar).

Tras guardar vacante, redirecciones dependen de `request.session['tipo_cliente']` (`Standard` vs `Headhunter`).

---

## 5. Configuración y parametrización del cliente (catálogo operativo)

Estos módulos definen qué puede exigir el proceso de selección (cargos, requisitos por cargo, pruebas, políticas internas) y datos maestros del cliente.

### 5.1 Rutas con `<pk>` (admin ATS o cliente con permiso)

Prefijo **`/cliente/detalle/...`** — namespace **`clientes`**. Vistas en **`admin_views.py`** con **`@validar_permisos('acceso_admin', 'acceso_cliente')`** (salvo las que son solo admin, indicadas abajo):

| Ruta | Nombre URL | Contenido típico |
|------|------------|-------------------|
| `/cliente/detalle/<pk>/` | `cliente_detalle` | Ver nota §5.3 |
| `/cliente/detalle/informacion/<pk>/` | `cliente_info` | Datos generales del cliente |
| `/cliente/detalle/politicas/<pk>/` | `cliente_politicas` | Políticas internas ligadas al cliente |
| `/cliente/detalle/pruebas/<pk>/` | `cliente_pruebas` | Pruebas psicométricas asociadas al cliente |
| `/cliente/detalle/cargos/<pk>/` | `cliente_cargos` | **Cargos** (`Cli068Cargo`) |
| `/cliente/detalle/cargos/configuracion/<pk>/<cargo_id>/` | `cliente_cargos_configuracion` | Asignación **requisitos** (`Cli070AsignacionRequisito`) y **pruebas** (`Cli071AsignacionPrueba`) al cargo |
| `/cliente/detalle/requisitos/<pk>/` | `cliente_requisitos` | Catálogo / gestión de requisitos del cliente |
| `/cliente/detalle/grupo_trabajo/<pk>/` | `client_detail_group_work` | Usuarios internos del cliente |

Solo **`acceso_admin`:** `client_detail_assigned` (asignados desde panel admin).

### 5.2 Rutas sin `<pk>` (cliente logueado = sesión)

El **`cliente_id` de sesión** determina sobre qué empresa se actúa:

| Ruta | Nombre | Uso |
|------|--------|-----|
| `/cliente/informacion_principal` | `info_principal_cliente` | Edición datos propios |
| `/cliente/cargos` | `cargos_cliente` | Cargos |
| `/cliente/cargos/detalle/<cargo_id>/` | `cargos_cliente_detalle` | Configuración requisitos/pruebas por cargo |
| `/cliente/pruebas` | `pruebas_cliente` | Pruebas |
| `/cliente/politicas` | `politicas_cliente` | Políticas |
| `/cliente/requisitos` | `requisitos_cliente` | Requisitos |
| `/cliente/grupo_trabajo` | `usuarios_internos_listar` | Equipo / usuarios internos |

Un **Headhunter** autenticado tiene en sesión el **`cliente_id` del Headhunter**, por lo que estas pantallas **parametrizan al Headhunter mismo**, no automáticamente al cliente asignado. Para parametrizar al **cliente asignado**, hay que usar las rutas **con `<pk>`** del apartado 5.1 con **`pk = id` del cliente asignado** (si el rol tiene `acceso_cliente` y las políticas de negocio lo permiten).

### 5.3 Colisión del nombre `cliente_detalle`

En `applications/cliente/urls.py` el nombre **`cliente_detalle`** está declarado **dos veces**; Django usa la **última** definición, que apunta a **`ClienteAdminView.cliente_detalle`** (`acceso_admin` únicamente). La plantilla de clientes asignados enlaza `{% url 'clientes:cliente_detalle' cliente.id %}`: **un usuario solo Headhunter podría no tener acceso** si no dispone de `acceso_admin`.

Para entrada segura con **`acceso_cliente`**, usar rutas explícitas como **`clientes:cliente_info`**, **`clientes:cliente_cargos`**, etc., con el **`pk`** del cliente asignado.

---

## 6. Resumen de flujo

```text
[Admin ATS] Crea Cli051Cliente tipo '2' (Headhunter) + asignación a 1000 (tipo '1')
        → Usuario portal grupo 3 con cliente_id_051 = ese Headhunter

[Headhunter] /cliente/asignados/
        → NIT: buscar o crear Cli051Cliente tipo '3'
        → Cli064AsignacionCliente (maestro=sesión, asignado=cliente, tipo_asignacion='2')

[Headhunter] /vacante/mis_vacantes/<id_cliente_asignado>/  y creación/edición de vacante
        → asignación vacante: maestro=sesión, asignado=pk cliente, tipo '2'

[Headhunter] /vacante/clientes/
        → Vista consolidada de vacantes (tipo_asignacion='2', maestro=sesión)

Parametrización cliente asignado (pk = id cliente asignado)
        → /cliente/detalle/informacion/<pk>/, …/politicas/, …/cargos/, …/requisitos/, …/grupo_trabajo/<pk>/
```

---

## 7. Referencias de código

- Tipos y asignación: `applications/services/choices.py`, `applications/cliente/models.py` (`Cli051Cliente`, `Cli064AsignacionCliente`)
- Headhunter asigna clientes: `applications/cliente/views/client_views.py` (`client_headhunter_assigned`)
- APIs NIT / asignación: `applications/cliente/views/api_views.py`
- URLs: `applications/cliente/urls.py`, `applications/vacante/urls.py`
- Vacantes headhunter: `applications/vacante/views/client_views.py` (`vacancy_client_assigned`), `applications/vacante/views/admin_views.py` (`list_vacanty_from_client`, `_asignacion_cliente_para_vacante_desde_admin`)
- Menú lateral Headhunter: `templates/admin/layout/partials/menu_sidebar/dashboard_sidebar_client.html`
