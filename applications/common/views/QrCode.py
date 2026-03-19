import qrcode
from io import BytesIO
from django.http import HttpResponse
from django.core.files.base import ContentFile
from applications.common.views.EnvioCorreo import generate_token


def generate_qr(request):
    """Genera imagen QR de la URL proporcionada o la URL actual."""
    url_actual = f"{request.scheme}://{request.get_host()}"
    data = request.GET.get("data", url_actual)

    img = qrcode.make(data)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type="image/png")


def get_or_create_asignacion_qr(usuario, request):
    """
    Obtiene o crea el registro Cat005AsignacionQr para el usuario.
    Genera token, URL de registro candidato y guarda la imagen QR si no existe.
    Retorna el objeto asignacion_qr o None si hay error.
    """
    from applications.common.models import Cat005AsignacionQr, Cat001Estado
    from applications.usuarios.models import Grupo

    if not usuario or not usuario.group:
        return None

    try:
        estado_activo = Cat001Estado.objects.get(id=1)
        grupo = usuario.group

        asignacion = Cat005AsignacionQr.objects.filter(usuario_asignado=usuario).first()
        if not asignacion:
            asignacion = Cat005AsignacionQr.objects.create(
                nombre=f'QR Registro - {usuario.username}',
                descripcion='Código QR para registro de candidatos',
                estado_id_001=estado_activo,
                grupo_asignacion=grupo,
                usuario_asignado=usuario,
            )

        url_base = f"{request.scheme}://{request.get_host()}"
        registro_url = f"{url_base}/registro/candidato/"

        if not asignacion.token_qr:
            asignacion.token_qr = generate_token(50)
            asignacion.save(update_fields=['token_qr'])

        url_con_token = f"{registro_url}?token={asignacion.token_qr}"

        if not asignacion.qr_code or not asignacion.qr_code.name:
            img = qrcode.make(url_con_token)
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            nombre_archivo = f"qr_{usuario.id}_{asignacion.id}.png"
            asignacion.qr_code.save(nombre_archivo, ContentFile(buffer.getvalue()), save=True)

        return asignacion
    except Exception:
        return None
