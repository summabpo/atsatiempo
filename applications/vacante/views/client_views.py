from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, Count, Q, Value, Case, When, CharField
from applications.cliente.models import Cli051Cliente, Cli064AsignacionCliente

from applications.vacante.models import Cli052Vacante, Cli055ProfesionEstudio, Cli053SoftSkill, Cli054HardSkill, Cli052VacanteHardSkillsId054, Cli052VacanteSoftSkillsId053, Cli072FuncionesResponsabilidades, Cli073PerfilVacante, Cli068Cargo, Cli074AsignacionFunciones
from applications.reclutado.models import Cli056AplicacionVacante
from applications.entrevista.models import Cli057AsignacionEntrevista
from applications.usuarios.models import Permiso
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.candidato.models import Can101Candidato
from django.contrib import messages
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required
from applications.usuarios.decorators  import validar_permisos
from django.db.models.functions import Concat

#forms
from applications.vacante.forms.VacanteForms import VacancyFormEdit, VacanteForm, VacanteFormEdit, VacancyFormAll

#views
from applications.services.service_vacanty import query_vacanty_all, query_vacanty_detail

#query
from applications.services.service_client import query_client_detail


#crear todas las vacantes
@login_required
@validar_permisos('acceso_cliente')
def create_vacanty(request):

    vacantes = Cli052Vacante.objects.all()
    form = VacancyFormAll()

    context = {
        'vacantes': vacantes,
        'form': form
    }

    return render(request, 'admin/vacancy/client_user/vacancy_create.html', context)

#listar todas las vacantes del cliente
@login_required
@validar_permisos('acceso_cliente')
def list_vacanty_all(request):

    # Verificar si el cliente_id está en la sesión
    cliente_id = request.session.get('cliente_id')
    
    # Obtener el cliente correspondiente al ID
    cliente = get_object_or_404(Cli051Cliente, id=cliente_id)

    vacantes = query_vacanty_all()
    vacantes = vacantes.filter(
        estado_id_001=1,  # Asumiendo que ese es el campo correcto para el estado
        asignacion_cliente_id_064__id_cliente_asignado=cliente
    )

    print(vacantes)

    context ={
        'vacantes': vacantes,
    }

    return render(request, 'admin/vacancy/client_user/vacancy_list.html', context)

#detalle de la vacante
@login_required
@validar_permisos('acceso_cliente')
def detail_vacanty(request, pk):
    # Verificar si el cliente_id está en la sesión
    cliente_id = request.session.get('cliente_id')
    
    # Obtener información de la vacante
    vacante = get_object_or_404(query_vacanty_all(), id=pk)
    print(vacante)

    vacante = query_vacanty_detail().get(id=pk)

    context ={
        'vacante': vacante,
    }

    return render(request, 'admin/vacancy/client_user/vacancy_detail.html', context)