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
def is_active_url(url_name):
    return url_name in URLS_CLIENTES


# Define una lista global de rutas activas
URLS_VACANTES = [
    'vacantes_detalle_cliente',
    'vacantes_reclutados_cliente',
    'vacantes_entrevista_cliente',
    'vacantes_asignar_analista_cliente',
    'vacantes_reclutados_cliente',
    'reclutados_detalle_cliente',
    'entrevistar_gestionar_cliente',

]

@register.filter(name='is_active_url_cliente_vacante')
def is_active_url(url_name):
    return url_name in URLS_VACANTES