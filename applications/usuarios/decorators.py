from functools import wraps
from django.core.exceptions import PermissionDenied
from .models import Grupo, Permiso, GrupoPermiso, UsuarioBase
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout

def validar_permisos(*nombres_permisos):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                print('------1------')
                #raise PermissionDenied
                messages.error(request, "Debes iniciar sesión para acceder a esta página.")
                list(messages.get_messages(request))  # Forzar almacenamiento del mensaje
                return redirect('accesses:login')
            
            user = request.user

            #trae el nombre del usuario
            usuario = UsuarioBase.objects.get(username=user)

            #trae el nombre del grupo
            grupos_usuario = Grupo.objects.filter(id=usuario.group.id, activate=True)

            permisos = Permiso.objects.filter(nombre__in=nombres_permisos)
            if not permisos:
                print('------2------')
                raise ValueError(f"Ninguno de los permisos especificados existe: {nombres_permisos}")
            
            permisos_usuario = GrupoPermiso.objects.filter(
                grupo__in=grupos_usuario,
                permiso__in=permisos
            ).values_list('permiso__nombre', flat=True)

            # Guardamos los permisos en request
            request.permisos_usuario = list(permisos_usuario)

            if permisos_usuario:
                print('------3------')
                return view_func(request, *args, **kwargs)
            else:
                print('------4------')
                # logout(request)
                messages.error(request, 'No Cuenta con permisos para acceder a este modulo.')
                return redirect('accesses:acceso_denegado')
                # raise PermissionDenied

        return _wrapped_view
    return decorator