from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, Count, Q, Value, Case, When, CharField
from django.db.models.functions import Concat


#consulta vacantes
from applications.vacante.models import Cli052Vacante


def query_vacanty_all():
    return  Cli052Vacante.objects.select_related(
        'perfil_vacante',
        'cargo',
        'asignacion_cliente_id_064__id_cliente_asignado',
        'usuario_asignado'
    ).annotate(
        nombre_completo=Concat(
            F('usuario_asignado__primer_nombre'), Value(' '),
            F('usuario_asignado__segundo_nombre'), Value(' '),
            F('usuario_asignado__primer_apellido'), Value(' '),
            F('usuario_asignado__segundo_apellido')
        ),
        vacante_estado = Case(
            When(estado_vacante=1, then=Value('Activa')),
            When(estado_vacante=2, then=Value('En Proceso')),
            When(estado_vacante=3, then=Value('Finalizada')),
            When(estado_vacante=4, then=Value('Cancelada')),
            output_field=CharField()  # Definir el tipo de campo de salida
        ),
        total_aplicaciones=Count('aplicaciones'),
        aplicadas=Count('aplicaciones', filter=Q(aplicaciones__estado_aplicacion=1)),
        en_proceso=Count('aplicaciones', filter=Q(aplicaciones__estado_aplicacion__in=[2, 3, 5, 6])),
        finalizadas=Count('aplicaciones', filter=Q(aplicaciones__estado_aplicacion=9)),
        canceladas=Count('aplicaciones', filter=Q(aplicaciones__estado_aplicacion=10)),
        desistidos=Count('aplicaciones', filter=Q(aplicaciones__estado_aplicacion=11)),
        no_aptas=Count('aplicaciones', filter=Q(aplicaciones__estado_aplicacion=12)),
        seleccionados=Count('aplicaciones', filter=Q(aplicaciones__estado_aplicacion=8)),
    )

def query_vacanty_detail():
    return  Cli052Vacante.objects.select_related(
        'perfil_vacante',
        'cargo',
        'asignacion_cliente_id_064__id_cliente_asignado',
        'usuario_asignado'
    )