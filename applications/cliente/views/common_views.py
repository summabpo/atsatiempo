import json
import random
import string
from django.conf import traceback
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError

# Models
from applications.common.views.EnvioCorreo import enviar_correo
from applications.usuarios.models import UsuarioBase, Grupo
from applications.cliente.models import Cli051Cliente

# Forms
from applications.usuarios.forms.UsuarioModalForm import UsuarioModalForm

# Decorators
from applications.usuarios.decorators import validar_permisos

def generate_random_password(length=12):
    """Genera una contraseña aleatoria para nuevos usuarios."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

@login_required
@validar_permisos('acceso_admin', 'acceso_cliente')
@csrf_exempt
@require_http_methods(["POST"])
def crear_usuario_modal(request):
    """
    API para crear un nuevo usuario a través de modal.
    Método: POST
    """
    try:
        # Obtener el cliente_id de la sesión o del request
        cliente_id = request.session.get('cliente_id') or request.POST.get('cliente_id')
        
        if not cliente_id:
            return JsonResponse({
                'success': False,
                'message': 'ID de cliente no encontrado'
            }, status=400)

        # Verificar que el cliente existe
        cliente = get_object_or_404(Cli051Cliente, id=cliente_id)
        
        # Crear formulario con datos del request
        form = UsuarioModalForm(request.POST, request.FILES, cliente_id=cliente_id)
        
        if form.is_valid():
            # Generar contraseña aleatoria
            password = generate_random_password()
            
            # Crear el usuario
            usuario = UsuarioBase.objects.create_user(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                primer_nombre=form.cleaned_data['primer_nombre'].capitalize(),
                segundo_nombre=form.cleaned_data['segundo_nombre'].capitalize() if form.cleaned_data['segundo_nombre'] else '',
                primer_apellido=form.cleaned_data['primer_apellido'].capitalize(),
                segundo_apellido=form.cleaned_data['segundo_apellido'].capitalize() if form.cleaned_data['segundo_apellido'] else '',
                telefono=form.cleaned_data['telefono'] or '',
                password=password,
                cliente_id_051=cliente,
                group=form.cleaned_data['group'],
                is_verificado=True,
                is_active=True
            )
            
            # Manejar imagen de perfil si se proporciona
            if form.cleaned_data.get('imagen_perfil'):
                usuario.imagen_perfil = form.cleaned_data['imagen_perfil']
                usuario.save()
            
            # Preparar datos del usuario para la respuesta
            usuario_data = {
                'id': usuario.id,
                'primer_nombre': usuario.primer_nombre,
                'segundo_nombre': usuario.segundo_nombre or '',
                'primer_apellido': usuario.primer_apellido,
                'segundo_apellido': usuario.segundo_apellido or '',
                'email': usuario.email,
                'telefono': usuario.telefono or '',
                'group_name': usuario.group.name if usuario.group else '',
                'is_active': usuario.is_active,
                'password': password  # Solo para mostrar al usuario
            }

            # Enviar correo de bienvenida con los datos del usuario recién registrado
            contexto_mail = {
                'name': usuario.primer_nombre,
                'last_name': usuario.primer_apellido,
                'user': usuario.email,
                'email': usuario.email,
                'password': password,
                'url': request.build_absolute_uri('/'),
            }

            try:
                enviar_correo(
                    'creacion_usuario_cliente',
                    contexto_mail,
                    'Creación de Usuario Interno ATS',
                    [usuario.email],
                    correo_remitente=None
                )
                print(f"Resultado del envío: {'Éxito' if enviar_correo else 'Falló'}")
            except Exception as e:
                print(f"Error al enviar correo: {e}")
                traceback.print_exc()
            
            return JsonResponse({
                'success': True,
                'message': f'Usuario {usuario.primer_nombre} {usuario.primer_apellido} creado exitosamente',
                'usuario': usuario_data
            })
        else:
            # Obtener errores del formulario
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = [str(error) for error in field_errors]
            
            return JsonResponse({
                'success': False,
                'message': 'Errores en el formulario',
                'errors': errors
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error interno del servidor: {str(e)}'
        }, status=500)

@login_required
@validar_permisos('acceso_admin', 'acceso_cliente')
@require_http_methods(["GET"])
def obtener_usuario_modal(request, pk):
    """
    API para obtener datos de un usuario para editar.
    Método: GET
    """
    try:
        usuario = get_object_or_404(UsuarioBase, id=pk)
        
        # Preparar datos del usuario
        usuario_data = {
            'id': usuario.id,
            'primer_nombre': usuario.primer_nombre,
            'segundo_nombre': usuario.segundo_nombre or '',
            'primer_apellido': usuario.primer_apellido,
            'segundo_apellido': usuario.segundo_apellido or '',
            'email': usuario.email,
            'telefono': usuario.telefono or '',
            'group_id': usuario.group.id if usuario.group else None,
            'group_name': usuario.group.name if usuario.group else '',
            'imagen_perfil_url': usuario.imagen_perfil.url if usuario.imagen_perfil else None,
            'is_active': usuario.is_active
        }
        
        return JsonResponse({
            'success': True,
            'usuario': usuario_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener usuario: {str(e)}'
        }, status=500)

@login_required
@validar_permisos('acceso_admin', 'acceso_cliente')
@csrf_exempt
@require_http_methods(["POST"])
def actualizar_usuario_modal(request, pk):
    """
    API para actualizar un usuario existente.
    Método: POST
    """
    try:
        usuario = get_object_or_404(UsuarioBase, id=pk)
        
        # Crear formulario con datos del request y usuario existente
        form = UsuarioModalForm(request.POST, request.FILES, usuario=usuario)
        
        if form.is_valid():
            # Actualizar campos del usuario
            usuario.primer_nombre = form.cleaned_data['primer_nombre'].capitalize()
            usuario.segundo_nombre = form.cleaned_data['segundo_nombre'].capitalize() if form.cleaned_data['segundo_nombre'] else ''
            usuario.primer_apellido = form.cleaned_data['primer_apellido'].capitalize()
            usuario.segundo_apellido = form.cleaned_data['segundo_apellido'].capitalize() if form.cleaned_data['segundo_apellido'] else ''
            usuario.email = form.cleaned_data['email']
            usuario.username = form.cleaned_data['email']  # Actualizar también username
            usuario.telefono = form.cleaned_data['telefono'] or ''
            usuario.group = form.cleaned_data['group']
            
            # Manejar imagen de perfil si se proporciona
            if form.cleaned_data.get('imagen_perfil'):
                usuario.imagen_perfil = form.cleaned_data['imagen_perfil']
            
            usuario.save()
            
            # Preparar datos del usuario actualizado para la respuesta
            usuario_data = {
                'id': usuario.id,
                'primer_nombre': usuario.primer_nombre,
                'segundo_nombre': usuario.segundo_nombre or '',
                'primer_apellido': usuario.primer_apellido,
                'segundo_apellido': usuario.segundo_apellido or '',
                'email': usuario.email,
                'telefono': usuario.telefono or '',
                'group_name': usuario.group.name if usuario.group else '',
                'is_active': usuario.is_active
            }
            
            return JsonResponse({
                'success': True,
                'message': f'Usuario {usuario.primer_nombre} {usuario.primer_apellido} actualizado exitosamente',
                'usuario': usuario_data
            })
        else:
            # Obtener errores del formulario
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = [str(error) for error in field_errors]
            
            return JsonResponse({
                'success': False,
                'message': 'Errores en el formulario',
                'errors': errors
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error interno del servidor: {str(e)}'
        }, status=500)

@login_required
@validar_permisos('acceso_admin', 'acceso_cliente')
@csrf_exempt
@require_http_methods(["POST"])
def cambiar_estado_usuario_modal(request, pk):
    """
    API para cambiar el estado activo/inactivo de un usuario.
    Método: POST
    """
    try:
        usuario = get_object_or_404(UsuarioBase, id=pk)
        
        # Cambiar el estado del usuario
        nuevo_estado = not usuario.is_active
        usuario.is_active = nuevo_estado
        usuario.save()
        
        # Preparar mensaje según el nuevo estado
        if nuevo_estado:
            mensaje = f'Usuario {usuario.primer_nombre} {usuario.primer_apellido} activado exitosamente'
        else:
            mensaje = f'Usuario {usuario.primer_nombre} {usuario.primer_apellido} desactivado exitosamente'
        
        # Preparar datos del usuario para la respuesta
        usuario_data = {
            'id': usuario.id,
            'primer_nombre': usuario.primer_nombre,
            'segundo_nombre': usuario.segundo_nombre or '',
            'primer_apellido': usuario.primer_apellido,
            'segundo_apellido': usuario.segundo_apellido or '',
            'email': usuario.email,
            'telefono': usuario.telefono or '',
            'group_name': usuario.group.name if usuario.group else '',
            'is_active': usuario.is_active
        }
        
        return JsonResponse({
            'success': True,
            'message': mensaje,
            'usuario': usuario_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al cambiar estado del usuario: {str(e)}'
        }, status=500)

@login_required
@validar_permisos('acceso_admin', 'acceso_cliente')
@require_http_methods(["GET"])
def obtener_grupos_activos(request):
    """
    API para obtener la lista de grupos activos.
    Método: GET
    """
    try:
        grupos = Grupo.objects.filter(activate=True).exclude(id__in=[1, 6]).values('id', 'name', 'description')
        
        return JsonResponse({
            'success': True,
            'grupos': list(grupos)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener grupos: {str(e)}'
        }, status=500)
