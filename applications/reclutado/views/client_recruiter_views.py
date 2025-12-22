from django.contrib.auth.views import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, Count, Q, Value, Case, When, CharField
from django.contrib import messages
from django.utils import timezone
from applications.common.models import Cat001Estado
from applications.usuarios.decorators  import validar_permisos
import json

#models
from applications.reclutado.models import Cli056AplicacionVacante
from applications.vacante.models import Cli052Vacante
from applications.candidato.models import Can101Candidato
from applications.services.service_vacanty import query_vacanty_all, get_vacanty_questions
from applications.services.service_interview import query_interview_all
from applications.services.service_recruited import query_recruited_vacancy_id
from applications.services.service_client import query_client_detail
from applications.services.service_candidate import buscar_candidato
from applications.services.choices import ESTADO_RECLUTADO_CHOICES_STATIC

#forms
from applications.reclutado.forms.FormRecruited import ActualizarEstadoReclutadoForm


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

@login_required
@validar_permisos('acceso_reclutador')
def detail_recruited(request, pk):
    # Obtener la aplicación de vacante
    asignacion_vacante = get_object_or_404(Cli056AplicacionVacante, id=pk)
    
    # Verificar que la vacante esté asignada al reclutador actual
    if asignacion_vacante.vacante_id_052.asignacion_reclutador != request.user:
        messages.error(request, 'No tiene permisos para acceder a este candidato.')
        return redirect('reclutados:vacantes_asignadas_reclutador')
    
    # Obtener información del candidato
    candidato = get_object_or_404(Can101Candidato, id=asignacion_vacante.candidato_101.id)
    info_detalle_candidato = buscar_candidato(candidato.id)
    
    # Obtener información de la vacante
    vacante = asignacion_vacante.vacante_id_052
    
    # Obtener el JSON match
    json_match_raw = asignacion_vacante.json_match
    if json_match_raw:
        try:
            if isinstance(json_match_raw, str):
                json_match = json.loads(json_match_raw)
            else:
                json_match = json_match_raw
        except (json.JSONDecodeError, TypeError):
            json_match = {}
    else:
        json_match = {}
    
    # Obtener historial de cambios de estado
    registro_reclutamiento = asignacion_vacante.registro_reclutamiento
    historial_estados = []
    if registro_reclutamiento:
        try:
            if isinstance(registro_reclutamiento, str):
                historial_estados = json.loads(registro_reclutamiento)
            else:
                historial_estados = registro_reclutamiento
            if not isinstance(historial_estados, list):
                historial_estados = []
        except (json.JSONDecodeError, TypeError):
            historial_estados = []
    
    # Inicializar formulario
    form = ActualizarEstadoReclutadoForm(estado_actual=asignacion_vacante.estado_reclutamiento)
    
    if request.method == 'POST':
        form = ActualizarEstadoReclutadoForm(request.POST, estado_actual=asignacion_vacante.estado_reclutamiento)
        if form.is_valid():
            nuevo_estado = int(form.cleaned_data['estado_reclutamiento'])
            comentario = form.cleaned_data['comentario']
            
            # Obtener nombres de estados
            estado_anterior_nombre = dict(ESTADO_RECLUTADO_CHOICES_STATIC).get(asignacion_vacante.estado_reclutamiento, 'Desconocido')
            estado_nuevo_nombre = dict(ESTADO_RECLUTADO_CHOICES_STATIC).get(nuevo_estado, 'Desconocido')
            
            # Crear el registro del cambio de estado según el formato especificado
            nuevo_registro = {
                "fecha_hora_actualizacion": timezone.now().isoformat(),
                "id_usuario_registro": request.user.id,
                "comentario": comentario,
                "estado_anterior": {
                    "codigo": asignacion_vacante.estado_reclutamiento,
                    "nombre": estado_anterior_nombre
                },
                "estado_nuevo": {
                    "codigo": nuevo_estado,
                    "nombre": estado_nuevo_nombre
                }
            }
            
            # Agregar el nuevo registro al historial
            historial_estados.append(nuevo_registro)
            
            # Actualizar el estado y el registro de reclutamiento
            asignacion_vacante.estado_reclutamiento = nuevo_estado
            asignacion_vacante.registro_reclutamiento = historial_estados
            asignacion_vacante.save()
            
            messages.success(request, f'Estado actualizado de "{estado_anterior_nombre}" a "{estado_nuevo_nombre}" exitosamente.')
            return redirect('reclutados:reclutados_detalle_reclutador', pk=pk)
        else:
            messages.error(request, 'Error al actualizar el estado. Verifique los datos.')
    
    context = {
        'candidato': candidato,
        'reclutado': asignacion_vacante,
        'vacante': vacante,
        'info_detalle_candidato': info_detalle_candidato,
        'json_match': json_match,
        'form': form,
        'historial_estados': historial_estados,
    }
    
    return render(request, 'admin/recruiter/client_recruiter/detail_recruited.html', context)
