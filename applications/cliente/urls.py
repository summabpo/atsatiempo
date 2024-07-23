from django.urls import path
from . import views

url_principal = 'cliente/'

urlpatterns = [
    path( url_principal+'crear', views.cliente_crear, name='cliente_crear'),
    path( url_principal+'listar', views.ListadoClientes.as_view(), name='cliente_listar'),
]