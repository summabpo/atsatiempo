"""
Funciones comunes para generar los datos de cada panel del dashboard administrador.
Cada función retorna un diccionario con los datos necesarios para renderizar su panel.
"""
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from django.db.models.functions import ExtractMonth


def get_panel_metricas_superiores():
    """
    Panel: 4 tarjetas superiores (Total personal, Vacantes, Clientes, Headhunters).
    Retorna: total_personal, vacantes_total, total_clientes, headhunters
    """
    from applications.candidato.models import Can101Candidato
    from applications.cliente.models import Cli051Cliente
    from applications.vacante.models import Cli052Vacante

    total_personal = Can101Candidato.objects.count()
    vacantes_total = Cli052Vacante.objects.filter(estado_id_001=1).count()
    total_clientes = Cli051Cliente.objects.filter(estado_id_001=1).count()
    headhunters = list(
        Cli051Cliente.objects
        .filter(tipo_cliente='2', estado_id_001=1)
        .select_related('ciudad_id_004')
        .order_by('razon_social')
    )
    return {
        'total_personal': total_personal,
        'vacantes_total': vacantes_total,
        'total_clientes': total_clientes,
        'headhunters': headhunters,
    }


def get_panel_candidatos_por_dia():
    """
    Panel: Candidatos registrados por día (últimos 15 días).
    Retorna: usuarios_por_dia_labels, usuarios_por_dia_data
    """
    from applications.usuarios.models import UsuarioBase

    hoy = timezone.now().date()
    chart_labels = []
    chart_data = []
    for i in range(14, -1, -1):
        d = hoy - timedelta(days=i)
        chart_labels.append(d.strftime('%d/%m'))
        count = UsuarioBase.objects.filter(date_joined__date=d, group_id=2).count()
        chart_data.append(count)
    return {
        'usuarios_por_dia_labels': chart_labels,
        'usuarios_por_dia_data': chart_data,
    }


def get_panel_candidatos_por_mes():
    """
    Panel: Candidatos registrados por mes (año en curso).
    Retorna: usuarios_por_mes_labels, usuarios_por_mes_data, anio_actual
    """
    from applications.usuarios.models import UsuarioBase

    hoy = timezone.now().date()
    anio_actual = hoy.year
    meses_nombres = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    conteo_mensual = (
        UsuarioBase.objects
        .filter(date_joined__year=anio_actual, group_id=2)
        .annotate(mes=ExtractMonth('date_joined'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )
    conteo_por_mes = {r['mes']: r['total'] for r in conteo_mensual}
    usuarios_por_mes_labels = meses_nombres
    usuarios_por_mes_data = [conteo_por_mes.get(m, 0) for m in range(1, 13)]
    return {
        'usuarios_por_mes_labels': usuarios_por_mes_labels,
        'usuarios_por_mes_data': usuarios_por_mes_data,
        'anio_actual': anio_actual,
    }


def get_panel_ciudad_residencia():
    """
    Panel: Candidatos por ciudad de residencia + Resumen por ciudad.
    Retorna: ciudad_labels, ciudad_data, sin_ciudad, con_ciudad
    """
    from applications.candidato.models import Can101Candidato

    ciudad_conteo = (
        Can101Candidato.objects
        .filter(ciudad_id_004__isnull=False)
        .values('ciudad_id_004__nombre')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    ciudad_labels = [c['ciudad_id_004__nombre'] for c in ciudad_conteo]
    ciudad_data = [c['total'] for c in ciudad_conteo]
    sin_ciudad = Can101Candidato.objects.filter(ciudad_id_004__isnull=True).count()
    con_ciudad = sum(ciudad_data)
    return {
        'ciudad_labels': ciudad_labels,
        'ciudad_data': ciudad_data,
        'sin_ciudad': sin_ciudad,
        'con_ciudad': con_ciudad,
    }


def get_panel_tipo_estudio():
    """
    Panel: Tipo de estudio (donut + lista).
    Retorna: nivel_estudio_labels, nivel_estudio_data, nivel_estudio_labels_zip, nivel_estudio_items
    """
    from applications.candidato.models import Can103Educacion
    from applications.services.choices import NIVEL_ESTUDIO_CHOICES_STATIC

    nivel_labels_dict = dict(NIVEL_ESTUDIO_CHOICES_STATIC)
    niveles_orden = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    conteo_por_nivel = {n: 0 for n in niveles_orden}

    estudios_con_tipo = (
        Can103Educacion.objects
        .filter(candidato_id_101__isnull=False, tipo_estudio__isnull=False)
        .exclude(tipo_estudio='')
        .values_list('candidato_id_101_id', 'tipo_estudio')
    )
    max_por_candidato = {}
    for candidato_id, tipo in estudios_con_tipo:
        if candidato_id not in max_por_candidato or tipo > max_por_candidato[candidato_id]:
            max_por_candidato[candidato_id] = tipo

    for tipo in max_por_candidato.values():
        if tipo in conteo_por_nivel:
            conteo_por_nivel[tipo] += 1

    nivel_estudio_labels = [nivel_labels_dict.get(n, n) for n in niveles_orden]
    nivel_estudio_data = [conteo_por_nivel[n] for n in niveles_orden]
    nivel_estudio_labels_zip = list(zip(nivel_estudio_labels, nivel_estudio_data))

    nivel_colors = ['#6c757d', '#0d6efd', '#198754', '#ffc107', '#fd7e14', '#B10022', '#6610f2', '#20c997', '#e83e8c']
    total_candidatos = sum(nivel_estudio_data)
    nivel_estudio_items = []
    for i, (label, count) in enumerate(nivel_estudio_labels_zip):
        pct = round((count / total_candidatos * 100), 1) if total_candidatos > 0 else 0
        nivel_estudio_items.append({
            'label': label,
            'count': count,
            'percentage': pct,
            'color': nivel_colors[i % len(nivel_colors)],
        })
    return {
        'nivel_estudio_labels': nivel_estudio_labels,
        'nivel_estudio_data': nivel_estudio_data,
        'nivel_estudio_labels_zip': nivel_estudio_labels_zip,
        'nivel_estudio_items': nivel_estudio_items,
        'nivel_estudio_colors': nivel_colors,
    }


def get_panel_profesion_estudio():
    """
    Panel: Candidatos por profesión o estudio (top 15).
    Retorna: profesion_labels, profesion_data
    """
    from applications.candidato.models import Can103Educacion

    profesion_conteo = (
        Can103Educacion.objects
        .filter(profesion_estudio__isnull=False)
        .values('profesion_estudio__nombre')
        .annotate(total=Count('candidato_id_101', distinct=True))
        .order_by('-total')[:15]
    )
    profesion_labels = [p['profesion_estudio__nombre'] for p in profesion_conteo]
    profesion_data = [p['total'] for p in profesion_conteo]
    return {
        'profesion_labels': profesion_labels,
        'profesion_data': profesion_data,
    }


def get_panel_metricas_analista_interno(user_id):
    """
    Métricas del dashboard analista interno (vacantes asignadas al usuario).
    - vacantes_asignadas_analista: vacantes activas con usuario_asignado = user_id
    - vacantes_pendientes_entrevista: vacantes distintas con ≥1 aplicación en estado Aplicado (1)
    - vacantes_pendientes_respuesta_cliente: vacantes distintas con aplicación en 8/12/13 sin descripcion_respuesta_cliente
    - vacantes_terminadas: vacantes finalizadas (estado_vacante=3) asignadas al analista
    """
    from applications.vacante.models import Cli052Vacante
    from applications.reclutado.models import Cli056AplicacionVacante

    vacantes_terminadas = Cli052Vacante.objects.filter(
        usuario_asignado_id=user_id,
        estado_id_001=1,
        estado_vacante=3,
    ).count()

    vacantes_qs = Cli052Vacante.objects.filter(usuario_asignado_id=user_id, estado_id_001=1)
    vacantes_asignadas_analista = vacantes_qs.count()
    vac_ids = list(vacantes_qs.values_list('id', flat=True))
    if not vac_ids:
        return {
            'vacantes_asignadas_analista': 0,
            'vacantes_pendientes_entrevista': 0,
            'vacantes_pendientes_respuesta_cliente': 0,
            'vacantes_terminadas': vacantes_terminadas,
        }

    vacantes_pendientes_entrevista = (
        Cli056AplicacionVacante.objects.filter(
            vacante_id_052_id__in=vac_ids,
            estado_aplicacion=1,
        )
        .values('vacante_id_052_id')
        .distinct()
        .count()
    )

    qs_resp = Cli056AplicacionVacante.objects.filter(
        vacante_id_052_id__in=vac_ids,
        estado_aplicacion__in=[8, 12, 13],
    ).filter(
        Q(registro_reclutamiento__isnull=True)
        | Q(registro_reclutamiento__descripcion_respuesta_cliente__isnull=True)
        | Q(registro_reclutamiento__descripcion_respuesta_cliente='')
    )
    vacantes_pendientes_respuesta_cliente = qs_resp.values('vacante_id_052_id').distinct().count()

    return {
        'vacantes_asignadas_analista': vacantes_asignadas_analista,
        'vacantes_pendientes_entrevista': vacantes_pendientes_entrevista,
        'vacantes_pendientes_respuesta_cliente': vacantes_pendientes_respuesta_cliente,
        'vacantes_terminadas': vacantes_terminadas,
    }


def get_panel_metricas_reclutador(user_id):
    """
    Métricas del dashboard reclutador (vacantes con asignacion_reclutador = usuario).
    - vacantes_asignadas_reclutador: vacantes activas asignadas al reclutador
    - total_aplicaciones_reclutador: total de aplicaciones en esas vacantes
    - aspirantes_reclutador: estado_reclutamiento = 1 (aspirantes / recibidos)
    - precalificados_reclutador: estado_reclutamiento = 2 (precalificados por CV)
    - aprobados_entrevista_reclutador: estado_reclutamiento = 3 (aprobados para entrevista)
    - descartados_reclutador: estado_reclutamiento = 4
    - seleccionados_pipeline_reclutador: estado_aplicacion en 8 o 13 (seleccionado en el proceso)
    """
    from applications.vacante.models import Cli052Vacante
    from applications.reclutado.models import Cli056AplicacionVacante

    vacantes_qs = Cli052Vacante.objects.filter(
        asignacion_reclutador_id=user_id,
        estado_id_001=1,
    )
    vacantes_asignadas_reclutador = vacantes_qs.count()
    vac_ids = list(vacantes_qs.values_list('id', flat=True))

    if not vac_ids:
        return {
            'vacantes_asignadas_reclutador': 0,
            'total_aplicaciones_reclutador': 0,
            'aspirantes_reclutador': 0,
            'precalificados_reclutador': 0,
            'aprobados_entrevista_reclutador': 0,
            'descartados_reclutador': 0,
            'seleccionados_pipeline_reclutador': 0,
        }

    base = Cli056AplicacionVacante.objects.filter(vacante_id_052_id__in=vac_ids)
    
    return {
        'vacantes_asignadas_reclutador': vacantes_asignadas_reclutador,
        'total_aplicaciones_reclutador': base.count(),
        'aspirantes_reclutador': base.filter(estado_reclutamiento=1).count(),
        'precalificados_reclutador': base.filter(estado_reclutamiento=2).count(),
        'aprobados_entrevista_reclutador': base.filter(estado_reclutamiento=3).count(),
        'descartados_reclutador': base.filter(estado_reclutamiento=4).count(),
        'seleccionados_pipeline_reclutador': base.filter(estado_aplicacion__in=[8, 13]).count(),
    }
