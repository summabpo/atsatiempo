
from django.shortcuts import render, redirect # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore

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
    cliente_id = request.session.get('cliente_id')
    if cliente_id:
        # Mismo criterio que el listado cliente: vacante ligada por asignación (Cli064) al cliente asignado
        vacantes_activas_count = Cli052Vacante.objects.filter(
            asignacion_cliente_id_064__id_cliente_asignado=cliente_id,
            asignacion_cliente_id_064__tipo_asignacion="1",
            estado_id_001_id=1,
            estado_vacante__in=(1, 2),
        ).count()
    context = {
        'vacantes_activas_count': vacantes_activas_count,
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


