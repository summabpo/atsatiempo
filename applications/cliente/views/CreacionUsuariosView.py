from django.shortcuts import render, redirect
from applications.usuarios.models import UsuarioBase, Grupo
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.cliente.models import Cli051Cliente
from applications.cliente.forms.CreacionUsuariosForm import CrearUsuarioInternoForm
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
import random
import string
from applications.common.views.EnvioCorreo import enviar_correo, generate_token

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))

def usuario_interno(request):
    # Verificar si el cliente_id está en la sesión
    user_id = request.session.get('_auth_user_id')
    cliente_id = request.session.get('cliente_id')
    
    # Obtener un solo objeto cliente o lanzar un 404 si no existe
    cliente = get_object_or_404(Cli051Cliente, id=cliente_id)

    usuarios_internos = UsuarioBase.objects.filter(group__in=[4, 5], cliente_id_051=cliente)

    form_errores = False

    if request.method == 'POST':
        form_creacion = CrearUsuarioInternoForm(request.POST)
        if form_creacion.is_valid():
            #campos del form
            primer_nombre = form_creacion.cleaned_data['primer_nombre']
            segundo_nombre = form_creacion.cleaned_data['segundo_nombre']
            primer_apellido = form_creacion.cleaned_data['primer_apellido']
            segundo_apellido = form_creacion.cleaned_data['segundo_apellido']
            correo = form_creacion.cleaned_data['correo']
            rol = form_creacion.cleaned_data['rol']

            grupo = get_object_or_404(Grupo, id=rol)

            passwordoriginal = generate_random_password()
            password = make_password(passwordoriginal)

            user = UsuarioBase.objects.create_user(
                username= correo, 
                email= correo, 
                primer_nombre = primer_nombre.capitalize(), 
                segundo_nombre = segundo_nombre.capitalize(), 
                primer_apellido = primer_apellido.capitalize(), 
                segundo_apellido = segundo_apellido.capitalize(),  
                password=password,
                cliente_id_051 = cliente,
                is_verificado = True,
                group=grupo,
            )

            # Envio del correo electronico de confirmación del usuario y contraseña
            contexto_mail = {
                'name': primer_nombre.capitalize(),
                'last_name': primer_apellido.capitalize(),
                'user': correo,
                'email': correo,
                'password': passwordoriginal,
            }

            # Envio de correo
            enviar_correo('creacion_usuario_cliente', contexto_mail, 'Creación de Usuario Interno ATS', [correo], correo_remitente=None)

            frase_aleatoria = 'Se ha enviado un correo electronico para su validar el mismo.'
            messages.success(request, frase_aleatoria)
            return redirect('clientes:usuarios_internos_listar')  
        else:
            form_errores = True
            messages.error(request, 'Error al crear usuario interno')

    else:
        form_creacion = CrearUsuarioInternoForm()
    
    contexto = {
        'usuarios_internos': usuarios_internos,
        'form_creacion': form_creacion,
        'form_errores': form_errores,
    }

    return render(request, 'cliente/listado_usuarios_internos.html', contexto)



