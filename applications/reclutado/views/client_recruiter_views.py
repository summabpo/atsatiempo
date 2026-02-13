from django.contrib.auth.views import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, Count, Q, Value, Case, When, CharField
from django.contrib import messages
from django.utils import timezone
from datetime import date, timedelta
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
from applications.services.service_interview import query_interview_all
from applications.services.service_recruited import query_recruited_vacancy_id
from applications.services.service_client import query_client_detail
from applications.services.service_candidate import buscar_candidato
from applications.services.choices import ESTADO_RECLUTADO_CHOICES_STATIC
from applications.common.views.EnvioCorreo import enviar_correo
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
    
    # Obtener el JSON match
    json_match_raw = asignacion_vacante.json_match
    if json_match_raw:
        try:
            if isinstance(json_match_raw, str):
                json_match = json.loads(json_match_raw)
            else:
                json_match = json_match_raw
        except (json.JSONDecodeError, TypeError):
            json_match = {}
    else:
        json_match = {}
    
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
            
            # Obtener nombres de estados
            estado_anterior_nombre = dict(ESTADO_RECLUTADO_CHOICES_STATIC).get(asignacion_vacante.estado_reclutamiento, 'Desconocido')
            estado_nuevo_nombre = dict(ESTADO_RECLUTADO_CHOICES_STATIC).get(nuevo_estado, 'Desconocido')
            
            # Crear el registro del cambio de estado según el formato especificado
            nuevo_registro = {
                "fecha_hora_actualizacion": timezone.now().isoformat(),
                "id_usuario_registro": request.user.id,
                "comentario": comentario,
                "estado_anterior": {
                    "codigo": asignacion_vacante.estado_reclutamiento,
                    "nombre": estado_anterior_nombre
                },
                "estado_nuevo": {
                    "codigo": nuevo_estado,
                    "nombre": estado_nuevo_nombre
                }
            }
            
            # Agregar el nuevo registro al historial
            historial_estados.append(nuevo_registro)
            
            # Actualizar el estado y el registro de reclutamiento
            asignacion_vacante.estado_reclutamiento = nuevo_estado
            asignacion_vacante.registro_reclutamiento = historial_estados
            asignacion_vacante.save()
            
            messages.success(request, f'Estado actualizado de "{estado_anterior_nombre}" a "{estado_nuevo_nombre}" exitosamente.')
            return redirect('reclutados:reclutados_detalle_reclutador', pk=pk)
        else:
            messages.error(request, 'Error al actualizar el estado. Verifique los datos.')
    
    context = {
        'candidato': candidato,
        'reclutado': asignacion_vacante,
        'vacante': vacante,
        'info_detalle_candidato': info_detalle_candidato,
        'json_match': json_match,
        'json_match_inicial': json_match_inicial,
        'form': form,
        'historial_estados': historial_estados,
        'preguntas_reclutamiento': preguntas_reclutamiento,
        'preguntas_vacante': preguntas_vacante,
        'candidato_anterior': candidato_anterior,
        'candidato_siguiente': candidato_siguiente,
    }
    
    return render(request, 'admin/recruiter/client_recruiter/detail_recruited.html', context)


@login_required
@validar_permisos('acceso_reclutador', 'acceso_admin')
def crear_entrevistas_multiples(request, pk, vacante_id):
    """
    Vista para crear múltiples entrevistas a la vez para varios candidatos seleccionados
    """
    # Verificar que la vacante esté asignada al reclutador actual
    vacante = get_object_or_404(
        Cli052Vacante.objects.prefetch_related('habilidades'),
        id=vacante_id,
        asignacion_reclutador=request.user,
        estado_id_001=1
    )
    
    # Obtener el cliente asignado
    cliente_id = None
    cliente = None
    if vacante.asignacion_cliente_id_064 and vacante.asignacion_cliente_id_064.id_cliente_asignado:
        cliente_id = vacante.asignacion_cliente_id_064.id_cliente_asignado.id
        cliente = vacante.asignacion_cliente_id_064.id_cliente_asignado
    
    if request.method == 'POST':
        # Obtener IDs de aplicaciones desde el formulario
        aplicaciones_ids_str = request.POST.get('aplicaciones_ids', '')
        if not aplicaciones_ids_str:
            messages.error(request, 'No se seleccionaron candidatos.')
            return redirect('reclutados:vacantes_gestion_reclutador', pk=pk, vacante_id=vacante_id)
        
        aplicaciones_ids = [int(id.strip()) for id in aplicaciones_ids_str.split(',') if id.strip().isdigit()]
        
        if not aplicaciones_ids:
            messages.error(request, 'No se seleccionaron candidatos válidos.')
            return redirect('reclutados:vacantes_gestion_reclutador', pk=pk, vacante_id=vacante_id)
        
        # Validar que todas las aplicaciones pertenezcan a la vacante
        aplicaciones = Cli056AplicacionVacante.objects.filter(
            id__in=aplicaciones_ids,
            vacante_id_052=vacante
        )
        
        if aplicaciones.count() != len(aplicaciones_ids):
            messages.error(request, 'Algunos candidatos seleccionados no pertenecen a esta vacante.')
            return redirect('reclutados:vacantes_gestion_reclutador', pk=pk, vacante_id=vacante_id)
        
        # Procesar formulario de entrevista
        grupo_id = request.session.get('grupo_id', 2)
        form = EntrevistaCrearForm(request.POST, grupo_id=grupo_id, cliente_id=cliente_id, vacante=vacante)
        
        if form.is_valid():
            fecha_entrevista = form.cleaned_data['fecha_entrevista']
            hora_entrevista = form.cleaned_data['hora_entrevista']
            entrevistador_id = form.cleaned_data['entrevistador']
            tipo_entrevista = form.cleaned_data['tipo_entrevista']
            lugar_enlace = form.cleaned_data['lugar_enlace']
            
            usuario_asignado = get_object_or_404(UsuarioBase, id=entrevistador_id)
            usuario_asigno = request.user
            estado_default = Cat001Estado.objects.get(id=1)
            
            url_actual = f"{request.scheme}://{request.get_host()}"
            
            # Crear entrevista para cada aplicación
            entrevistas_creadas = []
            errores = []
            
            for aplicacion in aplicaciones:
                try:
                    # Crear la asignación de entrevista
                    asignacion_entrevista = Cli057AsignacionEntrevista.objects.create(
                        asignacion_vacante=aplicacion,
                        usuario_asigno=usuario_asigno,
                        usuario_asignado=usuario_asignado,
                        fecha_entrevista=fecha_entrevista,
                        hora_entrevista=hora_entrevista,
                        tipo_entrevista=tipo_entrevista,
                        lugar_enlace=lugar_enlace,
                        estado_asignacion=1,  # Pendiente por defecto
                        estado=estado_default,
                    )
                    
                    entrevistas_creadas.append(asignacion_entrevista)
                    
                    # Crear historial
                    crear_historial_aplicacion(
                        aplicacion, 
                        2, 
                        request.session.get('_auth_user_id'), 
                        'Entrevista Asignada'
                    )
                    
                    # Obtener información del candidato
                    candidato = aplicacion.candidato_101
                    
                    # Preparar contexto para el correo
                    contexto_email = {
                        'entrevistador': f'{usuario_asignado.primer_nombre} {usuario_asignado.segundo_nombre} {usuario_asignado.primer_apellido}',
                        'nombre_candidato': candidato.nombre_completo(),
                        'fecha_entrevista': fecha_entrevista,
                        'hora_entrevista': hora_entrevista,
                        'lugar_enlace': lugar_enlace,
                        'vacante': vacante.titulo,
                        'cliente': cliente.razon_social if cliente else 'N/A',
                        'url': url_actual
                    }
                    
                    # Lista de correos
                    lista_correos = [
                        usuario_asignado.email,
                        candidato.email
                    ]
                    
                    # Enviar correo
                    try:
                        enviar_correo(
                            'asignacion_entrevista_entrevista', 
                            contexto_email, 
                            f'Asignación de Entrevista ID: {asignacion_entrevista.id}', 
                            lista_correos, 
                            correo_remitente=None
                        )
                    except Exception as e:
                        # No fallar si el correo no se puede enviar
                        print(f"Error al enviar correo: {e}")
                    
                except Exception as e:
                    errores.append(f"Error al crear entrevista para {aplicacion.candidato_nombre}: {str(e)}")
            
            # Mensajes de resultado
            if entrevistas_creadas:
                messages.success(
                    request, 
                    f'Se han asignado {len(entrevistas_creadas)} entrevista(s) correctamente.'
                )
            
            if errores:
                for error in errores:
                    messages.warning(request, error)
            
            return redirect('reclutados:vacantes_gestion_reclutador', pk=pk, vacante_id=vacante_id)
        else:
            messages.error(request, 'Error en el formulario. Verifique los datos.')
            return redirect('reclutados:vacantes_gestion_reclutador', pk=pk, vacante_id=vacante_id)
    
    # Si es GET, redirigir
    return redirect('reclutados:vacantes_gestion_reclutador', pk=pk, vacante_id=vacante_id)
