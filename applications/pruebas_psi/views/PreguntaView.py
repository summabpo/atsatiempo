from django.shortcuts import render, redirect
from ..forms import Psi201PreguntaForm

# Vista basada en función para crear preguntas
def crear_pregunta(request):
    if request.method == 'POST':
        form = Psi201PreguntaForm(request.POST)
        if form.is_valid():
            form.save()  # Guarda la nueva pregunta en la base de datos
            return redirect('crear_pregunta')  # Redirigir a alguna vista donde se muestren las preguntas
    else:
        form = Psi201PreguntaForm()
    
    return render(request, 'pruebas_psi/crear_pregunta.html', {'form': form})