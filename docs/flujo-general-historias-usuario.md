# Flujo general del ATS (atsatiempo) — guía para historias de usuario y documentación

Este documento **integra** los flujos descritos en:

- [`flujo-candidato.md`](flujo-candidato.md) — recorrido del candidato.
- [`flujo-headhunter-cliente.md`](flujo-headhunter-cliente.md) — Headhunter, clientes asignados y parametrización.
- [`flujo-vacante-seleccion-entrevista.md`](flujo-vacante-seleccion-entrevista.md) — vacante, analista, reclutador, entrevista y cliente.

Sirve como **mapa maestro numerado** y como **procedimiento** para derivar historias de usuario (HU) y documentación funcional de forma coherente.

---

## Parte A — Flujo end-to-end enumerado (visión de producto)

Cada bloque puede descomponerse en varias historias de usuario; el número indica **orden lógico** del proceso, no obligatoriamente orden de implementación.

### A.1 Capa empresa / Headhunter (antes de que exista la vacante visible al candidato)

| # | Etapa | Resumen | Doc de referencia |
|---|--------|---------|-------------------|
| A.1.1 | Alta cliente Headhunter | Creación de `Cli051Cliente` tipo Headhunter (`'2'`) y usuario portal; asignación maestro sistema. | `flujo-headhunter-cliente` §2 |
| A.1.2 | Cliente asignado | Por NIT: buscar o crear cliente tipo asignado (`'3'`) y `Cli064AsignacionCliente` tipo Headhunter (`'2'`). | `flujo-headhunter-cliente` §3 |
| A.1.3 | Parametrización del cliente | Cargos, requisitos, pruebas, políticas, grupo de trabajo; rutas con `pk` del cliente asignado cuando aplica. | `flujo-headhunter-cliente` §5 |

### A.2 Vacante y roles internos

| # | Etapa | Resumen | Doc de referencia |
|---|--------|---------|-------------------|
| A.2.1 | Creación de vacante | `Cli052Vacante` con asignación cliente según rol (admin, cliente, Headhunter con `pk`). | `flujo-vacante-seleccion-entrevista` §1 |
| A.2.2 | Asignación analista | `usuario_asignado`, historial en `data_asignacion_usuario`; listados del analista. | `flujo-vacante-seleccion-entrevista` §2 |
| A.2.3 | Asignación reclutador | `asignacion_reclutador`, historial en `data_asignacion_reclutador`; listado reclutador. | `flujo-vacante-seleccion-entrevista` §3 |

### A.3 Candidato (autogestión)

| # | Etapa | Resumen | Doc de referencia |
|---|--------|---------|-------------------|
| A.3.1 | Registro y validación | Registro candidato, token, verificación de correo; reenvío de token. | `flujo-candidato` §1–2 |
| A.3.2 | Login y dashboard | Entrada a `/candidato/inicio`, datos de sesión. | `flujo-candidato` §3 |
| A.3.3 | Perfil | Información básica, académica, laboral, habilidades, etc.; reglas de completitud y `puede_aplicar`. | `flujo-candidato` §4 |
| A.3.4 | Exploración de vacantes | Listado, filtros, exclusión de ya aplicadas. | `flujo-candidato` §5 |
| A.3.5 | Postulación | Formulario de preguntas, `Cli056AplicacionVacante`, match, historial. | `flujo-candidato` §6 |
| A.3.6 | Seguimiento post-aplicación | Aplicadas, detalle, requisitos, políticas, documentación por token. | `flujo-candidato` §7 |

### A.4 Selección: embudo, entrevista y cierre

| # | Etapa | Resumen | Doc de referencia |
|---|--------|---------|-------------------|
| A.4.1 | Embudo reclutamiento | Estados `estado_reclutamiento` 1–4; detalle reclutador por aplicación. | `flujo-vacante-seleccion-entrevista` §4–5 |
| A.4.2 | Entrevista | Programación `Cli057AsignacionEntrevista`, historial de aplicación. | `flujo-vacante-seleccion-entrevista` §6 (parcial) |
| A.4.3 | Entrevistador | Listado y gestión; actualización `estado_asignacion` y `estado_aplicacion`. | `flujo-vacante-seleccion-entrevista` §7 |
| A.4.4 | Cliente | Detalle vacante, métricas, candidatos seleccionados, entrevistas, `cantidad_presentar`. | `flujo-vacante-seleccion-entrevista` §8 |
| A.4.5 | Fin de proceso | Estados terminales `estado_aplicacion` y vida de vacante (`estado_vacante`). | `flujo-vacante-seleccion-entrevista` §9 |

---

## Parte B — Pasos para generar historias de usuario

Usar este checklist por cada **actor** (candidato, Headhunter, cliente asignado, analista, reclutador, entrevistador, admin ATS).

### B.1 Preparación

1. **Elegir el tramo del flujo** en la Parte A (por ejemplo A.3.3 Perfil).
2. **Abrir el doc específico** en `docs/` y localizar rutas, nombres de URL y reglas de negocio citadas.
3. **Identificar actor y objetivo** en una frase: quién necesita qué resultado observable.

### B.2 Redacción de la historia (plantilla)

Para cada HU, completar:

- **Título:** verbo + objeto (ej.: “Postular a una vacante con preguntas de reclutamiento”).
- **Como** \<actor\>  
- **Quiero** \<acción o capacidad\>  
- **Para** \<beneficio o resultado de negocio\>

**Criterios de aceptación** (lista verificable):

- Dado \<contexto previo\>…
- Cuando \<acción del usuario o evento\>…
- Entonces \<resultado en pantalla, datos o estado del sistema\>…

Incluir cuando aplique: permisos, mensajes de error, redirecciones, límites (porcentajes, estados), integraciones (correo, token).

### B.3 Trazabilidad con el código (opcional pero recomendable)

- Anotar **nombre de URL Django** (`namespace:name`) y **archivo de vista** tomados del doc fuente.
- Si la HU implica cambio de modelo, citar modelo y campo (`applications/.../models.py`).

### B.4 Priorización sugerida

1. **Fundamentos de identidad:** registro/login/validación (A.3.1–A.3.2).
2. **Oferta laboral:** creación vacante y publicación efectiva (A.2.x alineado con estados de vacante).
3. **Conversión candidato:** perfil mínimo para aplicar y postulación (A.3.3–A.3.5).
4. **Operación selección:** embudo, entrevista, cliente (A.4.x).
5. **Casos especiales:** Headhunter y clientes asignados (A.1.x) según alcance del release.

---

## Parte C — Pasos para documentación funcional / técnica

1. **Mantener los tres documentos de flujo** actualizados cuando cambien URLs, permisos o reglas de negocio.
2. **Este documento general** debe actualizarse si se agregan etapas nuevas en la Parte A o se redefine el orden del proceso.
3. **Por módulo liberado**, añadir un anexo corto: alcance, HU cubiertas, riesgos conocidos (ej.: colisión de nombres URL mencionada en `flujo-headhunter-cliente` §5.3).
4. **Glosario mínimo** en documentación de release: `estado_aplicacion`, `estado_reclutamiento`, tipos de cliente, `Cli064AsignacionCliente`.

---

## Parte D — Ejemplos de historias derivadas (orientación)

| ID ref. | Ejemplo de título | Actor |
|---------|-------------------|--------|
| A.3.1 | Validar correo con token antes del primer acceso exitoso | Candidato |
| A.1.2 | Registrar cliente asignado por NIT y vincularlo al Headhunter en sesión | Headhunter |
| A.2.2 | Asignar analista de selección a una vacante con registro en historial | Cliente / admin |
| A.4.1 | Mover candidato a “Aprobados para Entrevista” en el embudo | Reclutador |
| A.4.3 | Registrar resultado de entrevista que actualice estado de aplicación | Entrevistador |

*(Los títulos son ilustrativos; las HU definitivas deben incluir criterios de aceptación completos.)*

---

## Parte E — Diagrama de relación entre documentos

```text
flujo-general-historias-usuario.md (este archivo)
    ├── flujo-candidato.md .............. A.3 y enlaces a postulación/seguimiento
    ├── flujo-headhunter-cliente.md ..... A.1, parametrización, vacantes HH
    └── flujo-vacante-seleccion-entrevista.md ... A.2, A.4, estados y entrevistas
```

---

## Referencia rápida de archivos de código (consolidado)

| Área | Ubicación típica |
|------|------------------|
| Acceso y dashboard | `applications/usuarios/views/user_login/` |
| Perfil candidato | `applications/candidato/` |
| Vacantes | `applications/vacante/` |
| Reclutamiento / aplicación | `applications/reclutado/` |
| Entrevistas | `applications/entrevista/` |
| Cliente / asignaciones | `applications/cliente/` |
| Reglas y catálogos | `applications/services/choices.py`, modelos en `applications/*/models.py` |

---

*Última alineación con los documentos en `docs/` del repositorio. Actualizar este índice cuando el producto evolucione.*
