from django.urls import path

from .views.usuariosInternosATS import CreacionUsuarioInternoView
from .views import client_views
from applications.common.views import PruebasView


#new
from applications.usuarios.views.user_login import loginView

urlpatterns = [
    #new
    path('test_template', PruebasView.test_template, name='test'),
    path('', loginView.principal, name='home'),
    path('login/', loginView.login_view, name='login'),
    path('registro/', loginView.registration, name='registration'),
    path('registro/empresa', loginView.company_registration, name='company_registration'),
    path('registro/candidato/', loginView.candidate_registration, name='candidate_registration'),
    path('inicio/', loginView.dashboard_begin, name='inicio'),
    path('logout_view/', loginView.logout_view, name='logout'),
    path('validar_token/<str:token>', loginView.validar_token, name='validar_token'),
    path('enviar_token/', loginView.enviar_token, name='enviar_token'),
    path('acceso_denegado/', loginView.acceso_denegado, name='acceso_denegado'),
    path('cambiar_password/', loginView.change_password_form, name='change_password'),
    path('confirmar_password/<str:token>', loginView.confirm_password_form, name='confirm_password'),
    
    #candidate
    path('inicio/candidato', loginView.dashboard_candidato, name='inicio_candidato'),

    #client
    path('cliente/grupo_trabajo_interno/', client_views.create_internal_client, name='users_client'),
    path('cliente/colaborador/<int:pk>', client_views.detail_internal_client, name='users_client_detail'),

    # Seguridad
    # path('inicio', login.inicio_app, name='inicio'),
    # path('login', login.login_view, name='login'),
    # path('logout_view/', login.logout_view, name='logout'),
    # path('registro_empresa/', login.signup_view, name='signup'),
    # path('registro_candidato/', login.signup_candidato, name='signup_candidato'),
    #path('validar_token/<str:token>', login.validar_token, name='validar_token'),
    # path('enviar_token/', login.enviar_token, name='enviar_token'),
    

    # Usuarios Cliente

    # Usuarios Internos ATS
    path('usuarios_internos_ats/', CreacionUsuarioInternoView.crear_usuario_interno, name='listado_persona_interno'),

]