from django.shortcuts import render
from applications.cliente.models import Cli069Requisito, Cli070AsignacionRequisito, Cli071AsignacionPrueba, Cli051ClientePoliticas
from applications.common.views.EnvioCorreo import enviar_correo
from applications.services.service_candidate import personal_information_calculation
from applications.services.service_recruited import consultar_historial_aplicacion_vacante, query_recruited_vacancy_id, consultar_historial_aplicacion_vacante_candidate
from applications.vacante.forms.BuscarVacanteForm import VacanteFiltro
from applications.vacante.models import Cli052Vacante, Cli055ProfesionEstudio, Cli053SoftSkill, Cli054HardSkill, Cli052VacanteHardSkillsId054, Cli052VacanteSoftSkillsId053, Cli072FuncionesResponsabilidades, Cli073PerfilVacante, Cli068Cargo, Cli074AsignacionFunciones
from applications.reclutado.models import Cli056AplicacionVacante, Cli079RequisitosCargado, Cli080DocumentoFirmadoAplicacionVacante
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
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.contrib.staticfiles import finders
from io import BytesIO
from datetime import datetime
import os
import uuid
import string
import secrets
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from django.core.files.base import ContentFile

from applications.vacante.views.common_view import get_politicas_internas, get_pruebas, get_requisitos

def generar_codigo_unico():
    """Genera un código único alfanumérico"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(characters) for _ in range(12))

def generar_pdf_documento_firmado(aplicacion, fecha_firma=None, ip_firmante=None, codigo_unico=None):
    """Función auxiliar para generar el PDF del documento firmado"""
    if fecha_firma is None:
        fecha_firma = datetime.now()
    
    # Obtener información del candidato
    candidato = aplicacion.candidato_101
    nombre_completo = candidato.nombre_completo()
    numero_documento = candidato.numero_documento or "N/A"
    tipo_documento = "Cédula de Ciudadanía"
    ciudad_documento = candidato.ciudad_id_004.nombre if candidato.ciudad_id_004 else "N/A"
    fecha_nacimiento = candidato.fecha_nacimiento.strftime("%d/%m/%Y") if candidato.fecha_nacimiento else "N/A"
    
    # Obtener información de la vacante y cargo
    vacante = aplicacion.vacante_id_052
    cargo_postulado = vacante.cargo.nombre_cargo if vacante.cargo else "N/A"
    
    # Obtener información del cliente
    cliente = vacante.cargo.cliente if vacante.cargo and vacante.cargo.cliente else None
    nombre_empresa = cliente.razon_social if cliente else "N/A"
    
    # Ciudad de firma
    ciudad_firma = ciudad_documento
    
    # Fecha de firma
    dia_firma = fecha_firma.day
    meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    mes_firma = meses[fecha_firma.month - 1]
    anio_firma = fecha_firma.year
    hora_firma = fecha_firma.strftime("%H:%M:%S")
    fecha_firma_str = fecha_firma.strftime("%d/%m/%Y")
    
    # Información del responsable
    responsable = aplicacion.usuario_reclutador if aplicacion.usuario_reclutador else None
    nombre_responsable = responsable.get_full_name() if responsable and hasattr(responsable, 'get_full_name') and responsable.get_full_name() else (responsable.username if responsable else "N/A")
    cargo_responsable = "Responsable del Proceso de Selección"
    
    # Obtener políticas internas del cliente
    politicas_internas = []
    if cliente:
        politicas_internas = Cli051ClientePoliticas.objects.filter(
            cliente=cliente,
            estado_id=1
        ).select_related('politica_interna')
    
    # Obtener respuestas guardadas
    respuestas_guardadas = aplicacion.json_politicas_internas if aplicacion.json_politicas_internas else {}
    if not isinstance(respuestas_guardadas, dict):
        respuestas_guardadas = {}
    
    # Obtener la firma guardada
    firma_guardada = None
    try:
        documento_firmado = Cli080DocumentoFirmadoAplicacionVacante.objects.filter(
            aplicacion_vacante_056=aplicacion,
            estado_id=1
        ).first()
        if documento_firmado and documento_firmado.imagen_firmada:
            firma_guardada = documento_firmado.imagen_firmada.path
    except:
        pass
    
    # Construir texto de políticas internas con respuestas
    texto_politicas = ""
    if politicas_internas:
        for politica in politicas_internas:
            descripcion = politica.politica_interna.descripcion
            respuestas_json = politica.politica_interna.respuestas_politica
            politica_id_str = str(politica.politica_interna.id)
            respuesta_guardada = respuestas_guardadas.get(politica_id_str, {})
            
            texto_politicas += f"""
                            
                            {descripcion}"""
            
            if respuestas_json and isinstance(respuestas_json, dict):
                try:
                    if "si" in respuestas_json or "no" in respuestas_json:
                        respuesta_valor = respuesta_guardada.get('respuesta', '')
                        
                        if respuesta_valor == 'si':
                            texto_politicas += f"""
                            
                            Respuesta: SÍ"""
                            
                            if "si" in respuestas_json and isinstance(respuestas_json["si"], dict):
                                preguntas_si = respuestas_json["si"]
                                preguntas_respuestas = respuesta_guardada.get('preguntas', {})
                                
                                preguntas_ordenadas = sorted(
                                    [(k, v) for k, v in preguntas_si.items() if k.startswith("pregunta")],
                                    key=lambda x: int(x[0].replace("pregunta", "")) if x[0].replace("pregunta", "").isdigit() else 999
                                )
                                
                                for pregunta_key, pregunta_data in preguntas_ordenadas:
                                    if isinstance(pregunta_data, dict):
                                        pregunta_texto = pregunta_data.get("pregunta", "")
                                        ayuda = pregunta_data.get("ayuda", "")
                                        respuesta_pregunta = preguntas_respuestas.get(pregunta_key, "")
                                        
                                        if pregunta_texto:
                                            if ayuda:
                                                texto_politicas += f"""
                            Si la respuesta es "Sí": {pregunta_texto} ({ayuda}): {respuesta_pregunta if respuesta_pregunta else '__________'}"""
                                            else:
                                                texto_politicas += f"""
                            Si la respuesta es "Sí": {pregunta_texto}: {respuesta_pregunta if respuesta_pregunta else '__________'}"""
                        elif respuesta_valor == 'no':
                            texto_politicas += f"""
                            
                            Respuesta: NO"""
                        else:
                            texto_politicas += f"""
                            
                            Respuesta: __________"""
                    else:
                        respuesta_texto = respuesta_guardada.get('respuesta', '')
                        texto_politicas += f"""
                            
                            Respuesta: {respuesta_texto if respuesta_texto else '__________'}"""
                except Exception as e:
                    respuesta_texto = respuesta_guardada.get('respuesta', '')
                    texto_politicas += f"""
                            
                            Respuesta: {respuesta_texto if respuesta_texto else '__________'}"""
            else:
                respuesta_texto = respuesta_guardada.get('respuesta', '')
                texto_politicas += f"""
                            
                            Respuesta: {respuesta_texto if respuesta_texto else '__________'}"""
    
    # Texto del documento
    texto_documento = f"""YO, {nombre_completo}, identificado(a) con {tipo_documento} No. {numero_documento} de {ciudad_documento}, nacido(a) el {fecha_nacimiento}, aspirando al cargo {cargo_postulado}, declaro que la información suministrada en este documento es verdadera y corresponde a mi situación actual.

                            Autorizo a {nombre_empresa} para utilizar esta información en el proceso de selección y para realizar las verificaciones que considere necesarias, de acuerdo con la normatividad vigente y sus políticas internas.{texto_politicas}
                            
                            Entiendo que cualquier información falsa u omitida puede ser motivo de retiro del proceso de selección o de terminación de la relación laboral, si llegare a ser contratado(a).
                            
                            Firmo en {ciudad_firma}, a los {dia_firma} días del mes de {mes_firma} de {anio_firma}.

                            _______________________________________________________
                            Candidato: {nombre_completo}
                            {tipo_documento} {numero_documento}
                            

                            _______________________________________________________
                            Responsable del proceso
                            Nombre: {nombre_responsable}
                            Cargo: {cargo_responsable}"""
    
    # Información de firma para el pie de página
    info_firma = f"Fecha y hora de firma: {fecha_firma_str} {hora_firma}"
    if ip_firmante:
        info_firma += f" | IP: {ip_firmante}"
    if codigo_unico:
        info_firma += f" | Código único: {codigo_unico}"
    
    # Crear el buffer para el PDF
    buffer = BytesIO()
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=36, leftMargin=36,
                            topMargin=30, bottomMargin=60)  # Aumentado bottomMargin para el pie de página
    
    # Contenedor para los elementos del PDF
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Colores de la aplicación
    color_primary = colors.HexColor('#B10022')
    
    # Encabezado con logo
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'admin', 'images', 'landing', 'logo-talent-tray.png')
    
    header_data = []
    if logo_path and os.path.exists(logo_path):
        try:
            logo_img = RLImage(logo_path, width=0.8*inch, height=0.35*inch)
            header_data.append([logo_img, ''])
        except:
            header_data.append(['', ''])
    else:
        header_data.append(['', ''])
    
    header_table = Table(header_data, colWidths=[1*inch, 6.77*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (0, 0), 0),
        ('RIGHTPADDING', (0, 0), (0, 0), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 0.05*inch))
    
    # Línea divisoria
    line_table = Table([['']], colWidths=[7.77*inch], rowHeights=[0.015*inch])
    line_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), color_primary),
        ('TOPPADDING', (0, 0), (0, 0), 0),
        ('BOTTOMPADDING', (0, 0), (0, 0), 0),
    ]))
    elements.append(line_table)
    elements.append(Spacer(1, 0.1*inch))
    
    # Estilos
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=color_primary,
        spaceAfter=15,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        alignment=TA_JUSTIFY,
        spaceAfter=12,
        fontName='Helvetica'
    )
    
    signature_style = ParagraphStyle(
        'CustomSignature',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        alignment=TA_LEFT,
        spaceAfter=6,
        spaceBefore=20,
        fontName='Helvetica'
    )
    
    footer_style = ParagraphStyle(
        'CustomFooter',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#666666'),
        fontName='Helvetica'
    )
    
    # Título de sección
    title = Paragraph("POLÍTICAS INTERNAS", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.15*inch))
    
    # Cuerpo del documento
    parrafos = texto_documento.split('\n\n')
    firma_insertada = False
    for i, parrafo in enumerate(parrafos):
        if parrafo.strip():
            if parrafo.strip().startswith('________________________________') and ('Candidato:' in parrafo or (i + 1 < len(parrafos) and 'Candidato:' in parrafos[i + 1])):
                lineas = parrafo.split('\n')
                for j, linea in enumerate(lineas):
                    if linea.strip().startswith('________________________________'):
                        p = Paragraph(linea.replace('\n', '<br/>'), signature_style)
                        elements.append(p)
                        
                        if firma_guardada and os.path.exists(firma_guardada) and not firma_insertada:
                            try:
                                firma_img = RLImage(firma_guardada, width=3*inch, height=1*inch)
                                elements.append(Spacer(1, 0.1*inch))
                                elements.append(firma_img)
                                elements.append(Spacer(1, 0.1*inch))
                                firma_insertada = True
                            except Exception as e:
                                pass
                        
                        if j + 1 < len(lineas):
                            resto_parrafo = '\n'.join(lineas[j + 1:])
                            p = Paragraph(resto_parrafo.replace('\n', '<br/>'), signature_style)
                            elements.append(p)
                        break
                else:
                    p = Paragraph(parrafo.replace('\n', '<br/>'), signature_style)
                    elements.append(p)
                
                elements.append(Spacer(1, 0.15*inch))
            elif parrafo.startswith('Firma') or parrafo.startswith('Espacio para') or parrafo.startswith('Candidato:') or parrafo.startswith('Responsable'):
                p = Paragraph(parrafo.replace('\n', '<br/>'), signature_style)
                elements.append(p)
                elements.append(Spacer(1, 0.15*inch))
            elif 'Respuesta:' in parrafo and i + 1 < len(parrafos) and 'Si la respuesta es' in parrafos[i + 1]:
                p = Paragraph(parrafo.replace('\n', '<br/>'), body_style)
                elements.append(p)
                elements.append(Spacer(1, 0.05*inch))
            elif 'Si la respuesta es' in parrafo:
                p = Paragraph(parrafo.replace('\n', '<br/>'), body_style)
                elements.append(p)
                elements.append(Spacer(1, 0.05*inch))
            else:
                p = Paragraph(parrafo.replace('\n', '<br/>'), body_style)
                elements.append(p)
                elements.append(Spacer(1, 0.15*inch))
    
    # Agregar pie de página con información de firma
    elements.append(Spacer(1, 0.2*inch))
    footer = Paragraph(info_firma, footer_style)
    elements.append(footer)
    
    # Construir el PDF
    doc.build(elements)
    
    return buffer

@login_required
@validar_permisos('acceso_candidato')
def apply_vacancy(request):
    

    # Obtener el ID del candidato desde la sesión
    candidato_id = request.session.get('candidato_id')
    vacancy = Cli056AplicacionVacante.objects.filter(candidato_101=candidato_id, estado=1).order_by('-id')
    
    context = {
        'vacancy': vacancy,
    }

    return render(request, 'admin/vacancy/candidate_user/apply_vacancy.html', context)

@login_required
@validar_permisos('acceso_candidato')
def apply_vacancy_detail(request, pk):
    # Obtener el ID del candidato desde la sesión
    candidato_id = request.session.get('candidato_id')
    
    # Obtener la aplicación de vacante específica
    try:
        vacancy = Cli056AplicacionVacante.objects.get(id=pk, candidato_101=candidato_id)
        vacante = get_object_or_404(Cli052Vacante.objects.prefetch_related('habilidades'), id=vacancy.vacante_id_052.id, estado_id_001=1)
        historico_vacante = consultar_historial_aplicacion_vacante_candidate(vacancy.id)

        print(vacancy.vacante_id_052.cargo.id)

        requisito =get_requisitos(vacancy)
        pruebas = get_pruebas(vacancy)
        politicas_internas = get_politicas_internas(vacancy)
        print(politicas_internas)
        
        # Obtener los requisitos cargados en estado 1
        requisitos_cargados = Cli079RequisitosCargado.objects.filter(
            aplicacion_vacante_056=vacancy,
            estado_id=1
        ).select_related('asignacion_requisito_070', 'usuario_cargado')
        
        # Crear un diccionario para acceso rápido por asignacion_requisito_070.id
        requisitos_cargados_dict = {
            req.asignacion_requisito_070.id: req 
            for req in requisitos_cargados
        }
        
        # Agregar información de requisito cargado a cada requisito
        requisitos_con_info = []
        for req in requisito:
            requisito_info = {
                'requisito': req,
                'cargado': requisitos_cargados_dict.get(req.id)
            }
            requisitos_con_info.append(requisito_info)

    except Cli056AplicacionVacante.DoesNotExist:
        messages.error(request, "La aplicación de vacante no existe o no pertenece al candidato.")
        return redirect('vacantes:vacante_candidato_aplicadas')
        
        

    # Asegurar que json_politicas_internas sea un diccionario
    json_politicas_internas = vacancy.json_politicas_internas if vacancy.json_politicas_internas else {}
    
    # Calcular estado de políticas: finalizada si todas las políticas tienen respuestas
    politicas_finalizadas = False
    if politicas_internas and json_politicas_internas:
        politicas_con_respuesta = 0
        for politica in politicas_internas:
            politica_id = str(politica.politica_interna.id)
            if politica_id in json_politicas_internas and json_politicas_internas[politica_id].get('respuesta'):
                politicas_con_respuesta += 1
        politicas_finalizadas = politicas_con_respuesta == len(politicas_internas)

    # Obtener el documento firmado si existe
    documento_firmado = None
    try:
        documento_firmado = Cli080DocumentoFirmadoAplicacionVacante.objects.filter(
            aplicacion_vacante_056=vacancy,
            estado_id=1
        ).first()
    except:
        pass
        
    context = {
        'vacancy': vacancy,
        'vacante': vacante,
        'requisito': requisito,
        'requisitos_con_info': requisitos_con_info,
        'pruebas': pruebas,
        'politicas_internas': politicas_internas,
        'historial': historico_vacante,
        'is_candidato': True,  # Indicar que es candidato para restringir información
        'json_politicas_internas': json_politicas_internas,
        'politicas_finalizadas': politicas_finalizadas,
        'documento_firmado': documento_firmado,
    }

    return render(request, 'admin/vacancy/candidate_user/apply_vacancy_detail.html', context)

@login_required
@validar_permisos('acceso_candidato')
def vacancy_available(request):
    # Obtener el ID del candidato desde la sesión
    candidato_id = request.session.get('candidato_id')

    data = personal_information_calculation(candidato_id)

    # Filtrar las vacantes disponibles para el candidato
    vacantes_disponibles = Cli052Vacante.objects.select_related(
        'perfil_vacante', 
        'perfil_vacante__lugar_trabajo'
    ).filter(
        estado_id_001=1,
    ).exclude(
        aplicaciones__candidato_101=candidato_id
    ).order_by('-fecha_creacion')

    #
    form = VacanteFiltro(request.GET or None, request_data=request.GET)

    if form.is_valid():
        ciudad = form.cleaned_data.get('ciudad')
        experiencia_requerida = form.cleaned_data.get('experiencia_requerida')
        profesion_estudio = form.cleaned_data.get('profesion_estudio')
        palabras_clave = form.cleaned_data.get('palabras_clave')

        if ciudad:
            vacantes_disponibles = vacantes_disponibles.filter(perfil_vacante__lugar_trabajo=ciudad)

        if experiencia_requerida:
            # Convertir a entero ya que viene como string desde el formulario
            experiencia_requerida = int(experiencia_requerida)
            
            if experiencia_requerida == 6:  # Sin Experiencia
                # Para "Sin Experiencia", mostrar solo vacantes que requieran exactamente "Sin Experiencia"
                vacantes_disponibles = vacantes_disponibles.filter(perfil_vacante__tiempo_experiencia=6)
            else:
                # Para otros casos, mostrar vacantes que requieran la experiencia seleccionada o menos
                # Crear lista de valores válidos (desde 1 hasta el valor seleccionado)
                valores_experiencia = list(range(1, experiencia_requerida + 1))
                vacantes_disponibles = vacantes_disponibles.filter(perfil_vacante__tiempo_experiencia__in=valores_experiencia)

        if profesion_estudio:
            # Manejar diferentes tipos de profesiones
            if profesion_estudio.startswith('grupo_'):
                # Es un grupo de profesiones
                grupo_id = profesion_estudio.replace('grupo_', '')
                vacantes_disponibles = vacantes_disponibles.filter(perfil_vacante__grupo_profesion=grupo_id)
            else:
                # Es una profesión individual o del JSON
                from django.db.models import Q
                vacantes_disponibles = vacantes_disponibles.filter(
                    Q(perfil_vacante__profesion_estudio=profesion_estudio) |
                    Q(perfil_vacante__profesion_estudio_listado__icontains=f'"id":{profesion_estudio}')
                )

        # Filtro por palabras clave
        if palabras_clave:
            from django.db.models import Q
            # Buscar en múltiples campos relacionados
            vacantes_disponibles = vacantes_disponibles.filter(
                Q(titulo__icontains=palabras_clave) |  # Título de la vacante
                Q(descripcion_vacante__icontains=palabras_clave) |  # Descripción de la vacante
                Q(cargo__nombre_cargo__icontains=palabras_clave) |  # Nombre del cargo
                Q(perfil_vacante__profesion_estudio__nombre__icontains=palabras_clave) |  # Profesión individual
                Q(perfil_vacante__grupo_profesion__nombre__icontains=palabras_clave) |  # Grupo de profesión
                Q(perfil_vacante__profesion_estudio_listado__icontains=palabras_clave)  # Profesiones del JSON
            )

        

    context = {
        'vacantes_disponibles': vacantes_disponibles,
        'data_candidate': data,
        'form': form,
    }

    return render(request, 'admin/vacancy/candidate_user/vacancy_available.html', context)


@login_required
@validar_permisos('acceso_candidato')
def get_filter_options(request):
    """Vista AJAX para obtener opciones de filtros dinámicamente"""
    from django.http import JsonResponse
    from applications.vacante.forms.BuscarVacanteForm import VacanteFiltro
    
    # Obtener parámetros del request
    ciudad = request.GET.get('ciudad', '')
    experiencia = request.GET.get('experiencia_requerida', '')
    profesion = request.GET.get('profesion_estudio', '')
    palabras_clave = request.GET.get('palabras_clave', '')
    
    # Crear datos de request para el formulario
    request_data = {
        'ciudad': ciudad,
        'experiencia_requerida': experiencia,
        'profesion_estudio': profesion,
        'palabras_clave': palabras_clave
    }
    
    # Crear formulario con los datos actuales
    form = VacanteFiltro(request_data=request_data)
    
    # Obtener las opciones de cada campo
    response_data = {
        'ciudad_options': list(form.fields['ciudad'].choices),
        'profesion_options': list(form.fields['profesion_estudio'].choices),
        'experiencia_options': list(form.fields['experiencia_requerida'].choices),
    }
    
    return JsonResponse(response_data)


@login_required
@validar_permisos('acceso_candidato')
def get_filter_stats(request):
    """Vista AJAX para obtener estadísticas de filtros"""
    from django.http import JsonResponse
    from applications.vacante.models import Cli052Vacante, Cli073PerfilVacante
    from applications.candidato.models import Can101Candidato
    
    # Obtener parámetros del request
    ciudad = request.GET.get('ciudad', '')
    experiencia = request.GET.get('experiencia_requerida', '')
    profesion = request.GET.get('profesion_estudio', '')
    palabras_clave = request.GET.get('palabras_clave', '')
    
    # Obtener candidato actual
    candidato_id = request.session.get('candidato_id')
    candidato = Can101Candidato.objects.get(pk=candidato_id)
    
    # Construir queryset base
    vacantes_disponibles = Cli052Vacante.objects.filter(
        estado_vacante__in=[1, 2],
        perfil_vacante__estado=1,
    ).exclude(
        aplicaciones__candidato_101=candidato_id
    )
    
    # Aplicar filtros
    if ciudad:
        vacantes_disponibles = vacantes_disponibles.filter(perfil_vacante__lugar_trabajo=ciudad)
    
    if experiencia:
        experiencia_int = int(experiencia) if experiencia.isdigit() else None
        if experiencia_int:
            if experiencia_int == 6:  # Sin Experiencia
                vacantes_disponibles = vacantes_disponibles.filter(perfil_vacante__tiempo_experiencia=6)
            else:
                valores_experiencia = list(range(1, experiencia_int + 1))
                vacantes_disponibles = vacantes_disponibles.filter(perfil_vacante__tiempo_experiencia__in=valores_experiencia)
    
    if profesion:
        # Manejar diferentes tipos de profesiones
        if profesion.startswith('grupo_'):
            # Es un grupo de profesiones
            grupo_id = profesion.replace('grupo_', '')
            vacantes_disponibles = vacantes_disponibles.filter(perfil_vacante__grupo_profesion=grupo_id)
        else:
            # Es una profesión individual o del JSON
            from django.db.models import Q
            vacantes_disponibles = vacantes_disponibles.filter(
                Q(perfil_vacante__profesion_estudio=profesion) |
                Q(perfil_vacante__profesion_estudio_listado__icontains=f'"id":{profesion}')
            )

    # Filtro por palabras clave
    if palabras_clave:
        from django.db.models import Q
        # Buscar en múltiples campos relacionados
        vacantes_disponibles = vacantes_disponibles.filter(
            Q(titulo__icontains=palabras_clave) |  # Título de la vacante
            Q(descripcion_vacante__icontains=palabras_clave) |  # Descripción de la vacante
            Q(cargo__nombre_cargo__icontains=palabras_clave) |  # Nombre del cargo
            Q(perfil_vacante__profesion_estudio__nombre__icontains=palabras_clave) |  # Profesión individual
            Q(perfil_vacante__grupo_profesion__nombre__icontains=palabras_clave) |  # Grupo de profesión
            Q(perfil_vacante__profesion_estudio_listado__icontains=palabras_clave)  # Profesiones del JSON
        )
    
    # Obtener estadísticas
    total_resultados = vacantes_disponibles.count()
    
    # Estadísticas por ciudad
    stats_ciudad = {}
    for vacante in vacantes_disponibles.select_related('perfil_vacante__lugar_trabajo'):
        ciudad_nombre = vacante.perfil_vacante.lugar_trabajo.nombre if vacante.perfil_vacante.lugar_trabajo else 'Sin ciudad'
        stats_ciudad[ciudad_nombre] = stats_ciudad.get(ciudad_nombre, 0) + 1
    
    # Estadísticas por profesión
    stats_profesion = {}
    import json
    
    for vacante in vacantes_disponibles.select_related('perfil_vacante__profesion_estudio', 'perfil_vacante__grupo_profesion'):
        perfil = vacante.perfil_vacante
        
        # 1. Profesión individual
        if perfil.profesion_estudio:
            profesion_nombre = perfil.profesion_estudio.nombre
            stats_profesion[profesion_nombre] = stats_profesion.get(profesion_nombre, 0) + 1
        
        # 2. Grupo de profesiones
        if perfil.grupo_profesion:
            grupo_nombre = perfil.grupo_profesion.nombre
            stats_profesion[grupo_nombre] = stats_profesion.get(grupo_nombre, 0) + 1
        
        # 3. Profesiones del listado JSON
        if perfil.profesion_estudio_listado:
            try:
                profesiones_json = json.loads(perfil.profesion_estudio_listado)
                if isinstance(profesiones_json, list):
                    for prof in profesiones_json:
                        if isinstance(prof, dict) and 'value' in prof:
                            profesion_nombre = prof['value']
                            stats_profesion[profesion_nombre] = stats_profesion.get(profesion_nombre, 0) + 1
            except (json.JSONDecodeError, TypeError):
                continue
        
        # Si no hay ninguna profesión definida
        if not perfil.profesion_estudio and not perfil.grupo_profesion and not perfil.profesion_estudio_listado:
            stats_profesion['Sin profesión'] = stats_profesion.get('Sin profesión', 0) + 1
    
    # Estadísticas por experiencia
    stats_experiencia = {}
    from applications.services.choices import TIEMPO_EXPERIENCIA_CHOICES_STATIC
    experiencia_choices = dict(TIEMPO_EXPERIENCIA_CHOICES_STATIC[1:])  # Excluir opción vacía
    
    for vacante in vacantes_disponibles:
        exp_id = vacante.perfil_vacante.tiempo_experiencia
        exp_nombre = experiencia_choices.get(exp_id, f'Experiencia {exp_id}')
        stats_experiencia[exp_nombre] = stats_experiencia.get(exp_nombre, 0) + 1
    
    response_data = {
        'total_resultados': total_resultados,
        'stats_ciudad': stats_ciudad,
        'stats_profesion': stats_profesion,
        'stats_experiencia': stats_experiencia,
    }
    
    return JsonResponse(response_data)

@login_required
@validar_permisos('acceso_candidato')
def upload_requisito_document(request, aplicacion_id, requisito_id):
    """Vista para cargar documentos de requisitos"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        # Obtener el ID del candidato desde la sesión
        candidato_id = request.session.get('candidato_id')
        
        # Verificar que la aplicación pertenece al candidato
        aplicacion = get_object_or_404(
            Cli056AplicacionVacante, 
            id=aplicacion_id, 
            candidato_101=candidato_id
        )
        
        # Obtener la asignación del requisito
        asignacion_requisito = get_object_or_404(Cli070AsignacionRequisito, id=requisito_id)
        
        # Verificar que el archivo fue enviado
        if 'archivo_requisito' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'No se envió ningún archivo'}, status=400)
        
        archivo = request.FILES['archivo_requisito']
        
        # Validar tipo de archivo (solo PDF, JPG, PNG)
        import os
        ext = os.path.splitext(archivo.name)[1].lower()
        extensiones_permitidas = ['.pdf', '.jpg', '.png']
        if ext not in extensiones_permitidas:
            return JsonResponse({
                'success': False, 
                'error': 'Solo se permiten archivos PDF, JPG y PNG'
            }, status=400)
        
        # Validar tamaño del archivo (máximo 10 MB)
        if archivo.size > 10 * 1024 * 1024:
            return JsonResponse({'success': False, 'error': 'El archivo no puede superar los 10 MB'}, status=400)
        
        # Obtener el estado activo (id=1)
        estado = get_object_or_404(Cat001Estado, id=1)
        
        # Obtener el usuario logueado
        usuario = request.user
        
        # Crear o actualizar el requisito cargado
        requisito_cargado, created = Cli079RequisitosCargado.objects.update_or_create(
            aplicacion_vacante_056=aplicacion,
            asignacion_requisito_070=asignacion_requisito,
            defaults={
                'archivo_requisito': archivo,
                'usuario_cargado': usuario,
                'estado': estado,
            }
        )
        
        mensaje = 'Documento cargado exitosamente' if created else 'Documento actualizado exitosamente'
        
        return JsonResponse({
            'success': True,
            'message': mensaje,
            'requisito_id': requisito_cargado.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al cargar el documento: {str(e)}'
        }, status=500)

@login_required
@validar_permisos('acceso_candidato')
def guardar_respuestas_politicas(request, aplicacion_id):
    """Vista para guardar las respuestas de políticas internas"""
    try:
        # Obtener el ID del candidato desde la sesión
        candidato_id = request.session.get('candidato_id')
        
        # Verificar que la aplicación pertenece al candidato
        aplicacion = get_object_or_404(
            Cli056AplicacionVacante, 
            id=aplicacion_id, 
            candidato_101=candidato_id
        )
        
        if request.method == 'POST':
            import json
            
            # Obtener datos del FormData
            respuestas_json_str = request.POST.get('respuestas', '{}')
            respuestas = json.loads(respuestas_json_str) if respuestas_json_str else {}
            
            # Obtener la imagen de la firma
            firma_file = request.FILES.get('firma')
            
            # Obtener o inicializar json_politicas_internas
            politicas_guardadas = aplicacion.json_politicas_internas if aplicacion.json_politicas_internas else {}
            if not isinstance(politicas_guardadas, dict):
                politicas_guardadas = {}
            
            # Guardar todas las respuestas
            from applications.cliente.models import Cli067PoliticasInternas
            for politica_id_str, politica_data in respuestas.items():
                try:
                    politica_id = int(politica_id_str)
                    politica_obj = Cli067PoliticasInternas.objects.get(id=politica_id)
                    respuestas_json = politica_obj.respuestas_politica
                    respuesta = politica_data.get('respuesta', '')
                    preguntas = politica_data.get('preguntas', {})
                    
                    # Construir la estructura de respuesta según el JSON de la política
                    respuesta_estructurada = {}
                    
                    if respuestas_json and isinstance(respuestas_json, dict):
                        # Si tiene estructura si/no
                        if "si" in respuestas_json or "no" in respuestas_json:
                            respuesta_estructurada['respuesta'] = respuesta
                            # Si la respuesta es "si" y hay preguntas, guardarlas
                            if respuesta == "si" and preguntas:
                                respuesta_estructurada['preguntas'] = preguntas
                        else:
                            # Si no tiene estructura si/no, guardar como texto
                            respuesta_estructurada['respuesta'] = respuesta
                    else:
                        # Si no hay JSON, guardar como texto
                        respuesta_estructurada['respuesta'] = respuesta
                    
                    # Guardar la respuesta para esta política
                    politicas_guardadas[str(politica_id)] = respuesta_estructurada
                    
                except (Cli067PoliticasInternas.DoesNotExist, ValueError):
                    # Si no se encuentra la política o hay error, guardar de forma simple
                    politicas_guardadas[politica_id_str] = {
                        'respuesta': politica_data.get('respuesta', ''),
                        'preguntas': politica_data.get('preguntas', {})
                    }
            
            # Guardar en el campo json_politicas_internas
            aplicacion.json_politicas_internas = politicas_guardadas
            aplicacion.save()
            
            # Guardar la firma en Cli080DocumentoFirmadoAplicacionVacante
            if firma_file:
                # Generar código único
                codigo_unico = generar_codigo_unico()
                
                # Obtener IP del firmante
                ip_firmante = request.META.get('REMOTE_ADDR', '')
                if not ip_firmante:
                    ip_firmante = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() if request.META.get('HTTP_X_FORWARDED_FOR') else ''
                
                # Obtener o crear el documento firmado
                documento_firmado, created = Cli080DocumentoFirmadoAplicacionVacante.objects.get_or_create(
                    aplicacion_vacante_056=aplicacion,
                    defaults={
                        'usuario_firmante': request.user,
                        'estado': get_object_or_404(Cat001Estado, pk=1),
                        'ip_firmante': ip_firmante,
                        'codigo_unico': codigo_unico
                    }
                )
                
                # Si ya existe, actualizar
                if not created:
                    documento_firmado.usuario_firmante = request.user
                    documento_firmado.ip_firmante = ip_firmante
                    if not documento_firmado.codigo_unico:
                        documento_firmado.codigo_unico = codigo_unico
                    else:
                        codigo_unico = documento_firmado.codigo_unico
                
                # Guardar la firma
                documento_firmado.imagen_firmada.save(
                    f'firma_{aplicacion.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png',
                    firma_file,
                    save=True
                )
                
                # Guardar primero para tener el ID actualizado
                documento_firmado.save()
                
                # Generar y guardar el PDF firmado
                fecha_firma_actual = datetime.now()
                pdf_buffer = generar_pdf_documento_firmado(
                    aplicacion=aplicacion,
                    fecha_firma=fecha_firma_actual,
                    ip_firmante=ip_firmante,
                    codigo_unico=codigo_unico
                )
                
                # Guardar el PDF en el campo documento_firmado
                nombre_pdf = f'politica_firmada_{aplicacion.id}_{fecha_firma_actual.strftime("%Y%m%d_%H%M%S")}.pdf'
                documento_firmado.documento_firmado.save(
                    nombre_pdf,
                    ContentFile(pdf_buffer.getvalue()),
                    save=True
                )
                
                documento_firmado.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Respuestas de políticas guardadas exitosamente.'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Método no permitido'
            }, status=405)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al guardar las respuestas: {str(e)}'
        }, status=500)

@login_required
@validar_permisos('acceso_candidato')
def generar_declaracion_pdf(request, aplicacion_id):
    """Vista para generar el PDF de declaración del candidato"""
    try:
        # Obtener el ID del candidato desde la sesión
        candidato_id = request.session.get('candidato_id')
        
        # Verificar que la aplicación pertenece al candidato
        aplicacion = get_object_or_404(
            Cli056AplicacionVacante, 
            id=aplicacion_id, 
            candidato_101=candidato_id
        )
        
        # Obtener información del candidato
        candidato = aplicacion.candidato_101
        nombre_completo = candidato.nombre_completo()
        numero_documento = candidato.numero_documento or "N/A"
        tipo_documento = "Cédula de Ciudadanía"  # Valor por defecto, puede ajustarse según necesidad
        ciudad_documento = candidato.ciudad_id_004.nombre if candidato.ciudad_id_004 else "N/A"
        fecha_nacimiento = candidato.fecha_nacimiento.strftime("%d/%m/%Y") if candidato.fecha_nacimiento else "N/A"
        
        # Obtener información de la vacante y cargo
        vacante = aplicacion.vacante_id_052
        cargo_postulado = vacante.cargo.nombre_cargo if vacante.cargo else "N/A"
        
        # Obtener información del cliente
        cliente = vacante.cargo.cliente if vacante.cargo and vacante.cargo.cliente else None
        nombre_empresa = cliente.razon_social if cliente else "N/A"
        
        # Ciudad de firma (usar ciudad del candidato)
        ciudad_firma = ciudad_documento
        
        # Fecha actual
        fecha_actual = datetime.now()
        dia_firma = fecha_actual.day
        meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        mes_firma = meses[fecha_actual.month - 1]
        anio_firma = fecha_actual.year
        
        # Información del responsable (usuario reclutador o usuario logueado)
        responsable = aplicacion.usuario_reclutador if aplicacion.usuario_reclutador else request.user
        nombre_responsable = responsable.get_full_name() if hasattr(responsable, 'get_full_name') and responsable.get_full_name() else responsable.username
        cargo_responsable = "Responsable del Proceso de Selección"  # Valor por defecto
        
        # Obtener políticas internas del cliente
        politicas_internas = []
        if cliente:
            politicas_internas = Cli051ClientePoliticas.objects.filter(
                cliente=cliente,
                estado_id=1
            ).select_related('politica_interna')
        
        # Obtener respuestas guardadas
        respuestas_guardadas = aplicacion.json_politicas_internas if aplicacion.json_politicas_internas else {}
        if not isinstance(respuestas_guardadas, dict):
            respuestas_guardadas = {}
        
        # Obtener información del documento firmado
        documento_firmado_obj = None
        fecha_firma_pdf = None
        ip_firmante_pdf = None
        codigo_unico_pdf = None
        
        try:
            documento_firmado_obj = Cli080DocumentoFirmadoAplicacionVacante.objects.filter(
                aplicacion_vacante_056=aplicacion,
                estado_id=1
            ).first()
            if documento_firmado_obj:
                fecha_firma_pdf = documento_firmado_obj.fecha_firma_hora_ip
                ip_firmante_pdf = documento_firmado_obj.ip_firmante
                codigo_unico_pdf = documento_firmado_obj.codigo_unico
        except:
            pass
        
        # Si existe un documento PDF guardado, devolverlo directamente
        if documento_firmado_obj and documento_firmado_obj.documento_firmado:
            try:
                # Leer el archivo PDF guardado
                documento_firmado_obj.documento_firmado.open('rb')
                pdf_content = documento_firmado_obj.documento_firmado.read()
                documento_firmado_obj.documento_firmado.close()
                
                # Crear la respuesta HTTP con el PDF guardado
                response = HttpResponse(pdf_content, content_type='application/pdf')
                response['Content-Disposition'] = f'inline; filename="politica_firmada_{aplicacion_id}.pdf"'
                return response
            except Exception as e:
                # Si hay error al leer el archivo, continuar con la generación dinámica
                pass
        
        # Si no hay fecha de firma, usar la fecha actual
        if fecha_firma_pdf is None:
            fecha_firma_pdf = datetime.now()
        
        # Generar el PDF usando la función auxiliar
        pdf_buffer = generar_pdf_documento_firmado(
            aplicacion=aplicacion,
            fecha_firma=fecha_firma_pdf,
            ip_firmante=ip_firmante_pdf,
            codigo_unico=codigo_unico_pdf
        )
        
        # Obtener el valor del buffer y crear la respuesta HTTP
        pdf = pdf_buffer.getvalue()
        pdf_buffer.close()
        
        # Crear la respuesta HTTP
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="declaracion_{aplicacion_id}_{datetime.now().strftime("%Y%m%d")}.pdf"'
        response.write(pdf)
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error al generar el PDF: {str(e)}')
        return redirect('vacantes:vacante_candidato_aplicadas_detalle', pk=aplicacion_id)