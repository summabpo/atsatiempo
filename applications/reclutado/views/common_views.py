from applications.common.models import Cat001Estado, Cat005AsignacionQr
from applications.reclutado.models import Cli084AsignacionRegistroReclutado


def crear_registro_cli084(token, usuario):
    """
    Valida que el token exista en Cat005AsignacionQr (activo) y crea el registro en Cli084.
    Parámetros: token (str), usuario (UsuarioBase o id).
    Retorna: id del registro creado o None si el token no existe o no está activo.
    """
    asignacion_qr = Cat005AsignacionQr.objects.filter(
        token_qr=token,
        estado_id_001_id=1
    ).first()

    if not asignacion_qr:
        return None

    usuario_id = usuario.id if hasattr(usuario, 'id') else usuario
    estado_activo = Cat001Estado.objects.get(id=1)

    registro = Cli084AsignacionRegistroReclutado.objects.create(
        estado=estado_activo,
        usuario_registrado_id=usuario_id,
        asignacion_qr_005=asignacion_qr,
    )
    return registro.id