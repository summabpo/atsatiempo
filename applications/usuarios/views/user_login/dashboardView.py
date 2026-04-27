
from django.shortcuts import render, redirect # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from django.db.models import Q
from django.utils import timezone

from ...decorators  import validar_permisos
from applications.usuarios.views.commons.dashboard_panels import (
    get_panel_metricas_superiores,
    get_panel_candidatos_por_dia,
    get_panel_candidatos_por_mes,
    get_panel_ciudad_residencia,
    get_panel_tipo_estudio,
    get_panel_profesion_estudio,
    get_panel_metricas_analista_interno,
    get_panel_metricas_reclutador,
)

# consultas
from applications.services.service_candidate import personal_information_calculation
from applications.services.service_vacanty import query_vacanty_with_skills_and_details
from applications.vacante.models import Cli052Vacante
from applications.reclutado.models import Cli056AplicacionVacante
from django.utils.formats import date_format
from django.db.models import Exists, OuterRef

#pantalla inicio
@login_required
@validar_permisos('acceso_candidato')
def dashboard_candidato(request):
    """ Vista que carga la página de inicio y muestra variables de sesión """
    
    # Obtener todas las variables de sesión
    session_variables = dict(request.session)
    candidato_id = request.session.get('candidato_id')
    data = personal_information_calculation(candidato_id)
    vacantes_disponibles = query_vacanty_with_skills_and_details().filter(estado_id_001=1)
    
    vacantes_disponibles = vacantes_disponibles.exclude(
        aplicaciones__candidato_101_id=candidato_id
    )
    
    # Obtener datos detallados para mostrar en el dashboard
    from applications.candidato.models import Can101Candidato, Can102Experiencia, Can103Educacion, Can101CandidatoSkill
    candidato_obj = Can101Candidato.objects.get(id=candidato_id)
    educaciones = Can103Educacion.objects.filter(candidato_id_101=candidato_obj).order_by('-fecha_inicial')[:3]
    experiencias = Can102Experiencia.objects.filter(candidato_id_101=candidato_obj).order_by('-fecha_inicial')[:3]
    habilidades = Can101CandidatoSkill.objects.filter(candidato_id_101=candidato_obj).select_related('skill_id_104')[:6]

    # Nivel educativo más alto según tipo_estudio (mayor ID = mayor nivel)
    estudio_mas_alto = (
        Can103Educacion.objects
        .filter(candidato_id_101=candidato_obj, tipo_estudio__isnull=False)
        .exclude(tipo_estudio='')
        .order_by('-tipo_estudio')
        .first()
    )
    nivel_educativo_maximo = estudio_mas_alto.mostrar_tipo_estudio() if estudio_mas_alto else 'Sin estudios registrados'

    context = {
        'session_variables': session_variables,
        'data_candidate': data,
        'vacantes_disponibles': vacantes_disponibles,
        'candidato': candidato_obj,
        'educaciones': educaciones,
        'experiencias': experiencias,
        'habilidades': habilidades,
        'nivel_educativo_maximo': nivel_educativo_maximo,
    }
    
    return render(request, 'admin/dashboard/dashboard_candidate.html', context)


@login_required
@validar_permisos('acceso_cliente')
def dashboard_cliente(request):
    """ Vista que carga la página de inicio y muestra variables de sesión """
    vacantes_activas_count = 0
    vacantes_activas_mes_count = 0
    vacantes_finalizadas_count = 0
    vacantes_finalizadas_mes_count = 0
    vacantes_vencidas_count = 0
    vacantes_vencidas_mes_count = 0
    candidatos_entrevista_aprobada_sin_calificar_count = 0
    candidatos_feedback_mes_count = 0
    feedback_pendiente_ultimos = []
    feedback_pendiente_extra_count = 0
    vacantes_cancelables_count = 0
    vacantes_cancelables = []
    vacantes_cancelables_payload = []
    vacantes_talento_por_enviar_count = 0
    aplicaciones_validacion_confianza_count = 0
    aplicaciones_espera_respuesta_count = 0
    vacantes_talento_por_enviar_payload = []
    aplicaciones_validacion_confianza_payload = []
    aplicaciones_espera_respuesta_payload = []
    cliente_id = request.session.get('cliente_id')
    if cliente_id:
        # Criterio por asignación (Cli064):
        # - cliente asignado (tipo 1) y/o
        # - cliente maestro/headhunter (tipo 2)
        # Evita filtrar por tipo_asignacion para no perder visibilidad según rol/relación.
        base_vacantes = (
            Cli052Vacante.objects.filter(estado_id_001_id=1)
            .filter(
                Q(asignacion_cliente_id_064__id_cliente_asignado_id=cliente_id)
                | Q(asignacion_cliente_id_064__id_cliente_maestro_id=cliente_id)
            )
            .distinct()
        )

        # Activas: Activa (1) o En proceso (2)
        vacantes_activas_count = base_vacantes.filter(estado_vacante__in=(1, 2)).count()

        # Vacantes sin envío de candidatos al cliente:
        # no tienen aplicaciones en estados "enviados/gestionados por el cliente" (3..15).
        estados_enviados_cliente = (3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
        qs_talento_por_enviar = (
            base_vacantes.filter(estado_vacante__in=(1, 2))
            .annotate(
                tiene_candidatos_enviados=Exists(
                    Cli056AplicacionVacante.objects.filter(vacante_id_052_id=OuterRef("pk")).filter(
                        estado_aplicacion__in=estados_enviados_cliente
                    )
                )
            )
            .filter(tiene_candidatos_enviados=False)
        )
        vacantes_talento_por_enviar_count = qs_talento_por_enviar.count()
        vacantes_talento_por_enviar_payload = list(
            qs_talento_por_enviar.select_related("cargo").order_by("-id")[:200].values(
                "id",
                "titulo",
                "cargo__nombre_cargo",
                "numero_posiciones",
                "fecha_creacion",
            )
        )

        # Aplicaciones en estados solicitados
        qs_estado_5 = (
            Cli056AplicacionVacante.objects.filter(vacante_id_052__in=base_vacantes)
            .filter(estado_aplicacion=5)
            .select_related("candidato_101", "vacante_id_052__cargo")
            .order_by("-fecha_actualizacion")
        )
        aplicaciones_validacion_confianza_count = qs_estado_5.count()
        aplicaciones_validacion_confianza_payload = [
            {
                "aplicacion_id": a.id,
                "vacante_id": a.vacante_id_052_id,
                "cargo": (a.vacante_id_052.cargo.nombre_cargo if getattr(a.vacante_id_052, "cargo", None) else a.vacante_id_052.titulo),
                "candidato": getattr(a.candidato_101, "nombre_completo", None) or " ".join(
                    [p for p in [a.candidato_101.primer_nombre, a.candidato_101.segundo_nombre, a.candidato_101.primer_apellido, a.candidato_101.segundo_apellido] if p]
                ).strip(),
                "estado": "Acciones decisivas programadas",
            }
            for a in list(qs_estado_5[:300])
        ]

        qs_estado_13 = (
            Cli056AplicacionVacante.objects.filter(vacante_id_052__in=base_vacantes)
            .filter(estado_aplicacion=13)
            .select_related("candidato_101", "vacante_id_052__cargo")
            .order_by("-fecha_actualizacion")
        )
        aplicaciones_espera_respuesta_count = qs_estado_13.count()
        aplicaciones_espera_respuesta_payload = [
            {
                "aplicacion_id": a.id,
                "vacante_id": a.vacante_id_052_id,
                "cargo": (a.vacante_id_052.cargo.nombre_cargo if getattr(a.vacante_id_052, "cargo", None) else a.vacante_id_052.titulo),
                "candidato": getattr(a.candidato_101, "nombre_completo", None) or " ".join(
                    [p for p in [a.candidato_101.primer_nombre, a.candidato_101.segundo_nombre, a.candidato_101.primer_apellido, a.candidato_101.segundo_apellido] if p]
                ).strip(),
                "estado": "En espera por respuesta de contratación",
            }
            for a in list(qs_estado_13[:300])
        ]

        # Vacantes cancelables (Activa/En proceso) para el panel "Cancelar Vacantes"
        vacantes_cancelables = list(
            base_vacantes.filter(estado_vacante__in=(1, 2))
            .select_related("cargo", "usuario_asignado", "asignacion_reclutador")
            .order_by("-id")[:200]
        )
        vacantes_cancelables_count = len(vacantes_cancelables)

        def _nombre_usuario(u):
            if not u:
                return ""
            partes = [u.primer_nombre, u.segundo_nombre, u.primer_apellido, u.segundo_apellido]
            return " ".join([p for p in partes if p]).strip()

        vacantes_cancelables_payload = [
            {
                "id": v.id,
                "cargo": (v.cargo.nombre_cargo if getattr(v, "cargo", None) else ""),
                "fecha_inicio": date_format(timezone.localtime(v.fecha_creacion), "SHORT_DATETIME_FORMAT")
                if v.fecha_creacion
                else "",
                "analista_asignado": _nombre_usuario(getattr(v, "usuario_asignado", None)),
                "reclutador_asignado": _nombre_usuario(getattr(v, "asignacion_reclutador", None)),
            }
            for v in vacantes_cancelables
        ]

        # Finalizadas/cerradas: Finalizada (3)
        vacantes_finalizadas_count = base_vacantes.filter(estado_vacante=3).count()

        # Cerradas en el mes en curso (por fecha_cierre; rango [inicio_mes, siguiente_mes))
        ahora = timezone.now()
        inicio_mes = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if inicio_mes.month == 12:
            fin_mes_exclusivo = inicio_mes.replace(year=inicio_mes.year + 1, month=1, day=1)
        else:
            fin_mes_exclusivo = inicio_mes.replace(month=inicio_mes.month + 1, day=1)
        vacantes_finalizadas_mes_count = (
            base_vacantes.filter(estado_vacante=3)
            .filter(fecha_cierre__isnull=False)
            .filter(fecha_cierre__gte=inicio_mes, fecha_cierre__lt=fin_mes_exclusivo)
            .count()
        )

        # Activas/en proceso creadas en el mes en curso (fecha_cierre aún no aplica)
        vacantes_activas_mes_count = (
            base_vacantes.filter(estado_vacante__in=(1, 2))
            .filter(fecha_creacion__gte=inicio_mes, fecha_creacion__lt=fin_mes_exclusivo)
            .count()
        )

        # Vencidas: fecha_cierra_planteada ya pasó y la vacante sigue activa/en proceso
        vacantes_vencidas_count = (
            base_vacantes.filter(estado_vacante__in=(1, 2))
            .filter(fecha_cierra_planteada__isnull=False)
            .filter(fecha_cierra_planteada__lt=timezone.now())
            .count()
        )

        # Vencidas con fecha de cierre planteada en el mes en curso (y ya vencida)
        vacantes_vencidas_mes_count = (
            base_vacantes.filter(estado_vacante__in=(1, 2))
            .filter(fecha_cierra_planteada__isnull=False)
            .filter(fecha_cierra_planteada__lt=timezone.now())
            .filter(
                fecha_cierra_planteada__gte=inicio_mes,
                fecha_cierra_planteada__lt=fin_mes_exclusivo,
            )
            .count()
        )

        # Candidatos con entrevista aprobada (estado_aplicacion=3) aún sin calificación del cliente.
        # En este flujo la calificación del cliente ocurre después (p. ej. Seleccionado por Cliente / No Apto),
        # por eso se cuentan los que siguen en estado 3.
        candidatos_entrevista_aprobada_sin_calificar_count = (
            Cli056AplicacionVacante.objects.filter(vacante_id_052__in=base_vacantes)
            .filter(estado_aplicacion=3)
            .count()
        )

        # Misma lógica estado 3, aplicaciones registradas en el mes en curso (fecha_aplicacion)
        candidatos_feedback_mes_count = (
            Cli056AplicacionVacante.objects.filter(vacante_id_052__in=base_vacantes)
            .filter(estado_aplicacion=3)
            .filter(fecha_aplicacion__gte=inicio_mes, fecha_aplicacion__lt=fin_mes_exclusivo)
            .count()
        )

        qs_feedback_pendiente = (
            Cli056AplicacionVacante.objects.filter(vacante_id_052__in=base_vacantes)
            .filter(estado_aplicacion=3)
            .select_related("candidato_101")
            .order_by("-fecha_actualizacion")
        )
        feedback_pendiente_total = qs_feedback_pendiente.count()
        feedback_pendiente_ultimos = list(qs_feedback_pendiente[:4])
        feedback_pendiente_extra_count = max(0, feedback_pendiente_total - len(feedback_pendiente_ultimos))
    context = {
        'vacantes_activas_count': vacantes_activas_count,
        'vacantes_activas_mes_count': vacantes_activas_mes_count,
        'vacantes_finalizadas_count': vacantes_finalizadas_count,
        'vacantes_finalizadas_mes_count': vacantes_finalizadas_mes_count,
        'vacantes_vencidas_count': vacantes_vencidas_count,
        'vacantes_vencidas_mes_count': vacantes_vencidas_mes_count,
        'candidatos_entrevista_aprobada_sin_calificar_count': candidatos_entrevista_aprobada_sin_calificar_count,
        'candidatos_feedback_mes_count': candidatos_feedback_mes_count,
        'feedback_pendiente_ultimos': feedback_pendiente_ultimos,
        'feedback_pendiente_extra_count': feedback_pendiente_extra_count,
        'vacantes_cancelables_count': vacantes_cancelables_count,
        'vacantes_cancelables': vacantes_cancelables,
        'vacantes_cancelables_payload': vacantes_cancelables_payload,
        'vacantes_talento_por_enviar_count': vacantes_talento_por_enviar_count,
        'aplicaciones_validacion_confianza_count': aplicaciones_validacion_confianza_count,
        'aplicaciones_espera_respuesta_count': aplicaciones_espera_respuesta_count,
        'vacantes_talento_por_enviar_payload': vacantes_talento_por_enviar_payload,
        'aplicaciones_validacion_confianza_payload': aplicaciones_validacion_confianza_payload,
        'aplicaciones_espera_respuesta_payload': aplicaciones_espera_respuesta_payload,
    }
    return render(request, 'admin/dashboard/dashboard_client.html', context)


@login_required
@validar_permisos('acceso_admin')
def dashboard_administrador(request):
    """Dashboard administrador. Cada panel se genera desde views.commons.dashboard_panels."""
    context = {}
    context.update(get_panel_metricas_superiores())
    context.update(get_panel_candidatos_por_dia())
    context.update(get_panel_candidatos_por_mes())
    context.update(get_panel_ciudad_residencia())
    context.update(get_panel_tipo_estudio())
    context.update(get_panel_profesion_estudio())
    return render(request, 'admin/dashboard/dashboard_admin.html', context)



@login_required
@validar_permisos('acceso_analista_seleccion')
def dashboard_analista_internal(request):
    """Dashboard analista interno: solo métricas de vacantes asignadas (sin gráficos de candidatos)."""
    context = {}
    context.update(get_panel_metricas_analista_interno(request.user.id))
    return render(request, 'admin/dashboard/dashboard_analista_internal.html', context)


@login_required
@validar_permisos('acceso_reclutador')
def dashboard_reclutador(request):
    """Dashboard reclutador: vacantes asignadas y conteos por estado de reclutamiento y de aplicación."""
    context = {}
    context.update(get_panel_metricas_reclutador(request.user.id))
    return render(request, 'admin/dashboard/dashboard_reclutador.html', context)


