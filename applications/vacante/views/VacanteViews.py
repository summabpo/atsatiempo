from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, Count, Q
from applications.cliente.models import Cli051Cliente
from applications.vacante.forms.VacanteForms import VacanteForm, VacanteFormEdit
from applications.vacante.models import Cli052Vacante, Cli055ProfesionEstudio, Cli053SoftSkill, Cli054HardSkill, Cli052VacanteHardSkillsId054, Cli052VacanteSoftSkillsId053, Cli056AplicacionVacante, Cli057AsignacionEntrevista
from applications.usuarios.models import Permiso
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.candidato.models import Can101Candidato
from django.contrib import messages
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required
from applications.usuarios.decorators  import validar_permisos

# utils
from applications.vacante.views.consultas.AsignacionVacanteConsultaView import consulta_asignacion_vacante_candidato

# forms
from applications.vacante.forms.VacanteFilterForm import VacanteFilterForm

centinela = None

#ADMIN

#CLIENTE

# Ver vacantes por id cliente para ver todas las vacantes que ha creado
@login_required
@validar_permisos(*Permiso.obtener_nombres())
def ver_vacante_cliente(request):
    
    # Verificar si el cliente_id está en la sesión
    cliente_id = request.session.get('cliente_id')
    primer_nombre = request.session.get('primer_nombre')
    
    # Obtener el cliente usando el id de la sesión
    cliente = get_object_or_404(Cli051Cliente, pk=cliente_id)
    #estado_general_vacante
    estado = Cat001Estado.objects.get(id=1)
    #listado vacantes activas
    vacantes = Cli052Vacante.objects.annotate(num_aplicaciones=Count('aplicaciones')).filter(cliente_id_051=cliente.id, estado_id_001=1).order_by('-id')

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
        vacantes = Cli052Vacante.objects.annotate(num_aplicaciones=Count('aplicaciones')).filter(cliente_id_051=cliente.id, estado_id_001=1).order_by('-id')

    return render(request, 'vacante/listado_vacantes_cliente.html',
        { 
            'form': form,
            'vacantes': vacantes,
            'cliente': cliente,
            'form_errors': form_errors,
            'primer_nombre': primer_nombre,
        })

# vacante por cliente sin loqin 
def vacante_cliente_mostrar(request, pk=None):
    #datos clientes
    cliente = get_object_or_404(Cli051Cliente, pk=pk)
    #estado_general_vacante
    estado = Cat001Estado.objects.get(id=1)
    #listado vacantes activas
    vacantes = Cli052Vacante.objects.filter(cliente_id_051=cliente.id, estado_id_001=1).order_by('-id')

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
            return redirect('vacantes:vacantes_cliente', pk=cliente.id)
        else:
            form_errors = True
            messages.error(request, form.errors)
    else:
        form = VacanteForm()
        form_edit = VacanteFormEdit()
        vacantes = Cli052Vacante.objects.filter(cliente_id_051=cliente.id, estado_id_001=1).order_by('-id')

    return render(request, 'vacante/listado_vacantes_cliente.html',
        { 
            'form': form,
            'form_edit': form_edit,
            'vacantes': vacantes,
            'cliente': cliente,
            'form_errors': form_errors,
        })    


#Ver Gestión de la vacante
@login_required
@validar_permisos(*Permiso.obtener_nombres())
def vacante_gestion(request, pk):
    vacante = get_object_or_404(Cli052Vacante, pk=pk)
    cliente = get_object_or_404(Cli051Cliente, id=vacante.cliente_id_051.id)
    vacante_aplicada = Cli056AplicacionVacante.objects.filter(vacante_id_052=vacante.id)

    user_id = request.session.get('_auth_user_id')
    print(user_id)

    contexto = {
        'vacante': vacante,
        'cliente': cliente,
        'vacante_aplicada': vacante_aplicada,
    }

    return render(request, 'vacante/gestion_vacante.html', contexto)

#CANDIDATO

#Ver vacantes aplicadas del candidato
@login_required
@validar_permisos(*Permiso.obtener_nombres())
def ver_vacante_candidato_aplicadas(request):
    candidato_id = request.session.get('candidato_id')
    candidato = get_object_or_404(Can101Candidato, id=candidato_id)
    # vacante_aplicada = Cli056AplicacionVacante.objects.filter(candidato_101=candidato.id)
    # vacante = get_object_or_404(Cli052Vacante, id=vacante_aplicada.vacante_id_052)
    vacante_aplicada = consulta_asignacion_vacante_candidato(candidato.id)
    contexto = {
        # 'vacante': vacante,
        'vacante_aplicada' : vacante_aplicada,

    }

    return render(request, 'vacante/vacante_candidato.html', contexto)

#Confirmación de Vacante Aplicada
@login_required
@validar_permisos(*Permiso.obtener_nombres())
def vacante_aplicada(request, pk):
    error_vacante = False

    candidato_id = request.session.get('candidato_id')
    vacante = get_object_or_404(Cli052Vacante, id=pk)
    candidato = get_object_or_404(Can101Candidato, id=candidato_id)
    # Verifica si ya existe una aplicación para esta vacante y este candidato
    aplicacion_existente = Cli056AplicacionVacante.objects.filter(
        candidato_101=candidato,
        vacante_id_052=vacante
    ).exists()


    if aplicacion_existente:
        messages.warning(request, 'Ya has aplicado a esta vacante anteriormente.')
        error_vacante = True
    else:
        Cli056AplicacionVacante.objects.create(
                candidato_101=candidato,
                vacante_id_052=vacante
            )
        messages.success(request, 'Has aplicado a la vacante con éxito.')

    return render(request, 'vacante/aplicar_vacante.html',
        { 
            'vacantes': vacante,
            'error_vacante': error_vacante,
        })

#Ver Detalle de la vacante
@login_required
@validar_permisos(*Permiso.obtener_nombres())
def vacante_detalle(request, pk):

    candidato_id = candidato_id = request.session.get('candidato_id')
    candidato = get_object_or_404(Can101Candidato, id=candidato_id)

    vacante = get_object_or_404(Cli052Vacante, pk=pk)
    cliente = get_object_or_404(Cli051Cliente, id=vacante.cliente_id_051.id)

    try:
        asignacion_vacante = Cli056AplicacionVacante.objects.get(
            candidato_101=candidato.id, vacante_id_052=vacante.id
        )
        
    except Cli056AplicacionVacante.DoesNotExist:
        asignacion_vacante = None
        asignacion_entrevista = None
    
    # Ajuste validación entrevista.
    asignacion_entrevista = None
    if asignacion_vacante:
        try:
            asignacion_entrevista = Cli057AsignacionEntrevista.objects.get(
                asignacion_vacante=asignacion_vacante.id
            )
        except Cli057AsignacionEntrevista.DoesNotExist:
            asignacion_entrevista = None
    user_id = request.session.get('_auth_user_id')

    print(user_id)

    contexto = {
        'vacante': vacante,
        'cliente': cliente,
        'asignacion_vacante': asignacion_vacante,
        'asignacion_entrevista': asignacion_entrevista,
    }
    return render(request, 'vacante/detalle_vacante.html', contexto)

def vacante_api(request, pk=None):
    global centinela

    if request.method == 'GET':
        id_vacante = request.GET.get('dato')
        vacante = Cli052Vacante.objects.get(id=id_vacante)

        centinela = vacante.id

        ciudad = Cat004Ciudad.objects.get(id=vacante.ciudad.id)
        profesion = Cli055ProfesionEstudio.objects.get(id=vacante.profesion_estudio_id_055.id)
        print(profesion)

        response_data = {
            'data': {
                'id': vacante.id,
                'titulo': vacante.titulo,
                'numero_posiciones': vacante.numero_posiciones,
                'profesion_estudio': profesion.nombre,
                'experiencia': vacante.experiencia_requerida,
                'soft_skills': vacante.numero_posiciones,
                'hard_skills': vacante.numero_posiciones,
                'funciones_responsabilidades': vacante.funciones_responsabilidades,
                'salario': vacante.salario,
                'ciudad': ciudad.id,
            }
        }

        print(response_data);
        return JsonResponse(response_data)

# Listado de Vacantes Activas
def buscar_vacante(request):

    vacantes = Cli052Vacante.objects.filter(
        estado_id_001=1,
        estado_vacante__in=[1, 2]
    )

    form = VacanteFilterForm(request.GET or None)

    if form.is_valid():
        ciudad = form.cleaned_data.get('ciudad')
        salario_min = form.cleaned_data.get('salario_min')
        salario_max = form.cleaned_data.get('salario_max')
        experiencia = form.cleaned_data.get('experiencia_requerida')
        soft_skills = form.cleaned_data.get('soft_skills')
        hard_skills = form.cleaned_data.get('hard_skills')
        profesion = form.cleaned_data.get('profesion_estudio')

        #valida filtro ciudad
        if ciudad:
            vacantes = vacantes.filter(ciudad_id=ciudad)
        if salario_min:
            try:
                salario_min = int(salario_min.replace('.', '').strip())
                vacantes = vacantes.filter(salario__gte=salario_min)
            except ValueError:
                pass  # Ignorar si el valor no es válido
        if salario_max:
            try:
                salario_max = int(salario_max.replace('.', '').strip())
                vacantes = vacantes.filter(salario__lte=salario_max)
            except ValueError:
                pass  # Ignorar si el valor no es válido
        if experiencia:
            vacantes = vacantes.filter(experiencia_requerida=experiencia)
        if soft_skills:
            vacantes = vacantes.filter(soft_skills_id_053__in=soft_skills).distinct()
        if hard_skills:
            vacantes = vacantes.filter(hard_skills_id_054__in=hard_skills).distinct()
        if profesion:
            vacantes = vacantes.filter(profesion_estudio_id_055=profesion)
    else:
        # Si no se aplican filtros, limitar a los primeros 10 registros
        vacantes = vacantes[:10]

    return render(request, 'vacante/buscar_vacante.html', {'vacantes': vacantes, 'form': form})