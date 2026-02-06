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
    Estructura esperada: {"tipo": "HF", "bloques": [{"bloque": 1, "dia_inicio": "L", "dia_final": "S", "hora_inicio": "06:00:00", "hora_final": "15:00:00"}]}
    """
    if not value:
        return {'tipo': None, 'tipo_display': None, 'bloques': []}
    
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
        
        # Mapeo de tipo de horario
        tipo_horario_map = {
            'HF': 'Horario Fijo',
            'HX': 'Horario Flexible',
            'HR': 'Horario Rotativo',
        }
        
        # Si es un string JSON, parsearlo
        if isinstance(value, str):
            data = json.loads(value)
        else:
            data = value
        
        # Si es un diccionario con estructura {"tipo": "...", "bloques": [...]}
        if isinstance(data, dict):
            tipo = data.get('tipo', '')
            bloques_data = data.get('bloques', [])
            
            bloques = []
            for bloque in bloques_data:
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
            
            return {
                'tipo': tipo,
                'tipo_display': tipo_horario_map.get(tipo, tipo),
                'bloques': bloques
            }
        
        # Si es una lista (estructura antigua), mantener compatibilidad
        if isinstance(data, list):
            bloques = []
            for bloque in data:
                if isinstance(bloque, dict):
                    dia_inicio = dias_abreviados.get(bloque.get('dia_inicio', ''), bloque.get('dia_inicio', ''))
                    dia_final = dias_abreviados.get(bloque.get('dia_final', ''), bloque.get('dia_final', ''))
                    
                    hora_inicio = bloque.get('hora_inicio', '')
                    if hora_inicio and len(hora_inicio) > 5:
                        hora_inicio = hora_inicio[:5]
                    
                    hora_final = bloque.get('hora_final', '')
                    if hora_final and len(hora_final) > 5:
                        hora_final = hora_final[:5]
                    
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
            
            return {
                'tipo': None,
                'tipo_display': None,
                'bloques': bloques
            }
        
        return {'tipo': None, 'tipo_display': None, 'bloques': []}
    except (json.JSONDecodeError, TypeError, AttributeError):
        return {'tipo': None, 'tipo_display': None, 'bloques': []}

@register.filter(name='get_match_porcentaje')
def get_match_porcentaje(json_match):
    """
    Filtro para obtener el porcentaje_total del match desde json_match
    Maneja tanto si es un diccionario como si es un string JSON
    """
    if not json_match:
        return None
    
    try:
        # Si es un string JSON, parsearlo
        if isinstance(json_match, str):
            data = json.loads(json_match)
        else:
            data = json_match
        
        # Acceder al porcentaje_total
        if isinstance(data, dict) and 'resumen' in data:
            resumen = data.get('resumen', {})
            if isinstance(resumen, dict) and 'porcentaje_total' in resumen:
                return resumen.get('porcentaje_total')
        
        return None
    except (json.JSONDecodeError, TypeError, AttributeError):
        return None

@register.filter(name='get_tipo_horario_display')
def get_tipo_horario_display(value):
    """
    Filtro para obtener el nombre del tipo de horario desde su código
    """
    tipo_horario_map = {
        'HF': 'Horario Fijo',
        'HX': 'Horario Flexible',
        'HR': 'Horario Rotativo',
    }
    return tipo_horario_map.get(value, value)

@register.filter(name='parse_idiomas')
def parse_idiomas(value):
    """
    Filtro para parsear el JSON de idiomas
    Estructura esperada: [{"bloque": 1, "idioma": "ES", "nivel": "B1", "nivel_idioma": "1"}, ...]
    """
    if not value:
        return []
    
    try:
        # Mapeo de códigos de idioma a nombres
        idiomas_map = {
            'ES': 'Español',
            'EN': 'Inglés',
            'FR': 'Francés',
            'DE': 'Alemán',
            'IT': 'Italiano',
            'PT': 'Portugués',
            'RU': 'Ruso',
            'ZH': 'Chino',
            'JP': 'Japonés',
            'AR': 'Árabe',
        }
        
        # Mapeo de niveles de idioma
        niveles_map = {
            'A1': 'A1 - Principiante',
            'A2': 'A2 - Básico',
            'B1': 'B1 - Intermedio',
            'B2': 'B2 - Intermedio Alto',
            'C1': 'C1 - Avanzado',
            'C2': 'C2 - Nativo o Bilingüe',
        }
        
        # Si es un string JSON, parsearlo
        if isinstance(value, str):
            data = json.loads(value)
        else:
            data = value
        
        # Si es una lista, procesarla
        if isinstance(data, list):
            idiomas = []
            for idioma in data:
                if isinstance(idioma, dict):
                    codigo_idioma = idioma.get('idioma', '')
                    nombre_idioma = idiomas_map.get(codigo_idioma, codigo_idioma.upper())
                    nivel_codigo = idioma.get('nivel', '') or idioma.get('nivel_idioma', '')
                    nivel_display = niveles_map.get(nivel_codigo, nivel_codigo)
                    tiene_certificado = idioma.get('nivel_idioma', '') == '1' or idioma.get('certificado', False)
                    
                    if codigo_idioma:
                        idiomas.append({
                            'idioma': codigo_idioma,
                            'nombre': nombre_idioma,
                            'nivel': nivel_display if nivel_display else nivel_codigo,
                            'certificado': tiene_certificado
                        })
            return idiomas
        
        return []
    except (json.JSONDecodeError, TypeError, AttributeError):
        return []

@register.filter(name='parse_estudios_complementarios')
def parse_estudios_complementarios(value):
    """
    Filtro para parsear el JSON de estudios complementarios
    Estructura esperada: [{"estudio": "...", "certificado": true/false}, ...]
    """
    if not value:
        return []
    
    try:
        # Si es un string JSON, parsearlo
        if isinstance(value, str):
            data = json.loads(value)
        else:
            data = value
        
        # Si es una lista, procesarla
        if isinstance(data, list):
            estudios = []
            for estudio in data:
                if isinstance(estudio, dict):
                    nombre_estudio = estudio.get('estudio', '') or estudio.get('nombre', '')
                    certificado = estudio.get('certificado', False) or estudio.get('certificado_estudios_complementarios', False)
                    
                    # Normalizar certificado (puede venir como string "True"/"False" o boolean)
                    if isinstance(certificado, str):
                        certificado = certificado.lower() in ['true', '1', 'si', 'sí', 'yes']
                    elif certificado is None:
                        certificado = False
                    
                    if nombre_estudio:
                        estudios.append({
                            'estudio': nombre_estudio,
                            'certificado': certificado
                        })
            return estudios
        
        return []
    except (json.JSONDecodeError, TypeError, AttributeError):
        return []

@register.filter(name='extract_vacancy_sections')
def extract_vacancy_sections(description):
    """
    Filtro para extraer secciones específicas de la descripción de la vacante
    Devuelve una lista de diccionarios con 'title' y 'items'
    """
    if not description:
        return []
    
    sections_to_extract = [
        'FUNCIONES Y RESPONSABILIDADES',
        'EXPERIENCIA REQUERIDA',
        'PERFIL ACADÉMICO',
        'ESTUDIOS COMPLEMENTARIOS',
        'IDIOMAS',
        'HORARIO DE TRABAJO'
    ]
    
    unwanted_sections = [
        'INFORMACIÓN DEL CARGO',
        'COMPETENCIAS Y HABILIDADES',
        'FIT CULTURAL',
        'OFERTA SALARIAL',
        'ÚNETE A NUESTRO EQUIPO',
        'OPORTUNIDAD LABORAL'
    ]
    
    lines = description.split('\n')
    extracted_sections = []
    current_section = None
    current_items = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Verificar si es un título de sección deseada
        is_desired_section = False
        for section_title in sections_to_extract:
            if section_title in line:
                # Guardar sección anterior si existe
                if current_section:
                    extracted_sections.append({
                        'title': current_section,
                        'items': current_items
                    })
                # Iniciar nueva sección
                current_section = line
                current_items = []
                is_desired_section = True
                break
        
        # Verificar si es una sección no deseada
        if not is_desired_section:
            is_unwanted_section = False
            for unwanted in unwanted_sections:
                if unwanted in line and len(line) < 100:
                    is_unwanted_section = True
                    break
            
            if is_unwanted_section and current_section:
                # Guardar sección actual y terminar
                extracted_sections.append({
                    'title': current_section,
                    'items': current_items
                })
                current_section = None
                current_items = []
            elif current_section and not is_desired_section:
                # Agregar item a la sección actual
                # Limpiar el bullet point si existe
                item = line.lstrip('•').lstrip('-').strip()
                if item:
                    current_items.append(item)
    
    # Agregar última sección si existe
    if current_section:
        extracted_sections.append({
            'title': current_section,
            'items': current_items
        })
    
    return extracted_sections 