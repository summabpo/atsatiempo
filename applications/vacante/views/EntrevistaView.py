from django.shortcuts import render, redirect, get_object_or_404

#modelos
from applications.vacante.models import Cli057AsignacionEntrevista, Cli056AplicacionVacante, Cli052Vacante
from applications.cliente.models import Cli051Cliente
from applications.vacante.forms.EntrevistaForm import EntrevistaCrearForm
from applications.usuarios.models import Permiso
from django.contrib.auth.decorators import login_required
from applications.usuarios.decorators  import validar_permisos

# Create your views here.


#CLIENTE

# Ver entrevistas generadas
@login_required
@validar_permisos(*Permiso.obtener_nombres())
def ver_entrevista_todos(request):    
    asignaciones = Cli057AsignacionEntrevista.objects.filter(estado=1, asignacion_vacante__candidato_101__id=1 ).select_related(
        'asignacion_vacante__candidato_101',
        'asignacion_vacante__vacante_id_052',
        'usuario_asigno',
        'usuario_asignado'
    ).values('asignacion_vacante__id','asignacion_vacante__candidato_101__primer_nombre').order_by('fecha_asignacion')
    
    print(asignaciones)

    contexto = {
        'asignaciones': asignaciones
    }

#Generar Entrevista
@login_required
@validar_permisos(*Permiso.obtener_nombres())
def crear_entrevista(request, asignacion_id):
    aplicacion_entrevista = get_object_or_404(Cli056AplicacionVacante, id=asignacion_id)
    vacante = get_object_or_404(Cli052Vacante, id=aplicacion_entrevista.vacante_id_052.id)

    contexto = {
        'aplicacion_entrevista': aplicacion_entrevista,
        'vacante': vacante,
        'EntrevistaForm': EntrevistaCrearForm,

    }

    return render(request, 'vacante/crear_entrevista.html', contexto)