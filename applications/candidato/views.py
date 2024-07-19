from django.shortcuts import render, redirect, get_object_or_404
from .models import Can101Candidato
from .forms.CandidatoForms import CandidatoForm
from django.views.generic import (TemplateView, ListView)

# Create your views here.
class InicioView(TemplateView):
    """ vista que carga la pagina de inicio """
    template_name = 'candidato/index.html'

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
            print(empleado)
            return redirect('candidatos:candidato_listar')
    else:
        form = CandidatoForm(instance=candidato)

    return render(request, 'candidato/form_candidato.html', {
        'form': form,
        'accion': accion,
        'candidato': candidato
        }
    )

class ListadoCandidato(ListView):
    template_name = 'candidato/listado_candidatos.html'
    model = Can101Candidato
    context_object_name = 'candidatos'