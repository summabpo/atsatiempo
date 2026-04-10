# Descripción general de la plataforma ATS (atsatiempo)

Este documento **explica en conjunto** qué hace el sistema, **cómo encajan** los distintos actores y **cuál es el flujo completo** desde la configuración empresarial hasta el cierre de un proceso de selección. Sintetiza y ordena el contenido de:

- [`flujo-candidato.md`](flujo-candidato.md) — experiencia del candidato.
- [`flujo-headhunter-cliente.md`](flujo-headhunter-cliente.md) — Headhunter, empresas asignadas y parametrización.
- [`flujo-vacante-seleccion-entrevista.md`](flujo-vacante-seleccion-entrevista.md) — vacante, analista, reclutador, entrevistas y cliente.
- [`flujo-general-historias-usuario.md`](flujo-general-historias-usuario.md) — mapa por etapas y guía para historias de usuario y documentación de release.

La aplicación es un **ATS (Applicant Tracking System)** sobre **Django**: centraliza **oferta de vacantes**, **postulación y perfil de candidatos**, **selección por etapas** (reclutamiento, entrevistas, pruebas cuando aplique) y **visibilidad para la empresa contratante**, incluyendo el caso **Headhunter** que gestiona **clientes finales** como empresas separadas pero vinculadas.

---

## 1. Qué problema resuelve la plataforma

La plataforma permite:

1. **A las empresas (y a un Headhunter en nombre de terceros)** definir **cargos, requisitos, pruebas y políticas**, publicar **vacantes** y hacer seguimiento del **pipeline** de cada postulación.
2. **A los candidatos** registrarse, validar identidad por correo, **completar un perfil** con reglas de completitud, **buscar vacantes**, **aplicar** (con preguntas dinámicas y cálculo de *match*) y **dar seguimiento** a requisitos, documentación, políticas y entrevistas.
3. **A los roles internos** (analista de selección, reclutador, entrevistador) **trabajar en paralelo**: asignación por vacante, embudo de reclutamiento, programación y resultado de entrevistas, con **historial** sobre la aplicación.
4. **Al cliente empresa** ver **métricas**, candidatos por estado, límites de presentación (por ejemplo *terna* / `cantidad_presentar`) y el **cierre lógico** del proceso según estados definidos en catálogo.

El **alcance funcional** descrito en la documentación llega hasta el **cierre del proceso de selección en la plataforma** (estados finales de aplicación y de vacante). **No** se detalla aquí la contratación formal fuera del sistema (firma de contrato en el mundo real).

---

## 2. Actores principales (visión de producto)

| Actor | Rol en el sistema |
|-------|-------------------|
| **Administrador ATS** | Alta de clientes (incluido tipo Headhunter), soporte, rutas con permiso `acceso_admin`. |
| **Cliente Standard** | Empresa que usa el ATS de forma directa; vacantes bajo el patrón maestro sistema (`1000`) y asignación tipo estándar. |
| **Cliente Headhunter** | Empresa que **gestiona empresas finales** (“clientes asignados”) mediante `Cli064AsignacionCliente` con **tipo asignación Headhunter**. |
| **Cliente asignado** | Empresa final vinculada a un Headhunter; las vacantes pueden asociarse al **maestro** (Headhunter en sesión) y **asignado** (empresa final). |
| **Candidato** | Usuario de grupo candidato; registro, perfil, vacantes, aplicaciones. |
| **Analista de selección** | Ve y gestiona vacantes donde es `usuario_asignado`; rutas de analista cliente o analista ATS interno. |
| **Reclutador** | Asignado por vacante (`asignacion_reclutador`); mueve candidatos en el **embudo** `estado_reclutamiento` y coordina hacia entrevista. |
| **Entrevistador del cliente** | Permiso `acceso_cliente_entrevistador`; gestiona citas (`Cli057AsignacionEntrevista`) y resultados que impactan `estado_aplicacion`. |

Los **tipos de cliente** (`'1'` Standard, `'2'` Headhunter, `'3'` asignado a Headhunter) y las **asignaciones** entre maestro y asignado están detallados en [`flujo-headhunter-cliente.md`](flujo-headhunter-cliente.md).

---

## 3. Flujo completo en la práctica (de principio a fin)

### 3.1 Preparación del ecosistema empresarial

Antes de que un candidato vea vacantes útiles, el sistema necesita **empresas** y, si aplica, **relaciones maestro–asignado**.

- Un **administrador** puede crear un **cliente Headhunter** desde el panel (`/cliente/crear/`, etc.) y asociar un **usuario de portal** (grupo cliente) al registro `Cli051Cliente` correspondiente.
- El **Headhunter** registra o vincula **clientes finales** por **NIT** en `/cliente/asignados/`: se reutiliza o crea el cliente tipo asignado y se crea la **asignación** Headhunter si no existía.
- **Parametrización**: cargos (`Cli068Cargo`), requisitos por cargo, pruebas, políticas internas, requisitos en catálogo, grupo de trabajo. Para el **cliente asignado**, las rutas con **`pk`** del cliente permiten configurar esa empresa; las rutas **sin** `pk` actúan sobre el **`cliente_id` de sesión** (en un Headhunter, típicamente el propio Headhunter, no el asignado automáticamente). Este matiz está explicado en [`flujo-headhunter-cliente.md`](flujo-headhunter-cliente.md) §5.

### 3.2 La vacante como unidad central

La **vacante** (`Cli052Vacante`) conecta **asignación cliente** (`Cli064AsignacionCliente`), **cargo**, **perfil**, skills, fit cultural, y campos operativos como **analista** (`usuario_asignado`), **reclutador** (`asignacion_reclutador`), historiales JSON de asignaciones, **cantidad a presentar** al cliente y **estado de vacante**.

- Puede crearse desde **admin**, desde **cliente / Headhunter** (`/vacante/mis_vacantes/crear/<pk>/`, etc.). La lógica `_asignacion_cliente_para_vacante_desde_admin` distingue **portal cliente (grupo 3)**: maestro = sesión, asignado = `pk`, tipo asignación `'2'` (Headhunter); frente a otros casos con maestro `1000` y tipo `'1'`.

Una vez existe la vacante en estados adecuados, el **analista** queda definido para listados y edición; el **reclutador** para el embudo y la coordinación con entrevistas. Detalle en [`flujo-vacante-seleccion-entrevista.md`](flujo-vacante-seleccion-entrevista.md) §1–3.

### 3.3 Recorrido del candidato

El candidato **se registra** (`/registro/candidato/`), recibe **token** por correo y debe **validar** antes de un login pleno. Tras login, accede al **dashboard** (`/candidato/inicio`) con resumen de perfil y vacantes sugeridas.

Completa **perfil** en `/candidato/...`: datos básicos, formación, experiencia, habilidades, redes, archivos. El sistema calcula **porcentajes de completitud**; para **aplicar** rige una regla agregada (por ejemplo **80%** vía `puede_aplicar` / `calcular_porcentaje`). La vista amplia de vacantes disponibles puede condicionarse a un umbral en plantilla (por ejemplo **> 50%**).

En **vacantes disponibles** (`/vacante/disponibles/`) filtra y ve ofertas a las que **no** ha aplicado. Al aplicar (`/reclutado/aplicar_vacante/<id>/`), responde **preguntas de reclutamiento**, se crea **`Cli056AplicacionVacante`**, **match** (`json_match`, `json_match_inicial`) e **historial** de aplicación.

**Después de aplicar**, en “mis aplicaciones” y el **detalle**, gestiona **requisitos**, **políticas**, **autorización de datos**, **video**, PDFs y **entrevistas**; existe además acceso por **token** para documentación (`/reclutado/gestionar-documentacion/<token>/`). Todo el detalle está en [`flujo-candidato.md`](flujo-candidato.md).

### 3.4 Selección interna: embudo, entrevistas y cliente

- **Reclutador**: ve sus vacantes asignadas y, por vacante, columnas según **`estado_reclutamiento`**: Aspirantes → Precalificados → **Aprobados para Entrevista** → No aprobados por CV. En el **detalle del reclutado** actualiza estado, comentarios e historial `registro_reclutamiento`.
- **Programación de entrevista**: crea **`Cli057AsignacionEntrevista`** y actualiza vía **`crear_historial_aplicacion`** el **`estado_aplicacion`** (por ejemplo hacia “Entrevista programada”).
- **`estado_aplicacion`** cubre el ciclo: aplicado, entrevista (programada / aprobada / no aprobada), pruebas, seleccionado, finalizada, cancelaciones y **Seleccionado por Cliente**, entre otros (catálogo en `choices`).
- **Entrevistador**: lista sus entrevistas y las gestiona; los resultados alimentan de nuevo historial y estados.
- **Cliente** en **detalle de vacante** (`/vacante/detalle/<pk>/`): paneles por embudo, métricas por `estado_aplicacion`, candidatos en seleccionado / seleccionado por cliente, **`cantidad_presentar`**, y vista de entrevistas de la vacante.

El cierre se reconoce cuando la **vacante** pasa a finalizada/cancelada y/o las **aplicaciones** alcanzan estados terminales (finalizada, seleccionado, descartes, etc.), según [`flujo-vacante-seleccion-entrevista.md`](flujo-vacante-seleccion-entrevista.md) §8–9.

---

## 4. Conceptos transversales que unen todo el sistema

- **`Cli064AsignacionCliente`**: modela quién es **maestro** y quién **asignado** y con **qué tipo** de asignación; es la base para Headhunter → empresa final y para ligar **vacantes** al par correcto.
- **`Cli056AplicacionVacante`**: cada postulación; conecta candidato, vacante, estados, match y trazabilidad.
- **`estado_reclutamiento`**: embudo “operativo” del reclutador (CV / listo para entrevista / descartado por CV).
- **`estado_aplicacion`**: ciclo de vida **global** de la postulación en el ATS (entrevistas, pruebas, selección, cierres).
- **Historial** (`crear_historial_aplicacion`, `Cli063AplicacionVacanteHistorial`): auditoría de cambios relevantes sobre la aplicación.

---

## 5. Diagrama resumido del flujo end-to-end

```text
[Configuración empresa] → Clientes, Headhunter, asignados, parametrización (cargos, requisitos, políticas, pruebas)
        ↓
[Vacante] → Asignación analista y reclutador → Publicación / operación
        ↓
[Candidato] → Registro → Validación correo → Perfil → Vacantes → Aplicación (preguntas + match + historial)
        ↓
[Reclutador] → Embudo estado_reclutamiento → Entrevistas programadas
        ↓
[Entrevistador / otros roles] → Resultados → estado_aplicacion actualizado
        ↓
[Cliente] → Detalle vacante, métricas, presentación al cliente, seguimiento
        ↓
[Cierre] → Estados finales de aplicación y vacante (alcance dentro del ATS)
```

---

## 6. Documentación complementaria y uso recomendado

| Documento | Utilidad |
|-----------|----------|
| [`flujo-candidato.md`](flujo-candidato.md) | Rutas, permisos y reglas de perfil/aplicación del candidato. |
| [`flujo-headhunter-cliente.md`](flujo-headhunter-cliente.md) | Modelo de negocio Headhunter, NIT, vacantes por asignación, parametrización por `pk`. |
| [`flujo-vacante-seleccion-entrevista.md`](flujo-vacante-seleccion-entrevista.md) | Operación de vacante, analista, reclutador, entrevista, cliente y tablas de estados. |
| [`flujo-general-historias-usuario.md`](flujo-general-historias-usuario.md) | Enumeración por etapas (A.1–A.4), plantilla de HU y buenas prácticas de documentación. |

Para **onboarding** de producto o negocio, este archivo (**descripción general**) ofrece la narrativa; para **implementación o QA**, conviene ir al **flujo específico** y a las referencias de código que cada uno incluye.

---

## 7. Notas y límites conocidos (según la documentación fuente)

- Existe una **colisión de nombre de URL** `cliente_detalle` en `cliente/urls.py` que puede afectar accesos si solo se usa ese nombre sin `acceso_admin`; se recomiendan rutas explícitas con `pk` (véase [`flujo-headhunter-cliente.md`](flujo-headhunter-cliente.md) §5.3).
- En **entrevistador**, conviene **alinear permisos** entre listado y gestión en despliegue (nota en [`flujo-vacante-seleccion-entrevista.md`](flujo-vacante-seleccion-entrevista.md) §7).

---

*Documento de síntesis. Mantenerlo alineado con los flujos detallados en `docs/` cuando cambien reglas de negocio, URLs o permisos.*
