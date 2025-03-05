from django.shortcuts import render
from applications.pruebas_psi.models import Psi202Respuesta, Psi201Pregunta

def resultado_prueba(request, candidato_id):
    # Obtener las respuestas del candidato
    respuestas = Psi202Respuesta.objects.filter(candidato_id=candidato_id).select_related('id_pregunta')

    if not respuestas.exists():
        return render(request, 'pruebas_psi/sin_respuesta.html', {'candidato_id': candidato_id})

    # Calcular resultados por factor (ejemplo: promedio por factor)
    resultados = {}
    for respuesta in respuestas:
        factor = respuesta.id_pregunta.factor
        if factor not in resultados:
            resultados[factor] = []
        resultados[factor].append(respuesta.respuesta)

        # Calcular el promedio de cada factor
    promedios = {factor: sum(resps) / len(resps) for factor, resps in resultados.items()}

    context = {
        'candidato_id': candidato_id,
        'resultados': resultados,
        'promedios': promedios,
    }
    return render(request, 'pruebas_psi/resultado_prueba.html', context)