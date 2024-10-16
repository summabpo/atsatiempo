#liberias django
from django.shortcuts import get_object_or_404

#modelos
from applications.cliente.models import Cli051Cliente
from applications.vacante.models import Cli052Vacante

# Panel principal administrador ATS

# Panel principal Cliente
def info_vacantes_pendientes(pk):
    cliente = get_object_or_404(Cli051Cliente, pk=pk)
    vacantes = Cli052Vacante.objects.filter(cliente_id_051 = cliente.id)
    
    return vacantes

# Panel principal Candidato
