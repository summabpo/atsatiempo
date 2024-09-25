from django.shortcuts import render, redirect
from applications.usuarios.models import UsuarioBase
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.cliente.models import Cli051Cliente
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

def usuario_interno(request):
    # Verificar si el cliente_id está en la sesión
    user_id = request.session.get('_auth_user_id')
    cliente_id = request.session.get('cliente_id')
    
    # Obtener un solo objeto cliente o lanzar un 404 si no existe
    cliente = get_object_or_404(Cli051Cliente, id=cliente_id)

    usuarios_internos = UsuarioBase.objects.filter(group__in=[2, 3], cliente_id_051=cliente)

    contexto = {
        'usuarios_internos': usuarios_internos,
    }

    return render(request, 'cliente/listado_usuarios_internos.html', contexto)



