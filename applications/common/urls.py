from django.urls import path
from .views import PruebasView

url_principal = 'pruebas/'

urlpatterns = [
    path( url_principal+'listado_simple', PruebasView.ListadoSimpleListView.as_view(), name='listado'),
    path( url_principal+'listado_exportar', PruebasView.ListadoExportarListView.as_view(), name='listado'),
]