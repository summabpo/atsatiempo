from django.urls import path
from .views import login

urlpatterns = [
    path('', login.principal, name='home'),
    path('inicio', login.inicio_app, name='inicio'),
    path('login', login.login_view, name='login'),
    path('logout_view/', login.logout_view, name='logout'),
    path('registro_empresa/', login.signup_view, name='signup'),
    path('registro_candidato/', login.signup_candidato, name='signup_candidato'),
    path('validar_token/<str:token>', login.validar_token, name='validar_token'),
    path('enviar_token/', login.enviar_token, name='enviar_token'),
]