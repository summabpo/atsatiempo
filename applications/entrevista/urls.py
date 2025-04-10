from django.urls import path
from applications.entrevista.views import client_views

url_principal = 'entrevista/'

urlpatterns = [
    path( url_principal+'gestionar/<int:pk>/', client_views.management_interview, name='entrevistar_gestionar_cliente'),
]