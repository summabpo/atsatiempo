from django.urls import path
from applications.entrevista.views import client_views, client_analyst_internal_views

url_principal = 'entrevista/'

urlpatterns = [
    #client_user
    path( url_principal+'gestionar/<int:pk>/', client_views.management_interview, name='entrevistar_gestionar_cliente'),

    #client_analyst_user
    path( url_principal+'gestionar/analista/<int:pk>/', client_analyst_internal_views.management_interview, name='entrevistar_gestionar_analista_interno'),

]