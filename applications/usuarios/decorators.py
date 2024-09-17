from functools import wraps
from django.core.exceptions import PermissionDenied
from .models import Grupo, Permiso, GrupoPermiso, UsuarioBase

def validar_permisos(*nombres_permisos):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied
            
            user = request.user

            #tra el nombre del usuario
            usuario = UsuarioBase.objects.get(username=user)
            
            #trae el nombre del grupo
            grupos_usuario = Grupo.objects.filter(id=usuario.group.id, activate=True)
            
            permisos = Permiso.objects.filter(nombre__in=nombres_permisos)
            if not permisos:
                raise ValueError(f"Ninguno de los permisos especificados existe: {nombres_permisos}")
            
            tiene_algun_permiso = GrupoPermiso.objects.filter(
                grupo__in=grupos_usuario,
                permiso__in=permisos
            ).exists()
            
            if tiene_algun_permiso:
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied
        
        return _wrapped_view
    return decorator