from django.shortcuts import render
from applications.common.views.EnvioCorreo import enviar_correo
from applications.services.service_candidate import personal_information_calculation
from applications.services.service_recruited import consultar_historial_aplicacion_vacante, query_recruited_vacancy_id, consultar_historial_aplicacion_vacante_candidate
from applications.vacante.forms.BuscarVacanteForm import VacanteFiltro
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
from django.shortcuts import render, redirect, get_object_or_404

@login_required
@validar_permisos('acceso_candidato')
def apply_vacancy(request):
    

    # Obtener el ID del candidato desde la sesión
    candidato_id = request.session.get('candidato_id')
    vacancy = Cli056AplicacionVacante.objects.filter(candidato_101=candidato_id, estado=1).order_by('-id')
    
    context = {
        'vacancy': vacancy,
    }

    return render(request, 'admin/vacancy/candidate_user/apply_vacancy.html', context)

@login_required
@validar_permisos('acceso_candidato')
def apply_vacancy_detail(request, pk):
    # Obtener el ID del candidato desde la sesión
    candidato_id = request.session.get('candidato_id')
    
    # Obtener la aplicación de vacante específica
    try:
        vacancy = Cli056AplicacionVacante.objects.get(id=pk, candidato_101=candidato_id)
        vacante = get_object_or_404(Cli052Vacante, id=vacancy.vacante_id_052.id, estado_id_001=1)
        historico_vacante = consultar_historial_aplicacion_vacante_candidate(vacancy.id)
    except Cli056AplicacionVacante.DoesNotExist:
        messages.error(request, "La aplicación de vacante no existe o no pertenece al candidato.")
        return redirect('vacantes:vacante_candidato_aplicadas')
        

    context = {
        'vacancy': vacancy,
        'vacante': vacante,
        'historial': historico_vacante,
    }

    return render(request, 'admin/vacancy/candidate_user/apply_vacancy_detail.html', context)

@login_required
@validar_permisos('acceso_candidato')
def vacancy_available(request):
    # Obtener el ID del candidato desde la sesión
    candidato_id = request.session.get('candidato_id')

    data = personal_information_calculation(candidato_id)

    # Filtrar las vacantes disponibles para el candidato
    vacantes_disponibles = Cli052Vacante.objects.select_related(
        'perfil_vacante', 
        'perfil_vacante__lugar_trabajo'
    ).filter(
        estado_id_001=1,
    ).exclude(
        aplicaciones__candidato_101=candidato_id
    ).order_by('-fecha_creacion')

    #
    form = VacanteFiltro(request.GET or None)

    if form.is_valid():
        ciudad = form.cleaned_data.get('ciudad')
        experiencia_requerida = form.cleaned_data.get('experiencia_requerida')
        profesion_estudio = form.cleaned_data.get('profesion_estudio')

        if ciudad:
            vacantes_disponibles = vacantes_disponibles.filter(perfil_vacante__lugar_trabajo=ciudad)

        if experiencia_requerida:
            vacantes_disponibles = vacantes_disponibles.filter(perfil_vacante__tiempo_experiencia=experiencia_requerida)

        if profesion_estudio:
            vacantes_disponibles = vacantes_disponibles.filter(perfil_vacante__profesion_estudio=profesion_estudio)

        

    context = {
        'vacantes_disponibles': vacantes_disponibles,
        'data_candidate': data,
        'form': form,
    }

    return render(request, 'admin/vacancy/candidate_user/vacancy_available.html', context)