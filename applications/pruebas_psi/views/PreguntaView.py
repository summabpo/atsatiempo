from django.shortcuts import render, redirect
from ..forms import Psi201PreguntaForm
from applications.pruebas_psi.models import Psi201Pregunta


# Vista basada en función para crear preguntas
def crear_pregunta(request):
    if request.method == 'POST':
        form = Psi201PreguntaForm(request.POST)
        if form.is_valid():
            form.save()  # Guarda la nueva pregunta en la base de datos
            return redirect('pruebas_psi:listar_preguntas')  # Redirigir a lista de preguntas
    else:
        form = Psi201PreguntaForm()

    return render(request, 'pruebas_psi/crear_pregunta.html', {'form': form})

# Vista basada en función para listar preguntas
def listar_preguntas(request):
    preguntas = Psi201Pregunta.objects.all()
    return render(request, 'pruebas_psi/listar_preguntas.html', {'preguntas': preguntas})