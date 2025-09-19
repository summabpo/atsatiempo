from django.urls import path
from applications.entrevista.views import client_views, client_analyst_internal_views, client_interviewer_views

url_principal = 'entrevista/'

urlpatterns = [
    #client_user
    path( url_principal+'gestionar/<int:pk>/', client_views.management_interview, name='entrevistar_gestionar_cliente'),
    path( url_principal+'listado/cliente/', client_views.interview_list, name='entrevistas_listado_cliente'),

    #client_analyst_user
    path( url_principal+'gestionar/analista/<int:pk>/', client_analyst_internal_views.management_interview, name='entrevistar_gestionar_analista_interno'),
    path( url_principal+'listado/<int:pk>/', client_analyst_internal_views.interview_list, name='entrevistar_listado_analista_interno'),

    #client_interviewer_user
    path( url_principal+'gestionar/entrevistador/<int:pk>/', client_interviewer_views.management_interview, name='entrevistar_gestionar_entrevistador'),
    path( url_principal+'listado/entrevistador/', client_interviewer_views.interview_list, name='entrevistas_listado_entrevistador'),
    

]