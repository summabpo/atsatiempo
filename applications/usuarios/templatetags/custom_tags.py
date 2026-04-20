from django import template
import json
import re
from datetime import date

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


URLS_USUARIOS = [
    'usuarios_listar',
    'usuarios_candidatos',
    'usuarios_internos',
    'usuario_candidato_detalle',
]


@register.filter(name='is_active_url_usuarios')
def is_active_url_usuarios(url_name):
    return url_name in URLS_USUARIOS


# Define una lista global de rutas activas
URLS_VACANTES_CLIENTE  = [
    'vacantes_detalle_cliente',
    'vacantes_reclutados_cliente',
    'vacantes_entrevista_cliente',
    'vacantes_asignar_analista_cliente',
    'vacantes_gestion_propias_cliente',
    'vacantes_gestion_propias_cliente_2',
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
    'vacantes_detalle_cliente',
    'vacantes_entrevista_cliente',
    'vacantes_asignar_analista_cliente',
    'entrevistar_gestionar_analista_interno',
    'reclutados_analista_interno',
    'reclutados_detalle_analista_interno',
    'entrevistar_listado_analista_interno',
]

@register.filter(name='is_active_url_analista_interno_vacante')
def is_active_url_analista_interno_vacante(url_name):
    return url_name in URLS_VACANTES_ANALISTA

@register.filter(name='edad_desde_fecha')
def edad_desde_fecha(fecha_nacimiento):
    """
    Calcula la edad en años a partir de una fecha de nacimiento.
    """
    if not fecha_nacimiento:
        return None
    try:
        hoy = date.today()
        edad = hoy.year - fecha_nacimiento.year
        if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
            edad -= 1
        return edad
    except (TypeError, AttributeError):
        return None


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

def _extraer_nombre_profesion(item):
    """Extrae el nombre de una profesión desde un item (dict o string)."""
    if isinstance(item, str):
        return item.strip() if item.strip() else None
    if isinstance(item, dict):
        nombre = item.get('value') or item.get('name') or item.get('nombre') or item.get('label')
        if nombre:
            return str(nombre).strip() if str(nombre).strip() else None
    return None


@register.filter(name='parse_profesiones_json')
def parse_profesiones_json(value):
    """
    Filtro para parsear el JSON de profesiones y extraer los nombres.
    Soporta: [{"value":"X","id":9}], [{"name":"X"}], ["X"], etc.
    """
    if not value:
        return []
    
    try:
        data = value
        if isinstance(value, str):
            value_stripped = value.strip()
            if not value_stripped:
                return []
            data = json.loads(value_stripped)
        
        if not isinstance(data, list):
            return []
        
        resultado = []
        for item in data:
            if isinstance(item, (str, int, float)):
                nombre = str(item).strip() if str(item).strip() else None
            else:
                nombre = _extraer_nombre_profesion(item)
            if nombre:
                resultado.append(nombre)
        return resultado
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
                'tipo': None,
                'tipo_display': None,
                'bloques': bloques
            }
        
        return {'tipo': None, 'tipo_display': None, 'bloques': []}
    
    except (json.JSONDecodeError, TypeError, AttributeError):
        return {'tipo': None, 'tipo_display': None, 'bloques': []}

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Obtener un elemento de un diccionario por su clave"""
    if isinstance(dictionary, dict):
        return dictionary.get(str(key))
    return None

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

@register.filter(name='get_match_inicial_porcentaje')
def get_match_inicial_porcentaje(json_match_inicial):
    """
    Filtro para obtener el total del match inicial desde json_match_inicial.ponderaciones.total
    Maneja tanto si es un diccionario como si es un string JSON
    """
    if not json_match_inicial:
        return None
    
    try:
        # Si es un string JSON, parsearlo
        if isinstance(json_match_inicial, str):
            data = json.loads(json_match_inicial)
        else:
            data = json_match_inicial
        
        # Acceder al total desde ponderaciones
        if isinstance(data, dict) and 'ponderaciones' in data:
            ponderaciones = data.get('ponderaciones', {})
            if isinstance(ponderaciones, dict) and 'total' in ponderaciones:
                return ponderaciones.get('total')
        
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
    Filtro para extraer secciones específicas de la descripción de la vacante.
    Devuelve una lista de diccionarios con 'title' y 'items' en este orden:
    formación, experiencia, funciones, idioma, horarios, salario.
    """
    if not description:
        return []
    
    # Orden de visualización: formación → experiencia → funciones → idioma → horarios → salario
    display_order = [
        'PERFIL ACADÉMICO',
        'ESTUDIOS COMPLEMENTARIOS',
        'EXPERIENCIA REQUERIDA',
        'FUNCIONES Y RESPONSABILIDADES',
        'IDIOMAS',
        'HORARIO DE TRABAJO',
        'OFERTA SALARIAL',
    ]
    
    sections_to_extract = list(display_order)
    
    unwanted_sections = [
        'INFORMACIÓN DEL CARGO',
        'COMPETENCIAS Y HABILIDADES',
        'FIT CULTURAL',
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
    
    # Ordenar según display_order (formación, experiencia, funciones, idioma, horarios, salario)
    def section_sort_key(s):
        title = s.get('title', '')
        for i, ordered in enumerate(display_order):
            if ordered in title:
                return i
        return len(display_order)
    
    extracted_sections.sort(key=section_sort_key)
    return extracted_sections


# Encabezados de sección que ya se muestran en otras tarjetas de la ficha (presentación vacante).
_DESCRIPCION_DROP_HEADER_MAX = 120

# Subcadenas que identifican inicio de una sección a omitir en la descripción (título corto tipo encabezado).
def _line_starts_drop_descripcion_section(ls):
    if not ls or len(ls) >= _DESCRIPCION_DROP_HEADER_MAX:
        return False
    u = ls.upper()
    if 'FUNCIONES' in u and 'RESPONSABILIDADES' in u:
        return True
    if 'EXPERIENCIA' in u and 'REQUERIDA' in u:
        return True
    if 'PERFIL' in u and 'ACAD' in u:
        return True
    if 'HORARIO' in u and 'TRABAJO' in u:
        return True
    if 'IDIOMAS' in u:
        return True
    if 'ESTUDIOS' in u and 'COMPLEMENTAR' in u:
        return True
    return False


# Encabezados de sección que sí deben mostrarse en la descripción (fin de un bloque omitido).
# Nota: "Estudios complementarios" no va aquí: se omiten en texto porque tienen tarjeta propia en la ficha.
_DESCRIPCION_KEEP_MARKERS = (
    'OPORTUNIDAD LABORAL',
    'INFORMACIÓN DEL CARGO',
    'COMPETENCIAS Y HABILIDADES',
    'FIT CULTURAL',
)


def _line_starts_keep_descripcion_section(ls):
    if not ls or len(ls) >= _DESCRIPCION_DROP_HEADER_MAX:
        return False
    return any(m in ls for m in _DESCRIPCION_KEEP_MARKERS)


def _drop_descripcion_secciones_duplicadas_ficha(text):
    """
    Quita bloques de la descripción que en la presentación ya tienen tarjeta propia
    (funciones, experiencia, perfil académico, horarios, idiomas, estudios complementarios).
    """
    if not text or not isinstance(text, str):
        return text
    lines = text.split('\n')
    out = []
    skip = False
    for line in lines:
        ls = line.strip()
        if not skip:
            if ls and _line_starts_drop_descripcion_section(ls):
                skip = True
                continue
            out.append(line)
        else:
            if ls and _line_starts_keep_descripcion_section(ls):
                skip = False
                out.append(line)
    return '\n'.join(out)


def _omitir_seccion_descripcion_por_titulo(ct_up):
    """ct_up: título de sección ya en mayúsculas (parser)."""
    if 'FUNCIONES' in ct_up and 'RESPONSABILIDADES' in ct_up:
        return True
    if 'EXPERIENCIA' in ct_up and 'REQUERIDA' in ct_up:
        return True
    if 'PERFIL' in ct_up and 'ACAD' in ct_up:
        return True
    if 'HORARIO' in ct_up and 'TRABAJO' in ct_up:
        return True
    if 'IDIOMAS' in ct_up:
        return True
    if 'ESTUDIOS' in ct_up and 'COMPLEMENTAR' in ct_up:
        return True
    return False


@register.filter(name='strip_funciones_descripcion')
def strip_funciones_descripcion(value):
    """Elimina de la descripción bloques que se muestran en otras secciones de la ficha (incl. estudios complementarios)."""
    return _drop_descripcion_secciones_duplicadas_ficha(value or '')


@register.filter(name='format_descripcion_vacante')
def format_descripcion_vacante(value):
    """
    Parsea la descripción de la vacante y devuelve secciones estructuradas con título e items.
    Convierte bullets (•) en listas y preserva la estructura para mejor visualización.
    """
    if not value or not isinstance(value, str):
        return []
    # Eliminar mensaje de invitación a postularse
    fragmentos = [
        "🎉 ¡ÚNETE A NUESTRO EQUIPO!", "¡ÚNETE A NUESTRO EQUIPO!",
        "Si cumples con el perfil descrito y estás interesado(a) en formar parte de nuestro equipo, "
        "te invitamos a postularte. Ofrecemos un ambiente de trabajo dinámico, oportunidades de "
        "crecimiento profesional y un equipo comprometido con la excelencia.",
        "📧 ¡Esperamos tu postulación!", "¡Esperamos tu postulación!",
    ]
    text = value
    for frag in fragmentos:
        text = text.replace(frag, '')
    text = _drop_descripcion_secciones_duplicadas_ficha(text)
    lines_raw = [line.strip() for line in text.split('\n') if line.strip()]
    text = '\n'.join(lines_raw)
    if not text:
        return []

    # Secciones conocidas. Varias se omiten en presentación (se muestran en otras tarjetas de la ficha; p. ej. estudios complementarios).
    section_markers = [
        'OPORTUNIDAD LABORAL',
        'INFORMACIÓN DEL CARGO',
        'FUNCIONES Y RESPONSABILIDADES',
        'EXPERIENCIA REQUERIDA',
        'PERFIL ACADÉMICO',
        'ESTUDIOS COMPLEMENTARIOS',
        'IDIOMAS',
        'HORARIO DE TRABAJO',
        'COMPETENCIAS Y HABILIDADES',
        'FIT CULTURAL',
    ]

    # Patrón para eliminar emojis al limpiar títulos
    emoji_pattern = re.compile(
        "["
        "\U0001F300-\U0001F9FF"  # Emojis
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )

    lines = text.split('\n')
    sections = []
    current_section = None
    current_items = []

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue

        # ¿Es un título de sección?
        is_section = False
        for marker in section_markers:
            if marker in line_stripped and len(line_stripped) < 120:
                if current_section:
                    sections.append({
                        'title': current_section,
                        'items': current_items
                    })
                # Limpiar emojis del título para mostrar
                clean_title = emoji_pattern.sub('', line_stripped).strip()
                if clean_title.endswith(':'):
                    clean_title = clean_title[:-1].strip()
                ct_up = clean_title.upper()
                if _omitir_seccion_descripcion_por_titulo(ct_up):
                    current_section = None
                    current_items = []
                    is_section = True
                    break
                current_section = clean_title
                current_items = []
                is_section = True
                break

        if not is_section and current_section:
            # Es un ítem de la sección actual
            item = line_stripped.lstrip('•').lstrip('-').strip()
            if item:
                current_items.append(item)

    if current_section:
        sections.append({
            'title': current_section,
            'items': current_items
        })

    return sections


@register.filter(name='remove_unete_equipo')
def remove_unete_equipo(value):
    """Elimina el mensaje de invitación a postularse para no mostrarlo al cliente."""
    if not value or not isinstance(value, str):
        return value
    # Fragmentos del mensaje a eliminar (pueden estar en líneas separadas)
    fragmentos = [
        "🎉 ¡ÚNETE A NUESTRO EQUIPO!",
        "¡ÚNETE A NUESTRO EQUIPO!",
        "Si cumples con el perfil descrito y estás interesado(a) en formar parte de nuestro equipo, "
        "te invitamos a postularte. Ofrecemos un ambiente de trabajo dinámico, oportunidades de "
        "crecimiento profesional y un equipo comprometido con la excelencia.",
        "📧 ¡Esperamos tu postulación!",
        "¡Esperamos tu postulación!",
    ]
    result = value
    for frag in fragmentos:
        result = result.replace(frag, '')
    # Limpiar líneas vacías múltiples y espacios extra
    lines = [line.strip() for line in result.split('\n') if line.strip()]
    result = '\n\n'.join(lines)
    return result.strip()