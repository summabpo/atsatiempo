import random
import string
from django.shortcuts import render, redirect
import json
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from applications.usuarios.decorators  import validar_permisos
from django.db.models import F, Q, Case, When, Value, CharField, Count, Exists, OuterRef
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

def consulta_vacantes_todas():
    vacantes = Cli052Vacante.objects.select_related(
        'cliente_id_051',
        'ciudad',
        'profesion_estudio_id_055',
    ).values(
        'id',
        'fecha_creacion',
        'titulo',
        'numero_posiciones',
        'ciudad__nombre',
        'profesion_estudio_id_055__nombre',
        'funciones_responsabilidades',
        'salario',
        'cliente_id_051__razon_social',
        'estado_vacante',
    ).annotate(
        vacante_estado = Case(
            When(estado_vacante=1, then=Value('Activa')),
            When(estado_vacante=2, then=Value('En Proceso')),
            When(estado_vacante=3, then=Value('Finalizada')),
            When(estado_vacante=4, then=Value('Cancelada')),
            output_field=CharField()  # Definir el tipo de campo de salida
        ),
        vacante_experiencia_requerida = Case(
            When(experiencia_requerida=1, then=Value('0 a 6 Meses')),
            When(experiencia_requerida=2, then=Value('1 año a 2 años')),
            When(experiencia_requerida=3, then=Value('Más de 2 años')),
            When(experiencia_requerida=4, then=Value('Sin Experiencia')),
            output_field=CharField()  # Definir el tipo de campo de salida
        ),
        vacante_aplicados = Count('aplicaciones'),
        # Contador de aplicaciones por estado
        aplicados=Count(
            'aplicaciones',
            filter=Q(aplicaciones__estado_aplicacion=1) | Q(aplicaciones__estado_aplicacion=2) | Q(aplicaciones__estado_aplicacion=3) | Q(aplicaciones__estado_aplicacion=5) | Q(aplicaciones__estado_aplicacion=6)
        ),
        no_apto=Count(
            'aplicaciones',
            filter=Q(aplicaciones__estado_aplicacion=4) | Q(aplicaciones__estado_aplicacion=7)
        ),
        seleccionados=Count(
            'aplicaciones',
            filter=Q(aplicaciones__estado_aplicacion=8)
        ),
        canceladas=Count(
            'aplicaciones',
            filter=Q(aplicaciones__estado_aplicacion=10)
        ),
        desistidos=Count(
            'aplicaciones',
            filter=Q(aplicaciones__estado_aplicacion=11)
        )
    ).filter(estado_id_001=1).order_by('-id')

    return vacantes

def consulta_vacantes_disponibles(candidato_id):
    # Subquery que verifica si existe una aplicación para el candidato actual y la vacante
    subquery = Cli056AplicacionVacante.objects.filter(
        candidato_101_id=candidato_id,
        vacante_id_052=OuterRef('pk')
    )

    vacantes = Cli052Vacante.objects.select_related(
            'cliente_id_051',
            'ciudad',
            'profesion_estudio_id_055',
        ).annotate(
            aplicada=Exists(subquery)  # Campo booleano que indica si ya se ha aplicado
        ).filter(
            estado_id_001 = 1,  # Filtra vacantes activas
            estado_vacante=1  # Filtra vacantes activas
        ).order_by(
            '-aplicada', '-id' # Ordenar por aplicación y luego por ID
        ).values(
            'id',
            'fecha_creacion',
            'titulo',
            'numero_posiciones',
            'ciudad__nombre',
            'profesion_estudio_id_055__nombre',
            'funciones_responsabilidades',
            'salario',
            'cliente_id_051__razon_social',
            'aplicada',  # Incluye el campo que indica si ya se aplicó
        )  

    return vacantes

def consulta_vacantes_cliente(cliente_id):
    vacantes = Cli052Vacante.objects.select_related(
        'cliente_id_051',
        'ciudad',
        'profesion_estudio_id_055',
    ).values(
        'id',
        'fecha_creacion',
        'titulo',
        'numero_posiciones',
        'ciudad__nombre',
        'profesion_estudio_id_055__nombre',
        'funciones_responsabilidades',
        'salario',
        'cliente_id_051__razon_social',
        'estado_vacante',
    ).annotate(
        vacante_estado = Case(
            When(estado_vacante=1, then=Value('Activa')),
            When(estado_vacante=2, then=Value('En Proceso')),
            When(estado_vacante=3, then=Value('Finalizada')),
            When(estado_vacante=4, then=Value('Cancelada')),
            output_field=CharField()  # Definir el tipo de campo de salida
        ),
        vacante_experiencia_requerida = Case(
            When(experiencia_requerida=1, then=Value('0 a 6 Meses')),
            When(experiencia_requerida=2, then=Value('1 año a 2 años')),
            When(experiencia_requerida=3, then=Value('Más de 2 años')),
            When(experiencia_requerida=4, then=Value('Sin Experiencia')),
            output_field=CharField()  # Definir el tipo de campo de salida
        ),
        vacante_aplicados = Count('aplicaciones'),
        # Contador de aplicaciones por estado
        aplicados=Count(
            'aplicaciones',
            filter=Q(aplicaciones__estado_aplicacion=1) | Q(aplicaciones__estado_aplicacion=2) | Q(aplicaciones__estado_aplicacion=3) | Q(aplicaciones__estado_aplicacion=5) | Q(aplicaciones__estado_aplicacion=6)
        ),
        no_apto=Count(
            'aplicaciones',
            filter=Q(aplicaciones__estado_aplicacion=4) | Q(aplicaciones__estado_aplicacion=7) | Q(aplicaciones__estado_aplicacion=12)
        ),
        seleccionados=Count(
            'aplicaciones',
            filter=Q(aplicaciones__estado_aplicacion=8)
        ),
        canceladas=Count(
            'aplicaciones',
            filter=Q(aplicaciones__estado_aplicacion=10)
        ),
        desistidos=Count(
            'aplicaciones',
            filter=Q(aplicaciones__estado_aplicacion=11)
        )
    ).filter(cliente_id_051=cliente_id, estado_id_001=1).order_by('-id')

    return vacantes
