from django.urls import path
from .views import PruebasView
from applications.common.views.base import BaseView

url_principal = 'pruebas/'

urlpatterns = [

    path( url_principal+'base_grid', BaseView.base_grid, name='base_grid'),
    path( url_principal+'listado_simple', PruebasView.ListadoSimpleListView.as_view(), name='listado'),
    path( url_principal+'listado_exportar', PruebasView.ListadoExportarListView.as_view(), name='listado'),
    path( url_principal+'texto_sugerido', PruebasView.PruebaTextoSugerido, name='listado'),
    path( url_principal+'api/prueba_texto_sugerido', PruebasView.sugerir_habilidades, name='habilidad_sugerida'),
    # path( url_principal+'test', PruebasView.sugerir_habilidades, name='test')
]