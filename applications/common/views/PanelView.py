#liberias django
from django.shortcuts import get_object_or_404
from django.db.models import F, Count, Q

#modelos
from applications.cliente.models import Cli051Cliente
from applications.vacante.models import Cli052Vacante, Cli056AplicacionVacante, Cli057AsignacionEntrevista
from applications.candidato.models import Can101Candidato

# Panel principal administrador ATS

# Panel principal Cliente
def info_vacantes_pendientes(pk):
    cliente = get_object_or_404(Cli051Cliente, pk=pk)
    # vacantes = Cli052Vacante.objects.filter(cliente_id_051 = cliente.id)
    vacantes = Cli052Vacante.objects.annotate(num_aplicaciones=Count('aplicaciones')).filter(cliente_id_051 = cliente.id)
    
    return vacantes

# Panel principal Candidato
def info_entrevistas_candidato(pk):
    # candidato = get_object_or_404(Can101Candidato, pk=pk)
    
    asignaciones = Cli057AsignacionEntrevista.objects.select_related(
        'asignacion_vacante__vacante_id_052__cliente_id_051', 
        'asignacion_vacante__vacante_id_052', 
        'asignacion_vacante__candidato_101'
    ).filter(
        asignacion_vacante__candidato_101=pk
    ).order_by('-fecha_entrevista').values(
        # Campos del modelo principal (Cli057AsignacionEntrevista)
        'id',
        'fecha_entrevista',
        'hora_entrevista',
        'lugar_enlace',
        # Resto de clientes pendientes
        razon_social=F('asignacion_vacante__vacante_id_052__cliente_id_051__razon_social'),
        titulo_vacante=F('asignacion_vacante__vacante_id_052__titulo'),
        primer_nombre=F('asignacion_vacante__candidato_101__primer_nombre'),
        segundo_nombre=F('asignacion_vacante__candidato_101__segundo_nombre'),
        primer_apellido=F('asignacion_vacante__candidato_101__primer_apellido'),
        segundo_apellido=F('asignacion_vacante__candidato_101__segundo_apellido'),

    )
    

    return asignaciones