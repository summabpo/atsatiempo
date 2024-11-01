from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from applications.usuarios.decorators  import validar_permisos
from django.contrib import messages
from applications.common.views.EnvioCorreo import enviar_correo, generate_token
from django.db.models import F
from django.http import JsonResponse
import json

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
            return redirect('vacantes:vacantes')
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

    asignacion_entrevista = consulta_asignacion_entrevista_cliente(cliente_id)

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
    entrevista = get_object_or_404(Cli057AsignacionEntrevista, pk=pk)
        # Formulario Vacantes
    if request.method == 'POST': 
        form = EntrevistaGestionForm(request.POST)
        if form.is_valid():
            titulo = form.cleaned_data['titulo']
            numero_posiciones = form.cleaned_data['numero_posiciones']
        else:
            messages.error(request, form.errors)
    else:
        # Formulario Entrevista
        form = EntrevistaGestionForm(request.POST)
        entrevista = get_object_or_404(Cli057AsignacionEntrevista, pk=pk)
    contexto = {
        'form' : form,
        'entrevista' : entrevista
    }

    return render(request, 'vacante/gestion_entrevista.html', contexto)