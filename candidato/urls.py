from django.urls import path
from . import views

urlpatterns = [
    path('', views.InicioView.as_view(), name='inicio'),
    path('crear_candidato', views.candidato_crear, name='candidato_crear'),
]