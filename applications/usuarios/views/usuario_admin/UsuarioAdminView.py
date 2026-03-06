"""
Vistas de administración de usuarios.
Acceso solo para administrador (grupo_id=1).
"""
from django.shortcuts import render, get_object_or_404

from applications.usuarios.decorators import validar_permisos
from applications.usuarios.models import UsuarioBase
from applications.candidato.models import Can101Candidato, Can102Experiencia, Can103Educacion
from applications.reclutado.models import Cli056AplicacionVacante
from django.contrib.auth.decorators import login_required


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


@login_required
@validar_permisos('acceso_admin')
def usuario_candidato_detalle(request, pk):
    """Dashboard del candidato: vacantes aplicadas e información en solo lectura."""
    candidato = get_object_or_404(
        Can101Candidato.objects.select_related('ciudad_id_004', 'estado_id_001'),
        id=pk
    )
    usuario = UsuarioBase.objects.filter(candidato_id_101=candidato).select_related('group').first()
    aplicaciones = (
        Cli056AplicacionVacante.objects
        .filter(candidato_101=candidato)
        .select_related(
            'vacante_id_052',
            'vacante_id_052__cargo',
            'vacante_id_052__asignacion_cliente_id_064',
            'vacante_id_052__asignacion_cliente_id_064__id_cliente_asignado',
            'vacante_id_052__usuario_asignado',
            'usuario_reclutador',
        )
        .order_by('-fecha_aplicacion')
    )
    experiencias = Can102Experiencia.objects.filter(candidato_id_101=candidato).order_by('-fecha_inicial')
    educaciones = Can103Educacion.objects.filter(candidato_id_101=candidato).select_related('ciudad_id_004', 'profesion_estudio').order_by('-fecha_inicial')
    return render(request, 'admin/users/admin_user/usuario_candidato_detalle.html', {
        'candidato': candidato,
        'usuario': usuario,
        'aplicaciones': aplicaciones,
        'experiencias': experiencias,
        'educaciones': educaciones,
    })
