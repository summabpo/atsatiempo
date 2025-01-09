from django.urls import path
from .views import views, CandidatoView , LaboralView, EstudioView, HabilidadView


url_principal = 'candidato/'

urlpatterns = [
    path( url_principal+'crear', views.candidato_crear, name='candidato_crear'),
    # path( url_principal+'listar', views.ListadoCandidato.as_view(), name='candidato_listar'),
    path( url_principal+'listar', CandidatoView.candidatos_listar, name='candidato_listar'),

    path( url_principal+'academica/<int:pk>/', EstudioView.estudio_mostrar, name='candidato_academica'),
    path( url_principal+'academica/api/', EstudioView.estudio_api,name='estudio_api'),

    path( url_principal+'laboral/<int:pk>/', LaboralView.laboral_mostrar, name='candidato_laboral'),
    path( url_principal+'laboral/api/', LaboralView.laboral_api, name='laboral_api'),

    path( url_principal+'candidato/habilidades/<int:pk>/', HabilidadView.habilidad_obtener, name='candidato_habilidad'),
    path('limpiar_lisskill', HabilidadView.limpiar_lisskill, name='limpiar_lisskill'),
    path( url_principal+'eliminar_habilidad/', HabilidadView.habilidad_eliminar, name='habilidad_eliminar'),
    path( url_principal+'eliminar_habilidad/<int:pk> <int:candidato_id>', HabilidadView.habilidad_eliminar_id, name='habilidad_eliminar_id'),
    # path( url_principal+'pruebas', pruebas.pruebas, name='pruebas'),

    # path( url_principal+'editar/<int:pk>/', views.candidato_crear, name='candidato_editar'),
    path( url_principal+'editar/<int:pk>/', CandidatoView.candidato_mostrar, name='candidato_editar'),
    path( url_principal+'experiencia/crear/<int:candidato_id>/', views.experiencia_crear, name='experiencia_crear'),
    path( url_principal+'experiencia/listar/<int:candidato_id>/', views.experiencia_listar, name='experiencia_listar'),
    path( url_principal+'estudio/crear/<int:candidato_id>/', views.estudio_crear, name='estudio_crear'),
    path( url_principal+'estudio/listar/<int:candidato_id>/', views.estudio_listar, name='estudio_listar'),
    path( url_principal+'ajax/obtener_estudio/', CandidatoView.obtener_estudio_view, name='ajax_obtener_estudio'),
    path( url_principal+'ajax/obtener_laboral/', CandidatoView.obtener_laboral_view, name='ajax_obtener_laboral'),
    path( url_principal+'script/crear_habilidad/', CandidatoView.habilidades_crear, name='script_crear_habilidad'),
]