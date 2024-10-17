from django.shortcuts import render, redirect
import json
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from applications.usuarios.decorators  import validar_permisos


#model
from applications.vacante.models import Cli052Vacante, Cli055ProfesionEstudio, Cli053SoftSkill, Cli052VacanteSoftSkillsId053, Cli054HardSkill, Cli052VacanteHardSkillsId054, Cli056AplicacionVacante, Cli057AsignacionEntrevista
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.usuarios.models import Permiso
from ..models import Cli051Cliente
#form
from applications.vacante.forms.VacanteForms import VacanteForm
from ..forms.ClienteForms import ClienteForm


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

# Mostrar detalle de cada cliente
@login_required
@validar_permisos(*Permiso.obtener_nombres())
def cliente_detalle(request, pk):

    cliente = get_object_or_404(Cli051Cliente, pk=pk)

    contexto = {
        'cliente' : cliente,
    }

    return render(request, 'cliente/cliente_detalle.html', contexto)

# Mostrar detalle de cada cliente
@login_required
@validar_permisos(*Permiso.obtener_nombres())
def cliente_vacante(request, pk):

    vacante = Cli052Vacante.objects.filter(cliente_id_051= pk)

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
    
    return render(request, 'cliente/cliente_vacante_reclutado.html', contexto)


# Create your views here.
@login_required
#@validar_permisos(*Permiso.obtener_nombres())
def cliente_crear(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES)
        if form.is_valid():
            ClienteForm.logo = form.cleaned_data['logo']
            form.save()
            return redirect('clientes:cliente_listar')  # Cambia a la vista deseada después de guardar
    else:
        form = ClienteForm()
    
    return render(request, 'cliente/form_cliente.html', {'form': form})


global_id = None 

@login_required
#@validar_permisos(*Permiso.obtener_nombres())
def obtener_cliente_view(request):
    global global_id

    if request.method == 'GET':
        id_cliente = request.GET.get('dato')
        solicitud_cliente= get_object_or_404(Cli051Cliente, pk=id_cliente)

        global_id = solicitud_cliente.id

        estado_id = Cat001Estado.objects.get(nombre=solicitud_cliente.estado_id_001)
        ciudad_id = Cat004Ciudad.objects.get(nombre=solicitud_cliente.ciudad_id_004)

        response_data = {
            'data': {
                'id': solicitud_cliente.id,
                'estado_id_001': estado_id.id,
                'nit': solicitud_cliente.nit,
                'razon_social': solicitud_cliente.razon_social,
                'ciudad_id_004': ciudad_id.id,
                'email': solicitud_cliente.email,
                'contacto': solicitud_cliente.contacto,
                'telefono': solicitud_cliente.telefono,
                'perfil_empresarial': solicitud_cliente.perfil_empresarial,
                'logo': solicitud_cliente.logo.url if solicitud_cliente.logo else None,
                
            }
        }       
        return JsonResponse(response_data)

    if request.method == 'POST':
        nit = None
        razon_social = None
        email = None
        contacto = None
        telefono = None
        perfil_empresarial = None
        logo = None
        ciudad_id_004 = None

        nit = request.POST.get('nit')
        razon_social = request.POST.get('razon_social')
        email = request.POST.get('email')
        contacto = request.POST.get('contacto')
        telefono = request.POST.get('telefono')
        perfil_empresarial = request.POST.get('perfil_empresarial')
        logo = request.POST.get('logo')
        ciudad_id_004 = request.POST.get('ciudad_id_004')

        cliente_id = global_id
        
        cliente_modificar = get_object_or_404(Cli051Cliente, pk=cliente_id)
        
        # Obtener la instancia del modelo Cat004Ciudad
        ciudad = get_object_or_404(Cat004Ciudad, pk=ciudad_id_004)

        cliente_modificar.estado_id_001 = Cat001Estado.objects.get(id=1)
        cliente_modificar.nit = nit
        cliente_modificar.razon_social = razon_social
        cliente_modificar.email = email
        cliente_modificar.contacto = contacto
        cliente_modificar.telefono = telefono
        cliente_modificar.perfil_empresarial = perfil_empresarial
        cliente_modificar.logo = logo
        cliente_modificar.ciudad_id_004 = ciudad

        cliente_modificar.save()

        messages.success(request, 'Se ha realizado la actualización del registro éxito.')
        return redirect('clientes:cliente_listar')

    return JsonResponse({'error': 'Método no permitido'}, status=405)