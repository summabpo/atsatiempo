import traceback
from django.shortcuts import render, redirect, get_object_or_404
from applications.usuarios.models import UsuarioBase, Grupo
from applications.cliente.models import Cli051Cliente
from applications.usuarios.forms.CreacionUsuariosForm import CrearUsuarioInternoForm, CrearUsuarioInternoAtsForm
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
    usuarios_internos = UsuarioBase.objects.filter(group__in=[4,5], is_active=True, cliente_id_051=cliente_id)

    form = CrearUsuarioInternoForm()

    if request.method == 'POST':
        form = CrearUsuarioInternoForm(request.POST, request.FILES)
        if form.is_valid():
            primer_nombre = form.cleaned_data['primer_nombre']
            segundo_nombre = form.cleaned_data['segundo_nombre']
            primer_apellido = form.cleaned_data['primer_apellido']
            segundo_apellido = form.cleaned_data['segundo_apellido']
            correo = form.cleaned_data['correo']
            rol = form.cleaned_data['rol']
            imagen_perfil = form.cleaned_data['imagen_perfil']

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
                imagen_perfil=imagen_perfil,
                cliente_id_051_id=cliente_id,
            )

            contexto_mail = {
                'name': primer_nombre.capitalize(),
                'last_name': primer_apellido.capitalize(),
                'user': correo,
                'email': correo,
                'password': passwordoriginal,
                'url': url_actual,
            }

            try:
                enviar_correo('creacion_usuario_cliente', contexto_mail, 'Creación de Usuario Interno ATS', [correo], correo_remitente=None)
                print(f"Resultado del envío: {'Éxito' if enviar_correo else 'Falló'}")
            except Exception as e:
                print(f"Error al enviar correo: {e}")
                traceback.print_exc()

            messages.success(request, 'Usuario interno creado exitosamente.')
            return redirect('accesses:users_client')
        else:
            print(form.errors)
            messages.error(request, 'Error al crear el usuario interno.')
    else:
        form = CrearUsuarioInternoForm()

    context = {
        'usuarios_internos': usuarios_internos,
        'form': form,
    }

    return render(request, 'admin/users/client_user/group_work_list.html', context)

@login_required 
@validar_permisos('acceso_cliente')
def detail_internal_client(request, pk):
    url_actual = f"{request.scheme}://{request.get_host()}"
    # Verificar si el cliente_id está en la sesión
    cliente_id = request.session.get('cliente_id')

    #Obtener usuarios internos 
    usuarios_detalle = UsuarioBase.objects.get(id=pk, group__in=[4,5], is_active=True, cliente_id_051=cliente_id)

    print(usuarios_detalle)

    context = {
        'usuarios_detalle': usuarios_detalle
    }

    return render(request, 'admin/users/client_user/group_work_detail.html', context)