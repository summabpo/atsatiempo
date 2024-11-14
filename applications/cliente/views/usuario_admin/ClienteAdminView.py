import random
import string
from django.shortcuts import render, redirect
import json
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from applications.usuarios.decorators  import validar_permisos
from django.db.models import F, Value
from django.db.models.functions import Concat

#model
from applications.vacante.models import Cli052Vacante, Cli055ProfesionEstudio, Cli053SoftSkill, Cli052VacanteSoftSkillsId053, Cli054HardSkill, Cli052VacanteHardSkillsId054, Cli056AplicacionVacante, Cli057AsignacionEntrevista
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.usuarios.models import Permiso
from applications.cliente.models import Cli051Cliente
from applications.usuarios.models import UsuarioBase, Grupo

#form
from applications.vacante.forms.VacanteForms import VacanteForm, VacanteFormEdit
from applications.cliente.forms.ClienteForms import ClienteForm
from applications.cliente.forms.CreacionUsuariosForm import CrearUsuarioInternoForm

#utils
from applications.common.views.EnvioCorreo import enviar_correo, generate_token
from applications.vacante.views.consultas.AsignacionVacanteConsultaView import consulta_asignacion_vacante, consulta_asignacion_vacante_id
from applications.vacante.views.consultas.AsignacionEntrevistaConsultaView import consulta_asignacion_entrevista_cliente
from applications.vacante.views.consultas.VacanteConsultaView import consulta_vacantes_todas

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

# Portal interno
# Mostrar todos los clientes todos
@login_required
@validar_permisos(*Permiso.obtener_nombres())
def cliente_listar(request):
    clientes = Cli051Cliente.objects.filter(estado_id_001=1).order_by('-id')
    form_errors = False

    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES)
        if form.is_valid():
            ClienteForm.logo = form.cleaned_data['logo']
            form.save()
            messages.success(request, 'Cliente Creado!')
            return redirect('clientes:cliente_listar')  # Cambia a la vista deseada después de guardar
        else:
            form_errors = True
            form = ClienteForm(request.POST, request.FILES)
    else:
        form = ClienteForm()

    
    return render(request, 'cliente/cliente_listar.html', {
        'clientes': clientes,
        'form': form,
        'form_errors': form_errors,
        })

# Mostrar Listado de cada cliente
@login_required
@validar_permisos(*Permiso.obtener_nombres())
def cliente_detalle(request, pk):

    cliente = get_object_or_404(Cli051Cliente, pk=pk)

    contexto = {
        'cliente' : cliente,
    }

    return render(request, 'cliente/cliente_detalle.html', contexto)

@login_required
@validar_permisos(*Permiso.obtener_nombres())
def cliente_grupo_trabajo(request, pk):
    url_actual = f"{request.scheme}://{request.get_host()}"
    form_errores = False
    cliente = get_object_or_404(Cli051Cliente, pk=pk)

    usuarios_internos = UsuarioBase.objects.filter(group__in=[4, 5], cliente_id_051=cliente)

    if request.method == 'POST':
        form_creacion = CrearUsuarioInternoForm(request.POST)
        if form_creacion.is_valid():
            #campos del form
            primer_nombre = form_creacion.cleaned_data['primer_nombre']
            segundo_nombre = form_creacion.cleaned_data['segundo_nombre']
            primer_apellido = form_creacion.cleaned_data['primer_apellido']
            segundo_apellido = form_creacion.cleaned_data['segundo_apellido']
            correo = form_creacion.cleaned_data['correo']
            rol = form_creacion.cleaned_data['rol']

            grupo = get_object_or_404(Grupo, id=rol)

            passwordoriginal = generate_random_password()

            user = UsuarioBase.objects.create_user(
                username= correo, 
                email= correo, 
                primer_nombre = primer_nombre.capitalize(), 
                segundo_nombre = segundo_nombre.capitalize(), 
                primer_apellido = primer_apellido.capitalize(), 
                segundo_apellido = segundo_apellido.capitalize(),  
                password=passwordoriginal,
                cliente_id_051 = cliente,
                is_verificado = True,
                group=grupo,
            )

            # Envio del correo electronico de confirmación del usuario y contraseña
            contexto_mail = {
                'name': primer_nombre.capitalize(),
                'last_name': primer_apellido.capitalize(),
                'user': correo,
                'email': correo,
                'password': passwordoriginal,
                'url' : url_actual,
            }

            # Envio de correo
            enviar_correo('creacion_usuario_cliente', contexto_mail, 'Creación de Usuario Interno ATS', [correo], correo_remitente=None)

            frase_aleatoria = 'Se ha enviado un correo electronico para su validar el mismo.'
            messages.success(request, frase_aleatoria)
            return redirect('clientes:cliente_grupo_trabajo', pk=pk)

        else:
            form_errores = True
            messages.error(request, 'Error al crear usuario interno')
    else:
        form_creacion = CrearUsuarioInternoForm()

    contexto = {
        'cliente' : cliente,
        'usuarios_internos': usuarios_internos,
        'form_creacion': form_creacion,
        'form_errores': form_errores,
    }
    return render(request, 'cliente/cliente_grupo_trabajo.html', contexto)

# Mostrar detalle de cada cliente
@login_required
@validar_permisos(*Permiso.obtener_nombres())
def cliente_vacante(request, pk):

    vacante = Cli052Vacante.objects.filter(cliente_id_051= pk).order_by('-id')

    estado = Cat001Estado.objects.get(id=1)
    form_errors = False
    cliente = get_object_or_404(Cli051Cliente, pk=pk)

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
            return redirect('clientes:cliente_vacante', pk=cliente.id)
        else:
            form_errors = True
            messages.error(request, form.errors)
    else:
        form_errors = True
        form = VacanteForm()

    contexto = {
        'form' : form,
        'cliente' : cliente,
        'vacante' : vacante,
        'form_errors' : form_errors
    }        
    
    return render(request, 'cliente/cliente_vacante.html', contexto)

# Mostrar detalle de cada vacante
@login_required
@validar_permisos(*Permiso.obtener_nombres())
def cliente_vacante_detalle(request, pk):
    vacante = get_object_or_404(Cli052Vacante, pk=pk)
    cliente = get_object_or_404(Cli051Cliente, pk=vacante.cliente_id_051.id)
    candidato_aplicante = Cli056AplicacionVacante.objects.select_related(
        'vacante_id_052',
        'candidato_101'
    ).filter(
        vacante_id_052__id=vacante.id
    ).order_by('fecha_aplicacion')


    contexto = {
        'cliente' : cliente,
        'vacante' : vacante,
        'candidato_aplicante' : candidato_aplicante,
    }        
    
    return render(request, 'cliente/cliente_vacante_detalle.html', contexto)

# Mostrar reclutamiento de la vacante_seleccionada vacante
@login_required
@validar_permisos(*Permiso.obtener_nombres())
def cliente_vacante_reclutado(request, pk):
    vacante = get_object_or_404(Cli052Vacante, pk=pk)
    asignacion_vacante = consulta_asignacion_vacante_id(vacante.id)
    cliente = get_object_or_404(Cli051Cliente, pk=vacante.cliente_id_051.id)
    candidato_aplicante = Cli056AplicacionVacante.objects.select_related(
        'vacante_id_052',
        'candidato_101'
    ).filter(
        vacante_id_052__id=vacante.id
    ).order_by('fecha_aplicacion')


    contexto = {
        'cliente' : cliente,
        'vacante' : vacante,
        'candidato_aplicante' : candidato_aplicante,
        'asignacion_vacante' : asignacion_vacante,
    }        
    
    return render(request, 'cliente/cliente_vacante_reclutado.html', contexto)

@login_required
@validar_permisos(*Permiso.obtener_nombres())
def cliente_vacante_entrevista(request, pk):
    vacante = get_object_or_404(Cli052Vacante, pk=pk)
    cliente = get_object_or_404(Cli051Cliente, pk=vacante.cliente_id_051.id)
    
    entrevista = Cli057AsignacionEntrevista.objects.select_related(
        'asignacion_vacante__vacante_id_052__cliente_id_051', 
        'asignacion_vacante__vacante_id_052', 
        'asignacion_vacante__candidato_101',
        'usuario_asigno'
        'usuario_asignado'
    ).filter(
        asignacion_vacante__vacante_id_052__id=vacante.id
    ).order_by('-fecha_entrevista').values(
        # Campos del modelo principal (Cli057AsignacionEntrevista)
        'id',
        'fecha_asignacion',
        'fecha_entrevista',
        'hora_entrevista',
        'tipo_entrevista',
        'lugar_enlace',
        'estado_asignacion',
        # Resto de clientes pendientes
        razon_social=F('asignacion_vacante__vacante_id_052__cliente_id_051__razon_social'),
        titulo_vacante=F('asignacion_vacante__vacante_id_052__titulo'),
        nombre_candidato = Concat(
            F('asignacion_vacante__candidato_101__primer_nombre'),
            Value(' '),
            F('asignacion_vacante__candidato_101__segundo_nombre'),
            Value(' '),
            F('asignacion_vacante__candidato_101__primer_apellido'),
            Value(' '),
            F('asignacion_vacante__candidato_101__segundo_apellido')
        ),
        nombre_asigno=Concat(
            F('usuario_asigno__primer_nombre'),
            Value(' '),
            F('usuario_asigno__primer_apellido')
        ),
        nombre_asignado=Concat(
            F('usuario_asignado__primer_nombre'),
            Value(' '),
            F('usuario_asignado__primer_apellido')
        ),
    )
    asignacion_entrevista = consulta_asignacion_entrevista_cliente(vacante.id)
    contexto = {
        'vacante' : vacante,
        'cliente' : cliente,
        'entrevista' : entrevista,
        'asignacion_entrevista' : asignacion_entrevista,
        
    }
    return render(request, 'cliente/cliente_vacante_entrevista.html', contexto)

@login_required
@validar_permisos(*Permiso.obtener_nombres())
def cliente_vacante_editar(request, pk):
    vacante = get_object_or_404(Cli052Vacante, pk=pk)
    cliente = get_object_or_404(Cli051Cliente, pk=vacante.cliente_id_051.id)

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
            return redirect('clientes:cliente_vacante_editar', pk=vacante.id)
        
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
        'vacante' : vacante,
        'cliente' : cliente,
        'form_vacante': form_vacante,
        
    }
    return render(request, 'cliente/cliente_vacante_editar.html', contexto)

@login_required
@validar_permisos(*Permiso.obtener_nombres())
def reclutados_todos(request):
    contexto = {
        'asignacion_vacante' : consulta_asignacion_vacante()
    }
    return render(request, 'cliente/cliente_vacante_reclutado_todos.html', contexto)

# Ver todas las vacantes activas
@login_required
@validar_permisos(*Permiso.obtener_nombres())
def vacantes_todos(request):
    
    vacantes = consulta_vacantes_todas() 

    return render(request, 'vacante/listado_vacantes_todos.html',
        { 
            'vacantes': vacantes,
        })