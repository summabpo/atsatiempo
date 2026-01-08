from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, Count, Q, Value, Case, When, CharField 
from django.db import transaction, IntegrityError
from applications.cliente.models import Cli051Cliente, Cli064AsignacionCliente, Cli078MotivadoresCandidato

from applications.services.service_interview import query_interview_all
from applications.services.service_recruited import query_recruited_vacancy_id
from applications.reclutado.forms.FormRecruited import ReclutadoCrearForm
from applications.vacante.models import Cli052Vacante, Cli055ProfesionEstudio, Cli053SoftSkill, Cli054HardSkill, Cli052VacanteHardSkillsId054, Cli052VacanteSoftSkillsId053, Cli072FuncionesResponsabilidades, Cli073PerfilVacante, Cli068Cargo, Cli074AsignacionFunciones, Cli075GrupoProfesion
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
from applications.vacante.forms.VacanteForms import VacancyAssingForm, VacancyFormAllV2, VacancyFormEdit, VacanteForm, VacanteFormEdit, VacancyFormAll, VacancyAssignRecruiterForm

#views
from applications.services.service_vacanty import query_vacanty_all, query_vacanty_detail, get_vacanty_questions

#query
from applications.services.service_client import query_client_detail


#crear todas las vacantes
@login_required
@validar_permisos('acceso_cliente')
def create_vacanty(request):

    # Verificar si el cliente_id está en la sesión
    cliente_id = request.session.get('cliente_id')

    # Data cliente a mostrar
    data = query_client_detail(cliente_id)

    vacantes = Cli052Vacante.objects.select_related(
        'asignacion_cliente_id_064__id_cliente_asignado'
    ).filter(
        asignacion_cliente_id_064__id_cliente_asignado=cliente_id,
        asignacion_cliente_id_064__tipo_asignacion='1'  # Aquí va el campo correcto
    )

    form = VacancyFormAll(cliente_id=cliente_id)

    if request.method == 'POST':
        form = VacancyFormAll(request.POST, cliente_id=cliente_id)

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
                id_cliente_asignado=Cli051Cliente.objects.get(id=cliente_id),
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
            return redirect('vacantes:vacantes_listado_cliente')

        else:
            print(form.errors)
    else:
        form = VacancyFormAll(cliente_id=cliente_id)

    context = {
        'form': form,
        'vacantes': vacantes,
    }

    return render(request, 'admin/vacancy/client_user/vacancy_create.html', context)

@login_required
@validar_permisos('acceso_cliente')
def create_vacanty_v2(request):
    # Verificar si el cliente_id está en la sesión
    cliente_id = request.session.get('cliente_id')

    asignacion_cliente = Cli064AsignacionCliente.objects.get(id_cliente_asignado=cliente_id)
    
    form = VacancyFormAllV2(cliente_id=cliente_id)

    if request.method == 'POST':
        form = VacancyFormAllV2(request.POST, cliente_id=cliente_id)

        if form.is_valid():
            # --- 1. Recolecta los datos de los campos JSON en listas de Python ---
            # Motivo de la vacante
            motivo_vacante_data = {
                "motivo": form.cleaned_data.get('motivo_vacante'),
                "otro_motivo": form.cleaned_data.get('otro_motivo')
            }

            # Horarios con estructura mejorada
            tipo_horario = form.cleaned_data.get('tipo_horario')
            horarios_data = {
                "tipo": tipo_horario,
                "bloques": []
            }
            
            for i in range(1, 4):
                horario_inicio = form.cleaned_data.get(f'horario_inicio_{i}')
                horario_final = form.cleaned_data.get(f'horario_final_{i}')
                hora_inicio = form.cleaned_data.get(f'hora_inicio_{i}')
                hora_final = form.cleaned_data.get(f'hora_final_{i}')
                
                if all([horario_inicio, horario_final, hora_inicio, hora_final]):
                    horarios_data["bloques"].append({
                        "dia_inicio": horario_inicio,
                        "dia_final": horario_final,
                        "hora_inicio": str(hora_inicio),
                        "hora_final": str(hora_final),
                        "bloque": i
                    })
            
            # Funciones y responsabilidades
            funciones_data = []
            for i in range(1,4):
                funcion = form.cleaned_data.get(f'funciones_responsabilidades_{i}')
                if funcion:
                    funciones_data.append({"bloque": i, "funcion": funcion})

            # Experiencia laboral
            experiencia_data = []
            for i in range(1,4):
                tiempo_experiencia = form.cleaned_data.get(f'tiempo_experiencia_{i}')
                experiencia_especifica = form.cleaned_data.get(f'experiencia_especifica_en_{i}')
                if tiempo_experiencia and experiencia_especifica:
                    experiencia_data.append({
                        "bloque": i,
                        "tiempo_experiencia" : tiempo_experiencia,
                        "experiencia_especifica" : experiencia_especifica,
                    })

            # Idiomas
            idiomas_data = []
            for i in range(1,3): # Asumiendo 2 bloques de idiomas
                idioma = form.cleaned_data.get(f'idioma_{i}')
                nivel_idioma = form.cleaned_data.get(f'nivel_idioma_{i}')
                if idioma and nivel_idioma:
                    idiomas_data.append({
                        "bloque": i,
                        "idioma" : idioma,
                        "nivel" : nivel_idioma,
                    })
            
            # Estudios complementarios
            estudios_data = []
            for i in range(1,4):
                estudio = form.cleaned_data.get(f'estudios_complementarios_{i}')
                certificado = form.cleaned_data.get(f'estudios_complementarios_certificado_{i}')
                if estudio: # Certificado puede ser False
                    estudios_data.append({
                        "bloque": i,
                        "estudio" : estudio,
                        "certificado" : certificado,
                    })

            # --- 2. Crea el Perfil de la Vacante pasando los objetos Python ---
            # Handle grupo_profesion field properly
            grupo_profesion_value = form.cleaned_data['grupo_profesion']
            grupo_profesion_obj = None
            if grupo_profesion_value and grupo_profesion_value != '':
                try:
                    grupo_profesion_obj = Cli075GrupoProfesion.objects.get(id=grupo_profesion_value)
                except Cli075GrupoProfesion.DoesNotExist:
                    grupo_profesion_obj = None
            
            # Handle profesion_estudio field properly
            profesion_estudio_value = form.cleaned_data['profesion_estudio']
            profesion_estudio_obj = None
            if profesion_estudio_value and profesion_estudio_value != '':
                try:
                    profesion_estudio_obj = Cli055ProfesionEstudio.objects.get(id=profesion_estudio_value)
                except Cli055ProfesionEstudio.DoesNotExist:
                    profesion_estudio_obj = None

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
            # Fit Cultural (Los campos son ModelChoiceField, no ModelMultipleChoiceField)
            fit_cultural_objects = []
            
            # Agregar cada selección individual si existe
            if form.cleaned_data.get('grupo_fit_1'):
                fit_cultural_objects.append(form.cleaned_data['grupo_fit_1'])
            if form.cleaned_data.get('grupo_fit_2'):
                fit_cultural_objects.append(form.cleaned_data['grupo_fit_2'])
            if form.cleaned_data.get('grupo_fit_3'):
                fit_cultural_objects.append(form.cleaned_data['grupo_fit_3'])
            if form.cleaned_data.get('grupo_fit_4'):
                fit_cultural_objects.append(form.cleaned_data['grupo_fit_4'])
            if form.cleaned_data.get('grupo_fit_5'):
                fit_cultural_objects.append(form.cleaned_data['grupo_fit_5'])

            #motivadores
            motivadores_candidato = form.cleaned_data.get('motivadores_candidato')

            #Comentarios 
            comentarios= form.cleaned_data.get('comentarios')
            descripcion_vacante = form.cleaned_data.get('descripcion_vacante')

            #creacion perfil de la vacante
            perfil_vacante = Cli073PerfilVacante.objects.create(
                edad_inicial=form.cleaned_data['edad_inicial'],
                edad_final=form.cleaned_data['edad_final'],
                genero=form.cleaned_data['genero'],
                tiempo_experiencia=1,
                modalidad=form.cleaned_data['modalidad'],
                salario=form.cleaned_data['salario'].replace('.', ''),
                tipo_salario=form.cleaned_data['tipo_salario'],
                frecuencia_pago=form.cleaned_data['frecuencia_pago'],
                salario_adicional=form.cleaned_data['salario_adicional'],
                profesion_estudio=profesion_estudio_obj,
                nivel_estudio=form.cleaned_data['nivel_estudio'],
                estado_estudio=form.cleaned_data['estado_estudio'],
                lugar_trabajo_id=form.cleaned_data['lugar_trabajo'],
                barrio=form.cleaned_data['barrio'],
                direccion=form.cleaned_data['direccion'],
                termino_contrato=form.cleaned_data['termino_contrato'],
                tipo_horario=tipo_horario,
                # Pasa las listas de Python directamente
                motivo_vacante=motivo_vacante_data,
                horario=horarios_data,
                experiencia_laboral=experiencia_data,
                idiomas=idiomas_data,
                estudio_complementario=estudios_data,
                funciones_responsabilidades=funciones_data,
                tipo_profesion=form.cleaned_data['tipo_profesion'],
                profesion_estudio_listado=form.cleaned_data['profesion_estudio_listado'],
                grupo_profesion=grupo_profesion_obj
            )

            # --- 3. Crea la Vacante ---
            cargo_obj = Cli068Cargo.objects.get(id=form.cleaned_data['cargo'])
            
            vacante = Cli052Vacante.objects.create(
                cargo=cargo_obj,
                numero_posiciones=form.cleaned_data['numero_posiciones'],
                cantidad_presentar=form.cleaned_data['cantidad_presentar'],
                titulo=f'Vacante para el cargo: {cargo_obj.nombre_cargo}',
                fecha_presentacion=form.cleaned_data['fecha_presentacion'],
                asignacion_cliente_id_064=asignacion_cliente,
                perfil_vacante=perfil_vacante,
                descripcion_vacante=form.cleaned_data.get('descripcion_vacante'),
                comentarios=form.cleaned_data.get('comentarios')
            )
            
            # Asignar motivadores múltiples
            motivadores_ids = form.cleaned_data.get('motivadores_candidato', [])
            if motivadores_ids:
                motivadores_objects = Cli078MotivadoresCandidato.objects.filter(id__in=motivadores_ids)
                vacante.motivadores.set(motivadores_objects)
            
            # 1. Combina todos los objetos skill del formulario en una sola lista
            skills_seleccionadas = (
                list(form.cleaned_data.get('skill_relacionales', [])) +
                list(form.cleaned_data.get('skill_personales', [])) +
                list(form.cleaned_data.get('skill_cognitivas', [])) +
                list(form.cleaned_data.get('skill_digitales', [])) +
                list(form.cleaned_data.get('skill_liderazgo', []))
            )

            # 2. Usa .set() en tu nuevo campo 'habilidades'. Django hace todo el trabajo.
            if skills_seleccionadas:
                vacante.habilidades.set(skills_seleccionadas)

            # Fit Cultural (Los campos son ModelChoiceField, no ModelMultipleChoiceField)
            if fit_cultural_objects:
                # .set() espera una lista de objetos o de IDs. Ambas funcionan.
                vacante.fit_cultural.set(fit_cultural_objects)
            
            messages.success(request, 'Vacante creada correctamente')
            return redirect('vacantes:vacantes_listado_cliente')
        else:
            messages.error(request, 'Por favor revise el formulario, errores encontrados.')
            
    else:
        form = VacancyFormAllV2(cliente_id=cliente_id)

    context = {
        'form': form,
    }

    return render(request, 'admin/vacancy/client_user/vacancy_create_v2.html', context)

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

    context ={ 
        'vacantes': vacantes,
    }

    return render(request, 'admin/vacancy/client_user/vacancy_list.html', context)


#gestionar la vacante
@login_required
@validar_permisos('acceso_cliente')
def vacancy_management_from_client(request, pk, vacante_id):
    # Verificar si el cliente_id está en la sesión
    cliente_id = request.session.get('cliente_id')
    form_errors = False
    
    # Data cliente a mostrar
    data = query_client_detail(pk)
    vacante = get_object_or_404(Cli052Vacante.objects.prefetch_related('habilidades'), id=vacante_id)
    

    # Obtener información de las entrevistas por vacante
    entrevistas = query_interview_all()
    entrevistas = entrevistas.filter(asignacion_vacante__vacante_id_052=vacante.id)

    # Obtener preguntas de la vacante
    preguntas = get_vacanty_questions(vacante.id)

    # Obtener los reclutados asociados a la vacante con estado_aplicacion = 8 (Seleccionado)
    reclutados = query_recruited_vacancy_id(vacante.id).filter(estado_aplicacion=8)
    
    # Para este template solo mostramos finalistas (estado_aplicacion = 8)
    reclutados_finalizalista = list(reclutados)
    
    # Mantener las otras listas vacías para compatibilidad con el template
    reclutados_recibido = []
    reclutados_seleccionado = []
    reclutados_descartado = []
    

    # Formularios para reclutar candidato y asignar analista a la vacante
    form_reclutados = ReclutadoCrearForm()
    form = VacancyAssingForm(cliente_id=cliente_id)
    form_reclutador = VacancyAssignRecruiterForm(cliente_id=cliente_id)
    analista_asignado = UsuarioBase.objects.filter(id=vacante.usuario_asignado_id).first()
    reclutador_asignado = UsuarioBase.objects.filter(id=vacante.asignacion_reclutador_id).first()

    context = {
        'data': data,
        'vacante': vacante,
        'reclutados': reclutados,
        'reclutados_recibido': reclutados_recibido,
        'reclutados_seleccionado': reclutados_seleccionado,
        'reclutados_finalizalista': reclutados_finalizalista,
        'reclutados_descartado': reclutados_descartado,
        'entrevistas': entrevistas,
        'form_reclutados' : form_reclutados,
        'preguntas': preguntas,
        'form': form,
        'form_reclutador': form_reclutador,
        'analista_asignado': analista_asignado,
        'reclutador_asignado': reclutador_asignado,
        'form_errors': form_errors,
    }
    return render(request, 'admin/vacancy/client_user/vacancy_management.html', context)


#detalle de la vacante
@login_required
@validar_permisos('acceso_admin', 'acceso_cliente', 'acceso_analista_seleccion_ats', 'acceso_analista_seleccion')
def detail_vacancy(request, pk):
    # Verificar si el cliente_id está en la sesión
    # cliente_id = request.session.get('cliente_id')
    vacante = Cli052Vacante.objects.get(id=pk)
    cliente_id = vacante.asignacion_cliente_id_064.id_cliente_asignado.id
    print(f'cliente_id: {cliente_id}')
    print(f'pk: {pk}')
    print(vacante)
    habilidades_guardadas = vacante.habilidades.all() 
    perfil_vacante = vacante.perfil_vacante

    # IDs de Skills extraídos de la tabla can_104_skill
    SKILLS_RELACIONALES_IDS = [1, 2, 3, 4, 5]
    SKILLS_PERSONALES_IDS = [6, 7, 8, 9, 10]
    SKILLS_COGNITIVAS_IDS = [11, 12, 13, 14, 15, 16]
    SKILLS_LIDERAZGO_IDS = [18, 19, 20, 21, 22]
    SKILLS_DIGITALES_IDS = [23, 24, 25, 26, 27]

    # IDs para FIT CULTURAL extraídos de la tabla cli_077_fit_cultural
    FIT_GRUPO_1_IDS = [1, 2, 3, 4]
    FIT_GRUPO_2_IDS = [5, 6, 7, 8]
    FIT_GRUPO_3_IDS = [9, 10, 11, 12, 13]
    FIT_GRUPO_4_IDS = [14, 15, 16]
    FIT_GRUPO_5_IDS = [17, 18, 19, 20]

    # Función para procesar profesion_estudio_listado
    def procesar_profesion_listado(listado_json):
        if not listado_json:
            return ""
        try:
            # Si es un string JSON, parsearlo y devolverlo como string JSON válido
            if isinstance(listado_json, str):
                # Verificar si ya es JSON válido
                try:
                    data = json.loads(listado_json)
                    # Si es una lista de objetos con 'value' e 'id', devolver el JSON original
                    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict) and 'value' in data[0]:
                        return listado_json
                    else:
                        # Si no tiene el formato esperado, convertirlo
                        return json.dumps([{"value": item, "id": i} for i, item in enumerate(data)])
                except json.JSONDecodeError:
                    # Si no es JSON válido, crear el formato correcto
                    return json.dumps([{"value": listado_json, "id": 0}])
            else:
                # Si ya es una lista o dict, convertirlo al formato correcto
                if isinstance(listado_json, list):
                    if len(listado_json) > 0 and isinstance(listado_json[0], dict) and 'value' in listado_json[0]:
                        return json.dumps(listado_json)
                    else:
                        return json.dumps([{"value": item, "id": i} for i, item in enumerate(listado_json)])
                else:
                    return json.dumps([{"value": str(listado_json), "id": 0}])
        except (json.JSONDecodeError, TypeError, AttributeError):
            # Si no es JSON válido, devolver como string simple
            return json.dumps([{"value": str(listado_json), "id": 0}]) if listado_json else ""

    # Construir initial data para el formulario
    initial = {
        'titulo': vacante.titulo,
        'cargo': vacante.cargo_id if vacante.cargo else None,
        'termino_contrato': perfil_vacante.termino_contrato if perfil_vacante else None,
        'modalidad': perfil_vacante.modalidad if perfil_vacante else None,
        'cantidad_presentar': vacante.cantidad_presentar,
        'numero_posiciones': vacante.numero_posiciones,
        'fecha_presentacion': vacante.fecha_presentacion.strftime('%Y-%m-%d') if vacante.fecha_presentacion else None,
        'barrio': perfil_vacante.barrio if perfil_vacante else None,
        'direccion': perfil_vacante.direccion if perfil_vacante else None,
        'salario': str(perfil_vacante.salario) if perfil_vacante and perfil_vacante.salario else None,
        'tipo_salario': perfil_vacante.tipo_salario if perfil_vacante else None,
        'frecuencia_pago': perfil_vacante.frecuencia_pago if perfil_vacante else None,
        'salario_adicional': perfil_vacante.salario_adicional if perfil_vacante else None,
        'edad_inicial': perfil_vacante.edad_inicial if perfil_vacante else None,
        'edad_final': perfil_vacante.edad_final if perfil_vacante else None,
        'genero': perfil_vacante.genero if perfil_vacante else None,
        'lugar_trabajo': perfil_vacante.lugar_trabajo_id if perfil_vacante and perfil_vacante.lugar_trabajo else None,
        'profesion_estudio': perfil_vacante.profesion_estudio_id if perfil_vacante and perfil_vacante.profesion_estudio else None,
        'nivel_estudio': perfil_vacante.nivel_estudio if perfil_vacante else None,
        'estado_estudio': perfil_vacante.estado_estudio if perfil_vacante else None,
        'cantidad_semestres': perfil_vacante.cantidad_semestres if perfil_vacante else None,
        'motivadores_candidato': list(vacante.motivadores.values_list('id', flat=True)) if vacante.motivadores.exists() else [],
        'comentarios': vacante.comentarios,
        'descripcion_vacante': vacante.descripcion_vacante,
        'tipo_profesion': perfil_vacante.tipo_profesion if perfil_vacante else None,
        'grupo_profesion': perfil_vacante.grupo_profesion_id if perfil_vacante and perfil_vacante.grupo_profesion else None,
        'profesion_estudio_listado': procesar_profesion_listado(perfil_vacante.profesion_estudio_listado) if perfil_vacante else None,
    }

    # Cargar skills correctamente por grupo
    initial['skill_relacionales'] = habilidades_guardadas.filter(id__in=SKILLS_RELACIONALES_IDS)
    initial['skill_personales'] = habilidades_guardadas.filter(id__in=SKILLS_PERSONALES_IDS)
    initial['skill_cognitivas'] = habilidades_guardadas.filter(id__in=SKILLS_COGNITIVAS_IDS)
    initial['skill_digitales'] = habilidades_guardadas.filter(id__in=SKILLS_DIGITALES_IDS)
    initial['skill_liderazgo'] = habilidades_guardadas.filter(id__in=SKILLS_LIDERAZGO_IDS)

    # Extraer datos de campos JSON del perfil_vacante
    if perfil_vacante:
        # Motivo de la vacante
        if perfil_vacante.motivo_vacante and isinstance(perfil_vacante.motivo_vacante, dict):
            initial['motivo_vacante'] = perfil_vacante.motivo_vacante.get('motivo', '')
            initial['otro_motivo'] = perfil_vacante.motivo_vacante.get('otro_motivo', '')

        # Horarios
        if perfil_vacante.horario:
            for horario in perfil_vacante.horario:
                if isinstance(horario, dict):  # <-- Verificación aplicada
                    bloque = horario.get('bloque', 1)
                    initial[f'horario_inicio_{bloque}'] = horario.get('dia_inicio', '')
                    initial[f'horario_final_{bloque}'] = horario.get('dia_final', '')
                    initial[f'hora_inicio_{bloque}'] = horario.get('hora_inicio', '')
                    initial[f'hora_final_{bloque}'] = horario.get('hora_final', '')

        # Experiencia laboral
        if perfil_vacante.experiencia_laboral:
            for exp in perfil_vacante.experiencia_laboral:
                if isinstance(exp, dict):  # <-- Verificación aplicada
                    bloque = exp.get('bloque', 1)
                    initial[f'tiempo_experiencia_{bloque}'] = exp.get('tiempo_experiencia', '')
                    initial[f'experiencia_especifica_en_{bloque}'] = exp.get('experiencia_especifica', '')

        # Idiomas
        if perfil_vacante.idiomas:
            for idioma in perfil_vacante.idiomas:
                if isinstance(idioma, dict):  # <-- Verificación aplicada
                    bloque = idioma.get('bloque', 1)
                    initial[f'idioma_{bloque}'] = idioma.get('idioma', '')
                    initial[f'nivel_idioma_{bloque}'] = idioma.get('nivel', '')

        # Estudios complementarios
        if perfil_vacante.estudio_complementario:
            for estudio in perfil_vacante.estudio_complementario:
                if isinstance(estudio, dict):  # <-- Verificación aplicada
                    bloque = estudio.get('bloque', 1)
                    initial[f'estudios_complementarios_{bloque}'] = estudio.get('estudio', '')
                    initial[f'estudios_complementarios_certificado_{bloque}'] = estudio.get('certificado', '')

        # Funciones y responsabilidades
        if perfil_vacante.funciones_responsabilidades:
            for funcion in perfil_vacante.funciones_responsabilidades:
                if isinstance(funcion, dict):  # <-- Verificación aplicada
                    bloque = funcion.get('bloque', 1)
                    initial[f'funciones_responsabilidades_{bloque}'] = funcion.get('funcion', '')

    # Fit cultural
    initial['grupo_fit_1'] = list(vacante.fit_cultural.filter(id__in=FIT_GRUPO_1_IDS).values_list('id', flat=True))
    initial['grupo_fit_2'] = list(vacante.fit_cultural.filter(id__in=FIT_GRUPO_2_IDS).values_list('id', flat=True))
    initial['grupo_fit_3'] = list(vacante.fit_cultural.filter(id__in=FIT_GRUPO_3_IDS).values_list('id', flat=True))
    initial['grupo_fit_4'] = list(vacante.fit_cultural.filter(id__in=FIT_GRUPO_4_IDS).values_list('id', flat=True))
    initial['grupo_fit_5'] = list(vacante.fit_cultural.filter(id__in=FIT_GRUPO_5_IDS).values_list('id', flat=True))

    if request.method == 'POST':
        form = VacancyFormAllV2(request.POST, cliente_id=cliente_id)
        if form.is_valid():

            # Update existing data
            vacante.titulo = form.cleaned_data['titulo']
            vacante.cargo = Cli068Cargo.objects.get(id=form.cleaned_data['cargo'])
            vacante.numero_posiciones = form.cleaned_data['numero_posiciones']
            vacante.cantidad_presentar = form.cleaned_data['cantidad_presentar']
            vacante.fecha_presentacion = form.cleaned_data['fecha_presentacion']
            vacante.descripcion_vacante = form.cleaned_data['descripcion_vacante']
            vacante.comentarios = form.cleaned_data['comentarios']
            # Actualizar motivadores múltiples
            motivadores_ids = form.cleaned_data.get('motivadores_candidato', [])
            if motivadores_ids:
                motivadores_objects = Cli078MotivadoresCandidato.objects.filter(id__in=motivadores_ids)
                vacante.motivadores.set(motivadores_objects)
            else:
                vacante.motivadores.clear()

            vacante.save()

            # Update perfil_vacante
            perfil_vacante = vacante.perfil_vacante
            perfil_vacante.edad_inicial = form.cleaned_data['edad_inicial']
            perfil_vacante.edad_final = form.cleaned_data['edad_final']
            perfil_vacante.genero = form.cleaned_data['genero']
            perfil_vacante.modalidad = form.cleaned_data['modalidad']
            perfil_vacante.salario = form.cleaned_data['salario'].replace('.', '') if form.cleaned_data['salario'] else None
            perfil_vacante.tipo_salario = form.cleaned_data['tipo_salario']
            perfil_vacante.frecuencia_pago = form.cleaned_data['frecuencia_pago']
            perfil_vacante.salario_adicional = form.cleaned_data['salario_adicional']
            perfil_vacante.profesion_estudio = Cli055ProfesionEstudio.objects.get(id=form.cleaned_data['profesion_estudio']) if form.cleaned_data['profesion_estudio'] else None
            perfil_vacante.nivel_estudio = form.cleaned_data['nivel_estudio']
            perfil_vacante.estado_estudio = form.cleaned_data['estado_estudio']
            perfil_vacante.cantidad_semestres = form.cleaned_data['cantidad_semestres']
            perfil_vacante.lugar_trabajo = Cat004Ciudad.objects.get(id=form.cleaned_data['lugar_trabajo']) if form.cleaned_data['lugar_trabajo'] else None
            perfil_vacante.termino_contrato = form.cleaned_data['termino_contrato']
            perfil_vacante.barrio = form.cleaned_data['barrio']
            perfil_vacante.direccion = form.cleaned_data['direccion']
            perfil_vacante.tipo_profesion = form.cleaned_data['tipo_profesion']
            perfil_vacante.grupo_profesion = Cli075GrupoProfesion.objects.get(id=form.cleaned_data['grupo_profesion']) if form.cleaned_data['grupo_profesion'] else None
            perfil_vacante.profesion_estudio_listado = form.cleaned_data['profesion_estudio_listado']
            
            # Guardar datos JSON
            # Motivo de la vacante
            motivo_vacante_data = {
                'motivo': form.cleaned_data['motivo_vacante'],
                'otro_motivo': form.cleaned_data['otro_motivo'] if form.cleaned_data['motivo_vacante'] == 'Otro' else None
            }
            perfil_vacante.motivo_vacante = motivo_vacante_data
            
            # Horarios (múltiples bloques)
            horarios_data = []
            for i in range(1, 4):
                horario_inicio = form.cleaned_data.get(f'horario_inicio_{i}')
                horario_final = form.cleaned_data.get(f'horario_final_{i}')
                hora_inicio = form.cleaned_data.get(f'hora_inicio_{i}')
                hora_final = form.cleaned_data.get(f'hora_final_{i}')
                
                if all([horario_inicio, horario_final, hora_inicio, hora_final]):
                    horarios_data.append({
                        'bloque': i,
                        'dia_inicio': horario_inicio,
                        'dia_final': horario_final,
                        'hora_inicio': str(hora_inicio),
                        'hora_final': str(hora_final)
                    })
            perfil_vacante.horario = horarios_data
            
            # Experiencia laboral
            experiencia_data = []
            for i in range(1, 4):
                tiempo_experiencia = form.cleaned_data.get(f'tiempo_experiencia_{i}')
                experiencia_especifica = form.cleaned_data.get(f'experiencia_especifica_en_{i}')
                
                if tiempo_experiencia and experiencia_especifica:
                    experiencia_data.append({
                        'bloque': i,
                        'tiempo_experiencia': tiempo_experiencia,
                        'experiencia_especifica': experiencia_especifica
                    })
            perfil_vacante.experiencia_laboral = experiencia_data
            
            # Idiomas
            idiomas_data = []
            for i in range(1, 3):
                idioma = form.cleaned_data.get(f'idioma_{i}')
                nivel_idioma = form.cleaned_data.get(f'nivel_idioma_{i}')
                
                if idioma and nivel_idioma:
                    idiomas_data.append({
                        'bloque': i,
                        'idioma': idioma,
                        'nivel': nivel_idioma
                    })
            perfil_vacante.idiomas = idiomas_data
            
            # Estudios complementarios
            estudios_data = []
            for i in range(1, 4):
                estudio = form.cleaned_data.get(f'estudios_complementarios_{i}')
                certificado = form.cleaned_data.get(f'estudios_complementarios_certificado_{i}')
                
                if estudio and certificado is not None:
                    estudios_data.append({
                        'bloque': i,
                        'estudio': estudio,
                        'certificado': certificado
                    })
            perfil_vacante.estudio_complementario = estudios_data
            
            # Funciones y responsabilidades
            funciones_data = []
            for i in range(1, 4):
                funcion = form.cleaned_data.get(f'funciones_responsabilidades_{i}')
                if funcion:
                    funciones_data.append({
                        'bloque': i,
                        'funcion': funcion
                    })
            perfil_vacante.funciones_responsabilidades = funciones_data
            
            perfil_vacante.save()

            # Update skills (ManyToMany fields)
            # 1. Recolecta todos los objetos 'skill' del formulario en una sola lista
            skills_seleccionadas = (
                list(form.cleaned_data.get('skill_relacionales', [])) +
                list(form.cleaned_data.get('skill_personales', [])) +
                list(form.cleaned_data.get('skill_cognitivas', [])) +
                list(form.cleaned_data.get('skill_digitales', [])) +
                list(form.cleaned_data.get('skill_liderazgo', []))
            )

            # 2. ✅ Usa .set() para actualizar la relación.
            # Esto borra las habilidades viejas y agrega las nuevas automáticamente.
            vacante.habilidades.set(skills_seleccionadas)
            
            # Fit Cultural (Los campos son ModelChoiceField, no ModelMultipleChoiceField)
            vacante.fit_cultural.clear()
            fit_cultural_objects = []
            
            # Agregar cada selección individual si existe
            if form.cleaned_data.get('grupo_fit_1'):
                fit_cultural_objects.append(form.cleaned_data['grupo_fit_1'])
            if form.cleaned_data.get('grupo_fit_2'):
                fit_cultural_objects.append(form.cleaned_data['grupo_fit_2'])
            if form.cleaned_data.get('grupo_fit_3'):
                fit_cultural_objects.append(form.cleaned_data['grupo_fit_3'])
            if form.cleaned_data.get('grupo_fit_4'):
                fit_cultural_objects.append(form.cleaned_data['grupo_fit_4'])
            if form.cleaned_data.get('grupo_fit_5'):
                fit_cultural_objects.append(form.cleaned_data['grupo_fit_5'])
            
            if fit_cultural_objects:
                vacante.fit_cultural.add(*fit_cultural_objects)
            
            messages.success(request, 'Vacante editada correctamente')
            return redirect('vacantes:vacantes_propias', pk=pk)
        else:
            messages.error(request, 'Por favor revise el formulario, errores encontrados.')

    else:
        form = VacancyFormAllV2(initial=initial, cliente_id=cliente_id)

    context ={
        'vacante': vacante,
        'form': form,
    }

    return render(request, 'admin/vacancy/client_user/vacancy_detail.html', context)

#detalle de la vacante
@login_required
@validar_permisos('acceso_admin', 'acceso_cliente', 'acceso_analista_seleccion_ats')
def detail_vacancy_interview(request, pk):
    # Verificar si el cliente_id está en la sesión
    cliente_id = request.session.get('cliente_id')
    
    # Obtener información de la vacante
    vacante = query_vacanty_detail().get(id=pk)

    # Obtener información de las entrevistas por vacante
    entrevistas = query_interview_all()
    entrevistas = entrevistas.filter(asignacion_vacante__vacante_id_052=pk)
    

    context ={
        'vacante': vacante,
        'entrevistas': entrevistas,
    }

    return render(request, 'admin/vacancy/client_user/vacancy_detail_interview.html', context)

#detalle de la vacante
@login_required
@validar_permisos('acceso_admin', 'acceso_cliente')
def detail_vacancy_assign(request, pk):
    # Verificar si el cliente_id está en la sesión
    cliente_id = request.session.get('cliente_id')
    
    # Obtener información de la vacante
    vacante = query_vacanty_detail().get(id=pk)
    print(vacante.usuario_asignado_id)
    analista_asignado = UsuarioBase.objects.filter(id=vacante.usuario_asignado_id).first()

    form = VacancyAssingForm(cliente_id=cliente_id)

    if request.method == 'POST':
        form = VacancyAssingForm(request.POST, cliente_id=cliente_id)
        if form.is_valid():
            analista_asignado = form.cleaned_data['analista_asignado']

            vacante.usuario_asignado = get_object_or_404(UsuarioBase, id=analista_asignado)
            vacante.save()
            
            messages.success(request, 'Analista asignado correctamente')
            return redirect('vacantes:vacantes_asignar_analista_cliente', pk=pk)
        else:
            print(form.errors)
    else:
        form = VacancyAssingForm(cliente_id=cliente_id)

    context ={
        'vacante': vacante,
        'form': form,
        'analista_asignado': analista_asignado,
    }

    return render(request, 'admin/vacancy/client_user/vacancy_detail_assign.html', context)

#@login_required
#@validar_permisos('acceso_cliente')
def vacancy_client_assigned(request):
    # Verificar si el cliente_id está en la sesión
    cliente_id = request.session.get('cliente_id')
    
    vacantes = query_vacanty_all()
    vacantes = vacantes.filter(
        asignacion_cliente_id_064__id_cliente_maestro=cliente_id,
        asignacion_cliente_id_064__tipo_asignacion='2'
    )

    context ={
        'vacantes': vacantes,
    }

    return render(request, 'admin/vacancy/client_user/headhunter/vacancy_client_assigned.html', context)