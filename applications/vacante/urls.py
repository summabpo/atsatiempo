from django.urls import path
from .views import VacanteViews


url_principal = 'vacante/'

urlpatterns = [
    path( url_principal+'cliente/<int:pk>/', VacanteViews.vacante_cliente_mostrar, name='vacantes_cliente'),
]