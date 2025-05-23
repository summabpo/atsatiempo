from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from applications.candidato.forms.EstudioForms import EstudioCandidatoForm, candidateStudyForm
from applications.candidato.forms.ExperienciaForms import candidateJobForm
from applications.candidato.forms.HabilidadForms import CandidateHabilityForm
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.usuarios.decorators  import validar_permisos

#models
from applications.candidato.models import Can101Candidato, Can102Experiencia, Can103Educacion, Can104Skill, Can101CandidatoSkill


#forms
from applications.candidato.forms.CandidatoForms import CandidateForm

#views
@login_required
@validar_permisos('acceso_candidato')
def candidate_info(request):

    candidato_id = request.session.get('candidato_id')
    

    candidato = get_object_or_404(Can101Candidato, pk=candidato_id)

    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES, instance=candidato)

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
            if form.cleaned_data['imagen_perfil']:
                candidato.imagen_perfil = form.cleaned_data['imagen_perfil']
            if form.cleaned_data['hoja_de_vida']:
                candidato.hoja_de_vida = form.cleaned_data['hoja_de_vida']
            candidato.email = form.cleaned_data['email']
            candidato.save()

            messages.success(request, 'Información básica actualizada exitosamente.')

            return redirect('candidatos:candidato_info_personal')
        else:
            messages.error(request, 'Error al actualizar la información básica.')
    else:
        initial_data = {
            'email': candidato.email,
            'primer_nombre': candidato.primer_nombre,
            'segundo_nombre': candidato.segundo_nombre,
            'primer_apellido': candidato.primer_apellido,
            'segundo_apellido': candidato.segundo_apellido,
            'ciudad_id_004': candidato.ciudad_id_004,
            'sexo': candidato.sexo,
            'fecha_nacimiento': candidato.fecha_nacimiento.strftime('%Y-%m-%d') if candidato.fecha_nacimiento else '',
            'telefono': candidato.telefono,
            'skills': candidato.skills.all(),
            'imagen_perfil': candidato.imagen_perfil,
            'hoja_de_vida': candidato.hoja_de_vida,
            'numero_documento': candidato.numero_documento,
            'direccion': candidato.direccion,
        }
        print(f"Initial data para fecha_nacimiento: {initial_data.get('fecha_nacimiento')}")
        form = CandidateForm(initial=initial_data, instance=candidato)

    context = {
        'form': form,
    }

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
            carrera = form.cleaned_data['carrera']
            fortaleza_adquiridas = form.cleaned_data['fortaleza_adquiridas']
            candidato_id_101 = Can101Candidato.objects.get(id=candidato_id)
            ciudad_obj_004 = form.cleaned_data['ciudad_id_004']
            tipo_estudio = form.cleaned_data['tipo_estudio']
            if form.cleaned_data['certificacion']:
                certificacion = form.cleaned_data['certificacion']
            
            Can103Educacion.objects.create(
                estado_id_001=Cat001Estado.objects.get(id=1),  # Cambia esto según tu lógica
                institucion=institucion,
                grado_en=grado_en,
                fecha_inicial=fecha_inicial,
                fecha_final=fecha_final,
                titulo=titulo,
                carrera=carrera,
                fortaleza_adquiridas=fortaleza_adquiridas,
                candidato_id_101=candidato_id_101,
                ciudad_id_004=ciudad_obj_004,
                tipo_estudio=tipo_estudio,
                certificacion=certificacion if form.cleaned_data['certificacion'] else None
            )
            
            messages.success(request, 'Información académica actualizada exitosamente.')
            return redirect('candidatos:candidato_info_academica')
        else:
            form_errors = True
            messages.error(request, 'Error al actualizar la información académica.')
    else:
        form = candidateStudyForm(request.POST or None)

    context = {
        'studies': studies,
        'form': form,
        'form_errors': form_errors,
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
        'carrera': study.carrera,
        'fortaleza_adquiridas': study.fortaleza_adquiridas,
        'ciudad_id_004': study.ciudad_id_004.id if study.ciudad_id_004 else None,
        'tipo_estudio': study.tipo_estudio,
        'certificacion': study.certificacion,
    }

    if request.method == 'POST':
        form = candidateStudyForm(request.POST, request.FILES, initial=initial)
        if form.is_valid():

            study.institucion = form.cleaned_data['institucion']
            study.grado_en = form.cleaned_data['grado_en']
            study.fecha_inicial = form.cleaned_data['fecha_inicial']
            study.fecha_final = form.cleaned_data['fecha_final'] if form.cleaned_data['fecha_final'] else None
            study.titulo = form.cleaned_data['titulo'] if form.cleaned_data['titulo'] else None
            study.carrera = form.cleaned_data['carrera']
            study.fortaleza_adquiridas = form.cleaned_data['fortaleza_adquiridas']
            study.candidato_id_101 = Can101Candidato.objects.get(id=request.session.get('candidato_id'))
            study.ciudad_id_004 = form.cleaned_data['ciudad_id_004']
            study.tipo_estudio = form.cleaned_data['tipo_estudio']
            if form.cleaned_data['certificacion']:
                study.certificacion = form.cleaned_data['certificacion']
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

    context = {
        'jobs': jobs,
        'form': form,
        'form_errors': form_errors,
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

    form = CandidateHabilityForm()

    # Obtener las habilidades del candidato (ajusta según tu modelo)
    skills = Can101CandidatoSkill.objects.filter(candidato_id_101=candidato_id).order_by('-id')

    if request.method == 'POST':
        form = CandidateHabilityForm(request.POST)
        if form.is_valid():
            habilidad = form.cleaned_data['skill_id_104'].upper()
            nivel = form.cleaned_data['nivel']

            # Guardar la habilidad en la base de datos
            skill, created = Can104Skill.objects.get_or_create(
                nombre=habilidad,
                estado_id_004=Cat001Estado.objects.get(id=1)
                )  # Cambia esto según tu lógica
            
            candidato = Can101Candidato.objects.get(id=candidato_id)

            # Verificar si la habilidad ya existe para el candidato
            if not Can101CandidatoSkill.objects.filter(candidato_id_101=candidato, skill_id_104=skill).exists():
                Can101CandidatoSkill.objects.create(
                    candidato_id_101=candidato,
                    skill_id_104=skill,
                    nivel=nivel
                )
                messages.success(request, 'Habilidad agregada exitosamente.')
            else:
                messages.error(request, 'La habilidad ya está registrada.')

            return redirect('candidatos:candidato_info_habilidades')
        else:
            messages.error(request, 'Error al agregar la habilidad.')
    else:
        form = CandidateHabilityForm()   
    context = {
        'form': form,
        'skills': skills,
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
def candidate_info_perfil(request, pk):
    candidato_id = request.session.get(pk)
    # Obtener el candidato (ajusta según tu modelo)
    candidato = Can101Candidato.objects.get(id=pk)
    # Obtener la experiencia laboral del candidato (ajusta según tu modelo)
    jobs = Can102Experiencia.objects.filter(candidato_id_101=candidato.id).order_by('-fecha_inicial')
    # Obtener la educación del candidato (ajusta según tu modelo)
    studies = Can103Educacion.objects.filter(candidato_id_101=candidato.id).order_by('-fecha_inicial')
    # Obtener las habilidades del candidato (ajusta según tu modelo)
    skills = Can101CandidatoSkill.objects.filter(candidato_id_101=candidato.id).order_by('-id')
    
    context = {
        'candidato': candidato,
        'jobs': jobs,
        'studies': studies,
        'skills': skills,
    }

    return render(request, 'admin/candidate/candidate_user/info_perfil.html', context)