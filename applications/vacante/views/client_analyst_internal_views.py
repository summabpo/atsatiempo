from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, Count, Q, Value, Case, When, CharField
from applications.cliente.models import Cli051Cliente, Cli064AsignacionCliente

from applications.services.service_recruited import query_recruited_vacancy_id
from applications.vacante.models import Cli052Vacante, Cli055ProfesionEstudio, Cli053SoftSkill, Cli054HardSkill, Cli052VacanteHardSkillsId054, Cli052VacanteSoftSkillsId053, Cli072FuncionesResponsabilidades, Cli073PerfilVacante, Cli068Cargo, Cli074AsignacionFunciones
from applications.reclutado.models import Cli056AplicacionVacante
from applications.entrevista.models import Cli057AsignacionEntrevista
from applications.usuarios.models import Permiso, UsuarioBase
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.candidato.models import Can101Candidato
from django.contrib import messages
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required
from applications.usuarios.decorators  import validar_permisos
from django.db.models.functions import Concat

#forms
from applications.vacante.forms.VacanteForms import VacancyAssingForm, VacancyFormEdit, VacanteForm, VacanteFormEdit, VacancyFormAll

#views
from applications.services.service_vacanty import query_vacanty_all, query_vacanty_detail

#query
from applications.services.service_client import query_client_detail



@login_required
@validar_permisos('acceso_analista_seleccion_ats')
def list_assigned_vacancies(request):
    # Verificar si el cliente_id está en la sesión
    user_logged_in = request.session.get('user_login')
    
    vacantes = query_vacanty_all()
    vacantes = vacantes.filter(
        estado_id_001=1,  # Asumiendo que ese es el campo correcto para el estado
        usuario_asignado=user_logged_in.get('id'),  # Asumiendo que el ID del usuario asignado está en la sesión
    )

    context = {
        'vacantes': vacantes,
    }

    return render(request, 'admin/vacancy/client_analyst_internal_user/vacancy_list.html', context)