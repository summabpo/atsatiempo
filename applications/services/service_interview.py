from applications.entrevista.models import Cli057AsignacionEntrevista
from django.db.models.functions import Concat
from django.db.models import Value, F
#consulta de entrevista general

def query_interview_all():
    return Cli057AsignacionEntrevista.objects.select_related(
        'asignacion_vacante__vacante_id_052__asignacion_cliente_id_064__id_cliente_asignado',
        'asignacion_vacante__vacante_id_052__perfil_vacante',
        'asignacion_vacante__candidato_101'
    ).annotate(
        nombre_candidato=Concat(
            'asignacion_vacante__candidato_101__primer_nombre',
            Value(' '),
            'asignacion_vacante__candidato_101__segundo_nombre',
            Value(' '),
            'asignacion_vacante__candidato_101__primer_apellido',
            Value(' '),
            'asignacion_vacante__candidato_101__segundo_apellido', 
        ),
        imagen_candidato=F('asignacion_vacante__candidato_101__imagen_perfil'),
        nombre_asignado=Concat(
            'usuario_asignado__primer_nombre',
            Value(' '),
            'usuario_asignado__segundo_nombre',
            Value(' '),
            'usuario_asignado__primer_apellido',
            Value(' '),
            'usuario_asignado__segundo_apellido', 
        ),
        nombre_cliente=F('asignacion_vacante__vacante_id_052__asignacion_cliente_id_064__id_cliente_asignado__razon_social'),
        titulo_vacante=F('asignacion_vacante__vacante_id_052__titulo'),
    )
