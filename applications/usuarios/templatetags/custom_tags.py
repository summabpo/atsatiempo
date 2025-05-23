from django import template

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