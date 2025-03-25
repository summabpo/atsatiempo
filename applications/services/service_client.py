from django.db.models import F, Count, Q, Value, Case, When, CharField
from applications.cliente.models import Cli051Cliente, Cli064AsignacionCliente
from applications.services.choices import TIPO_CLIENTE_STATIC

#consulta de detalle de cliente
def query_client_detail(id):
    cliente = Cli051Cliente.objects.filter(id=id).prefetch_related(
        "actividad_economica",
        "ciudad_id_004",
        "estado_id_001"
    ).first()

    if not cliente:
        return None  # Cliente no encontrado

    # Obtener asignaciones del cliente (como maestro o asignado)
    asignaciones = Cli064AsignacionCliente.objects.filter(
        id_cliente_maestro=cliente
    ).select_related("id_cliente_asignado")

    data = {
        "cliente": {
            "id": cliente.id,
            "nit": cliente.nit,
            "razon_social": cliente.razon_social,
            "email": cliente.email,
            "contacto": cliente.contacto,
            "telefono": cliente.telefono,
            "perfil_empresarial": cliente.perfil_empresarial,
            "tipo_cliente": cliente.get_tipo_cliente_display(),
            "actividad_economica": cliente.actividad_economica.descripcion if cliente.actividad_economica else "No definida",
            "ciudad": cliente.ciudad_id_004.nombre,
            "estado": cliente.estado_id_001.nombre,
            "logo": cliente.logo.url if cliente.logo else None,
            "cargo": cliente.contacto_cargo,
            "direccion": cliente.direccion_cargo,
            "referencias_laborales": cliente.referencias_laborales,
            "cantidad_colaboradores": cliente.cantidad_colaboradores,
        },
        "asignaciones": [
            {
                "id": a.id,
                "cliente_asignado": a.id_cliente_asignado.razon_social,
                "tipo_asignacion": a.get_tipo_asignacion_display(),
                "fecha_asignacion": a.fecha_asignacion
            }
            for a in asignaciones
        ]
    }

    return data

def query_client_all():

    clientes = Cli051Cliente.objects.select_related(
        'ciudad_id_004',
        'actividad_economica',
        'estado_id_001'
    )
    
    return clientes