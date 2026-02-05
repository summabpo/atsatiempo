from datetime import datetime
import os
from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.contrib.auth.decorators import login_required
from django.contrib import messages


from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.usuarios.decorators  import validar_permisos

#models
from applications.candidato.models import Can101Candidato, Can102Experiencia, Can103Educacion, Can104Skill, Can101CandidatoSkill, Can105RedSocial, Can106CandidatoRed


#forms
from applications.candidato.forms.CandidatoForms import CandidateForm
from applications.candidato.forms.EstudioForms import EstudioCandidatoForm, candidateStudyForm
from applications.candidato.forms.ExperienciaForms import candidateJobForm
from applications.candidato.forms.HabilidadForms import CandidateHabilityForm, CandidateHabilityFormList
from applications.candidato.forms.SocialForms import SocialNetworkForm

from collections import Counter

from applications.usuarios.models import UsuarioBase

#views
@login_required
@validar_permisos('acceso_candidato')
def candidate_info(request):

    candidato_id = request.session.get('candidato_id')
    
    candidato = get_object_or_404(Can101Candidato, pk=candidato_id)

    if request.method == 'POST':
        # Inicializar files_saved_in_request
        files_saved_in_request = {
            'imagen_perfil': False,
            'hoja_de_vida': False,
            'video_perfil': False,
        }
        
        # Validar y guardar archivos primero si son válidos
        files_saved = False
        file_errors = {}
        
        # Guardar archivos sin validaciones - permitir todos los archivos
        if 'imagen_perfil' in request.FILES:
            imagen_perfil = request.FILES['imagen_perfil']
            candidato.imagen_perfil = imagen_perfil
            files_saved = True
            files_saved_in_request['imagen_perfil'] = True
        
        if 'hoja_de_vida' in request.FILES:
            hoja_de_vida = request.FILES['hoja_de_vida']
            candidato.hoja_de_vida = hoja_de_vida
            files_saved = True
            files_saved_in_request['hoja_de_vida'] = True
        
        if 'video_perfil' in request.FILES:
            video_perfil = request.FILES['video_perfil']
            candidato.video_perfil = video_perfil
            files_saved = True
            files_saved_in_request['video_perfil'] = True
        
        # Crear el formulario DESPUÉS de validar y guardar archivos, pasando files_saved_in_request actualizado
        form = CandidateForm(request.POST, request.FILES, instance=candidato, files_saved_in_request=files_saved_in_request)
        
        # Si hay errores en archivos, agregarlos al formulario
        for field, error_msg in file_errors.items():
            form.add_error(field, error_msg)
        
        # Si se guardaron archivos, guardar el candidato inmediatamente
        if files_saved:
            candidato.save()
            # Actualizar imagen de perfil en el usuario si se guardó una nueva
            if 'imagen_perfil' in request.FILES and 'imagen_perfil' not in file_errors:
                usuario = UsuarioBase.objects.get(id=request.session.get('user_login')['id'])
                usuario.imagen_perfil = candidato.imagen_perfil
                usuario.save()
            # Recargar el candidato para que el formulario tenga los archivos actualizados
            candidato.refresh_from_db()
            # NO mostrar mensaje aquí - solo se mostrará cuando el formulario se procese correctamente

        if form.is_valid():
            candidato.numero_documento = form.cleaned_data['numero_documento']
            candidato.primer_nombre = form.cleaned_data['primer_nombre']
            candidato.segundo_nombre = form.cleaned_data['segundo_nombre']
            candidato.primer_apellido = form.cleaned_data['primer_apellido']
            candidato.segundo_apellido = form.cleaned_data['segundo_apellido']
            candidato.ciudad_id_004 = form.cleaned_data['ciudad_id_004']
            candidato.sexo = form.cleaned_data['sexo']
            candidato.fecha_nacimiento = form.cleaned_data['fecha_nacimiento']
            candidato.telefono = form.cleaned_data['telefono']
            candidato.direccion = form.cleaned_data['direccion']
            # Los archivos ya fueron guardados arriba si eran válidos, NO sobrescribirlos
            # Solo actualizar si hay un nuevo archivo en el formulario que no se guardó antes
            if 'imagen_perfil' in request.FILES and 'imagen_perfil' not in file_errors and not files_saved_in_request['imagen_perfil']:
                # Hay un nuevo archivo que no se guardó antes, guardarlo ahora
                candidato.imagen_perfil = request.FILES['imagen_perfil']
            # Si ya se guardó antes, no hacer nada (mantener el que ya está guardado)
            
            if 'hoja_de_vida' in request.FILES and 'hoja_de_vida' not in file_errors and not files_saved_in_request['hoja_de_vida']:
                candidato.hoja_de_vida = request.FILES['hoja_de_vida']
            
            if 'video_perfil' in request.FILES and 'video_perfil' not in file_errors and not files_saved_in_request['video_perfil']:
                candidato.video_perfil = request.FILES['video_perfil']
            
            candidato.email = form.cleaned_data['email']
            candidato.perfil = form.cleaned_data['perfil']
            
            # Combinar todos los campos de fit cultural de los diferentes grupos
            fit_cultural_objs = []
            for i in range(1, 6):  # grupo_fit_1 a grupo_fit_5
                grupo_field = f'grupo_fit_{i}'
                if grupo_field in form.cleaned_data and form.cleaned_data[grupo_field]:
                    # Ahora cada campo es una selección única, no una lista
                    fit_cultural_objs.append(form.cleaned_data[grupo_field])
            
            # Guardar la estructura de fit_cultural como lista de diccionarios con id y nombre
            if fit_cultural_objs:
                fit_cultural_data = [
                    {"id": fc.id, "nombre": fc.nombre}
                    for fc in fit_cultural_objs
                ]
                candidato.fit_cultural = fit_cultural_data
            else:
                candidato.fit_cultural = []
            motivadores_objs = form.cleaned_data['motivadores']
            if motivadores_objs:
                motivadores_data = [
                    {"id": m.id, "nombre": m.nombre}
                    for m in motivadores_objs
                ]
                candidato.motivadores = motivadores_data
            else:
                candidato.motivadores = []
            
            UsuarioBase.objects.get(id=request.session.get('user_login')['id']).candidato_id_101 = candidato
            usuario = UsuarioBase.objects.get(id=request.session.get('user_login')['id'])
            # Actualizar la imagen de perfil en el usuario si hay una nueva
            if candidato.imagen_perfil:
                usuario.imagen_perfil = candidato.imagen_perfil
            usuario.save()
            
            candidato.save()

            # Mostrar mensaje de éxito solo cuando el formulario se procesa correctamente
            messages.success(request, 'Información básica actualizada exitosamente.')

            return redirect('candidatos:candidato_info_personal')
        else:
            print(form.errors)
            # Si los archivos ya se guardaron, no mostrar error general, solo los errores específicos
            if not files_saved:
                messages.error(request, 'Error al actualizar la información básica.')
            # Si hay error, recrear el formulario pero manteniendo los archivos de request.FILES
            # para que se puedan reutilizar en el siguiente envío
            form = CandidateForm(request.POST, request.FILES, instance=candidato, files_saved_in_request=files_saved_in_request)
    else:
        initial_data = {
            'email': candidato.email,
            'primer_nombre': candidato.primer_nombre,
            'segundo_nombre': candidato.segundo_nombre,
            'primer_apellido': candidato.primer_apellido,
            'segundo_apellido': candidato.segundo_apellido,
            'ciudad_id_004': candidato.ciudad_id_004.id if candidato.ciudad_id_004 else None,
            'sexo': candidato.sexo,
            'fecha_nacimiento': candidato.fecha_nacimiento.strftime('%Y-%m-%d') if candidato.fecha_nacimiento else '',
            'telefono': candidato.telefono,
            # 'skills': candidato.skills.all(),  # Si el form no tiene este campo, omitirlo
            # Los campos de archivo no se pasan en initial, se muestran en el form por el instance
            'numero_documento': candidato.numero_documento,
            'direccion': candidato.direccion,
            'perfil': candidato.perfil,
            # Inicializar campos de fit cultural por grupo
            'grupo_fit_1': None,
            'grupo_fit_2': None,
            'grupo_fit_3': None,
            'grupo_fit_4': None,
            'grupo_fit_5': None,
            'motivadores': [item['id'] for item in candidato.motivadores] if candidato.motivadores else [],
            'aspiracion_salarial': candidato.aspiracion_salarial,
            'imagen_perfil': candidato.imagen_perfil,
            'hoja_de_vida': candidato.hoja_de_vida,
            'video_perfil': candidato.video_perfil,
        }
        
        # Distribuir los datos de fit_cultural en los campos correspondientes por grupo
        if candidato.fit_cultural:
            from applications.cliente.models import Cli077FitCultural
            for item in candidato.fit_cultural:
                try:
                    fit_obj = Cli077FitCultural.objects.get(id=item['id'])
                    grupo_field = f'grupo_fit_{fit_obj.grupo.id}'
                    if grupo_field in initial_data:
                        initial_data[grupo_field] = fit_obj.id
                except Cli077FitCultural.DoesNotExist:
                    continue
        
        form = CandidateForm(initial=initial_data, instance=candidato)

    # Obtener descripciones de fit cultural para tooltips
    from applications.cliente.models import Cli077FitCultural
    import json
    fit_cultural_descriptions = {}
    fit_cultural_items = Cli077FitCultural.objects.filter(estado=1).select_related('grupo')
    for item in fit_cultural_items:
        if item.descripcion:
            fit_cultural_descriptions[str(item.id)] = item.descripcion

    # Calcular porcentajes de completitud
    from applications.services.service_candidate import personal_information_calculation
    porcentajes = personal_information_calculation(candidato.id)
    
    # Calcular porcentaje de redes sociales
    from applications.candidato.models import Can106CandidatoRed
    socialNetwork = Can106CandidatoRed.objects.filter(candidato_id_101=candidato.id, estado_id_001=1)
    if socialNetwork.exists():
        porcentaje_redes = 100
    else:
        porcentaje_redes = 0
    
    porcentajes['redes_sociales'] = {
        'porcentaje': porcentaje_redes,
        'campos': {
            'total': 1,
            'llenos': 1 if socialNetwork.exists() else 0,
        }
    }
    
    # Recalcular porcentaje total incluyendo las 5 secciones
    porcentajes['porcentaje_total'] = int((
        porcentajes['info_personal']['porcentaje'] + 
        porcentajes['educacion']['porcentaje'] + 
        porcentajes['experiencia']['porcentaje'] + 
        porcentajes['skills']['porcentaje'] + 
        porcentajes['redes_sociales']['porcentaje']
    ) / 5)

    context = {
        'form': form,
        'candidato': candidato,  # Agregar el candidato al contexto para mostrar el video
        'fit_cultural_descriptions': json.dumps(fit_cultural_descriptions),  # Pasar como JSON
        'porcentajes': porcentajes,
        'active_section': 'personal',
        'files_saved_in_request': {
            'imagen_perfil': False,
            'hoja_de_vida': False,
            'video_perfil': False,
        }
    }
    
    # Si se guardaron archivos en esta petición, indicarlo en el contexto
    if request.method == 'POST':
        if 'files_saved_in_request' in locals():
            context['files_saved_in_request'] = files_saved_in_request

    return render(request, 'admin/candidate/candidate_user/info_personal.html', context)

@login_required
@validar_permisos('acceso_candidato')
def candidate_info_academy(request):
    form_errors = False
    candidato_id = request.session.get('candidato_id')

    studies = Can103Educacion.objects.filter(candidato_id_101=candidato_id).order_by('-fecha_inicial')
    form = candidateStudyForm()

    if request.method == 'POST':
        form = candidateStudyForm(request.POST, request.FILES)
        if form.is_valid():
            institucion = form.cleaned_data['institucion']
            grado_en = form.cleaned_data['grado_en']
            fecha_inicial = form.cleaned_data['fecha_inicial']
            fecha_final = form.cleaned_data['fecha_final'] if form.cleaned_data['fecha_final'] else None
            titulo = form.cleaned_data['titulo'] if form.cleaned_data['titulo'] else None
            # carrera = form.cleaned_data['carrera']
            # fortaleza_adquiridas = form.cleaned_data['fortaleza_adquiridas']
            candidato_id_101 = Can101Candidato.objects.get(id=candidato_id)
            ciudad_obj_004 = form.cleaned_data['ciudad_id_004']
            tipo_estudio = form.cleaned_data['tipo_estudio']
            if form.cleaned_data['certificacion']:
                certificacion = form.cleaned_data['certificacion']
            
            profesion_estudio = form.cleaned_data['profesion_estudio'] if form.cleaned_data['profesion_estudio'] else None
            
            Can103Educacion.objects.create(
                estado_id_001=Cat001Estado.objects.get(id=1),  # Cambia esto según tu lógica
                institucion=institucion,
                grado_en=grado_en,
                fecha_inicial=fecha_inicial,
                fecha_final=fecha_final,
                titulo=titulo,
                # carrera=carrera,
                # fortaleza_adquiridas=fortaleza_adquiridas,
                candidato_id_101=candidato_id_101,
                ciudad_id_004=ciudad_obj_004,
                tipo_estudio=tipo_estudio,
                certificacion=certificacion if form.cleaned_data['certificacion'] else None,
                profesion_estudio= profesion_estudio if profesion_estudio else None
            )
            
            messages.success(request, 'Información académica actualizada exitosamente.')
            return redirect('candidatos:candidato_info_academica')
        else:
            form_errors = True
            messages.error(request, 'Error al actualizar la información académica.')
    else:
        form = candidateStudyForm(request.POST or None)

    # Calcular porcentajes de completitud
    from applications.services.service_candidate import personal_information_calculation
    candidato = Can101Candidato.objects.get(id=candidato_id)
    porcentajes = personal_information_calculation(candidato.id)
    
    # Calcular porcentaje de redes sociales
    from applications.candidato.models import Can106CandidatoRed
    socialNetwork = Can106CandidatoRed.objects.filter(candidato_id_101=candidato.id, estado_id_001=1)
    if socialNetwork.exists():
        porcentaje_redes = 100
    else:
        porcentaje_redes = 0
    
    porcentajes['redes_sociales'] = {
        'porcentaje': porcentaje_redes,
        'campos': {
            'total': 1,
            'llenos': 1 if socialNetwork.exists() else 0,
        }
    }
    
    # Recalcular porcentaje total incluyendo las 5 secciones
    porcentajes['porcentaje_total'] = int((
        porcentajes['info_personal']['porcentaje'] + 
        porcentajes['educacion']['porcentaje'] + 
        porcentajes['experiencia']['porcentaje'] + 
        porcentajes['skills']['porcentaje'] + 
        porcentajes['redes_sociales']['porcentaje']
    ) / 5)

    context = {
        'studies': studies,
        'form': form,
        'form_errors': form_errors,
        'porcentajes': porcentajes,
        'active_section': 'academica',
    }
    return render(request, 'admin/candidate/candidate_user/info_academy.html', context)

@login_required
@validar_permisos('acceso_candidato')
def candidate_info_academy_edit(request, pk):
    study = get_object_or_404(Can103Educacion, pk=pk)
    form_errors = False

    initial = {
        'institucion': study.institucion,
        'fecha_inicial': study.fecha_inicial.strftime('%Y-%m-%d') if study.fecha_inicial else '',
        'fecha_final': study.fecha_final.strftime('%Y-%m-%d') if study.fecha_final else '',
        'grado_en': study.grado_en,
        'titulo': study.titulo,
        # 'carrera': study.carrera,
        # 'fortaleza_adquiridas': study.fortaleza_adquiridas,
        'ciudad_id_004': study.ciudad_id_004.id if study.ciudad_id_004 else None,
        'tipo_estudio': study.tipo_estudio,
        'certificacion': study.certificacion,
        'profesion_estudio': study.profesion_estudio.id if study.profesion_estudio else None,
    }

    if request.method == 'POST':
        form = candidateStudyForm(request.POST, request.FILES, initial=initial)
        if form.is_valid():

            study.institucion = form.cleaned_data['institucion']
            study.grado_en = form.cleaned_data['grado_en']
            study.fecha_inicial = form.cleaned_data['fecha_inicial']
            study.fecha_final = form.cleaned_data['fecha_final'] if form.cleaned_data['fecha_final'] else None
            study.titulo = form.cleaned_data['titulo'] if form.cleaned_data['titulo'] else None
            # study.carrera = form.cleaned_data['carrera']
            # study.fortaleza_adquiridas = form.cleaned_data['fortaleza_adquiridas']
            study.candidato_id_101 = Can101Candidato.objects.get(id=request.session.get('candidato_id'))
            study.ciudad_id_004 = form.cleaned_data['ciudad_id_004']
            study.tipo_estudio = form.cleaned_data['tipo_estudio']
            if form.cleaned_data['certificacion']:
                study.certificacion = form.cleaned_data['certificacion']
            study.profesion_estudio = form.cleaned_data['profesion_estudio'] if form.cleaned_data['profesion_estudio'] else None
            study.save()

            messages.success(request, 'Información académica actualizada exitosamente.')
            return redirect('candidatos:candidato_info_academica')
        else:
            form_errors = True
            messages.error(request, 'Error al actualizar la información académica.')
    else:
        form = candidateStudyForm(initial=initial)

    context = {
        'form': form,
        'form_errors': form_errors,
    }
    return render(request, 'admin/candidate/candidate_user/info_academy_edit.html', context)

@login_required
@validar_permisos('acceso_candidato')
def candidate_info_job(request):
    form_errors = False
    candidato_id = request.session.get('candidato_id')

    jobs = Can102Experiencia.objects.filter(candidato_id_101=candidato_id).order_by('-fecha_inicial')
    
    if request.method == 'POST':
        form = candidateJobForm(request.POST)
        if form.is_valid():
            entidad = form.cleaned_data['entidad']
            sector = form.cleaned_data['sector']
            fecha_inicial = form.cleaned_data['fecha_inicial']
            fecha_final = form.cleaned_data['fecha_final'] if form.cleaned_data['fecha_final'] else None
            activo = form.cleaned_data['activo']
            logro = form.cleaned_data['logro']
            candidato_id_101 = Can101Candidato.objects.get(id=candidato_id)
            cargo = form.cleaned_data['cargo']
            motivo_salida = form.cleaned_data['motivo_salida']
            salario = form.cleaned_data['salario'] if form.cleaned_data['salario'] else None
            modalidad_trabajo = form.cleaned_data['modalidad_trabajo']
            nombre_jefe = form.cleaned_data['nombre_jefe'] if form.cleaned_data['nombre_jefe'] else None

            Can102Experiencia.objects.create(
                estado_id_001=Cat001Estado.objects.get(id=1),  # Cambia esto según tu lógica
                entidad=entidad,
                sector=sector,
                fecha_inicial=fecha_inicial,
                fecha_final=fecha_final,
                activo=activo,
                logro=logro,
                candidato_id_101=candidato_id_101,
                cargo=cargo,
                motivo_salida=motivo_salida,
                salario=salario,
                modalidad_trabajo=modalidad_trabajo,
                nombre_jefe=nombre_jefe
            )
            
            messages.success(request, 'Información laboral actualizada exitosamente.')
            return redirect('candidatos:candidato_info_laboral')
        else:
            form_errors = True
            messages.error(request, 'Error al crear la información laboral.')
    else:
        form = candidateJobForm()

    # Calcular porcentajes de completitud
    from applications.services.service_candidate import personal_information_calculation
    candidato = Can101Candidato.objects.get(id=candidato_id)
    porcentajes = personal_information_calculation(candidato.id)
    
    # Calcular porcentaje de redes sociales
    from applications.candidato.models import Can106CandidatoRed
    socialNetwork = Can106CandidatoRed.objects.filter(candidato_id_101=candidato.id, estado_id_001=1)
    if socialNetwork.exists():
        porcentaje_redes = 100
    else:
        porcentaje_redes = 0
    
    porcentajes['redes_sociales'] = {
        'porcentaje': porcentaje_redes,
        'campos': {
            'total': 1,
            'llenos': 1 if socialNetwork.exists() else 0,
        }
    }
    
    # Recalcular porcentaje total incluyendo las 5 secciones
    porcentajes['porcentaje_total'] = int((
        porcentajes['info_personal']['porcentaje'] + 
        porcentajes['educacion']['porcentaje'] + 
        porcentajes['experiencia']['porcentaje'] + 
        porcentajes['skills']['porcentaje'] + 
        porcentajes['redes_sociales']['porcentaje']
    ) / 5)

    context = {
        'jobs': jobs,
        'form': form,
        'form_errors': form_errors,
        'porcentajes': porcentajes,
        'active_section': 'laboral',
    }
    return render(request, 'admin/candidate/candidate_user/info_job.html', context)

@login_required
@validar_permisos('acceso_candidato')
def candidate_info_job_edit(request, pk):
    # Obtener el ID del candidato desde la sesión
    candidato_id = request.session.get('candidato_id')

    # Obtener la experiencia laboral del candidato (ajusta según tu modelo)
    job = Can102Experiencia.objects.get(id=pk)


    # Inicializar el formulario con los datos de la experiencia laboral
    initial={
        'entidad': job.entidad,
        'sector': job.sector,
        'fecha_inicial': job.fecha_inicial.strftime('%Y-%m-%d') if job.fecha_inicial else '',
        'fecha_final': job.fecha_final.strftime('%Y-%m-%d') if job.fecha_final else '',
        'activo': job.activo,
        'logro': job.logro,
        'cargo': job.cargo,
        'motivo_salida': job.motivo_salida,
        'salario': job.salario,
        'modalidad_trabajo': job.modalidad_trabajo,
        'nombre_jefe': job.nombre_jefe,
    }

    

    if request.method == 'POST':
        form = candidateJobForm(request.POST, initial=initial, instance=True)
        if form.is_valid():
            # Actualizar la experiencia laboral con los datos del formulario
            job.entidad = form.cleaned_data['entidad']
            job.sector = form.cleaned_data['sector']
            job.fecha_inicial = form.cleaned_data['fecha_inicial']
            job.fecha_final = form.cleaned_data['fecha_final'] if form.cleaned_data['fecha_final'] else None
            job.activo = form.cleaned_data['activo']
            job.logro = form.cleaned_data['logro']
            job.cargo = form.cleaned_data['cargo']
            job.motivo_salida = form.cleaned_data['motivo_salida']
            job.salario = form.cleaned_data['salario'] if form.cleaned_data['salario'] else None
            job.modalidad_trabajo = form.cleaned_data['modalidad_trabajo']
            job.nombre_jefe = form.cleaned_data['nombre_jefe'] if form.cleaned_data['nombre_jefe'] else None
            job.save()

            messages.success(request, 'Información laboral actualizada exitosamente.')
            return redirect('candidatos:candidato_info_laboral')
        else:
            messages.error(request, 'Error al actualizar la información laboral.')
    else:
        form = candidateJobForm(initial=initial, instance=True)
    # Renderizar la plantilla con la información de la experiencia laboral
    context = {
        'form': form,
    }
    return render(request, 'admin/candidate/candidate_user/info_job_edit.html', context)

@login_required
@validar_permisos('acceso_candidato')
def candidate_info_skills(request):

    # Obtener el ID del candidato desde la sesión
    candidato_id = request.session.get('candidato_id')

    # Formulario por habilidad
    form = CandidateHabilityForm()

    # Obtener las habilidades del candidato (ajusta según tu modelo)
    skills = Can101CandidatoSkill.objects.filter(candidato_id_101=candidato_id).order_by('-id')

    # Prepare the initial data dictionary for the form
    initial_data = {
        'skill_relacionales': [],
        'skill_personales': [],
        'skill_cognitivas': [],
        'skill_digitales': [],
        'skill_liderazgo': [],
    }

    for cs in skills:
        # Check the group of the skill and add its ID to the correct list
        if cs.skill_id_104.grupo.id == 1:
            initial_data['skill_relacionales'].append(cs.skill_id_104.id)
        elif cs.skill_id_104.grupo.id == 2:
            initial_data['skill_personales'].append(cs.skill_id_104.id)
        elif cs.skill_id_104.grupo.id == 3:
            initial_data['skill_cognitivas'].append(cs.skill_id_104.id)
        elif cs.skill_id_104.grupo.id == 4:
            initial_data['skill_digitales'].append(cs.skill_id_104.id)
        elif cs.skill_id_104.grupo.id == 5:
            initial_data['skill_liderazgo'].append(cs.skill_id_104.id)
    
    if request.method == 'POST':
        form = CandidateHabilityFormList(request.POST, request.FILES)    
        if form.is_valid():

            #list_complete_Skills
            skill_all = []
            # Obtener los IDs de las habilidades relacionales
            ids_skill_relacionales = [skill.id for skill in form.cleaned_data['skill_relacionales']]
            skill_all.extend(ids_skill_relacionales)

            # Obtener los IDs de las habilidades personales
            ids_skill_personales = [skill.id for skill in form.cleaned_data['skill_personales']]
            skill_all.extend(ids_skill_personales)

            # Obtener los IDs de las habilidades cognitivas
            ids_skill_cognitivas = [skill.id for skill in form.cleaned_data['skill_cognitivas']]
            skill_all.extend(ids_skill_cognitivas)

            # Obtener los IDs de las habilidades digitales
            ids_skill_digitales = [skill.id for skill in form.cleaned_data['skill_digitales']]
            skill_all.extend(ids_skill_digitales)

            # Obtener los IDs de las habilidades de liderazgo
            ids_skill_liderazgo = [skill.id for skill in form.cleaned_data['skill_liderazgo']]
            skill_all.extend(ids_skill_liderazgo)
            
            for skill_id in skill_all:
                skill = Can104Skill.objects.get(id=skill_id)

                #Verificar si la habilidad ya existe para el candidato
                candidato = Can101Candidato.objects.get(id=candidato_id)
                # Eliminar habilidades que ya no están seleccionadas
                habilidades_actuales = set(Can101CandidatoSkill.objects.filter(candidato_id_101=candidato).values_list('skill_id_104', flat=True))
                habilidades_nuevas = set(skill_all)
                habilidades_a_eliminar = habilidades_actuales - habilidades_nuevas
                Can101CandidatoSkill.objects.filter(candidato_id_101=candidato, skill_id_104__in=habilidades_a_eliminar).delete()

                # Agregar nuevas habilidades si no existen
                if not Can101CandidatoSkill.objects.filter(candidato_id_101=candidato, skill_id_104=skill).exists():
                    Can101CandidatoSkill.objects.create(
                        candidato_id_101=candidato,
                        skill_id_104=skill,
                        nivel=1,  # Puedes ajustar el nivel según tu lógica o formulario
                        tipo_habilidad='S',  # Ajusta según tu lógica o formulario
                        certificado_habilidad=None  # Ajusta según tu lógica o formulario
                    )

                messages.success(request, 'Habilidades agregadas exitosamente.')

            return redirect('candidatos:candidato_info_habilidades')
        else:
            messages.error(request, 'Error al agregar la habilidad.')
    else:
        print("No es un POST")
        form = CandidateHabilityFormList(initial=initial_data)

    
    # Calcular porcentajes de completitud
    from applications.services.service_candidate import personal_information_calculation
    candidato = Can101Candidato.objects.get(id=candidato_id)
    porcentajes = personal_information_calculation(candidato.id)
    
    # Calcular porcentaje de redes sociales
    from applications.candidato.models import Can106CandidatoRed
    socialNetwork = Can106CandidatoRed.objects.filter(candidato_id_101=candidato.id, estado_id_001=1)
    if socialNetwork.exists():
        porcentaje_redes = 100
    else:
        porcentaje_redes = 0
    
    porcentajes['redes_sociales'] = {
        'porcentaje': porcentaje_redes,
        'campos': {
            'total': 1,
            'llenos': 1 if socialNetwork.exists() else 0,
        }
    }
    
    # Recalcular porcentaje total incluyendo las 5 secciones
    porcentajes['porcentaje_total'] = int((
        porcentajes['info_personal']['porcentaje'] + 
        porcentajes['educacion']['porcentaje'] + 
        porcentajes['experiencia']['porcentaje'] + 
        porcentajes['skills']['porcentaje'] + 
        porcentajes['redes_sociales']['porcentaje']
    ) / 5)
    
    context = {
        'form': form,
        'skills': skills,
        'porcentajes': porcentajes,
        'active_section': 'habilidades',
    }
    
    return render(request, 'admin/candidate/candidate_user/info_skills.html', context)

@login_required
@validar_permisos('acceso_candidato')
def candidate_info_skills_delete(request, pk):
    # Obtener el ID del candidato desde la sesión
    candidato_id = request.session.get('candidato_id')
    # Obtener la habilidad del candidato (ajusta según tu modelo)
    skill = Can101CandidatoSkill.objects.get(id=pk)
    # Eliminar la habilidad del candidato
    skill.delete()
    # Mostrar un mensaje de éxito
    messages.success(request, 'Habilidad eliminada exitosamente.')

    return redirect('candidatos:candidato_info_habilidades')

@login_required
@validar_permisos('acceso_candidato')
def candidate_info_perfil(request):
    candidato_id = request.session.get('candidato_id')
    # Obtener el candidato (ajusta según tu modelo)
    candidato = Can101Candidato.objects.get(id=candidato_id)
    # Obtener la experiencia laboral del candidato (ajusta según tu modelo)
    jobs = Can102Experiencia.objects.filter(candidato_id_101=candidato.id).order_by('-fecha_inicial')
    # Obtener la educación del candidato (ajusta según tu modelo)
    studies = Can103Educacion.objects.filter(candidato_id_101=candidato.id).order_by('-fecha_inicial')
    # Obtener las habilidades del candidato (ajusta según tu modelo)
    skills = Can101CandidatoSkill.objects.filter(candidato_id_101=candidato.id).order_by('-id')
    
    # Agrupar habilidades según la lógica del formulario
    skills_by_group = {
        'Relacionales': [],
        'Personales': [],
        'Cognitivas': [],
        'Digitales / Ágiles': [],
        'Liderazgo / Dirección': []
    }
    
    for skill in skills:
        if skill.tipo_habilidad == 'S' and skill.skill_id_104.grupo:
            grupo_id = skill.skill_id_104.grupo.id
            if grupo_id == 1:
                skills_by_group['Relacionales'].append(skill)
            elif grupo_id == 2:
                skills_by_group['Personales'].append(skill)
            elif grupo_id == 3:
                skills_by_group['Cognitivas'].append(skill)
            elif grupo_id == 4:
                skills_by_group['Liderazgo / Dirección'].append(skill)
            elif grupo_id == 5:
                skills_by_group['Digitales / Ágiles'].append(skill)

    socialNetwork = Can106CandidatoRed.objects.filter(candidato_id_101=candidato.id, estado_id_001=1).order_by('-id')
    
    context = {
        'candidato': candidato,
        'jobs': jobs,
        'studies': studies,
        'skills': skills,
        'skills_by_group': skills_by_group,
        'socialNetwork': socialNetwork,
    }

    return render(request, 'admin/candidate/candidate_user/info_perfil.html', context)

@login_required
@validar_permisos('acceso_candidato')
def candidate_info_social_network(request):
    candidato_id = request.session.get('candidato_id')
    
    # Obtener el candidato (ajusta según tu modelo)
    candidato = Can101Candidato.objects.get(id=candidato_id)

    redes = Can106CandidatoRed.objects.filter(estado_id_001=1, candidato_id_101=candidato_id).order_by('-id')
    print(redes)
    if request.method == 'POST':
        form = SocialNetworkForm(request.POST)
        if form.is_valid():
            red_social_id_105 = form.cleaned_data['red_social_id_105']
            url = form.cleaned_data['url']

            # Verificar si la red social ya está registrada para el candidato
            if not Can106CandidatoRed.objects.filter(candidato_id_101=candidato, red_social_id_105=red_social_id_105, estado_id_001=1).exists():
                Can106CandidatoRed.objects.create(
                    candidato_id_101=candidato,
                    red_social_id_105=red_social_id_105,
                    url=url,
                    estado_id_001=Cat001Estado.objects.get(id=1)  # Cambia esto según tu lógica
                )
                messages.success(request, 'Red social agregada exitosamente.')
                return redirect('candidatos:candidato_info_redes')
            else:
                messages.error(request, 'La red social ya está registrada.')

            
        else:
            messages.error(request, 'Error al agregar la red social.')
        
    else:
        form = SocialNetworkForm()
        

    # Calcular porcentajes de completitud
    from applications.services.service_candidate import personal_information_calculation
    porcentajes = personal_information_calculation(candidato.id)
    
    # Calcular porcentaje de redes sociales
    if redes.exists():
        porcentaje_redes = 100
    else:
        porcentaje_redes = 0
    
    porcentajes['redes_sociales'] = {
        'porcentaje': porcentaje_redes,
        'campos': {
            'total': 1,
            'llenos': 1 if redes.exists() else 0,
        }
    }
    
    # Recalcular porcentaje total incluyendo las 5 secciones
    porcentajes['porcentaje_total'] = int((
        porcentajes['info_personal']['porcentaje'] + 
        porcentajes['educacion']['porcentaje'] + 
        porcentajes['experiencia']['porcentaje'] + 
        porcentajes['skills']['porcentaje'] + 
        porcentajes['redes_sociales']['porcentaje']
    ) / 5)

    context = {
        'candidato': candidato,
        'form': form,
        'redes': redes,
        'porcentajes': porcentajes,
        'active_section': 'redes',
    }

    return render(request, 'admin/candidate/candidate_user/info_social_network.html', context)

@login_required
@validar_permisos('acceso_candidato')
def candidate_info_social_network_edit(request, pk):
    candidato_id = request.session.get('candidato_id')

    # Obtener el candidato (ajusta según tu modelo)
    candidato = Can101Candidato.objects.get(id=candidato_id)

    red = get_object_or_404(Can106CandidatoRed, pk=pk, candidato_id_101=candidato)

    # Inicializar el formulario con los datos de la red social
    initial = {
        'red_social_id_105': red.red_social_id_105,
        'url': red.url,
    }

    if request.method == 'POST':
        form = SocialNetworkForm(request.POST, initial=initial)
        if form.is_valid():
            red_social_id_105 = form.cleaned_data['red_social_id_105']
            url = form.cleaned_data['url']

            # Actualizar la red social
            red.red_social_id_105 = red_social_id_105
            red.url = url
            red.save()

            messages.success(request, 'Red social actualizada exitosamente.')
            return redirect('candidatos:candidato_info_redes')
        else:
            messages.error(request, 'Error al actualizar la red social.')
    else:
        form = SocialNetworkForm(initial=initial)



    context = {
        'candidato': candidato,
        'form': form,
        'red': red,
    }

    return render(request, 'admin/candidate/candidate_user/info_social_network_edit.html', context)

@login_required
@validar_permisos('acceso_candidato')
def canidate_info_social_network_delete(request, pk):
    candidato_id = request.session.get('candidato_id')

    # Obtener el candidato (ajusta según tu modelo)
    candidato = Can101Candidato.objects.get(id=candidato_id)

    # Obtener la red social del candidato
    red_social = get_object_or_404(Can106CandidatoRed, pk=pk, candidato_id_101=candidato)

    # Eliminar la red social
    red_social.estado_id_001 = Cat001Estado.objects.get(id=3)
    red_social.save()

    messages.success(request, 'Red social eliminada exitosamente.')
    
    return redirect('candidatos:candidato_info_redes')

