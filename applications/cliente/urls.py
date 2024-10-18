from django.urls import path
from .views import  ClienteView, CreacionUsuariosView
from applications.cliente.views.preguntasView import PreguntasView

url_principal = 'cliente/'

urlpatterns = [
    path( url_principal+'crear', ClienteView.cliente_crear, name='cliente_crear'),
    path( url_principal+'listar', ClienteView.cliente_listar, name='cliente_listar'),
    path( url_principal+'grupo_trabajo', CreacionUsuariosView.usuario_interno, name='usuarios_internos_listar'),
    path( url_principal+'ajax/obtener_cliente/', ClienteView.obtener_cliente_view, name='ajax_obtener_cliente'),

    # Detalles Cliente
    path( url_principal+'detalle/<int:pk>/', ClienteView.cliente_detalle, name='cliente_detalle'),

    # Detalles Vacante
    path( url_principal+'vacante/<int:pk>/', ClienteView.cliente_vacante, name='cliente_vacante'),
    path( url_principal+'vacante/detalle/<int:pk>/', ClienteView.cliente_vacante_detalle, name='cliente_vacante_detalle'),
    # path( url_principal+'vacante/detalle/<int:pk>/', ClienteView.cliente_vacante_detalle, name='cliente_vacante_detalle'),
    path( url_principal+'vacante/reclutado/<int:pk>/', ClienteView.cliente_vacante_reclutado, name='cliente_vacante_reclutado'),

    # Preguntas Cuestionario
    path( url_principal+'ver_preguntas/', PreguntasView.ver_preguntas_cliente, name='ver_preguntas_cliente'),
]