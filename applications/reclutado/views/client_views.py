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
from applications.vacante.forms.VacanteForms import VacancyFormAll

#query
from applications.services.service_vacanty import  query_vacanty_detail
from applications.services.service_recruited import query_recruited_vacancy_id

#detalle de la vacante
@login_required
@validar_permisos('acceso_admin', 'acceso_cliente')
def detail_vacancy_recruited(request, pk):
    # Verificar si el cliente_id está en la sesión
    cliente_id = request.session.get('cliente_id')
    
    # Obtener información de la vacante
    vacante = query_vacanty_detail().get(id=pk)

    # Obtener los reclutados asociados a la vacante
    reclutados = query_recruited_vacancy_id(vacante.id)

    context ={
        'vacante': vacante,
        'reclutados': reclutados,
    }

    return render(request, 'admin/vacancy/client_user/vacancy_detail_recruited.html', context)


