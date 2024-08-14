from django.urls import path
from .views import  ClienteView

url_principal = 'cliente/'

urlpatterns = [
    path( url_principal+'crear', ClienteView.cliente_crear, name='cliente_crear'),
    path( url_principal+'listar', ClienteView.mostrar_clientes, name='cliente_listar'),
    path( url_principal+'ajax/obtener_cliente/', ClienteView.obtener_cliente_view, name='ajax_obtener_cliente'),
]