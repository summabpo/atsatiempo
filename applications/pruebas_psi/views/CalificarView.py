from django.shortcuts import render, redirect, get_object_or_404
from ..forms import CalificarPreguntaForm
from applications.pruebas_psi.models import Psi201Pregunta, Psi202Respuesta
from applications.candidato.models import Can101Candidato

def calificar_prueba(request, candidato_id):
    candidato = get_object_or_404(Can101Candidato, pk=candidato_id)
    pregunta_id = request.session.get('pregunta_id', 1)  # Usar sesión para controlar el progreso

    try:
        pregunta = Psi201Pregunta.objects.get(id_pregunta=pregunta_id)
    except Psi201Pregunta.DoesNotExist:
        # Todas las preguntas han sido respondidas
        return redirect('resultados', candidato_id=candidato_id)

    if request.method == 'POST':
        form = CalificarPreguntaForm(request.POST, pregunta_obj=pregunta)
        if form.is_valid():
            calificacion = form.cleaned_data['calificacion']
            # Guardar la respuesta
            Psi202Respuesta.objects.create(
                candidato=candidato,
                id_pregunta=pregunta,
                respuesta=calificacion
            )
            # Avanzar a la siguiente pregunta
            request.session['pregunta_id'] = pregunta_id + 1
            return redirect('calificar_prueba', candidato_id=candidato.id)
    else:
        form = CalificarPreguntaForm(pregunta_obj=pregunta)

    return render(request, 'pruebas_psi/calificar_prueba.html', {'form': form, 'candidato': candidato, 'pregunta': pregunta})