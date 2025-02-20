from django.urls import path
from applications.cliente.views import  ClienteView, CreacionUsuariosView
from applications.cliente.views.preguntasView import PreguntasView

#vistas del usuario administrador ATS
from .views.usuario_admin import ClienteAdminView

url_principal = 'cliente/'

urlpatterns = [
    #new
    path( url_principal+'/', ClienteView.cliente_crear, name='cliente_crear'),




    path( url_principal+'crear', ClienteView.cliente_crear, name='cliente_crear'),
    path( url_principal+'grupo_trabajo', CreacionUsuariosView.usuario_interno, name='usuarios_internos_listar'),
    path( url_principal+'ajax/obtener_cliente/', ClienteView.obtener_cliente_view, name='ajax_obtener_cliente'),

    # Administrador ATS
    # Modulos Globales
    path( url_principal+'listar', ClienteAdminView.cliente_listar, name='cliente_listar'),
    path( url_principal+'reclutado_todos', ClienteAdminView.reclutados_todos, name='cliente_vacante_reclutado_todos'),
    path( url_principal+'vacantes_todos/', ClienteAdminView.vacantes_todos, name='vacantes_cliente_todas'),
    
    # Detalles Cliente
    path( url_principal+'detalle/<int:pk>/', ClienteAdminView.cliente_detalle, name='cliente_detalle'),
    path( url_principal+'vacante/<int:pk>/', ClienteAdminView.cliente_vacante, name='cliente_vacante'),
    path( url_principal+'grupo_trabajo/<int:pk>/', ClienteAdminView.cliente_grupo_trabajo, name='cliente_grupo_trabajo'),
    
    # Detalles Vacante
    path( url_principal+'vacante/detalle/<int:pk>/', ClienteAdminView.cliente_vacante_detalle, name='cliente_vacante_detalle'),
    path( url_principal+'vacante/reclutado/<int:pk>/', ClienteAdminView.cliente_vacante_reclutado, name='cliente_vacante_reclutado'),
    path( url_principal+'vacante/entrevista/<int:pk>/', ClienteAdminView.cliente_vacante_entrevista, name='cliente_vacante_entrevista'),
    path( url_principal+'vacante/editar/<int:pk>/', ClienteAdminView.cliente_vacante_editar, name='cliente_vacante_editar'),
    path( url_principal+'vacante/emparejamiento/<int:pk>/', ClienteAdminView.cliente_vacante_emparejamiento_vacante, name='cliente_vacante_emparejamiento_vacante'),

    # Preguntas Cuestionario
    path( url_principal+'ver_preguntas/', PreguntasView.ver_preguntas_cliente, name='ver_preguntas_cliente'),
]