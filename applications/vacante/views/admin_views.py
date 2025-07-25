from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, Count, Q, Value, Case, When, CharField
from applications.cliente.models import Cli051Cliente, Cli064AsignacionCliente, Cli078MotivadoresCandidato

from applications.reclutado.forms.FormRecruited import ReclutadoCrearForm
from applications.services.service_interview import query_interview_all
from applications.services.service_recruited import query_recruited_vacancy_id
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

    asignacion_cliente = Cli064AsignacionCliente.objects.get(id_cliente_asignado=pk)


    form = VacancyFormAllV2(cliente_id=pk)

    if request.method == 'POST':
        form = VacancyFormAllV2(request.POST, cliente_id=pk)

        if form.is_valid():
            #datos principales
            cargo = form.cleaned_data['cargo']
            cargo_obj= Cli068Cargo.objects.get(id=cargo)
            termino_contrato = form.cleaned_data['termino_contrato']
            modalidad = form.cleaned_data['modalidad']
            numero_posiciones = form.cleaned_data['numero_posiciones']
            cantidad_presentar = form.cleaned_data['cantidad_presentar']
            fecha_presentacion = form.cleaned_data['fecha_presentacion']
            lugar_trabajo = form.cleaned_data['lugar_trabajo']
            barrio = form.cleaned_data['barrio']
            direccion = form.cleaned_data['direccion']
            salario = form.cleaned_data['salario'].replace('.', '')
            tipo_salario = form.cleaned_data['tipo_salario']
            frecuencia_pago = form.cleaned_data['frecuencia_pago']
            salario_adicional = form.cleaned_data['salario_adicional']
            edad_inicial = form.cleaned_data['edad_inicial']
            edad_final = form.cleaned_data['edad_final']   
            genero = form.cleaned_data['genero']
            motivo_vacante = form.cleaned_data['motivo_vacante']
            otro_motivo = form.cleaned_data['otro_motivo']
            
            json_motivo =  []
            json_motivo.append({
                "motivo_vacante":motivo_vacante,
                "otro_motivo":otro_motivo
            })

            horarios = []
            for i in range(1, 4):
                horario_inicio = form.cleaned_data.get(f'horario_inicio_{i}')
                horario_final = form.cleaned_data.get(f'horario_final_{i}')
                hora_inicio = form.cleaned_data.get(f'hora_inicio_{i}')
                hora_final = form.cleaned_data.get(f'hora_final_{i}')
                if all([horario_inicio, horario_final, hora_inicio, hora_final]):
                    horarios.append({
                        "horario_inicio": horario_inicio,
                        "horario_final": horario_final,
                        "hora_inicio": str(hora_inicio),
                        "hora_final": str(hora_final),
                    })
            json_horarios = json.dumps(horarios, ensure_ascii=False)
            
            funcion_responsabilidad = []
            for i in range(1,4):
                funciones_responsabilidades = form.cleaned_data.get(f'funciones_responsabilidades_{i}')
                if funciones_responsabilidades:
                    funcion_responsabilidad.append({
                        "funcion_responsabilidad": funciones_responsabilidades,
                    })
            json_funciones = json.dumps(funcion_responsabilidad, ensure_ascii=False)

            # requisitos tecnicos
            experiencia = []
            for i in range(1,4):
                tiempo_experiencia = form.cleaned_data.get(f'tiempo_experiencia_{i}')
                experiencia_especifica_en = form.cleaned_data.get(f'experiencia_especifica_en_{i}')
                if all([tiempo_experiencia, experiencia_especifica_en]):
                    experiencia.append({
                        "tiempo_experiencia" : tiempo_experiencia,
                        "experiencia_especifica_en" : experiencia_especifica_en,
                    })
            json_experiencia = json.dumps(experiencia, ensure_ascii=False)

            idiomas = []
            for i in range(1,4):
                idioma = form.cleaned_data.get(f'idioma_{i}')
                nivel_idioma = form.cleaned_data.get(f'nivel_idioma_{i}')
                if all([idioma, nivel_idioma]):
                    idiomas.append({
                        "idioma" : idioma,
                        "nivel_idioma" : nivel_idioma,
                    })
            json_idiomas = json.dumps(idiomas, ensure_ascii=False)

            profesion_estudio = form.cleaned_data['profesion_estudio']
            nivel_estudio = form.cleaned_data['nivel_estudio']
            estado_estudio = form.cleaned_data['estado_estudio']

            estudios_complentarios_all = []
            for i in range(1,4):
                estudios_complementarios = form.cleaned_data.get(f'estudios_complementarios_{i}')
                estudios_complementarios_certificado = form.cleaned_data.get(f'estudios_complementarios_certificado_{i}')

                if all([estudios_complementarios, estudios_complementarios_certificado]):
                    estudios_complentarios_all.append({
                        "estudio" : estudios_complementarios,
                        "certificado_estudios_complementarios" : estudios_complementarios_certificado,
                    })
            json_estudios_complementarios = json.dumps(estudios_complentarios_all, ensure_ascii=False)

            # Competencias
            relacionales = form.cleaned_data.get('skill_relacionales', [])
            personales = form.cleaned_data.get('skill_personales', [])
            cognitivas = form.cleaned_data.get('skill_cognitivas', [])
            digitales = form.cleaned_data.get('skill_digitales', [])
            liderazgo = form.cleaned_data.get('skill_liderazgo', [])
            
            all_selected_skills = (
                list(relacionales) +
                list(personales) +
                list(cognitivas) +
                list(digitales) +
                list(liderazgo)
            )

            
            #fitcultural 
            grupo_fit_1 = form.cleaned_data.get('grupo_fit_1', [])
            grupo_fit_2 = form.cleaned_data.get('grupo_fit_2', [])
            grupo_fit_3 = form.cleaned_data.get('grupo_fit_3', [])
            grupo_fit_4 = form.cleaned_data.get('grupo_fit_4', [])
            grupo_fit_5 = form.cleaned_data.get('grupo_fit_5', [])

            all_grupo_fit = (
                list(grupo_fit_1) +
                list(grupo_fit_2) +
                list(grupo_fit_3) +
                list(grupo_fit_4) +
                list(grupo_fit_5) 
            )

            #motivadores
            motivadores_candidato = form.cleaned_data.get('motivadores_candidato')
            otro_motivador = form.cleaned_data.get('otro_motivador')

            #Comentarios 
            comentarios= form.cleaned_data.get('comentarios')
            descripcion_vacante = form.cleaned_data.get('descripcion_vacante')

            #creacion perfil de la vacante
            perfil_vacante = Cli073PerfilVacante.objects.create(
                edad_inicial= edad_inicial,
                edad_final= edad_final,
                genero= genero,
                tiempo_experiencia= 6,
                modalidad=modalidad,
                salario=salario,
                tipo_salario= tipo_salario,
                frecuencia_pago=frecuencia_pago,
                salario_adicional= salario_adicional,
                idioma= None,
                nivel_idioma=None,
                profesion_estudio= Cli055ProfesionEstudio.objects.get(id=profesion_estudio), # ForeignKey a Cli055ProfesionEstudio
                nivel_estudio= nivel_estudio,
                estado_estudio= estado_estudio,
                lugar_trabajo = Cat004Ciudad.objects.get(id=lugar_trabajo),
                barrio= barrio,
                direccion= direccion,
                url_mapa= None,
                termino_contrato=termino_contrato,
                horario_inicio= None,
                horario_final= None,
                hora_inicio= None,
                hora_final= None,
                motivo_vacante= json_motivo,
                horario= json_horarios,
                experiencia_laboral= json_experiencia,
                idiomas=json_idiomas,
                estudio_complementario= json_estudios_complementarios,
                funciones_responsabilidades=json_funciones
            )

            vacante = Cli052Vacante.objects.create(
                cargo = cargo_obj,
                numero_posiciones = numero_posiciones,
                cantidad_presentar=cantidad_presentar,
                titulo = f'Vacante para el cargo:{cargo_obj.nombre_cargo}',
                motivadores = Cli078MotivadoresCandidato.objects.get(id=motivadores_candidato),
                otro_motivador = otro_motivador,
                fecha_presentacion = fecha_presentacion,
                asignacion_cliente_id_064 = asignacion_cliente,
                perfil_vacante = perfil_vacante,
                descripcion_vacante = descripcion_vacante, 
                comentarios = comentarios
            )

            # 1. Elimina las relaciones existentes para esta vacante.
            # Esto es crucial para manejar actualizaciones y evitar errores por la restricción 'unique_together'.
            Cli052VacanteSoftSkillsId053.objects.filter(cli052vacante=vacante).delete()

            # 2. Prepara una lista de los nuevos objetos a crear.
            # Usar 'cli053softskill_id' es más eficiente porque evita consultar cada objeto SoftSkill.
            objetos_a_crear = [
                Cli052VacanteSoftSkillsId053(
                    cli052vacante=vacante,
                    cli053softskill_id=skill_obj.id 
                )
                for skill_obj in all_selected_skills 
            ]

            # 3. Inserta todos los nuevos registros en una sola consulta (si la lista no está vacía).
            if objetos_a_crear:
                Cli052VacanteSoftSkillsId053.objects.bulk_create(objetos_a_crear)
            
            vacante.fit_cultural.set(all_grupo_fit)
            
            messages.success(request, 'Vacante creada correctamente')
            return redirect('vacantes:vacantes_propias' pk=pk)
        else:
            messages.error(request, 'Por favor revise el formulario, errores encontrados.')
            
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

@login_required
@validar_permisos('acceso_admin')
def vacanty_management_from_client(request, pk, vacante_id):

    # Data cliente a mostrar
    data = query_client_detail(pk)
    vacante = get_object_or_404(Cli052Vacante, id=vacante_id)
    # Obtener información de las entrevistas por vacante
    entrevistas = query_interview_all()
    entrevistas = entrevistas.filter(asignacion_vacante__vacante_id_052=vacante.id)

    # Obtener los reclutados asociados a la vacante
    reclutados = query_recruited_vacancy_id(vacante.id)

    #Formulario para reclutar candidato a la vacante
    form_reclutados = ReclutadoCrearForm()
    if request.method == 'POST':
        form_reclutados = ReclutadoCrearForm(request.POST)
        if form_reclutados.is_valid():
            numero_documento = form_reclutados.cleaned_data['numero_documento']
            primer_nombre = form_reclutados.cleaned_data['primer_nombre']
            segundo_nombre = form_reclutados.cleaned_data['segundo_nombre']
            primer_apellido = form_reclutados.cleaned_data['primer_apellido']
            segundo_apellido = form_reclutados.cleaned_data['segundo_apellido']
            telefono = form_reclutados.cleaned_data['telefono']
            email = form_reclutados.cleaned_data['email']

            #registro del candidato
            candidato, created = Can101Candidato.objects.get_or_create(
                numero_documento=numero_documento,
                defaults={
                    'primer_nombre': primer_nombre,
                    'segundo_nombre': segundo_nombre,
                    'primer_apellido': primer_apellido,
                    'segundo_apellido': segundo_apellido,
                    'telefono': telefono,
                    'email': email,
                    'estado_id_001': Cat001Estado.objects.get(id=1),  # Asumiendo que 1 es el estado por defecto
                }
            )

            if created:
                messages.success(request, 'Candidato creado exitosamente.')
            else:
                messages.info(request, 'Candidato ya existe. Se actualizarán los datos.')
                # Actualizar los datos del candidato si ya existe
                candidato.primer_nombre = primer_nombre
                candidato.segundo_nombre = segundo_nombre
                candidato.primer_apellido = primer_apellido
                candidato.segundo_apellido = segundo_apellido
                candidato.telefono = telefono
                candidato.email = email
                candidato.save()

            # Validar que el candidato no esté ya registrado en la vacante
            if Cli056AplicacionVacante.objects.filter(candidato_101=candidato, vacante_id_052=vacante).exists():
                messages.error(request, 'El candidato ya está registrado en esta vacante.')
                return redirect('vacantes:vacantes_gestion_propias', pk=pk, vacante_id=vacante_id)

            #registro de la aplicacion de la vacante
            aplicacion_vacante = Cli056AplicacionVacante.objects.create(
                vacante_id_052=vacante,
                candidato_101=candidato,
                estado=Cat001Estado.objects.get(id=1),  # 1 es el estado por defecto
            )
            messages.success(request, 'Candidato asignado en la vacante exitosamente.')
            return redirect('vacantes:vacantes_gestion_propias', pk=pk, vacante_id=vacante_id)    
        else:
            form_errors = True
            messages.error(request, 'Error al crear el candidato. Verifique los datos.')
            
    else:
        form_reclutados = ReclutadoCrearForm()

    context = {
        'data': data,
        'vacante': vacante,
        'reclutados': reclutados,
        'entrevistas': entrevistas,
        'form_reclutados' : form_reclutados,
    }

    return render(request, 'admin/vacancy/admin_user/client_detail_vacancy_management.html', context) 