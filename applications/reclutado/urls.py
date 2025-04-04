from django.urls import path
from applications.reclutado.views import client_views


url_principal = 'reclutado/'

urlpatterns = [
    #client_user
    path( url_principal+'listado/<int:pk>/', client_views.detail_vacancy_recruited, name='vacantes_reclutados_cliente'),
]