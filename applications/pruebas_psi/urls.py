from django.urls import path
from .views.PreguntaView import crear_pregunta

urlpatterns = [
    path('crear-pregunta/', crear_pregunta, name='crear_pregunta'),
]