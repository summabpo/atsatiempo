from django.shortcuts import render, redirect, get_object_or_404
from atsatiempo.asgi import application
from ..forms import Psi202RespuestaForm
from applications.candidato.models import Can101Candidato
from applications.pruebas_psi.models import Psi202Respuesta


def asignar_respuesta(request, candidato_id):
    candidato = get_object_or_404(Can101Candidato, pk=candidato_id)

    if request.method == 'POST':
        form = Psi202RespuestaForm(request.POST)
        if form.is_valid():
            respuesta = form.save(commit=False)
            respuesta.candidato = candidato
            respuesta.save()
            return redirect('asignar_respuesta')
    else:
        form = Psi202RespuestaForm()

    return render(request, 'pruebas_psi/asignar_respuesta.html', {'form': form, 'candidato': candidato})