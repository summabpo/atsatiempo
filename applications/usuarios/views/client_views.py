import traceback
from django.shortcuts import render, redirect, get_object_or_404
from applications.usuarios.models import UsuarioBase, Grupo
from applications.cliente.models import Cli051Cliente
from applications.usuarios.forms.CreacionUsuariosForm import CrearUsuarioInternoForm, CrearUsuarioInternoAtsForm, EditUsuarioInternoForm
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

    cliente_type = Cli051Cliente.objects.get(id=cliente_id).tipo_cliente

    if cliente_type == '1':
        group_list = [3, 4, 5]
    elif cliente_type == '2':
        group_list = [5, 7]
    elif cliente_type == '3':
        group_list = [3, 4]
        
    else:
        group_list = [3, 4, 5]

    #Obtener usuarios internos 
    usuarios_internos = UsuarioBase.objects.filter(group__in=group_list, is_active=True, cliente_id_051=cliente_id)

    form = CrearUsuarioInternoForm(tipo_cliente=cliente_type)

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
        form = CrearUsuarioInternoForm(tipo_cliente=cliente_type)

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
    usuarios_detalle = UsuarioBase.objects.get(id=pk, is_active=True, cliente_id_051=cliente_id)

    cliente_type = Cli051Cliente.objects.get(id=cliente_id).tipo_cliente

    initial_data = {
        'primer_nombre': usuarios_detalle.primer_nombre,
        'segundo_nombre': usuarios_detalle.segundo_nombre,
        'primer_apellido': usuarios_detalle.primer_apellido,
        'segundo_apellido': usuarios_detalle.segundo_apellido,
        'correo': usuarios_detalle.email,
        'rol': usuarios_detalle.group.id,
        'imagen_perfil': usuarios_detalle.imagen_perfil,
    }

    if request.method == 'POST':
        form = EditUsuarioInternoForm(request.POST, request.FILES, usuario=usuarios_detalle, initial=initial_data, tipo_cliente=cliente_type)
        if form.is_valid():
            primer_nombre = form.cleaned_data['primer_nombre']
            segundo_nombre = form.cleaned_data['segundo_nombre']
            primer_apellido = form.cleaned_data['primer_apellido']
            segundo_apellido = form.cleaned_data['segundo_apellido']
            correo = form.cleaned_data['correo']
            rol = form.cleaned_data['rol']
            imagen_perfil = form.cleaned_data['imagen_perfil']
            password = form.cleaned_data['password']
            password_confirm = form.cleaned_data['password_confirm']

            grupo = get_object_or_404(Grupo, id=rol)

            # Actualizar el usuario
            usuarios_detalle.primer_nombre = primer_nombre.capitalize()
            usuarios_detalle.segundo_nombre = segundo_nombre.capitalize()
            usuarios_detalle.primer_apellido = primer_apellido.capitalize()
            usuarios_detalle.segundo_apellido = segundo_apellido.capitalize()
            usuarios_detalle.email = correo
            usuarios_detalle.group = grupo
            if imagen_perfil:
                usuarios_detalle.imagen_perfil = imagen_perfil

            if password:
                is_current_user = usuarios_detalle.id == request.user.id
    
                if is_current_user:
                    # Para el usuario actual, usar set_password pero mantener la sesión
                    usuarios_detalle.set_password(password)
                    messages.error(request, 'Tu contraseña ha sido actualizada. Te recomendamos cerrar sesión y volver a iniciar.')
                    print("Contraseña actualizada")
                else:
                    usuarios_detalle.password = make_password(password)
                
                # usuarios_detalle.password = make_password(password)
            
            usuarios_detalle.save()

            messages.success(request, 'Usuario interno actualizado exitosamente.')
            return redirect('accesses:users_client_detail', pk=usuarios_detalle.id)
        else:
            print(form.errors)
            messages.error(request, 'Error al actualizar el usuario interno.')
    else:
        form = EditUsuarioInternoForm(initial=initial_data, tipo_cliente=cliente_type)

    print(usuarios_detalle)

    context = {
        'usuarios_detalle': usuarios_detalle,
        'form': form,
    }

    return render(request, 'admin/users/client_user/group_work_detail.html', context)