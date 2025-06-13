from django.urls import path
from .views import VacanteViews, EntrevistaView, admin_views, client_views, client_analyst_views, client_analyst_internal_views, candidate_views
from applications.vacante.views.usuario_candidato import VacanteCandidatoView
from applications.vacante.views.usuario_cliente import VacanteClienteView



url_principal = 'vacante/'

urlpatterns = [

    #new
    #admin_user
    path( url_principal+'crear/', admin_views.create_vacanty, name='vacantes_crear'),
    path( url_principal+'listar/', admin_views.list_vacanty_all, name='vacantes_todas'),
    path( url_principal+'mis_vacantes/<int:pk>/', admin_views.list_vacanty_from_client, name='vacantes_propias'),
    path( url_principal+'mis_vacantes/crear/<int:pk>/', admin_views.create_vacanty_from_client, name='vacantes_crear_propias'),
    path( url_principal+'mis_vacantes/editar/<int:pk>/<int:vacante_id>/', admin_views.edit_vacanty_from_client, name='vacantes_editar_propias'),
    
    #client_user
    path( url_principal+'crear_vacante/', client_views.create_vacanty, name='vacantes_crear_cliente'),
    path( url_principal+'listado/', client_views.list_vacanty_all, name='vacantes_listado_cliente'),
    path( url_principal+'detalle/<int:pk>/', client_views.detail_vacancy, name='vacantes_detalle_cliente'),
    path( url_principal+'detalle/entrevistas/<int:pk>/', client_views.detail_vacancy_interview, name='vacantes_entrevista_cliente'),
    path( url_principal+'asignar_analista/<int:pk>/', client_views.detail_vacancy_assign, name='vacantes_asignar_analista_cliente'),

    #client_analyst_user
    path( url_principal+'asignadas/', client_analyst_views.list_assigned_vacancies, name='vacantes_asignadas'),

    #client_analyst_internal_user
    path( url_principal+'asignadas/analista', client_analyst_internal_views.list_assigned_vacancies, name='vacantes_asignadas_analista_interno'),
    path( url_principal+'gestion/analista/<int:pk>/', client_analyst_internal_views.detail_vacancy, name='vacantes_gestion_analista_interno'),

    #client_candidate_user
    path( url_principal+'aplicadas/candidato/', candidate_views.apply_vacancy, name='vacante_candidato_aplicadas'),
    path( url_principal+'aplicadas/detalle/<int:pk>', candidate_views.apply_vacancy_detail, name='vacante_candidato_aplicadas_detalle'),
    path( url_principal+'disponibles/', candidate_views.vacancy_available, name='vacante_candidato_disponibles'),










    #Vacante New
    path( url_principal+'buscar/', VacanteViews.find_vacanty, name='find_vacanty'),

    path( url_principal+'', VacanteViews.buscar_vacante, name='buscar_vacante'),
    path( url_principal+'emparejamiento/<int:candidato_id>/<int:vacante_id>/', VacanteViews.vacante_candidato_emparejamiento, name='vacante_candidato_emparejamiento'),
    
    path( url_principal+'api/', VacanteViews.vacante_api, name='vacante_api'),
    path( url_principal+'cliente/<int:pk>/', VacanteViews.vacante_cliente_mostrar, name='vacantes_cliente'),
    
    path( url_principal+'detalle_vacante/<int:pk>/', VacanteViews.vacante_detalle, name='vacante_detalle'),
    path( url_principal+'aplicacion_vacante/<int:pk>/', VacanteViews.vacante_aplicada, name='vacante_aplicada'),
    
    #Entrevistas
    path( url_principal+'entrevista/', EntrevistaView.ver_entrevista_todos, name='ver_entrevista_todos'),
    
    path( url_principal+'entrevista/entrevistador', EntrevistaView.ver_entrevista_entrevistador, name='ver_entrevista_entrevistador'),
    path( url_principal+'crear_entrevista/<int:asignacion_id>/', EntrevistaView.crear_entrevista, name='crear_entrevista'),
    
    #Candidato
    path( url_principal+'disponibles/', VacanteCandidatoView.ver_vacante_disponibles, name='ver_vacantes_disponibles'),
    path( url_principal+'vacante_aplicadas/', VacanteViews.ver_vacante_candidato_aplicadas, name='vacante_candidato'),
    path( url_principal+'entrevista/candidato', EntrevistaView.ver_entrevista_candidato, name='ver_entrevista_candidato'),

    #Cliente
    #path( url_principal+'cliente/', VacanteViews.ver_vacante_cliente, name='vacantes'), #por suprimir
    path( url_principal+'cliente/', VacanteClienteView.vacantes_cliente, name='vacantes_cliente_todas'),
    path( url_principal+'gestion/<int:pk>/', VacanteViews.vacante_gestion, name='vacante_gestion'),
    path( url_principal+'gestion/reclutados/<int:pk>/', VacanteClienteView.gestion_vacante_reclutados, name='gestion_vacante_reclutados'),
    path( url_principal+'gestion/entrevistas/<int:pk>/', VacanteClienteView.gestion_vacante_entrevistas, name='gestion_vacante_entrevistas'),
    path( url_principal+'gestion/cancelar/<int:pk>/', VacanteClienteView.gestion_vacante_cancelar, name='gestion_vacante_cancelar'),
    path( url_principal+'gestion/entrevistas/calificar/<int:pk>/', VacanteClienteView.gestion_entrevista, name='gestion_entrevista'),
    path( url_principal+'gestion/editar/<int:pk>/', VacanteClienteView.gestion_vacante_editar, name='gestion_vacante_editar'),

    #api
    path( url_principal+'api/mostrar_entrevistas_calendario/', EntrevistaView.obtener_entrevistas, name='gestion_vacante_editar'),
]