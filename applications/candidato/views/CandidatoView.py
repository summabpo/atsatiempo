from django.shortcuts import render, redirect, get_object_or_404
from applications.candidato.models import Can101Candidato, Can102Experiencia, Can103Educacion
from applications.candidato.forms.CandidatoForms import CandidatoForm
from applications.candidato.forms.ExperienciaForms import ExperienciaCandidatoForm
from applications.candidato.forms.EstudioForms import EstudioCandidatoForm
from django.views.generic import (TemplateView, ListView)

def candidato_mostrar(request, pk=None):
    # Valida si se pasa un parametro pk o ID del candidato
    if pk:
        candidato = get_object_or_404(Can101Candidato, pk=pk)
        experiencias = Can102Experiencia.objects.filter(candidato_id_101=candidato.id, estado_id_001=1).order_by('-id')
        estudios = Can103Educacion.objects.filter(candidato_id_101=candidato.id, estado_id_001=1).order_by('-id')

        accion = 'Editar'
    else:
        candidato = None
        experiencias = None
        estudios = None
        
        accion = 'Crear'

    # Valida el formulario candidato
    if request.method == 'POST':
        form = CandidatoForm(request.POST, instance=candidato)
        if form.is_valid():
            empleado = form.save()
            return redirect('candidatos:candidato_listar')
    else:
        form = CandidatoForm(instance=candidato)
        

    return render(request, 'candidato/form_candidato.html', {
        'form': form,
        'candidato': candidato,
        'experiencias': experiencias, 
        'accion': accion, 
        'estudios': estudios
        })