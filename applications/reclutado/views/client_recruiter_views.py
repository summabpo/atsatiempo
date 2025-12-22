from django.contrib.auth.views import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, Count, Q, Value, Case, When, CharField
from applications.common.models import Cat001Estado
from applications.usuarios.decorators  import validar_permisos

#models
from applications.reclutado.models import Cli056AplicacionVacante
from applications.vacante.models import Cli052Vacante
from applications.services.service_vacanty import query_vacanty_all, get_vacanty_questions
from applications.services.service_interview import query_interview_all
from applications.services.service_recruited import query_recruited_vacancy_id
from applications.services.service_client import query_client_detail


@login_required
@validar_permisos('acceso_reclutador')
def vacancies_assigned_recruiter(request):

    # Consultar vacantes asignadas al reclutador con estadísticas
    vacantes = query_vacanty_all()
    vacantes = vacantes.filter(
        asignacion_reclutador=request.user,
        estado_id_001=1
    ).annotate(
        # Contar personal reclutado (estado_reclutamiento en 2 o 3: Seleccionado o Finalizalista)
        reclutados_recibido=Count(
            'aplicaciones',
            filter=Q(aplicaciones__estado_reclutamiento=1)
        ),
        reclutados_seleccionado=Count(
            'aplicaciones',
            filter=Q(aplicaciones__estado_reclutamiento=2)
        ),
        reclutados_finalizalista=Count(
            'aplicaciones',
            filter=Q(aplicaciones__estado_reclutamiento=3)
        ),
        reclutados_descartado=Count(
            'aplicaciones',
            filter=Q(aplicaciones__estado_reclutamiento=4)
        ),
        # Personal reclutado: suma de seleccionados y finalistas
        personal_reclutado=Count(
            'aplicaciones',
            filter=Q(aplicaciones__estado_reclutamiento__in=[2, 3])
        )
    )

    context = {
        'vacantes': vacantes,
    }

    return render(request, 'admin/recruiter/client_recruiter/vacancies_assigned_recruiter.html', context)


@login_required
@validar_permisos('acceso_reclutador')
def vacancies_assigned_recruiter_detail(request, pk, vacante_id):
    # Verificar que la vacante esté asignada al reclutador actual
    vacante = get_object_or_404(
        Cli052Vacante.objects.prefetch_related('habilidades'),
        id=vacante_id,
        asignacion_reclutador=request.user,
        estado_id_001=1
    )
    
    # Obtener el cliente asignado
    cliente_id = None
    if vacante.asignacion_cliente_id_064 and vacante.asignacion_cliente_id_064.id_cliente_asignado:
        cliente_id = vacante.asignacion_cliente_id_064.id_cliente_asignado.id
        data = query_client_detail(cliente_id)
    else:
        data = None
    
    # Obtener información de las entrevistas por vacante
    entrevistas = query_interview_all()
    entrevistas = entrevistas.filter(asignacion_vacante__vacante_id_052=vacante.id)
    
    # Obtener preguntas de la vacante
    preguntas = get_vacanty_questions(vacante.id)
    
    # Obtener los reclutados asociados a la vacante
    reclutados = query_recruited_vacancy_id(vacante.id)
    
    # Agrupar reclutados por estado de reclutamiento
    reclutados_recibido = [r for r in reclutados if r.estado_reclutamiento == 1]
    reclutados_seleccionado = [r for r in reclutados if r.estado_reclutamiento == 2]
    reclutados_finalizalista = [r for r in reclutados if r.estado_reclutamiento == 3]
    reclutados_descartado = [r for r in reclutados if r.estado_reclutamiento == 4]
    
    context = {
        'data': data,
        'vacante': vacante,
        'reclutados': reclutados,
        'reclutados_recibido': reclutados_recibido,
        'reclutados_seleccionado': reclutados_seleccionado,
        'reclutados_finalizalista': reclutados_finalizalista,
        'reclutados_descartado': reclutados_descartado,
        'entrevistas': entrevistas,
        'preguntas': preguntas,
    }
    
    return render(request, 'admin/recruiter/client_recruiter/vacancies_assigned_recruiter_detail.html', context)