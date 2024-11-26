from django.shortcuts import render, redirect, get_object_or_404

#models
from applications.vacante.models import Cli052Vacante
from applications.candidato.models import Can102Experiencia

#utils
from django.utils.timezone import now

def calcular_match(candidato, vacante):
    # Pesos para cada criterio
    peso_hard_skills = 40
    peso_soft_skills = 20
    peso_experiencia = 20
    peso_educacion = 20

    # Calcular coincidencia de Hard Skills
    hard_skills_candidato = set(candidato.skills.all())  # Habilidades del candidato
    hard_skills_vacante = set(vacante.hard_skills_id_054.all())  # Hard Skills de la vacante
    match_hard_skills = len(hard_skills_candidato & hard_skills_vacante) / len(hard_skills_vacante) if hard_skills_vacante else 0

    # Calcular coincidencia de Soft Skills
    soft_skills_vacante = set(vacante.soft_skills_id_053.all())  # Soft Skills de la vacante
    soft_skills_candidato = set(vacante.hard_skills_id_054.all())  # Hard Skills de la vacante
    match_soft_skills = len(soft_skills_candidato & soft_skills_vacante) / len(soft_skills_vacante) if soft_skills_vacante else 0

    # Calcular experiencia laboral
    experiencia_candidato = sum([
        (exp.fecha_final.year - exp.fecha_inicial.year) if exp.fecha_final else 0
        for exp in candidato.can102experiencia_set.all()  # Relación inversa predeterminada
    ])
    experiencia_vacante_minima = vacante.experiencia_requerida
    match_experiencia = 1 if experiencia_candidato >= experiencia_vacante_minima else 0

    # Calcular nivel de estudios
    nivel_educacion_candidato = (
        candidato.can103educacion_set.last().titulo  # Usar la relación inversa predeterminada
        if candidato.can103educacion_set.exists() else None
    )
    nivel_educacion_vacante = vacante.profesion_estudio_id_055.nombre
    match_educacion = 1 if nivel_educacion_candidato == nivel_educacion_vacante else 0

    # Calcular el porcentaje total
    porcentaje_match = (
        (match_hard_skills * peso_hard_skills) +
        (match_soft_skills * peso_soft_skills) +
        (match_experiencia * peso_experiencia) +
        (match_educacion * peso_educacion)
    )
    print(porcentaje_match)
    return porcentaje_match