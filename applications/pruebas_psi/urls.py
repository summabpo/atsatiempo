import atsatiempo.asgi
from django.urls import path
from applications.pruebas_psi.views.PreguntaView import crear_pregunta, listar_preguntas
from applications.pruebas_psi.views.ResultadoView import resultado_prueba
from applications.pruebas_psi.views.RespuestaView import asignar_respuesta
from applications.pruebas_psi.views.CalificarView import calificar_prueba

app_name = 'pruebas_psi'


urlpatterns = [
    path('crear-pregunta/', crear_pregunta, name='crear_pregunta'),
    path('listar-preguntas/', listar_preguntas, name='listar_preguntas'),
    path('resultado-prueba/<int:candidato_id>/', resultado_prueba, name='resultado_prueba'),
    path('asignar-respuesta/<int:candidato_id>/', asignar_respuesta, name='asignar_respuesta'),
    path('calificar-prueba/<int:candidato_id>/', calificar_prueba, name='calificar_prueba'),
]