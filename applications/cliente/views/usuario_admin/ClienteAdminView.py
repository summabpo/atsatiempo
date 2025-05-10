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
from django.utils import timezone
from datetime import datetime, timedelta

#model
from applications.vacante.models import Cli052Vacante, Cli055ProfesionEstudio, Cli053SoftSkill, Cli052VacanteSoftSkillsId053, Cli054HardSkill, Cli052VacanteHardSkillsId054
from applications.reclutado.models import Cli056AplicacionVacante
from applications.entrevista.models import Cli057AsignacionEntrevista
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.usuarios.models import Permiso
from applications.cliente.models import Cli051Cliente
from applications.usuarios.models import UsuarioBase, Grupo, TokenAutorizacion
from applications.candidato.models import Can101Candidato, Can101CandidatoSkill, Can102Experiencia, Can103Educacion, Can104Skill

#form
from applications.vacante.forms.VacanteForms import VacanteForm, VacanteFormEdit, VacanteAdicionalForms
from applications.cliente.forms.ClienteForms import ClienteForm, ClienteFormEdit
from applications.usuarios.forms.CreacionUsuariosForm import CrearUsuarioInternoForm

#utils
from applications.common.views.EnvioCorreo import enviar_correo, generate_token
from applications.vacante.views.consultas.AsignacionVacanteConsultaView import consulta_asignacion_vacante, consulta_asignacion_vacante_id
from applications.vacante.views.consultas.AsignacionEntrevistaConsultaView import consulta_asignacion_entrevista_cliente
from applications.vacante.views.consultas.VacanteConsultaView import consulta_vacantes_todas, consulta_vacantes_cliente
from components.EmparejamientoVacantesCandidato import calcular_match

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

# Portal interno
# Mostrar todos los clientes todos
@login_required
@validar_permisos('acceso_admin')
def cliente_listar(request):
    url_actual = f"{request.scheme}://{request.get_host()}"
    clientes = Cli051Cliente.objects.filter(estado_id_001=1).order_by('-id')
    form_errors = False

    if request.method == 'POST':
        form_cliente = ClienteForm(request.POST, request.FILES)
        if form_cliente.is_valid():
            
            razon_social = form_cliente.cleaned_data['razon_social']
            nit = form_cliente.cleaned_data['nit']
            email = form_cliente.cleaned_data['email']
            contacto = form_cliente.cleaned_data['contacto']
            telefono = form_cliente.cleaned_data['telefono']
            perfil_empresarial = form_cliente.cleaned_data['perfil_empresarial']
            estado_id_001 = Cat001Estado.objects.get(id=1)
            ciudad_id_004 = Cat004Ciudad.objects.get(id = form_cliente.cleaned_data['ciudad_id_004'])
            
            # Manejo del campo logo (imagen)
            if form_cliente.cleaned_data.get('logo'):
                logo = form_cliente.cleaned_data['logo']
            else:
                logo = None

            cliente = Cli051Cliente.objects.create(
                razon_social = razon_social,
                nit = nit,
                email = email,
                contacto = contacto,
                telefono = telefono,
                perfil_empresarial = perfil_empresarial,
                estado_id_001 = estado_id_001,
                ciudad_id_004 = ciudad_id_004,
                logo = logo
            )

            password = generate_random_password()

            grupo = Grupo.objects.get(id=3)
            user = UsuarioBase.objects.create_user(
                username= email, 
                email= email, 
                password=password,
                cliente_id_051 = cliente ,
                primer_nombre = contacto.capitalize() ,
                primer_apellido = contacto.capitalize(),  
                group=grupo,
            )

            token_generado = generate_token(50);

            TokenAutorizacion.objects.create(
                user_id=user.id,
                token=token_generado,  # Una función que genere un token único
                fecha_expiracion=timezone.now() + timedelta(days=2),  # Si tiene fecha de expiración
            )    

            # Envio del correo electronico de confirmación del usuario y contraseña
            contexto = {
                'name': contacto.capitalize(),
                'last_name': contacto.capitalize(),
                'user': user,
                'email': email,
                'password': password,
                'token': token_generado,
                'url': url_actual
            }

            # Envia el metodo
            enviar_correo('bienvenida', contexto, 'Creación de Usuario ATS', [email], correo_remitente=None)
            
            messages.success(request, 'Cliente Creado!, Se ha enviado al correo del cliente el usuario y la contraseña')
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
@validar_permisos('acceso_admin')
def  cliente_detalle(request, pk):

    cliente = get_object_or_404(Cli051Cliente, pk=pk)
    contadores_vacantes = Cli052Vacante.contar_vacantes_por_estado(cliente.id)

    # Define los datos iniciales que quieres pasar al formulario
    initial_data = {
        'estado_id_001': cliente.estado_id_001.id if cliente.estado_id_001 else '',
        'nit': cliente.nit,
        'razon_social': cliente.razon_social,
        'ciudad_id_004': cliente.ciudad_id_004.id if cliente.ciudad_id_004 else '',
        'email': cliente.email,
        'contacto': cliente.contacto,
        'telefono': cliente.telefono,
        'perfil_empresarial': cliente.perfil_empresarial,
        'logo': cliente.logo.url if cliente.logo else '',
    }

    form_cliente = ClienteFormEdit(initial=initial_data)

    #logica para mostrar el form
    if request.method == 'POST':
        form_cliente = ClienteFormEdit(request.POST, request.FILES)
        if form_cliente.is_valid():

            cliente.razon_social = form_cliente.cleaned_data['razon_social']
            cliente.nit = form_cliente.cleaned_data['nit']
            cliente.email = form_cliente.cleaned_data['email']
            cliente.contacto = form_cliente.cleaned_data['contacto']
            cliente.telefono = form_cliente.cleaned_data['telefono']
            cliente.perfil_empresarial = form_cliente.cleaned_data['perfil_empresarial']
            cliente.estado_id_001 = Cat001Estado.objects.get(id=1)
            cliente.ciudad_id_004 = Cat004Ciudad.objects.get(id = form_cliente.cleaned_data['ciudad_id_004'])

            # Manejo del campo logo (imagen)
            if form_cliente.cleaned_data.get('logo'):
                cliente.logo = form_cliente.cleaned_data['logo']

            cliente.save()

            messages.success(request, 'El cliente ha sido actualizado con éxito.')
            return redirect('clientes:cliente_detalle', pk=cliente.id)

        else:
            messages.error(request, form_cliente.errors)  
    else:
        form_cliente = ClienteFormEdit(initial=initial_data)
    contexto = {
        'cliente' : cliente,
        'form_cliente' : form_cliente,
        'contadores_vacantes' : contadores_vacantes,
    }

    return render(request, 'cliente/cliente_detalle.html', contexto)

@login_required
@validar_permisos('acceso_admin')
def cliente_grupo_trabajo(request, pk):
    url_actual = f"{request.scheme}://{request.get_host()}"
    form_errores = False
    cliente = get_object_or_404(Cli051Cliente, pk=pk)
    contadores_vacantes = Cli052Vacante.contar_vacantes_por_estado(pk)

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
        'contadores_vacantes': contadores_vacantes,
    }
    return render(request, 'cliente/cliente_grupo_trabajo.html', contexto)

# Mostrar detalle de cada cliente
@login_required
@validar_permisos('acceso_admin')
def cliente_vacante(request, pk):

    vacante = Cli052Vacante.objects.filter(cliente_id_051= pk).order_by('-id')
    contadores_vacantes = Cli052Vacante.contar_vacantes_por_estado(pk)

    listado_vacante = consulta_vacantes_cliente(pk)

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
        'listado_vacante' : listado_vacante,
        'form_errors' : form_errors,
        'contadores_vacantes' : contadores_vacantes,
    }        

    return render(request, 'cliente/cliente_vacante.html', contexto)

# Mostrar detalle de cada vacante
@login_required
@validar_permisos('acceso_admin')
def cliente_vacante_detalle(request, pk):
    vacante = get_object_or_404(Cli052Vacante, pk=pk)
    cliente = get_object_or_404(Cli051Cliente, pk=vacante.cliente_id_051.id)
    candidato_aplicante = Cli056AplicacionVacante.objects.select_related(
        'vacante_id_052',
        'candidato_101'
    ).filter(
        vacante_id_052__id=vacante.id
    ).order_by('fecha_aplicacion')

    contadores_reclutados = Cli056AplicacionVacante.calcular_cantidades_y_porcentajes(pk)



    contexto = {
        'cliente' : cliente,
        'vacante' : vacante,
        'candidato_aplicante' : candidato_aplicante,
        'contadores_reclutados' : contadores_reclutados,
    }        
    
    return render(request, 'cliente/cliente_vacante_detalle.html', contexto)

# Mostrar reclutamiento de la vacante_seleccionada vacante
@login_required
@validar_permisos('acceso_admin')
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

    contadores_reclutados = Cli056AplicacionVacante.calcular_cantidades_y_porcentajes(pk)

    contexto = {
        'cliente' : cliente,
        'vacante' : vacante,
        'candidato_aplicante' : candidato_aplicante,
        'asignacion_vacante' : asignacion_vacante,
        'contadores_reclutados' : contadores_reclutados,
    }        
    
    return render(request, 'cliente/cliente_vacante_reclutado.html', contexto)

@login_required
@validar_permisos('acceso_admin')
def cliente_vacante_entrevista(request, pk):
    vacante = get_object_or_404(Cli052Vacante, pk=pk)
    cliente = get_object_or_404(Cli051Cliente, pk=vacante.cliente_id_051.id)

    contadores_reclutados = Cli056AplicacionVacante.calcular_cantidades_y_porcentajes(pk)
    
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
        'contadores_reclutados' : contadores_reclutados,
        
    }
    return render(request, 'cliente/cliente_vacante_entrevista.html', contexto)

@login_required
@validar_permisos('acceso_admin')
def cliente_vacante_editar(request, pk):
    vacante = get_object_or_404(Cli052Vacante, pk=pk)
    cliente = get_object_or_404(Cli051Cliente, pk=vacante.cliente_id_051.id)

    contadores_reclutados = Cli056AplicacionVacante.calcular_cantidades_y_porcentajes(pk)

    # Define los datos iniciales que quieres pasar al formulario
    initial_data = {
        'titulo': vacante.titulo,
        'numero_posiciones': vacante.numero_posiciones,
        'profesion_estudio_id_055': vacante.profesion_estudio_id_055.nombre,
        'experiencia_requerida': vacante.experiencia_requerida,
        'soft_skills_id_053': ','.join([skill.nombre for skill in vacante.soft_skills_id_053.all()]),
        'hard_skills_id_054': ','.join([skill.nombre for skill in vacante.hard_skills_id_054.all()]),
        'funciones_responsabilidades': ', '.join([funcion['value'] for funcion in json.loads(vacante.funciones_responsabilidades)]),

        # 'funciones_responsabilidades': vacante.funciones_responsabilidades,
        'ciudad': vacante.ciudad.id if vacante.ciudad else '',
        'salario': vacante.salario,
        'usuario_asignado': vacante.usuario_asignado.id if vacante.usuario_asignado else '',
    }

    print(initial_data)
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

            usuario_asignado = UsuarioBase.objects.get(id=form_vacante.cleaned_data['usuario_asignado'])
            vacante.usuario_asignado = usuario_asignado

            estado_id = Cat001Estado.objects.get(id=1)
            
            
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
        'contadores_reclutados': contadores_reclutados,
        
    }
    return render(request, 'cliente/cliente_vacante_editar.html', contexto)

@login_required
@validar_permisos('acceso_admin')
def cliente_vacante_emparejamiento_vacante(request, pk):

    candidatos = Can101Candidato.objects.filter(estado_id_001=1)
    vacante = get_object_or_404(Cli052Vacante, pk=pk)
    cliente = get_object_or_404(Cli051Cliente, pk=vacante.cliente_id_051.id)

    matches = []
    for candidato in candidatos:
        porcentaje_match = calcular_match(candidato, vacante)
        # if porcentaje_match >= 60:
        #     matches.append({'candidato': candidato, 'porcentaje': porcentaje_match})
        matches.append({'candidato': candidato, 'porcentaje': porcentaje_match})
    contexto = {
        'cliente' : cliente,
        'vacante' : vacante,
        'matches': matches
    }

    return render(request, 'cliente/cliente_vacante_emparejamiento.html', contexto)

@login_required
@validar_permisos('acceso_admin')
def reclutados_todos(request):
    contexto = {
        'asignacion_vacante' : consulta_asignacion_vacante()
    }
    return render(request, 'cliente/cliente_vacante_reclutado_todos.html', contexto)

# Ver todas las vacantes activas
@login_required
@validar_permisos('acceso_admin')
def vacantes_todos(request):
    #url actual
    url_actual = f"{request.scheme}://{request.get_host()}"

    #estado_general_vacante
    estado = Cat001Estado.objects.get(id=1)
    
    form_errors = False

    vacantes = consulta_vacantes_todas() 

    if request.method == 'POST':
        form = VacanteAdicionalForms(request.POST)
        if form.is_valid():
            #datos formulario
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
            cliente = Cli051Cliente.objects.get(id=form.cleaned_data['cliente_id_051'])
            usuario_asignado = UsuarioBase.objects.get(id=form.cleaned_data['usuario_asignado'])

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
                usuario_asignado = usuario_asignado,
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

            # Envio del correo electronico de confirmación de la creación de la vacante.
            contexto_mail = {
                'Cliente': cliente.razon_social.capitalize(),
                'id': vacante_creada.id,
                'vacante': vacante_creada.titulo.capitalize(),
                'fecha_creacion': vacante_creada.fecha_creacion,
                'vacante_cantidad': vacante_creada.numero_posiciones,
                'url': url_actual,
            }
            
            # correos a enviar
            correo_cliente = cliente.email
            correo_analista = usuario_asignado.email if usuario_asignado else None

            lista_correos = [
                correo_cliente,
                correo_analista
            ]

            enviar_correo('creacion_vacante', contexto_mail, 'Creación de Vacante ATS', lista_correos, correo_remitente=None)

            messages.success(request, 'El registro de la vacante ha sido creado con éxito.')
            return redirect('clientes:vacantes_cliente_todas')
        else:
            form_errors = True
            messages.error(request, form.errors)    
    else:
        form = VacanteAdicionalForms()

    return render(request, 'vacante/listado_vacantes_todos.html',
        { 
            'vacantes': vacantes,
            'form_errors': form_errors,
            'form': form,
        })


def vacante_candidato_emparejamiento(request):

    vacantes = {}
    return render(request, 'vacante/vacante_candidato_emparejamiento.html',
        { 
            'vacantes': vacantes,
        })