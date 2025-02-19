from django.urls import path

from .views.usuariosInternosATS import CreacionUsuarioInternoView
from applications.common.views import PruebasView
from .views import login

#new
from applications.usuarios.views.user_login import loginView

urlpatterns = [
    #new
    path('test_template', PruebasView.test_template, name='test'),
    path('', loginView.principal, name='home'),
    path('login', loginView.login_view, name='login'),
    path('registro', loginView.registration, name='registration'),
    path('registro/empresa', loginView.company_registration, name='company_registration'),
    path('registro/candidato', loginView.candidate_registration, name='candidate_registration'),
    path('inicio/', loginView.dashboard_begin, name='inicio'),
    path('logout_view/', loginView.logout_view, name='logout'),

    # Seguridad
    # path('inicio', login.inicio_app, name='inicio'),
    # path('login', login.login_view, name='login'),
    # path('logout_view/', login.logout_view, name='logout'),
    # path('registro_empresa/', login.signup_view, name='signup'),
    # path('registro_candidato/', login.signup_candidato, name='signup_candidato'),
    path('validar_token/<str:token>', login.validar_token, name='validar_token'),
    path('enviar_token/', login.enviar_token, name='enviar_token'),
    path('acceso_denegado/', login.acceso_denegado, name='acceso_denegado'),

    # Usuarios Cliente

    # Usuarios Internos ATS
    path('usuarios_internos_ats/', CreacionUsuarioInternoView.crear_usuario_interno, name='listado_persona_interno'),

]