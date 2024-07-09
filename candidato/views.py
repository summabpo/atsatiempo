from django.shortcuts import render
from .models import Can101Candidato
from django.views.generic import (TemplateView,)
# Create your views here.
class InicioView(TemplateView):
    """ vista que carga la pagina de inicio """
    template_name = 'candidato/index.html'