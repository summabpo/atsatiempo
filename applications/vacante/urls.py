from django.urls import path
from .views import VacanteViews, EntrevistaView
from applications.vacante.views.usuario_candidato import VacanteCandidatoView
from applications.vacante.views.usuario_cliente import VacanteClienteView


url_principal = 'vacante/'

urlpatterns = [
    path( url_principal+'', VacanteViews.buscar_vacante, name='buscar_vacante'),
    path( url_principal+'api/', VacanteViews.vacante_api, name='vacante_api'),
    path( url_principal+'cliente/<int:pk>/', VacanteViews.vacante_cliente_mostrar, name='vacantes_cliente'),
    
    path( url_principal+'detalle_vacante/<int:pk>/', VacanteViews.vacante_detalle, name='vacante_detalle'),
    path( url_principal+'aplicacion_vacante/<int:pk>/', VacanteViews.vacante_aplicada, name='vacante_aplicada'),
    
    
    
    #Entrevistas
    path( url_principal+'entrevista/', EntrevistaView.ver_entrevista_todos, name='ver_entrevista_todos'),
    path( url_principal+'entrevista/candidato', EntrevistaView.ver_entrevista_candidato, name='ver_entrevista_candidato'),
    path( url_principal+'entrevista/entrevistador', EntrevistaView.ver_entrevista_entrevistador, name='ver_entrevista_entrevistador'),
    path( url_principal+'crear_entrevista/<int:asignacion_id>/', EntrevistaView.crear_entrevista, name='crear_entrevista'),
    
    #Candidato
    path( url_principal+'disponibles/', VacanteCandidatoView.ver_vacante_disponibles, name='ver_vacantes_disponibles'),
    path( url_principal+'vacante_aplicadas/', VacanteViews.ver_vacante_candidato_aplicadas, name='vacante_candidato'),


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