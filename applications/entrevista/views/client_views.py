from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, Count, Q, Value, Case, When, CharField
from applications.cliente.models import Cli051Cliente, Cli064AsignacionCliente


from applications.common.views.EnvioCorreo import enviar_correo
from applications.services.service_interview import query_interview_all
from applications.vacante.forms.EntrevistaForm import EntrevistaCrearForm, EntrevistaGestionForm, EntrevistaFinalizarForm
from applications.vacante.models import Cli052Vacante, Cli055ProfesionEstudio, Cli053SoftSkill, Cli054HardSkill, Cli052VacanteHardSkillsId054, Cli052VacanteSoftSkillsId053, Cli072FuncionesResponsabilidades, Cli073PerfilVacante, Cli068Cargo, Cli074AsignacionFunciones
from applications.reclutado.models import Cli056AplicacionVacante, Cli079RequisitosCargado, Cli082PruebaCargada, Cli083ConfiabilidadRiesgoCargado
from applications.entrevista.models import Cli057AsignacionEntrevista
from applications.usuarios.models import Permiso, UsuarioBase
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.candidato.models import Can101Candidato
from django.contrib import messages
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from applications.usuarios.decorators  import validar_permisos
from django.db.models.functions import Concat
from django.utils.timezone import now

#forms
from applications.vacante.forms.VacanteForms import VacancyFormAll

#query
from applications.services.service_recruited import query_recruited_vacancy_id
from components.RegistrarHistorialVacante import crear_historial_aplicacion
from applications.vacante.views.common_view import get_requisitos


def _id_usuario_resultado_entrevista(request, asignacion_vacante):
    if request.user.is_authenticated and getattr(request.user, 'id', None):
        return request.user.id
    usuario_candidato = asignacion_vacante.candidato_101.usuario.first()
    return usuario_candidato.id if usuario_candidato else request.session.get('user_id')


def _merge_base_resultado_keys(resultado, asignacion_entrevista, asignacion_vacante, request):
    if not isinstance(resultado, dict):
        resultado = {}
    resultado = dict(resultado)
    resultado.setdefault('id_usuario', _id_usuario_resultado_entrevista(request, asignacion_vacante))
    fe = asignacion_entrevista.fecha_entrevista
    resultado.setdefault('fecha_entrevista', fe.strftime('%Y-%m-%d') if fe else None)
    return resultado


def _observacion_guardada(val):
    """Texto de observación presente y no solo espacios."""
    if val is None:
        return False
    return str(val).strip() != ''


def _resultado_evaluacion_completo(resultado, habilidades_vacante, fit_cultural_vacante, motivadores_vacante):
    if not resultado:
        return False
    for h in habilidades_vacante:
        sec = resultado.get('6. HABILIDADES VACANTE') or {}
        ent = sec.get(str(h.id))
        if (
            not isinstance(ent, dict)
            or ent.get('calificacion') in (None, '')
            or not _observacion_guardada(ent.get('observacion'))
        ):
            return False
    for fc in fit_cultural_vacante:
        sec = resultado.get('2. FIT CULTURAL') or {}
        ent = sec.get(str(fc.id))
        if (
            not isinstance(ent, dict)
            or ent.get('calificacion') in (None, '')
            or not _observacion_guardada(ent.get('observacion'))
        ):
            return False
    for m in motivadores_vacante:
        sec = resultado.get('3. MOTIVADORES') or {}
        ent = sec.get(str(m.id))
        if (
            not isinstance(ent, dict)
            or ent.get('calificacion') in (None, '')
            or not _observacion_guardada(ent.get('observacion'))
        ):
            return False
    pruebas = resultado.get('4. PRUEBAS (Resultados y análisis psicotécnicos)', resultado.get('4. PRUEBAS', {}))
    if (
        not isinstance(pruebas, dict)
        or pruebas.get('calificacion') in (None, '')
        or not _observacion_guardada(pruebas.get('observacion'))
    ):
        return False
    conf = (
        resultado.get('5. INDICE Y CONFIABILIDAD DEL RIESGO')
        or resultado.get('6. INDICE DE CONFIABILIDAD Y RIESGO')
        or resultado.get('5. INDICE DE CONFIABILIDAD Y RIESGO')
        or {}
    )
    if (
        not isinstance(conf, dict)
        or conf.get('calificacion') in (None, '')
        or not _observacion_guardada(conf.get('observacion'))
    ):
        return False
    return True


def _promedio_seccion_resultado(resultado, key):
    if not resultado or not isinstance(resultado, dict):
        return None
    sec = resultado.get(key) or {}
    if not isinstance(sec, dict):
        return None
    vals = []
    for x in sec.values():
        if isinstance(x, dict) and x.get('calificacion') not in (None, ''):
            try:
                vals.append(int(x['calificacion']))
            except (TypeError, ValueError):
                pass
    if not vals:
        return None
    return round(sum(vals) / len(vals), 1)


def _calif_guardada_item(resultado, key, item_id):
    sec = (resultado or {}).get(key) or {}
    if not isinstance(sec, dict):
        return None
    entry = sec.get(str(item_id))
    if not isinstance(entry, dict) or entry.get('calificacion') in (None, ''):
        return None
    try:
        return int(entry['calificacion'])
    except (TypeError, ValueError):
        return None


def _build_resultado_data_dict(resultado_json):
    if not resultado_json:
        return None
    pruebas_json = resultado_json.get('4. PRUEBAS (Resultados y análisis psicotécnicos)', resultado_json.get('4. PRUEBAS', {}))
    prueba_cargada_obj = None
    if isinstance(pruebas_json, dict) and pruebas_json.get('prueba_cargada_id'):
        prueba_cargada_obj = Cli082PruebaCargada.objects.filter(id=pruebas_json['prueba_cargada_id']).first()
    confiabilidad = (
        resultado_json.get('5. INDICE Y CONFIABILIDAD DEL RIESGO')
        or resultado_json.get('6. INDICE DE CONFIABILIDAD Y RIESGO')
        or resultado_json.get('5. INDICE DE CONFIABILIDAD Y RIESGO')
        or {}
    )
    confiabilidad_cargada_obj = None
    if isinstance(confiabilidad, dict) and confiabilidad.get('confiabilidad_cargada_id'):
        confiabilidad_cargada_obj = Cli083ConfiabilidadRiesgoCargado.objects.filter(id=confiabilidad['confiabilidad_cargada_id']).first()
    return {
        'fecha_entrevista': resultado_json.get('fecha_entrevista'),
        'id_usuario': resultado_json.get('id_usuario'),
        'fit_cultural': resultado_json.get('2. FIT CULTURAL', {}),
        'motivadores': resultado_json.get('3. MOTIVADORES', {}),
        'pruebas': pruebas_json if isinstance(pruebas_json, dict) else {},
        'prueba_cargada_obj': prueba_cargada_obj,
        'confiabilidad': confiabilidad if isinstance(confiabilidad, dict) else {},
        'confiabilidad_cargada_obj': confiabilidad_cargada_obj,
        'habilidades': resultado_json.get('6. HABILIDADES VACANTE', {}),
    }


#detalle de la vacante
@login_required
@validar_permisos('acceso_admin', 'acceso_cliente', 'acceso_cliente_entrevistador', 'acceso_analista_seleccion')
def management_interview(request, pk):
    # Verificar si el cliente_id está en la sesión
    cliente_id = request.session.get('cliente_id')

    #obtener asignación de la entrevista
    asignacion_entrevista = get_object_or_404(Cli057AsignacionEntrevista, id=pk)
    

    # verificar información de asignación de la vacante
    asignacion_vacante = get_object_or_404(Cli056AplicacionVacante, id=asignacion_entrevista.asignacion_vacante.id)

    #obtener información del candidato
    info_candidato = get_object_or_404(Can101Candidato, id=asignacion_entrevista.asignacion_vacante.candidato_101.id)
    
    # Obtener información de la vacante (habilidades, fit_cultural y motivadores para el formulario)
    vacante = get_object_or_404(
        Cli052Vacante.objects.prefetch_related('habilidades', 'fit_cultural', 'motivadores'),
        id=asignacion_entrevista.asignacion_vacante.vacante_id_052.id
    )
    habilidades_vacante = list(vacante.habilidades.all())
    fit_cultural_vacante = list(vacante.fit_cultural.all())
    motivadores_vacante = list(vacante.motivadores.all())

    if request.method == 'POST':
        form_final = EntrevistaFinalizarForm(request.POST)
        if form_final.is_valid():
            asignacion_entrevista.refresh_from_db()
            if asignacion_entrevista.estado_asignacion != 1:
                messages.error(request, 'Esta entrevista ya fue gestionada.')
                return redirect('reclutados:reclutados_detalle_cliente', pk=asignacion_vacante.id)
            rj = asignacion_entrevista.resultado_entrevista or {}
            if not _resultado_evaluacion_completo(rj, habilidades_vacante, fit_cultural_vacante, motivadores_vacante):
                messages.error(
                    request,
                    'Debe completar y guardar todas las secciones de la evaluación (botones en verde) antes de finalizar.',
                )
            else:
                observacion = form_final.cleaned_data['observacion']
                estado_asignacion = int(form_final.cleaned_data['estado_asignacion'])
                if estado_asignacion == 2:
                    crear_historial_aplicacion(
                        asignacion_vacante, 3, request.session.get('_auth_user_id'), 'Seleccionado por el cliente.'
                    )
                if estado_asignacion == 3:
                    crear_historial_aplicacion(
                        asignacion_vacante, 4, request.session.get('_auth_user_id'), 'No aprobo la entrevista el candidato'
                    )
                asignacion_entrevista.observacion = observacion
                asignacion_entrevista.estado_asignacion = estado_asignacion
                asignacion_entrevista.fecha_gestion = now()
                asignacion_entrevista.save()
                messages.success(request, 'Se ha actualizado la entrevista.')
                return redirect('reclutados:reclutados_detalle_cliente', pk=asignacion_vacante.id)
        else:
            messages.error(request, form_final.errors)

    entrevista = get_object_or_404(Cli057AsignacionEntrevista, pk=pk)
    initial_data = {}
    if entrevista.resultado_entrevista:
        resultado = entrevista.resultado_entrevista
        conf = (
            resultado.get('5. INDICE Y CONFIABILIDAD DEL RIESGO')
            or resultado.get('6. INDICE DE CONFIABILIDAD Y RIESGO')
            or resultado.get('5. INDICE DE CONFIABILIDAD Y RIESGO')
            or {}
        )
        initial_data = {
            'confiabilidad_riesgo_calificacion': str(conf.get('calificacion', '')),
            'confiabilidad_riesgo_observaciones': conf.get('observacion', '') or '',
        }
        pruebas_data = resultado.get('4. PRUEBAS (Resultados y análisis psicotécnicos)', resultado.get('4. PRUEBAS', {}))
        if isinstance(pruebas_data, dict):
            initial_data['prueba_calificacion'] = str(pruebas_data.get('calificacion', ''))
            initial_data['prueba_observaciones'] = pruebas_data.get('observacion', '') or ''
        habilidades_guardadas = resultado.get('6. HABILIDADES VACANTE', {})
        for skill_id, data in habilidades_guardadas.items():
            if isinstance(data, dict):
                if 'calificacion' in data:
                    initial_data[f'habilidad_{skill_id}'] = str(data['calificacion'])
                initial_data[f'habilidad_{skill_id}_observacion'] = data.get('observacion', '') or ''
            elif isinstance(data, (int, float)):
                initial_data[f'habilidad_{skill_id}'] = str(int(data))
        fit_cultural_guardado = resultado.get('2. FIT CULTURAL', {})
        for fc_id, data in fit_cultural_guardado.items():
            if isinstance(data, dict):
                if 'calificacion' in data:
                    initial_data[f'fit_cultural_{fc_id}'] = str(data['calificacion'])
                initial_data[f'fit_cultural_{fc_id}_observacion'] = data.get('observacion', '') or ''
            elif isinstance(data, (int, float)):
                initial_data[f'fit_cultural_{fc_id}'] = str(int(data))
        motivadores_guardado = resultado.get('3. MOTIVADORES', {})
        for m_id, data in motivadores_guardado.items():
            if isinstance(data, dict):
                if 'calificacion' in data:
                    initial_data[f'motivador_{m_id}'] = str(data['calificacion'])
                initial_data[f'motivador_{m_id}_observacion'] = data.get('observacion', '') or ''
            elif isinstance(data, (int, float)):
                initial_data[f'motivador_{m_id}'] = str(int(data))

    form = EntrevistaGestionForm(
        initial=initial_data, habilidades=habilidades_vacante, fit_cultural=fit_cultural_vacante, motivadores=motivadores_vacante
    )

    if request.method != 'POST':
        initial_final = {}
        if entrevista.observacion:
            initial_final['observacion'] = entrevista.observacion
        if entrevista.estado_asignacion in (2, 3):
            initial_final['estado_asignacion'] = str(entrevista.estado_asignacion)
        form_final = EntrevistaFinalizarForm(initial=initial_final)

    asignacion_entrevista = entrevista
    tiene_resultado = asignacion_entrevista.resultado_entrevista is not None and bool(asignacion_entrevista.resultado_entrevista)
    resultado_data = None
    if tiene_resultado:
        resultado_data = _build_resultado_data_dict(asignacion_entrevista.resultado_entrevista)

    puede_editar_secciones = asignacion_entrevista.estado_asignacion == 1
    rjson = asignacion_entrevista.resultado_entrevista or {}
    secciones_total = (
        len(habilidades_vacante) + len(fit_cultural_vacante) + len(motivadores_vacante) + 2
    )
    secciones_ok = 0
    for h in habilidades_vacante:
        sec = rjson.get('6. HABILIDADES VACANTE') or {}
        ent = sec.get(str(h.id))
        if (
            isinstance(ent, dict)
            and ent.get('calificacion') not in (None, '')
            and _observacion_guardada(ent.get('observacion'))
        ):
            secciones_ok += 1
    for fc in fit_cultural_vacante:
        sec = rjson.get('2. FIT CULTURAL') or {}
        ent = sec.get(str(fc.id))
        if (
            isinstance(ent, dict)
            and ent.get('calificacion') not in (None, '')
            and _observacion_guardada(ent.get('observacion'))
        ):
            secciones_ok += 1
    for m in motivadores_vacante:
        sec = rjson.get('3. MOTIVADORES') or {}
        ent = sec.get(str(m.id))
        if (
            isinstance(ent, dict)
            and ent.get('calificacion') not in (None, '')
            and _observacion_guardada(ent.get('observacion'))
        ):
            secciones_ok += 1
    pruebas_chk = rjson.get('4. PRUEBAS (Resultados y análisis psicotécnicos)', rjson.get('4. PRUEBAS', {}))
    if (
        isinstance(pruebas_chk, dict)
        and pruebas_chk.get('calificacion') not in (None, '')
        and _observacion_guardada(pruebas_chk.get('observacion'))
    ):
        secciones_ok += 1
    conf_chk = (
        rjson.get('5. INDICE Y CONFIABILIDAD DEL RIESGO')
        or rjson.get('6. INDICE DE CONFIABILIDAD Y RIESGO')
        or rjson.get('5. INDICE DE CONFIABILIDAD Y RIESGO')
        or {}
    )
    if (
        isinstance(conf_chk, dict)
        and conf_chk.get('calificacion') not in (None, '')
        and _observacion_guardada(conf_chk.get('observacion'))
    ):
        secciones_ok += 1

    habilidades_modal_fields = []
    for h in habilidades_vacante:
        habilidades_modal_fields.append(
            {
                'h': h,
                'modal_id': f'modalHabilidad{h.id}',
                'cal': form[f'habilidad_{h.id}'],
                'obs': form[f'habilidad_{h.id}_observacion'],
                'calif_int': _calif_guardada_item(rjson, '6. HABILIDADES VACANTE', h.id),
            }
        )
    fit_modal_fields = []
    for fc in fit_cultural_vacante:
        fit_modal_fields.append(
            {
                'fc': fc,
                'modal_id': f'modalFit{fc.id}',
                'cal': form[f'fit_cultural_{fc.id}'],
                'obs': form[f'fit_cultural_{fc.id}_observacion'],
                'calif_int': _calif_guardada_item(rjson, '2. FIT CULTURAL', fc.id),
            }
        )
    motivadores_modal_fields = []
    for m in motivadores_vacante:
        motivadores_modal_fields.append(
            {
                'm': m,
                'modal_id': f'modalMotivador{m.id}',
                'cal': form[f'motivador_{m.id}'],
                'obs': form[f'motivador_{m.id}_observacion'],
                'calif_int': _calif_guardada_item(rjson, '3. MOTIVADORES', m.id),
            }
        )

    promedio_habilidades_ent = _promedio_seccion_resultado(rjson, '6. HABILIDADES VACANTE')
    promedio_fit_ent = _promedio_seccion_resultado(rjson, '2. FIT CULTURAL')
    promedio_motivadores_ent = _promedio_seccion_resultado(rjson, '3. MOTIVADORES')
    prueba_calif_ent = None
    if isinstance(pruebas_chk, dict) and pruebas_chk.get('calificacion') not in (None, ''):
        try:
            prueba_calif_ent = int(pruebas_chk['calificacion'])
        except (TypeError, ValueError):
            prueba_calif_ent = None
    conf_calif_ent = None
    if isinstance(conf_chk, dict) and conf_chk.get('calificacion') not in (None, ''):
        try:
            conf_calif_ent = int(conf_chk['calificacion'])
        except (TypeError, ValueError):
            conf_calif_ent = None
    
    # Requisitos del cargo y cuáles tiene cargados esta aplicación
    requisitos_cargo = get_requisitos(asignacion_vacante)
    requisitos_cargados_qs = Cli079RequisitosCargado.objects.filter(
        aplicacion_vacante_056=asignacion_vacante
    ).select_related('asignacion_requisito_070__requisito', 'usuario_cargado')
    requisitos_cargados_dict = {r.asignacion_requisito_070.id: r for r in requisitos_cargados_qs}
    requisitos_con_info = [
        {'requisito': req, 'cargado': requisitos_cargados_dict.get(req.id)}
        for req in requisitos_cargo
    ]

    # Documento de política de datos firmada (si existe)
    documento_politica_firmada = asignacion_vacante.documentos_firmar.filter(
        documento_firmado__isnull=False
    ).exclude(documento_firmado='').first()

    context = {
        'vacante': vacante,
        'candidato': info_candidato,
        'reclutado': asignacion_vacante,
        'form': form,
        'form_final': form_final,
        'entrevista': asignacion_entrevista,
        'resultado_json': asignacion_entrevista.resultado_entrevista if asignacion_entrevista.resultado_entrevista else None,
        'resultado_data': resultado_data,
        'tiene_resultado': tiene_resultado,
        'puede_editar_secciones': puede_editar_secciones,
        'secciones_total': secciones_total,
        'secciones_ok': secciones_ok,
        'habilidades_modal_fields': habilidades_modal_fields,
        'fit_modal_fields': fit_modal_fields,
        'motivadores_modal_fields': motivadores_modal_fields,
        'promedio_habilidades_ent': promedio_habilidades_ent,
        'promedio_fit_ent': promedio_fit_ent,
        'promedio_motivadores_ent': promedio_motivadores_ent,
        'prueba_calif_ent': prueba_calif_ent,
        'conf_calif_ent': conf_calif_ent,
        'habilidades_vacante': habilidades_vacante,
        'fit_cultural_vacante': fit_cultural_vacante,
        'motivadores_vacante': motivadores_vacante,
        'requisitos_con_info': requisitos_con_info,
        'documento_politica_firmada': documento_politica_firmada,
    }

    return render(request, 'admin/interview/client_user/interview_management.html', context)


@login_required
@validar_permisos('acceso_admin', 'acceso_cliente', 'acceso_cliente_entrevistador', 'acceso_analista_seleccion')
@require_POST
def save_interview_section(request, pk):
    asignacion_entrevista = get_object_or_404(Cli057AsignacionEntrevista, id=pk)
    if asignacion_entrevista.estado_asignacion != 1:
        return JsonResponse({'ok': False, 'error': 'La entrevista no admite edición.'}, status=400)

    asignacion_vacante = get_object_or_404(Cli056AplicacionVacante, id=asignacion_entrevista.asignacion_vacante.id)
    vacante = get_object_or_404(
        Cli052Vacante.objects.prefetch_related('habilidades', 'fit_cultural', 'motivadores'),
        id=asignacion_entrevista.asignacion_vacante.vacante_id_052.id,
    )
    habilidades_vacante = list(vacante.habilidades.all())
    fit_cultural_vacante = list(vacante.fit_cultural.all())
    motivadores_vacante = list(vacante.motivadores.all())

    section = request.POST.get('section')
    resultado = _merge_base_resultado_keys(
        asignacion_entrevista.resultado_entrevista or {},
        asignacion_entrevista,
        asignacion_vacante,
        request,
    )
    pruebas_key = '4. PRUEBAS (Resultados y análisis psicotécnicos)'
    conf_key = '5. INDICE Y CONFIABILIDAD DEL RIESGO'

    try:
        if section == 'habilidad':
            item_id = int(request.POST.get('item_id', ''))
            h = next((x for x in habilidades_vacante if x.id == item_id), None)
            if not h:
                return JsonResponse({'ok': False, 'error': 'Habilidad no válida.'}, status=400)
            cal = request.POST.get(f'habilidad_{item_id}')
            obs = request.POST.get(f'habilidad_{item_id}_observacion', '') or ''
            if not cal:
                return JsonResponse({'ok': False, 'error': 'La calificación es obligatoria.'}, status=400)
            if not _observacion_guardada(obs):
                return JsonResponse({'ok': False, 'error': 'Las observaciones son obligatorias.'}, status=400)
            resultado.setdefault('6. HABILIDADES VACANTE', {})
            resultado['6. HABILIDADES VACANTE'][str(item_id)] = {
                'nombre': h.nombre,
                'calificacion': int(cal),
                'observacion': obs,
            }
        elif section == 'fit_cultural':
            item_id = int(request.POST.get('item_id', ''))
            fc = next((x for x in fit_cultural_vacante if x.id == item_id), None)
            if not fc:
                return JsonResponse({'ok': False, 'error': 'Ítem de fit cultural no válido.'}, status=400)
            cal = request.POST.get(f'fit_cultural_{item_id}')
            obs = request.POST.get(f'fit_cultural_{item_id}_observacion', '') or ''
            if not cal:
                return JsonResponse({'ok': False, 'error': 'La calificación es obligatoria.'}, status=400)
            if not _observacion_guardada(obs):
                return JsonResponse({'ok': False, 'error': 'Las observaciones son obligatorias.'}, status=400)
            resultado.setdefault('2. FIT CULTURAL', {})
            resultado['2. FIT CULTURAL'][str(item_id)] = {
                'nombre': fc.nombre,
                'calificacion': int(cal),
                'observacion': obs,
            }
        elif section == 'motivador':
            item_id = int(request.POST.get('item_id', ''))
            m = next((x for x in motivadores_vacante if x.id == item_id), None)
            if not m:
                return JsonResponse({'ok': False, 'error': 'Motivador no válido.'}, status=400)
            cal = request.POST.get(f'motivador_{item_id}')
            obs = request.POST.get(f'motivador_{item_id}_observacion', '') or ''
            if not cal:
                return JsonResponse({'ok': False, 'error': 'La calificación es obligatoria.'}, status=400)
            if not _observacion_guardada(obs):
                return JsonResponse({'ok': False, 'error': 'Las observaciones son obligatorias.'}, status=400)
            resultado.setdefault('3. MOTIVADORES', {})
            resultado['3. MOTIVADORES'][str(item_id)] = {
                'nombre': m.nombre,
                'calificacion': int(cal),
                'observacion': obs,
            }
        elif section == 'pruebas':
            cal = request.POST.get('prueba_calificacion')
            obs = request.POST.get('prueba_observaciones', '') or ''
            if not cal:
                return JsonResponse({'ok': False, 'error': 'La calificación es obligatoria.'}, status=400)
            if not _observacion_guardada(obs):
                return JsonResponse({'ok': False, 'error': 'Las observaciones son obligatorias.'}, status=400)
            prev = resultado.get(pruebas_key) or resultado.get('4. PRUEBAS') or {}
            prueba_cargada_id = prev.get('prueba_cargada_id') if isinstance(prev, dict) else None
            if request.FILES.get('prueba_cargada'):
                estado_activo = get_object_or_404(Cat001Estado, id=1)
                obj_prueba = Cli082PruebaCargada.objects.create(
                    aplicacion_vacante_056=asignacion_vacante,
                    prueba_cargada=request.FILES['prueba_cargada'],
                    usuario_cargada=request.user,
                    estado=estado_activo,
                )
                prueba_cargada_id = obj_prueba.id
            resultado[pruebas_key] = {
                'calificacion': int(cal),
                'observacion': obs,
                'prueba_cargada_id': prueba_cargada_id,
            }
        elif section == 'confiabilidad':
            cal = request.POST.get('confiabilidad_riesgo_calificacion')
            obs = request.POST.get('confiabilidad_riesgo_observaciones', '') or ''
            if not cal:
                return JsonResponse({'ok': False, 'error': 'La calificación es obligatoria.'}, status=400)
            if not _observacion_guardada(obs):
                return JsonResponse({'ok': False, 'error': 'Las observaciones son obligatorias.'}, status=400)
            prev = resultado.get(conf_key) or {}
            confiabilidad_cargada_id = prev.get('confiabilidad_cargada_id') if isinstance(prev, dict) else None
            if request.FILES.get('confiabilidad_riesgo_cargado'):
                estado_activo = get_object_or_404(Cat001Estado, id=1)
                obj_conf = Cli083ConfiabilidadRiesgoCargado.objects.create(
                    aplicacion_vacante_056=asignacion_vacante,
                    documento_cargado=request.FILES['confiabilidad_riesgo_cargado'],
                    usuario_cargado=request.user,
                    estado=estado_activo,
                )
                confiabilidad_cargada_id = obj_conf.id
            resultado[conf_key] = {
                'calificacion': int(cal),
                'observacion': obs,
                'confiabilidad_cargada_id': confiabilidad_cargada_id,
            }
        else:
            return JsonResponse({'ok': False, 'error': 'Sección no válida.'}, status=400)
    except (ValueError, TypeError) as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)

    asignacion_entrevista.resultado_entrevista = resultado
    asignacion_entrevista.save()
    return JsonResponse({'ok': True, 'message': 'Guardado.'})


#listado entrevistas por vacante
@login_required
@validar_permisos('acceso_cliente')
def interview_list(request):
    # Verificar si el cliente_id está en la sesión
    cliente_id = request.session.get('cliente_id')

    # Obtener información de las entrevistas por vacante
    entrevistas = query_interview_all()
    entrevistas = entrevistas.filter(asignacion_vacante__vacante_id_052__asignacion_cliente_id_064__id_cliente_asignado=cliente_id)

    context = {
        'entrevistas': entrevistas,
    }

    return render(request, 'admin/interview/client_user/interview_list.html', context)