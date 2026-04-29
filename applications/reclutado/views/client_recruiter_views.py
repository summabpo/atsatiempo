from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.db.models import F, Count, Q, Value, Case, When, CharField
from django.contrib import messages
from django.utils import timezone
from datetime import date, timedelta
from zoneinfo import ZoneInfo
from django.views.decorators.clickjacking import xframe_options_exempt

# Hora civil Colombia para registros en JSON (evita guardar ISO solo en UTC y confundir al leer en BD/UI)
_BOGOTA_TZ = ZoneInfo('America/Bogota')
from applications.common.models import Cat001Estado
from applications.usuarios.decorators  import validar_permisos
from applications.candidato.models import Can103Educacion
import json

#models
from applications.reclutado.models import Cli056AplicacionVacante
from applications.vacante.models import Cli052Vacante
from applications.candidato.models import Can101Candidato
from applications.entrevista.models import Cli057AsignacionEntrevista
from applications.usuarios.models import UsuarioBase
from applications.services.service_vacanty import query_vacanty_all, get_vacanty_questions
from applications.services.service_interview import query_interview_all, attach_ultima_entrevista_a_reclutados
from applications.services.service_recruited import query_recruited_vacancy_id
from applications.services.service_client import query_client_detail
from applications.services.service_candidate import buscar_candidato
from applications.services.choices import (
    ESTADO_APLICACION_COLOR_STATIC,
    ESTADO_RECLUTADO_CHOICES_STATIC,
    ESTADO_RECLUTADO_COLOR_STATIC,
)
from applications.common.views.EnvioCorreo import enviar_correo, generar_token_documento
from components.RegistrarHistorialVacante import crear_historial_aplicacion

#forms
from applications.reclutado.forms.FormRecruited import ActualizarEstadoReclutadoForm, BusquedaRecibidosForm
from applications.vacante.forms.EntrevistaForm import EntrevistaCrearForm


@login_required
@validar_permisos('acceso_reclutador')
def vacancies_assigned_recruiter(request):

    # Consultar vacantes asignadas al reclutador con estadísticas
    vacantes = query_vacanty_all()
    vacantes = vacantes.filter(
        asignacion_reclutador=request.user,
        estado_id_001=1
    ).annotate(
        # Contar personal reclutado (estado_reclutamiento en 2 o 3: Seleccionado o Finalizalista)
        reclutados_recibido=Count(
            'aplicaciones',
            filter=Q(aplicaciones__estado_reclutamiento=1)
        ),
        reclutados_seleccionado=Count(
            'aplicaciones',
            filter=Q(aplicaciones__estado_reclutamiento=2)
        ),
        reclutados_finalizalista=Count(
            'aplicaciones',
            filter=Q(aplicaciones__estado_reclutamiento=3)
        ),
        reclutados_descartado=Count(
            'aplicaciones',
            filter=Q(aplicaciones__estado_reclutamiento=4)
        ),
        # Personal reclutado: suma de seleccionados y finalistas
        personal_reclutado=Count(
            'aplicaciones',
            filter=Q(aplicaciones__estado_reclutamiento__in=[2, 3])
        )
    )

    context = {
        'vacantes': vacantes,
    }

    return render(request, 'admin/recruiter/client_recruiter/vacancies_assigned_recruiter.html', context)


@login_required
@validar_permisos('acceso_reclutador')
def vacancies_assigned_recruiter_detail(request, pk, vacante_id):
    # Verificar que la vacante esté asignada al reclutador actual
    vacante = get_object_or_404(
        Cli052Vacante.objects.prefetch_related('habilidades'),
        id=vacante_id,
        asignacion_reclutador=request.user,
        estado_id_001=1
    )
    
    # Obtener el cliente asignado
    cliente_id = None
    if vacante.asignacion_cliente_id_064 and vacante.asignacion_cliente_id_064.id_cliente_asignado:
        cliente_id = vacante.asignacion_cliente_id_064.id_cliente_asignado.id
        data = query_client_detail(cliente_id)
    else:
        data = None
    
    # Obtener información de las entrevistas por vacante
    entrevistas = query_interview_all()
    entrevistas = entrevistas.filter(asignacion_vacante__vacante_id_052=vacante.id)
    
    # Obtener preguntas de la vacante
    preguntas = get_vacanty_questions(vacante.id)
    
    # Obtener los reclutados asociados a la vacante
    reclutados = query_recruited_vacancy_id(vacante.id)
    
    # Formulario de entrevista para múltiples candidatos
    grupo_id = request.session.get('grupo_id', 2)  # Default grupo reclutador
    form_entrevista_multiples = EntrevistaCrearForm(
        grupo_id=grupo_id, 
        cliente_id=cliente_id, 
        vacante=vacante,
        modal_id='modalAsignarEntrevistas'  # ID del modal para el dropdown-parent
    )
    
    # Agrupar reclutados por estado de reclutamiento y ordenar por fecha de aplicación ascendente
    reclutados_recibido = sorted([r for r in reclutados if r.estado_reclutamiento == 1], key=lambda x: (x.fecha_aplicacion or timezone.now(), x.id))
    reclutados_seleccionado = sorted([r for r in reclutados if r.estado_reclutamiento == 2], key=lambda x: (x.fecha_aplicacion or timezone.now(), x.id))
    reclutados_finalizalista = sorted([r for r in reclutados if r.estado_reclutamiento == 3], key=lambda x: (x.fecha_aplicacion or timezone.now(), x.id))
    reclutados_descartado = sorted([r for r in reclutados if r.estado_reclutamiento == 4], key=lambda x: (x.fecha_aplicacion or timezone.now(), x.id))
    attach_ultima_entrevista_a_reclutados(reclutados_finalizalista)

    # Procesar formulario de búsqueda para Recibidos
    form_busqueda = BusquedaRecibidosForm(request.GET)
    if form_busqueda.is_valid():
        nombre_candidato = form_busqueda.cleaned_data.get('nombre_candidato')
        fecha_inicio = form_busqueda.cleaned_data.get('fecha_inicio')
        fecha_fin = form_busqueda.cleaned_data.get('fecha_fin')
        edad_minima = form_busqueda.cleaned_data.get('edad_minima')
        edad_maxima = form_busqueda.cleaned_data.get('edad_maxima')
        nivel_estudio = form_busqueda.cleaned_data.get('nivel_estudio')
        puntaje_match_minimo = form_busqueda.cleaned_data.get('puntaje_match_minimo')
        
        # Aplicar filtros
        reclutados_recibido_filtrados = reclutados_recibido.copy()
        
        if nombre_candidato:
            nombre_lower = nombre_candidato.lower()
            reclutados_recibido_filtrados = [
                r for r in reclutados_recibido_filtrados
                if nombre_lower in r.candidato_nombre.lower()
            ]
        
        if fecha_inicio:
            reclutados_recibido_filtrados = [
                r for r in reclutados_recibido_filtrados
                if r.fecha_aplicacion and r.fecha_aplicacion >= fecha_inicio
            ]
        
        if fecha_fin:
            reclutados_recibido_filtrados = [
                r for r in reclutados_recibido_filtrados
                if r.fecha_aplicacion and r.fecha_aplicacion <= fecha_fin
            ]
        
        if edad_minima or edad_maxima:
            hoy = date.today()
            reclutados_recibido_filtrados_edad = []
            for r in reclutados_recibido_filtrados:
                if r.candidato_101 and r.candidato_101.fecha_nacimiento:
                    edad = hoy.year - r.candidato_101.fecha_nacimiento.year
                    if (hoy.month, hoy.day) < (r.candidato_101.fecha_nacimiento.month, r.candidato_101.fecha_nacimiento.day):
                        edad -= 1
                    
                    cumple_edad = True
                    if edad_minima and edad < edad_minima:
                        cumple_edad = False
                    if edad_maxima and edad > edad_maxima:
                        cumple_edad = False
                    
                    if cumple_edad:
                        reclutados_recibido_filtrados_edad.append(r)
                else:
                    # Si no tiene fecha de nacimiento, incluir solo si no hay filtro de edad mínima
                    if not edad_minima:
                        reclutados_recibido_filtrados_edad.append(r)
            reclutados_recibido_filtrados = reclutados_recibido_filtrados_edad
        
        if nivel_estudio:
            reclutados_recibido_filtrados_nivel = []
            for r in reclutados_recibido_filtrados:
                if r.candidato_101:
                    educaciones = Can103Educacion.objects.filter(
                        candidato_id_101=r.candidato_101.id,
                        tipo_estudio=nivel_estudio
                    )
                    if educaciones.exists():
                        reclutados_recibido_filtrados_nivel.append(r)
            reclutados_recibido_filtrados = reclutados_recibido_filtrados_nivel
        
        if puntaje_match_minimo:
            reclutados_recibido_filtrados_puntaje = []
            for r in reclutados_recibido_filtrados:
                porcentaje = None
                if r.json_match:
                    try:
                        if isinstance(r.json_match, str):
                            json_match_dict = json.loads(r.json_match)
                        else:
                            json_match_dict = r.json_match
                        
                        # Acceder al porcentaje_total siguiendo la misma lógica del template tag
                        if isinstance(json_match_dict, dict) and 'resumen' in json_match_dict:
                            resumen = json_match_dict.get('resumen', {})
                            if isinstance(resumen, dict) and 'porcentaje_total' in resumen:
                                porcentaje = resumen.get('porcentaje_total')
                    except (json.JSONDecodeError, TypeError, AttributeError):
                        porcentaje = None
                
                if porcentaje and float(porcentaje) >= float(puntaje_match_minimo):
                    reclutados_recibido_filtrados_puntaje.append(r)
            reclutados_recibido_filtrados = reclutados_recibido_filtrados_puntaje
        
        reclutados_recibido = sorted(reclutados_recibido_filtrados, key=lambda x: (x.fecha_aplicacion or timezone.now(), x.id))
    
    context = {
        'data': data,
        'vacante': vacante,
        'reclutados': reclutados,
        'reclutados_recibido': reclutados_recibido,
        'reclutados_seleccionado': reclutados_seleccionado,
        'reclutados_finalizalista': reclutados_finalizalista,
        'reclutados_descartado': reclutados_descartado,
        'entrevistas': entrevistas,
        'preguntas': preguntas,
        'form_busqueda': form_busqueda,
        'form_entrevista_multiples': form_entrevista_multiples,
        'pk': pk,  # ID del cliente para usar en las URLs
    }
    
    return render(request, 'admin/recruiter/client_recruiter/vacancies_assigned_recruiter_detail.html', context)


@login_required
@validar_permisos('acceso_reclutador')
def vacancies_assigned_recruiter_detail2(request, pk, vacante_id):
    """
    Lista TODO el personal reclutado (todas las aplicaciones) de una vacante asignada al reclutador.
    """
    vacante = get_object_or_404(
        Cli052Vacante.objects.select_related("asignacion_cliente_id_064", "cargo").prefetch_related("habilidades"),
        id=vacante_id,
        asignacion_reclutador=request.user,
        estado_id_001=1,
    )
    cliente_id = None
    if vacante.asignacion_cliente_id_064 and vacante.asignacion_cliente_id_064.id_cliente_asignado:
        cliente_id = vacante.asignacion_cliente_id_064.id_cliente_asignado.id

    grupo_id = request.session.get('grupo_id', 2)
    form_entrevista_multiples = EntrevistaCrearForm(
        grupo_id=grupo_id,
        cliente_id=cliente_id,
        vacante=vacante,
        modal_id='modalAsignarEntrevistaUnica',
    )

    reclutados = query_recruited_vacancy_id(vacante.id)
    reclutados = sorted(
        reclutados,
        key=lambda x: (
            x.estado_reclutamiento or 0,
            x.fecha_aplicacion or timezone.now(),
            x.id,
        ),
    )

    # Edad y nivel de estudio más alto (por candidato)
    candidato_ids = [
        r.candidato_101_id
        for r in reclutados
        if getattr(r, "candidato_101_id", None)
    ]
    candidato_ids = list({int(cid) for cid in candidato_ids})

    estudios_qs = (
        Can103Educacion.objects.filter(candidato_id_101_id__in=candidato_ids, tipo_estudio__isnull=False)
        .exclude(tipo_estudio="")
        .order_by("candidato_id_101_id", "-tipo_estudio", "-id")
        .only("id", "candidato_id_101_id", "tipo_estudio")
    )
    estudio_mas_alto_por_candidato = {}
    for e in estudios_qs:
        if e.candidato_id_101_id not in estudio_mas_alto_por_candidato:
            estudio_mas_alto_por_candidato[e.candidato_id_101_id] = e.mostrar_tipo_estudio()

    hoy = date.today()
    for r in reclutados:
        edad = None
        cand = getattr(r, "candidato_101", None)
        fn = getattr(cand, "fecha_nacimiento", None) if cand else None
        if fn:
            edad = hoy.year - fn.year - (1 if (hoy.month, hoy.day) < (fn.month, fn.day) else 0)

        r.edad_anios = edad
        r.nivel_estudio_maximo = estudio_mas_alto_por_candidato.get(
            getattr(r, "candidato_101_id", None),
            "Sin estudios registrados",
        )
        _estado_nombre, _estado_color = ESTADO_RECLUTADO_COLOR_STATIC.get(
            getattr(r, "estado_reclutamiento", None),
            ("Desconocido", "secondary"),
        )
        r.estado_reclutamiento_color = _estado_color

    estados_map = dict(ESTADO_RECLUTADO_CHOICES_STATIC)
    estados_aplicacion_color = ESTADO_APLICACION_COLOR_STATIC
    conteo_por_estado = {}
    for r in reclutados:
        codigo = getattr(r, "estado_reclutamiento", None)
        if codigo is None:
            continue
        conteo_por_estado[codigo] = conteo_por_estado.get(codigo, 0) + 1
    estados_reclutado_leyenda = []
    for codigo, nombre in ESTADO_RECLUTADO_CHOICES_STATIC:
        if codigo in ("", None):
            continue
        _nombre, color = ESTADO_RECLUTADO_COLOR_STATIC.get(codigo, (nombre, "secondary"))
        estados_reclutado_leyenda.append({
            "codigo": codigo,
            "nombre": nombre,
            "color": color,
            "total": conteo_por_estado.get(codigo, 0),
        })

    context = {
        "vacante": vacante,
        "reclutados": reclutados,
        "estados_map": estados_map,
        "estados_aplicacion_color": estados_aplicacion_color,
        "estados_reclutado_opciones": list(ESTADO_RECLUTADO_CHOICES_STATIC),
        "estados_reclutado_leyenda": estados_reclutado_leyenda,
        "form_entrevista_multiples": form_entrevista_multiples,
        "pk": pk,
    }
    return render(
        request,
        "admin/recruiter/client_recruiter/vacancies_assigned_recruiter_detail2.html",
        context,
    )


def _historial_estados_lista_desde_registro(registro_reclutamiento):
    historial_estados = []
    if registro_reclutamiento:
        try:
            if isinstance(registro_reclutamiento, str):
                historial_estados = json.loads(registro_reclutamiento)
            else:
                historial_estados = registro_reclutamiento
            if not isinstance(historial_estados, list):
                historial_estados = []
        except (json.JSONDecodeError, TypeError):
            historial_estados = []
    return historial_estados


def aplicar_cambio_estado_reclutado(request, asignacion_vacante, nuevo_estado, comentario):
    """
    Persiste el cambio de estado y el historial en registro_reclutamiento
    (misma lógica que el POST del detalle reclutado).
    Devuelve (nombre_estado_anterior, nombre_estado_nuevo).
    """
    historial_estados = _historial_estados_lista_desde_registro(asignacion_vacante.registro_reclutamiento)
    estado_anterior_nombre = dict(ESTADO_RECLUTADO_CHOICES_STATIC).get(asignacion_vacante.estado_reclutamiento, 'Desconocido')
    estado_nuevo_nombre = dict(ESTADO_RECLUTADO_CHOICES_STATIC).get(nuevo_estado, 'Desconocido')

    ahora_bogota = timezone.now().astimezone(_BOGOTA_TZ)
    nuevo_registro = {
        "fecha_actualizacion": ahora_bogota.strftime("%d/%m/%Y"),
        "hora_actualizacion": ahora_bogota.strftime("%H:%M"),
        "fecha_hora_actualizacion": ahora_bogota.isoformat(),
        "id_usuario_registro": request.user.id,
        "comentario": comentario,
        "estado_anterior": {
            "codigo": asignacion_vacante.estado_reclutamiento,
            "nombre": estado_anterior_nombre,
        },
        "estado_nuevo": {
            "codigo": nuevo_estado,
            "nombre": estado_nuevo_nombre,
        },
    }
    historial_estados.append(nuevo_registro)
    asignacion_vacante.estado_reclutamiento = nuevo_estado
    asignacion_vacante.registro_reclutamiento = historial_estados
    asignacion_vacante.save()
    return estado_anterior_nombre, estado_nuevo_nombre


@login_required
@validar_permisos('acceso_reclutador')
def cambiar_estado_personal_reclutador(request, pk, vacante_id):
    """POST: cambio de estado desde la lista de personal reclutado (misma gestión que detalle reclutado)."""
    redirect_lista = redirect('reclutados:vacantes_gestion_reclutador_detail2', pk=pk, vacante_id=vacante_id)

    if request.method != 'POST':
        messages.error(request, 'Método no permitido.')
        return redirect_lista

    aplicacion_id = request.POST.get('aplicacion_id')
    if not aplicacion_id or not str(aplicacion_id).isdigit():
        messages.error(request, 'Solicitud inválida.')
        return redirect_lista

    vacante = get_object_or_404(
        Cli052Vacante.objects.select_related('asignacion_cliente_id_064'),
        id=vacante_id,
        asignacion_reclutador=request.user,
        estado_id_001=1,
    )
    ac = getattr(vacante.asignacion_cliente_id_064, 'id_cliente_asignado_id', None)
    if ac is None or ac != pk:
        messages.error(request, 'No tiene permisos para gestionar esta aplicación.')
        return redirect_lista

    asignacion_vacante = get_object_or_404(
        Cli056AplicacionVacante.objects.select_related('vacante_id_052'),
        id=int(aplicacion_id),
        vacante_id_052=vacante,
    )

    if request.session.get('grupo_id') not in (3, 5, 6):
        if asignacion_vacante.vacante_id_052.asignacion_reclutador != request.user:
            messages.error(request, 'No tiene permisos para acceder a este candidato.')
            return redirect('reclutados:vacantes_asignadas_reclutador')

    form = ActualizarEstadoReclutadoForm(request.POST, estado_actual=asignacion_vacante.estado_reclutamiento)
    if form.is_valid():
        nuevo_estado = int(form.cleaned_data['estado_reclutamiento'])
        comentario = form.cleaned_data['comentario']
        estado_ant, estado_nuevo = aplicar_cambio_estado_reclutado(
            request, asignacion_vacante, nuevo_estado, comentario
        )
        messages.success(
            request,
            f'Estado actualizado de {estado_ant} a {estado_nuevo} exitosamente.',
        )
    else:
        messages.error(request, 'Error al actualizar el estado. Verifique los datos.')

    return redirect_lista


@login_required
@validar_permisos('acceso_reclutador', 'acceso_admin', 'acceso_cliente', 'acceso_analista_seleccion_ats', 'acceso_analista_seleccion')
def detail_recruited(request, pk):
    # Obtener la aplicación de vacante
    asignacion_vacante = get_object_or_404(Cli056AplicacionVacante, id=pk)
    
    if request.session.get('grupo_id') != 3 and request.session.get('grupo_id') != 5 and request.session.get('grupo_id') != 6:
        # Verificar que la vacante esté asignada al reclutador actual
        if asignacion_vacante.vacante_id_052.asignacion_reclutador != request.user:
            messages.error(request, 'No tiene permisos para acceder a este candidato.')
            return redirect('reclutados:vacantes_asignadas_reclutador')
    
    # Obtener información del candidato
    candidato = get_object_or_404(Can101Candidato, id=asignacion_vacante.candidato_101.id)
    info_detalle_candidato = buscar_candidato(candidato.id)
    
    # Obtener información de la vacante
    vacante = asignacion_vacante.vacante_id_052

    # Otras aplicaciones del mismo candidato con vacantes del mismo cliente asignado (asignación 064)
    otras_aplicaciones_mismo_cliente = []
    cliente_asignado_otros_procesos = None
    asig_vac = getattr(vacante, 'asignacion_cliente_id_064', None)
    if asig_vac and getattr(asig_vac, 'id_cliente_asignado_id', None):
        cliente_asignado_otros_procesos = asig_vac.id_cliente_asignado
        otras_aplicaciones_mismo_cliente = list(
            Cli056AplicacionVacante.objects.filter(
                candidato_101_id=candidato.id,
                vacante_id_052__asignacion_cliente_id_064__id_cliente_asignado_id=asig_vac.id_cliente_asignado_id,
            )
            .exclude(pk=asignacion_vacante.pk)
            .select_related('vacante_id_052', 'vacante_id_052__cargo')
            .order_by('-fecha_aplicacion', '-id')
        )

    # Obtener el JSON match inicial
    json_match_inicial_raw = asignacion_vacante.json_match_inicial
    if json_match_inicial_raw:
        try:
            if isinstance(json_match_inicial_raw, str):
                json_match_inicial = json.loads(json_match_inicial_raw)
            else:
                json_match_inicial = json_match_inicial_raw
        except (json.JSONDecodeError, TypeError):
            json_match_inicial = {}
    else:
        json_match_inicial = {}

    match_inicial_gauge_pct = None
    match_inicial_gauge_pct_int = None
    _pond = json_match_inicial.get('ponderaciones') if isinstance(json_match_inicial, dict) else None
    if isinstance(_pond, dict):
        try:
            total_v = _pond.get('total')
            total_max_v = _pond.get('total_maximo')
            if total_v is not None and total_max_v is not None:
                total_f = float(total_v)
                total_max_f = float(total_max_v)
                if total_max_f > 0:
                    match_inicial_gauge_pct = round(min(100.0, (total_f / total_max_f) * 100.0), 1)
                elif total_f >= 0:
                    match_inicial_gauge_pct = round(min(100.0, total_f), 1)
            elif total_v is not None:
                match_inicial_gauge_pct = round(min(100.0, float(total_v)), 1)
        except (TypeError, ValueError):
            match_inicial_gauge_pct = None
        if match_inicial_gauge_pct is not None:
            match_inicial_gauge_pct_int = int(round(match_inicial_gauge_pct))

    match_inicial_gauge_color = None
    match_inicial_gauge_nivel = None
    if match_inicial_gauge_pct_int is not None:
        if match_inicial_gauge_pct_int >= 80:
            match_inicial_gauge_color = '#28a745'
            match_inicial_gauge_nivel = 'ALTO NIVEL DE AFINIDAD'
        elif match_inicial_gauge_pct_int >= 60:
            match_inicial_gauge_color = '#ffc107'
            match_inicial_gauge_nivel = 'MEDIO NIVEL DE AFINIDAD'
        elif match_inicial_gauge_pct_int >= 40:
            match_inicial_gauge_color = '#fd7e14'
            match_inicial_gauge_nivel = 'BAJO NIVEL DE AFINIDAD'
        else:
            match_inicial_gauge_color = '#dc3545'
            match_inicial_gauge_nivel = 'MUY BAJO NIVEL DE AFINIDAD'

    # Obtener historial de cambios de estado
    registro_reclutamiento = asignacion_vacante.registro_reclutamiento
    historial_estados = []
    if registro_reclutamiento:
        try:
            if isinstance(registro_reclutamiento, str):
                historial_estados = json.loads(registro_reclutamiento)
            else:
                historial_estados = registro_reclutamiento
            if not isinstance(historial_estados, list):
                historial_estados = []
        except (json.JSONDecodeError, TypeError):
            historial_estados = []
    
    # Obtener respuestas de la aplicación
    preguntas_reclutamiento_raw = asignacion_vacante.preguntas_reclutamiento
    preguntas_reclutamiento = {}
    if preguntas_reclutamiento_raw:
        try:
            if isinstance(preguntas_reclutamiento_raw, str):
                preguntas_reclutamiento = json.loads(preguntas_reclutamiento_raw)
            else:
                preguntas_reclutamiento = preguntas_reclutamiento_raw
            if not isinstance(preguntas_reclutamiento, dict):
                preguntas_reclutamiento = {}
        except (json.JSONDecodeError, TypeError):
            preguntas_reclutamiento = {}
    
    # Obtener las preguntas originales de la vacante para mostrar el contexto
    preguntas_vacante = get_vacanty_questions(vacante.id)
    
    # Obtener candidatos anterior y siguiente con el mismo estado de reclutamiento, ordenados por fecha de aplicación
    estado_actual = asignacion_vacante.estado_reclutamiento
    candidato_anterior = None
    candidato_siguiente = None
    
    # Obtener todos los candidatos con el mismo estado de reclutamiento y la misma vacante, ordenados por fecha de aplicación
    candidatos_mismo_estado = Cli056AplicacionVacante.objects.filter(
        vacante_id_052=vacante,
        estado_reclutamiento=estado_actual
    ).order_by('fecha_aplicacion', 'id')  # Ordenar por fecha, y si hay empate, por ID
    
    # Obtener el candidato anterior (fecha anterior o misma fecha con ID menor)
    fecha_actual = asignacion_vacante.fecha_aplicacion
    if fecha_actual:
        candidato_anterior_qs = candidatos_mismo_estado.filter(
            Q(fecha_aplicacion__lt=fecha_actual) | 
            (Q(fecha_aplicacion=fecha_actual) & Q(id__lt=asignacion_vacante.id))
        ).order_by('-fecha_aplicacion', '-id')
        if candidato_anterior_qs.exists():
            candidato_anterior = candidato_anterior_qs.first()
        
        # Obtener el candidato siguiente (fecha posterior o misma fecha con ID mayor)
        candidato_siguiente_qs = candidatos_mismo_estado.filter(
            Q(fecha_aplicacion__gt=fecha_actual) | 
            (Q(fecha_aplicacion=fecha_actual) & Q(id__gt=asignacion_vacante.id))
        ).order_by('fecha_aplicacion', 'id')
        if candidato_siguiente_qs.exists():
            candidato_siguiente = candidato_siguiente_qs.first()
    else:
        # Si no hay fecha de aplicación, ordenar solo por ID
        candidato_anterior_qs = candidatos_mismo_estado.filter(id__lt=asignacion_vacante.id).order_by('-id')
        if candidato_anterior_qs.exists():
            candidato_anterior = candidato_anterior_qs.first()
        
        candidato_siguiente_qs = candidatos_mismo_estado.filter(id__gt=asignacion_vacante.id).order_by('id')
        if candidato_siguiente_qs.exists():
            candidato_siguiente = candidato_siguiente_qs.first()
    
    # Inicializar formulario
    form = ActualizarEstadoReclutadoForm(estado_actual=asignacion_vacante.estado_reclutamiento)
    
    if request.method == 'POST':
        form = ActualizarEstadoReclutadoForm(request.POST, estado_actual=asignacion_vacante.estado_reclutamiento)
        if form.is_valid():
            nuevo_estado = int(form.cleaned_data['estado_reclutamiento'])
            comentario = form.cleaned_data['comentario']
            estado_anterior_nombre, estado_nuevo_nombre = aplicar_cambio_estado_reclutado(
                request, asignacion_vacante, nuevo_estado, comentario
            )
            messages.success(request, f'Estado actualizado de {estado_anterior_nombre} a {estado_nuevo_nombre} exitosamente.')
            return redirect('reclutados:reclutados_detalle_reclutador', pk=pk)
        else:
            messages.error(request, 'Error al actualizar el estado. Verifique los datos.')
    
    context = {
        'candidato': candidato,
        'reclutado': asignacion_vacante,
        'vacante': vacante,
        'info_detalle_candidato': info_detalle_candidato,
        'json_match_inicial': json_match_inicial,
        'match_inicial_gauge_pct': match_inicial_gauge_pct,
        'match_inicial_gauge_pct_int': match_inicial_gauge_pct_int,
        'match_inicial_gauge_color': match_inicial_gauge_color,
        'match_inicial_gauge_nivel': match_inicial_gauge_nivel,
        'form': form,
        'historial_estados': historial_estados,
        'preguntas_reclutamiento': preguntas_reclutamiento,
        'preguntas_vacante': preguntas_vacante,
        'candidato_anterior': candidato_anterior,
        'candidato_siguiente': candidato_siguiente,
        'otras_aplicaciones_mismo_cliente': otras_aplicaciones_mismo_cliente,
        'cliente_asignado_otros_procesos': cliente_asignado_otros_procesos,
    }
    
    return render(request, 'admin/recruiter/client_recruiter/detail_recruited.html', context)

@login_required
@xframe_options_exempt
@validar_permisos('acceso_reclutador', 'acceso_admin', 'acceso_cliente', 'acceso_analista_seleccion_ats', 'acceso_analista_seleccion')
def detail_recruited_embed(request, pk):
    """
    Versión embebible del detalle de reclutado para mostrarse en modal (iframe).
    """
    return detail_recruited(request, pk)

@login_required
@validar_permisos('acceso_reclutador', 'acceso_admin', 'acceso_cliente', 'acceso_analista_seleccion_ats', 'acceso_analista_seleccion')
def detail_recruited_profile_modal(request, pk):
    """
    Renderiza solo el bloque de Perfil Candidato para mostrarse en modal.
    """
    asignacion_vacante = get_object_or_404(Cli056AplicacionVacante, id=pk)

    if request.session.get('grupo_id') not in (3, 5, 6):
        if asignacion_vacante.vacante_id_052.asignacion_reclutador != request.user:
            messages.error(request, 'No tiene permisos para acceder a este candidato.')
            return redirect('reclutados:vacantes_asignadas_reclutador')

    candidato = get_object_or_404(Can101Candidato, id=asignacion_vacante.candidato_101.id)
    info_detalle_candidato = buscar_candidato(candidato.id)
    context = {
        "candidato": candidato,
        "info_detalle_candidato": info_detalle_candidato,
    }
    return render(request, "admin/recruiter/client_recruiter/partials/profile_candidate_modal_content.html", context)


def _nombre_candidato_aplicacion_para_msg(aplicacion):
    """Cli056AplicacionVacante no tiene candidato_nombre (solo existe en consultas anotadas)."""
    try:
        cand = getattr(aplicacion, 'candidato_101', None)
        if cand:
            return cand.nombre_completo()
    except Exception:
        pass
    return f'aplicación #{aplicacion.pk}'


def _post_crear_entrevistas_reclutador(request, pk, vacante_id, redirect_name):
    """
    POST compartido: crea entrevistas para ids en aplicaciones_ids (separados por coma).
    También acepta aplicacion_id (un solo id) por compatibilidad con el modal único.
    """
    vacante = get_object_or_404(
        Cli052Vacante.objects.prefetch_related('habilidades'),
        id=vacante_id,
        asignacion_reclutador=request.user,
        estado_id_001=1,
    )

    cliente_id = None
    cliente = None
    if vacante.asignacion_cliente_id_064 and vacante.asignacion_cliente_id_064.id_cliente_asignado:
        cliente_id = vacante.asignacion_cliente_id_064.id_cliente_asignado.id
        cliente = vacante.asignacion_cliente_id_064.id_cliente_asignado

    aplicaciones_ids_str = (
        request.POST.get('aplicaciones_ids')
        or request.POST.get('aplicacion_id')
        or ''
    ).strip()
    if not aplicaciones_ids_str:
        messages.error(request, 'No se seleccionaron candidatos.')
        return redirect(redirect_name, pk=pk, vacante_id=vacante_id)

    aplicaciones_ids = []
    for part in aplicaciones_ids_str.replace(';', ',').split(','):
        p = part.strip()
        if p.isdigit():
            aplicaciones_ids.append(int(p))
    aplicaciones_ids = list(dict.fromkeys(aplicaciones_ids))

    if not aplicaciones_ids:
        messages.error(request, 'No se seleccionaron candidatos válidos.')
        return redirect(redirect_name, pk=pk, vacante_id=vacante_id)

    aplicaciones = Cli056AplicacionVacante.objects.filter(
        id__in=aplicaciones_ids,
        vacante_id_052=vacante,
    ).select_related('candidato_101')

    if aplicaciones.count() != len(aplicaciones_ids):
        messages.error(request, 'Algunos candidatos seleccionados no pertenecen a esta vacante.')
        return redirect(redirect_name, pk=pk, vacante_id=vacante_id)

    uid_hist = getattr(request.user, 'pk', None) or request.session.get('_auth_user_id')
    try:
        uid_hist = int(uid_hist) if uid_hist is not None else None
    except (TypeError, ValueError):
        uid_hist = None
    if uid_hist is None:
        messages.error(request, 'No se pudo identificar su usuario para registrar el historial.')
        return redirect(redirect_name, pk=pk, vacante_id=vacante_id)

    grupo_id = request.session.get('grupo_id', 2)
    form = EntrevistaCrearForm(request.POST, grupo_id=grupo_id, cliente_id=cliente_id, vacante=vacante)

    if form.is_valid():
        fecha_entrevista = form.cleaned_data['fecha_entrevista']
        hora_entrevista = form.cleaned_data['hora_entrevista']
        entrevistador_id = form.cleaned_data['entrevistador']
        tipo_entrevista = form.cleaned_data['tipo_entrevista']
        lugar_enlace = form.cleaned_data['lugar_enlace']

        try:
            entrevistador_id = int(entrevistador_id)
        except (TypeError, ValueError):
            messages.error(request, 'Entrevistador no válido.')
            return redirect(redirect_name, pk=pk, vacante_id=vacante_id)

        usuario_asignado = get_object_or_404(UsuarioBase, id=entrevistador_id)
        usuario_asigno = request.user
        estado_default = Cat001Estado.objects.get(id=1)

        url_actual = f'{request.scheme}://{request.get_host()}'

        entrevistas_creadas = []
        errores = []

        for aplicacion in aplicaciones:
            try:
                with transaction.atomic():
                    asignacion_entrevista = Cli057AsignacionEntrevista.objects.create(
                        asignacion_vacante=aplicacion,
                        usuario_asigno=usuario_asigno,
                        usuario_asignado=usuario_asignado,
                        fecha_entrevista=fecha_entrevista,
                        hora_entrevista=hora_entrevista,
                        tipo_entrevista=tipo_entrevista,
                        lugar_enlace=lugar_enlace,
                        estado_asignacion=1,
                        estado=estado_default,
                    )
                    crear_historial_aplicacion(
                        aplicacion,
                        2,
                        uid_hist,
                        'Entrevista Asignada',
                    )

                entrevistas_creadas.append(asignacion_entrevista)

                usuario_generador = request.user if request.user.is_authenticated else None
                token_documento = generar_token_documento(aplicacion, usuario_generador)

                candidato = aplicacion.candidato_101

                contexto_email = {
                    'entrevistador': f'{usuario_asignado.primer_nombre} {usuario_asignado.segundo_nombre} {usuario_asignado.primer_apellido}',
                    'nombre_candidato': candidato.nombre_completo(),
                    'fecha_entrevista': fecha_entrevista,
                    'hora_entrevista': hora_entrevista,
                    'lugar_enlace': lugar_enlace,
                    'vacante': vacante.titulo,
                    'cliente': cliente.razon_social if cliente else 'N/A',
                    'url': url_actual,
                    'token_documento': token_documento,
                    'email_candidato': candidato.email,
                }

                lista_correos = [
                    usuario_asignado.email,
                    candidato.email,
                ]

                try:
                    enviar_correo(
                        'asignacion_entrevista_entrevista',
                        contexto_email,
                        f'Asignación de Entrevista ID: {asignacion_entrevista.id}',
                        lista_correos,
                        correo_remitente=None,
                    )
                except Exception as e:
                    errores.append(f'Correo no enviado (ID entrevista {asignacion_entrevista.id}): {e}')

            except Exception as e:
                errores.append(
                    f'Error al crear entrevista para {_nombre_candidato_aplicacion_para_msg(aplicacion)}: {str(e)}'
                )

        if entrevistas_creadas:
            messages.success(
                request,
                f'Se han asignado {len(entrevistas_creadas)} entrevista(s) correctamente.',
            )

        if errores:
            for error in errores:
                messages.warning(request, error)

        return redirect(redirect_name, pk=pk, vacante_id=vacante_id)

    errores_form = []
    for campo, msgs in form.errors.items():
        for m in msgs:
            errores_form.append(f'{campo}: {m}')
    if errores_form:
        messages.error(request, 'Revise los datos de la entrevista: ' + ' | '.join(errores_form))
    else:
        messages.error(request, 'Error en el formulario. Verifique los datos.')
    return redirect(redirect_name, pk=pk, vacante_id=vacante_id)


@login_required
@validar_permisos('acceso_reclutador', 'acceso_admin')
def crear_entrevistas_multiples(request, pk, vacante_id):
    """Varios candidatos desde gestión de vacante (modal selección múltiple)."""
    if request.method != 'POST':
        return redirect('reclutados:vacantes_gestion_reclutador', pk=pk, vacante_id=vacante_id)
    return _post_crear_entrevistas_reclutador(
        request,
        pk,
        vacante_id,
        'reclutados:vacantes_gestion_reclutador',
    )


@login_required
@validar_permisos('acceso_reclutador', 'acceso_admin')
def crear_entrevista_unica_reclutador(request, pk, vacante_id):
    """Un solo candidato desde la lista de aspirantes (vacancies_assigned_recruiter_detail2)."""
    if request.method != 'POST':
        return redirect('reclutados:vacantes_gestion_reclutador_detail2', pk=pk, vacante_id=vacante_id)
    return _post_crear_entrevistas_reclutador(
        request,
        pk,
        vacante_id,
        'reclutados:vacantes_gestion_reclutador_detail2',
    )
