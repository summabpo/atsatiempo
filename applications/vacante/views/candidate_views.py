from django.shortcuts import render
from applications.common.views.EnvioCorreo import enviar_correo
from applications.services.service_recruited import query_recruited_vacancy_id
from applications.vacante.forms.EntrevistaForm import EntrevistaCrearForm
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

@login_required

def apply_vacancy(request):
    """
    View to handle the application of a candidate to a vacancy.
    """

    # Obtener el ID del candidato desde la sesión
    candidato_id = request.session.get('candidato_id')
    vacanty = Cli056AplicacionVacante.objects.filter(candidato_101=candidato_id, estado=1)
    
    context = {
        vacanty: None,
    }

    return render(request, 'admin/vacancy/candidate_user/apply_vacancy.html', context)