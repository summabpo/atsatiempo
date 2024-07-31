from django.shortcuts import render, redirect, get_object_or_404
from applications.candidato.models import Can101Candidato, Can102Experiencia, Can103Educacion, Can101CandidatoSkill
from applications.candidato.forms.CandidatoForms import CandidatoForm
from applications.candidato.forms.ExperienciaForms import ExperienciaCandidatoForm
from applications.candidato.forms.HabilidadForms import HabilidadCandidatoForm
from applications.candidato.forms.EstudioForms import EstudioCandidatoForm
from django.views.generic import (TemplateView, ListView)
from django.contrib import messages

def candidato_mostrar(request, pk=None):
    # Valida si se pasa un parametro pk o ID del candidato
    if pk:
        candidato = get_object_or_404(Can101Candidato, pk=pk)
        experiencias = Can102Experiencia.objects.filter(candidato_id_101=candidato.id, estado_id_001=1).order_by('-id')
        estudios = Can103Educacion.objects.filter(candidato_id_101=candidato.id, estado_id_001=1).order_by('-id')
        habilidades = Can101CandidatoSkill.objects.filter(candidato_id_101=candidato.id).order_by('-id')

        accion = 'Editar'

    else:
        candidato = None
        experiencias = None
        estudios = None
        
        accion = 'Crear'

    if request.method == 'POST':

        if 'submit_candidato' in request.POST:
            print('pasa')
            form = CandidatoForm(request.POST, instance=candidato)
            
            if form.is_valid():
                form.save()
                messages.success(request, 'Experiencia Creada')
                return redirect('candidatos:candidato_editar', pk=candidato.id)
            else:
                errores = ''
                for field, errors in form.errors.items():
                    errores += f'{field}: {", ".join(errors)}'
                messages.error(request, f'El formulario tiene los siguientes errores: {errores}')
        else:
            form = CandidatoForm(instance=candidato) 

        if 'submit_experiencia' in request.POST:
            form_experiencia = ExperienciaCandidatoForm(request.POST)
            if form_experiencia.is_valid():
                form_experiencia.save(candidato_id=candidato.id)
                messages.success(request, 'Experiencia Creada')
                return redirect('candidatos:candidato_editar', pk=candidato.id)
            else:
                errores = ''
                for field, errors in form_experiencia.errors.items():
                    errores += f'{field}: {", ".join(errors)}'
                messages.error(request, f'El formulario tiene los siguientes errores lab: {errores}')
        else:
            form_experiencia = ExperienciaCandidatoForm(candidato_id=candidato.id)

        if 'submit_estudio' in request.POST:
            form_estudio = EstudioCandidatoForm(request.POST)
            if form_estudio.is_valid():
                form_estudio.save(candidato_id=candidato.id)
                messages.success(request, 'Experiencia Creada')
                return redirect('candidatos:candidato_editar', pk=candidato.id)
            else:
                errores = ''
                for field, errors in form_estudio.errors.items():
                    errores += f'{field}: {", ".join(errors)}'
                messages.error(request, f'El formulario tiene los siguientes errores aca : {errores}')
        else:
            form_estudio = EstudioCandidatoForm(candidato_id=candidato.id)

        if 'submit_habilidad' in request.POST:
            form_habilidad = HabilidadCandidatoForm(request.POST)
            if form_habilidad.is_valid():
                form_habilidad.save(candidato_id=candidato.id)
                messages.success(request, 'Habilidad Creada')
                return redirect('candidatos:candidato_editar', pk=candidato.id)
            else:
                errores = ''
                for field, errors in form_habilidad.errors.items():
                    errores += f'{field}: {", ".join(errors)}'
                messages.error(request, f'El formulario tiene los siguientes errores aca : {errores}')
        else:
            form_estudio = HabilidadCandidatoForm(candidato_id=candidato.id)
            
    else:
        form = CandidatoForm(instance=candidato)
        form_experiencia = ExperienciaCandidatoForm(candidato_id=candidato.id)
        form_estudio = EstudioCandidatoForm(candidato_id=candidato.id)
        form_habilidad = HabilidadCandidatoForm(candidato_id=candidato.id)

    return render(request, 'candidato/form_candidato.html', {
        'form': form,
        'form_experiencia' : form_experiencia,
        'form_estudio' : form_estudio,
        'form_habilidad' : form_habilidad,
        'candidato': candidato,
        'experiencias': experiencias, 
        'habilidades':habilidades,
        'accion': accion, 
        'estudios': estudios
        })