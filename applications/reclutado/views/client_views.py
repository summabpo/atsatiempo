from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, Count, Q, Value, Case, When, CharField
from applications.cliente.models import Cli051Cliente, Cli064AsignacionCliente


from applications.common.views.EnvioCorreo import enviar_correo
from applications.reclutado.forms.FormRecruited import ReclutadoCrearForm
from applications.services.service_candidate import buscar_candidato
from applications.vacante.forms.EntrevistaForm import EntrevistaCrearForm
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

#forms
from applications.vacante.forms.VacanteForms import VacancyFormAll

#query
from applications.services.service_vacanty import  query_vacanty_detail
from applications.services.service_recruited import consultar_historial_aplicacion_vacante, query_recruited_vacancy_id
from components.RegistrarHistorialVacante import crear_historial_aplicacion

#detalle de la vacante
@login_required
@validar_permisos('acceso_admin', 'acceso_cliente')
def detail_vacancy_recruited(request, pk):
    form_errors = False
    # Verificar si el cliente_id está en la sesión
    cliente_id = request.session.get('cliente_id')
    
    # Obtener información de la vacante
    vacante = query_vacanty_detail().get(id=pk)

    # Obtener los reclutados asociados a la vacante
    reclutados = query_recruited_vacancy_id(vacante.id)

    # formulario para asignar candidato a la vacante

    form = ReclutadoCrearForm()
    if request.method == 'POST':
        form = ReclutadoCrearForm(request.POST)
        if form.is_valid():
            numero_documento = form.cleaned_data['numero_documento']
            primer_nombre = form.cleaned_data['primer_nombre']
            segundo_nombre = form.cleaned_data['segundo_nombre']
            primer_apellido = form.cleaned_data['primer_apellido']
            segundo_apellido = form.cleaned_data['segundo_apellido']
            telefono = form.cleaned_data['telefono']
            email = form.cleaned_data['email']

            #registro del candidato
            candidato, created = Can101Candidato.objects.get_or_create(
                numero_documento=numero_documento,
                defaults={
                    'primer_nombre': primer_nombre,
                    'segundo_nombre': segundo_nombre,
                    'primer_apellido': primer_apellido,
                    'segundo_apellido': segundo_apellido,
                    'telefono': telefono,
                    'email': email,
                    'estado_id_001': Cat001Estado.objects.get(id=1),  # Asumiendo que 1 es el estado por defecto
                }
            )

            if created:
                messages.success(request, 'Candidato creado exitosamente.')
            else:
                messages.info(request, 'Candidato ya existe. Se actualizarán los datos.')
                # Actualizar los datos del candidato si ya existe
                candidato.primer_nombre = primer_nombre
                candidato.segundo_nombre = segundo_nombre
                candidato.primer_apellido = primer_apellido
                candidato.segundo_apellido = segundo_apellido
                candidato.telefono = telefono
                candidato.email = email
                candidato.save()

            # Validar que el candidato no esté ya registrado en la vacante
            if Cli056AplicacionVacante.objects.filter(candidato_101=candidato, vacante_id_052=vacante).exists():
                messages.error(request, 'El candidato ya está registrado en esta vacante.')
                return redirect('reclutados:vacantes_reclutados_cliente', pk=pk)

            #registro de la aplicacion de la vacante
            aplicacion_vacante = Cli056AplicacionVacante.objects.create(
                vacante_id_052=vacante,
                candidato_101=candidato,
                estado=Cat001Estado.objects.get(id=1),  # Asumiendo que 1 es el estado por defecto
            )
            messages.success(request, 'Candidato asignado en la vacante exitosamente.')
            return redirect('reclutados:vacantes_reclutados_cliente', pk=pk)    
        else:
            form_errors = True
            messages.error(request, 'Error al crear el candidato. Verifique los datos.')

    else:
        form = ReclutadoCrearForm()

    context ={
        'vacante': vacante,
        'reclutados': reclutados,
        'form': form,
        'form_errors' : form_errors,
    }

    return render(request, 'admin/vacancy/client_user/vacancy_detail_recruited.html', context)

#detalle de la vacante
@login_required
@validar_permisos('acceso_admin', 'acceso_cliente')
def detail_recruited(request, pk):
    url_actual = f"{request.scheme}://{request.get_host()}"
    validar_registro = False
    usuario_id = request.session.get('_auth_user_id')


    
    # verificar información de asignación de la vacante
    asignacion_vacante = get_object_or_404(Cli056AplicacionVacante, id=pk)

    #obtener información del candidato
    info_candidato = get_object_or_404(Can101Candidato, id=asignacion_vacante.candidato_101.id)
    info_detalle_candidato = buscar_candidato(asignacion_vacante.candidato_101.id)

    #obtener información del historico de la vacante:
    historico_vacante = consultar_historial_aplicacion_vacante(asignacion_vacante.id)
    # obtener los datos de las entrevistas
    entrevista = Cli057AsignacionEntrevista.objects.filter(asignacion_vacante=asignacion_vacante.id).order_by('-fecha_entrevista')
    

    # Verificar si el cliente_id está en la sesión
    cliente_id = request.session.get('cliente_id')
    cliente = get_object_or_404(Cli051Cliente, id=cliente_id)
    
    # Obtener información de la vacante
    vacante = query_vacanty_detail().get(id=asignacion_vacante.vacante_id_052.id)

    # Obtener los reclutados asociados a la vacante
    reclutados = query_recruited_vacancy_id(vacante.id)

    form = EntrevistaCrearForm(request.POST, grupo_id=4, cliente_id=cliente_id)
    
    if request.method == 'POST':
        if form.is_valid():
            fecha_entrevista = form.cleaned_data['fecha_entrevista']
            hora_entrevista = form.cleaned_data['hora_entrevista']
            entrevistador = form.cleaned_data['entrevistador']
            tipo_entrevista = form.cleaned_data['tipo_entrevista']
            lugar_enlace = form.cleaned_data['lugar_enlace']
            usuario_asignado = get_object_or_404(UsuarioBase, id=entrevistador)

            # Obtener instancias de los modelos relacionados
            usuario_asigno = request.user  # Asumiendo que el usuario actual es quien asigna la entrevista
            estado_default = Cat001Estado.objects.get(id=1)  # Asumiendo que 1 es el estado por defecto

            # Crear la nueva asignación de entrevista
            asignacion_entrevista = Cli057AsignacionEntrevista.objects.create(
                asignacion_vacante=asignacion_vacante,
                usuario_asigno=usuario_asigno,
                usuario_asignado=usuario_asignado,
                fecha_entrevista=fecha_entrevista,
                hora_entrevista=hora_entrevista,
                tipo_entrevista=tipo_entrevista,
                lugar_enlace=lugar_enlace,
                estado_asignacion=1,  # Pendiente por defecto
                estado=estado_default,
            )

            #funcion para crear registro en el historial y actualizar estado de la aplicacion de la vcatente
            crear_historial_aplicacion(asignacion_vacante, 2, request.session.get('_auth_user_id'), 'Entrevista Asignada')
            
            contexto_email_1 = {
                'entrevistador' : f'{usuario_asignado.primer_nombre} {usuario_asignado.segundo_nombre} {usuario_asignado.primer_apellido}',
                'nombre_candidato' : f'{info_candidato.primer_nombre} {info_candidato.segundo_nombre} {info_candidato.primer_apellido} {info_candidato.segundo_apellido}' ,
                'fecha_entrevista' : fecha_entrevista,
                'hora_entrevista' : hora_entrevista,
                'lugar_enlace' : lugar_enlace,
                'vacante' : vacante.titulo,
                'cliente' : cliente.razon_social,
                'url' : url_actual
            }

            lista_correos = [
                usuario_asignado.email,
                info_candidato.email
            ]

            # Envio de correo
            enviar_correo('asignacion_entrevista_entrevista', contexto_email_1, f'Asginación de Entrevista ID: {asignacion_entrevista.id}', lista_correos, correo_remitente=None)

            frase_aleatoria = 'Se ha asignado entrevista correctamente.'
            messages.success(request, frase_aleatoria)

            return redirect('reclutados:reclutados_detalle_cliente', pk=pk)
        else:
            messages.error(request, 'Error al crear la asignación')
    else:
        form = EntrevistaCrearForm(grupo_id=4, cliente_id=cliente_id)

    context ={
        'form': form,
        'vacante': vacante,
        'reclutados': reclutados,
        'candidato': info_candidato,
        'reclutado': asignacion_vacante,
        'entrevista': entrevista,
        'info_detalle_candidato': info_detalle_candidato,
        'historial': historico_vacante,
    }

    return render(request, 'admin/recruited/client_user/recruited_detail.html', context)