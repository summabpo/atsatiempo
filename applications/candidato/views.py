from django.shortcuts import render, redirect, get_object_or_404
from .models import Can101Candidato, Can102Experiencia
from .forms.CandidatoForms import CandidatoForm
from .forms.ExperienciaForms import ExperienciaCandidatoForm
from django.views.generic import (TemplateView, ListView)

# Create your views here.
class InicioView(TemplateView):
    """ vista que carga la pagina de inicio """
    template_name = 'candidato/index.html'

class ListadoCandidato(ListView):
    template_name = 'candidato/listado_candidatos.html'
    model = Can101Candidato
    context_object_name = 'candidatos'

def candidato_crear(request, pk=None):
    if pk:
        candidato = get_object_or_404(Can101Candidato, pk=pk)
        accion = 'Editar'
    else:
        candidato = None
        accion = 'Crear'

    if request.method == 'POST':
        form = CandidatoForm(request.POST, instance=candidato)
        if form.is_valid():
            empleado = form.save()
            return redirect('candidatos:candidato_listar')
    else:
        form = CandidatoForm(instance=candidato)

    return render(request, 'candidato/form_candidato.html', {
        'form': form,
        'accion': accion,
        'candidato': candidato
        }
    )

def experiencia_listar(request, candidato_id):
    
    candidato = get_object_or_404(Can101Candidato, pk=candidato_id)
    experiencias = Can102Experiencia.objects.filter(candidato_id_101=candidato)
    
    context = {
        'candidato': candidato,
        'experiencias': experiencias,
    }
    
    return render(request, 'candidato/listado_experiencia_laboral.html', context)

def experiencia_crear(request, candidato_id):
    candidato = get_object_or_404(Can101Candidato, id=candidato_id)

    if request.method == 'POST': 
        print('ingrese')
        form = ExperienciaCandidatoForm(request.POST)
        if form.is_valid():
            experiencia = form.save(candidato_id=candidato.id)
            # experiencia.save()
            return redirect('candidatos:experiencia_listar', candidato_id=candidato.id)

    else:
        form = ExperienciaCandidatoForm(candidato_id=candidato.id)
    
    return render(request, 'candidato/experiencia_crear.html', {'form': form, 'candidato': candidato})
