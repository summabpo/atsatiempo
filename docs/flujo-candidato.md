# Flujo del candidato en ATS (atsatiempo)

Este documento resume los pasos que un **candidato** recorre en la aplicación Django: registro, validación de correo, completar información de perfil, explorar vacantes y postularse. Está alineado con las vistas y URLs definidas en el código (2026).

---

## 1. Registro de cuenta

**Ruta:** `/registro/candidato/`  
**Nombre Django:** `accesses:candidate_registration`  
**Vista:** `applications.usuarios.views.user_login.loginView.candidate_registration`

Acciones principales:

1. El candidato completa el formulario (`SignupFormCandidato`): nombres, apellidos, correo, contraseña (duplicada), y **reCAPTCHA**.
2. Se valida que el correo no exista ya como usuario.
3. Se crea el registro en **`Can101Candidato`** con los datos básicos y estado activo.
4. Se crea **`UsuarioBase`** en el **grupo 2 (Candidato)** enlazado al candidato (`candidato_id_101`).
5. Se genera un **`TokenAutorizacion`** con vigencia (en código: 2 días).
6. Se envía correo de bienvenida con enlace para validar la cuenta (`enviar_correo('bienvenida', ...)`).

**Registro vía invitación (opcional):** si en el registro llega un `token` por GET/POST (por ejemplo QR), se invoca `crear_registro_cli084` para asociar el usuario a un flujo de reclutamiento previo.

Tras registrarse, el sistema redirige al **login** y muestra mensaje de que debe validar el correo.

---

## 2. Validación del correo electrónico

**Ruta:** `/validar_token/<token>/`  
**Nombre Django:** `accesses:validar_token`  
**Vista:** `loginView.validar_token`

- Si el token existe y no ha expirado, se marca **`UsuarioBase.is_verificado = True`**.
- Sin verificación, **no se puede iniciar sesión**: el login responde con error indicando revisar la bandeja de entrada.

Si el enlace venció, se informa que el link está vencido.

**Reenvío de validación:** existe la ruta `accesses:enviar_token` (`/enviar_token/`) para solicitar un nuevo correo con token.

---

## 3. Inicio de sesión y entrada al panel

**Ruta:** `/login/` — **Nombre:** `accesses:login`

Tras autenticarse con un usuario verificado:

- Para **grupo candidato (id 2)** se guarda en sesión **`candidato_id`** (y datos de usuario en `user_login`, imagen de perfil, etc.).

**Ruta de entrada genérica:** `/inicio/` — **Nombre:** `accesses:inicio` (`dashboard_begin`)

- Los candidatos se redirigen al dashboard propio: **`/candidato/inicio`** — **Nombre:** `accesses:inicio_candidato`  
- **Vista:** `dashboardView.dashboard_candidato`

En el dashboard del candidato se muestra el avance del perfil, un resumen de estudios, experiencia y habilidades, y **vacantes disponibles** que aún no ha aplicado (consulta con `query_vacanty_with_skills_and_details`, excluyendo aplicaciones propias).

---

## 4. Completar la información del perfil

Las rutas viven bajo el prefijo **`/candidato/`** (app `candidatos`). Todas las vistas de edición relevantes exigen **login** y permiso **`acceso_candidato`**.

| Área | Ruta aproximada | Nombre URL (namespace `candidatos`) |
|------|-----------------|--------------------------------------|
| Hub de perfil | `/candidato/perfil/` | `candidato_perfil` |
| Información básica | `/candidato/informacion/basica` | `candidato_info_personal` |
| Subida imagen perfil | `…/basica/upload/imagen` | `candidato_upload_imagen` |
| Subida hoja de vida | `…/basica/upload/hoja-vida` | `candidato_upload_hoja_vida` |
| Subida video perfil | `…/basica/upload/video` | `candidato_upload_video` |
| Formación académica | `/candidato/informacion/academica` (+ crear/editar) | `candidato_info_academica`, `…_crear`, `…_editar` |
| Experiencia laboral | `/candidato/informacion/laboral` (+ crear/editar) | `candidato_info_laboral`, `…_crear`, `…_editar` |
| Habilidades | `/candidato/informacion/habilidades` | `candidato_info_habilidades` (+ borrado) |
| Redes sociales | `/candidato/informacion/redes` | `candidato_info_redes` (+ editar/borrar) |

**Información básica** incluye, entre otros: documento, ciudad, sexo, fecha de nacimiento, teléfono, dirección, aspiración salarial, email, texto de perfil, **fit cultural** y **motivadores** (JSON), e **idiomas**.

### Indicadores de completitud

- **`personal_information_calculation`** (`applications.services.service_candidate`) calcula porcentajes por bloques: datos personales (campos puntuales), y “completado” binario para educación, experiencia y habilidades; devuelve un **`porcentaje_total`** (promedio de esos cuatro bloques).
- En la plantilla de **vacantes disponibles**, la lista amplia de vacantes y filtros se muestra cuando **`data_candidate.porcentaje_total > 50`** (`vacancy_available.html`).
- El modelo **`Can101Candidato.puede_aplicar()`** exige un umbral del **80%** según **`calcular_porcentaje()`**, que suma **35%** si hay registro académico, **35%** si hay experiencia laboral y **30%** si hay habilidades (en la práctica, **los tres bloques** para llegar al 100%). Conviene completar **academia + laboral + habilidades** antes de considerar el perfil listo para postular según esta regla de negocio.

---

## 5. Explorar vacantes abiertas

**Ruta:** `/vacante/disponibles/`  
**Nombre:** `vacantes:vacante_candidato_disponibles`  
**Vista:** `applications.vacante.views.candidate_views.vacancy_available`

- Lista vacantes con estado activo y **estado de vacante** en valores permitidos (`estado_vacante` en [1, 2] en la consulta).
- **Excluye** vacantes a las que el candidato ya aplicó.
- Permite **filtrar** por ciudad, experiencia requerida, profesión/estudio y palabras clave (`VacanteFiltro`).
- Hay endpoints AJAX para opciones y estadísticas de filtros: `vacantes:vacante_filtros_opciones` y `vacantes:vacante_filtros_estadisticas`.

Desde cada tarjeta, el botón **DETALLES** lleva al flujo de confirmación/aplicación en la app **`reclutados`**.

---

## 6. Aplicar a una vacante

### 6.1 Flujo principal (con preguntas de reclutamiento)

**Ruta:** `/reclutado/aplicar_vacante/<id_vacante>/`  
**Nombre:** `reclutados:reclutados_confirmar_aplicar_candidato`  
**Vista:** `applications.reclutado.views.candidate_views.confirm_apply_vacancy_recruited`

1. Requiere **`candidato_id`** en sesión; si no, redirige al inicio.
2. Muestra la vacante y un formulario dinámico **`PreguntasReclutamiento`** según la vacante.
3. Si el candidato **ya aplicó** a esa vacante, se marca estado en contexto (`centinel_vacante`) para no duplicar la acción desde la misma pantalla.
4. Al enviar el POST válido:
   - Se crea **`Cli056AplicacionVacante`** con estado de aplicación, respuestas en `preguntas_reclutamiento`, estado activo y opcionalmente usuario reclutador si aplica.
   - Se calculan y guardan **`json_match`** y **`json_match_inicial`** (emparejamiento candidato–vacante).
   - Se registra **historial** con `crear_historial_aplicacion`.

### 6.2 Flujo alternativo simplificado

**Ruta:** `/reclutado/aplicar_vacante/aplicar/<id_vacante>/`  
**Nombre:** `reclutados:reclutados_aplicar_candidato`  
**Vista:** `apply_vacancy_recruited_candidate`

Crea la aplicación sin el paso del formulario de preguntas (uso auxiliar en flujos específicos). Existe también en **`VacanteViews.vacante_aplicada`** un camino histórico `vacante_aplicada` para crear `Cli056AplicacionVacante` con otra plantilla.

---

## 7. Después de aplicar: seguimiento y documentación

**Mis aplicaciones**

- Listado: **`/vacante/aplicadas/candidato/`** — `vacantes:vacante_candidato_aplicadas`
- Detalle por aplicación: **`/vacante/aplicadas/detalle/<id_aplicacion>`** — `vacantes:vacante_candidato_aplicadas_detalle`

En el detalle el candidato puede gestionar, según el estado del proceso: **requisitos** (carga de documentos), **políticas internas** (respuestas y firma), **autorización de datos**, **video de perfil**, enlaces a PDFs generados, e información ligada a **entrevistas** asignadas.

**Acceso por enlace con token (documentación)**

- Prefijo: **`/reclutado/gestionar-documentacion/<token>/`** — validación del token y subida de documentos/video asociados sin depender solo de la sesión web habitual (`validar_token_documento` y rutas relacionadas en `reclutado/urls.py`).

---

## 8. Resumen visual del flujo

```text
Registro (/registro/candidato/)
    → Correo de bienvenida + token
    → Validar token (/validar_token/…)
Login (/login/)
    → /inicio/ → /candidato/inicio (dashboard)
Completar perfil (/candidato/informacion/…)
    → Ideal: academia + laboral + habilidades + datos básicos
Vacantes (/vacante/disponibles/)  [vista amplia si progreso > 50% en plantilla]
    → Confirmar y preguntas (/reclutado/aplicar_vacante/<id>/)
    → Cli056AplicacionVacante + match + historial
Seguimiento (/vacante/aplicadas/… + detalle)
    → Requisitos, políticas, autorización, entrevistas, token de documentación
```

---

## Referencias de código

- Registro y validación: `applications/usuarios/views/user_login/loginView.py`
- Dashboard candidato: `applications/usuarios/views/user_login/dashboardView.py`
- Perfil candidato: `applications/candidato/views/candidate_views.py`, `applications/candidato/urls.py`
- Vacantes disponibles y detalle de aplicación: `applications/vacante/views/candidate_views.py`, `applications/vacante/urls.py`
- Confirmación de aplicación y match: `applications/reclutado/views/candidate_views.py`, `applications/reclutado/urls.py`
- Completitud y datos agregados: `applications/services/service_candidate.py`
- Regla mínima para aplicar: `Can101Candidato.puede_aplicar` / `calcular_porcentaje` en `applications/candidato/models.py`
