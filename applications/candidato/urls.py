from django.urls import path
from .views import views, CandidatoView , LaboralView, EstudioView, HabilidadView, candidate_views
from .views import api_views


url_principal = 'candidato/'

urlpatterns = [

    #all_users
    path( url_principal+'perfil/', candidate_views.candidate_info_perfil, name='candidato_perfil'),

    #candidate_user
    path( url_principal+'informacion/basica', candidate_views.candidate_info, name='candidato_info_personal'),
    path( url_principal+'informacion/academica', candidate_views.candidate_info_academy, name='candidato_info_academica'),
    path( url_principal+'informacion/laboral', candidate_views.candidate_info_job, name='candidato_info_laboral'),
    path( url_principal+'informacion/habilidades', candidate_views.candidate_info_skills, name='candidato_info_habilidades'),
    path( url_principal+'informacion/redes', candidate_views.candidate_info_social_network, name='candidato_info_redes'),
    
    path( url_principal+'informacion/academica/editar/<int:pk>', candidate_views.candidate_info_academy_edit, name='candidato_info_academica_editar'),
    path( url_principal+'informacion/laboral/editar/<int:pk>', candidate_views.candidate_info_job_edit, name='candidato_info_laboral_editar'),
    path( url_principal+'informacion/redes/editar/<int:pk>', candidate_views.candidate_info_social_network_edit, name='candidato_info_redes_editar'),
    
    path( url_principal+'informacion/skills/borrar/<int:pk>', candidate_views.candidate_info_skills_delete, name='candidato_info_habilidades_borrar'),
    path( url_principal+'informacion/redes/borrar/<int:pk>', candidate_views.canidate_info_social_network_delete, name='candidato_info_redes_borrar'),

    #apis
    path( url_principal+'informacion/skills/api/', api_views.api_suggestions_skills, name='api_sugerencias_habilidades'),

    # path( url_principal+'crear', views.candidato_crear, name='candidato_crear'),
    # # path( url_principal+'listar', views.ListadoCandidato.as_view(), name='candidato_listar'),
    # path( url_principal+'listar', CandidatoView.candidatos_listar, name='candidato_listar'),

    # path( url_principal+'academica/<int:pk>/', EstudioView.estudio_mostrar, name='candidato_academica'),
    # path( url_principal+'academica/api/', EstudioView.estudio_api,name='estudio_api'),

    # path( url_principal+'laboral/<int:pk>/', LaboralView.laboral_mostrar, name='candidato_laboral'),
    # path( url_principal+'laboral/api/', LaboralView.laboral_api, name='laboral_api'),

    # path( url_principal+'candidato/habilidades/<int:pk>/', HabilidadView.habilidad_obtener, name='candidato_habilidad'),
    # path('limpiar_lisskill', HabilidadView.limpiar_lisskill, name='limpiar_lisskill'),
    # path( url_principal+'eliminar_habilidad/', HabilidadView.habilidad_eliminar, name='habilidad_eliminar'),
    # path( url_principal+'eliminar_habilidad/<int:pk> <int:candidato_id>', HabilidadView.habilidad_eliminar_id, name='habilidad_eliminar_id'),
    # # path( url_principal+'pruebas', pruebas.pruebas, name='pruebas'),

    # # path( url_principal+'editar/<int:pk>/', views.candidato_crear, name='candidato_editar'),
    # path( url_principal+'editar/<int:pk>/', CandidatoView.candidato_mostrar, name='candidato_editar'),
    # path( url_principal+'experiencia/crear/<int:candidato_id>/', views.experiencia_crear, name='experiencia_crear'),
    # path( url_principal+'experiencia/listar/<int:candidato_id>/', views.experiencia_listar, name='experiencia_listar'),
    # path( url_principal+'estudio/crear/<int:candidato_id>/', views.estudio_crear, name='estudio_crear'),
    # path( url_principal+'estudio/listar/<int:candidato_id>/', views.estudio_listar, name='estudio_listar'),
    # path( url_principal+'ajax/obtener_estudio/', CandidatoView.obtener_estudio_view, name='ajax_obtener_estudio'),
    # path( url_principal+'ajax/obtener_laboral/', CandidatoView.obtener_laboral_view, name='ajax_obtener_laboral'),
    # path( url_principal+'script/crear_habilidad/', CandidatoView.habilidades_crear, name='script_crear_habilidad'),
]