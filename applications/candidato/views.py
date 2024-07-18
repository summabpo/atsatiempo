from django.shortcuts import render, redirect
from .models import Can101Candidato
from .forms.CandidatoForms import CandidatoForm
from django.views.generic import (TemplateView,)
# Create your views here.
class InicioView(TemplateView):
    """ vista que carga la pagina de inicio """
    template_name = 'candidato/index.html'

def candidato_crear(request):
    """ vista que carga la pagina de inicio """
    if request.method == 'POST':
        form = CandidatoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('candidato_crear')
    else:
        form = CandidatoForm()

    return render(request, 'candidato/index.html', {'form': form})
