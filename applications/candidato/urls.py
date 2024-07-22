from django.urls import path
from . import views

url_principal = 'candidato/'

urlpatterns = [
    path('', views.InicioView.as_view(), name='inicio'),
    path( url_principal+'crear', views.candidato_crear, name='candidato_crear'),
    path( url_principal+'listar', views.ListadoCandidato.as_view(), name='candidato_listar'),
    path( url_principal+'editar/<int:pk>/', views.candidato_crear, name='candidato_editar'),
    path( url_principal+'experiencia/crear/<int:candidato_id>/', views.experiencia_crear, name='experiencia_crear'),
    path( url_principal+'experiencia/listar/<int:candidato_id>/', views.experiencia_listar, name='experiencia_listar'),
    
]