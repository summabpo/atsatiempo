from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, Count, Q
from applications.cliente.models import Cli051Cliente, Cli064AsignacionCliente

from applications.vacante.models import Cli052Vacante, Cli055ProfesionEstudio, Cli053SoftSkill, Cli054HardSkill, Cli052VacanteHardSkillsId054, Cli052VacanteSoftSkillsId053
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

#forms
from applications.vacante.forms.VacanteForms import VacanteForm, VacanteFormEdit, VacancyFormAll

#views


#query
from applications.services.service_client import query_client_detail


#crear todas las vacantes
@login_required
# @validar_permisos(*Permiso.obtener_nombres())
def create_vacanty(request):

    vacantes = Cli052Vacante.objects.all()
    form = VacancyFormAll()

    context = {
        'vacantes': vacantes,
        'form': form
    }

    return render(request, 'admin/vacancy/admin_user/vacancy_create.html', context)

# ver todas las vacantes
@login_required
# @validar_permisos(*Permiso.obtener_nombres())
def list_vacanty_all(request):

    vacantes = Cli052Vacante.objects.all()

    context = {
        'vacantes': vacantes
    }

    return render(request, 'admin/vacancy/admin_user/vacancy_all.html', context)


#crear vacante
@login_required
# @validar_permisos(*Permiso.obtener_nombres())
def create_vacanty_from_client(request, pk):

    # Data cliente a mostrar
    data = query_client_detail(pk)

    vacantes = Cli052Vacante.objects.select_related(
        'asignacion_cliente_id_064__id_cliente_asignado'
    ).filter(
        asignacion_cliente_id_064__id_cliente_asignado=pk,
        asignacion_cliente_id_064__tipo_asignacion='1'  # Aquí va el campo correcto
    )

    form = VacancyFormAll(cliente_id=pk)

    if request.method == 'POST':
        form = VacancyFormAll(request.POST, cliente_id=pk)

        if form.is_valid():
            
            # form.save()
            # messages.success(request, 'Vacante creada correctamente')
            # return redirect('vacantes_propias', pk=pk)
    else:
        form = VacancyFormAll(cliente_id=pk)

    context = {
        'data': data,
        'vacantes': vacantes,
        'form': form
    }

    return render(request, 'admin/vacancy/admin_user/client_detail_vacancy.html', context)