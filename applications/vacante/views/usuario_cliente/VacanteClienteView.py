from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from applications.usuarios.decorators  import validar_permisos
from django.contrib import messages
from applications.common.views.EnvioCorreo import enviar_correo, generate_token
from django.db.models import F
from django.http import JsonResponse
import json
from django.utils.timezone import now

#formularios
from applications.vacante.forms.EntrevistaForm import EntrevistaCrearForm
from applications.vacante.forms.VacanteForms import VacanteForm, VacanteFormEdit
from applications.vacante.forms.EntrevistaForm import EntrevistaGestionForm

#modelos
from applications.vacante.models import Cli057AsignacionEntrevista, Cli056AplicacionVacante, Cli052Vacante, Cli055ProfesionEstudio, Cli054HardSkill, Cli051Cliente, Cli052VacanteHardSkillsId054, Cli052VacanteSoftSkillsId053, Cli053SoftSkill
from applications.cliente.models import Cli051Cliente
from applications.usuarios.models import Permiso
from applications.usuarios.models import UsuarioBase
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.candidato.models import Can101Candidato

#consultas
from applications.vacante.views.consultas.VacanteConsultaView import consulta_vacantes_cliente
from applications.vacante.views.consultas.AsignacionVacanteConsultaView import consulta_asignacion_vacante_cliente
from applications.vacante.views.consultas.AsignacionEntrevistaConsultaView import consulta_asignacion_entrevista_cliente

#utils
from components.RegistrarHistorialVacante import crear_historial_aplicacion
from components.RegistrarGestionVacante import validar_vacante_cancelar

# Ver vacantes por id cliente para ver todas las vacantes que ha creado
@login_required
@validar_permisos(*Permiso.obtener_nombres())
def vacantes_cliente(request):
    
    # Verificar si el cliente_id está en la sesión
    cliente_id = request.session.get('cliente_id')
    primer_nombre = request.session.get('primer_nombre')
    
    # Obtener el cliente usando el id de la sesión
    cliente = get_object_or_404(Cli051Cliente, pk=cliente_id)
    #estado_general_vacante
    estado = Cat001Estado.objects.get(id=1)
    #listado vacantes activas
    vacantes = consulta_vacantes_cliente(request.session.get('cliente_id'))

    form_errors = False

    # Formulario Vacantes
    if request.method == 'POST': 
        form = VacanteForm(request.POST)
        
        if form.is_valid():
            #datos formulario

            titulo = form.cleaned_data['titulo']
            numero_posiciones = form.cleaned_data['numero_posiciones']
            profesion_estudio_id_055 = form.cleaned_data['profesion_estudio_id_055']
            experiencia_requerida = form.cleaned_data['experiencia_requerida']
            soft_skills_id_053 = form.cleaned_data['soft_skills_id_053']
            hard_skills_id_054 = form.cleaned_data['hard_skills_id_054']
            funciones_responsabilidades = form.cleaned_data['funciones_responsabilidades']
            salario = form.cleaned_data['salario']

            estado_id = Cat001Estado.objects.get(id=1)
            ciudad_id = Cat004Ciudad.objects.get(id=form.cleaned_data['ciudad'])

            # Intentar obtener el objeto profesion estudio
            profesion_estudio_dato, created = Cli055ProfesionEstudio.objects.get_or_create(
                nombre = profesion_estudio_id_055,
                defaults={'estado_id_001': estado}
            )

            #crea la vacante
            vacante_creada = Cli052Vacante.objects.create(
                titulo = titulo,
                numero_posiciones = numero_posiciones,
                experiencia_requerida = experiencia_requerida,
                funciones_responsabilidades = funciones_responsabilidades,
                salario = salario,
                estado_vacante = 1,
                ciudad_id = ciudad_id.id,
                cliente_id_051_id = cliente.id,
                estado_id_001_id = estado_id.id,
                profesion_estudio_id_055_id = profesion_estudio_dato.id,
            )

            # Convertir el string JSON en un objeto Python (lista de diccionarios)
            skills = json.loads(soft_skills_id_053)
            
            # Ahora puedes iterar sobre la lista de diccionarios
            for skill in skills:
                # Intentar obtener el objeto soft_skills
                soft_skills, created = Cli053SoftSkill.objects.get_or_create(
                    nombre = skill['value'],
                    defaults={'estado_id_001': estado}
                )

                Cli052VacanteSoftSkillsId053.objects.create(
                    cli052vacante=vacante_creada,
                    cli053softskill=soft_skills
                )

            # Convertir el string JSON en un objeto Python (lista de diccionarios)
            skills = json.loads(hard_skills_id_054)
            
            # Ahora puedes iterar sobre la lista de diccionarios
            for skill in skills:
                # Intentar obtener el objeto hard_skills
                hard_skills, created = Cli054HardSkill.objects.get_or_create(
                    nombre = skill['value'],
                    defaults={'estado_id_001': estado}
                )

                Cli052VacanteHardSkillsId054.objects.create(
                    cli052vacante=vacante_creada,
                    cli054hardskill=hard_skills
                )

            messages.success(request, 'El registro de la vacante ha sido creado con éxito.')
            return redirect('vacantes:vacantes_cliente_todas')
        else:
            form_errors = True
            messages.error(request, form.errors)
    else:
        form = VacanteForm()
        vacantes = consulta_vacantes_cliente(request.session.get('cliente_id'))

    contexto = { 
            'form': form,
            'vacantes': vacantes,
            'cliente': cliente,
            'form_errors': form_errors,
            'primer_nombre': primer_nombre,
        }
    return render(request, 'vacante/listado_vacantes_cliente.html', contexto)

# Ver vacantes por id cliente para ver todas las vacantes que ha creado
@login_required
@validar_permisos(*Permiso.obtener_nombres())
def gestion_vacante_reclutados(request, pk):
    vacante = get_object_or_404(Cli052Vacante, pk=pk)
    cliente_id = request.session.get('cliente_id')
    # Obtener el cliente usando el id de la sesión
    cliente = get_object_or_404(Cli051Cliente, pk=cliente_id)

    asignacion_vacante = consulta_asignacion_vacante_cliente(cliente_id, vacante.id)

    contexto = {
        'vacante' : vacante,
        'cliente' : cliente,
        'asignacion_vacante' : asignacion_vacante,
    }

    return render(request, 'vacante/gestion_vacante_reclutados.html', contexto)

# Ver vacantes por id cliente para ver todas las vacantes que ha creado
@login_required
@validar_permisos(*Permiso.obtener_nombres())
def gestion_vacante_entrevistas(request, pk):
    vacante = get_object_or_404(Cli052Vacante, pk=pk)
    cliente_id = request.session.get('cliente_id')
    # Obtener el cliente usando el id de la sesión
    cliente = get_object_or_404(Cli051Cliente, pk=cliente_id)

    asignacion_entrevista = consulta_asignacion_entrevista_cliente(vacante.id)

    contexto = {
        'vacante' : vacante,
        'cliente' : cliente,
        'asignacion_entrevista' : asignacion_entrevista,
    }

    return render(request, 'vacante/gestion_vacante_entrevistas.html', contexto)

# Ver vacantes por id cliente para ver todas las vacantes que ha creado
@login_required
@validar_permisos(*Permiso.obtener_nombres())
def gestion_entrevista(request, pk):

    cliente_id = request.session.get('cliente_id')
    grupo_id =  request.session.get('grupo_id')

    print(cliente_id)
    print(grupo_id)

    entrevista = get_object_or_404(Cli057AsignacionEntrevista, pk=pk)
    
    reclutamiento = entrevista.asignacion_vacante

    vacante = get_object_or_404(Cli052Vacante, id = reclutamiento.vacante_id_052.id)
    candidato = get_object_or_404(Can101Candidato, id = reclutamiento.candidato_101.id)
        # Formulario Vacantes
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
                crear_historial_aplicacion(reclutamiento, 4, request.session.get('_auth_user_id'), 'No aprobo la entrevista el candidato')
            if estado_asignacion == 4:
                estado_vacante = 8 # Se cambia estado de la vacante a seleccionado
                observacion_historial = 'Se selecciona candidato.'
            if estado_asignacion == 5:
                estado_vacante = 10 # Se cambia estado de la vacante a cancelado
                observacion_historial = 'Se cancela la postulación del candidato.'
            
            #crea el historial y actualiza el estado de la aplicacion de la vacante
            crear_historial_aplicacion(reclutamiento, estado_vacante, request.session.get('_auth_user_id'), observacion_historial)
            
            #actualizacion de gestión de entrevista
            entrevista.observacion = observacion
            entrevista.estado_asignacion = estado_asignacion
            entrevista.fecha_gestion = now()
            entrevista.save()

            messages.success(request, 'Se ha actualizado la entrevista.')

            
            
            if cliente_id:
                return redirect('vacantes:gestion_vacante_entrevistas', pk=vacante.id)
            else:
                return redirect('clientes:cliente_vacante_entrevista', pk=vacante.id)
        else:
            messages.error(request, form.errors)
    else:
        # Formulario Entrevista
        form = EntrevistaGestionForm()
        entrevista = get_object_or_404(Cli057AsignacionEntrevista, pk=pk)
    contexto = {
        'form' : form,
        'entrevista' : entrevista,
        'vacante' : vacante,
        'candidato' : candidato,
    }

    return render(request, 'vacante/gestionar_entrevista.html', contexto)

# Ver vacantes por id cliente para ver todas las vacantes que ha creado
@login_required
@validar_permisos(*Permiso.obtener_nombres())
def gestion_vacante_cancelar(request, pk):
    vacante = get_object_or_404(Cli052Vacante, pk=pk)
    cliente = get_object_or_404(Cli051Cliente, id=vacante.cliente_id_051.id)
    url_actual =  f"{request.scheme}://{request.get_host()}"
    
    #valida candidatos en estados pendientes por gestionar y los cancela
    validar_vacante_cancelar(vacante, url_actual)
    
    #cambia el estado de la vacante a cancelada
    vacante.estado_vacante = 4
    vacante.save()
    
    messages.success(request, 'Se ha cancelado la vacante.')

    contexto = {
        'vacante': vacante,
        'cliente': cliente,
    }

    return render(request, 'vacante/gestion_vacante_cancelar.html', contexto)

@login_required
@validar_permisos(*Permiso.obtener_nombres())
def gestion_vacante_editar(request, pk):

    # Se obtiene información de la vacante
    vacante = get_object_or_404(Cli052Vacante, pk=pk)
    
    # Define los datos iniciales que quieres pasar al formulario
    initial_data = {
        'titulo': vacante.titulo,
        'numero_posiciones': vacante.numero_posiciones,
        'profesion_estudio_id_055': vacante.profesion_estudio_id_055.nombre,
        'experiencia_requerida': vacante.experiencia_requerida,
        'soft_skills_id_053': ','.join([skill.nombre for skill in vacante.soft_skills_id_053.all()]),
        'hard_skills_id_054': ','.join([skill.nombre for skill in vacante.hard_skills_id_054.all()]),
        'funciones_responsabilidades': vacante.funciones_responsabilidades,
        'ciudad': vacante.ciudad.id if vacante.ciudad else '',
        'salario': vacante.salario,
    }

    # form_vacante = VacanteFormEdit()
    form_vacante = VacanteFormEdit(initial=initial_data)

    # Formulario Vacantes
    if request.method == 'POST': 
        form_vacante = VacanteFormEdit(request.POST)
        if form_vacante.is_valid():
            vacante.titulo = form_vacante.cleaned_data['titulo']
            vacante.numero_posiciones = form_vacante.cleaned_data['numero_posiciones']

            profesion_instance, created = Cli055ProfesionEstudio.objects.get_or_create(nombre=form_vacante.cleaned_data['profesion_estudio_id_055'])
            vacante.profesion_estudio_id_055 = profesion_instance


            vacante.experiencia_requerida = form_vacante.cleaned_data['experiencia_requerida']
            vacante.funciones_responsabilidades = form_vacante.cleaned_data['funciones_responsabilidades']

            soft_skills_id_053 = form_vacante.cleaned_data['soft_skills_id_053']
            hard_skills_id_054 = form_vacante.cleaned_data['hard_skills_id_054']
            
            # Buscar la instancia de Cat004Ciudad usando el ID proporcionado
            ciudad = Cat004Ciudad.objects.get(id=form_vacante.cleaned_data['ciudad'])
            vacante.ciudad = ciudad
            vacante.salario = form_vacante.cleaned_data['salario']

            estado_id = Cat001Estado.objects.get(id=1)
            
            print(form_vacante.cleaned_data['soft_skills_id_053'])
            # Convertir el string JSON en un objeto Python (lista de diccionarios)
            skills = json.loads(soft_skills_id_053)
            
            # Limpiar habilidades blandas existentes antes de agregar nuevas
            Cli052VacanteSoftSkillsId053.objects.filter(cli052vacante=vacante).delete()

            # Ahora puedes iterar sobre la lista de diccionarios
            for skill in skills:
                # Intentar obtener el objeto soft_skills
                soft_skills, created = Cli053SoftSkill.objects.get_or_create(
                    nombre = skill['value'],
                    defaults={'estado_id_001': estado_id}
                )

                Cli052VacanteSoftSkillsId053.objects.create(
                    cli052vacante=vacante,
                    cli053softskill=soft_skills
                )

            # Convertir el string JSON en un objeto Python (lista de diccionarios)
            skills = json.loads(hard_skills_id_054)

            # Limpiar habilidades duras existentes antes de agregar nuevas
            Cli052VacanteHardSkillsId054.objects.filter(cli052vacante=vacante).delete()
            
            # Ahora puedes iterar sobre la lista de diccionarios
            for skill in skills:
                # Intentar obtener el objeto hard_skills
                hard_skills, created = Cli054HardSkill.objects.get_or_create(
                    nombre = skill['value'],
                    defaults={'estado_id_001': estado_id}
                )

                Cli052VacanteHardSkillsId054.objects.create(
                    cli052vacante=vacante,
                    cli054hardskill=hard_skills
                )

            vacante.save()

            messages.success(request, 'El registro de la vacante ha sido actualizado con éxito.')
            return redirect('vacantes:gestion_vacante_editar', pk=vacante.id)
        
            # Valida si esta valido la variable de sesion cliente
            # cliente_id = request.session.get('cliente_id')
            # if cliente_id:
            #     return redirect('vacantes:gestion_vacante_editar', pk=vacante.id)
            # else:
            #     return redirect('clientes:gestion_vacante_editar', pk=vacante.id)
        else:
            messages.error(request, form_vacante.errors)    
    else:

        form_vacante = VacanteFormEdit(initial=initial_data)
        # Se obtiene información de la vacante

    contexto = {
        'vacante': vacante,
        'form_vacante': form_vacante,
    }

    return render(request, 'vacante/gestionar_editar_vacante.html', contexto)