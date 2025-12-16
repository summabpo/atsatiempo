# HISTORIAS DE USUARIO - MÓDULO DE RECLUTADOR

## ÍNDICE
1. [Ajuste de Base de Datos para Perfil de Reclutador](#1-ajuste-de-base-de-datos-para-perfil-de-reclutador)
2. [Ajuste de Views para Reutilización](#2-ajuste-de-views-para-reutilización)
3. [Creación de Dashboard para Reclutador](#3-creación-de-dashboard-para-reclutador)
4. [Listado de Vacantes Asignadas](#4-listado-de-vacantes-asignadas-por-el-reclutador)
5. [Interfaz Detalle de Vacante y Listado de Personal Reclutado](#5-interfaz-detalle-de-vacante-y-listado-de-personal-reclutado)
6. [Detalle de Reclutado e Historial de Aplicaciones](#6-detalle-de-reclutado-e-historial-de-aplicaciones)
7. [Listado Seccionado de Etapas de Reclutamiento](#7-listado-seccionado-de-etapas-de-reclutamiento)
8. [Regla de Negocio y Codificación del MATCH](#8-regla-de-negocio-y-codificación-del-match)
9. [Consulta de Listado de Candidatos por Calificación de Match](#9-consulta-de-listado-de-candidatos-por-calificación-de-match)
10. [Agregar Filtros por Búsqueda](#10-agregar-filtros-por-búsqueda)
11. [Generar Navegación entre Candidatos](#11-generar-navegación-entre-candidatos)
12. [Envío al WhatsApp desde PC](#12-envío-al-whatsapp-desde-pc)
13. [Ajustar Listado de Entrevistas y Generación Masiva](#13-ajustar-listado-de-entrevistas-y-generación-masiva)
14. [Crear Formulario de Entrevista con Etapas](#14-crear-formulario-de-entrevista-con-etapas)
15. [Ajustar Informe Final con Calificaciones](#15-ajustar-informe-final-con-calificaciones)
16. [Ajuste Data de Estilo de Trabajo Dominante](#16-ajuste-data-de-estilo-de-trabajo-dominante)
17. [Ajuste Data de Ritmo de Trabajo](#17-ajuste-data-de-ritmo-de-trabajo)
18. [Ajuste Data de Tipo de Liderazgo](#18-ajuste-data-de-tipo-de-liderazgo)

---

## 1. AJUSTE DE BASE DE DATOS PARA PERFIL DE RECLUTADOR

### Historia de Usuario 1.1: Crear Modelo de Perfil de Reclutador
**Como** administrador del sistema  
**Quiero** crear un nuevo modelo de perfil de reclutador en la base de datos  
**Para** poder gestionar usuarios con rol de reclutador y sus datos específicos

**Criterios de Aceptación:**
- Se debe crear un modelo `RecReclutador` que extienda o se relacione con `UsuarioBase`
- El modelo debe incluir campos como: especialización, años_experiencia, estado_activo, fecha_creacion
- Debe existir una relación Many-to-Many o ForeignKey con `Cli052Vacante` para las vacantes asignadas
- El modelo debe tener métodos para obtener estadísticas del reclutador (vacantes asignadas, candidatos gestionados, etc.)
- Se debe crear la migración correspondiente
- El modelo debe estar registrado en el admin de Django

**Tareas Técnicas:**
- Crear modelo `RecReclutador` en `applications/usuarios/models.py` o crear nueva app `reclutador`
- Definir relación con `UsuarioBase` mediante ForeignKey o OneToOne
- Crear relación con `Cli052Vacante` para asignación de vacantes
- Generar migración: `python manage.py makemigrations`
- Registrar modelo en admin

---

### Historia de Usuario 1.2: Asignar Vacantes a Reclutador
**Como** administrador del sistema  
**Quiero** poder asignar vacantes a reclutadores específicos  
**Para** distribuir la carga de trabajo y responsabilidades

**Criterios de Aceptación:**
- Se debe poder asignar una o múltiples vacantes a un reclutador
- La asignación debe registrarse con fecha y usuario que realiza la asignación
- Se debe poder consultar todas las vacantes asignadas a un reclutador
- Se debe poder reasignar vacantes entre reclutadores
- El sistema debe notificar al reclutador cuando se le asigna una nueva vacante

**Tareas Técnicas:**
- Crear modelo `RecAsignacionVacante` con ForeignKey a `RecReclutador` y `Cli052Vacante`
- Agregar campo `reclutador_asignado` en `Cli052Vacante` como ForeignKey a `RecReclutador`
- Crear vista para asignación masiva de vacantes
- Implementar señal (signal) para notificación de asignación

---

## 2. AJUSTE DE VIEWS PARA REUTILIZACIÓN

### Historia de Usuario 2.1: Refactorizar Views de Información del Reclutador
**Como** desarrollador  
**Quiero** refactorizar las views existentes para que sean reutilizables  
**Para** evitar duplicación de código y facilitar el mantenimiento

**Criterios de Aceptación:**
- Crear views genéricas o funciones de utilidad para obtener información del reclutador
- Las views deben poder ser utilizadas tanto por el perfil de reclutador como por otros perfiles
- Se debe crear un servicio `service_recruiter.py` con funciones reutilizables
- Las funciones deben incluir: obtener_vacantes_asignadas, obtener_candidatos_gestionados, obtener_estadisticas_reclutador
- Se debe mantener compatibilidad con las views existentes

**Tareas Técnicas:**
- Crear archivo `applications/services/service_recruiter.py`
- Extraer lógica común de views existentes a funciones de servicio
- Crear decoradores o mixins para validar permisos de reclutador
- Refactorizar views existentes para usar los nuevos servicios
- Crear tests unitarios para las funciones de servicio

---

### Historia de Usuario 2.2: Crear Views Base para Reclutador
**Como** desarrollador  
**Quiero** crear views base específicas para el módulo de reclutador  
**Para** establecer una estructura consistente y reutilizable

**Criterios de Aceptación:**
- Crear clase base `RecruiterBaseView` con decoradores y permisos comunes
- Implementar mixins para funcionalidades comunes (obtener reclutador actual, validar asignación, etc.)
- Las views deben validar que el usuario tenga rol de reclutador
- Debe existir un decorador `@validar_permisos_reclutador` para validar acceso

**Tareas Técnicas:**
- Crear `applications/reclutador/views/base_views.py`
- Implementar clase base y mixins
- Crear decorador de permisos
- Documentar uso de las views base

---

## 3. CREACIÓN DE DASHBOARD PARA RECLUTADOR

### Historia de Usuario 3.1: Dashboard Principal del Reclutador
**Como** reclutador  
**Quiero** visualizar un dashboard con información relevante de mis actividades  
**Para** tener una visión general de mi trabajo y gestionar eficientemente mis tareas

**Criterios de Aceptación:**
- El dashboard debe mostrar métricas clave: vacantes asignadas, candidatos en proceso, entrevistas programadas, match promedio
- Debe incluir gráficos visuales (barras, pastel, líneas) para estadísticas
- Debe mostrar lista de tareas pendientes (entrevistas próximas, candidatos por revisar)
- Debe tener acceso rápido a acciones frecuentes (crear entrevista, revisar candidatos, ver vacantes)
- El dashboard debe ser responsivo y cargar rápidamente
- Debe mostrar notificaciones de actividades recientes

**Tareas Técnicas:**
- Crear view `dashboard_recruiter` en `applications/reclutador/views/dashboard_views.py`
- Crear template `templates/admin/reclutador/dashboard.html`
- Implementar consultas optimizadas para métricas
- Integrar librería de gráficos (Chart.js o similar)
- Crear componentes reutilizables para métricas
- Implementar cache para datos que no cambian frecuentemente

---

### Historia de Usuario 3.2: Widgets de Actividad Reciente
**Como** reclutador  
**Quiero** ver un resumen de mis actividades recientes en el dashboard  
**Para** estar al día con los cambios y acciones pendientes

**Criterios de Aceptación:**
- Mostrar últimas 10 aplicaciones recibidas en mis vacantes
- Mostrar próximas 5 entrevistas programadas
- Mostrar candidatos que requieren revisión (nuevos matches, cambios de estado)
- Mostrar vacantes que están próximas a cerrar
- Cada item debe tener un enlace a su detalle correspondiente
- Debe actualizarse automáticamente o tener botón de refrescar

**Tareas Técnicas:**
- Crear función `obtener_actividades_recientes` en servicio
- Implementar widgets en template del dashboard
- Crear vistas AJAX para actualización dinámica
- Implementar paginación o scroll infinito si es necesario

---

## 4. LISTADO DE VACANTES ASIGNADAS POR EL RECLUTADOR

### Historia de Usuario 4.1: Listar Vacantes Asignadas
**Como** reclutador  
**Quiero** ver un listado de todas las vacantes que me han sido asignadas  
**Para** gestionar eficientemente mis responsabilidades de reclutamiento

**Criterios de Aceptación:**
- El listado debe mostrar: título de vacante, cliente, fecha de asignación, estado, número de candidatos, match promedio
- Debe permitir filtrar por estado de vacante (Activa, En Proceso, Finalizada, Cancelada)
- Debe permitir ordenar por fecha de asignación, título, estado
- Debe mostrar indicadores visuales del progreso (candidatos seleccionados vs requeridos)
- Cada vacante debe tener un enlace a su detalle
- Debe incluir búsqueda por texto (título, cliente)

**Tareas Técnicas:**
- Crear view `listar_vacantes_asignadas` en `applications/reclutador/views/vacante_views.py`
- Crear template con tabla responsive
- Implementar filtros y búsqueda con Django Filter
- Crear paginación
- Optimizar consultas con select_related y prefetch_related

**NOTA:** Se debe preguntar al usuario cómo será la asignación de vacantes (manual por admin, automática por algoritmo, por cliente, etc.)

---

### Historia de Usuario 4.2: Detalle de Vacante Asignada
**Como** reclutador  
**Quiero** ver el detalle completo de una vacante asignada  
**Para** entender todos los requisitos y gestionar mejor el proceso de selección

**Criterios de Aceptación:**
- Debe mostrar toda la información de la vacante (perfil, requisitos, habilidades, fit cultural)
- Debe mostrar estadísticas: total aplicaciones, en proceso, seleccionados, match promedio
- Debe tener acceso rápido a: listado de candidatos, crear entrevista, ver matches
- Debe mostrar historial de acciones realizadas en la vacante
- Debe permitir actualizar notas o comentarios sobre la vacante

**Tareas Técnicas:**
- Crear view `detalle_vacante_asignada`
- Reutilizar componentes de detalle existentes si es posible
- Agregar sección de notas/comentarios del reclutador
- Implementar acciones rápidas (botones para acciones frecuentes)

---

## 5. INTERFAZ DETALLE DE VACANTE Y LISTADO DE PERSONAL RECLUTADO

### Historia de Usuario 5.1: Vista Detallada de Vacante con Candidatos
**Como** reclutador  
**Quiero** ver el detalle de una vacante junto con el listado de candidatos que han aplicado  
**Para** evaluar y gestionar el proceso de selección de manera integral

**Criterios de Aceptación:**
- La vista debe mostrar información completa de la vacante en la parte superior
- Debe mostrar listado de candidatos con: nombre, match percentage, estado de aplicación, fecha de aplicación
- Debe permitir filtrar candidatos por: estado, rango de match, fecha de aplicación
- Debe permitir ordenar por match, fecha, nombre
- Cada candidato debe tener acciones rápidas: ver perfil, programar entrevista, cambiar estado
- Debe mostrar indicadores visuales del match (barra de progreso, colores)

**Tareas Técnicas:**
- Crear view `detalle_vacante_candidatos`
- Integrar componente de listado de candidatos
- Implementar filtros y ordenamiento
- Crear acciones rápidas con modales o dropdowns
- Optimizar consultas para evitar N+1 queries

---

### Historia de Usuario 5.2: Listado de Personal Reclutado por Vacante
**Como** reclutador  
**Quiero** ver un listado de todos los candidatos que han sido reclutados para mis vacantes  
**Para** hacer seguimiento y generar reportes de mis resultados

**Criterios de Aceptación:**
- Debe mostrar: nombre candidato, vacante, fecha de reclutamiento, estado actual
- Debe permitir filtrar por: vacante, fecha, estado de reclutado
- Debe mostrar estadísticas: total reclutados, por vacante, por mes
- Debe permitir exportar el listado a Excel o PDF
- Cada reclutado debe tener enlace a su detalle completo

**Tareas Técnicas:**
- Crear view `listar_personal_reclutado`
- Implementar filtros con Django Filter
- Crear función de exportación
- Agregar gráficos de estadísticas
- Crear template responsive

---

## 6. DETALLE DE RECLUTADO E HISTORIAL DE APLICACIONES

### Historia de Usuario 6.1: Vista Detallada del Reclutado
**Como** reclutador  
**Quiero** ver el detalle completo de un candidato reclutado  
**Para** tener toda la información necesaria para el seguimiento y reportes

**Criterios de Aceptación:**
- Debe mostrar información personal completa del candidato
- Debe mostrar información de la vacante para la cual fue reclutado
- Debe mostrar fecha de reclutamiento y estado actual
- Debe mostrar calificaciones de la entrevista si fueron realizadas
- Debe mostrar match percentage y detalles del match
- Debe permitir agregar notas o comentarios sobre el reclutado

**Tareas Técnicas:**
- Crear view `detalle_reclutado`
- Reutilizar componentes de detalle de candidato existentes
- Integrar información de entrevista y match
- Agregar formulario para notas del reclutador

---

### Historia de Usuario 6.2: Historial de Aplicaciones del Candidato
**Como** reclutador  
**Quiero** ver el historial completo de aplicaciones de un candidato  
**Para** entender su trayectoria y experiencia en el proceso de selección

**Criterios de Aceptación:**
- Debe mostrar todas las aplicaciones del candidato (incluso a otras vacantes)
- Para cada aplicación debe mostrar: vacante, fecha, estado, match, reclutador asignado
- Debe mostrar el historial de cambios de estado con fechas y usuarios
- Debe mostrar resultados de entrevistas y pruebas si las hay
- Debe estar ordenado cronológicamente (más reciente primero)
- Debe permitir filtrar por estado o vacante

**Tareas Técnicas:**
- Crear view `historial_aplicaciones_candidato`
- Consultar modelo `Cli063AplicacionVacanteHistorial`
- Crear componente de timeline para visualizar historial
- Integrar información de entrevistas y pruebas

---

## 7. LISTADO SECCIONADO DE ETAPAS DE RECLUTAMIENTO

### Historia de Usuario 7.1: Vista Kanban de Etapas de Reclutamiento
**Como** reclutador  
**Quiero** ver los candidatos organizados por etapas del proceso de reclutamiento  
**Para** gestionar visualmente el flujo de trabajo y mover candidatos entre etapas

**Criterios de Aceptación:**
- Debe mostrar columnas para cada etapa: Aplicado, Entrevista Programada, Entrevista Aprobada, Prueba Programada, Prueba Superada, Seleccionado
- Cada candidato debe aparecer como una tarjeta en la columna correspondiente a su estado
- Debe permitir arrastrar y soltar (drag & drop) candidatos entre etapas
- Cada tarjeta debe mostrar: foto, nombre, match percentage, vacante
- Debe mostrar contador de candidatos por etapa
- Debe permitir filtrar por vacante específica

**Tareas Técnicas:**
- Crear view `kanban_etapas_reclutamiento`
- Implementar frontend con librería de drag & drop (SortableJS, Dragula, etc.)
- Crear endpoint AJAX para actualizar estado al mover candidato
- Implementar validaciones de transición de estados
- Crear template con diseño tipo Kanban

**NOTA:** Se debe preguntar al usuario qué etapas específicas se manejan según el proceso que se hace con el candidato

---

### Historia de Usuario 7.2: Vista de Lista por Etapas
**Como** reclutador  
**Quiero** ver los candidatos en formato de lista agrupados por etapa  
**Para** tener una vista alternativa más detallada del proceso

**Criterios de Aceptación:**
- Debe mostrar secciones colapsables para cada etapa
- Cada sección debe mostrar lista de candidatos con más información
- Debe permitir cambiar etapa desde la lista (dropdown o botones)
- Debe mostrar estadísticas por etapa (total, porcentaje del total)
- Debe permitir exportar candidatos de una etapa específica

**Tareas Técnicas:**
- Crear view `lista_etapas_reclutamiento`
- Implementar componentes colapsables (acordeón)
- Crear acciones masivas para cambiar etapa de múltiples candidatos
- Agregar funcionalidad de exportación

---

## 8. REGLA DE NEGOCIO Y CODIFICACIÓN DEL MATCH

### Historia de Usuario 8.1: Establecer Reglas de Negocio para el Match
**Como** administrador del sistema  
**Quiero** definir y configurar las reglas de negocio para el cálculo del match  
**Para** que el sistema calcule correctamente la compatibilidad entre candidatos y vacantes

**Criterios de Aceptación:**
- Se debe documentar las reglas de negocio del match (pesos, criterios, umbrales)
- Los criterios deben incluir: Hard Skills, Soft Skills, Experiencia, Educación, Fit Cultural, Ubicación, Salario
- Se debe definir la ponderación de cada criterio (porcentajes)
- Se debe establecer umbrales mínimos de match para considerar un candidato apto
- Las reglas deben ser configurables (preferiblemente desde admin o configuración)
- Se debe crear documentación técnica del algoritmo

**Tareas Técnicas:**
- Revisar y documentar algoritmo existente en `components/EmparejamientoVacantesCandidato.py`
- Crear archivo de configuración para pesos y umbrales
- Refactorizar código del match para que sea más mantenible
- Crear tests unitarios para validar el cálculo del match
- Documentar reglas de negocio en archivo markdown

---

### Historia de Usuario 8.2: Implementar Cálculo de Match Mejorado
**Como** desarrollador  
**Quiero** mejorar la implementación del cálculo de match  
**Para** que sea más preciso, eficiente y mantenible

**Criterios de Aceptación:**
- El cálculo debe considerar todos los criterios definidos en las reglas de negocio
- Debe retornar un JSON estructurado con el desglose del match por criterio
- Debe ser eficiente (evitar consultas N+1, usar cache cuando sea apropiado)
- Debe guardar el resultado del match en `json_match` de `Cli056AplicacionVacante`
- Debe recalcular automáticamente cuando cambien datos relevantes del candidato o vacante
- Debe mostrar el match percentage de forma clara en la interfaz

**Tareas Técnicas:**
- Refactorizar función `calcular_match_total` en servicio
- Crear servicio `service_match.py` con funciones especializadas
- Implementar cache para cálculos costosos
- Crear señales (signals) para recalcular match automáticamente
- Actualizar views para mostrar match actualizado

---

## 9. CONSULTA DE LISTADO DE CANDIDATOS POR CALIFICACIÓN DE MATCH

### Historia de Usuario 9.1: Listar Candidatos Ordenados por Match
**Como** reclutador  
**Quiero** ver un listado de candidatos ordenados por su porcentaje de match  
**Para** priorizar la revisión de los candidatos más compatibles con la vacante

**Criterios de Aceptación:**
- Debe mostrar listado de candidatos con su porcentaje de match destacado
- Debe permitir ordenar por match (ascendente/descendente)
- Debe mostrar indicador visual del match (barra de progreso, colores)
- Debe permitir filtrar por rango de match (ej: solo > 70%)
- Debe mostrar desglose del match por criterio al hacer hover o click
- Debe permitir exportar el listado con información de match

**Tareas Técnicas:**
- Crear view `listar_candidatos_por_match`
- Implementar ordenamiento por campo calculado (match percentage)
- Crear componente de visualización de match (barra, colores)
- Implementar filtros de rango
- Crear modal o tooltip para mostrar desglose del match

---

### Historia de Usuario 9.2: Vista Comparativa de Candidatos por Match
**Como** reclutador  
**Quiero** comparar candidatos lado a lado según su match  
**Para** tomar decisiones más informadas sobre qué candidatos priorizar

**Criterios de Aceptación:**
- Debe permitir seleccionar múltiples candidatos para comparar
- Debe mostrar tabla comparativa con: match total, match por criterio, información clave
- Debe resaltar diferencias y similitudes entre candidatos
- Debe permitir exportar la comparación
- Debe mostrar gráfico comparativo de match por criterio

**Tareas Técnicas:**
- Crear view `comparar_candidatos_match`
- Implementar selección múltiple de candidatos
- Crear componente de tabla comparativa
- Integrar gráficos comparativos
- Implementar funcionalidad de exportación

---

## 10. AGREGAR FILTROS POR BÚSQUEDA

### Historia de Usuario 10.1: Sistema de Filtros Avanzados
**Como** reclutador  
**Quiero** poder filtrar candidatos y vacantes con múltiples criterios  
**Para** encontrar rápidamente la información que necesito

**Criterios de Aceptación:**
- Debe permitir filtrar candidatos por: nombre, email, habilidades, experiencia, educación, match, estado
- Debe permitir filtrar vacantes por: título, cliente, estado, fecha, reclutador asignado
- Los filtros deben poder combinarse (AND lógico)
- Debe guardar filtros frecuentes como favoritos
- Debe permitir limpiar todos los filtros con un botón
- Los filtros deben persistir en la URL para poder compartir

**Tareas Técnicas:**
- Implementar Django Filter para modelos relevantes
- Crear formularios de filtros con widgets apropiados
- Implementar persistencia de filtros en sesión o URL
- Crear componentes reutilizables de filtros
- Implementar búsqueda full-text si es necesario

**NOTA:** Se debe preguntar al usuario qué campos específicos quieren poder filtrar

---

### Historia de Usuario 10.2: Búsqueda Global
**Como** reclutador  
**Quiero** tener una búsqueda global que me permita encontrar cualquier información rápidamente  
**Para** ahorrar tiempo navegando entre secciones

**Criterios de Aceptación:**
- Debe tener un campo de búsqueda global en el header/navbar
- Debe buscar en: candidatos, vacantes, clientes, entrevistas
- Debe mostrar resultados agrupados por tipo
- Debe mostrar sugerencias mientras se escribe (autocomplete)
- Debe resaltar los términos buscados en los resultados
- Debe permitir acceso rápido al resultado con un click

**Tareas Técnicas:**
- Crear view de búsqueda global
- Implementar búsqueda en múltiples modelos
- Integrar autocomplete (Select2, Algolia, o similar)
- Crear template de resultados de búsqueda
- Optimizar consultas de búsqueda con índices

---

## 11. GENERAR NAVEGACIÓN ENTRE CANDIDATOS

### Historia de Usuario 11.1: Navegación Secuencial entre Candidatos
**Como** reclutador  
**Quiero** poder navegar entre candidatos de forma secuencial (anterior/siguiente)  
**Para** revisar múltiples candidatos de manera eficiente sin volver al listado

**Criterios de Aceptación:**
- En la vista de detalle de candidato debe haber botones "Anterior" y "Siguiente"
- La navegación debe respetar el orden y filtros del listado desde donde se accedió
- Debe mostrar indicador de posición (ej: "Candidato 3 de 15")
- Debe deshabilitar botones cuando se está en el primero o último
- Debe mantener el contexto (vacante, filtros aplicados)
- Debe permitir navegación con teclado (flechas izquierda/derecha)

**Tareas Técnicas:**
- Crear función para obtener candidato anterior/siguiente según contexto
- Agregar botones de navegación en template de detalle
- Implementar navegación por teclado con JavaScript
- Guardar contexto de navegación en sesión o URL
- Crear indicador de posición

---

### Historia de Usuario 11.2: Navegación Rápida con Lista Desplegable
**Como** reclutador  
**Quiero** poder saltar directamente a un candidato específico desde una lista  
**Para** acceder rápidamente a cualquier candidato sin navegar secuencialmente

**Criterios de Aceptación:**
- Debe tener un dropdown o selector que muestre lista de candidatos
- La lista debe mostrar nombre y match percentage
- Debe permitir buscar dentro de la lista
- Debe mantener el orden del listado original
- Debe actualizarse según los filtros aplicados

**Tareas Técnicas:**
- Crear componente de selector de candidatos
- Implementar búsqueda dentro del selector
- Integrar con sistema de navegación secuencial
- Crear endpoint AJAX para obtener lista de candidatos filtrados

---

## 12. ENVÍO AL WHATSAPP DESDE PC

### Historia de Usuario 12.1: Integración con WhatsApp Web
**Como** reclutador  
**Quiero** poder enviar mensajes a candidatos desde WhatsApp Web abierto en mi PC  
**Para** comunicarme rápidamente con los candidatos sin usar mi teléfono

**Criterios de Aceptación:**
- Debe haber un botón "Enviar WhatsApp" en el detalle del candidato
- Al hacer click, debe abrir WhatsApp Web con el número del candidato pre-cargado
- Debe usar el formato de URL de WhatsApp: `https://wa.me/[número]?text=[mensaje]`
- El mensaje debe tener un template predefinido pero editable
- Debe validar que el candidato tenga número de teléfono
- Debe funcionar solo si WhatsApp Web está abierto en el navegador

**Tareas Técnicas:**
- Crear función para generar URL de WhatsApp con template de mensaje
- Agregar botón en template de detalle de candidato
- Implementar validación de número de teléfono
- Crear templates de mensajes configurables
- Documentar limitaciones (requiere WhatsApp Web abierto)

**NOTA:** Esta funcionalidad tiene limitaciones técnicas ya que requiere que WhatsApp Web esté abierto. Se debe informar al usuario sobre esto.

---

### Historia de Usuario 12.2: Historial de Comunicaciones por WhatsApp
**Como** reclutador  
**Quiero** registrar cuando he enviado mensajes por WhatsApp a un candidato  
**Para** llevar un registro de las comunicaciones realizadas

**Criterios de Aceptación:**
- Debe permitir registrar manualmente que se envió un mensaje por WhatsApp
- Debe guardar: fecha, hora, tipo de mensaje, notas
- Debe mostrar historial de comunicaciones en el detalle del candidato
- Debe permitir agregar notas sobre la conversación
- Debe mostrar indicador visual de última comunicación

**Tareas Técnicas:**
- Crear modelo `RecComunicacionWhatsApp` con relación a candidato
- Crear formulario para registrar comunicación
- Crear vista para listar historial de comunicaciones
- Agregar sección de comunicaciones en detalle de candidato

---

## 13. AJUSTAR LISTADO DE ENTREVISTAS Y GENERACIÓN MASIVA

### Historia de Usuario 13.1: Listado Mejorado de Entrevistas
**Como** reclutador  
**Quiero** ver un listado mejorado de todas mis entrevistas  
**Para** gestionar mejor mi agenda y seguimiento de entrevistas

**Criterios de Aceptación:**
- Debe mostrar: candidato, vacante, fecha, hora, tipo, estado, match
- Debe permitir filtrar por: fecha, estado, tipo, vacante, candidato
- Debe permitir ordenar por fecha, candidato, estado
- Debe mostrar indicadores visuales de estado (colores, badges)
- Debe destacar entrevistas próximas (hoy, mañana)
- Debe permitir acciones rápidas: ver detalle, cancelar, reprogramar

**Tareas Técnicas:**
- Mejorar view `listar_entrevistas` existente
- Agregar filtros con Django Filter
- Mejorar template con mejor diseño y UX
- Implementar indicadores de urgencia
- Agregar acciones rápidas

---

### Historia de Usuario 13.2: Generación Masiva de Entrevistas
**Como** reclutador  
**Quiero** poder crear múltiples entrevistas a la vez  
**Para** ahorrar tiempo al programar entrevistas para varios candidatos

**Criterios de Aceptación:**
- Debe permitir seleccionar múltiples candidatos de una lista
- Debe permitir definir fecha, hora y tipo de entrevista para todos
- Debe permitir personalizar fecha/hora individual si es necesario
- Debe validar que no haya conflictos de horario
- Debe enviar correos de notificación a todos los candidatos seleccionados
- Debe mostrar resumen antes de confirmar la creación
- Debe permitir cancelar la operación masiva

**Tareas Técnicas:**
- Crear view `crear_entrevistas_masivas`
- Crear formulario con selección múltiple de candidatos
- Implementar validación de conflictos de horario
- Integrar envío masivo de correos
- Crear template con wizard/pasos
- Implementar transacciones para rollback en caso de error

---

### Historia de Usuario 13.3: Envío Masivo de Correos para Entrevistas
**Como** reclutador  
**Quiero** que el sistema envíe automáticamente correos a los candidatos cuando se crean entrevistas  
**Para** notificarles oportunamente sobre su entrevista programada

**Criterios de Aceptación:**
- Debe enviar correo automáticamente al crear una entrevista
- El correo debe incluir: fecha, hora, tipo, lugar/enlace, información de contacto
- Debe usar templates de correo personalizables
- Debe permitir envío masivo sin duplicar correos
- Debe registrar en el sistema que se envió el correo
- Debe permitir reenviar correo manualmente si es necesario

**Tareas Técnicas:**
- Crear templates de correo para entrevistas
- Implementar señal (signal) para envío automático al crear entrevista
- Crear función de envío masivo de correos
- Integrar con sistema de correo existente (Django Email)
- Crear modelo o campo para registrar envío de correos
- Implementar cola de tareas (Celery) si el volumen es alto

---

## 14. CREAR FORMULARIO DE ENTREVISTA CON ETAPAS

### Historia de Usuario 14.1: Formulario de Entrevista con 5 Etapas Obligatorias
**Como** reclutador  
**Quiero** completar un formulario estructurado durante o después de la entrevista  
**Para** evaluar al candidato de manera sistemática y objetiva

**Criterios de Aceptación:**
- El formulario debe tener 5 secciones correspondientes a las etapas:
  1. IDENTIDAD MÁS ALLÁ DEL CV (obligatorio) - Calificable de 1 a 10
  2. ANÁLISIS CORPORAL – Lenguaje no verbal (obligatorio)
  3. PROPÓSITO Y CRECIMIENTO PERSONAL (obligatorio)
  4. ANÁLISIS 360° DE ENCAJE PERSONAL Y PROFESIONAL (obligatorio) - Calificación escala 1 a 10
  5. ÍNDICE DE CONFIABILIDAD Y RIESGO - Calificación escala 1 a 10
- Cada etapa debe tener campos de texto para observaciones
- Las etapas con calificación deben tener slider o input numérico de 1 a 10
- Debe validar que todas las etapas obligatorias estén completas antes de guardar
- Debe permitir guardar como borrador y completar después
- Debe calcular un promedio de las calificaciones

**Tareas Técnicas:**
- Crear modelo `RecEvaluacionEntrevista` con campos para cada etapa
- Crear formulario `EvaluacionEntrevistaForm` con validaciones
- Crear view para mostrar y procesar formulario
- Crear template con diseño tipo wizard (pasos)
- Implementar validación de campos obligatorios
- Calcular y guardar promedio de calificaciones

---

### Historia de Usuario 14.2: Guardado Progresivo del Formulario
**Como** reclutador  
**Quiero** poder guardar el formulario de entrevista de forma progresiva  
**Para** no perder información si necesito pausar la evaluación

**Criterios de Aceptación:**
- Debe permitir guardar cada etapa individualmente
- Debe mostrar indicador de progreso (cuántas etapas completadas)
- Debe marcar visualmente las etapas completadas
- Debe permitir navegar entre etapas sin perder datos
- Debe validar solo al intentar finalizar la evaluación completa
- Debe mostrar resumen antes de finalizar

**Tareas Técnicas:**
- Implementar guardado AJAX por etapa
- Crear indicador de progreso visual
- Implementar navegación entre etapas con guardado automático
- Crear validación final antes de marcar como completa
- Crear vista de resumen antes de finalizar

---

## 15. AJUSTAR INFORME FINAL CON CALIFICACIONES EN LA ENTREVISTA

### Historia de Usuario 15.1: Generar Informe Final de Entrevista
**Como** reclutador  
**Quiero** generar un informe final que incluya todas las calificaciones de la entrevista  
**Para** tener un documento completo de la evaluación del candidato

**Criterios de Aceptación:**
- El informe debe incluir: información del candidato, información de la vacante, calificaciones por etapa, promedio general, observaciones, recomendación
- Debe mostrar las 5 etapas con sus calificaciones y observaciones
- Debe incluir gráficos visuales de las calificaciones (barras, radar)
- Debe permitir exportar a PDF
- Debe permitir imprimir el informe
- Debe tener un diseño profesional y legible

**Tareas Técnicas:**
- Crear view `generar_informe_entrevista`
- Crear template de informe con diseño profesional
- Integrar librería de generación de PDF (WeasyPrint, ReportLab)
- Crear gráficos de calificaciones
- Implementar funcionalidad de impresión
- Agregar opción de personalizar template del informe

---

### Historia de Usuario 15.2: Vista de Resumen de Evaluación
**Como** reclutador  
**Quiero** ver un resumen visual de la evaluación del candidato  
**Para** tener una visión rápida de los resultados antes de generar el informe completo

**Criterios de Aceptación:**
- Debe mostrar calificaciones por etapa en formato de tarjetas o gráficos
- Debe mostrar promedio general destacado
- Debe mostrar recomendación (Apto/No Apto) basada en umbrales
- Debe permitir acceder al detalle de cada etapa
- Debe mostrar fecha de evaluación y reclutador que la realizó
- Debe tener diseño visual atractivo y fácil de entender

**Tareas Técnicas:**
- Crear view `resumen_evaluacion_entrevista`
- Crear componentes visuales para calificaciones
- Implementar lógica de recomendación basada en umbrales
- Crear gráfico tipo radar o barras para visualización
- Integrar con vista de detalle de entrevista

---

## 16. AJUSTE DATA DE ESTILO DE TRABAJO DOMINANTE

### Historia de Usuario 16.1: Gestionar Opciones de Estilo de Trabajo Dominante
**Como** administrador del sistema  
**Quiero** poder gestionar las opciones disponibles para "Estilo de Trabajo Dominante"  
**Para** que los usuarios puedan seleccionar la opción que mejor describe su entorno laboral

**Criterios de Aceptación:**
- Debe existir un modelo o catálogo para estilos de trabajo dominante
- Debe permitir CRUD completo (crear, leer, actualizar, eliminar) desde admin
- Las opciones deben estar disponibles en formularios de vacante y candidato
- Debe validar que se seleccione una opción cuando es obligatorio
- Debe permitir agregar descripciones o ejemplos para cada opción
- Debe estar relacionado con el cálculo del match (fit cultural)

**Tareas Técnicas:**
- Crear o ajustar modelo `CatEstiloTrabajo` en `applications/common/models.py`
- Registrar en admin de Django
- Actualizar formularios de vacante y candidato para usar el catálogo
- Actualizar lógica de match para considerar estilo de trabajo
- Crear migración si es necesario

---

### Historia de Usuario 16.2: Visualización de Estilo de Trabajo en Match
**Como** reclutador  
**Quiero** ver cómo el estilo de trabajo del candidato se compara con el requerido por la vacante  
**Para** evaluar el fit cultural en este aspecto

**Criterios de Aceptación:**
- En la vista de match debe mostrarse comparación de estilo de trabajo
- Debe indicar si hay coincidencia o no
- Debe mostrar el estilo del candidato y el requerido por la vacante
- Debe incluirse en el cálculo del match si aplica
- Debe aparecer en el informe final de match

**Tareas Técnicas:**
- Actualizar función de cálculo de match para incluir estilo de trabajo
- Agregar sección en vista de match
- Actualizar template de informe de match
- Documentar cómo se calcula la coincidencia

---

## 17. AJUSTE DATA DE RITMO DE TRABAJO

### Historia de Usuario 17.1: Gestionar Opciones de Ritmo de Trabajo
**Como** administrador del sistema  
**Quiero** poder gestionar las opciones disponibles para "Ritmo de Trabajo"  
**Para** que los usuarios puedan describir el ritmo laboral de su entorno

**Criterios de Aceptación:**
- Debe existir un modelo o catálogo para ritmo de trabajo
- Debe permitir CRUD completo desde admin
- Las opciones deben estar disponibles en formularios de vacante y candidato
- Debe validar selección cuando es obligatorio
- Debe permitir agregar descripciones para cada opción
- Debe estar relacionado con el cálculo del match

**Tareas Técnicas:**
- Crear o ajustar modelo `CatRitmoTrabajo` en `applications/common/models.py`
- Registrar en admin
- Actualizar formularios relevantes
- Actualizar lógica de match
- Crear migración si es necesario

---

### Historia de Usuario 17.2: Visualización de Ritmo de Trabajo en Match
**Como** reclutador  
**Quiero** ver la comparación del ritmo de trabajo entre candidato y vacante  
**Para** evaluar si el candidato se adaptará al ritmo requerido

**Criterios de Aceptación:**
- Debe mostrarse en la vista de match
- Debe indicar coincidencia o diferencia
- Debe incluirse en cálculo de match si aplica
- Debe aparecer en informe final

**Tareas Técnicas:**
- Actualizar cálculo de match
- Agregar sección en vista de match
- Actualizar template de informe

---

## 18. AJUSTE DATA DE TIPO DE LIDERAZGO

### Historia de Usuario 18.1: Gestionar Opciones de Tipo de Liderazgo
**Como** administrador del sistema  
**Quiero** poder gestionar las opciones disponibles para "Tipo de Liderazgo"  
**Para** que los usuarios puedan describir el estilo de liderazgo de su organización

**Criterios de Aceptación:**
- Debe existir un modelo o catálogo para tipo de liderazgo
- Debe permitir CRUD completo desde admin
- Las opciones deben estar disponibles en formularios de vacante y candidato
- Debe validar selección cuando es obligatorio
- Debe permitir agregar descripciones
- Debe estar relacionado con el cálculo del match

**Tareas Técnicas:**
- Crear o ajustar modelo `CatTipoLiderazgo` en `applications/common/models.py`
- Registrar en admin
- Actualizar formularios relevantes
- Actualizar lógica de match
- Crear migración si es necesario

---

### Historia de Usuario 18.2: Visualización de Tipo de Liderazgo en Match
**Como** reclutador  
**Quiero** ver la comparación del tipo de liderazgo entre candidato y vacante  
**Para** evaluar el encaje del candidato con el estilo de liderazgo de la organización

**Criterios de Aceptación:**
- Debe mostrarse en la vista de match
- Debe indicar coincidencia o diferencia
- Debe incluirse en cálculo de match si aplica
- Debe aparecer en informe final

**Tareas Técnicas:**
- Actualizar cálculo de match
- Agregar sección en vista de match
- Actualizar template de informe

---

## NOTAS ADICIONALES

### Preguntas Pendientes para el Usuario:

1. **Asignación de Vacantes (Actividad 4):** ¿Cómo será la asignación de vacantes a reclutadores?
   - ¿Manual por administrador?
   - ¿Automática por algoritmo (distribución equitativa, por especialización)?
   - ¿Por cliente o tipo de vacante?
   - ¿Un reclutador puede tener múltiples vacantes simultáneamente?

2. **Etapas de Reclutamiento (Actividad 7):** ¿Qué etapas específicas se manejan en el proceso?
   - ¿Las etapas son las definidas en `ESTADO_APLICACION_CHOICES_STATIC`?
   - ¿Se pueden personalizar las etapas por cliente o tipo de vacante?
   - ¿Hay etapas adicionales que no están en el sistema actual?

3. **Filtros de Búsqueda (Actividad 10):** ¿Qué campos específicos quieren poder filtrar?
   - ¿Solo campos básicos (nombre, email, estado)?
   - ¿También campos avanzados (habilidades, experiencia, educación, match)?
   - ¿Necesitan filtros combinados complejos?

### Consideraciones Técnicas:

- Todas las nuevas funcionalidades deben mantener compatibilidad con el sistema existente
- Se debe seguir el patrón de arquitectura actual (apps separadas, servicios, views)
- Se deben crear migraciones para todos los cambios de base de datos
- Se deben agregar tests unitarios para las nuevas funcionalidades críticas
- Se debe documentar las nuevas APIs y endpoints creados

### Priorización Sugerida:

**Fase 1 (Fundacional):**
- Actividades 1, 2, 3 (Base de datos, views, dashboard)

**Fase 2 (Gestión Básica):**
- Actividades 4, 5, 6 (Vacantes, detalle, historial)

**Fase 3 (Proceso de Reclutamiento):**
- Actividades 7, 8, 9 (Etapas, match, listados)

**Fase 4 (Optimización):**
- Actividades 10, 11, 12 (Filtros, navegación, WhatsApp)

**Fase 5 (Entrevistas):**
- Actividades 13, 14, 15 (Entrevistas, formulario, informe)

**Fase 6 (Ajustes Finales):**
- Actividades 16, 17, 18 (Ajustes de data)

---

**Documento generado el:** [Fecha]  
**Versión:** 1.0  
**Autor:** Sistema ATS

