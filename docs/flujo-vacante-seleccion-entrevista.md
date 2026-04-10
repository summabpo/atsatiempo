# Flujo operativo: vacante → analista → reclutador → entrevista → cliente

Descripción del proceso en **atsatiempo** desde la **creación de la vacante** hasta la **gestión por el cliente** y los **estados finales** de la postulación (`Cli056AplicacionVacante`). Basado en modelos, `choices` y vistas actuales.

---

## 1. Creación de la vacante

La vacante es **`Cli052Vacante`**, ligada a **`Cli064AsignacionCliente`** (cliente maestro / asignado según el flujo), **`Cli068Cargo`**, **`Cli073PerfilVacante`**, skills, fit cultural, etc.

**Entradas típicas en URLs** (`applications/vacante/urls.py`):

| Ruta | Nombre | Quién |
|------|--------|--------|
| `/vacante/crear/` | `vacantes_crear` | Administrador ATS |
| `/vacante/mis_vacantes/crear/<pk>/` | `vacantes_crear_propias` | Cliente / Headhunter (según `pk` y sesión) |
| `/vacante/crear_vacante/` | `vacantes_crear_cliente` | Cliente (`create_vacanty_v2`) |

Al guardar, la función **`_asignacion_cliente_para_vacante_desde_admin`** (`admin_views.py`) crea o reutiliza **`Cli064AsignacionCliente`**: para **grupo 3** (portal cliente, incl. headhunter) maestro = `cliente_id` de sesión y asignado = `pk`, **`tipo_asignacion = '2'`**; para otros casos, maestro **1000** y **`tipo_asignacion = '1'`**.

Campos relevantes en **`Cli052Vacante`** para el resto del flujo:

- **`usuario_asignado`**: analista de selección actual (FK `UsuarioBase`).
- **`data_asignacion_usuario`**: JSON con historial de asignaciones de analistas (consecutivo, fechas, quién asignó).
- **`asignacion_reclutador`**: reclutador actual (FK `UsuarioBase`).
- **`data_asignacion_reclutador`**: historial JSON de asignaciones de reclutadores.
- **`cantidad_presentar`**, **`estado_vacante`**: ciclo de vida de la vacante (activa, en proceso, finalizada, cancelada).

---

## 2. Asignación del analista de selección a la vacante

Objetivo: definir **quién es el analista** que verá la vacante en sus listados y podrá editarla (según permisos).

**Opción A — Pantalla dedicada del cliente**

- **Ruta:** `/vacante/asignar_analista/<pk>/` (`pk` = id de la **vacante**).
- **Nombre:** `vacantes:vacantes_asignar_analista_cliente`
- **Vista:** `client_views.detail_vacancy_assign`
- **Formulario:** `VacancyAssingForm` → asigna `vacante.usuario_asignado` y guarda.

**Opción B — Gestión integral de la vacante (misma pantalla que reclutador y alta manual de candidato)**

- **Ruta:** `/vacante/mis_vacantes/gestionar/<pk_cliente>/<vacante_id>/` — `vacantes:vacantes_gestion_propias`  
  o equivalente cliente: `/vacante/gestionar/<pk>/<vacante_id>/` — `vacantes:vacantes_gestion_propias_cliente`
- **Vista:** `admin_views.vacanty_management_from_client`
- **POST** con botón **`submit_analista`:** actualiza `usuario_asignado` y **añade un registro** a `data_asignacion_usuario` (auditoría).

**Listados del analista**

- Analista ligado al **cliente** (`acceso_analista_seleccion`): `/vacante/asignadas/` — `vacantes_asignadas` — filtra `usuario_asignado = user_login.id`.
- Analista **ATS interno** (`acceso_analista_seleccion_ats`): `/vacante/asignadas/analista` — `vacantes_asignadas_analista_interno` — mismo criterio sobre `usuario_asignado`.

Desde ahí puede abrir **gestión/edición** de la vacante (`vacantes_gestion_analista_interno`, `vacantes_editar_analista_interno`) y flujos de **reclutados** bajo rutas `reclutados:reclutados_analista_interno` / `reclutados_detalle_analista_interno`.

---

## 3. Asignación del reclutador a la vacante

El **reclutador** es quien trabaja el **embudo de reclutamiento** por candidato (`estado_reclutamiento`) y prepara candidatos hacia la **entrevista**.

- En **gestión de vacante** (`vacanty_management_from_client`), **POST** con **`submit_reclutador`**:
  - Asigna `vacante.asignacion_reclutador`.
  - Registra historial en **`data_asignacion_reclutador`**.

**Listado del reclutador**

- **Ruta:** `/reclutado/vacantes_asignadas/`
- **Nombre:** `reclutados:vacantes_asignadas_reclutador`
- **Vista:** `client_recruiter_views.vacancies_assigned_recruiter`
- **Filtro:** `asignacion_reclutador=request.user`, vacante activa (`estado_id_001=1`).
- Muestra conteos por **`estado_reclutamiento`** (1–4).

**Detalle por vacante (reclutador)**

- **Ruta:** `/reclutado/vacantes_asignadas/gestionar/<pk>/<vacante_id>/`
- **Nombre:** `reclutados:vacantes_gestion_reclutador`
- Agrupa aplicaciones en columnas según **`estado_reclutamiento`**, búsqueda en “Recibidos”, formulario para **programar entrevistas** múltiples (`EntrevistaCrearForm`).

---

## 4. Embudo de reclutamiento (`estado_reclutamiento`)

Definido en **`ESTADO_RECLUTADO_CHOICES_STATIC`** (`applications/services/choices.py`):

| Código | Etiqueta |
|--------|----------|
| 1 | Aspirantes |
| 2 | Precalificados por CV |
| 3 | **Aprobados para Entrevista** |
| 4 | No aprobados por CV |

El reclutador (u otros roles autorizados en la vista) actualiza el estado desde el **detalle del reclutado**:

- **Ruta:** `/reclutado/detalle/reclutado/<pk>/` — `reclutados:reclutados_detalle_reclutador` (`pk` = id de **`Cli056AplicacionVacante`**).
- **Vista:** `client_recruiter_views.detail_recruited`
- Al guardar, se escribe **`estado_reclutamiento`**, comentario y **`registro_reclutamiento`** (historial JSON de cambios).

**Para “dejar al candidato listo para entrevista”** en términos de este embudo: pasar al candidato a **`estado_reclutamiento = 3` (Aprobados para Entrevista)**. A partir de ahí se coordina la **creación de la cita de entrevista** (`Cli057AsignacionEntrevista`), que en el historial de aplicación suele reflejarse como transición de **`estado_aplicacion`** hacia **Entrevista programada (2)** u otros estados según la acción (ver sección 6).

---

## 5. Qué hace el reclutador (resumen)

1. Ve **solo vacantes** donde es `asignacion_reclutador`.
2. En cada vacante, revisa candidatos en **Aspirantes**, mueve a **Precalificados por CV** o **No aprobados por CV**, y marca **Aprobados para Entrevista** cuando corresponde.
3. Puede **programar entrevistas** (fecha, hora, entrevistador, tipo, enlace/lugar) desde la gestión de la vacante; eso crea **`Cli057AsignacionEntrevista`** y dispara historial vía **`crear_historial_aplicacion`** (p. ej. “Entrevista asignada”).
4. Abre el **detalle del candidato** para ver match, CV, comentarios y cambiar **`estado_reclutamiento`** con trazabilidad.

---

## 6. Estados de la aplicación (`estado_aplicacion`) e interacción con entrevistas

Catálogo principal (**`ESTADO_APLICACION_CHOICES_STATIC`**):

| Código | Significado |
|--------|-------------|
| 1 | Aplicado |
| 2 | Entrevista programada |
| 3 | Entrevista aprobada |
| 4 | Entrevista no aprobada |
| 5–7 | Pruebas (programada / superada / no superada) |
| 8 | Seleccionado |
| 9 | Finalizada |
| 10–12 | Cancelada / Desiste / No apto |
| 13 | Seleccionado por Cliente |

El componente **`crear_historial_aplicacion`** (usado al asignar entrevista, gestionar resultados, etc.) va actualizando **`estado_aplicacion`** y el historial **`Cli063AplicacionVacanteHistorial`**.

---

## 7. Entrevistador del cliente

Usuarios con permiso **`acceso_cliente_entrevistador`** (grupo entrevistador del cliente).

**Listado de entrevistas asignadas a mí**

- **Ruta:** `/entrevista/listado/entrevistador/`
- **Nombre:** `entrevistas:entrevistas_listado_entrevistador`
- **Filtro:** `entrevistas` donde **`usuario_asignado`** = usuario en sesión.

**Gestionar una entrevista**

- **Ruta:** `/entrevista/gestionar/entrevistador/<pk>/` (`pk` = id de **`Cli057AsignacionEntrevista`**)
- **Nombre:** `entrevistas:entrevistar_gestionar_entrevistador`
- **Formulario:** `EntrevistaGestionForm` — observación + **`estado_asignacion`**.
- Según el código en `client_interviewer_views.management_interview`, al confirmar se llama **`crear_historial_aplicacion`** con el **`estado_aplicacion`** objetivo, por ejemplo:
  - Aprobación de etapa intermedia → **3** (Entrevista aprobada).
  - No apto en entrevista → **4** / reglas asociadas (según ramas del formulario).
  - Selección final por entrevistador → **8** (Seleccionado).
  - Cancelación → **10**.

> Nota: el archivo `client_interviewer_views.py` declara en una vista permisos `acceso_admin` y `acceso_cliente`; el **listado** usa `acceso_cliente_entrevistador`. Conviene alinear permisos en despliegue real.

Hay flujos paralelos para **gestión de entrevista** desde **analista interno** (`entrevistar_gestionar_analista_interno`) y desde **vista cliente genérica** (`entrevistar_gestionar_cliente`), con lógica ampliada (resultados por secciones, requisitos, etc.) en `entrevista/views/client_views.py`.

---

## 8. Cliente empresa: seguimiento, aprobación y cierre

**Detalle de vacante (cliente / admin / analista según permisos)**

- **Ruta:** `/vacante/detalle/<pk>/` — `vacantes:vacantes_detalle_cliente`
- **Vista:** `client_views.detail_vacancy`

Incluye:

- Secciones por **`estado_reclutamiento`** (misma taxonomía 1–4).
- Panel de candidatos en **Seleccionado (8)** o **Seleccionado por Cliente (13)**.
- Métricas de aplicaciones por **`estado_aplicacion`** (aplicados, en etapa entrevista/pruebas, no aprobados, seleccionados).
- Lógica de **`cantidad_presentar`** para ordenar candidatos en la “decisión del cliente” (presentación de terna / n-candidatos).

**Entrevistas de la vacante**

- **Ruta:** `/vacante/detalle/entrevistas/<pk>/` — `vacantes:vacantes_entrevista_cliente`

**Gestión amplia de vacante (admin/cliente/analista selección)**

- **`vacanty_management_from_client`** — mismos formularios de **analista**, **reclutador** y **alta manual de candidato** descritos arriba.

El **cliente** “aprueba y gestiona” en la práctica:

- Viendo el pipeline y los **estados finales** de cada postulación (hasta **Finalizada 9**, **Seleccionado 8**, **Seleccionado por cliente 13**, o estados de descarte).
- Interactuando con **entrevistas** y, según configuración, con **requisitos/pruebas/políticas** del candidato en otras pantallas del sistema.

---

## 9. Dónde termina el proceso (alcance del flujo)

1. **Vacante:** puede pasar a **finalizada** o **cancelada** (`estado_vacante` en `Cli052Vacante`).
2. **Candidato / aplicación:** estados terminales típicos en **`estado_aplicacion`**:
   - **9 — Finalizada** (proceso cerrado con contratación o cierre administrativo).
   - **8 / 13 — Seleccionado / Seleccionado por cliente** (éxito en selección).
   - **10, 11, 12** — Cancelada, Desiste, No apto (salidas sin contratación).
3. **Reclutamiento interno:** candidato en columna **No aprobados por CV (4)** o fuera del embudo operativo.

El sistema **no modela en este mismo documento** la contratación fuera del ATS (firma de contrato en mundo real); el tope funcional descrito es **cierre del proceso de selección en la plataforma** según los estados anteriores.

---

## 10. Diagrama resumido

```text
[Crear vacante] → [Asignar analista: usuario_asignado]
                → [Asignar reclutador: asignacion_reclutador]

[Analista] listado / edición vacante
[Reclutador] embudo 1→2→3 o 4  |  3 = listo para coordinar entrevista
                → Programar entrevista → Cli057AsignacionEntrevista + historial aplicación

[Entrevistador] ejecuta / califica entrevista → actualiza estado_aplicacion (3,4,8,10…)

[Cliente] detalle vacante: métricas, seleccionados 8/13, cantidad_presentar, entrevistas

[Fin] estado_aplicacion 9 u otros finales | vacante estado_vacante 3/4
```

---

## 11. Referencias de código

- Vacante y asignaciones: `applications/vacante/models.py` (`Cli052Vacante`), `applications/vacante/views/admin_views.py` (`vacanty_management_from_client`, `_asignacion_cliente_para_vacante_desde_admin`)
- Asignación analista solo: `applications/vacante/views/client_views.py` (`detail_vacancy_assign`)
- Analista: `applications/vacante/views/client_analyst_views.py`, `client_analyst_internal_views.py`
- Reclutador: `applications/reclutado/views/client_recruiter_views.py`
- Choices: `applications/services/choices.py` (`ESTADO_APLICACION_*`, `ESTADO_RECLUTADO_*`)
- Entrevista: `applications/entrevista/models.py` (`Cli057AsignacionEntrevista`), `applications/entrevista/views/client_interviewer_views.py`, `client_views.py`
- Cliente detalle vacante: `applications/vacante/views/client_views.py` (`detail_vacancy`)
- URLs: `applications/vacante/urls.py`, `applications/reclutado/urls.py`, `applications/entrevista/urls.py`
