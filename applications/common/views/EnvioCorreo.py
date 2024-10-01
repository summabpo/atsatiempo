from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import string
import secrets

def enviar_correo(tipo_correo, contexto, asunto, lista_destinatarios, correo_remitente=None):
    if correo_remitente is None:
        correo_remitente = settings.EMAIL_HOST_USER
    
    plantilla_correo = {
        'bienvenida': 'authentication/correo_bienvenida.html',
        'token': 'authentication/token_generado.html',
        'creacion_usuario_cliente': 'cliente/creacion_usuario.html',
        'asignacion_entrevista_entrevista' : 'vacante/asignacion_entrevista_correo.html',
    }

    nombre_plantilla = plantilla_correo.get(tipo_correo)

    if not plantilla_correo:
        raise ValueError(f"Tipo de correo no reconocido: {tipo_correo}")
    
    mensaje = render_to_string(nombre_plantilla, contexto)

    email = EmailMessage(
        subject=asunto,
        body=mensaje,
        from_email=correo_remitente,
        to=lista_destinatarios,
    )
    email.content_subtype = "html"

    try:
        email.send()
        return True
    except Exception as e:
        print(f"Error el enviar el correo: {e}")
        return False
    



def generate_token(length=100):
    # Definimos los caracteres que queremos usar en nuestro token
    characters = string.ascii_letters + string.digits
    
    # Generamos el token
    token = ''.join(secrets.choice(characters) for _ in range(length))
    
    return token