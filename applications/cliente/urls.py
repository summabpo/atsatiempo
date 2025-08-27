from django.urls import path
from applications.cliente.views import  ClienteView, CreacionUsuariosView
from applications.cliente.views import admin_views, client_views, common_views
from applications.cliente.views.preguntasView import PreguntasView

#vistas del usuario administrador ATS
from .views.usuario_admin import ClienteAdminView

url_principal = 'cliente/'

urlpatterns = [
    #new
    #admin_user
    path( url_principal+'crear/', admin_views.crear_cliente, name='cliente_crear'),
    path( url_principal+'listar/', admin_views.ver_cliente, name='cliente_ver'),
    path( url_principal+'detalle/<int:pk>/', admin_views.client_detail, name='cliente_detalle'),
    path( url_principal+'detalle/informacion/<int:pk>/', admin_views.client_detail_info, name='cliente_info'),
    path( url_principal+'detalle/politicas/<int:pk>/', admin_views.client_detail_politics, name='cliente_politicas'),
    path( url_principal+'detalle/pruebas/<int:pk>/', admin_views.client_detail_test, name='cliente_pruebas'),
    path( url_principal+'detalle/cargos/<int:pk>/', admin_views.client_detail_position, name='cliente_cargos'),
    path( url_principal+'detalle/requisitos/<int:pk>/', admin_views.client_detail_required, name='cliente_requisitos'),
    path( url_principal+'detalle/cargos/configuracion/<int:pk>/<int:cargo_id>/', admin_views.client_detail_position_config, name='cliente_cargos_configuracion'),
    path( url_principal+'detalle/grupo_trabajo/<int:pk>/', admin_views.client_detail_group_work, name='client_detail_group_work'),

    # APIs para modales de usuarios
    path( url_principal+'ajax/crear_usuario/', common_views.crear_usuario_modal, name='ajax_crear_usuario'),
    path( url_principal+'ajax/obtener_usuario/<int:pk>/', common_views.obtener_usuario_modal, name='ajax_obtener_usuario'),
    path( url_principal+'ajax/actualizar_usuario/<int:pk>/', common_views.actualizar_usuario_modal, name='ajax_actualizar_usuario'),
    path( url_principal+'ajax/cambiar_estado_usuario/<int:pk>/', common_views.cambiar_estado_usuario_modal, name='ajax_cambiar_estado_usuario'),
    path( url_principal+'ajax/obtener_grupos/', common_views.obtener_grupos_activos, name='ajax_obtener_grupos'),

    
    #client_user
    path( url_principal+'informacion_principal', client_views.client_detail_info, name='info_principal_cliente'),
    path( url_principal+'cargos', client_views.client_position, name='cargos_cliente'),
    path( url_principal+'cargos/detalle/<int:cargo_id>/', client_views.client_position_config, name='cargos_cliente_detalle'),
    path( url_principal+'pruebas', client_views.client_test, name='pruebas_cliente'),
    path( url_principal+'politicas', client_views.client_politics, name='politicas_cliente'),
    path( url_principal+'requisitos', client_views.client_required, name='requisitos_cliente'),

    # path( url_principal+'crear', ClienteView.cliente_crear, name='cliente_crear'),
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