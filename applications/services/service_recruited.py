import random
import string
from django.shortcuts import render, redirect
import json
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from applications.reclutado.models import Cli056AplicacionVacante
from applications.usuarios.decorators  import validar_permisos
from django.db.models import F, Q, Case, When, Value, CharField
from django.db.models.functions import Concat




#Consulta de asignación de vacante por ID
def query_recruited_vacancy_id(vacante_id):
    #consultar vacante
    return Cli056AplicacionVacante.objects.select_related(
        'candidato_101',
        'vacante_id_052',
        'vacante_id_052__asignacion_cliente_id_064__id_cliente_asignado',
        'vacante_id_052__perfil_vacante__lugar_trabajo',
        'vacante_id_052__perfil_vacante__profesion_estudio',
    ).filter(
        vacante_id_052=vacante_id
    ).annotate(
        vacante_id=F('vacante_id_052__id'),
        vacante_titulo=F('vacante_id_052__titulo'),
        vacante_numero_posiciones=F('vacante_id_052__numero_posiciones'),
        vacante_profesion_estudio=F('vacante_id_052__perfil_vacante__profesion_estudio__nombre'),
        vacante_ciudad=F('vacante_id_052__perfil_vacante__lugar_trabajo__nombre'),
        vacante_salario=F('vacante_id_052__perfil_vacante__salario'),
        vacante_fecha_creacion=F('vacante_id_052__fecha_creacion'),
        cliente_id=F('vacante_id_052__asignacion_cliente_id_064__id_cliente_asignado__id'),
        cliente_nit=F('vacante_id_052__asignacion_cliente_id_064__id_cliente_asignado__nit'),
        cliente_razon_social=F('vacante_id_052__asignacion_cliente_id_064__id_cliente_asignado__razon_social'),
        candidato_id=F('candidato_101__id'),
        candidato_documento=F('candidato_101__numero_documento'),
        candidato_imagen_perfil=F('candidato_101__imagen_perfil'),
        candidato_nombre=Concat(
            F('candidato_101__primer_nombre'), Value(' '),
            F('candidato_101__segundo_nombre'), Value(' '),
            F('candidato_101__primer_apellido'), Value(' '),
            F('candidato_101__segundo_apellido')
        ),
        vacante_estado=Case(
            When(vacante_id_052__estado_vacante=1, then=Value('Activa')),
            When(vacante_id_052__estado_vacante=2, then=Value('En Proceso')),
            When(vacante_id_052__estado_vacante=3, then=Value('Finalizada')),
            When(vacante_id_052__estado_vacante=4, then=Value('Cancelada')),
            default=Value('Desconocido'),
            output_field=CharField()
        ),
        aplicacion_vacante_estado=Case(
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
            usuario_asignado_nombre=Concat(
            F('vacante_id_052__usuario_asignado__primer_nombre'),
            Value(' '),
            F('vacante_id_052__usuario_asignado__segundo_nombre'),
            Value(' '),
            F('vacante_id_052__usuario_asignado__primer_apellido'),
            Value(' '),
            F('vacante_id_052__usuario_asignado__segundo_apellido'),
            output_field=CharField()
        )
    ).order_by('-id')