from django.shortcuts import render, redirect
from ..models import Cli051Cliente
from applications.common.models import Cat001Estado, Cat004Ciudad
from ..forms.ClienteForms import ClienteForm
from django.views.generic import (
    ListView
)
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from applications.usuarios.models import Permiso
from django.contrib.auth.decorators import login_required
from applications.usuarios.decorators  import validar_permisos

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



@login_required
#@validar_permisos(*Permiso.obtener_nombres())
def mostrar_clientes(request):
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

    
    return render(request, 'cliente/listado_clientes.html', {
        'clientes': clientes,
        'form': form,
        'form_errors': form_errors,
        })

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