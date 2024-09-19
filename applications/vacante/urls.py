from django.urls import path
from .views import VacanteViews


url_principal = 'vacante/'

urlpatterns = [
    path( url_principal+'cliente/<int:pk>/', VacanteViews.vacante_cliente_mostrar, name='vacantes_cliente'),
    path( url_principal+'cliente_todos/', VacanteViews.vacante_cliente_todas, name='vacantes_cliente_todas'),
    path( url_principal+'cliente/', VacanteViews.vacante_cliente, name='vacantes'),
    path( url_principal+'detalle_vacante/<int:pk>/', VacanteViews.vacante_detalle, name='vacante_detalle'),
    path( url_principal+'aplicacion_vacante/<int:pk>/', VacanteViews.vacante_aplicada, name='vacante_aplicada'),
]