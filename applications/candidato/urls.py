from django.urls import path
from . import views

url_principal = 'candidato/'

urlpatterns = [
    path('', views.InicioView.as_view(), name='inicio'),
    path( url_principal+'crear', views.candidato_crear, name='candidato_crear'),
    path( url_principal+'listar', views.ListadoCandidato.as_view(), name='candidato_listar'),
    path( url_principal+'editar/<int:pk>/', views.candidato_crear, name='candidato_editar'),
]