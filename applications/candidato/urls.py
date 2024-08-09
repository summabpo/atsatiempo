from django.urls import path
from .views import views, CandidatoView

url_principal = 'candidato/'

urlpatterns = [
    path('', views.InicioView.as_view(), name='inicio'),
    path( url_principal+'crear', views.candidato_crear, name='candidato_crear'),
    path( url_principal+'listar', views.ListadoCandidato.as_view(), name='candidato_listar'),
    # path( url_principal+'editar/<int:pk>/', views.candidato_crear, name='candidato_editar'),
    path( url_principal+'editar/<int:pk>/', CandidatoView.candidato_mostrar, name='candidato_editar'),
    path( url_principal+'experiencia/crear/<int:candidato_id>/', views.experiencia_crear, name='experiencia_crear'),
    path( url_principal+'experiencia/listar/<int:candidato_id>/', views.experiencia_listar, name='experiencia_listar'),
    path( url_principal+'estudio/crear/<int:candidato_id>/', views.estudio_crear, name='estudio_crear'),
    path( url_principal+'estudio/listar/<int:candidato_id>/', views.estudio_listar, name='estudio_listar'),
    path( url_principal+'ajax/obtener_estudio/', CandidatoView.obtener_estudio_view, name='ajax_obtener_estudio'),
    path( url_principal+'ajax/obtener_laboral/', CandidatoView.obtener_laboral_view, name='ajax_obtener_laboral'),
    path( url_principal+'script/crear_habilidad/', CandidatoView.obtener_laboral_view, name='script_crear_habilidad'),
]