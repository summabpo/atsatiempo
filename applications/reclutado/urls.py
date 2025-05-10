from django.urls import path
from applications.reclutado.views import client_views, client_analyst_internal_views
from applications.reclutado.views import api_views


url_principal = 'reclutado/'

urlpatterns = [
    #client_user
    path( url_principal+'listado/<int:pk>/', client_views.detail_vacancy_recruited, name='vacantes_reclutados_cliente'),
    path( url_principal+'detalle/<int:pk>/', client_views.detail_recruited, name='reclutados_detalle_cliente'),

    #analyst_internal_user
    path( url_principal+'listado/analista/<int:pk>/', client_analyst_internal_views.detail_vacancy_recruited, name='reclutados_analista_interno'),
    path( url_principal+'gestion/<int:pk>/', client_analyst_internal_views.detail_recruited, name='reclutados_detalle_analista_interno'),


    #api
    path( url_principal+'api/buscar_candidato/', api_views.api_candidate_document, name='api_canidate_document' ),
    
]