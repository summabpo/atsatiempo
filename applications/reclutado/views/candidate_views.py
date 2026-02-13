from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, Count, Q, Value, Case, When, CharField
from applications.common.models import Cat001Estado
from applications.common.views.EnvioCorreo import enviar_correo
from applications.entrevista.forms.PreguntasReclutamientoForm import PreguntasReclutamiento
from applications.reclutado.models import Cli056AplicacionVacante, Cli063AplicacionVacanteHistorial
from applications.candidato.models import Can101Candidato
from applications.services.service_vacanty import query_vacanty_with_skills_and_details
from applications.vacante.models import Cli052Vacante
from components.RegistrarHistorialVacante import crear_historial_aplicacion
from django.contrib import messages
from applications.vacante.views.common_view import get_match, get_match_initial
from applications.usuarios.models import UsuarioBase

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
    form = PreguntasReclutamiento(vacante_id=pk)

    if request.method == 'POST':
        form = PreguntasReclutamiento(pk, request.POST)        
        if form.is_valid():
            print(form.cleaned_data)

            # Obtener la instancia del usuario reclutador si existe
            usuario_reclutador_id = request.session.get('_auth_user_id')
            usuario_reclutador = None
            if usuario_reclutador_id:
                try:
                    usuario_reclutador = UsuarioBase.objects.get(id=usuario_reclutador_id)
                except UsuarioBase.DoesNotExist:
                    usuario_reclutador = None
            
            asignacion_vacante = Cli056AplicacionVacante.objects.create(
                candidato_101_id=candidate_id,
                vacante_id_052_id=pk,
                estado_aplicacion=1,
                preguntas_reclutamiento=form.cleaned_data,
                estado= get_object_or_404(Cat001Estado, pk=1),  # Estado activo por defecto
                usuario_reclutador=usuario_reclutador
            )
            
            match_candidato_vacante = get_match(candidato.id, pk)
            match_inicial = get_match_initial(candidato.id, pk)
            
            # Convertir a formato JSON (diccionario Python) para guardar en JSONField
            import json
            try:
                # Si get_match retorna un string JSON, parsearlo a diccionario
                if isinstance(match_candidato_vacante, str):
                    match_candidato_vacante = json.loads(match_candidato_vacante)
            except (json.JSONDecodeError, TypeError):
                # Si ya es un diccionario o hay error, usar tal cual
                pass
            
            try:
                # Si get_match_initial retorna un string JSON, parsearlo a diccionario
                if isinstance(match_inicial, str):
                    match_inicial = json.loads(match_inicial)
            except (json.JSONDecodeError, TypeError):
                # Si ya es un diccionario o hay error, usar tal cual
                pass

            asignacion_vacante.json_match = match_candidato_vacante
            asignacion_vacante.json_match_inicial = match_inicial

            asignacion_vacante.save()

            #funcion para crear registro en el historial y actualizar estado de la aplicacion de la vcatente
            crear_historial_aplicacion(asignacion_vacante, 1, request.session.get('_auth_user_id'), 'Aplicación a Vacante por el candidato')

            messages.success(request, 'Aplicación a la vacante realizada con éxito.')
            return redirect('reclutados:reclutados_confirmar_aplicar_candidato', pk=pk)
        else:
            messages.error(request, 'Por favor, complete todos los campos requeridos.')
    else:
        form = PreguntasReclutamiento(vacante_id=pk)

    centinel_vacante = False

    # Verificar si el candidato ya ha aplicado a la vacante
    if Cli056AplicacionVacante.objects.filter(vacante_id_052=vacante, candidato_101=candidato).exists():
        # Si ya ha aplicado, redirigir a la página de detalle de la vacante
        centinel_vacante = True
        # return redirect('reclutados_detalle_cliente', pk=pk)

    # Verificar si el usuario es de tipo candidato
    tipo_usuario = request.session.get('tipo_usuario', '')
    grupo_id = request.session.get('grupo_id', None)
    is_candidato = (tipo_usuario == 'Candidato' or grupo_id == 2)
    
    context = {
        'vacante': vacante,
        'candidato': candidato,
        'centinel_vacante': centinel_vacante,
        'form': form,
        'is_candidato': is_candidato
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
        estado_aplicacion=1,
        estado= get_object_or_404(Cat001Estado, pk=1)  # Estado activo por defecto
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



def test_match(request, pk):    

    aplicacion_vacante = get_object_or_404(Cli056AplicacionVacante, pk=pk)
    
    candidato = aplicacion_vacante.candidato_101
    vacante = aplicacion_vacante.vacante_id_052

    json_match_inicial = get_match_initial(candidato.id, vacante.id)

    context = {
        'json_match_inicial': json_match_inicial,
    }

    return render(request, 'admin/test_dev/test_match_initial.html', context)

