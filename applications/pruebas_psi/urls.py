from django.urls import path
from .views.PreguntaView import crear_pregunta
from .views.RespuestaView import asignar_respuesta

urlpatterns = [
    path('crear-pregunta/', crear_pregunta, name='crear_pregunta'),
]

urlpatterns = [
    path('asignar-respuesta/<int:candidato_id>/', asignar_respuesta, name='asignar_respuesta'),
]