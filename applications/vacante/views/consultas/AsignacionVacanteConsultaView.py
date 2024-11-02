import random
import string
from django.shortcuts import render, redirect
import json
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from applications.usuarios.decorators  import validar_permisos
from django.db.models import F, Q, Case, When, Value, CharField
from django.db.models.functions import Concat

#model
from applications.vacante.models import Cli052Vacante, Cli055ProfesionEstudio, Cli053SoftSkill, Cli052VacanteSoftSkillsId053, Cli054HardSkill, Cli052VacanteHardSkillsId054, Cli056AplicacionVacante, Cli057AsignacionEntrevista
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.usuarios.models import Permiso
from applications.cliente.models import Cli051Cliente
from applications.usuarios.models import UsuarioBase, Grupo

#form
from applications.vacante.forms.VacanteForms import VacanteForm
from applications.cliente.forms.ClienteForms import ClienteForm
from applications.cliente.forms.CreacionUsuariosForm import CrearUsuarioInternoForm

def consulta_asignacion_vacante():
    #consultar vacante
    asingacion_vacante = Cli056AplicacionVacante.objects.select_related(
        'candidato_101',
        'vacante_id_052',
        'vacante_id_052__cliente_id_051',
        'vacante_id_052__ciudad',
        'vacante_id_052__profesion_estudio_id_055',
    ).values(
        'id',
        'fecha_aplicacion',
        'fecha_actualizacion',
        vacante_id = F('vacante_id_052__id'),
        vacante_titulo = F('vacante_id_052__titulo'),
        vacante_numero_posiciones = F('vacante_id_052__numero_posiciones'),
        vacante_profesion_estudio = F('vacante_id_052__profesion_estudio_id_055__nombre'),
        vacante_ciudad = F('vacante_id_052__ciudad__nombre'),
        vacante_salario = F('vacante_id_052__salario'),
        vacante_fecha_creacion = F('vacante_id_052__fecha_creacion'),
        cliente_id = F('vacante_id_052__cliente_id_051__id'),
        cliente_nit = F('vacante_id_052__cliente_id_051__nit'),
        cliente_razon_social = F('vacante_id_052__cliente_id_051__razon_social'),
        candidato_id = F('candidato_101__id'),        
    ).annotate(
        vacante_estado = Case(
            When(vacante_id_052__estado_vacante=1, then=Value('Activa')),
            When(vacante_id_052__estado_vacante=2, then=Value('En Proceso')),
            When(vacante_id_052__estado_vacante=3, then=Value('Finalizada')),
            When(vacante_id_052__estado_vacante=4, then=Value('Cancelada')),
            output_field=CharField()  # Definir el tipo de campo de salida
        ),
        aplicacion_vacante_estado = Case(
            When(estado_aplicacion=1,  then=Value('Aplicado')),
            When(estado_aplicacion=2,  then=Value('Entrevista Programada')),
            When(estado_aplicacion=3,  then=Value('Entrevista Aprobada')),
            When(estado_aplicacion=4,  then=Value('Entrevista No Aprobada')),
            When(estado_aplicacion=5,  then=Value('Prueba Programada')),
            When(estado_aplicacion=6,  then=Value('Prueba Superada')),
            When(estado_aplicacion=7,  then=Value('Prueba No Superada')),
            When(estado_aplicacion=8,  then=Value('Seleccionado')),
            When(estado_aplicacion=9,  then=Value('Finalizada')),
            When(estado_aplicacion=10, then=Value('Cancelada')),
            When(estado_aplicacion=11, then=Value('Desiste')),
            default=Value('Estado desconocido'),
            output_field=CharField()
        ),
        vacante_experiencia_requerida = Case(
            When(vacante_id_052__experiencia_requerida=1, then=Value('0 a 6 Meses')),
            When(vacante_id_052__experiencia_requerida=2, then=Value('1 año a 2 años')),
            When(vacante_id_052__experiencia_requerida=3, then=Value('Más de 2 años')),
            When(vacante_id_052__experiencia_requerida=4, then=Value('Sin Experiencia')),
            output_field=CharField()  # Definir el tipo de campo de salida
        ),
        candidato_nombre = Concat(
            F('candidato_101__primer_nombre'),
            Value(' '),
            F('candidato_101__segundo_nombre'),
            Value(' '),
            F('candidato_101__primer_apellido'),
            Value(' '),
            F('candidato_101__segundo_apellido'),
        )
    ).order_by(
        '-id'
    )

    #consultar aplicaciones
    return asingacion_vacante

def consulta_asignacion_vacante_cliente(cliente_id, vacante_id):
    #consultar vacante
    asingacion_vacante = Cli056AplicacionVacante.objects.select_related(
        'candidato_101',
        'vacante_id_052',
        'vacante_id_052__cliente_id_051',
        'vacante_id_052__ciudad',
        'vacante_id_052__profesion_estudio_id_055',
    ).values(
        'id',
        'fecha_aplicacion',
        'fecha_actualizacion',
        'estado_aplicacion',
        vacante_id = F('vacante_id_052__id'),
        vacante_titulo = F('vacante_id_052__titulo'),
        vacante_numero_posiciones = F('vacante_id_052__numero_posiciones'),
        vacante_profesion_estudio = F('vacante_id_052__profesion_estudio_id_055__nombre'),
        vacante_ciudad = F('vacante_id_052__ciudad__nombre'),
        vacante_salario = F('vacante_id_052__salario'),
        vacante_fecha_creacion = F('vacante_id_052__fecha_creacion'),
        cliente_id = F('vacante_id_052__cliente_id_051__id'),
        cliente_nit = F('vacante_id_052__cliente_id_051__nit'),
        cliente_razon_social = F('vacante_id_052__cliente_id_051__razon_social'),
        candidato_id = F('candidato_101__id'),       
    ).annotate(
        vacante_estado = Case(
            When(vacante_id_052__estado_vacante=1, then=Value('Activa')),
            When(vacante_id_052__estado_vacante=2, then=Value('En Proceso')),
            When(vacante_id_052__estado_vacante=3, then=Value('Finalizada')),
            When(vacante_id_052__estado_vacante=4, then=Value('Cancelada')),
            output_field=CharField()  # Definir el tipo de campo de salida
        ),
        aplicacion_vacante_estado = Case(
            When(estado_aplicacion=1,  then=Value('Aplicado')),
            When(estado_aplicacion=2,  then=Value('Entrevista Programada')),
            When(estado_aplicacion=3,  then=Value('Entrevista Aprobada')),
            When(estado_aplicacion=4,  then=Value('Entrevista No Aprobada')),
            When(estado_aplicacion=5,  then=Value('Prueba Programada')),
            When(estado_aplicacion=6,  then=Value('Prueba Superada')),
            When(estado_aplicacion=7,  then=Value('Prueba No Superada')),
            When(estado_aplicacion=8,  then=Value('Seleccionado')),
            When(estado_aplicacion=9,  then=Value('Finalizada')),
            When(estado_aplicacion=10, then=Value('Cancelada')),
            When(estado_aplicacion=11, then=Value('Desiste')),
            When(estado_aplicacion=12, then=Value('No Apto')),
            default=Value('Estado desconocido'),
            output_field=CharField()
        ),
        vacante_experiencia_requerida = Case(
            When(vacante_id_052__experiencia_requerida=1, then=Value('0 a 6 Meses')),
            When(vacante_id_052__experiencia_requerida=2, then=Value('1 año a 2 años')),
            When(vacante_id_052__experiencia_requerida=3, then=Value('Más de 2 años')),
            When(vacante_id_052__experiencia_requerida=4, then=Value('Sin Experiencia')),
            output_field=CharField()  # Definir el tipo de campo de salida
        ),
        candidato_nombre = Concat(
            F('candidato_101__primer_nombre'),
            Value(' '),
            F('candidato_101__segundo_nombre'),
            Value(' '),
            F('candidato_101__primer_apellido'),
            Value(' '),
            F('candidato_101__segundo_apellido'),
        )
    ).order_by(
        '-id'
    ).filter(vacante_id_052__cliente_id_051=cliente_id, vacante_id_052=vacante_id)

    #consultar aplicaciones
    return asingacion_vacante