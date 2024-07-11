from django.urls import path
from . import views

urlpatterns = [
    path('crear_cliente', views.cliente_crear, name='crear_cliente'),
]