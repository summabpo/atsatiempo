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
@validar_permisos('acceso_admin')
def crear_usuario_interno(request):
    url_actual = f"{request.scheme}://{request.get_host()}"

    usuarios_internos = UsuarioBase.objects.filter(group__in=[6], is_active=True)

    form_errores = False

    if request.method == 'POST':
        form_creacion = CrearUsuarioInternoAtsForm(request.POST)
        if form_creacion.is_valid():
            primer_nombre = form_creacion.cleaned_data['primer_nombre']
            segundo_nombre = form_creacion.cleaned_data['segundo_nombre']
            primer_apellido = form_creacion.cleaned_data['primer_apellido']
            segundo_apellido = form_creacion.cleaned_data['segundo_apellido']
            correo = form_creacion.cleaned_data['correo']
            rol = form_creacion.cleaned_data['rol']

            grupo = get_object_or_404(Grupo, id=rol)

            passwordoriginal = generate_random_password()

            user = UsuarioBase.objects.create_user(
                username=correo,
                email=correo,
                primer_nombre=primer_nombre.capitalize(),
                segundo_nombre=segundo_nombre.capitalize(),
                primer_apellido=primer_apellido.capitalize(),
                segundo_apellido=segundo_apellido.capitalize(),
                password=passwordoriginal,
                is_verificado=True,
                group=grupo,
            )

            contexto_mail = {
                'name': primer_nombre.capitalize(),
                'last_name': primer_apellido.capitalize(),
                'user': correo,
                'email': correo,
                'password': passwordoriginal,
                'url': url_actual,
            }

            enviar_correo('creacion_usuario_cliente', contexto_mail, 'Creación de Usuario Interno ATS', [correo], correo_remitente=None)

            frase_aleatoria = 'Se ha enviado un correo electronico para su validar el mismo.'
            messages.success(request, frase_aleatoria)
            return redirect('accesses:listado_persona_interno')
        else:
            form_errores = True
            messages.error(request, 'Error al crear usuario interno')
    else:
        form_creacion = CrearUsuarioInternoAtsForm()

    contexto = {
        'usuarios_internos': usuarios_internos,
        'form_creacion': form_creacion,
        'form_errores': form_errores,
    }

    return render(request, 'authentication/listado_usuarios_internos_ats.html', contexto)

@login_required
@validar_permisos('acceso_admin')
def ver_detalle_usuario_interno(request, id):
    usuario_interno = get_object_or_404(UsuarioBase, id=id)

    contexto = {
        'usuario_interno': usuario_interno,
    }

    return render(request, 'authentication/ver_usuario_interno.html', contexto)