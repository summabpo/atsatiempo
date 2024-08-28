from django.shortcuts import render, redirect, get_object_or_404
from applications.candidato.models import Can101Candidato, Can103Educacion
from applications.candidato.forms.CandidatoForms import CandidatoForm
from applications.candidato.forms.ExperienciaForms import ExperienciaCandidatoForm
from applications.candidato.forms.EstudioForms import EstudioCandidatoForm
from django.views.generic import (TemplateView, ListView)
from django.contrib import messages

def estudio_mostrar(request, pk=None):
    candidato = get_object_or_404(Can101Candidato, pk=pk)
    estudios = Can103Educacion.objects.filter(candidato_id_101=candidato.id, estado_id_001=1).order_by('-id')

    # Formulario Estudios
    if request.method == 'POST': 
        form = EstudioCandidatoForm(request.POST)
        if form.is_valid():
            form.save(candidato_id=candidato.id)
            messages.success(request, 'El registro de experiencia academica ha sido creado')
            return redirect('candidatos:candidato_academica', pk=candidato.id)
        else:
            messages.error(request, form.errors)
    else:
        form = EstudioCandidatoForm(candidato_id=candidato.id)

    #Listado de objetos a enviar al template
    context = {
        'form': form,
        'candidato': candidato,
        'estudios': estudios,
    }

    return render(request, 'candidato/form_estudio.html', context)