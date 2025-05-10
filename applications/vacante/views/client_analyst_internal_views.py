from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, Count, Q, Value, Case, When, CharField
from applications.cliente.models import Cli051Cliente, Cli064AsignacionCliente

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

#forms
from applications.vacante.forms.VacanteForms import VacancyAssingForm, VacancyFormEdit, VacanteForm, VacanteFormEdit, VacancyFormAll

#views
from applications.services.service_vacanty import query_vacanty_all, query_vacanty_detail

#query
from applications.services.service_client import query_client_detail
from components.RegistrarHistorialVacante import crear_historial_aplicacion



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


#detalle de la vacante
@login_required
@validar_permisos('acceso_analista_seleccion_ats')
def detail_vacancy(request, pk):
    # vacante = query_vacanty_detail().get(id=pk)
    vacante = get_object_or_404(Cli052Vacante, id=pk)

    cliente_id = Cli051Cliente.objects.get(id=vacante.asignacion_cliente_id_064.id_cliente_asignado.id)

    # Pre-fill the form with the existing data from the vacante
    initial_data = {
        'titulo': vacante.titulo,
        'cargo': vacante.cargo.id if vacante.cargo else None,
        'numero_posiciones': vacante.numero_posiciones,
        'cantidad_presentar': vacante.cantidad_presentar,
        'fecha_presentacion': vacante.fecha_presentacion,
        'termino_contrato': vacante.perfil_vacante.termino_contrato if vacante.perfil_vacante else None,
        'tiempo_experiencia': vacante.perfil_vacante.tiempo_experiencia if vacante.perfil_vacante else None,
        'modalidad': vacante.perfil_vacante.modalidad if vacante.perfil_vacante else None,
        'jornada': vacante.perfil_vacante.jornada if vacante.perfil_vacante else None,
        'lugar_trabajo': vacante.perfil_vacante.lugar_trabajo.id if vacante.perfil_vacante and vacante.perfil_vacante.lugar_trabajo else None,
        'barrio': vacante.perfil_vacante.barrio if vacante.perfil_vacante else None,
        'direccion': vacante.perfil_vacante.direccion if vacante.perfil_vacante else None,
        'url_mapa': vacante.perfil_vacante.url_mapa if vacante.perfil_vacante else None,
        'horario_inicio': vacante.perfil_vacante.horario_inicio if vacante.perfil_vacante else None,
        'horario_final': vacante.perfil_vacante.horario_final if vacante.perfil_vacante else None,
        'hora_inicio': vacante.perfil_vacante.hora_inicio if vacante.perfil_vacante else None,
        'hora_final': vacante.perfil_vacante.hora_final if vacante.perfil_vacante else None,
        'soft_skills': json.dumps([{'value': skill.cli053softskill.nombre} for skill in vacante.cli052vacantesoftskillsid053_set.all()]),
        'hard_skills': json.dumps([{'value': skill.cli054hardskill.nombre} for skill in vacante.cli052vacantehardskillsid054_set.all()]),
        'idioma': vacante.perfil_vacante.idioma if vacante.perfil_vacante else None,
        'nivel_idioma': vacante.perfil_vacante.nivel_idioma if vacante.perfil_vacante else None,
        'profesion_estudio': vacante.perfil_vacante.profesion_estudio.id if vacante.perfil_vacante and vacante.perfil_vacante.profesion_estudio else None,
        'nivel_estudio': vacante.perfil_vacante.nivel_estudio if vacante.perfil_vacante else None,
        'edad_inicial': vacante.perfil_vacante.edad_inicial if vacante.perfil_vacante else None,
        'edad_final': vacante.perfil_vacante.edad_final if vacante.perfil_vacante else None,
        'genero': vacante.perfil_vacante.genero if vacante.perfil_vacante else None,
        'salario': vacante.perfil_vacante.salario if vacante.perfil_vacante else None,
        'tipo_salario': vacante.perfil_vacante.tipo_salario if vacante.perfil_vacante else None,
        'frecuencia_pago': vacante.perfil_vacante.frecuencia_pago if vacante.perfil_vacante else None,
        'salario_adicional': vacante.perfil_vacante.salario_adicional if vacante.perfil_vacante else None,
        'funciones_responsabilidades': json.dumps([{'value': funcion.funcion_responsabilidad.nombre} for funcion in vacante.cli074asignacionfunciones_set.all()]),
        'descripcion_vacante': vacante.descripcion_vacante,
    }

    form = VacancyFormEdit(initial=initial_data, cliente_id=cliente_id)
    
    if request.method == 'POST':
        form = VacancyFormEdit(request.POST, cliente_id=cliente_id)
        if form.is_valid():

            # Update existing data
            vacante.titulo = form.cleaned_data['titulo']
            vacante.cargo = Cli068Cargo.objects.get(id=form.cleaned_data['cargo'])
            vacante.numero_posiciones = form.cleaned_data['numero_posiciones']
            vacante.cantidad_presentar = form.cleaned_data['cantidad_presentar']
            vacante.fecha_presentacion = form.cleaned_data['fecha_presentacion']
            vacante.descripcion_vacante = form.cleaned_data['descripcion_vacante']
            vacante.save()

            perfil_vacante = vacante.perfil_vacante
            perfil_vacante.edad_inicial = form.cleaned_data['edad_inicial']
            perfil_vacante.edad_final = form.cleaned_data['edad_final']
            perfil_vacante.genero = form.cleaned_data['genero']
            perfil_vacante.tiempo_experiencia = form.cleaned_data['tiempo_experiencia']
            perfil_vacante.modalidad = form.cleaned_data['modalidad']
            perfil_vacante.jornada = form.cleaned_data['jornada']
            perfil_vacante.salario = form.cleaned_data['salario']
            perfil_vacante.tipo_salario = form.cleaned_data['tipo_salario']
            perfil_vacante.frecuencia_pago = form.cleaned_data['frecuencia_pago']
            perfil_vacante.salario_adicional = form.cleaned_data['salario_adicional']
            perfil_vacante.idioma = form.cleaned_data['idioma']
            perfil_vacante.nivel_idioma = form.cleaned_data['nivel_idioma']
            perfil_vacante.profesion_estudio = Cli055ProfesionEstudio.objects.get(id=form.cleaned_data['profesion_estudio'])
            perfil_vacante.nivel_estudio = form.cleaned_data['nivel_estudio']
            perfil_vacante.lugar_trabajo = Cat004Ciudad.objects.get(id=form.cleaned_data['lugar_trabajo'])
            perfil_vacante.termino_contrato = form.cleaned_data['termino_contrato']
            perfil_vacante.horario_inicio = form.cleaned_data['horario_inicio']
            perfil_vacante.horario_final = form.cleaned_data['horario_final']
            perfil_vacante.hora_inicio = form.cleaned_data['hora_inicio']
            perfil_vacante.hora_final = form.cleaned_data['hora_final']
            perfil_vacante.barrio = form.cleaned_data['barrio']
            perfil_vacante.direccion = form.cleaned_data['direccion']
            perfil_vacante.url_mapa = form.cleaned_data['url_mapa']
            perfil_vacante.save()

            # Update soft skills
            vacante.cli052vacantesoftskillsid053_set.all().delete()
            soft_skills = json.loads(form.cleaned_data['soft_skills'])
            for skill in soft_skills:
                soft_skill, created = Cli053SoftSkill.objects.get_or_create(
                    nombre=skill['value'],
                    defaults={'estado_id_001': Cat001Estado.objects.get(id=1)}
                )
                Cli052VacanteSoftSkillsId053.objects.create(
                    cli052vacante=vacante,
                    cli053softskill=soft_skill
                )

            # Update hard skills
            vacante.cli052vacantehardskillsid054_set.all().delete()
            hard_skills = json.loads(form.cleaned_data['hard_skills'])
            for skill in hard_skills:
                hard_skill, created = Cli054HardSkill.objects.get_or_create(
                    nombre=skill['value'],
                    defaults={'estado_id_001': Cat001Estado.objects.get(id=1)}
                )
                Cli052VacanteHardSkillsId054.objects.create(
                    cli052vacante=vacante,
                    cli054hardskill=hard_skill
                )

            # Update responsibilities
            vacante.cli074asignacionfunciones_set.all().delete()
            funciones_responsabilidades = json.loads(form.cleaned_data['funciones_responsabilidades'])
            for funcion in funciones_responsabilidades:
                funcion_responsabilidad, created = Cli072FuncionesResponsabilidades.objects.get_or_create(
                    nombre=funcion['value'],
                    defaults={'estado': Cat001Estado.objects.get(id=1)}
                )
                Cli074AsignacionFunciones.objects.create(
                    vacante=vacante,
                    funcion_responsabilidad=funcion_responsabilidad,
                    estado=Cat001Estado.objects.get(id=1)
                )
            
            messages.success(request, 'Vacante editada correctamente')
            return redirect('vacantes:vacantes_gestion_analista_interno', pk=pk)
        else:
            print(form.errors)
    else:
        form = VacancyFormEdit(initial=initial_data, cliente_id=cliente_id)

    context ={
        'vacante': vacante,
        'form': form,
    }

    return render(request, 'admin/vacancy/client_analyst_internal_user/vacancy_detail.html', context)