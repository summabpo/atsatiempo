"""
Hoja de vida en PDF: diseño compacto, sin identificadores internos (id, pk, *_id).
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

_SKIP_KEYS = frozenset(
    k.lower()
    for k in (
        'id',
        'pk',
        'candidato_id',
        'candidato_id_101',
        'vacante_id',
        'vacante_id_052',
        'estado_id',
        'estado_id_001',
        'usuario_id',
        'cliente_id',
        'aplicacion_id',
    )
)


def _is_skipped_key(key):
    k = str(key).lower()
    return k in _SKIP_KEYS or k.endswith('_id')


def _content_width():
    return A4[0] - 2.2 * cm


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


def _linea_fechas_experiencia(ex):
    """Texto de fechas solo si hay datos; si no hay fechas ni vigencia, None (no mostrar línea)."""
    fini_raw = ex.get('fecha_inicial')
    ffin_raw = ex.get('fecha_final')
    activo = ex.get('activo')
    if activo:
        if fini_raw:
            return f'{_fmt_date(fini_raw)} a Actualidad'
        return 'Actualidad'
    if not fini_raw and not ffin_raw:
        return None
    fini = _fmt_date(fini_raw) if fini_raw else None
    ffin = _fmt_date(ffin_raw) if ffin_raw else None
    if fini and ffin:
        return f'{fini} a {ffin}'
    if fini:
        return fini
    return ffin


def _parse_json_if_string(val):
    if isinstance(val, str):
        t = val.strip()
        if (t.startswith('{') and t.endswith('}')) or (t.startswith('[') and t.endswith(']')):
            try:
                return json.loads(t)
            except (json.JSONDecodeError, TypeError):
                pass
    return val


def _lineas_para_listado(val, prefer_nombre_value=False):
    val = _parse_json_if_string(val)
    if val is None or val == '' or val == [] or val == {}:
        return []
    if isinstance(val, str):
        parts = [p.strip() for p in val.replace('\r\n', '\n').split('\n')]
        parts = [p for p in parts if p]
        return parts if parts else [val]
    if isinstance(val, list):
        out = []
        for item in val:
            if prefer_nombre_value and isinstance(item, dict):
                n = item.get('nombre')
                if n is not None and str(n).strip():
                    out.append(str(n).strip())
                    continue
            if isinstance(item, dict):
                for k, v in item.items():
                    if _is_skipped_key(k):
                        continue
                    out.append(f'{k}: {v}')
            elif isinstance(item, (list, tuple)):
                out.extend(_lineas_para_listado(item, prefer_nombre_value=prefer_nombre_value))
            else:
                out.append(str(item))
        return out
    if isinstance(val, dict):
        out = []
        for k, v in sorted(val.items(), key=lambda x: str(x[0]).casefold()):
            if _is_skipped_key(k):
                continue
            if isinstance(v, (dict, list)):
                try:
                    out.append(f'{k}: {json.dumps(v, ensure_ascii=False)}')
                except (TypeError, ValueError):
                    out.append(f'{k}: {v}')
            else:
                out.append(f'{k}: {v}')
        return out
    return [str(val)]


def _skill_nombres_ordenados(skills):
    nombres = []
    seen = set()
    for s in skills or []:
        n = (s.get('nombre') or '').strip()
        if not n:
            continue
        k = n.casefold()
        if k not in seen:
            seen.add(k)
            nombres.append(n)
    nombres.sort(key=lambda x: x.casefold())
    return nombres


def _p(text, style):
    return Paragraph(escape(str(text or '')).replace('\n', '<br/>'), style)


def _abs_media_url(request, rel_url):
    if not rel_url:
        return None
    if rel_url.startswith('http'):
        return rel_url
    if request:
        return request.build_absolute_uri(rel_url)
    return rel_url


def _foto_flowable(candidato, request, width=2.6 * cm, height=2.6 * cm):
    if not candidato.imagen_perfil:
        return None
    try:
        pth = candidato.imagen_perfil.path
        if pth and os.path.exists(pth):
            return RLImage(pth, width=width, height=height, kind='proportional')
    except (ValueError, NotImplementedError, OSError):
        pass
    try:
        url = _abs_media_url(request, candidato.imagen_perfil.url)
        if not url:
            return None
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; TalentTray/1.0)'})
        with urllib.request.urlopen(req, timeout=20) as resp:
            return RLImage(BytesIO(resp.read()), width=width, height=height, kind='proportional')
    except Exception:
        return None


def _blank_avatar_flowable(width=2.6 * cm, height=2.6 * cm):
    path = finders.find('admin/images/blank.png') or os.path.join(
        settings.BASE_DIR, 'static', 'admin', 'images', 'blank.png'
    )
    if path and os.path.exists(path):
        try:
            return RLImage(path, width=width, height=height, kind='proportional')
        except Exception:
            pass
    return None


def _card(flow_rows, width, border_color, pad=6):
    t = Table(flow_rows, colWidths=[width])
    t.setStyle(
        TableStyle(
            [
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                ('BOX', (0, 0), (-1, -1), 0.35, border_color),
                ('LEFTPADDING', (0, 0), (-1, -1), pad),
                ('RIGHTPADDING', (0, 0), (-1, -1), pad),
                ('TOPPADDING', (0, 0), (-1, -1), pad),
                ('BOTTOMPADDING', (0, 0), (-1, -1), pad),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]
        )
    )
    return t


def _section_title(title, styles, color_primary, _color_dark, width, header_bg):
    """Cabecera alineada a las tarjetas de vacante/perfil (bg-primary bg-opacity-10)."""
    st = ParagraphStyle(
        'SecTitle',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        fontName='Helvetica-Bold',
        textColor=color_primary,
        spaceAfter=0,
    )
    p = Paragraph(escape(title), st)
    t = Table([[p]], colWidths=[width])
    t.setStyle(
        TableStyle(
            [
                ('BACKGROUND', (0, 0), (-1, -1), header_bg),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
                ('BOX', (0, 0), (-1, -1), 0.35, colors.HexColor('#dee2e6')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]
        )
    )
    return t


def _field_block(label, value, styles, w):
    """Etiqueta en mayúsculas + valor (como «Información de Contacto» en recruited_detail)."""
    st_l = ParagraphStyle(
        'FL',
        parent=styles['Normal'],
        fontSize=7.5,
        leading=10,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#6c757d'),
        spaceAfter=2,
        spaceBefore=0,
    )
    st_v = ParagraphStyle(
        'FV',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#212529'),
        spaceAfter=8,
    )
    lab = escape(str(label).upper())
    val = escape(str(value if value not in (None, '') else '—'))
    return Table(
        [
            [Paragraph(lab, st_l)],
            [Paragraph(val, st_v)],
        ],
        colWidths=[w],
    )


def _timeline_html(institution, lines):
    parts = [f"<b><font color='#212529'>{escape(institution)}</font></b>"]
    for line in lines:
        if line:
            parts.append(f'<font color="#6c757d" size="9">{escape(line)}</font>')
    return '<br/>'.join(parts)


def _timeline_block(content_flowable, inner_w, primary, border):
    """Bloque con acento izquierdo (similar a la línea de tiempo en recruited_detail)."""
    t = Table([[content_flowable]], colWidths=[inner_w])
    t.setStyle(
        TableStyle(
            [
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                ('LINEBEFORE', (0, 0), (-1, -1), 3.5, primary),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('BOX', (0, 0), (-1, -1), 0.35, border),
            ]
        )
    )
    return t


def _skills_grid(names, w, primary, bg, border, styles):
    if not names:
        return Paragraph('—', ParagraphStyle('e', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#6c757d')))
    cols = 4
    cw = w / cols
    ct = ParagraphStyle(
        'ch',
        parent=styles['Normal'],
        fontSize=7.5,
        leading=9,
        fontName='Helvetica-Bold',
        textColor=primary,
        alignment=TA_CENTER,
    )
    rows_out = []
    i = 0
    while i < len(names):
        row = []
        for _ in range(cols):
            if i < len(names):
                cell = Table([[Paragraph(escape(names[i]), ct)]], colWidths=[max(cw - 6, 18)])
                cell.setStyle(
                    TableStyle(
                        [
                            ('BACKGROUND', (0, 0), (-1, -1), bg),
                            ('BOX', (0, 0), (-1, -1), 0.35, border),
                            ('TOPPADDING', (0, 0), (-1, -1), 2),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                            ('LEFTPADDING', (0, 0), (-1, -1), 3),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                        ]
                    )
                )
                row.append(cell)
                i += 1
            else:
                row.append(Paragraph('', styles['Normal']))
        rows_out.append(row)
    return Table(rows_out, colWidths=[cw, cw, cw, cw])


def _bullets(raw, body_left, bg, border, w, prefer_nombre_value=False):
    lines = _lineas_para_listado(raw, prefer_nombre_value=prefer_nombre_value)
    ps = ParagraphStyle('b', parent=body_left, fontSize=8.5, leading=10, leftIndent=4, spaceAfter=0)
    if not lines:
        return Paragraph('—', ps)
    rows = [[Paragraph(f'• {escape(x)}', ps)] for x in lines]
    t = Table(rows, colWidths=[w])
    t.setStyle(
        TableStyle(
            [
                ('BACKGROUND', (0, 0), (-1, -1), bg),
                ('BOX', (0, 0), (-1, -1), 0.35, border),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]
        )
    )
    return t


def build_hoja_vida_pdf(request, candidato, info_detalle, vacante_titulo=None):
    buffer = BytesIO()
    w = _content_width()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.1 * cm,
        leftMargin=1.1 * cm,
        topMargin=0.6 * cm,
        bottomMargin=0.65 * cm,
    )
    styles = getSampleStyleSheet()
    primary = colors.HexColor('#B10022')
    dark = colors.HexColor('#212529')
    gray = colors.HexColor('#6c757d')
    border = colors.HexColor('#dee2e6')
    bg_soft = colors.HexColor('#F7E6E9')
    header_bg = bg_soft  # mismo criterio que card-header bg-primary bg-opacity-10 en la UI
    inner = w - 12
    half = (inner - 8) / 2

    body = ParagraphStyle(
        'B',
        parent=styles['Normal'],
        fontSize=9,
        leading=11.5,
        alignment=TA_JUSTIFY,
        textColor=dark,
    )
    body_left = ParagraphStyle('BL', parent=body, alignment=TA_LEFT)
    foot = ParagraphStyle('F', parent=styles['Normal'], fontSize=6.5, textColor=gray, alignment=TA_CENTER, spaceBefore=4)

    elements = []
    nombre = candidato.nombre_completo() or info_detalle.get('nombre_completo') or 'Candidato'

    foto = _foto_flowable(candidato, request) or _blank_avatar_flowable()
    fw = Table([[foto]], colWidths=[2.6 * cm])
    fw.setStyle(
        TableStyle(
            [
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('BOX', (0, 0), (-1, -1), 1, border),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]
        )
    )
    nm = ParagraphStyle('N', parent=styles['Normal'], fontSize=14, fontName='Helvetica-Bold', textColor=dark, leading=17)
    sub = ParagraphStyle('S', parent=styles['Normal'], fontSize=8.5, textColor=gray, leading=11)
    vac_st = ParagraphStyle('V', parent=styles['Normal'], fontSize=8.5, textColor=primary, fontName='Helvetica-Bold', leading=11)
    rc = [[Paragraph(escape(nombre), nm)], [Paragraph('Hoja de vida', sub)]]
    if vacante_titulo:
        rc.append([Paragraph(escape(str(vacante_titulo)), vac_st)])
    rt = Table(rc, colWidths=[inner - 2.75 * cm])
    head = Table([[fw, rt]], colWidths=[2.75 * cm, inner - 2.75 * cm])
    head.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    elements.append(_card([[head]], w, border, pad=6))
    elements.append(Spacer(1, 0.1 * cm))

    doc_n = escape(str(info_detalle.get('numero_documento') or '—'))
    em = escape(str(info_detalle.get('email') or '—'))
    tel = escape(str(info_detalle.get('telefono') or '—'))
    strip_st = ParagraphStyle('Strip', parent=styles['Normal'], alignment=TA_CENTER, textColor=colors.white, leading=12)
    strip = Table(
        [
            [
                Paragraph(
                    f'<font name="Helvetica-Bold" size="7">DOCUMENTO</font><br/>'
                    f'<font name="Helvetica" size="9">{doc_n}</font>',
                    strip_st,
                ),
                Paragraph(
                    f'<font name="Helvetica-Bold" size="7">CORREO</font><br/>'
                    f'<font name="Helvetica" size="9">{em}</font>',
                    strip_st,
                ),
                Paragraph(
                    f'<font name="Helvetica-Bold" size="7">TELÉFONO</font><br/>'
                    f'<font name="Helvetica" size="9">{tel}</font>',
                    strip_st,
                ),
            ]
        ],
        colWidths=[w / 3, w / 3, w / 3],
    )
    strip.setStyle(
        TableStyle(
            [
                ('BACKGROUND', (0, 0), (-1, -1), primary),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
                ('LINEAFTER', (0, 0), (0, 0), 0.5, colors.HexColor('#E88496')),
                ('LINEAFTER', (1, 0), (1, 0), 0.5, colors.HexColor('#E88496')),
            ]
        )
    )
    elements.append(strip)
    elements.append(Spacer(1, 0.1 * cm))

    datos_rows = [
        [_section_title('Datos personales', styles, primary, dark, inner, header_bg)],
        [
            Table(
                [
                    [
                        _field_block('Género', info_detalle.get('sexo'), styles, half),
                        _field_block('Fecha de nacimiento', _fmt_date(info_detalle.get('fecha_nacimiento')), styles, half),
                    ],
                    [
                        _field_block('Ubicación', f"{info_detalle.get('ciudad') or '—'}, Colombia", styles, half),
                        _field_block('Edad', str(candidato.edad) if candidato.edad is not None else '—', styles, half),
                    ],
                ],
                colWidths=[half, half],
            )
        ],
        [_field_block('Dirección', (candidato.direccion or '').strip() or '—', styles, inner)],
    ]
    if candidato.aspiracion_salarial is not None:
        datos_rows.append(
            [_field_block('Aspiración salarial', f"${candidato.aspiracion_salarial:,.0f}".replace(',', '.'), styles, inner)]
        )
    elements.append(_card(datos_rows, w, border, pad=6))
    elements.append(Spacer(1, 0.1 * cm))

    if (candidato.perfil or '').strip():
        elements.append(
            _card(
                [
                    [_section_title('Perfil profesional', styles, primary, dark, inner, header_bg)],
                    [_p(candidato.perfil.strip(), body)],
                ],
                w,
                border,
                pad=6,
            )
        )
        elements.append(Spacer(1, 0.1 * cm))

    educaciones = info_detalle.get('educacion') or []
    edu_rows = [[_section_title('Formación académica', styles, primary, dark, inner, header_bg)]]
    if not educaciones:
        edu_rows.append([Paragraph('<font color="#6c757d">No se registran estudios.</font>', body_left)])
    else:
        for i, edu in enumerate(educaciones):
            tit = edu.get('institucion') or ''
            ln = []
            if edu.get('titulo') or edu.get('tipo_estudio'):
                ln.append(f"{edu.get('titulo') or ''} ({edu.get('tipo_estudio') or ''})".strip())
            ln.append(f"{_fmt_date(edu.get('fecha_inicial'))} — {_fmt_date(edu.get('fecha_final'))}")
            if edu.get('carrera'):
                ln.append(str(edu['carrera']))
            if edu.get('fortalezas'):
                ln.append(f"Fortalezas: {edu['fortalezas']}")
            para = Paragraph(_timeline_html(tit, ln), body_left)
            edu_rows.append([_timeline_block(para, inner, primary, border)])
            if i < len(educaciones) - 1:
                edu_rows.append([Spacer(1, 0.1 * cm)])

    elements.append(_card(edu_rows, w, border, pad=6))
    elements.append(Spacer(1, 0.1 * cm))

    experiencias = info_detalle.get('experiencia') or []
    exp_rows = [[_section_title('Experiencia laboral', styles, primary, dark, inner, header_bg)]]
    if not experiencias:
        exp_rows.append([Paragraph('<font color="#6c757d">No se registran experiencias laborales.</font>', body_left)])
    else:
        for i, ex in enumerate(experiencias):
            ent = ex.get('entidad') or ''
            sec = ex.get('sector') or ''
            head = ent + (f' ({sec})' if sec else '')
            lines = []
            if ex.get('cargo'):
                lines.append(str(ex['cargo']))
            fecha_txt = _linea_fechas_experiencia(ex)
            if fecha_txt:
                lines.append(fecha_txt)
            if ex.get('logro'):
                lines.append(str(ex['logro']))
            para = Paragraph(_timeline_html(head, lines), body_left)
            exp_rows.append([_timeline_block(para, inner, primary, border)])
            if i < len(experiencias) - 1:
                exp_rows.append([Spacer(1, 0.1 * cm)])

    elements.append(_card(exp_rows, w, border, pad=6))
    elements.append(Spacer(1, 0.1 * cm))

    skills = _skill_nombres_ordenados(info_detalle.get('skills') or [])
    elements.append(
        _card(
            [
                [_section_title('Habilidades', styles, primary, dark, inner, header_bg)],
                [_skills_grid(skills, inner, primary, bg_soft, border, styles)],
            ],
            w,
            border,
            pad=6,
        )
    )
    elements.append(Spacer(1, 0.1 * cm))

    if candidato.idiomas:
        id_lines = _lineas_para_listado(candidato.idiomas)
        id_txt = '\n'.join(id_lines) if id_lines else '—'
        elements.append(
            _card(
                [
                    [_section_title('Idiomas', styles, primary, dark, inner, header_bg)],
                    [_p(id_txt, body_left)],
                ],
                w,
                border,
                pad=6,
            )
        )
        elements.append(Spacer(1, 0.1 * cm))

    if candidato.motivadores:
        elements.append(
            _card(
                [
                    [_section_title('Motivadores', styles, primary, dark, inner, header_bg)],
                    [_bullets(candidato.motivadores, body_left, bg_soft, border, inner, prefer_nombre_value=True)],
                ],
                w,
                border,
                pad=6,
            )
        )
        elements.append(Spacer(1, 0.1 * cm))

    if candidato.fit_cultural:
        elements.append(
            _card(
                [
                    [_section_title('Fit cultural', styles, primary, dark, inner, header_bg)],
                    [_bullets(candidato.fit_cultural, body_left, bg_soft, border, inner, prefer_nombre_value=True)],
                ],
                w,
                border,
                pad=6,
            )
        )
        elements.append(Spacer(1, 0.08 * cm))

    logo = finders.find('admin/images/landing/logo-talent-tray.png') or os.path.join(
        settings.BASE_DIR, 'static', 'admin', 'images', 'landing', 'logo-talent-tray.png'
    )
    if logo and os.path.exists(logo):
        try:
            elements.append(RLImage(logo, width=1.4 * cm, height=0.45 * cm, kind='proportional'))
        except Exception:
            pass

    elements.append(
        Paragraph(
            f'Generado el {datetime.now().strftime("%d/%m/%Y %H:%M")} · Talent Tray',
            foot,
        )
    )

    doc.build(elements)
    buffer.seek(0)
    return buffer
