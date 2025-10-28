from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, Count, Q, Value, Case, When, CharField
from applications.cliente.models import Cli051Cliente, Cli064AsignacionCliente


from applications.common.views.EnvioCorreo import enviar_correo
from applications.services.service_interview import query_interview_all
from applications.vacante.forms.EntrevistaForm import EntrevistaCrearForm, EntrevistaGestionForm
from applications.vacante.models import Cli052Vacante, Cli055ProfesionEstudio, Cli053SoftSkill, Cli054HardSkill, Cli052VacanteHardSkillsId054, Cli052VacanteSoftSkillsId053, Cli072FuncionesResponsabilidades, Cli073PerfilVacante, Cli068Cargo, Cli074AsignacionFunciones
from applications.reclutado.models import Cli056AplicacionVacante
from applications.entrevista.models import Cli057AsignacionEntrevista
from applications.usuarios.models import Permiso, UsuarioBase
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.candidato.models import Can101Candidato
from django.contrib import messages
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required
from applications.usuarios.decorators  import validar_permisos
from django.db.models.functions import Concat
from django.utils.timezone import now

#forms
from applications.vacante.forms.VacanteForms import VacancyFormAll

#query
from applications.services.service_vacanty import  query_vacanty_detail
from applications.services.service_recruited import query_recruited_vacancy_id
from components.RegistrarHistorialVacante import crear_historial_aplicacion


#detalle de la vacante
@login_required
@validar_permisos('acceso_admin', 'acceso_cliente', 'acceso_cliente_entrevistador', 'acceso_analista_seleccion')
def management_interview(request, pk):
    # Verificar si el cliente_id está en la sesión
    cliente_id = request.session.get('cliente_id')

    #obtener asignación de la entrevista
    asignacion_entrevista = get_object_or_404(Cli057AsignacionEntrevista, id=pk)
    

    # verificar información de asignación de la vacante
    asignacion_vacante = get_object_or_404(Cli056AplicacionVacante, id=asignacion_entrevista.asignacion_vacante.id)

    #obtener información del candidato
    info_candidato = get_object_or_404(Can101Candidato, id=asignacion_entrevista.asignacion_vacante.candidato_101.id)
    
    # Obtener información de la vacante
    vacante = query_vacanty_detail().get(id=asignacion_entrevista.asignacion_vacante.vacante_id_052.id)
    

    if request.method == 'POST': 
        form = EntrevistaGestionForm(request.POST)
        if form.is_valid():
            observacion = form.cleaned_data['observacion']
            estado_asignacion = int(form.cleaned_data['estado_asignacion'])

            estado_vacante = None
            observacion_historial = None

            #validación estados.
            if estado_asignacion == 2:
                estado_vacante = 3 # Pasa entrevista y queda en estado entrevista aprobada
                observacion_historial = 'Se aprueba el candidato, siguen en proceso.'
            if estado_asignacion == 3:
                estado_vacante = 12  # No Apto Entrevista No Aprobada
                observacion_historial = 'Candidato No Apto en Entrevista'
                #crea el historial y actualiza el estado de la aplicacion de la vacante
                crear_historial_aplicacion(asignacion_vacante, 4, request.session.get('_auth_user_id'), 'No aprobo la entrevista el candidato')
            if estado_asignacion == 4:
                estado_vacante = 8 # Se cambia estado de la vacante a seleccionado
                observacion_historial = 'Se selecciona candidato.'
            if estado_asignacion == 5:
                estado_vacante = 10 # Se cambia estado de la vacante a cancelado
                observacion_historial = 'Se cancela la postulación del candidato.'

            #crea el historial y actualiza el estado de la aplicacion de la vacante
            crear_historial_aplicacion(asignacion_vacante, estado_vacante, request.session.get('_auth_user_id'), observacion_historial)

            #actualizacion de gestión de entrevista
            asignacion_entrevista.observacion = observacion
            asignacion_entrevista.estado_asignacion = estado_asignacion
            asignacion_entrevista.fecha_gestion = now()
            asignacion_entrevista.save()

            messages.success(request, 'Se ha actualizado la entrevista.')

            return redirect('reclutados:reclutados_detalle_cliente', pk=asignacion_vacante.id)
        else:
            messages.error(request, form.errors)
    else:
        # Formulario Entrevista
        form = EntrevistaGestionForm()
        entrevista = get_object_or_404(Cli057AsignacionEntrevista, pk=pk)

    context ={
        'vacante': vacante,
        'candidato': info_candidato,
        'reclutado': asignacion_vacante,
        'form': form,
    }

    return render(request, 'admin/interview/client_user/interview_management.html', context)

#listado entrevistas por vacante
@login_required
@validar_permisos('acceso_cliente')
def interview_list(request):
    # Verificar si el cliente_id está en la sesión
    cliente_id = request.session.get('cliente_id')

    # Obtener información de las entrevistas por vacante
    entrevistas = query_interview_all()
    entrevistas = entrevistas.filter(asignacion_vacante__vacante_id_052__asignacion_cliente_id_064__id_cliente_asignado=cliente_id)

    context = {
        'entrevistas': entrevistas,
    }

    return render(request, 'admin/interview/client_user/interview_list.html', context)