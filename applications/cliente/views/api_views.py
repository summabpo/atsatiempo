from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from applications.usuarios.decorators import validar_permisos
from applications.cliente.models import Cli051Cliente, Cli064AsignacionCliente
import json

@login_required
@validar_permisos('acceso_admin')
@csrf_exempt
@require_http_methods(["POST"])
def buscar_cliente_por_nit(request):
    """
    API para buscar cliente por NIT
    Retorna información del cliente si existe
    """
    try:
        data = json.loads(request.body)
        nit = data.get('nit', '').strip()
        
        if not nit:
            return JsonResponse({
                'success': False,
                'message': 'El NIT es requerido',
                'cliente': None
            })
        
        # Convertir NIT a entero si es posible
        try:
            nit_int = int(nit)
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'El NIT debe ser un número válido',
                'cliente': None
            })
        
        # Buscar cliente por NIT
        cliente = Cli051Cliente.objects.filter(nit=nit_int).first()
        
        if cliente:
            # Cliente encontrado
            return JsonResponse({
                'success': True,
                'message': 'Cliente encontrado',
                'cliente': {
                    'id': cliente.id,
                    'nit': cliente.nit,
                    'razon_social': cliente.razon_social,
                    'email': cliente.email or '',
                    'telefono': cliente.telefono or '',
                    'contacto': cliente.contacto or '',
                    'contacto_cargo': cliente.contacto_cargo or '',
                    'direccion_cargo': cliente.direccion_cargo or '',
                    'perfil_empresarial': cliente.perfil_empresarial or '',
                    'cantidad_colaboradores': cliente.cantidad_colaboradores or 0,
                    'referencias_laborales': cliente.referencias_laborales or 0,
                    'tipo_cliente': cliente.tipo_cliente or '',
                    'actividad_economica_id': cliente.actividad_economica.id if cliente.actividad_economica else None,
                    'actividad_economica_nombre': cliente.actividad_economica.descripcion if cliente.actividad_economica else '',
                    'ciudad_id': cliente.ciudad_id_004.id if cliente.ciudad_id_004 else None,
                    'ciudad_nombre': cliente.ciudad_id_004.nombre if cliente.ciudad_id_004 else '',
                    'estado_id': cliente.estado_id_001.id if cliente.estado_id_001 else None,
                    'estado_nombre': cliente.estado_id_001.nombre if cliente.estado_id_001 else '',
                    'logo_url': cliente.logo.url if cliente.logo else None,
                    'periodicidad_pago': cliente.periodicidad_pago or '',
                    'fecha_creacion': cliente.fecha_creacion.strftime('%Y-%m-%d') if hasattr(cliente, 'fecha_creacion') and cliente.fecha_creacion else None,
                    'fecha_actualizacion': cliente.fecha_actualizacion.strftime('%Y-%m-%d') if hasattr(cliente, 'fecha_actualizacion') and cliente.fecha_actualizacion else None
                }
            })
        else:
            # Cliente no encontrado
            return JsonResponse({
                'success': False,
                'message': 'Cliente no encontrado con el NIT proporcionado',
                'cliente': None
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Error en el formato de datos JSON',
            'cliente': None
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error interno del servidor: {str(e)}',
            'cliente': None
        })

@login_required
@validar_permisos('acceso_admin')
@csrf_exempt
@require_http_methods(["POST"])
def verificar_asignacion_cliente(request):
    """
    API para verificar si un cliente ya está asignado a un cliente maestro
    """
    try:
        data = json.loads(request.body)
        cliente_id = data.get('cliente_id')
        cliente_maestro_id = data.get('cliente_maestro_id')
        
        if not cliente_id or not cliente_maestro_id:
            return JsonResponse({
                'success': False,
                'message': 'Se requieren los IDs del cliente y cliente maestro',
                'ya_asignado': False
            })
        
        # Verificar si ya existe una asignación activa
        asignacion_existente = Cli064AsignacionCliente.objects.filter(
            id_cliente_asignado_id=cliente_id,
            id_cliente_maestro_id=cliente_maestro_id,
            estado__id=1  # Estado activo
        ).first()
        
        return JsonResponse({
            'success': True,
            'ya_asignado': asignacion_existente is not None,
            'message': 'Cliente ya asignado' if asignacion_existente else 'Cliente no asignado'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Error en el formato de datos JSON',
            'ya_asignado': False
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error interno del servidor: {str(e)}',
            'ya_asignado': False
        })
