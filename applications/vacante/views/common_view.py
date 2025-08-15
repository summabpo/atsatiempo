from django.shortcuts import render, redirect, get_object_or_404
from datetime import date

#models
from applications.vacante.models import Cli052Vacante, Cli055ProfesionEstudio
from applications.candidato.models import Can101Candidato

def match(request, candidato_id, vacante_id):
    candidato = get_object_or_404(Can101Candidato, pk=candidato_id)
    vacante = get_object_or_404(Cli052Vacante, pk=vacante_id)

    #bloque edad

    json_match = {}

    #edad candidato
    if candidato.fecha_nacimiento:
        today = date.today()
        edad_candidato = today.year - candidato.fecha_nacimiento.year - (
            (today.month, today.day) < (candidato.fecha_nacimiento.month, candidato.fecha_nacimiento.day)
        )
    else:
        edad_candidato = None

    if edad_candidato >= vacante.perfil_vacante.edad_inicial and edad_candidato <= vacante.perfil_vacante.edad_final:
        edad_candidato_valido = True
    else:
        edad_candidato_valido = False


    json_match["match_edad"] = {
        "edad": edad_candidato,
        "rango_edad": {
            "minima": vacante.perfil_vacante.edad_inicial,
            "maxima": vacante.perfil_vacante.edad_final
        },
        "resultado": edad_candidato_valido
    }
    
    

    context = {
        'candidato': candidato,
        'vacante': vacante,
    }

    return render(request, 'admin/vacancy/match.html', context)
