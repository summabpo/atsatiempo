from django.shortcuts import render, redirect # type: ignore
from django.contrib.auth import authenticate, login, logout # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from django.contrib import messages # type: ignore
from django.http import HttpResponse # type: ignore
from applications.reclutado.views.common_views import crear_registro_cli084
from applications.services.service_candidate import personal_information_calculation
from applications.services.service_vacanty import query_vacanty_all, query_vacanty_with_skills_and_details

from applications.usuarios.models import UsuarioBase, TokenAutorizacion, Grupo, Permiso
from applications.usuarios.forms.CorreoForm import CorreoForm
from applications.cliente.models import Cli051Cliente, Cli064AsignacionCliente
from applications.candidato.models import Can101Candidato
import random
from django.utils.text import capfirst # type: ignore
from applications.common.models import Cat004Ciudad, Cat001Estado
from applications.common.views.EnvioCorreo import enviar_correo, generate_token
from django.utils import timezone # type: ignore
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404 # type: ignore
from ...decorators  import validar_permisos
from django.conf import settings # type: ignore

# form
from applications.usuarios.forms.loginform import LoginForm
from applications.usuarios.forms.UserForms import SignupForm
from applications.usuarios.forms.CandidatoForm import SignupFormCandidato
from applications.usuarios.forms.EmailUserForm import EmailForm, EmailUserForm, CambioContrasenaPerfilForm

# consultas
from applications.vacante.views.consultas.AsignacionVacanteConsultaView import consulta_asignacion_vacante_candidato
from applications.common.views.PanelView import info_vacantes_pendientes, info_entrevistas_candidato


#dictado de frases aleatorias
frases_falla_login = [
    "🔐 Credenciales inválidas. Por favor, intente nuevamente."
]

frases_inicio_sesion = [
    "🌟 Esta cuenta ya está registrada. ¿Necesita recuperar su acceso?"
]

frases_error_contrasena = [
    "🔍 Revise su contraseña: los caracteres deben ser idénticos en ambos campos."
]


# pantalla principal
def principal(request):
    """Pantalla Inicial"""
    return render(request, 'admin/login/home.html') 

# pantalla de registro empresa o candidato
def registration(request):
    return render(request, 'admin/login/registration.html')

# registro cliente.
def company_registration(request):
    url_actual = f"{request.scheme}://{request.get_host()}"

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            
            email = form.cleaned_data['email']
            email2 = form.cleaned_data['email2']
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            name = form.cleaned_data['name']
            last_name = form.cleaned_data['last_name']
            nombre_completo = name+' '+last_name
            
            nit = form.cleaned_data['nit']
            companyname = form.cleaned_data['companyname']
            # city = form.cleaned_data['city']
            # companycontact = form.cleaned_data['companycontact']
            # companyemail = form.cleaned_data['companyemail']
            
            if email == email2:
                if password1 == password2:
                    if UsuarioBase.objects.filter(username=email).exists():
                        messages.error(request, '¡Oops! Parece que alguien más ya se adelantó y tomó ese correo. Prueba con otro, o tal vez es el momento de reconciliarte con tu contraseña olvidada.')
                    elif Cli051Cliente.objects.filter(nit=nit).exists():
                        messages.error(request, '¡Oops! Parece que alguien más ya se adelantó y registro este NIT.')
                    elif Cli051Cliente.objects.filter(razon_social=companyname).exists():
                        messages.error(request, '¡Oops! Parece que alguien más ya se adelantó y registro esta Razón Social.')# Usuario.objects.filter(email=email).exists():
                    else:

                        city =  Cat004Ciudad.objects.get(id = form.cleaned_data['city'] )

                        new_company = Cli051Cliente (
                            estado_id_001 = Cat001Estado.objects.get(id=1),
                            razon_social= companyname,
                            nit= nit,                        
                            ciudad_id_004= city ,
                            email= form.cleaned_data['email'],
                            contacto= nombre_completo,
                            tipo_cliente='1',
                        )

                        new_company.save()

                        grupo = Grupo.objects.get(id=3)
                        user = UsuarioBase.objects.create_user(
                            username= email, 
                            email= email, 
                            password=password1,
                            cliente_id_051 = new_company ,
                            primer_nombre = name.capitalize() ,
                            primer_apellido = last_name.capitalize(),  
                            group=grupo,
                        )

                        token_generado = generate_token(50);

                        TokenAutorizacion.objects.create(
                            user_id=user.id,
                            token=token_generado,  # Una función que genere un token único
                            fecha_expiracion=timezone.now() + timedelta(days=2),  # Si tiene fecha de expiración
                        )

                        # Crear la asignación del cliente (Cli064AsignacionCliente)
                        asignacion_cliente = Cli064AsignacionCliente(
                            id_cliente_maestro=Cli051Cliente.objects.get(id=1000),
                            id_cliente_asignado=new_company,
                            tipo_asignacion='1',
                            estado=Cat001Estado.objects.get(id=1)
                        )
                        asignacion_cliente.save()


                        # Envio del correo electronico de confirmación del usuario y contraseña
                        contexto = {
                            'name': name.capitalize(),
                            'last_name': last_name.capitalize(),
                            'user': user,
                            'email': email,
                            'password': password1,
                            'token': token_generado,
                            'url': url_actual
                        }

                        # Envia el metodo
                        if enviar_correo('bienvenida', contexto, 'Creación de Usuario ATS', [email], correo_remitente=None):
                            messages.success(request, 'Se ha enviado correo electrónico')
                            print('Se ha enviado correo electrónico')
                        else:
                            messages.error(request, 'Error al enviar el correo de bienvenida. Por favor, intenta más tarde.')
                            print('Se ha enviado correo electrónico')
                        
                        # login(request, user)
                        frase_aleatoria = 'Se ha enviado un correo electronico para su validar el mismo.'
                        messages.success(request, frase_aleatoria)
                        return redirect('accesses:login')  
                else:
                    frase_aleatoria = random.choice(frases_error_contrasena)
                    messages.error(request, frase_aleatoria)
            else:
                messages.error(request, 'La dirección de correo electrónico no coincide.')
    else:
        form = SignupForm()
    login_f = random.choice(frases_inicio_sesion)
    return render(request, 'admin/login/company_registration.html', 
                    {'form': form,
                    'login_f':login_f,
                    })

#registro candidato
def candidate_registration(request):
    url_actual = f"{request.scheme}://{request.get_host()}"

    if request.method == 'POST':
        form = SignupFormCandidato(request.POST)
        if form.is_valid():

            email = form.cleaned_data['email']
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            primer_nombre = form.cleaned_data['primer_nombre']
            segundo_nombre = form.cleaned_data['segundo_nombre']
            primer_apellido = form.cleaned_data['primer_apellido']
            segundo_apellido = form.cleaned_data['segundo_apellido']
            

            if password1 == password2:
                if UsuarioBase.objects.filter(username=email).exists():
                    messages.error(request, '¡Oops! Parece que alguien más ya se adelantó y tomó ese correo. Prueba con otro, o tal vez es el momento de reconciliarte con tu contraseña olvidada.')
                else:
                    
                    #creacion del candidato en la tabla candidato
                    candidato = Can101Candidato.objects.create(
                        email=email,
                        primer_nombre=primer_nombre,
                        segundo_nombre=segundo_nombre,
                        primer_apellido=primer_apellido,
                        segundo_apellido=segundo_apellido,
                        estado_id_001 = Cat001Estado.objects.get(id=1)
                    )

                    grupo = Grupo.objects.get(id=2)
                    user = UsuarioBase.objects.create_user(
                        username= email, 
                        email= email, 
                        password=password1,
                        primer_nombre = primer_nombre.capitalize() ,
                        segundo_nombre = segundo_nombre.capitalize() ,
                        primer_apellido = primer_apellido.capitalize(),   
                        segundo_apellido = segundo_apellido.capitalize(), 
                        group = grupo,
                        candidato_id_101 = candidato,
                    )
                    
                    token_generado = generate_token(50);

                    TokenAutorizacion.objects.create(
                        user_id=user.id,
                        token=token_generado,  # Una función que genere un token único
                        fecha_expiracion=timezone.now() + timedelta(days=2),  # Si tiene fecha de expiración
                    )

                    # Envio del correo electronico de confirmación del usuario y contraseña
                    contexto = {
                        'name': primer_nombre.capitalize(),
                        'last_name': primer_apellido.capitalize(),
                        'user': user,
                        'email': email,
                        'password': password1,
                        'token': token_generado,
                        'url' : url_actual
                    }

                    # Envia el metodo
                    enviar_correo('bienvenida', contexto, 'Creación de Usuario ATS', [email], correo_remitente=None)

                    token_qr = request.POST.get('token') or request.GET.get('token')
                    if token_qr:
                        from applications.reclutado.views.common_views import crear_registro_cli084
                        crear_registro_cli084(token_qr, user)
                    
                    frase_aleatoria = 'Se ha enviado un correo electronico para su validar el mismo.'
                    messages.success(request, frase_aleatoria)

                    return redirect('accesses:login') 
            else:
                frase_aleatoria = random.choice(frases_error_contrasena)
                messages.error(request, frase_aleatoria)
    else:
        form = SignupFormCandidato()

    token_qr = request.GET.get('token')
    login_f = random.choice(frases_inicio_sesion)
    return render(request, 'admin/login/candidate_registration.html', {'form': form, 'login_f': login_f, 'token_qr': token_qr})

#pantalla inicio
# @login_required
@validar_permisos(*Permiso.obtener_nombres())
def dashboard_begin(request):
    """ Vista que carga la página de inicio y muestra variables de sesión """
    
    # Obtener todas las variables de sesión
    session_variables = dict(request.session)

    print(session_variables)

    # Accedemos a los permisos guardados en el request
    permisos_usuario = getattr(request, 'permisos_usuario', [])

    # valida 
    #ats portal interno
    if session_variables['grupo_id'] == 1:
        print('Sesion Admin')
        return redirect('accesses:inicio_administrador')
    #candidato información panel
    if session_variables['grupo_id'] == 2:
        return redirect('accesses:inicio_candidato')
    else:
        entrevistas_pendiente_candidato = None
        asignacion_vacante = None

    #cliente informacion panel
    if session_variables['grupo_id'] == 3:
        print('Sesion Cliente')
        cliente_id = request.session.get('cliente_id')
        return redirect('accesses:inicio_cliente')
    else:
        vacantes_pendiente_cliente = None  

    if session_variables['grupo_id'] == 7:
        cliente_id = request.session.get('cliente_id')
        print('Sesion Reclutador')
    else:
        reclutador_pendiente = None

    # Si quieres pasar las variables de sesión al template
    context = {
        'session_variables': session_variables,
        'permisos' : permisos_usuario,

    }
    
    return render(request, 'admin/dashboard.html', context)



# Salida de sesión.
def logout_view(request):
    print("Variables de sesión (antes de logout):", request.session.items())
    print('---------------------')
    logout(request)
    print("Variables de sesión (despues de logout):", request.session.items())
    return redirect('accesses:login')    # Redirigir a la página de inicio de sesión después de cerrar sesión

# Acceso a sistema
def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, "Ya has iniciado sesión.")
        return redirect('accesses:inicio')
    else:
        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    usuario = UsuarioBase.objects.get(username=user)
                    
                    if usuario.is_verificado == True:
                        login(request, user)

                        # Cargar variables de sesión aquí
                        request.session['primer_nombre'] = f'{usuario.primer_nombre} {usuario.primer_apellido}'
                        request.session['email'] = usuario.username
                        request.session['user_login'] = {
                            'id': usuario.id,
                            'username': usuario.username,
                            'email': usuario.email,
                            'primer_nombre': usuario.primer_nombre,
                            'segundo_nombre': usuario.segundo_nombre,
                            'primer_apellido': usuario.primer_apellido,
                            'segundo_apellido': usuario.segundo_apellido,
                            'grupo_id': usuario.group.id,
                            'cliente_id': usuario.cliente_id_051.id if usuario.cliente_id_051 else None,
                            'cliente_nombre': usuario.cliente_id_051.razon_social if usuario.cliente_id_051 else None,
                            'cliente_tipo': usuario.cliente_id_051.tipo_cliente if usuario.cliente_id_051 else None,
                        }

                        #validar imagen de perfil
                        try:
                            if usuario.imagen_perfil and usuario.imagen_perfil.name:
                                request.session['imagen_url'] = usuario.imagen_perfil.url
                            else:
                                request.session['imagen_url'] = f'{settings.STATIC_URL}media/avatars/blank.png'
                        except (ValueError, AttributeError):
                            request.session['imagen_url'] = f'{settings.STATIC_URL}media/avatars/blank.png'

                        #Tipo de usuario
                        request.session['tipo_usuario'] = usuario.group.name

                        #validar Grupo 1 Administrador
                        if usuario.group.id == 1:
                            request.session['imagen_url'] = f'{settings.MEDIA_URL}ats/logo_talenttray.jpg'

                        #validar Grupo 2 Candidato
                        if usuario.group.id == 2:
                            candidato_id = usuario.candidato_id_101.id
                            candidato = Can101Candidato.objects.get(id = candidato_id)
                            request.session['candidato_id'] = candidato.id
                        
                        # Validar Grupo 3 Cliente
                        if usuario.group.id == 3:
                            cliente_id = usuario.cliente_id_051.id
                            cliente = Cli051Cliente.objects.get(id = cliente_id)
                            request.session['cliente_id'] = cliente.id
                            if cliente.logo:
                                request.session['imagen_url'] = cliente.logo.url
                            else:
                                request.session['imagen_url'] = f'{settings.STATIC_URL}media/avatars/blank.png'

                            if cliente.tipo_cliente == '1':
                                request.session['tipo_cliente'] = 'Standard'
                            elif cliente.tipo_cliente == '2':
                                request.session['tipo_cliente'] = 'Headhunter'
                            elif cliente.tipo_cliente == '3':
                                request.session['tipo_cliente'] = 'Asignado'

                        # Grupo 4 Cliente Entrevistador
                        if usuario.group.id == 4:
                            request.session['cliente_id'] = usuario.cliente_id_051.id
                            
                        # Grupo 5 Analista Selección
                        if usuario.group.id == 5:
                            try:
                                if usuario.imagen_perfil and usuario.imagen_perfil.name:
                                    request.session['imagen_url'] = usuario.imagen_perfil.url
                                else:
                                    request.session['imagen_url'] = f'{settings.STATIC_URL}media/avatars/blank.png'
                            except (ValueError, AttributeError):
                                request.session['imagen_url'] = f'{settings.STATIC_URL}media/avatars/blank.png'
                            request.session['cliente_id'] = usuario.cliente_id_051.id
                        
                        # Grupo 6 Analista Selección ATS
                        if usuario.group.id == 6:
                            try:
                                if usuario.imagen_perfil and usuario.imagen_perfil.name:
                                    request.session['imagen_url'] = usuario.imagen_perfil.url
                                else:
                                    request.session['imagen_url'] = f'{settings.STATIC_URL}media/avatars/blank.png'
                            except (ValueError, AttributeError):
                                request.session['imagen_url'] = f'{settings.STATIC_URL}media/avatars/blank.png'

                        # Grupo 7 Analista Selección ATS (Interno)
                        if usuario.group.id == 7:
                            cliente_id = usuario.cliente_id_051.id
                            cliente = Cli051Cliente.objects.get(id = cliente_id)
                            request.session['cliente_id'] = cliente.id

                        request.session['grupo_id'] = usuario.group.id
                        return redirect('accesses:inicio')  
                    else:
                        messages.error(request, 'No se ha válidado su correo, por favor revise la bandeja de entrada.')
                        return redirect('accesses:login')  
                else:
                    frase_aleatoria = random.choice(frases_falla_login)
                    messages.error(request, frase_aleatoria)
                    return redirect('accesses:login')
                
            else:
                messages.error(request, "Por favor, complete todos los campos del formulario.")
        else:
            form = LoginForm()

    return render(request, 'admin/login/login.html',{
        'form':form,
        })

# valdidar token.
def validar_token(request, token):

    context = {
        'is_valid': False,
        'message': ''
    }
    

    # Buscar el token en la base de datos
    
    try:
        # Buscar el token en la base de datos
        token_obj = TokenAutorizacion.objects.get(token=token)
        
        # Validar si el token ha vencido
        if token_obj.fecha_expiracion < timezone.now():
            context['message'] = 'Link vencido'
            
            token_obj.fecha_validacion = timezone.now()
            token_obj.save()  # No olvides guardar el objeto actualizado

        else:
            # Si el token es válido
            usuario = get_object_or_404(UsuarioBase, id=token_obj.user.id)

            #Actualizar el estado de verificación
            usuario.is_verificado = True
            usuario.save()

            # Actualizar la fecha de validación del token
            token_obj.fecha_validacion = timezone.now()
            token_obj.save()  # No olvides guardar el objeto actualizado

            context['is_valid'] = True
            context['message'] = 'Correo validado correctamente'

    except TokenAutorizacion.DoesNotExist:
        context['message'] = 'Token no válido'

    return render(request, 'admin/login/authentication.html', context)

#validar correo para enviar correo
def enviar_token(request):
    url_actual = f"{request.scheme}://{request.get_host()}"
    if request.method == 'POST':
        form = CorreoForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']

            if UsuarioBase.objects.filter(username=email).exists():
                usuario_email = UsuarioBase.objects.get(username=email)
                
                token_generado = generate_token(50);
                TokenAutorizacion.objects.create(
                    user_id=usuario_email.id,
                    token=token_generado,  # Una función que genere un token único
                    fecha_expiracion=timezone.now() + timedelta(days=2),  # Si tiene fecha de expiración
                )

                #Envio del correo electronico de confirmación del usuario y contraseña
                contexto = {
                    'name': usuario_email.primer_nombre.capitalize(),
                    'last_name': usuario_email.primer_apellido.capitalize(),
                    'user': usuario_email.username,
                    'email': email,
                    'token': token_generado,
                    'url' : url_actual
                }
                # Envia el metodo
                enviar_correo('token', contexto, 'Creación de Usuario ATS', [email], correo_remitente=None)
                
                # login(request, user)
                frase_aleatoria = 'Se ha enviado un correo electronico para su validar el mismo.'
                messages.success(request, frase_aleatoria)
                return redirect('accesses:login')
                
            else:
                messages.error(request, 'El correo ingresado no se encuentra registrado')
                return redirect('accesses:enviar_token')  
        else:
            messages.error(request, '¡Oops! Hubo un error al procesar el correo.')
            return redirect('accesses:enviar_token') 
    else:
        form = CorreoForm()

    return render(request, 'admin/login/authentication_again.html', {'form': form, })

#vista para mostrar pantalla de acceso deneado cuando el decorador no tenga el listado de permisos cargados
def acceso_denegado(request):
    url_actual = f"{request.scheme}://{request.get_host()}"
    return render(request, 'admin/login/access_denied.html')

def change_password_form(request):
    url_actual = f"{request.scheme}://{request.get_host()}"
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            if UsuarioBase.objects.filter(username=email).exists():
                usuario_email = UsuarioBase.objects.get(username=email)

                token_generado = generate_token(50);
                TokenAutorizacion.objects.create(
                    user_id=usuario_email.id,
                    token=token_generado,  # Una función que genere un token único
                    fecha_expiracion=timezone.now() + timedelta(days=2),  # Si tiene fecha de expiración
                )

                contexto = {
                    'name': usuario_email.primer_nombre.capitalize(),
                    'last_name': usuario_email.primer_apellido.capitalize(),
                    'user': usuario_email.username,
                    'email': email,
                    'token': token_generado,
                    'url' : url_actual
                }

                enviar_correo('cambio_password', contexto, 'Cambio contraseña ATS', [email], correo_remitente=None)

                messages.success(request, 'Se ha enviado un correo electronico para su cambiar la contraseña')
                return redirect('accesses:change_password')
            else:
                messages.error(request, 'El correo ingresado no se encuentra registrado')
                return redirect('accesses:change_password')
        else:
            messages.error(request, '¡Oops! Hubo un error al procesar el correo.')
            return redirect('accesses:change_password')
    else:
        form = EmailForm()

    context = {
        'form': form,
    }

    return render(request, 'admin/login/change_password.html', context)

def confirm_password_form(request, token):
    form = EmailUserForm()

    try:
        token_obj = TokenAutorizacion.objects.get(token=token)
        
        if token_obj.fecha_expiracion < timezone.now():
            messages.error(request, 'Token vencido, por favor ingrese nuevamente su correo para generar uno nuevo')
            return redirect('accesses:change_password')
        
        if token_obj.fecha_validacion is not None:
            messages.error(request, 'Token ya validado, por favor ingrese nuevamente su correo para generar uno nuevo')
            return redirect('accesses:change_password')
        
        if request.method == 'POST':
            form = EmailUserForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data['password']
                confirm_password = form.cleaned_data['confirm_password']
                if password != confirm_password:
                    messages.error(request, 'Las contraseñas no coinciden')
                    return redirect('accesses:change_password')
                
                usuario = get_object_or_404(UsuarioBase, id=token_obj.user.id)
                usuario.set_password(password)
                usuario.save()

                token_obj.fecha_validacion = timezone.now()
                token_obj.save()

                messages.success(request, 'Contraseña actualizada correctamente')
                return redirect('accesses:login')
            else:
                messages.error(request, '¡Oops! Hubo un error al procesar la contraseña.')
                return redirect('accesses:change_password')
        else:
            form = EmailUserForm()

    except TokenAutorizacion.DoesNotExist:
        messages.error(request, 'Token no válido')
        return redirect('accesses:change_password')

    context = {
        'form': form,
    }

    return render(request, 'admin/login/confirm_password.html', context)


@login_required
@validar_permisos(*Permiso.obtener_nombres())
def my_profile(request):
    """Vista de perfil del usuario logueado: nombre, tipo, correo, teléfono, imagen y opción para cambiar contraseña."""
    from applications.common.views.QrCode import get_or_create_asignacion_qr

    usuario = get_object_or_404(UsuarioBase, id=request.user.id)
    
    nombre_completo = f'{usuario.primer_nombre or ""} {usuario.segundo_nombre or ""} {usuario.primer_apellido or ""} {usuario.segundo_apellido or ""}'.strip() or usuario.username
    tipo_usuario = usuario.group.name if usuario.group else 'Usuario'
    correo = usuario.username or usuario.email or '-'
    telefono = usuario.telefono or '-'
    imagen_url = None
    if usuario.imagen_perfil and usuario.imagen_perfil.name:
        imagen_url = usuario.imagen_perfil.url
    else:
        imagen_url = f'{settings.STATIC_URL}media/avatars/blank.png'
    
    form_cambio_password = CambioContrasenaPerfilForm()
    from django.urls import reverse
    try:
        url_cambiar_contrasena = reverse('accesses:cambiar_contrasena_perfil')
    except Exception:
        url_cambiar_contrasena = '/mi_perfil/cambiar-contrasena/'
    try:
        url_actualizar_imagen = reverse('accesses:actualizar_imagen_perfil')
    except Exception:
        url_actualizar_imagen = '/mi_perfil/actualizar-imagen/'

    show_qr_registro = False
    asignacion_qr = None
    url_registro_token = None
    grupo_id = request.session.get('grupo_id')
    if grupo_id in (1, 7):
        show_qr_registro = True
        asignacion_qr = get_or_create_asignacion_qr(usuario, request)
        if asignacion_qr and asignacion_qr.token_qr:
            url_base = f"{request.scheme}://{request.get_host()}"
            url_registro_token = f"{url_base}/registro/candidato/?token={asignacion_qr.token_qr}"
    
    context = {
        'usuario': usuario,
        'nombre_completo': nombre_completo,
        'tipo_usuario': tipo_usuario,
        'correo': correo,
        'telefono': telefono,
        'imagen_url': imagen_url,
        'form_cambio_password': form_cambio_password,
        'url_cambiar_contrasena': url_cambiar_contrasena,
        'url_actualizar_imagen': url_actualizar_imagen,
        'show_qr_registro': show_qr_registro,
        'asignacion_qr': asignacion_qr,
        'url_registro_token': url_registro_token,
    }
    return render(request, 'admin/login/my_profile.html', context)


@login_required
def generar_qr_imagen(request):
    """Genera imagen QR para la URL proporcionada en el parámetro data."""
    from applications.common.views.QrCode import generate_qr
    return generate_qr(request)


@login_required
def actualizar_imagen_perfil(request):
    """Vista para actualizar la imagen de perfil del usuario logueado."""
    redirect_url = '/mi_perfil/'
    if request.method != 'POST' or 'imagen_perfil' not in request.FILES:
        messages.error(request, 'No se envió ninguna imagen.')
        return redirect(redirect_url)
    
    archivo = request.FILES['imagen_perfil']
    ext = archivo.name.split('.')[-1].lower() if '.' in archivo.name else ''
    if ext not in ['jpg', 'jpeg', 'png']:
        messages.error(request, 'Formato no válido. Solo se permiten JPG, JPEG y PNG.')
        return redirect(redirect_url)
    if archivo.size > 5 * 1024 * 1024:
        messages.error(request, 'La imagen no debe superar los 5 MB.')
        return redirect(redirect_url)
    
    usuario = get_object_or_404(UsuarioBase, id=request.user.id)
    usuario.imagen_perfil = archivo
    usuario.save()
    
    request.session['imagen_url'] = usuario.imagen_perfil.url
    messages.success(request, 'Imagen de perfil actualizada correctamente.')
    return redirect(redirect_url)


@login_required
def cambiar_contrasena_perfil(request):
    """Vista para cambiar la contraseña del usuario logueado."""
    if request.method != 'POST':
        return redirect('accesses:my_profile')
    
    form = CambioContrasenaPerfilForm(request.POST)
    if form.is_valid():
        usuario = get_object_or_404(UsuarioBase, id=request.user.id)
        password_actual = form.cleaned_data['password_actual']
        password_nueva = form.cleaned_data['password_nueva']
        
        if not usuario.check_password(password_actual):
            messages.error(request, 'La contraseña actual no es correcta.')
            return redirect('accesses:my_profile')
        
        usuario.set_password(password_nueva)
        usuario.save()
        messages.success(request, 'Contraseña actualizada correctamente. Por favor, inicie sesión nuevamente.')
        logout(request)
        return redirect('accesses:login')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, error)
        return redirect('accesses:my_profile')