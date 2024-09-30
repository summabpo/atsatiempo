from django.urls import path
from .views import VacanteViews, EntrevistaView


url_principal = 'vacante/'

urlpatterns = [
    path( url_principal+'api/', VacanteViews.vacante_api, name='vacante_api'),
    path( url_principal+'cliente/<int:pk>/', VacanteViews.vacante_cliente_mostrar, name='vacantes_cliente'),
    path( url_principal+'cliente_todos/', VacanteViews.ver_vacante_cliente_todos, name='vacantes_cliente_todas'),
    path( url_principal+'cliente/', VacanteViews.ver_vacante_cliente, name='vacantes'),
    path( url_principal+'detalle_vacante/<int:pk>/', VacanteViews.vacante_detalle, name='vacante_detalle'),
    path( url_principal+'aplicacion_vacante/<int:pk>/', VacanteViews.vacante_aplicada, name='vacante_aplicada'),
    path( url_principal+'vacante_aplicadas/', VacanteViews.ver_vacante_candidato_aplicadas, name='vacante_candidato'),
    path( url_principal+'gestion/<int:pk>/', VacanteViews.vacante_gestion, name='vacante_gestion'),
    
    #Entrevistas
    path( url_principal+'entrevista', EntrevistaView.ver_entrevista_todos, name='ver_entrevista_todos'),
    path( url_principal+'crear_entrevista/<int:asignacion_id>/', EntrevistaView.crear_entrevista, name='crear_entrevista'),
    
]