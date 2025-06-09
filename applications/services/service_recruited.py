import random
import string
from django.shortcuts import render, redirect
import json
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from applications.reclutado.models import Cli056AplicacionVacante, Cli063AplicacionVacanteHistorial
from applications.services.choices import ESTADO_APLICACION_COLOR_STATIC
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


def consultar_historial_aplicacion_vacante(aplicacion_vacante_id):
    # Luego de obtener el candidato y demás datos...
    historial_aplicaciones = (
        Cli063AplicacionVacanteHistorial.objects
        .filter(aplicacion_vacante_056__id=aplicacion_vacante_id)
        .select_related('aplicacion_vacante_056', 'usuario_id_genero')
        .order_by('-fecha')
    )

    return  [
        {
            'id': h.id,
            'fecha': h.fecha,
            'usuario': str(h.usuario_id_genero) if h.usuario_id_genero else "Sistema",
            'estado': h.get_estado_display(),
            'descripcion': h.descripcion,
            'vacante': str(h.aplicacion_vacante_056.vacante_id_050) if hasattr(h.aplicacion_vacante_056, 'vacante_id_050') else '',
            'aplicacion_id': h.aplicacion_vacante_056.id,
        }
        for h in historial_aplicaciones
    ]

def consultar_historial_aplicacion_vacante_candidate(aplicacion_vacante_id):
    # Luego de obtener el candidato y demás datos...
    historial_aplicaciones = (
        Cli063AplicacionVacanteHistorial.objects
        .filter(aplicacion_vacante_056__id=aplicacion_vacante_id)
        .select_related('aplicacion_vacante_056', 'usuario_id_genero')
        .order_by('-fecha')
    )

    historial_datos = []
    for h in historial_aplicaciones:

        estado_info = ESTADO_APLICACION_COLOR_STATIC.get(h.estado, {'estado': 'Desconocido', 'color': 'gris'})


        historial_datos.append({
            'estado': estado_info[0],
            'color': estado_info[1],
            'descripcion': h.descripcion if h.descripcion else 'Sin descripción disponible.',
            'usuario': f'{h.usuario_id_genero.first_name} {h.usuario_id_genero.last_name}' if h.usuario_id_genero else 'Sistema',
            'vacante': h.aplicacion_vacante_056.vacante_id_052.titulo,  # Ajusta el campo si es necesario
            'aplicacion_id': h.aplicacion_vacante_056.id,
            'fecha': h.fecha
        })

    return historial_datos