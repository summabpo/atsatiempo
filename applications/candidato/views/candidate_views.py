from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from applications.candidato.forms.EstudioForms import EstudioCandidatoForm, candidateStudyForm
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
    candidato_id = request.session.get('candidato_id')

    studies = Can103Educacion.objects.filter(candidato_id_101=candidato_id).order_by('-fecha_inicial')
    form = candidateStudyForm()

    if request.method == 'POST':
        if form.is_valid():
            

            
            messages.success(request, 'Información académica actualizada exitosamente.')
            return redirect('candidatos:candidato_info_academica')
        else:
            messages.error(request, 'Error al actualizar la información académica.')
    else:
        form = candidateStudyForm(request.POST or None)

    context = {
        'studies': studies,
        'form': form,
    }
    return render(request, 'admin/candidate/candidate_user/info_academy.html', context)

@login_required
@validar_permisos('acceso_candidato')
def candidate_info_job(request):
    candidato_id = request.session.get('candidato_id')

    jobs = Can102Experiencia.objects.filter(candidato_id_101=candidato_id).order_by('-fecha_inicio')
    
    form = 25

    context = {
        'jobs': jobs,
        'form': form,
    }
    return render(request, 'admin/candidate/candidate_user/info_job.html', context)