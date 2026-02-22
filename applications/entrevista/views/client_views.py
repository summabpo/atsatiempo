from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, Count, Q, Value, Case, When, CharField
from applications.cliente.models import Cli051Cliente, Cli064AsignacionCliente


from applications.common.views.EnvioCorreo import enviar_correo
from applications.services.service_interview import query_interview_all
from applications.vacante.forms.EntrevistaForm import EntrevistaCrearForm, EntrevistaGestionForm
from applications.vacante.models import Cli052Vacante, Cli055ProfesionEstudio, Cli053SoftSkill, Cli054HardSkill, Cli052VacanteHardSkillsId054, Cli052VacanteSoftSkillsId053, Cli072FuncionesResponsabilidades, Cli073PerfilVacante, Cli068Cargo, Cli074AsignacionFunciones
from applications.reclutado.models import Cli056AplicacionVacante
from applications.entrevista.models import Cli057AsignacionEntrevista
from applications.usuarios.models import Permiso, UsuarioBase
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.candidato.models import Can101Candidato
from django.contrib import messages
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required
from applications.usuarios.decorators  import validar_permisos
from django.db.models.functions import Concat
from django.utils.timezone import now

#forms
from applications.vacante.forms.VacanteForms import VacancyFormAll

#query
from applications.services.service_recruited import query_recruited_vacancy_id
from components.RegistrarHistorialVacante import crear_historial_aplicacion


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
        form = EntrevistaGestionForm(request.POST, habilidades=habilidades_vacante, fit_cultural=fit_cultural_vacante, motivadores=motivadores_vacante)
        if form.is_valid():
            observacion = form.cleaned_data['observacion']
            estado_asignacion = int(form.cleaned_data['estado_asignacion'])

            # Construir el JSON con los resultados de la entrevista
            resultado_json = {
                'id_usuario': request.user.id,
                'fecha_entrevista': asignacion_entrevista.fecha_entrevista.strftime('%Y-%m-%d') if asignacion_entrevista.fecha_entrevista else None,
                '4. ANÁLISIS 360° DE ENCAJE PERSONAL Y PROFESIONAL': {
                    'calificacion': int(form.cleaned_data['encaje_360_calificacion']),
                    'observacion': form.cleaned_data['encaje_360_observaciones']
                },
                '5. INDICE DE CONFIABILIDAD Y RIESGO': {
                    'calificacion': int(form.cleaned_data['confiabilidad_riesgo_calificacion']),
                    'observacion': ''
                }
            }
            # 6. HABILIDADES DE LA VACANTE (calificación 1-10 + observaciones por habilidad)
            habilidades_result = {}
            for h in habilidades_vacante:
                field_cal = f'habilidad_{h.id}'
                field_obs = f'habilidad_{h.id}_observacion'
                if field_cal in form.cleaned_data and form.cleaned_data[field_cal]:
                    habilidades_result[str(h.id)] = {
                        'nombre': h.nombre,
                        'calificacion': int(form.cleaned_data[field_cal]),
                        'observacion': form.cleaned_data.get(field_obs, '') or '',
                    }
            resultado_json['6. HABILIDADES VACANTE'] = habilidades_result

            # 2. FIT CULTURAL (calificación + observaciones por ítem de la vacante)
            fit_cultural_result = {}
            for fc in fit_cultural_vacante:
                field_cal = f'fit_cultural_{fc.id}'
                field_obs = f'fit_cultural_{fc.id}_observacion'
                if field_cal in form.cleaned_data and form.cleaned_data[field_cal]:
                    fit_cultural_result[str(fc.id)] = {
                        'nombre': fc.nombre,
                        'calificacion': int(form.cleaned_data[field_cal]),
                        'observacion': form.cleaned_data.get(field_obs, '') or '',
                    }
            resultado_json['2. FIT CULTURAL'] = fit_cultural_result

            # 3. MOTIVADORES (calificación + observaciones por ítem de la vacante)
            motivadores_result = {}
            for m in motivadores_vacante:
                field_cal = f'motivador_{m.id}'
                field_obs = f'motivador_{m.id}_observacion'
                if field_cal in form.cleaned_data and form.cleaned_data[field_cal]:
                    motivadores_result[str(m.id)] = {
                        'nombre': m.nombre,
                        'calificacion': int(form.cleaned_data[field_cal]),
                        'observacion': form.cleaned_data.get(field_obs, '') or '',
                    }
            resultado_json['3. MOTIVADORES'] = motivadores_result

            estado_vacante = None
            observacion_historial = None

            #validación estados.
            if estado_asignacion == 2:
                estado_vacante = 8 # Se cambia estado de la vacante a seleccionado
                observacion_historial = 'Se aprueba el candidato, siguen en proceso.'
                crear_historial_aplicacion(asignacion_vacante, 8, request.session.get('_auth_user_id'), 'Seleccionado por el cliente.')
            if estado_asignacion == 3:
                estado_vacante = 12  # No Apto Entrevista No Aprobada
                observacion_historial = 'Candidato No Apto en Entrevista'
                #crea el historial y actualiza el estado de la aplicacion de la vacante
                crear_historial_aplicacion(asignacion_vacante, 4, request.session.get('_auth_user_id'), 'No aprobo la entrevista el candidato')
            # if estado_asignacion == 4:
            #     estado_vacante = 8 # Se cambia estado de la vacante a seleccionado
            #     observacion_historial = 'Se selecciona candidato.'
            # if estado_asignacion == 5:
            #     estado_vacante = 10 # Se cambia estado de la vacante a cancelado
            #     observacion_historial = 'Se cancela la postulación del candidato.'

            #crea el historial y actualiza el estado de la aplicacion de la vacante
            # crear_historial_aplicacion(asignacion_vacante, estado_vacante, request.session.get('_auth_user_id'), observacion_historial)

            #actualizacion de gestión de entrevista
            asignacion_entrevista.observacion = observacion
            asignacion_entrevista.estado_asignacion = estado_asignacion
            asignacion_entrevista.fecha_gestion = now()
            asignacion_entrevista.resultado_entrevista = resultado_json
            asignacion_entrevista.save()

            messages.success(request, 'Se ha actualizado la entrevista.')

            return redirect('reclutados:reclutados_detalle_cliente', pk=asignacion_vacante.id)
        else:
            messages.error(request, form.errors)
    else:
        # Formulario Entrevista
        entrevista = get_object_or_404(Cli057AsignacionEntrevista, pk=pk)
        
        # Si existe resultado JSON, cargar los datos en el formulario
        initial_data = {}
        if entrevista.resultado_entrevista:
            resultado = entrevista.resultado_entrevista
            initial_data = {
                'encaje_360_observaciones': resultado.get('4. ANÁLISIS 360° DE ENCAJE PERSONAL Y PROFESIONAL', {}).get('observacion', ''),
                'encaje_360_calificacion': str(resultado.get('4. ANÁLISIS 360° DE ENCAJE PERSONAL Y PROFESIONAL', {}).get('calificacion', '')),
                'confiabilidad_riesgo_calificacion': str(resultado.get('5. INDICE DE CONFIABILIDAD Y RIESGO', {}).get('calificacion', '')),
            }
            # Cargar calificaciones y observaciones de habilidades guardadas
            habilidades_guardadas = resultado.get('6. HABILIDADES VACANTE', {})
            for skill_id, data in habilidades_guardadas.items():
                if isinstance(data, dict):
                    if 'calificacion' in data:
                        initial_data[f'habilidad_{skill_id}'] = str(data['calificacion'])
                    initial_data[f'habilidad_{skill_id}_observacion'] = data.get('observacion', '') or ''
                elif isinstance(data, (int, float)):
                    initial_data[f'habilidad_{skill_id}'] = str(int(data))
            # Cargar fit cultural guardado
            fit_cultural_guardado = resultado.get('2. FIT CULTURAL', {})
            for fc_id, data in fit_cultural_guardado.items():
                if isinstance(data, dict):
                    if 'calificacion' in data:
                        initial_data[f'fit_cultural_{fc_id}'] = str(data['calificacion'])
                    initial_data[f'fit_cultural_{fc_id}_observacion'] = data.get('observacion', '') or ''
                elif isinstance(data, (int, float)):
                    initial_data[f'fit_cultural_{fc_id}'] = str(int(data))
            # Cargar motivadores guardados
            motivadores_guardado = resultado.get('3. MOTIVADORES', {})
            for m_id, data in motivadores_guardado.items():
                if isinstance(data, dict):
                    if 'calificacion' in data:
                        initial_data[f'motivador_{m_id}'] = str(data['calificacion'])
                    initial_data[f'motivador_{m_id}_observacion'] = data.get('observacion', '') or ''
                elif isinstance(data, (int, float)):
                    initial_data[f'motivador_{m_id}'] = str(int(data))
        
        # Cargar también los campos existentes
        if entrevista.observacion:
            initial_data['observacion'] = entrevista.observacion
        if entrevista.estado_asignacion:
            initial_data['estado_asignacion'] = str(entrevista.estado_asignacion)
        
        form = EntrevistaGestionForm(initial=initial_data, habilidades=habilidades_vacante, fit_cultural=fit_cultural_vacante, motivadores=motivadores_vacante)

    # Verificar si existe resultado JSON
    tiene_resultado = asignacion_entrevista.resultado_entrevista is not None and bool(asignacion_entrevista.resultado_entrevista)
    
    # Preparar datos del resultado para el template
    resultado_data = None
    if tiene_resultado:
        resultado_json = asignacion_entrevista.resultado_entrevista
        resultado_data = {
            'fecha_entrevista': resultado_json.get('fecha_entrevista'),
            'id_usuario': resultado_json.get('id_usuario'),
            'fit_cultural': resultado_json.get('2. FIT CULTURAL', {}),
            'motivadores': resultado_json.get('3. MOTIVADORES', {}),
            'encaje_360': resultado_json.get('4. ANÁLISIS 360° DE ENCAJE PERSONAL Y PROFESIONAL', {}),
            'confiabilidad': resultado_json.get('5. INDICE DE CONFIABILIDAD Y RIESGO', {}),
            'habilidades': resultado_json.get('6. HABILIDADES VACANTE', {}),
        }
    
    context = {
        'vacante': vacante,
        'candidato': info_candidato,
        'reclutado': asignacion_vacante,
        'form': form,
        'entrevista': asignacion_entrevista,
        'resultado_json': asignacion_entrevista.resultado_entrevista if asignacion_entrevista.resultado_entrevista else None,
        'resultado_data': resultado_data,
        'tiene_resultado': tiene_resultado,
        'habilidades_vacante': habilidades_vacante,
        'fit_cultural_vacante': fit_cultural_vacante,
        'motivadores_vacante': motivadores_vacante,
    }

    return render(request, 'admin/interview/client_user/interview_management.html', context)

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