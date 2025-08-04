from django import template
import json

register = template.Library()

# Define una lista global de rutas activas
URLS_CLIENTES = [
    'cliente_ver',
    'cliente_detalle',
    'cliente_info',
    'cliente_politicas',
    'cliente_pruebas',
    'cliente_cargos',
    'cliente_cargos_configuracion',
    'cliente_requisitos',
    'vacantes_propias',
    'vacantes_crear_propias',
    'vacantes_editar_propias',
]

@register.filter(name='is_active_url_cliente_all')
def is_active_url_cliente_all(url_name):
    return url_name in URLS_CLIENTES


# Define una lista global de rutas activas
URLS_VACANTES_CLIENTE  = [
    'vacantes_detalle_cliente',
    'vacantes_reclutados_cliente',
    'vacantes_entrevista_cliente',
    'vacantes_asignar_analista_cliente',
    'vacantes_reclutados_cliente',
    'reclutados_detalle_cliente',
    'entrevistar_gestionar_cliente',
    
]

@register.filter(name='is_active_url_cliente_vacante')
def is_active_url_cliente_vacante(url_name):
    return url_name in URLS_VACANTES_CLIENTE 


# Define una lista global de rutas activas
URLS_VACANTES_ANALISTA  = [
    'vacantes_gestion_analista_interno',
    'vacantes_asignadas_analista_interno',
    'entrevistar_gestionar_analista_interno',
    'reclutados_analista_interno',
    'reclutados_detalle_analista_interno',
    'entrevistar_listado_analista_interno',
]

@register.filter(name='is_active_url_analista_interno_vacante')
def is_active_url_analista_interno_vacante(url_name):
    return url_name in URLS_VACANTES_ANALISTA

@register.filter(name='format_number')
def format_number(value):
    """
    Filtro para formatear números con separadores de miles usando puntos
    Ejemplo: 1500000 -> 1.500.000
    """
    if value is None:
        return "0"
    
    try:
        # Convertir a entero y luego a string
        num = int(float(value))
        # Formatear con separadores de miles usando puntos
        return f"{num:,}".replace(",", ".")
    except (ValueError, TypeError):
        return str(value)

@register.filter(name='parse_profesiones_json')
def parse_profesiones_json(value):
    """
    Filtro para parsear el JSON de profesiones y extraer los nombres
    Ejemplo: [{"value":"Administración","id":9}] -> ["Administración"]
    """
    if not value:
        return []
    
    try:
        # Si ya es una lista, devolverla
        if isinstance(value, list):
            return [item.get('value', '') for item in value if isinstance(item, dict)]
        
        # Si es un string JSON, parsearlo
        if isinstance(value, str):
            data = json.loads(value)
            if isinstance(data, list):
                return [item.get('value', '') for item in data if isinstance(item, dict)]
        
        return []
    except (json.JSONDecodeError, TypeError, AttributeError):
        return []

@register.filter(name='parse_horarios_json')
def parse_horarios_json(value):
    """
    Filtro para parsear el JSON de horarios y extraer la información de bloques
    Ejemplo: [{"bloque": 1, "dia_inicio": "L", "dia_final": "V", "hora_inicio": "08:00:00", "hora_final": "17:00:00"}] 
    """
    if not value:
        return []
    
    try:
        # Mapeo de días abreviados a nombres completos
        dias_abreviados = {
            'L': 'Lunes',
            'M': 'Martes', 
            'X': 'Miércoles',
            'J': 'Jueves',
            'V': 'Viernes',
            'S': 'Sábado',
            'D': 'Domingo'
        }
        
        # Si ya es una lista, procesarla
        if isinstance(value, list):
            bloques = []
            for bloque in value:
                if isinstance(bloque, dict):
                    dia_inicio = dias_abreviados.get(bloque.get('dia_inicio', ''), bloque.get('dia_inicio', ''))
                    dia_final = dias_abreviados.get(bloque.get('dia_final', ''), bloque.get('dia_final', ''))
                    
                    # Formatear hora (quitar segundos si existen)
                    hora_inicio = bloque.get('hora_inicio', '')
                    if hora_inicio and len(hora_inicio) > 5:
                        hora_inicio = hora_inicio[:5]
                    
                    hora_final = bloque.get('hora_final', '')
                    if hora_final and len(hora_final) > 5:
                        hora_final = hora_final[:5]
                    
                    # Determinar el rango de días
                    if dia_inicio == dia_final:
                        rango_dias = dia_inicio
                    else:
                        rango_dias = f"{dia_inicio} - {dia_final}"
                    
                    bloques.append({
                        'bloque': bloque.get('bloque', ''),
                        'rango_dias': rango_dias,
                        'dia_inicio': dia_inicio,
                        'dia_final': dia_final,
                        'hora_inicio': hora_inicio,
                        'hora_final': hora_final
                    })
            return bloques
        
        # Si es un string JSON, parsearlo
        if isinstance(value, str):
            data = json.loads(value)
            if isinstance(data, list):
                return parse_horarios_json(data)
        
        return []
    except (json.JSONDecodeError, TypeError, AttributeError):
        return [] 