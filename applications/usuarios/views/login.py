from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from applications.usuarios.forms.loginform import LoginForm
from applications.usuarios.forms.UserForms import SignupForm
from applications.usuarios.forms.CandidatoForm import SignupFormCandidato
from applications.usuarios.models import UsuarioBase, TokenAutorizacion, Grupo, Permiso
from applications.usuarios.forms.CorreoForm import CorreoForm
from applications.cliente.models import Cli051Cliente
from applications.candidato.models import Can101Candidato
import random
from django.utils.text import capfirst
from applications.common.models import Cat004Ciudad, Cat001Estado
from applications.common.views.EnvioCorreo import enviar_correo, generate_token
from django.utils import timezone
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from ..decorators  import validar_permisos

## login 
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

frases_creacion_cuenta = [
    "¿Aún no tienes cuenta? ¡No te preocupes! Crear una es tan rápido que podrías hacerlo antes de que termine el video viral que estás viendo.",
    "¿Todavía no tienes cuenta? ¡No hay problema! Crear una es tan rápido que podrías hacerlo antes de que tu serie favorita lance el siguiente episodio.",
    "¿Aún sin cuenta? ¡No te preocupes! Crear una es tan rápido que podrías hacerlo antes de que tu videojuego cargue el siguiente nivel.",
    "¿Aún no tienes cuenta? ¡No te preocupes! Crear una es tan rápido que podrías hacerlo antes de que tu perro decida dejar de buscar su juguete.",
    "¿No tienes cuenta aún? ¡No hay problema! Crear una es tan rápido que podrías hacerlo antes de que tu planta decida crecer una hoja nueva.",
    "¿Todavía sin cuenta? ¡No te preocupes! Crear una es tan rápido que podrías hacerlo antes de que tu meme favorito se vuelva obsoleto.",
    "¿Aún sin cuenta? ¡No hay lío! Crear una es tan rápido que podrías hacerlo antes de que tu música de fondo cambie de canción.",
    "¿Aún no tienes cuenta? ¡No te preocupes! Crear una es tan rápido que podrías hacerlo antes de que tu tarta de cumpleaños se derrita.",
    "¿Todavía sin cuenta? ¡No hay problema! Crear una es tan rápido que podrías hacerlo antes de que tu gato decida dejar de ignorarte.",
    "¿Aún no tienes cuenta? ¡No te preocupes! Crear una es tan rápido que podrías hacerlo antes de que tu nuevo libro llegue al final de la primera página."
]

frases_restablecimiento = [
    "Te enviaremos un correo electrónico con instrucciones para restablecer tu contraseña. ¡Es tan fácil que podrías hacerlo mientras terminas de leer un artículo interesante!",
    "Recibirás un correo electrónico con instrucciones para restablecer tu contraseña. ¡Es tan rápido que podrías hacerlo antes de que tu serie favorita termine el primer episodio!",
    "Un correo electrónico con instrucciones para restablecer tu contraseña está en camino. ¡Es tan sencillo que podrías hacerlo mientras esperas que se cocine la pasta!",
    "Te enviaremos un correo con las instrucciones para restablecer tu contraseña. ¡Es tan fácil que podrías hacerlo mientras decides qué ver en tu plataforma de streaming!",
    "Pronto recibirás un correo con instrucciones para restablecer tu contraseña. ¡Es tan rápido que podrías hacerlo mientras tomas un breve descanso del trabajo!",
    "Te llegará un correo con las instrucciones para restablecer tu contraseña. ¡Es tan sencillo que podrías hacerlo mientras tu café se enfría!",
    "Un correo con las instrucciones para restablecer tu contraseña está en camino. ¡Es tan fácil que podrías hacerlo mientras esperas que se cargue una aplicación!",
    "Recibirás un correo con las instrucciones para restablecer tu contraseña. ¡Es tan rápido que podrías hacerlo mientras eliges tu próxima canción!",
    "Te enviaremos un correo con instrucciones para restablecer tu contraseña. ¡Es tan sencillo que podrías hacerlo mientras tu máquina de café hace su magia!",
    "Un correo con las instrucciones para restablecer tu contraseña llegará pronto. ¡Es tan fácil que podrías hacerlo mientras le das un vistazo a tus redes sociales!"
]

frases_bienvenida = [
    "¡Hola, aventurero! Espero que disfrutes más que un niño en una tienda de golosinas.",
    "¡Bienvenido al club! Espero que te diviertas tanto como un perro en una fiesta de disfraces.",
    "¡Saludos! Espero que te guste tanto como a un gato encontrar un rayo de sol en un día nublado.",
    "¡Qué alegría verte por aquí! Espero que te diviertas más que un niño con una caja de LEGO.",
    "¡Ey, bienvenido! Espero que disfrutes tanto como una abeja en un jardín lleno de flores.",
    "¡Hola, nuevo amigo! Espero que te guste tanto como un ratón encontrar un pedazo de queso.",
    "¡Hola, explorador! Espero que disfrutes más que un niño con una pala en la playa.",
    "¡Bienvenido! Espero que te diviertas tanto como un perro con una nueva pelota.",
    "¡Hey, qué tal! Espero que te guste tanto como un niño descubre un nuevo parque de diversiones.",
    "¡Saludos, compañero! Espero que disfrutes más que un chef con una receta ganadora.",
    "¡Hola, nuevo usuario! Espero que te diviertas tanto como un pájaro al vuelo libre.",
    "¡Bienvenido a bordo! Espero que disfrutes más que un pez en un estanque nuevo.",
    "¡Ey, qué pasa! Espero que te guste tanto como un niño con un nuevo juguete.",
    "¡Hola, amigo! Espero que disfrutes más que un gato con una caja nueva.",
    "¡Bienvenido a la fiesta! Espero que te diviertas tanto como una tortuga en un mar tranquilo.",
    "¡Hola, nuevo miembro! Espero que te guste tanto como a un niño le gusta encontrar caramelos escondidos.",
    "¡Qué bueno verte! Espero que disfrutes más que un caballo galopando libremente en el campo.",
    "¡Hola! Espero que te diviertas tanto como un mago descubriendo un nuevo truco.",
    "¡Bienvenido! Espero que disfrutes más que un niño en un rincón de juegos lleno de sorpresas.",
    "¡Hey, qué onda! Espero que te guste tanto como un gato jugando con una pelota de lana."
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

frases_error_usuario = [
    "¡Oh no! Este nombre de usuario ya está en uso. ¿Te atreves a encontrar uno tan genial como este?",
    "¡Vaya! Alguien más se adelantó y ya usó este nombre de usuario. Intenta ser más original y prueba con otro.",
    "¡Ups! Este nombre de usuario ya está registrado. Parece que el universo te está pidiendo que seas más creativo.",
    "¡Menuda coincidencia! Alguien más ya pensó en este nombre de usuario. Intenta con uno diferente antes de que todos se acaben.",
    "¡Oh! Este nombre de usuario ya está ocupado. Parece que alguien más también tiene buen gusto. Elige otro y sigue adelante.",
    "¡Oops! Este nombre de usuario ya está en la lista. ¿Qué tal probar con algo más único antes de que todos los buenos se acaben?",
    "¡Oh no! Este nombre de usuario ya está tomado. ¿Te animas a buscar un nombre tan épico como este?",
    "¡Vaya! Alguien más ya se adelantó y usó este nombre. ¿Qué tal ser el primero en elegir otro igualmente genial?",
    "¡Ay caramba! Este nombre de usuario ya está en uso. ¡Parece que te toca encontrar uno aún más increíble!",
    "¡Oh! Este nombre de usuario ya está ocupado. ¡Asegúrate de que tu nuevo nombre sea tan memorable como el primero!"
]

frases_error_email = [
    "¡Oops! Este correo electrónico ya está registrado. ¿Quizás quieras probar con otro antes de que todos se acaben?",
    "¡Oh no! Este correo electrónico ya está en uso. Parece que alguien más también le gusta el mismo dominio.",
    "¡Menuda coincidencia! Este correo electrónico ya está registrado. ¡Es como si todos estuvieran compitiendo por el mismo!",
    "¡Vaya! Este correo electrónico ya ha sido tomado. ¿Qué tal si encuentras uno aún más sorprendente para tu cuenta?",
    "¡Oh! Este correo electrónico ya está ocupado. ¡No te preocupes, hay muchos más por descubrir!",
    "¡Oops! Este correo electrónico ya está en uso. Parece que estás compitiendo con un montón de gente por el mismo. Prueba otro.",
    "¡Oh no! Este correo electrónico ya está registrado. ¿Qué tal si pruebas con otro para destacar entre la multitud?",
    "¡Ay caramba! Este correo electrónico ya ha sido tomado. ¡Elige otro antes de que todos los buenos se acaben!",
    "¡Vaya! Este correo electrónico ya está en uso. ¡No te preocupes, seguro que hay un montón de opciones interesantes!",
    "¡Oh! Este correo electrónico ya está en la lista. ¡Asegúrate de que el próximo sea tan atractivo como este!"
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

frases_cancelacion = [
    "¡Vaya! Parece que te arrepentiste. No te preocupes, aquí te esperamos si decides regresar.",
    "¡Oh no! El proceso de creación de cuenta se quedó a medias. ¿Seguro que quieres abandonar la aventura?",
    "¡Ups! Parece que cambiaste de opinión. ¡Esperamos verte de nuevo cuando estés listo para unirte!",
    "¡Menuda sorpresa! Cancelaste el registro. Si te animas, siempre habrá una cuenta esperándote.",
    "¡Oh! Parece que te echa atrás. La puerta queda abierta para cuando quieras completar el proceso.",
    "¡Oh no! Te saliste antes de terminar. ¡No dudes en volver cuando estés listo para formar parte!",
    "¡Vaya! El proceso se detuvo en seco. Si decides retomar, aquí estaremos para ayudarte a completar el registro.",
    "¡Ay! Te has escapado antes de terminar. Si te vuelves a animar, la puerta siempre estará abierta.",
    "¡Ups! El registro quedó en pausa. ¡No dudes en regresar cuando quieras completar tu cuenta!",
    "¡Oh! Parece que te echa atrás el proceso. Si decides intentarlo de nuevo, estaremos aquí para ayudarte."
]

# pantalla principal
def principal(request):
    """Pantalla Inicial"""
    return render(request, 'authentication/home.html')

#pantalla inicio

@login_required
@validar_permisos(*Permiso.obtener_nombres())
def inicio_app(request):
    """ Vista que carga la página de inicio y muestra variables de sesión """
    
    # Obtener todas las variables de sesión
    session_variables = dict(request.session)

    # Accedemos a los permisos guardados en el request
    permisos_usuario = getattr(request, 'permisos_usuario', [])

    print(permisos_usuario)
    
    # Puedes imprimir las variables de sesión para debug
    print("Variables de sesión:", session_variables)
    
    # Si quieres pasar las variables de sesión al template
    context = {
        'session_variables': session_variables,
        'permisos' : permisos_usuario,
    }
    
    return render(request, 'base/index.html', context)

# Acceso a sistema
def login_view(request):
    if request.user.is_authenticated:
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
                        request.session['primer_nombre'] = usuario.primer_nombre
                        # Valida el usuario es de grupo cliente para mostrar el id cliente. 
                        if usuario.group.id == 3:
                            request.session['cliente_id'] = usuario.cliente_id_051.id

                        if usuario.group.id == 2:
                            request.session['candidato_id'] = usuario.candidato_id_101.id
                        
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

    return render(request, './authentication/login.html',{
        'form':form,
        })

# Salida de sesión.
def logout_view(request):
    logout(request)
    return redirect('accesses:login')    # Redirigir a la página de inicio de sesión después de cerrar sesión

# registro cliente.
def signup_view(request):
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
            
            # nit = form.cleaned_data['nit']
            # companyname = form.cleaned_data['companyname']
            # city = form.cleaned_data['city']
            # companycontact = form.cleaned_data['companycontact']
            # companyemail = form.cleaned_data['companyemail']
            
            if email == email2:
                if password1 == password2:
                    if UsuarioBase.objects.filter(username=email).exists():
                        messages.error(request, '¡Oops! Parece que alguien más ya se adelantó y tomó ese correo. Prueba con otro, o tal vez es el momento de reconciliarte con tu contraseña olvidada.')
                    else:
                        
                        city =  Cat004Ciudad.objects.get(id = form.cleaned_data['city'] )
                        print(type(form.cleaned_data['nit']))
                        new_company = Cli051Cliente (
                            estado_id_001 = Cat001Estado.objects.get(id=1),
                            razon_social= form.cleaned_data['companyname'] ,
                            nit= form.cleaned_data['nit'],                        
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
                            'token': token_generado
                        }

                        # Envia el metodo
                        enviar_correo('bienvenida', contexto, 'Creación de Usuario ATS', [email], correo_remitente=None)
                        
                        # login(request, user)
                        frase_aleatoria = 'Se ha enviado un correo electronico para su validar el mismo.'
                        messages.success(request, frase_aleatoria)
                        return redirect('accesses:signup')  
                else:
                    frase_aleatoria = random.choice(frases_error_contrasena)
                    messages.error(request, frase_aleatoria)
            else:
                messages.error(request, 'La dirección de correo electrónico no coincide.')
    else:
        form = SignupForm()
    login_f = random.choice(frases_inicio_sesion)
    return render(request, './authentication/signup.html', 
                    {'form': form,
                    'login_f':login_f,
                    })

#registro candidato
def signup_candidato(request):
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
                        'token': token_generado
                    }

                    # Envia el metodo
                    enviar_correo('bienvenida', contexto, 'Creación de Usuario ATS', [email], correo_remitente=None)
                    
                    # login(request, user)
                    frase_aleatoria = 'Se ha enviado un correo electronico para su validar el mismo.'
                    messages.success(request, frase_aleatoria)
                    return redirect('accesses:home') 
            else:
                frase_aleatoria = random.choice(frases_error_contrasena)
                messages.error(request, frase_aleatoria)
    else:
        form = SignupFormCandidato()

    login_f = random.choice(frases_inicio_sesion)
    return render(request, './authentication/signup_candidato.html', {'form': form, 'login_f':login_f,} )

# valdidar token.
def validar_token(request, token):
    print(token)
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

    return render(request, 'authentication/correo_validar.html', context)

#validar correo para enviar correo
def enviar_token(request):
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
                    'token': token_generado
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

    return render(request, './authentication/correo_revalidacion.html', {'form': form, })