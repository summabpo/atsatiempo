from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, Count, Q, Value, Case, When, CharField
from applications.cliente.models import Cli051Cliente, Cli064AsignacionCliente


from applications.common.views.EnvioCorreo import enviar_correo, generar_token_documento
from applications.reclutado.forms.FormRecruited import ReclutadoCrearForm, RespuestaClienteForm
from applications.services.service_candidate import buscar_candidato
from applications.vacante.forms.EntrevistaForm import EntrevistaCrearForm
from applications.vacante.models import Cli052Vacante, Cli055ProfesionEstudio, Cli053SoftSkill, Cli054HardSkill, Cli052VacanteHardSkillsId054, Cli052VacanteSoftSkillsId053, Cli072FuncionesResponsabilidades, Cli073PerfilVacante, Cli068Cargo, Cli074AsignacionFunciones
from applications.reclutado.models import Cli056AplicacionVacante
from applications.entrevista.models import Cli057AsignacionEntrevista
from applications.usuarios.models import Permiso, UsuarioBase
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.candidato.models import Can101Candidato
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
import json
from django.contrib.auth.decorators import login_required
from applications.usuarios.decorators  import validar_permisos
from django.db.models.functions import Concat

#forms
from applications.vacante.forms.VacanteForms import VacancyFormAll

#query
from applications.services.service_vacanty import  query_vacanty_detail
from applications.services.service_recruited import consultar_historial_aplicacion_vacante, query_recruited_vacancy_id
from components.RegistrarHistorialVacante import crear_historial_aplicacion
from applications.reclutado.views.admin_views import _procesar_datos_reporte_final
from applications.reclutado.views.candidato_hoja_vida_pdf import build_hoja_vida_pdf, safe_filename_part


def _puede_descargar_hoja_vida_pdf(request, asignacion_vacante):
    """Misma lógica de acceso que el detalle del reclutado (cliente, admin, internos, reclutador)."""
    if getattr(request.user, 'is_superuser', False):
        return True
    grupo_id = request.session.get('grupo_id')
    vacante = asignacion_vacante.vacante_id_052
    id_cliente_vacante = vacante.asignacion_cliente_id_064.id_cliente_asignado.id
    if grupo_id == 1:
        return True
    if grupo_id in (3, 5, 6):
        return True
    if request.session.get('cliente_id') == id_cliente_vacante:
        return True
    reclutador = getattr(vacante, 'asignacion_reclutador_id', None)
    if reclutador and reclutador == request.user.id:
        return True
    return False


@login_required
@validar_permisos(
    'acceso_admin',
    'acceso_cliente',
    'acceso_analista_seleccion_ats',
    'acceso_analista_seleccion',
    'acceso_cliente_entrevistador',
    'acceso_reclutador',
)
def descargar_hoja_vida_pdf(request, pk):
    """
    Descarga la hoja de vida del candidato en PDF (datos del sistema).
    pk: id de Cli056AplicacionVacante.
    """
    asignacion_vacante = get_object_or_404(Cli056AplicacionVacante, id=pk)
    if not _puede_descargar_hoja_vida_pdf(request, asignacion_vacante):
        return HttpResponseForbidden('No tiene permisos para descargar esta hoja de vida.')

    candidato = get_object_or_404(Can101Candidato, id=asignacion_vacante.candidato_101_id)
    info_detalle = buscar_candidato(candidato.id)
    vacante = query_vacanty_detail().get(id=asignacion_vacante.vacante_id_052_id)
    titulo_vacante = getattr(vacante, 'titulo', None)

    pdf_buffer = build_hoja_vida_pdf(request, candidato, info_detalle, vacante_titulo=titulo_vacante)
    nombre_archivo = f"Hoja_de_vida_{safe_filename_part(candidato.nombre_completo())}.pdf"
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    # inline: el navegador muestra el PDF (útil al abrir en nueva pestaña)
    response['Content-Disposition'] = f'inline; filename="{nombre_archivo}"'
    return response

#detalle de la vacante
@login_required
@validar_permisos('acceso_admin', 'acceso_cliente', 'acceso_analista_seleccion')
def detail_vacancy_recruited(request, pk):
    form_errors = False
    # Verificar si el cliente_id está en la sesión
    cliente_id = request.session.get('cliente_id')
    
    # Obtener información de la vacante
    vacante = query_vacanty_detail().get(id=pk)

    # Obtener los reclutados asociados a la vacante
    reclutados = query_recruited_vacancy_id(vacante.id)

    # formulario para asignar candidato a la vacante
    form = ReclutadoCrearForm()
    if request.method == 'POST':
        form = ReclutadoCrearForm(request.POST)
        if form.is_valid():
            numero_documento = form.cleaned_data['numero_documento']
            primer_nombre = form.cleaned_data['primer_nombre']
            segundo_nombre = form.cleaned_data['segundo_nombre']
            primer_apellido = form.cleaned_data['primer_apellido']
            segundo_apellido = form.cleaned_data['segundo_apellido']
            telefono = form.cleaned_data['telefono']
            email = form.cleaned_data['email']

            #registro del candidato
            candidato, created = Can101Candidato.objects.get_or_create(
                numero_documento=numero_documento,
                defaults={
                    'primer_nombre': primer_nombre,
                    'segundo_nombre': segundo_nombre,
                    'primer_apellido': primer_apellido,
                    'segundo_apellido': segundo_apellido,
                    'telefono': telefono,
                    'email': email,
                    'estado_id_001': Cat001Estado.objects.get(id=1),  # Asumiendo que 1 es el estado por defecto
                }
            )

            if created:
                messages.success(request, 'Candidato creado exitosamente.')
            else:
                messages.info(request, 'Candidato ya existe. Se actualizarán los datos.')
                # Actualizar los datos del candidato si ya existe
                candidato.primer_nombre = primer_nombre
                candidato.segundo_nombre = segundo_nombre
                candidato.primer_apellido = primer_apellido
                candidato.segundo_apellido = segundo_apellido
                candidato.telefono = telefono
                candidato.email = email
                candidato.save()

            # Validar que el candidato no esté ya registrado en la vacante
            if Cli056AplicacionVacante.objects.filter(candidato_101=candidato, vacante_id_052=vacante).exists():
                messages.error(request, 'El candidato ya está registrado en esta vacante.')
                return redirect('reclutados:vacantes_reclutados_cliente', pk=pk)

            #registro de la aplicacion de la vacante
            aplicacion_vacante = Cli056AplicacionVacante.objects.create(
                vacante_id_052=vacante,
                candidato_101=candidato,
                estado=Cat001Estado.objects.get(id=1),  # Asumiendo que 1 es el estado por defecto
            )

            crear_historial_aplicacion(aplicacion_vacante, 1, request.session.get('_auth_user_id'), 'Aplicación a Vacante por el cliente')

            messages.success(request, 'Candidato asignado en la vacante exitosamente.')
            return redirect('reclutados:vacantes_reclutados_cliente', pk=pk)    
        else:
            form_errors = True
            messages.error(request, 'Error al crear el candidato. Verifique los datos.')

    else:
        form = ReclutadoCrearForm()

    context ={
        'vacante': vacante,
        'reclutados': reclutados,
        'form': form,
        'form_errors' : form_errors,
    }

    return render(request, 'admin/vacancy/client_user/vacancy_detail_recruited.html', context)

#detalle de la vacante
@login_required
@validar_permisos('acceso_admin', 'acceso_cliente', 'acceso_analista_seleccion_ats', 'acceso_analista_seleccion', 'acceso_cliente_entrevistador')
def detail_recruited(request, pk):
    url_actual = f"{request.scheme}://{request.get_host()}"

    validar_registro = False

    usuario_id = request.session.get('_auth_user_id')


    
    # verificar información de asignación de la vacante
    # asignacion_vacante = get_object_or_404(Cli056AplicacionVacante, id=pk)
    asignacion_vacante = get_object_or_404(Cli056AplicacionVacante, id=pk)
    # Obtener el json_match y parsearlo
    json_match_raw = asignacion_vacante.json_match
    
    # Parsear el JSON string a diccionario Python
    if json_match_raw:
        try:
            json_match = json.loads(json_match_raw)
        except (json.JSONDecodeError, TypeError):
            json_match = {}
    else:
        json_match = {}

    #obtener información del candidato
    info_candidato = get_object_or_404(Can101Candidato, id=asignacion_vacante.candidato_101.id)
    info_detalle_candidato = buscar_candidato(asignacion_vacante.candidato_101.id)

    #obtener información del historico de la vacante:
    historico_vacante = consultar_historial_aplicacion_vacante(asignacion_vacante.id)
    # obtener los datos de las entrevistas
    entrevista = Cli057AsignacionEntrevista.objects.filter(asignacion_vacante=asignacion_vacante.id).order_by('-fecha_entrevista')
    

    # Verificar si el cliente_id está en la sesión
    if request.session['grupo_id'] == 1:  # Si es admin
        cliente_id = asignacion_vacante.vacante_id_052.asignacion_cliente_id_064.id_cliente_asignado.id
        print(cliente_id)
        cliente = get_object_or_404(Cli051Cliente, id=cliente_id)
    elif request.session['grupo_id'] == 3 or request.session['grupo_id'] == 5 or request.session['grupo_id'] == 6:  # Si es analista_interno
        cliente_id = asignacion_vacante.vacante_id_052.asignacion_cliente_id_064.id_cliente_asignado.id
        cliente = get_object_or_404(Cli051Cliente, id=cliente_id)
    else:  # Si es cliente directo
        cliente_id = request.session.get('cliente_id')
        cliente = get_object_or_404(Cli051Cliente, id=cliente_id)
    
    # Obtener información de la vacante
    vacante = query_vacanty_detail().get(id=asignacion_vacante.vacante_id_052.id)
    
    # Obtener el grupo_id de la sesión
    grupo_id = request.session.get('grupo_id', 4)

    # Obtener los reclutados asociados a la vacante
    reclutados = query_recruited_vacancy_id(vacante.id)

    form = EntrevistaCrearForm(request.POST, grupo_id=grupo_id, cliente_id=cliente_id, vacante=vacante)
    
    if request.method == 'POST':
        if form.is_valid():
            fecha_entrevista = form.cleaned_data['fecha_entrevista']
            hora_entrevista = form.cleaned_data['hora_entrevista']
            entrevistador = form.cleaned_data['entrevistador']
            tipo_entrevista = form.cleaned_data['tipo_entrevista']
            lugar_enlace = form.cleaned_data['lugar_enlace']
            usuario_asignado = get_object_or_404(UsuarioBase, id=entrevistador)

            # Obtener instancias de los modelos relacionados
            usuario_asigno = request.user  # Asumiendo que el usuario actual es quien asigna la entrevista
            estado_default = Cat001Estado.objects.get(id=1)  # Asumiendo que 1 es el estado por defecto

            # Crear la nueva asignación de entrevista
            asignacion_entrevista = Cli057AsignacionEntrevista.objects.create(
                asignacion_vacante=asignacion_vacante,
                usuario_asigno=usuario_asigno,
                usuario_asignado=usuario_asignado,
                fecha_entrevista=fecha_entrevista,
                hora_entrevista=hora_entrevista,
                tipo_entrevista=tipo_entrevista,
                lugar_enlace=lugar_enlace,
                estado_asignacion=1,  # Pendiente por defecto
                estado=estado_default,
            )

            #funcion para crear registro en el historial y actualizar estado de la aplicacion de la vcatente
            crear_historial_aplicacion(asignacion_vacante, 2, request.session.get('_auth_user_id'), 'Entrevista Asignada')
            
            # Generar token para el documento
            usuario_generador = request.user if request.user.is_authenticated else None
            token_documento = generar_token_documento(asignacion_vacante, usuario_generador)
            
            contexto_email_1 = {
                'entrevistador' : f'{usuario_asignado.primer_nombre} {usuario_asignado.segundo_nombre} {usuario_asignado.primer_apellido}',
                'nombre_candidato' : f'{info_candidato.primer_nombre} {info_candidato.segundo_nombre} {info_candidato.primer_apellido} {info_candidato.segundo_apellido}' ,
                'fecha_entrevista' : fecha_entrevista,
                'hora_entrevista' : hora_entrevista,
                'lugar_enlace' : lugar_enlace,
                'vacante' : vacante.titulo,
                'cliente' : cliente.razon_social,
                'url' : url_actual,
                'token_documento' : token_documento,
                'email_candidato' : info_candidato.email
            }

            lista_correos = [
                usuario_asignado.email,
                info_candidato.email
            ]

            # Envio de correo
            enviar_correo('asignacion_entrevista_entrevista', contexto_email_1, f'Asginación de Entrevista ID: {asignacion_entrevista.id}', lista_correos, correo_remitente=None)

            frase_aleatoria = 'Se ha asignado entrevista correctamente.'
            messages.success(request, frase_aleatoria)

            return redirect('reclutados:reclutados_detalle_cliente', pk=pk)
        else:
            messages.error(request, 'Error al crear la asignación')
    else:
        form = EntrevistaCrearForm(grupo_id=grupo_id, cliente_id=cliente_id, vacante=vacante)

    # Formulario de respuesta del cliente (solo para grupo_id=3 y cliente_tipo=3)
    form_respuesta_cliente = RespuestaClienteForm()
    tiene_respuesta_cliente = False
    respuesta_cliente_data = None
    
    # Verificar si ya existe una respuesta del cliente
    if asignacion_vacante.estado_aplicacion in [8, 12, 13] and asignacion_vacante.registro_reclutamiento:
        if isinstance(asignacion_vacante.registro_reclutamiento, dict):
            descripcion_respuesta = asignacion_vacante.registro_reclutamiento.get('descripcion_respuesta_cliente', '')
            if descripcion_respuesta:
                tiene_respuesta_cliente = True
                es_apto = asignacion_vacante.estado_aplicacion in (8, 13)
                respuesta_cliente_data = {
                    'estado': 'Seleccionado' if es_apto else 'No Apto',
                    'estado_codigo': asignacion_vacante.estado_aplicacion,
                    'descripcion': descripcion_respuesta,
                    'color_badge': 'success' if es_apto else 'danger'
                }
    
    if request.method == 'POST' and 'submit' in request.POST and request.POST.get('submit') == 'Guardar Respuesta':
        form_respuesta_cliente = RespuestaClienteForm(request.POST)
        if form_respuesta_cliente.is_valid():
            estado_form = int(form_respuesta_cliente.cleaned_data['estado_respuesta'])
            # Seleccionado → siempre estado de aplicación 8 (compat. 13 en datos antiguos)
            if estado_form in (8, 13):
                estado_final = 8
            elif estado_form == 12:
                estado_final = 12
            else:
                estado_final = estado_form
            descripcion = form_respuesta_cliente.cleaned_data['descripcion']
            
            # Actualizar estado_aplicacion
            asignacion_vacante.estado_aplicacion = estado_final
            
            # Obtener o inicializar registro_reclutamiento
            registro_reclutamiento = asignacion_vacante.registro_reclutamiento if asignacion_vacante.registro_reclutamiento else {}
            if not isinstance(registro_reclutamiento, dict):
                registro_reclutamiento = {}
            
            # Guardar descripción en el JSON
            registro_reclutamiento['descripcion_respuesta_cliente'] = descripcion
            
            # Guardar cambios
            asignacion_vacante.registro_reclutamiento = registro_reclutamiento
            asignacion_vacante.save()
            
            # Crear historial (mismo estado persistido en la aplicación)
            _etiq = 'Seleccionado' if estado_final == 8 else 'No Apto'
            crear_historial_aplicacion(
                asignacion_vacante, estado_final, request.session.get('_auth_user_id'),
                f'Respuesta del cliente: {_etiq}'
            )

            nombre_candidato_mail = ' '.join(
                p for p in (
                    info_candidato.primer_nombre,
                    info_candidato.segundo_nombre,
                    info_candidato.primer_apellido,
                    info_candidato.segundo_apellido,
                ) if p
            ).strip()
            nombre_candidato_saludo = (info_candidato.primer_nombre or '').strip() or (nombre_candidato_mail.split()[0] if nombre_candidato_mail else 'Candidato')
            # Nombre comercial del headhunter origen (maestro), no del cliente/headhunter asignado
            _asignacion = getattr(vacante, 'asignacion_cliente_id_064', None)
            _maestro = getattr(_asignacion, 'id_cliente_maestro', None) if _asignacion else None
            if _maestro and (_maestro.razon_social or '').strip():
                nombre_empresa_cliente = _maestro.razon_social.strip()
            elif cliente and (cliente.razon_social or '').strip():
                nombre_empresa_cliente = cliente.razon_social.strip()
            else:
                nombre_empresa_cliente = 'Cliente'

            contexto_interno = {
                'cliente': nombre_empresa_cliente,
                'vacante': vacante.titulo,
                'id_vacante': vacante.id,
                'nombre_candidato': nombre_candidato_mail or str(info_candidato.id),
                'descripcion_respuesta': descripcion,
                'url': url_actual,
            }
            contexto_candidato = {
                'nombre_empresa_cliente': nombre_empresa_cliente,
                'nombre_candidato_saludo': nombre_candidato_saludo,
                'vacante': vacante.titulo,
                'url': url_actual,
            }

            correos_internos = []
            if getattr(vacante, 'usuario_asignado', None) and vacante.usuario_asignado.email:
                correos_internos.append(vacante.usuario_asignado.email.strip())
            if getattr(vacante, 'asignacion_reclutador', None) and vacante.asignacion_reclutador.email:
                correos_internos.append(vacante.asignacion_reclutador.email.strip())
            vistos_i = set()
            lista_internos = []
            for em in correos_internos:
                if em:
                    k = em.lower()
                    if k not in vistos_i:
                        vistos_i.add(k)
                        lista_internos.append(em)

            email_candidato = (info_candidato.email or '').strip()
            lista_candidato = [email_candidato] if email_candidato else []

            if estado_final == 8:
                if lista_internos:
                    try:
                        enviar_correo(
                            'respuesta_cliente_seleccionado_correo',
                            contexto_interno,
                            f'Respuesta del cliente — Candidato seleccionado · Vacante {vacante.id}',
                            lista_internos,
                            correo_remitente=None,
                        )
                    except Exception:
                        pass
                if lista_candidato:
                    try:
                        enviar_correo(
                            'candidato_respuesta_cliente_seleccionado_correo',
                            contexto_candidato,
                            f'{nombre_empresa_cliente} — Has sido seleccionado · {vacante.titulo}',
                            lista_candidato,
                            correo_remitente=None,
                        )
                    except Exception:
                        pass
            elif estado_final == 12:
                if lista_internos:
                    try:
                        enviar_correo(
                            'respuesta_cliente_no_seleccionado_correo',
                            contexto_interno,
                            f'Respuesta del cliente — No continúa · Vacante {vacante.id}',
                            lista_internos,
                            correo_remitente=None,
                        )
                    except Exception:
                        pass
                if lista_candidato:
                    try:
                        enviar_correo(
                            'candidato_respuesta_cliente_no_seleccionado_correo',
                            contexto_candidato,
                            f'{nombre_empresa_cliente} — Gracias por tu participación',
                            lista_candidato,
                            correo_remitente=None,
                        )
                    except Exception:
                        pass

            messages.success(request, 'Respuesta guardada exitosamente.')
            return redirect('reclutados:reclutados_detalle_cliente', pk=pk)
        else:
            messages.error(request, 'Error al guardar la respuesta. Verifique los datos.')
    else:
        # Si no hay respuesta existente, inicializar el formulario vacío
        if not tiene_respuesta_cliente:
            form_respuesta_cliente = RespuestaClienteForm()

    # Obtener datos del reporte final si el estado_aplicacion es 8 (Seleccionado) o si hay respuesta del cliente
    datos_reporte_final = None
    if asignacion_vacante.estado_aplicacion == 3 or tiene_respuesta_cliente:
        try:
            datos_reporte_final = _procesar_datos_reporte_final(request, asignacion_vacante.id)
        except Exception as e:
            # Si hay error al procesar el reporte, dejar datos_reporte_final como None
            datos_reporte_final = None

    context ={
        'form': form,
        'form_respuesta_cliente': form_respuesta_cliente,
        'tiene_respuesta_cliente': tiene_respuesta_cliente,
        'respuesta_cliente_data': respuesta_cliente_data,
        'vacante': vacante,
        'reclutados': reclutados,
        'candidato': info_candidato,
        'reclutado': asignacion_vacante,
        'entrevista': entrevista,
        'info_detalle_candidato': info_detalle_candidato,
        'historial': historico_vacante,
        'json_match': json_match,
        'datos_reporte_final': datos_reporte_final,
    }

    return render(request, 'admin/recruited/client_user/recruited_detail.html', context)