from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from django.contrib.staticfiles import finders
from io import BytesIO
import json
import os
import urllib.request
import urllib.parse
from datetime import datetime
try:
    from PIL import Image as PILImage, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, Flowable
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from applications.common.models import Cat001Estado
from applications.reclutado.models import Cli056AplicacionVacante
from applications.candidato.models import Can101Candidato
from applications.entrevista.models import Cli057AsignacionEntrevista
from applications.cliente.models import Cli051Cliente
from applications.usuarios.decorators import validar_permisos
from applications.services.service_vacanty import query_vacanty_detail
from applications.services.service_recruited import query_recruited_vacancy_id, consultar_historial_aplicacion_vacante
from applications.services.service_candidate import buscar_candidato
from applications.vacante.forms.EntrevistaForm import EntrevistaCrearForm
from components.RegistrarHistorialVacante import crear_historial_aplicacion
from applications.common.views.EnvioCorreo import enviar_correo
from applications.usuarios.models import UsuarioBase


@login_required
# @validar_permisos('acceso_admin')
def detail_aplicacion_vacante(request, pk):
    """
    Vista para mostrar el detalle de una aplicaci?n de vacante por parte del administrador.
    """
    url_actual = f"{request.scheme}://{request.get_host()}"
    
    # Obtener la aplicaci?n de vacante
    asignacion_vacante = get_object_or_404(Cli056AplicacionVacante, id=pk)
    
    # Obtener el json_match y parsearlo
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
    
    # Obtener informaci?n del candidato
    info_candidato = get_object_or_404(Can101Candidato, id=asignacion_vacante.candidato_101.id)
    info_detalle_candidato = buscar_candidato(asignacion_vacante.candidato_101.id)
    
    # Obtener informaci?n del historial de la vacante
    historico_vacante = consultar_historial_aplicacion_vacante(asignacion_vacante.id)
    
    # Obtener los datos de las entrevistas
    entrevista = Cli057AsignacionEntrevista.objects.filter(
        asignacion_vacante=asignacion_vacante.id
    ).order_by('-fecha_entrevista')
    
    # Obtener informaci?n del cliente
    cliente_id = asignacion_vacante.vacante_id_052.asignacion_cliente_id_064.id_cliente_asignado.id
    cliente = get_object_or_404(Cli051Cliente, id=cliente_id)
    
    # Obtener informaci?n de la vacante
    vacante = query_vacanty_detail().get(id=asignacion_vacante.vacante_id_052.id)
    
    # Obtener los reclutados asociados a la vacante
    reclutados = query_recruited_vacancy_id(vacante.id)
    
    # Obtener el grupo_id de la sesi?n
    grupo_id = request.session.get('grupo_id', 1)  # Default admin
    
    # Inicializar formulario de entrevista
    form = EntrevistaCrearForm(grupo_id=grupo_id, cliente_id=cliente_id, vacante=vacante)
    
    if request.method == 'POST':
        form = EntrevistaCrearForm(request.POST, grupo_id=grupo_id, cliente_id=cliente_id, vacante=vacante)
        if form.is_valid():
            fecha_entrevista = form.cleaned_data['fecha_entrevista']
            hora_entrevista = form.cleaned_data['hora_entrevista']
            entrevistador = form.cleaned_data['entrevistador']
            tipo_entrevista = form.cleaned_data['tipo_entrevista']
            lugar_enlace = form.cleaned_data['lugar_enlace']
            usuario_asignado = get_object_or_404(UsuarioBase, id=entrevistador)
            
            # Obtener instancias de los modelos relacionados
            usuario_asigno = request.user
            estado_default = Cat001Estado.objects.get(id=1)
            
            # Crear la nueva asignaci?n de entrevista
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
            
            # Funci?n para crear registro en el historial y actualizar estado de la aplicaci?n de la vacante
            crear_historial_aplicacion(
                asignacion_vacante, 
                2, 
                request.session.get('_auth_user_id'), 
                'Entrevista Asignada'
            )
            
            contexto_email = {
                'entrevistador': f'{usuario_asignado.primer_nombre} {usuario_asignado.segundo_nombre} {usuario_asignado.primer_apellido}',
                'nombre_candidato': f'{info_candidato.primer_nombre} {info_candidato.segundo_nombre} {info_candidato.primer_apellido} {info_candidato.segundo_apellido}',
                'fecha_entrevista': fecha_entrevista,
                'hora_entrevista': hora_entrevista,
                'lugar_enlace': lugar_enlace,
                'vacante': vacante.titulo,
                'cliente': cliente.razon_social,
                'url': url_actual
            }
            
            lista_correos = [
                usuario_asignado.email,
                info_candidato.email
            ]
            
            # Env?o de correo
            enviar_correo(
                'asignacion_entrevista_entrevista', 
                contexto_email, 
                f'Asignaci?n de Entrevista ID: {asignacion_entrevista.id}', 
                lista_correos, 
                correo_remitente=None
            )
            
            messages.success(request, 'Se ha asignado entrevista correctamente.')
            return redirect('reclutados:reclutados_detalle_admin', pk=pk)
        else:
            messages.error(request, 'Error al crear la asignaci?n')
    
    context = {
        'form': form,
        'vacante': vacante,
        'reclutados': reclutados,
        'candidato': info_candidato,
        'reclutado': asignacion_vacante,
        'entrevista': entrevista,
        'info_detalle_candidato': info_detalle_candidato,
        'historial': historico_vacante,
        'json_match': json_match,
        'cliente': cliente,
    }
    
    return render(request, 'admin/recruited/admin_user/recruited_detail.html', context)


@login_required
# @validar_permisos('acceso_admin')
def generar_reporte_pdf(request, pk):
    """
    Vista para generar un reporte PDF de la aplicación de vacante.
    """
    # Obtener la aplicación de vacante
    asignacion_vacante = get_object_or_404(Cli056AplicacionVacante, id=pk)
    
    # Obtener información del candidato
    info_candidato = get_object_or_404(Can101Candidato, id=asignacion_vacante.candidato_101.id)
    info_detalle_candidato = buscar_candidato(asignacion_vacante.candidato_101.id)
    
    # Obtener información del cliente
    cliente_id = asignacion_vacante.vacante_id_052.asignacion_cliente_id_064.id_cliente_asignado.id
    cliente = get_object_or_404(Cli051Cliente, id=cliente_id)
    
    # Obtener información de la vacante
    vacante = query_vacanty_detail().get(id=asignacion_vacante.vacante_id_052.id)
    
    # Crear el buffer para el PDF
    buffer = BytesIO()
    
    # Crear el documento PDF en tamaño carta con márgenes muy justas
    # Top margin muy reducido para que el encabezado esté más cerca del borde superior
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                            rightMargin=36, leftMargin=36,
                            topMargin=10, bottomMargin=36)
    
    # Contenedor para los elementos del PDF
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Colores de la aplicación
    color_primary = colors.HexColor('#B10022')  # Color principal
    # Fondo rojo con opacity 10 (bg-primary bg-opacity-10)
    # Cálculo: #B10022 (177, 0, 34) con 10% opacidad sobre blanco (255, 255, 255)
    # = (255*0.9 + 177*0.1, 255*0.9 + 0*0.1, 255*0.9 + 34*0.1) ≈ (247, 230, 233)
    color_bg_primary_opacity = colors.HexColor('#F7E6E9')  # #B10022 con 10% opacidad sobre blanco
    color_text_dark = colors.HexColor('#212529')  # Texto oscuro
    color_text_gray = colors.HexColor('#6c757d')  # Texto gris
    
    # ========== ENCABEZADO ==========
    # Intentar obtener la ruta del logo
    logo_path = None
    logo_paths = [
        os.path.join(settings.BASE_DIR, 'static', 'admin', 'images', 'landing', 'logo-talent-tray.png'),
        os.path.join(settings.BASE_DIR, 'static', 'admin', 'images', 'logo-icon.png'),
    ]
    
    for path in logo_paths:
        if os.path.exists(path):
            logo_path = path
            break
    
    # Si no se encuentra, intentar con finders
    if not logo_path:
        logo_path = finders.find('admin/images/landing/logo-talent-tray.png')
        if not logo_path:
            logo_path = finders.find('admin/images/logo-icon.png')
    
    # Obtener imagen del candidato desde el modelo Can101Candidato
    candidato_img_url = None
    candidato_img_path = None
    if info_candidato.imagen_perfil:
        # Intentar obtener la ruta local primero
        try:
            candidato_img_path = info_candidato.imagen_perfil.path
            if not os.path.exists(candidato_img_path):
                candidato_img_path = None
        except:
            candidato_img_path = None
        
        # Si no hay ruta local, intentar obtener la URL (para S3 o media)
        if not candidato_img_path:
            try:
                candidato_img_url = info_candidato.imagen_perfil.url
                # Si la URL es relativa, construir la URL completa
                if candidato_img_url and not candidato_img_url.startswith('http'):
                    if hasattr(settings, 'MEDIA_URL'):
                        if settings.MEDIA_URL.startswith('http'):
                            candidato_img_url = settings.MEDIA_URL.rstrip('/') + '/' + candidato_img_url.lstrip('/')
                        else:
                            # Construir URL completa desde la request
                            base_url = f"{request.scheme}://{request.get_host()}"
                            candidato_img_url = base_url + settings.MEDIA_URL.rstrip('/') + '/' + candidato_img_url.lstrip('/')
            except Exception as e:
                print(f"Error obteniendo URL de imagen: {e}")
                candidato_img_url = None
    
    # Columna izquierda: Logo
    if logo_path and os.path.exists(logo_path):
        try:
            logo_img = RLImage(logo_path, width=1.5*inch, height=0.5*inch, kind='proportional')
            header_left = logo_img
        except:
            header_left = Paragraph("<b>TALENT TRAY</b>", 
                                   ParagraphStyle('LogoText', fontSize=14, 
                                                 textColor=color_primary, 
                                                 fontName='Helvetica-Bold'))
    else:
        header_left = Paragraph("<b>TALENT TRAY</b>", 
                               ParagraphStyle('LogoText', fontSize=14, 
                                             textColor=color_primary, 
                                             fontName='Helvetica-Bold'))
    
    # Columna centro: Cargo (fuente grande) y Cliente (fuente pequeña)
    cargo_text = str(vacante.cargo) if vacante.cargo else 'Cargo no especificado'
    cliente_text = cliente.razon_social
    
    cargo_style = ParagraphStyle(
        'CargoStyle',
        parent=styles['Normal'],
        fontSize=18,
        textColor=color_text_dark,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=8  # Aumentado de 4 a 8 para más separación
    )
    
    cliente_style = ParagraphStyle(
        'ClienteStyle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=color_text_gray,
        fontName='Helvetica',
        alignment=TA_CENTER
    )
    
    # Crear tabla interna para el centro (cargo arriba, cliente abajo)
    from reportlab.platypus import KeepTogether
    header_center_table = Table([
        [Paragraph(f"<b>{cargo_text}</b>", cargo_style)],
        [Paragraph(cliente_text, cliente_style)]
    ], colWidths=[3*inch])
    header_center_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (0, 0), 8),  # Padding inferior en la fila del cargo
        ('TOPPADDING', (1, 0), (1, 0), 4),     # Padding superior en la fila del cliente
        ('BOTTOMPADDING', (1, 0), (1, 0), 2),
        ('TOPPADDING', (0, 0), (0, 0), 2),
    ]))
    
    # Clase personalizada para imagen circular con borde rojo
    class CircularImage(Flowable):
        def __init__(self, image_path_or_url, size, border_color, border_width=3):
            Flowable.__init__(self)
            self.image_path_or_url = image_path_or_url
            self.size = size
            self.border_color = border_color
            self.border_width = border_width
            self.is_url = image_path_or_url and (isinstance(image_path_or_url, str) and image_path_or_url.startswith('http'))
        
        def wrap(self, availWidth, availHeight):
            return (self.size, self.size)
        
        def draw(self):
            self.canv.saveState()
            
            # Cargar la imagen
            try:
                if PIL_AVAILABLE:
                    if self.is_url:
                        img_data = urllib.request.urlopen(self.image_path_or_url).read()
                        img_temp = BytesIO(img_data)
                        pil_img = PILImage.open(img_temp)
                    else:
                        pil_img = PILImage.open(self.image_path_or_url)
                    
                    # Convertir a RGBA si es necesario
                    if pil_img.mode != 'RGBA':
                        pil_img = pil_img.convert('RGBA')
                    
                    # Redimensionar la imagen a una resolución más alta para mejor calidad
                    # Usar 2x o 3x la resolución final para evitar pixelación
                    scale_factor = 3  # Factor de escala para mejor calidad
                    high_res_size = int(self.size * scale_factor)
                    pil_img = pil_img.resize((high_res_size, high_res_size), PILImage.Resampling.LANCZOS)
                    
                    # Crear una máscara circular en alta resolución
                    mask = PILImage.new('L', (high_res_size, high_res_size), 0)
                    draw = ImageDraw.Draw(mask)
                    draw.ellipse((0, 0, high_res_size, high_res_size), fill=255)
                    
                    # Aplicar la máscara
                    output = PILImage.new('RGBA', (high_res_size, high_res_size), (255, 255, 255, 0))
                    output.paste(pil_img, (0, 0))
                    output.putalpha(mask)
                    
                    # Redimensionar a tamaño final con alta calidad
                    final_size = int(self.size)
                    output = output.resize((final_size, final_size), PILImage.Resampling.LANCZOS)
                    
                    # Guardar en un buffer temporal con alta calidad
                    img_buffer = BytesIO()
                    output.save(img_buffer, format='PNG', optimize=False)
                    img_buffer.seek(0)
                    
                    # Dibujar el círculo de borde rojo primero
                    self.canv.setStrokeColor(self.border_color)
                    self.canv.setLineWidth(self.border_width)
                    self.canv.circle(self.size/2, self.size/2, self.size/2 - self.border_width/2, stroke=1, fill=0)
                    
                    # Dibujar la imagen circular con alta calidad
                    from reportlab.lib.utils import ImageReader
                    img_reader = ImageReader(img_buffer)
                    # Usar preserveAspectRatio para mantener calidad
                    self.canv.drawImage(img_reader, 0, 0, width=self.size, height=self.size, 
                                      preserveAspectRatio=True, mask='auto')
                else:
                    # Si PIL no está disponible, usar reportlab directamente
                    from reportlab.lib.utils import ImageReader
                    if self.is_url:
                        img_data = urllib.request.urlopen(self.image_path_or_url).read()
                        img_temp = BytesIO(img_data)
                        img_reader = ImageReader(img_temp)
                    else:
                        img_reader = ImageReader(self.image_path_or_url)
                    
                    # Dibujar el círculo de borde rojo
                    self.canv.setStrokeColor(self.border_color)
                    self.canv.setLineWidth(self.border_width)
                    self.canv.circle(self.size/2, self.size/2, self.size/2 - self.border_width/2, stroke=1, fill=0)
                    
                    # Dibujar la imagen (no será perfectamente circular sin PIL, pero se intenta)
                    self.canv.drawImage(img_reader, 0, 0, width=self.size, height=self.size)
                
            except Exception as e:
                print(f"Error dibujando imagen circular: {e}")
                import traceback
                traceback.print_exc()
                # Si hay error, dibujar un círculo gris con borde rojo
                self.canv.setFillColor(colors.HexColor('#CCCCCC'))
                self.canv.circle(self.size/2, self.size/2, self.size/2 - self.border_width/2, stroke=0, fill=1)
                self.canv.setStrokeColor(self.border_color)
                self.canv.setLineWidth(self.border_width)
                self.canv.circle(self.size/2, self.size/2, self.size/2 - self.border_width/2, stroke=1, fill=0)
            
            self.canv.restoreState()
    
    # Columna derecha: Imagen del candidato y nombre lado a lado
    # Tamaño de la imagen circular (más pequeña)
    img_size = 0.5*inch
    
    # Buscar imagen por defecto
    default_img_path = None
    default_img_paths = [
        os.path.join(settings.BASE_DIR, 'static', 'admin', 'images', 'blank.png'),
        finders.find('admin/images/blank.png'),
    ]
    for path in default_img_paths:
        if path and os.path.exists(path):
            default_img_path = path
            break
    
    candidato_img = None
    img_source = None
    
    # Intentar cargar la imagen desde la ruta local primero
    if candidato_img_path and os.path.exists(candidato_img_path):
        try:
            img_source = candidato_img_path
            print(f"Imagen encontrada en path: {candidato_img_path}")
        except Exception as e:
            print(f"Error obteniendo path de imagen: {e}")
    
    # Si no hay ruta local, intentar desde URL
    if not img_source and candidato_img_url:
        try:
            # Construir URL completa si es necesario
            if not candidato_img_url.startswith('http'):
                base_url = f"{request.scheme}://{request.get_host()}"
                candidato_img_url = base_url + candidato_img_url
            
            img_source = candidato_img_url
            print(f"Usando URL de imagen: {candidato_img_url}")
        except Exception as e:
            print(f"Error obteniendo URL de imagen: {e}")
    
    # Si no hay imagen del candidato, usar la imagen por defecto
    if not img_source:
        if default_img_path:
            img_source = default_img_path
            print(f"Usando imagen por defecto: {default_img_path}")
        else:
            print("No se encontró imagen por defecto")
    
    # Crear la imagen circular con borde rojo
    if img_source:
        try:
            candidato_img = CircularImage(
                image_path_or_url=img_source,
                size=img_size,
                border_color=color_primary,
                border_width=3
            )
            print(f"Imagen circular creada exitosamente")
        except Exception as e:
            print(f"Error creando imagen circular: {e}")
            import traceback
            traceback.print_exc()
            candidato_img = None
    
    # Separar nombre y apellidos del candidato
    candidato_nombre = f"{info_candidato.primer_nombre or ''} {info_candidato.segundo_nombre or ''}".strip()
    candidato_apellidos = f"{info_candidato.primer_apellido or ''} {info_candidato.segundo_apellido or ''}".strip()
    
    # Estilo para el nombre (más grande, similar al cargo pero más pequeño)
    candidato_nombre_style = ParagraphStyle(
        'CandidatoNombreStyle',
        parent=styles['Normal'],
        fontSize=14,  # Más pequeño que el cargo (18) pero más grande que los apellidos
        textColor=color_text_dark,
        fontName='Helvetica-Bold',
        alignment=TA_RIGHT,  # Alineado a la derecha
        spaceAfter=4
    )
    
    # Estilo para los apellidos (más pequeño, similar al cliente)
    candidato_apellidos_style = ParagraphStyle(
        'CandidatoApellidosStyle',
        parent=styles['Normal'],
        fontSize=9,  # Más pequeño que el cliente (11)
        textColor=color_text_gray,
        fontName='Helvetica',
        alignment=TA_RIGHT  # Alineado a la derecha
    )
    
    # Crear párrafos para nombre y apellidos
    candidato_nombre_para = Paragraph(f"<b>{candidato_nombre}</b>", candidato_nombre_style)
    candidato_apellidos_para = Paragraph(candidato_apellidos, candidato_apellidos_style)
    
    # Crear tabla interna para el nombre y apellidos (similar al centro)
    candidato_info_table = Table([
        [candidato_nombre_para],
        [candidato_apellidos_para]
    ], colWidths=[1.9*inch])  # Ajustado para dar más espacio al texto
    candidato_info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),  # Alineado a la derecha
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (0, 0), 4),  # Padding inferior en la fila del nombre
        ('TOPPADDING', (1, 0), (1, 0), 2),    # Padding superior en la fila de apellidos
        ('BOTTOMPADDING', (1, 0), (1, 0), 0),
        ('TOPPADDING', (0, 0), (0, 0), 0),
    ]))
    
    # Asegurar que siempre haya una imagen (del candidato o por defecto)
    final_img = candidato_img
    if not final_img:
        if default_img_path and os.path.exists(default_img_path):
            try:
                final_img = CircularImage(
                    image_path_or_url=default_img_path,
                    size=img_size,
                    border_color=color_primary,
                    border_width=3
                )
            except:
                final_img = None
    
    # Crear tabla para la derecha (nombre/apellidos a la izquierda, imagen a la derecha)
    if final_img:
        print(f"Creando tabla con nombre/apellidos e imagen circular")
        header_right_table = Table([
            [candidato_info_table, final_img]
        ], colWidths=[1.9*inch, 0.6*inch])  # Ajustado para imagen más pequeña
    else:
        # Si no hay imagen, solo mostrar el nombre y apellidos
        print("No hay imagen disponible, mostrando solo nombre/apellidos")
        header_right_table = Table([
            [candidato_info_table]
        ], colWidths=[2.5*inch])
    
    header_right_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'RIGHT'),   # Información alineada a la derecha
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),  # Imagen centrada
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (0, 0), 0),   # Sin padding izquierdo en texto
        ('RIGHTPADDING', (0, 0), (0, 0), 8),  # Padding derecho en texto para separar de la imagen
        ('LEFTPADDING', (1, 0), (1, 0), 0),   # Sin padding izquierdo en imagen
    ]))
    
    # Crear la tabla principal del encabezado con 3 columnas
    header_table = Table([
        [header_left, header_center_table, header_right_table]
    ], colWidths=[2.5*inch, 3*inch, 2.5*inch])
    
    # La tabla mantendrá su fondo, pero el Flowable dibujará el contenedor redondeado alrededor
    header_table.setStyle(TableStyle([
        # Fondo del contenedor con color rojo opacity 10 (bg-primary bg-opacity-10)
        ('BACKGROUND', (0, 0), (-1, -1), color_bg_primary_opacity),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [color_bg_primary_opacity]),
        # Alineación
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        # Centrar verticalmente todo el contenido
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # Padding interno para dar espacio (reducido arriba para acercar al borde)
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 8),  # Reducido de 15 a 8 para acercar al borde superior
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    # Clase personalizada para dibujar contenedor con esquinas redondeadas
    class RoundedContainer(Flowable):
        def __init__(self, table, width, bg_color, border_color, radius=8):
            Flowable.__init__(self)
            self.table = table
            self.width = width
            self.bg_color = bg_color
            self.border_color = border_color
            self.radius = radius
            self.height = None
        
        def wrap(self, availWidth, availHeight):
            # Calcular el tamaño de la tabla primero
            if self.height is None:
                # Hacer que la tabla calcule su tamaño
                self.table_width, self.table_height = self.table.wrap(availWidth, availHeight)
                self.height = self.table_height
            return (self.width, self.height)
        
        def draw(self):
            self.canv.saveState()
            
            # Dibujar fondo con esquinas redondeadas
            self.canv.setFillColor(self.bg_color)
            self.canv.roundRect(0, 0, self.width, self.height, self.radius, fill=1, stroke=0)
            
            # Dibujar borde delgado rojo con esquinas redondeadas
            # Asegurar que el borde cubra todo el contenedor
            border_width = 1.0  # Borde delgado pero visible
            self.canv.setStrokeColor(self.border_color)
            self.canv.setLineWidth(border_width)
            self.canv.setLineCap(1)  # Round cap
            self.canv.setLineJoin(1)  # Round join
            
            # Dibujar el borde completo alrededor del contenedor
            # Ajustar ligeramente para que el borde se vea completo en todos los lados
            half_border = border_width / 2
            self.canv.roundRect(
                half_border, 
                half_border, 
                self.width - border_width, 
                self.height - border_width, 
                self.radius, 
                fill=0, 
                stroke=1
            )
            
            self.canv.restoreState()
            
            # Dibujar la tabla encima del fondo (centrada horizontalmente)
            x_offset = (self.width - self.table_width) / 2
            self.table.drawOn(self.canv, x_offset, 0)
    
    # Ancho del contenedor (ancho de página menos márgenes)
    header_width = letter[0] - 72  # Ancho de letter menos márgenes izquierdo y derecho (36*2)
    
    # Crear el contenedor con esquinas redondeadas que envuelve la tabla
    rounded_container = RoundedContainer(
        table=header_table,
        width=header_width,
        bg_color=color_bg_primary_opacity,
        border_color=color_primary,  # Borde rojo delgado
        radius=15  # Esquinas más redondeadas
    )
    
    elements.append(rounded_container)
    elements.append(Spacer(1, 0.3*inch))
    
    # ========== PANEL DE INFORMACIÓN BÁSICA DEL CANDIDATO ==========
    # Obtener información adicional del candidato
    candidato_sexo_display = info_candidato.get_sexo_display() if hasattr(info_candidato, 'get_sexo_display') else (info_candidato.sexo or 'No especificado')
    candidato_ciudad = info_candidato.ciudad_id_004.nombre if info_candidato.ciudad_id_004 else 'No especificada'
    candidato_direccion = info_candidato.direccion or 'No especificada'
    candidato_perfil = info_candidato.perfil or 'No especificado'
    candidato_aspiracion = info_candidato.aspiracion_salarial
    candidato_fecha_nac = info_candidato.fecha_nacimiento.strftime('%d/%m/%Y') if info_candidato.fecha_nacimiento else 'No especificada'
    
    # Estilo para el título del panel (centrado y destacado)
    panel_title_style = ParagraphStyle(
        'PanelTitleStyle',
        parent=styles['Normal'],
        fontSize=16,
        textColor=color_primary,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,  # Título centrado
        spaceAfter=12
    )
    
    # Estilo para los títulos de los campos (en rojo, letra pequeña)
    field_title_style = ParagraphStyle(
        'FieldTitleStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=color_primary,  # Títulos en rojo
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        spaceAfter=2
    )
    
    # Estilo para los valores de información (texto gris)
    field_value_style = ParagraphStyle(
        'FieldValueStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=color_text_gray,
        fontName='Helvetica',
        alignment=TA_LEFT,
        spaceAfter=0
    )
    
    # Crear imagen del candidato para el panel
    panel_img_size = 1.3*inch
    panel_candidato_img = None
    if img_source:
        try:
            panel_candidato_img = CircularImage(
                image_path_or_url=img_source,
                size=panel_img_size,
                border_color=color_primary,
                border_width=3
            )
        except Exception as e:
            print(f"Error creando imagen para panel: {e}")
            panel_candidato_img = None
    
    # Si no hay imagen, usar la del header o crear una por defecto
    if not panel_candidato_img:
        if default_img_path and os.path.exists(default_img_path):
            try:
                panel_candidato_img = CircularImage(
                    image_path_or_url=default_img_path,
                    size=panel_img_size,
                    border_color=color_primary,
                    border_width=3
                )
            except:
                panel_candidato_img = None
    
    # Ancho para la columna de la imagen
    image_column_width = 1.5*inch
    # Ancho disponible para la información (dejando espacio para la imagen)
    info_column_width = header_width - image_column_width - 0.5*inch
    
    # Función auxiliar para crear celda con valor arriba y título abajo
    def create_info_cell_reversed(value, title):
        """Crea una celda con valor arriba y título abajo"""
        cell_table = Table([
            [Paragraph(str(value) if value else 'No especificado', field_value_style)],
            [Paragraph(f"<b>{title}</b>", field_title_style)]
        ], colWidths=[info_column_width / 2 - 0.1*inch])
        cell_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        return cell_table
    
    # Crear tabla tabular con información organizada
    info_table_data = []
    
    # Si hay perfil, agregarlo primero en la parte superior
    if candidato_perfil and candidato_perfil != 'No especificado':
        # Estilo para el texto del perfil
        perfil_text_style = ParagraphStyle(
            'PerfilTextStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=color_text_dark,
            fontName='Helvetica',
            alignment=TA_LEFT,
            spaceAfter=0
        )
        perfil_cell = Table([
            [Paragraph("<b>Perfil del Candidato</b>", field_title_style)],
            [Paragraph(candidato_perfil, perfil_text_style)]
        ], colWidths=[info_column_width])
        perfil_cell.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        if panel_candidato_img:
            info_table_data.append([perfil_cell, '', '', '', ''])
        else:
            info_table_data.append([perfil_cell, '', '', ''])
    
    # Crear filas de datos con valor arriba y título abajo
    if panel_candidato_img:
        # Con imagen: Valor | Título | Valor | Título | Imagen
        # Determinar en qué fila va la imagen (primera fila de información, no la del perfil)
        has_perfil = candidato_perfil and candidato_perfil != 'No especificado'
        first_info_row = 1 if has_perfil else 0
        
        # Fila 1: Documento y Email
        info_table_data.append([
            create_info_cell_reversed(info_candidato.numero_documento, "Documento"),
            create_info_cell_reversed(info_candidato.email, "Email"),
            '',  # Espacio
            '',  # Espacio
            panel_candidato_img if len(info_table_data) == first_info_row else ''
        ])
        
        # Fila 2: Teléfono y Género
        info_table_data.append([
            create_info_cell_reversed(info_candidato.telefono, "Teléfono"),
            create_info_cell_reversed(candidato_sexo_display, "Género"),
            '',  # Espacio
            '',  # Espacio
            ''
        ])
        
        # Fila 3: Fecha de Nacimiento y Ciudad
        info_table_data.append([
            create_info_cell_reversed(candidato_fecha_nac, "Fecha de Nacimiento"),
            create_info_cell_reversed(candidato_ciudad, "Ciudad"),
            '',  # Espacio
            '',  # Espacio
            ''
        ])
        
        # Fila 4: Dirección (ocupa 2 columnas de datos)
        direccion_cell = Table([
            [Paragraph(candidato_direccion, field_value_style)],
            [Paragraph("<b>Dirección</b>", field_title_style)]
        ], colWidths=[info_column_width])
        direccion_cell.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
        ]))
        info_table_data.append([direccion_cell, '', '', '', ''])
        
        # Fila 5: Aspiración Salarial (si existe, ocupa 2 columnas de datos)
        if candidato_aspiracion:
            aspiracion_cell = Table([
                [Paragraph(f"${candidato_aspiracion:,.0f}", field_value_style)],
                [Paragraph("<b>Aspiración Salarial</b>", field_title_style)]
            ], colWidths=[info_column_width])
            aspiracion_cell.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
            ]))
            info_table_data.append([aspiracion_cell, '', '', '', ''])
    else:
        # Sin imagen: Valor | Título | Valor | Título
        # Fila 1: Documento y Email
        info_table_data.append([
            create_info_cell_reversed(info_candidato.numero_documento, "Documento"),
            create_info_cell_reversed(info_candidato.email, "Email"),
            '',  # Espacio
            ''   # Espacio
        ])
        
        # Fila 2: Teléfono y Género
        info_table_data.append([
            create_info_cell_reversed(info_candidato.telefono, "Teléfono"),
            create_info_cell_reversed(candidato_sexo_display, "Género"),
            '',  # Espacio
            ''   # Espacio
        ])
        
        # Fila 3: Fecha de Nacimiento y Ciudad
        info_table_data.append([
            create_info_cell_reversed(candidato_fecha_nac, "Fecha de Nacimiento"),
            create_info_cell_reversed(candidato_ciudad, "Ciudad"),
            '',  # Espacio
            ''   # Espacio
        ])
        
        # Fila 4: Dirección (ocupa 2 columnas de datos)
        direccion_cell = Table([
            [Paragraph(candidato_direccion, field_value_style)],
            [Paragraph("<b>Dirección</b>", field_title_style)]
        ], colWidths=[info_column_width])
        direccion_cell.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
        ]))
        info_table_data.append([direccion_cell, '', '', ''])
        
        # Fila 5: Aspiración Salarial (si existe, ocupa 2 columnas de datos)
        if candidato_aspiracion:
            aspiracion_cell = Table([
                [Paragraph(f"${candidato_aspiracion:,.0f}", field_value_style)],
                [Paragraph("<b>Aspiración Salarial</b>", field_title_style)]
            ], colWidths=[info_column_width])
            aspiracion_cell.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
            ]))
            info_table_data.append([aspiracion_cell, '', '', ''])
    
    # Calcular anchos de columnas
    if panel_candidato_img:
        # Con imagen: Valor/Título | Valor/Título | Espacio | Espacio | Imagen
        cell_col_width = info_column_width / 2
        info_table = Table(info_table_data, colWidths=[cell_col_width, cell_col_width, 0.1*inch, 0.1*inch, image_column_width])
        
        # Encontrar la fila donde está la imagen
        img_row = 0
        for i, row in enumerate(info_table_data):
            if len(row) > 4 and row[4] and row[4] != '':
                img_row = i
                break
        
        # Estilos de la tabla
        table_styles = [
            ('BACKGROUND', (0, 0), (-1, -1), color_bg_primary_opacity),  # Fondo rojo opacity 10
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (1, -1), 'LEFT'),
            ('ALIGN', (4, img_row), (4, img_row), 'CENTER'),  # Imagen centrada
            ('VALIGN', (4, img_row), (4, img_row), 'MIDDLE'), # Imagen centrada verticalmente
            ('SPAN', (4, img_row), (4, len(info_table_data) - 1)),  # Imagen ocupa desde su fila hasta el final
            # Bordes internos sutiles
            ('LINEBELOW', (0, 0), (1, -2), 0.5, colors.HexColor('#E9ECEF')),  # Líneas entre filas
            # Padding - mismo que el contenedor de la cabecera (12)
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]
        
        # SPAN para filas de ancho completo (perfil, dirección y aspiración)
        if candidato_perfil and candidato_perfil != 'No especificado':
            table_styles.append(('SPAN', (0, 0), (1, 0)))  # Perfil ocupa 2 columnas
        direccion_row = len(info_table_data) - (2 if candidato_aspiracion else 1)
        table_styles.append(('SPAN', (0, direccion_row), (1, direccion_row)))  # Dirección
        if candidato_aspiracion:
            aspiracion_row = len(info_table_data) - 1
            table_styles.append(('SPAN', (0, aspiracion_row), (1, aspiracion_row)))  # Aspiración
    else:
        # Sin imagen: Valor/Título | Valor/Título | Espacio | Espacio
        cell_col_width = info_column_width / 2
        info_table = Table(info_table_data, colWidths=[cell_col_width, cell_col_width, 0.1*inch, 0.1*inch])
        
        # Estilos de la tabla
        table_styles = [
            ('BACKGROUND', (0, 0), (-1, -1), color_bg_primary_opacity),  # Fondo rojo opacity 10
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (1, -1), 'LEFT'),
            # Bordes internos sutiles
            ('LINEBELOW', (0, 0), (1, -2), 0.5, colors.HexColor('#E9ECEF')),  # Líneas entre filas
            # Padding - mismo que el contenedor de la cabecera (12)
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]
        
        # SPAN para filas de ancho completo (sin imagen)
        if candidato_perfil and candidato_perfil != 'No especificado':
            table_styles.append(('SPAN', (0, 0), (1, 0)))  # Perfil ocupa 2 columnas
        direccion_row = len(info_table_data) - (2 if candidato_aspiracion else 1)
        table_styles.append(('SPAN', (0, direccion_row), (1, direccion_row)))  # Dirección
        if candidato_aspiracion:
            aspiracion_row = len(info_table_data) - 1
            table_styles.append(('SPAN', (0, aspiracion_row), (1, aspiracion_row)))  # Aspiración
    
    info_table.setStyle(TableStyle(table_styles))
    
    # Crear tabla con título centrado y contenido directamente (sin contenedor adicional)
    panel_content_table = Table([
        [Paragraph("Información Básica del Candidato", panel_title_style)],
        [info_table]
    ], colWidths=[header_width])
    
    panel_content_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.white),
        ('BACKGROUND', (0, 1), (0, 1), color_bg_primary_opacity),  # Fondo rojo opacity 10 para el contenido
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # Título centrado
        ('ALIGN', (0, 1), (0, 1), 'LEFT'),    # Contenido alineado a la izquierda
        ('BOTTOMPADDING', (0, 0), (0, 0), 12),
        ('TOPPADDING', (0, 1), (0, 1), 0),
        # Mismo padding que el contenedor de la cabecera (12)
        ('LEFTPADDING', (0, 0), (0, 0), 12),
        ('RIGHTPADDING', (0, 0), (0, 0), 12),
        ('LEFTPADDING', (0, 1), (0, 1), 0),
        ('RIGHTPADDING', (0, 1), (0, 1), 0),
        ('BOTTOMPADDING', (0, 1), (0, 1), 12),
        # Bordes del contenedor
        ('LINEBELOW', (0, 0), (0, 0), 1, color_primary),  # Línea debajo del título
        ('LINEABOVE', (0, 1), (0, 1), 0.5, colors.HexColor('#E9ECEF')),  # Línea sutil arriba del contenido
    ]))
    
    # Agregar directamente la tabla sin contenedor adicional
    elements.append(panel_content_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Construir el PDF
    doc.build(elements)
    
    # Obtener el valor del buffer y crear la respuesta HTTP
    pdf = buffer.getvalue()
    buffer.close()
    
    # Crear la respuesta HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="reporte_aplicacion_{asignacion_vacante.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    response.write(pdf)
    
    return response

