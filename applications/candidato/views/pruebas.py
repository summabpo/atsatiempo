from django.shortcuts import render, redirect, get_object_or_404
from applications.candidato.forms.pruebasforms import PruebasForm


def pruebas(request):
    form = PruebasForm()
    
    return render(request, 'candidato/prueba.html'
                  ,{
                      'form':form
                  })