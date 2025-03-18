from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, Count, Q
from applications.cliente.models import Cli051Cliente, Cli064AsignacionCliente

from applications.vacante.models import Cli052Vacante, Cli055ProfesionEstudio, Cli053SoftSkill, Cli054HardSkill, Cli052VacanteHardSkillsId054, Cli052VacanteSoftSkillsId053, Cli073PerfilVacante, Cli068Cargo
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

            #datos principales
            titulo = form.cleaned_data['titulo'] 
            cargo = form.cleaned_data['cargo']
            numero_posiciones = form.cleaned_data['numero_posiciones']

            #detalles del trabajo
            tiempo_experiencia = form.cleaned_data['tiempo_experiencia']
            modalidad = form.cleaned_data['modalidad']
            jornada = form.cleaned_data['jornada']
            lugar_trabajo = form.cleaned_data['lugar_trabajo']
            termino_contrato = form.cleaned_data['termino_contrato']
            horario = form.cleaned_data['horario']
            
            #requisitos y habilidades
            soft_skills = form.cleaned_data['soft_skills']
            hard_skills = form.cleaned_data['hard_skills']
            idioma = form.cleaned_data['idioma']
            profesion_estudio = form.cleaned_data['profesion_estudio']
            nivel_estudio = form.cleaned_data['nivel_estudio']
            edad = form.cleaned_data['edad']
            genero = form.cleaned_data['genero']

            #informacion salarial
            salario = form.cleaned_data['salario']
            tipo_salario = form.cleaned_data['tipo_salario']
            frecuencia_pago = form.cleaned_data['frecuencia_pago']
            salario_adicional = form.cleaned_data['salario_adicional']

            #responsabilidad del cargo
            funciones_responsabilidades = form.cleaned_data['funciones_responsabilidades']
            
            #creacion del perfil de la vacante
            perfil_vacante = Cli073PerfilVacante.objects.create(
                edad='1',  # Assuming default value
                genero='1',  # Assuming default value
                tiempo_experiencia=1,  # Assuming default value
                horario=horario,
                modalidad='1',  # Assuming default value
                jornada='1',  # Assuming default value
                salario=1,
                tipo_salario='1',  # Assuming default value
                frecuencia_pago='1',  # Assuming default value
                salario_adicional=None,  # Assuming default value
                idioma='1',  # Assuming default value
                profesion_estudio=Cli055ProfesionEstudio.objects.get(id=1),  # Assuming default value
                nivel_estudio=1,  # Assuming default value
                lugar_trabajo=Cat004Ciudad.objects.get(id=1),
                termino_contrato=1,  # Assuming default value
                estado=Cat001Estado.objects.get(id=1),
                fecha_creacion=1
            )


            #creacion de la vacante
            vacante = Cli052Vacante.objects.create(
                titulo=titulo,
                numero_posiciones=numero_posiciones,  # Assuming default value
                estado_vacante=1,  # Assuming default value
                estado_id_001=Cat001Estado.objects.get(id=1),
                fecha_cierre=1,
                usuario_asignado=request.user,
                asignacion_cliente_id_064=Cli064AsignacionCliente.objects.get(id=pk),
                cargo=Cli068Cargo.objects.get(id=cargo),  # Fetching the cargo object
                perfil_vacante=perfil_vacante  
            )

            vacante.soft_skills_id_053.set(form.cleaned_data['soft_skills'])
            vacante.hard_skills_id_054.set(form.cleaned_data['hard_skills'])
            
            print(titulo)
            print(horario)
            print(funciones_responsabilidades)
            
            
            
            
            # form.save()
            messages.success(request, 'Vacante creada correctamente')
            # return redirect('vacantes_propias', pk=pk)
    else:
        form = VacancyFormAll(cliente_id=pk)

    context = {
        'data': data,
        'vacantes': vacantes,
        'form': form
    }

    return render(request, 'admin/vacancy/admin_user/client_detail_vacancy.html', context)