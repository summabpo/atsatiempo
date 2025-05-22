from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, Count, Q, Value, Case, When, CharField
from applications.common.views.EnvioCorreo import enviar_correo
from applications.reclutado.models import Cli056AplicacionVacante, Cli063AplicacionVacanteHistorial
from applications.candidato.models import Can101Candidato
from applications.services.service_vacanty import query_vacanty_with_skills_and_details
from applications.vacante.models import Cli052Vacante
from components.RegistrarHistorialVacante import crear_historial_aplicacion
from django.contrib import messages

def confirm_apply_vacancy_recruited(request, pk):
    """
    Función para aplicar a una vacante por parte de un candidato. 
    """
    candidate_id = request.session.get('candidato_id')
    if not candidate_id:
        return redirect('inicio')

    # Obtener la vacante y el candidato
    vacante = query_vacanty_with_skills_and_details().get(id=pk)
    candidato = get_object_or_404(Can101Candidato, pk=candidate_id)
    centinel_vacante = False

    # Verificar si el candidato ya ha aplicado a la vacante
    if Cli056AplicacionVacante.objects.filter(vacante_id_052=vacante, candidato_101=candidato).exists():
        # Si ya ha aplicado, redirigir a la página de detalle de la vacante
        centinel_vacante = True
        # return redirect('reclutados_detalle_cliente', pk=pk)

    context = {
        'vacante': vacante,
        'candidato': candidato,
        'centinel_vacante': centinel_vacante,
    }

    return render(request, 'admin/candidate/candidate_user/recluited_confirm.html', context)

def apply_vacancy_recruited_candidate(request, pk):
    candidate_id = request.session.get('candidato_id')
    if not candidate_id:
        return redirect('inicio')
    # Obtener la vacante y el candidato
    asignacion_vacante = Cli056AplicacionVacante.objects.create(
        candidato_101_id=candidate_id,
        vacante_id_052_id=pk,
        estado_aplicacion=1
    )

    #funcion para crear registro en el historial y actualizar estado de la aplicacion de la vcatente
    crear_historial_aplicacion(asignacion_vacante, 1, request.session.get('_auth_user_id'), 'Aplicación a Vacante por el candidato')
    
    # contexto_email_1 = {
    #     'entrevistador' : f'{usuario_asignado.primer_nombre} {usuario_asignado.segundo_nombre} {usuario_asignado.primer_apellido}',
    #     'nombre_candidato' : f'{info_candidato.primer_nombre} {info_candidato.segundo_nombre} {info_candidato.primer_apellido} {info_candidato.segundo_apellido}' ,
    #     'fecha_entrevista' : fecha_entrevista,
    #     'hora_entrevista' : hora_entrevista,
    #     'lugar_enlace' : lugar_enlace,
    #     'vacante' : vacante.titulo,
    #     'cliente' : cliente.razon_social,
    #     'url' : url_actual
    # }

    # lista_correos = [
    #     usuario_asignado.email,
    #     info_candidato.email
    # ]

    # Envio de correo
    # enviar_correo('asignacion_entrevista_entrevista', contexto_email_1, f'Asginación de Entrevista ID: {asignacion_entrevista.id}', lista_correos, correo_remitente=None)

    

    messages.success(request, 'Aplicación a la vacante realizada con éxito.')
    
    return redirect('reclutados:reclutados_confirmar_aplicar_candidato', pk=pk)
