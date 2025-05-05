from django.urls import path
from applications.entrevista.views import client_views, client_analyst_internal_views

url_principal = 'entrevista/'

urlpatterns = [
    #client_user
    path( url_principal+'gestionar/<int:pk>/', client_views.management_interview, name='entrevistar_gestionar_cliente'),
    path( url_principal+'listado/cliente/', client_views.interview_list, name='entrevistas_listado_cliente'),

    #client_analyst_user
    path( url_principal+'gestionar/analista/<int:pk>/', client_analyst_internal_views.management_interview, name='entrevistar_gestionar_analista_interno'),
    path( url_principal+'listado/<int:pk>/', client_analyst_internal_views.interview_list, name='entrevistar_listado_analista_interno'),
    

]