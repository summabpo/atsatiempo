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
    'cliente_requisitos'
]

@register.filter(name='is_active_url_cliente_all')
def is_active_url(url_name):
    return url_name in URLS_CLIENTES