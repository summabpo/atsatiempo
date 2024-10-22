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

# Ver todas las vacantes activas
@login_required
@validar_permisos(*Permiso.obtener_nombres())
def ver_vacante_cliente_todos(request):
    
    vacantes = Cli052Vacante.objects.filter(estado_id_001=1).order_by('-id')

    return render(request, 'vacante/listado_vacantes_todos.html',
        { 
            'vacantes': vacantes,
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
    vacante_aplicada = Cli056AplicacionVacante.objects.filter(candidato_101=candidato.id)
    # vacante = get_object_or_404(Cli052Vacante, id=vacante_aplicada.vacante_id_052)

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
        asignacion_entrevista = Cli057AsignacionEntrevista.objects.get(
            asignacion_vacante=asignacion_vacante.id
        )
    except Cli056AplicacionVacante.DoesNotExist:
        asignacion_vacante = None
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
