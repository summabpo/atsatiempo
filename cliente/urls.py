from django.urls import path
from . import views

urlpatterns = [
    path('crear_cliente', views.cliente_crear, name='cliente_crear'),
    path('listar_cliente', views.ListadoClientes.as_view(), name='cliente_listar'),
]