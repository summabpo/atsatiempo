"""
Vistas de administración de usuarios.
Acceso solo para administrador (grupo_id=1).
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from applications.usuarios.decorators import validar_permisos
from applications.usuarios.models import UsuarioBase


def _get_usuarios_queryset():
    """Queryset base para listado de usuarios."""
    return (
        UsuarioBase.objects
        .select_related('group', 'candidato_id_101', 'candidato_id_101__ciudad_id_004', 'cliente_id_051')
        .order_by('-date_joined')
    )


@login_required
@validar_permisos('acceso_admin')
def usuarios_listar(request):
    """Listado de todos los usuarios del sistema."""
    usuarios = _get_usuarios_queryset()
    return render(request, 'admin/users/admin_user/users_list.html', {'usuarios': usuarios})


@login_required
@validar_permisos('acceso_admin')
def usuarios_candidatos(request):
    """Listado de usuarios con grupo Candidato (group_id=2) que tengan candidato vinculado."""
    usuarios = _get_usuarios_queryset().filter(group_id=2, candidato_id_101__isnull=False)
    return render(request, 'admin/users/admin_user/users_list.html', {
        'usuarios': usuarios,
        'titulo_filtro': 'Candidatos',
        'ocultar_tipo_usuario': True,
    })


@login_required
@validar_permisos('acceso_admin')
def usuarios_internos(request):
    """Listado de usuarios internos (todos excepto grupo Candidato)."""
    usuarios = _get_usuarios_queryset().exclude(group_id=2)
    return render(request, 'admin/users/admin_user/users_list.html', {
        'usuarios': usuarios,
        'titulo_filtro': 'Usuarios internos',
        'mostrar_cliente': True,
    })
