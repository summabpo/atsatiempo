from django.shortcuts import render, redirect # type: ignore
from django.contrib.auth import authenticate, login, logout # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from django.contrib import messages # type: ignore
from django.http import HttpResponse # type: ignore
from applications.usuarios.models import UsuarioBase, TokenAutorizacion, Grupo, Permiso
from applications.usuarios.forms.CorreoForm import CorreoForm
from applications.cliente.models import Cli051Cliente
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

# consultas
from applications.vacante.views.consultas.AsignacionVacanteConsultaView import consulta_asignacion_vacante_candidato
from applications.common.views.PanelView import info_vacantes_pendientes, info_entrevistas_candidato


#dictado de frases aleatorias
frases_falla_login = [
    "¡Parece que el nombre de usuario o la contraseña están jugando a las escondidas! Revisa y vuelve a intentarlo.",
    "¡Oh no! El nombre de usuario o la contraseña decidieron tomar un día libre. ¡Verifica los datos y vuelve a intentarlo!",
    "¡Ups! El nombre de usuario o la contraseña están en modo de vacaciones. Asegúrate de ingresar la información correcta.",
    "¡Ay caramba! El nombre de usuario o la contraseña se escaparon. Revisa tus datos e intenta de nuevo.",
    "¡Vaya, vaya! El nombre de usuario o la contraseña están en huelga. Verifica tus credenciales y vuelve a intentarlo.",
    "¡Oh no! Parece que el nombre de usuario o la contraseña están de parranda. Asegúrate de que todo esté en orden y prueba de nuevo.",
    "¡Menuda sorpresa! El nombre de usuario o la contraseña decidieron hacer una siesta. Verifica la información e inténtalo otra vez.",
    "¡Atención! El nombre de usuario o la contraseña están haciendo travesuras. Asegúrate de que sean correctos y vuelve a intentarlo.",
    "¡Ups! Parece que el nombre de usuario o la contraseña se perdieron. Verifica los datos e intenta nuevamente.",
    "¡Oh! El nombre de usuario o la contraseña están de fiesta. Revisa tus credenciales y prueba de nuevo."
]

frases_inicio_sesion = [
    "¿Ya tienes una cuenta? ¡Perfecto! Entonces, deja de perder el tiempo y entra para empezar la diversión.",
    "¿Ya eres parte de la familia? ¡Genial! Solo falta iniciar sesión y empezar la acción.",
    "¡Ya tienes cuenta, aventurero! ¿Qué esperas? Inicia sesión y lánzate a la aventura.",
    "¿Cuentas con una cuenta? ¡Eso está bien! Solo falta hacer login y empezar a explorar.",
    "¿Ya eres usuario? ¡Perfecto! Solo inicia sesión y comienza a disfrutar.",
    "¡Ya tienes cuenta! Entonces, no pierdas más tiempo aquí. Inicia sesión y lánzate al meollo del asunto.",
    "¿Ya registraste tu cuenta? ¡Inicia sesión ya y empieza a disfrutar del contenido!",
    "¿Ya tienes acceso? ¡Genial! Solo falta iniciar sesión y comenzar la fiesta.",
    "¡Eres un usuario experimentado! Entonces, ¿por qué estás aquí? Inicia sesión y vamos a lo importante.",
    "¿Ya tienes una cuenta? ¡Entonces inicia sesión y deja de perder el tiempo aquí!"
]

frases_error_contrasena = [
    "¡Oops! Las contraseñas están jugando al escondite. Asegúrate de que coincidan y prueba de nuevo.",
    "¡Vaya! Parece que las contraseñas están en una pelea. Revisa que ambas sean iguales y vuelve a intentarlo.",
    "¡Oh no! Las contraseñas no se están poniendo de acuerdo. Verifica que coincidan y prueba otra vez.",
    "¡Menuda confusión! Las contraseñas no están sincronizadas. Asegúrate de que sean idénticas y vuelve a intentarlo.",
    "¡Ay caramba! Las contraseñas están haciendo travesuras. Asegúrate de que sean las mismas y prueba de nuevo.",
    "¡Oops! Las contraseñas están en desacuerdo. Revisa que sean iguales y vuelve a intentarlo.",
    "¡Oh! Las contraseñas están haciendo su propia fiesta. Asegúrate de que coincidan y vuelve a intentarlo.",
    "¡Ups! Las contraseñas no están en sintonía. Verifica que sean iguales y vuelve a intentarlo.",
    "¡Vaya! Las contraseñas parecen tener opiniones diferentes. Asegúrate de que sean iguales y vuelve a intentarlo.",
    "¡Oh no! Las contraseñas están en una pelea de egos. Asegúrate de que sean idénticas y vuelve a intentarlo."
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
                    
                    frase_aleatoria = 'Se ha enviado un correo electronico para su validar el mismo.'
                    messages.success(request, frase_aleatoria)

                    return redirect('accesses:login') 
            else:
                frase_aleatoria = random.choice(frases_error_contrasena)
                messages.error(request, frase_aleatoria)
    else:
        form = SignupFormCandidato()

    login_f = random.choice(frases_inicio_sesion)
    return render(request, 'admin/login/candidate_registration.html', {'form': form, 'login_f':login_f,} )

#pantalla inicio
@login_required
@validar_permisos(*Permiso.obtener_nombres())
def dashboard_begin(request):
    """ Vista que carga la página de inicio y muestra variables de sesión """
    
    # Obtener todas las variables de sesión
    session_variables = dict(request.session)

    # Accedemos a los permisos guardados en el request
    permisos_usuario = getattr(request, 'permisos_usuario', [])

    print(permisos_usuario)
    
    # Puedes imprimir las variables de sesión para debug
    print("Variables de sesión:", session_variables)

    # valida 
    #ats portal interno
    if session_variables['grupo_id'] == 1:
        print('Sesion Admin')
        
    #cliente informacion panel
    if session_variables['grupo_id'] == 3:
        print('Sesion Cliente')
        cliente_id = request.session.get('cliente_id')
        # vacantes_pendiente_cliente = info_vacantes_pendientes(cliente_id)
    else:
        vacantes_pendiente_cliente = None  

    #candidato información panel
    if session_variables['grupo_id'] == 2:
        
        candidato_id = request.session.get('candidato_id')
        # entrevistas_pendiente_candidato = info_entrevistas_candidato(candidato_id)
        # asignacion_vacante = consulta_asignacion_vacante_candidato(candidato_id)
    else:
        entrevistas_pendiente_candidato = None
        asignacion_vacante = None

    # Si quieres pasar las variables de sesión al template
    context = {
        'session_variables': session_variables,
        'permisos' : permisos_usuario,
        # 'vacantes_pendiente_cliente': vacantes_pendiente_cliente,
        # 'entrevistas_pendiente_candidato': entrevistas_pendiente_candidato,
        # 'asignacion_vacante': asignacion_vacante,
    }
    
    return render(request, 'admin/dashboard.html', context)

# Salida de sesión.
def logout_view(request):
    logout(request)
    return redirect('accesses:login')    # Redirigir a la página de inicio de sesión después de cerrar sesión

# Acceso a sistema
def login_view(request):
    if request.user.is_authenticated:
        # print('No esta autenticado')
        # messages.error(request, "Debes iniciar sesión para acceder a esta página.")
        # return redirect('accesses:login')
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
                        request.session['primer_nombre'] = f'{usuario.primer_nombre} {usuario.primer_apellido}'
                        request.session['email'] = usuario.username
                        
                        # Valida el usuario es de grupo cliente para mostrar el id cliente. 
                        if usuario.group.id == 4:
                            request.session['cliente_id'] = usuario.cliente_id_051.id
                            request.session['tipo_usuario'] = 'Cliente'
                            
                        if usuario.group.id == 3:
                            cliente_id = usuario.cliente_id_051.id
                            cliente = Cli051Cliente.objects.get(id = cliente_id)
                            request.session['cliente_id'] = cliente.id
                            if cliente.logo:
                                request.session['imagen_url'] = cliente.logo.url
                            else:
                                request.session['imagen_url'] = '/static/media/avatars/blank.png'

                            if cliente.tipo_cliente == '1':
                                request.session['tipo_cliente'] = 'Standard'
                            elif cliente.tipo_cliente == '2':
                                request.session['tipo_cliente'] = 'Headhunter'
                            elif cliente.tipo_cliente == '3':
                                request.session['tipo_cliente'] = 'Asignado'
                            
                            request.session['tipo_usuario'] = 'Cliente'

                        if usuario.group.id == 2:
                            candidato_id = usuario.candidato_id_101.id
                            candidato = Can101Candidato.objects.get(id = candidato_id)
                            request.session['candidato_id'] = candidato.id
                            if candidato.imagen_perfil:
                                request.session['imagen_url'] = candidato.imagen_perfil.url
                            else:
                                request.session['imagen_url'] = '/static/media/avatars/blank.png'
                            
                            request.session['tipo_usuario'] = 'Candidato'

                        if usuario.group.id == 1:
                            request.session['imagen_url'] = '/media_uploads/ats/logo_atiempo.png'
                            request.session['tipo_usuario'] = 'Administrador'

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
            form = LoginForm()

    return render(request, 'admin/login/login.html',{
        'form':form,
        })
