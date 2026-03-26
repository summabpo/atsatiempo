"""
PDF de hoja de vida estilo CV convencional: cabecera con foto, tonos rojos (#B10022),
secciones claras y orden profesional (ReportLab).
"""
import json
import os
import re
import urllib.request
from datetime import datetime
from io import BytesIO
from xml.sax.saxutils import escape

from django.conf import settings
from django.contrib.staticfiles import finders
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def safe_filename_part(text):
    if not text:
        return 'candidato'
    s = re.sub(r'[^\w\s-]', '', str(text), flags=re.UNICODE)
    s = re.sub(r'[-\s]+', '_', s).strip('_')
    return s[:80] or 'candidato'


def _fmt_date(d):
    if not d:
        return '—'
    if hasattr(d, 'strftime'):
        return d.strftime('%d/%m/%Y')
    return str(d)


def _json_readable(val):
    if val is None:
        return None
    if isinstance(val, (dict, list)):
        try:
            return json.dumps(val, ensure_ascii=False, indent=2)
        except (TypeError, ValueError):
            return str(val)
    return str(val)


def _p(text, style):
    t = str(text or '')
    return Paragraph(escape(t).replace('\n', '<br/>'), style)


def _abs_media_url(request, rel_url):
    if not rel_url:
        return None
    if rel_url.startswith('http'):
        return rel_url
    if request:
        return request.build_absolute_uri(rel_url)
    return rel_url


def _foto_flowable(candidato, request, width=3.4 * cm, height=3.4 * cm):
    """Foto del candidato: archivo local o descarga por URL (S3 / media)."""
    if not candidato.imagen_perfil:
        return None
    try:
        pth = candidato.imagen_perfil.path
        if pth and os.path.exists(pth):
            return RLImage(pth, width=width, height=height, kind='proportional')
    except (ValueError, NotImplementedError, OSError):
        pass
    try:
        url = candidato.imagen_perfil.url
        url = _abs_media_url(request, url)
        if not url:
            return None
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; TalentTray/1.0)'})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = BytesIO(resp.read())
        return RLImage(data, width=width, height=height, kind='proportional')
    except Exception:
        return None


def _blank_avatar_flowable(width=3.4 * cm, height=3.4 * cm):
    path = finders.find('admin/images/blank.png')
    if not path:
        path = os.path.join(settings.BASE_DIR, 'static', 'admin', 'images', 'blank.png')
    if path and os.path.exists(path):
        try:
            return RLImage(path, width=width, height=height, kind='proportional')
        except Exception:
            pass
    return None


def _section_bar_title(title, styles, color_primary, color_bg_bar):
    """Título de sección con barra roja lateral (estilo plantillas)."""
    st = ParagraphStyle(
        'SecTitle',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        textColor=color_primary,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        spaceAfter=0,
        spaceBefore=0,
    )
    p = Paragraph(escape(title.upper()), st)
    t = Table(
        [['', p]],
        colWidths=[0.4 * cm, 16.4 * cm],
    )
    t.setStyle(
        TableStyle(
            [
                ('BACKGROUND', (0, 0), (0, 0), color_primary),
                ('BACKGROUND', (1, 0), (1, 0), color_bg_bar),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ]
        )
    )
    return t


def build_hoja_vida_pdf(request, candidato, info_detalle, vacante_titulo=None):
    """
    request: para resolver URL absoluta de la imagen de perfil.
    candidato: Can101Candidato.
    info_detalle: dict de buscar_candidato().
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.1 * cm,
        bottomMargin=1.2 * cm,
    )
    styles = getSampleStyleSheet()

    color_primary = colors.HexColor('#B10022')
    color_dark = colors.HexColor('#212529')
    color_gray = colors.HexColor('#6c757d')
    color_border = colors.HexColor('#dee2e6')
    color_bg_light = colors.HexColor('#F7E6E9')
    color_bg_bar = colors.HexColor('#FDF8F9')

    style_name = ParagraphStyle(
        'Nombre',
        parent=styles['Normal'],
        fontSize=20,
        textColor=color_dark,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        spaceAfter=2,
        leading=24,
    )
    style_tagline = ParagraphStyle(
        'Tagline',
        parent=styles['Normal'],
        fontSize=11,
        textColor=color_gray,
        alignment=TA_LEFT,
        spaceAfter=6,
    )
    style_vac = ParagraphStyle(
        'Vacante',
        parent=styles['Normal'],
        fontSize=9,
        textColor=color_primary,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        spaceAfter=0,
    )
    body = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY,
        textColor=color_dark,
        spaceAfter=6,
    )
    body_left = ParagraphStyle(
        'BodyLeft',
        parent=body,
        alignment=TA_LEFT,
    )
    label_cell = ParagraphStyle(
        'LabelCell',
        parent=styles['Normal'],
        fontSize=9,
        textColor=color_gray,
        fontName='Helvetica-Bold',
    )
    footer = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=7,
        textColor=color_gray,
        alignment=TA_CENTER,
        spaceBefore=12,
    )

    elements = []
    nombre = candidato.nombre_completo() or info_detalle.get('nombre_completo') or 'Candidato'

    foto = _foto_flowable(candidato, request)
    if not foto:
        foto = _blank_avatar_flowable()

    # Bloque derecho: nombre + línea + vacante
    head_right = [
        Paragraph(escape(nombre), style_name),
        Paragraph('Candidato · Hoja de vida', style_tagline),
    ]
    if vacante_titulo:
        head_right.append(Paragraph(f'Postulación: {escape(str(vacante_titulo))}', style_vac))

    if foto:
        foto_cell = foto
    else:
        foto_cell = Paragraph(' ', body_left)

    # Marco foto: fondo rojo muy suave + borde
    foto_wrap = Table(
        [[foto_cell]],
        colWidths=[3.6 * cm],
    )
    foto_wrap.setStyle(
        TableStyle(
            [
                ('BACKGROUND', (0, 0), (-1, -1), color_bg_light),
                ('BOX', (0, 0), (-1, -1), 1.5, color_primary),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ]
        )
    )

    head_right_tbl = Table([[h] for h in head_right], colWidths=[12.4 * cm])
    head_right_tbl.setStyle(
        TableStyle(
            [
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ]
        )
    )

    header_main = Table(
        [[foto_wrap, head_right_tbl]],
        colWidths=[4.2 * cm, 12.4 * cm],
    )
    header_main.setStyle(
        TableStyle(
            [
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ]
        )
    )
    elements.append(header_main)
    elements.append(Spacer(1, 0.35 * cm))

    # Franja de contacto (como tarjeta del template)
    c_doc = escape(str(info_detalle.get('numero_documento') or '—'))
    c_mail = escape(str(info_detalle.get('email') or '—'))
    c_tel = escape(str(info_detalle.get('telefono') or '—'))
    contact_inner = Table(
        [
            [
                Paragraph(f'<b><font color="#ffffff">Documento</font></b><br/><font size="9" color="#ffffff">{c_doc}</font>', ParagraphStyle('c1', parent=styles['Normal'], alignment=TA_CENTER)),
                Paragraph(f'<b><font color="#ffffff">Correo</font></b><br/><font size="9" color="#ffffff">{c_mail}</font>', ParagraphStyle('c2', parent=styles['Normal'], alignment=TA_CENTER)),
                Paragraph(f'<b><font color="#ffffff">Teléfono</font></b><br/><font size="9" color="#ffffff">{c_tel}</font>', ParagraphStyle('c3', parent=styles['Normal'], alignment=TA_CENTER)),
            ]
        ],
        colWidths=[5.4 * cm, 5.4 * cm, 5.4 * cm],
    )
    contact_inner.setStyle(
        TableStyle(
            [
                ('BACKGROUND', (0, 0), (-1, -1), color_primary),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ]
        )
    )
    elements.append(contact_inner)
    elements.append(Spacer(1, 0.45 * cm))

    # Datos personales en tabla limpia (CV convencional)
    elements.append(_section_bar_title('Datos personales', styles, color_primary, color_bg_bar))
    elements.append(Spacer(1, 0.25 * cm))

    pers_rows = [
        ('Sexo', info_detalle.get('sexo') or '—'),
        ('Fecha de nacimiento', _fmt_date(info_detalle.get('fecha_nacimiento'))),
        ('Ciudad', f"{info_detalle.get('ciudad') or '—'}, Colombia"),
        ('Dirección', (candidato.direccion or '').strip() or '—'),
        ('Edad', str(candidato.edad) if candidato.edad is not None else '—'),
    ]
    if candidato.aspiracion_salarial is not None:
        pers_rows.append(
            ('Aspiración salarial', f"${candidato.aspiracion_salarial:,.0f}".replace(',', '.'))
        )
    pers_rows.append(('Completitud del perfil (ATS)', f"{info_detalle.get('porcentaje')}%"))

    dat_tbl = []
    for label, val in pers_rows:
        dat_tbl.append(
            [
                Paragraph(f'<font color="#6c757d">{escape(label)}</font>', label_cell),
                Paragraph(escape(str(val)), body_left),
            ]
        )
    t_dat = Table(dat_tbl, colWidths=[4.5 * cm, 12.1 * cm])
    t_dat.setStyle(
        TableStyle(
            [
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LINEBELOW', (0, 0), (-1, -2), 0.25, color_border),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]
        )
    )
    elements.append(t_dat)
    elements.append(Spacer(1, 0.35 * cm))

    # Perfil profesional
    if (candidato.perfil or '').strip():
        elements.append(_section_bar_title('Perfil profesional', styles, color_primary, color_bg_bar))
        elements.append(Spacer(1, 0.2 * cm))
        elements.append(_p(candidato.perfil.strip(), body))
        elements.append(Spacer(1, 0.25 * cm))

    # Experiencia antes que educación (orden típico CV)
    experiencias = info_detalle.get('experiencia') or []
    elements.append(_section_bar_title('Experiencia laboral', styles, color_primary, color_bg_bar))
    elements.append(Spacer(1, 0.25 * cm))
    if not experiencias:
        elements.append(Paragraph('No se registra experiencia laboral.', body_left))
    else:
        for ex in experiencias:
            ent = ex.get('entidad') or ''
            sec = ex.get('sector') or ''
            head = f"<b><font color='#B10022'>{escape(ent)}</font></b>"
            if sec:
                head += f" <font color='#6c757d'>· {escape(sec)}</font>"
            lines = [head]
            if ex.get('cargo'):
                lines.append(f"<b>{escape(str(ex['cargo']))}</b>")
            fini = _fmt_date(ex.get('fecha_inicial'))
            ffin = _fmt_date(ex.get('fecha_final'))
            if ex.get('activo'):
                ffin = 'Actualidad'
            lines.append(f"<font color='#6c757d' size='9'>{escape(f'{fini} — {ffin}')}</font>")
            if ex.get('logro'):
                lines.append(f"{escape(str(ex['logro']))}")
            elements.append(Paragraph('<br/>'.join(lines), body_left))
            elements.append(Spacer(1, 0.2 * cm))

    elements.append(Spacer(1, 0.15 * cm))
    educaciones = info_detalle.get('educacion') or []
    elements.append(_section_bar_title('Formación académica', styles, color_primary, color_bg_bar))
    elements.append(Spacer(1, 0.25 * cm))
    if not educaciones:
        elements.append(Paragraph('No se registran estudios.', body_left))
    else:
        for edu in educaciones:
            bloque = []
            bloque.append(f"<b><font color='#B10022'>{escape(edu.get('institucion') or '')}</font></b>")
            titulo = edu.get('titulo') or ''
            tipo = edu.get('tipo_estudio') or ''
            if titulo or tipo:
                bloque.append(f"{escape(titulo)} <font color='#6c757d'>({escape(tipo)})</font>".strip())
            fechas = f"{_fmt_date(edu.get('fecha_inicial'))} — {_fmt_date(edu.get('fecha_final'))}"
            bloque.append(f"<font color='#6c757d' size='9'>{escape(fechas)}</font>")
            if edu.get('carrera'):
                bloque.append(escape(str(edu['carrera'])))
            if edu.get('fortalezas'):
                bloque.append(f"<i>Fortalezas:</i> {escape(str(edu['fortalezas']))}")
            elements.append(Paragraph('<br/>'.join(bloque), body_left))
            elements.append(Spacer(1, 0.2 * cm))

    elements.append(Spacer(1, 0.1 * cm))
    skills = info_detalle.get('skills') or []
    elements.append(_section_bar_title('Habilidades y competencias', styles, color_primary, color_bg_bar))
    elements.append(Spacer(1, 0.25 * cm))
    if not skills:
        elements.append(Paragraph('No se registran habilidades.', body_left))
    else:
        chips = []
        for s in skills:
            if s.get('nombre'):
                chips.append(f"{escape(s['nombre'])} ({escape(s.get('nivel', ''))})")
        skill_para = ' &nbsp;·&nbsp; '.join(chips)
        skills_tbl = Table([[Paragraph(skill_para, body_left)]], colWidths=[16.6 * cm])
        skills_tbl.setStyle(
            TableStyle(
                [
                    ('BACKGROUND', (0, 0), (-1, -1), color_bg_light),
                    ('BOX', (0, 0), (-1, -1), 0.5, color_border),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ]
            )
        )
        elements.append(skills_tbl)

    extra_blocks = []
    if candidato.idiomas:
        extra_blocks.append(('Idiomas', _json_readable(candidato.idiomas)))
    if candidato.motivadores:
        extra_blocks.append(('Motivadores', _json_readable(candidato.motivadores)))
    if candidato.fit_cultural:
        extra_blocks.append(('Fit cultural', _json_readable(candidato.fit_cultural)))

    for title, content in extra_blocks:
        elements.append(Spacer(1, 0.3 * cm))
        elements.append(_section_bar_title(title, styles, color_primary, color_bg_bar))
        elements.append(Spacer(1, 0.2 * cm))
        elements.append(_p(content, body))

    logo_path = finders.find('admin/images/logo-icon.png')
    if not logo_path:
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'admin', 'images', 'logo-icon.png')
    if logo_path and os.path.exists(logo_path):
        try:
            elements.append(Spacer(1, 0.5 * cm))
            elements.append(RLImage(logo_path, width=2 * cm, height=0.65 * cm, kind='proportional'))
        except Exception:
            pass

    elements.append(
        Paragraph(
            f"Documento generado el {datetime.now().strftime('%d/%m/%Y %H:%M')} · Talent Tray · ATS",
            footer,
        )
    )

    doc.build(elements)
    buffer.seek(0)
    return buffer
