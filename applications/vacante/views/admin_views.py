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
from applications.vacante.forms.VacanteForms import VacancyFormAllV2, VacancyFormEdit, VacanteForm, VacanteFormEdit, VacancyFormAll

#views
from applications.services.service_vacanty import query_vacanty_all

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

    vacantes = query_vacanty_all()

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

    form = VacancyFormAllV2(cliente_id=pk)

    if request.method == 'POST':
        form = VacancyFormAllV2(request.POST, cliente_id=pk)

        if form.is_valid():

            #datos principales
            titulo = form.cleaned_data['titulo']                            #perfil de la vacante
            cargo = form.cleaned_data['cargo']                              #perfil de la vacante
            numero_posiciones = form.cleaned_data['numero_posiciones']      #perfil de la vacante
            cantidad_presentar = form.cleaned_data['cantidad_presentar']     #perfil de la vacante    
            fecha_presentacion = form.cleaned_data['fecha_presentacion']    #vacante
            

            #detalles del trabajo
            termino_contrato = form.cleaned_data['termino_contrato']
            tiempo_experiencia = form.cleaned_data['tiempo_experiencia']
            modalidad = form.cleaned_data['modalidad']
            jornada = form.cleaned_data['jornada']
            
            #lugar del trabajo
            lugar_trabajo = form.cleaned_data['lugar_trabajo']
            barrio =  form.cleaned_data['barrio']
            direccion =  form.cleaned_data['direccion']
            url_mapa = form.cleaned_data['url_mapa']
            
            horario_inicio = form.cleaned_data['horario_inicio']
            horario_final = form.cleaned_data['horario_final']
            hora_inicio = form.cleaned_data['hora_inicio']
            hora_final = form.cleaned_data['hora_final']
            
            #requisitos y habilidades
            soft_skills = form.cleaned_data['soft_skills']
            hard_skills = form.cleaned_data['hard_skills']
            idioma = form.cleaned_data['idioma']
            nivel_idioma = form.cleaned_data['nivel_idioma']
            profesion_estudio = form.cleaned_data['profesion_estudio']
            nivel_estudio = form.cleaned_data['nivel_estudio']
            edad_inicial = form.cleaned_data['edad_inicial']
            edad_final = form.cleaned_data['edad_final']
            genero = form.cleaned_data['genero']
            

            #informacion salarial
            salario = form.cleaned_data['salario']
            
            tipo_salario = form.cleaned_data['tipo_salario']
            frecuencia_pago = form.cleaned_data['frecuencia_pago']
            salario_adicional = form.cleaned_data['salario_adicional']

            #responsabilidad del cargo
            funciones_responsabilidades = form.cleaned_data['funciones_responsabilidades']

            #descripcion de la vacante
            descripcion_vacante = form.cleaned_data['descripcion_vacante']

            #creacion del perfil de la vacante
            perfil_vacante, perfil_vacante_nuevo = Cli073PerfilVacante.objects.get_or_create(
                edad_inicial=edad_inicial,
                edad_final=edad_final,
                genero=genero,
                tiempo_experiencia=tiempo_experiencia,
                modalidad=modalidad,
                jornada=jornada,
                salario=salario,
                tipo_salario=tipo_salario,
                frecuencia_pago=frecuencia_pago,
                salario_adicional=salario_adicional,
                idioma=idioma,
                nivel_idioma=nivel_idioma,
                profesion_estudio=Cli055ProfesionEstudio.objects.get(id=profesion_estudio),
                nivel_estudio=nivel_estudio,
                estado_estudio=False,  # Assuming default value
                lugar_trabajo=Cat004Ciudad.objects.get(id=lugar_trabajo),
                termino_contrato=termino_contrato,
                estado=Cat001Estado.objects.get(id=1),
                horario_inicio=horario_inicio,  # Assuming default value
                horario_final=horario_final,  # Assuming default value
                hora_inicio=hora_inicio,  # Assuming default value
                hora_final=hora_final,  # Assuming default value
                barrio=barrio,  # Assuming default value
                direccion=direccion,  # Assuming default value
                url_mapa=url_mapa  # Assuming default value
            )

        
            #verificacion de asignación vacante
            asignacion_cliente, asignacion_cliente_created = Cli064AsignacionCliente.objects.get_or_create(
                id_cliente_maestro=Cli051Cliente.objects.get(id=1000),
                id_cliente_asignado=Cli051Cliente.objects.get(id=pk),
                defaults={'tipo_asignacion': '1', 'estado': Cat001Estado.objects.get(id=1)}
            )

            #creacion de la vacante
            vacante = Cli052Vacante.objects.create(
                titulo=titulo,
                numero_posiciones=numero_posiciones,
                cantidad_presentar=cantidad_presentar,
                estado_vacante=1,
                estado_id_001=Cat001Estado.objects.get(id=1),
                fecha_presentacion=fecha_presentacion,
                # usuario_asignado=request.user,
                asignacion_cliente_id_064=asignacion_cliente,
                cargo=Cli068Cargo.objects.get(id=cargo),
                perfil_vacante=perfil_vacante,
                descripcion_vacante=descripcion_vacante
            )

            # Convertir el string JSON en un objeto Python (lista de diccionarios)
            skills = json.loads(soft_skills)
            
            # Ahora puedes iterar sobre la lista de diccionarios
            for skill in skills:
                # Intentar obtener el objeto soft_skills
                soft_skills, created = Cli053SoftSkill.objects.get_or_create(
                    nombre = skill['value'],
                    defaults={'estado_id_001': Cat001Estado.objects.get(id=1)}
                )

                Cli052VacanteSoftSkillsId053.objects.create(
                    cli052vacante=vacante,
                    cli053softskill=soft_skills
                )


            # Convertir el string JSON en un objeto Python (lista de diccionarios)
            skills = json.loads(hard_skills)
            
            # Ahora puedes iterar sobre la lista de diccionarios
            for skill in skills:
                # Intentar obtener el objeto hard_skills
                hard_skills, created = Cli054HardSkill.objects.get_or_create(
                    nombre = skill['value'],
                    defaults={'estado_id_001': Cat001Estado.objects.get(id=1)}
                )

                Cli052VacanteHardSkillsId054.objects.create(
                    cli052vacante=vacante,
                    cli054hardskill=hard_skills
                )

            # Iteraciones con las funciones y la vacante
            funciones_responsabilidades = json.loads(funciones_responsabilidades)
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

            # form.save()
            messages.success(request, 'Vacante creada correctamente')
            return redirect('vacantes:vacantes_propias', pk=pk)

        else:
            print(form.errors)
    else:
        form = VacancyFormAllV2(cliente_id=pk)

    context = {
        'data': data,
        'vacantes': vacantes,
        'form': form
    }

    return render(request, 'admin/vacancy/admin_user/client_detail_vacancy_create.html', context) 

#editar vacante
@login_required
# @validar_permisos(*Permiso.obtener_nombres())
def edit_vacanty_from_client(request, pk, vacante_id):
    # Data cliente a mostrar
    data = query_client_detail(pk)



    vacante = get_object_or_404(Cli052Vacante, id=vacante_id)

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

    form = VacancyFormEdit(initial=initial_data, cliente_id=pk)
    
    if request.method == 'POST':
        form = VacancyFormEdit(request.POST, cliente_id=pk)
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
            return redirect('vacantes:vacantes_propias', pk=pk)
        else:
            print(form.errors)

    context = {
        'data': data,
        'form': form
    }

    return render(request, 'admin/vacancy/admin_user/client_detail_vacancy_edit.html', context)

#crear vacante
@login_required
# @validar_permisos(*Permiso.obtener_nombres())
def list_vacanty_from_client(request, pk):

    # Data cliente a mostrar
    data = query_client_detail(pk)

    # Data
    vacantes = query_vacanty_all()

    #filtro para mostrar solo las vacantes del cliente
    vacantes = vacantes.filter(
        asignacion_cliente_id_064__id_cliente_asignado=pk,
        asignacion_cliente_id_064__tipo_asignacion='1'
    )

    context = {
        'data': data,
        'vacantes': vacantes,
    }

    return render(request, 'admin/vacancy/admin_user/client_detail_vacancy.html', context) 