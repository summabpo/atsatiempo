from django.shortcuts import render, redirect, get_object_or_404
from applications.usuarios.models import UsuarioBase, Grupo
from applications.cliente.models import Cli051Cliente
from applications.cliente.forms.CreacionUsuariosForm import CrearUsuarioInternoForm, CrearUsuarioInternoAtsForm
from django.contrib import messages
from django.contrib.auth.hashers import make_password
import random
import string
from applications.common.views.EnvioCorreo import enviar_correo
from django.contrib.auth.decorators import login_required
from applications.usuarios.decorators import validar_permisos
from applications.usuarios.models import Permiso

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

@login_required 
@validar_permisos('acceso_cliente')
def create_internal_client(request):
    url_actual = f"{request.scheme}://{request.get_host()}"
    # Verificar si el cliente_id está en la sesión
    cliente_id = request.session.get('cliente_id')

    #Obtener usuarios internos 
    usuarios_internos = UsuarioBase.objects.filter(group__in=[6], is_active=True, cliente_id_051=cliente_id)

    context = {
        'usuarios_internos': usuarios_internos,
    }

    return render(request, 'admin/users/client_user/group_work_list.html', context)

@login_required 
@validar_permisos('acceso_cliente')
def detail_internal_client(request, pk):
    url_actual = f"{request.scheme}://{request.get_host()}"
    # Verificar si el cliente_id está en la sesión
    cliente_id = request.session.get('cliente_id')

    #Obtener usuarios internos 
    usuarios_internos = UsuarioBase.objects.filter(id=pk, group__in=[6], is_active=True, cliente_id_051=cliente_id)

    context = {
        'usuarios_internos': usuarios_internos,
    }

    return render(request, 'admin/users/client_user/group_work_list.html', context)