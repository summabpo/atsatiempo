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

def consulta_asignacion_entrevista_todos():
    entrevista = 1
    return entrevista

def consulta_asignacion_entrevista_cliente(cliente_id):
    asignacion_entrevista = Cli057AsignacionEntrevista.objects.select_related(
        'asignacion_vacante',
        'asignacion_vacante__candidato_101',
        'asignacion_vacante__vacante_id_052',
        'asignacion_vacante__vacante_id_052__cliente_id_051',
    ).values(
        'id',
        'fecha_asignacion',
        'fecha_entrevista',
        'hora_entrevista',
        'lugar_enlace',
        fecha_asignacion_vacante = F('asignacion_vacante__fecha_aplicacion'),
        vacante_titulo = F('asignacion_vacante__vacante_id_052__titulo'),
        vacante_fecha_creacion = F('asignacion_vacante__vacante_id_052__fecha_creacion'),
    ).annotate(
        estado_asignacion_entrevista = Case(
            When(estado_asignacion=1, then=Value('Pendiente')),
            When(estado_asignacion=2, then=Value('Apto')),
            When(estado_asignacion=3, then=Value('No Apto')),
            When(estado_asignacion=4, then=Value('Seleccionado')),
            When(estado_asignacion=5, then=Value('Cancelado')),
        ),
        tipo_entrevista = Case(
            When(tipo_entrevista=1, then=Value('Virtual')),
            When(tipo_entrevista=2, then=Value('Presencial')),
        ),
        candidato_nombre = Concat(
            F('asignacion_vacante__candidato_101__primer_nombre'),
            Value(' '),
            F('asignacion_vacante__candidato_101__segundo_nombre'),
            Value(' '),
            F('asignacion_vacante__candidato_101__primer_apellido'),
            Value(' '),
            F('asignacion_vacante__candidato_101__segundo_apellido'),
        ),
        usuario_asigno = Concat(
            F('usuario_asigno__primer_nombre'),
            Value(' '),
            F('usuario_asigno__segundo_nombre'),
            Value(' '),
            F('usuario_asigno__primer_apellido'),
            Value(' '),
            F('usuario_asigno__segundo_apellido'),
        ),
        usuario_asignado = Concat(
            F('usuario_asignado__primer_nombre'),
            Value(' '),
            F('usuario_asignado__segundo_nombre'),
            Value(' '),
            F('usuario_asignado__primer_apellido'),
            Value(' '),
            F('usuario_asignado__segundo_apellido'),
        ),
    ).order_by(
        '-id'
    ).filter(asignacion_vacante__vacante_id_052__cliente_id_051=cliente_id)

    return asignacion_entrevista

