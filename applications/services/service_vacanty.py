from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, Count, Q, Value, Case, When, CharField
from django.db.models.functions import Concat


#consulta vacantes
from applications.vacante.models import Cli052Vacante


def query_vacanty_all():
    return  Cli052Vacante.objects.select_related(
        'perfil_vacante',
        'cargo',
        'asignacion_cliente_id_064__id_cliente_asignado',
        'usuario_asignado'
    ).annotate(
        nombre_completo=Concat(
            F('usuario_asignado__primer_nombre'), Value(' '),
            F('usuario_asignado__segundo_nombre'), Value(' '),
            F('usuario_asignado__primer_apellido'), Value(' '),
            F('usuario_asignado__segundo_apellido')
        ),
        vacante_estado = Case(
            When(estado_vacante=1, then=Value('Activa')),
            When(estado_vacante=2, then=Value('En Proceso')),
            When(estado_vacante=3, then=Value('Finalizada')),
            When(estado_vacante=4, then=Value('Cancelada')),
            output_field=CharField()  # Definir el tipo de campo de salida
        ),
        total_aplicaciones=Count('aplicaciones'),
        aplicadas=Count('aplicaciones', filter=Q(aplicaciones__estado_aplicacion=1)),
        en_proceso=Count('aplicaciones', filter=Q(aplicaciones__estado_aplicacion__in=[2, 3, 5, 6])),
        finalizadas=Count('aplicaciones', filter=Q(aplicaciones__estado_aplicacion=9)),
        canceladas=Count('aplicaciones', filter=Q(aplicaciones__estado_aplicacion=10)),
        desistidos=Count('aplicaciones', filter=Q(aplicaciones__estado_aplicacion=11)),
        no_aptas=Count('aplicaciones', filter=Q(aplicaciones__estado_aplicacion=12)),
        seleccionados=Count('aplicaciones', filter=Q(aplicaciones__estado_aplicacion=8)),
    )

def query_vacanty_detail():
    return  Cli052Vacante.objects.select_related(
        'perfil_vacante',
        'cargo',
        'asignacion_cliente_id_064__id_cliente_asignado',
        'usuario_asignado'
    )

def query_vacanty_with_skills_and_details():
    return Cli052Vacante.objects.select_related(
        'perfil_vacante',
        'perfil_vacante__profesion_estudio',
        'perfil_vacante__lugar_trabajo',
        'perfil_vacante__estado',
        'cargo',
        'asignacion_cliente_id_064',
        'asignacion_cliente_id_064__id_cliente_asignado',
        'usuario_asignado',
        'estado_id_001'
    ).prefetch_related(
        'soft_skills_id_053',
        'hard_skills_id_054',
        'perfil_vacante__profesion_estudio',
        'perfil_vacante__lugar_trabajo',
        'perfil_vacante__estado',
        'perfil_vacante',
        'cli074asignacionfunciones_set__funcion_responsabilidad'
    )

def get_vacanty_questions(vacante_id):
    try:
        vacante = Cli052Vacante.objects.select_related('perfil_vacante').get(id=vacante_id)
    except Cli052Vacante.DoesNotExist:
        return None

    preguntas = []
    preguntas_set = set()  # Para evitar duplicados

    perfil = vacante.perfil_vacante

    # Experiencia Laboral
    experiencia_laboral = getattr(perfil, 'experiencia_laboral', None)
    if experiencia_laboral:
        for exp in experiencia_laboral:
            pregunta_texto = (
                f"¿Cuenta con al menos {exp.get('tiempo_experiencia', '')} años de experiencia en "
                f"{exp.get('experiencia_especifica', '')}?"
            )
            pregunta_key = ("experiencia", pregunta_texto)
            if pregunta_key not in preguntas_set:
                preguntas.append({
                    "bloque": exp.get('bloque', 1),
                    "tipo_pregunta": "experiencia",
                    "pregunta": pregunta_texto,
                    "valores_relacionados": None
                })
                preguntas_set.add(pregunta_key)

    # Idiomas
    idiomas = getattr(perfil, 'idiomas', None)
    if idiomas:
        IDIOMA_CHOICES_MAP = {
            'EN': 'Inglés',
            'ES': 'Español',
            'FR': 'Francés',
            'DE': 'Alemán',
            'IT': 'Italiano',
            'PT': 'Portugués',
            'ZH': 'Chino',
            'JA': 'Japonés',
            'RU': 'Ruso',
            'AR': 'Árabe',
        }
        for idioma in idiomas:
            idioma_sigla = idioma.get('idioma', '')
            idioma_completo = IDIOMA_CHOICES_MAP.get(idioma_sigla, idioma_sigla)
            pregunta_idioma = (
                f"¿Cuenta con nivel {idioma.get('nivel', '')} en el idioma {idioma_completo}?"
            )
            pregunta_key = ("idioma", pregunta_idioma)
            if pregunta_key not in preguntas_set:
                preguntas.append({
                    "bloque": idioma.get('bloque', 2),
                    "tipo_pregunta": "idioma",
                    "pregunta": pregunta_idioma,
                    "valores_relacionados": None
                })
                preguntas_set.add(pregunta_key)

    # Estudios Complementarios
    estudios_complementarios = getattr(perfil, 'estudios_complementarios', None)
    if estudios_complementarios:
        for estudio in estudios_complementarios:
            pregunta_estudio = (
                f"¿Cuenta con estudios complementarios en {estudio.get('nombre', '')}?"
            )
            pregunta_key = ("estudio_complementario", pregunta_estudio)
            if pregunta_key not in preguntas_set:
                preguntas.append({
                    "bloque": estudio.get('bloque', 4),
                    "tipo_pregunta": "estudio_complementario",
                    "pregunta": pregunta_estudio,
                    "valores_relacionados": None
                })
                preguntas_set.add(pregunta_key)

    # Tipo Profesión V2
    tipo_profesion = getattr(perfil, 'tipo_profesion', None)
    if tipo_profesion:
        nivel_estudio = getattr(perfil, 'nivel_estudio', None)
        nivel_estudio_display = dict(getattr(perfil._meta.get_field('nivel_estudio'), 'choices', [])).get(nivel_estudio, nivel_estudio)
        if tipo_profesion == 'E':
            profesion_estudio = getattr(perfil, 'profesion_estudio', None)
            pregunta_profesion = (
                f"¿Cuenta con el nivel de estudio {nivel_estudio_display} en la profesión {profesion_estudio}?"
            )
            pregunta_key = ("profesion_especifica", pregunta_profesion)
            if pregunta_key not in preguntas_set:
                preguntas.append({
                    "bloque": 1,
                    "tipo_pregunta": "profesion_especifica",
                    "pregunta": pregunta_profesion,
                    "valores_relacionados": {
                        "nivel_estudio": nivel_estudio_display,
                        "profesion": profesion_estudio
                    }
                })
                preguntas_set.add(pregunta_key)
        elif tipo_profesion == 'G':
            grupo_profesiones = getattr(perfil, 'grupo_profesiones', None)
            if grupo_profesiones:
                pregunta_grupo = (
                    f"¿Cuenta con el nivel de estudio {nivel_estudio_display} y pertenece a alguno de los siguientes grupos de profesiones: {', '.join(grupo_profesiones)}?"
                )
                pregunta_key = ("profesion_grupo", pregunta_grupo)
                if pregunta_key not in preguntas_set:
                    preguntas.append({
                        "bloque": 2,
                        "tipo_pregunta": "profesion_grupo",
                        "pregunta": pregunta_grupo,
                        "valores_relacionados": {
                            "nivel_estudio": nivel_estudio_display,
                            "grupos": grupo_profesiones
                        }
                    })
                    preguntas_set.add(pregunta_key)
        elif tipo_profesion == 'L':
            listado_profesiones = getattr(perfil, 'profesion_estudio_listado', None)
            if listado_profesiones:
                nombres_profesiones = []
                valores_relacionados = []
                if isinstance(listado_profesiones, str):
                    try:
                        import json
                        listado_profesiones = json.loads(listado_profesiones)
                    except Exception as e:
                        print(f"Error parsing JSON: {e}")
                        listado_profesiones = []
                if isinstance(listado_profesiones, list) and listado_profesiones and isinstance(listado_profesiones[0], dict):
                    for prof in listado_profesiones:
                        nombre = prof.get('value', '')
                        id_prof = prof.get('id', None)
                        nombres_profesiones.append(nombre)
                        valores_relacionados.append({"value": nombre, "id": id_prof})
                elif isinstance(listado_profesiones, list):
                    nombres_profesiones = listado_profesiones
                    valores_relacionados = [{"value": nombre, "id": None} for nombre in nombres_profesiones]
                if nombres_profesiones:
                    pregunta_listado = (
                        f"¿Cuenta con el título en alguna de las siguientes profesiones: {', '.join(nombres_profesiones)}?"
                    )
                    pregunta_key = ("profesion", pregunta_listado)
                    if pregunta_key not in preguntas_set:
                        preguntas.append({
                            "bloque": 3,
                            "tipo_pregunta": "profesion",
                            "pregunta": pregunta_listado,
                            "valores_relacionados": valores_relacionados
                        })
                        preguntas_set.add(pregunta_key)

    # Estudios complementarios (otra posible fuente, diferente campo)
    estudios_complementarios_alt = getattr(perfil, 'estudio_complementario', None)
    if estudios_complementarios_alt:
        import json
        estudios = []
        if isinstance(estudios_complementarios_alt, list):
            estudios = estudios_complementarios_alt
        elif isinstance(estudios_complementarios_alt, str):
            try:
                estudios = json.loads(estudios_complementarios_alt)
            except Exception:
                estudios = []
        if estudios:
            for estudio in estudios:
                nombre = estudio.get('estudio') or estudio.get('nombre') or estudio.get('value') or ''
                certificado = estudio.get('certificado') or estudio.get('tiene_certificado') or estudio.get('con_certificado')
                if certificado is None:
                    certificado = getattr(perfil, 'estudios_complementarios_certificado', None)
                certificado_bool = False
                if isinstance(certificado, bool):
                    certificado_bool = certificado
                elif isinstance(certificado, str):
                    certificado_bool = certificado.lower() in ['true', '1', 'si', 'sí', 'yes']
                elif isinstance(certificado, int):
                    certificado_bool = certificado == 1
                if nombre:
                    if certificado_bool:
                        pregunta = f"¿Cuenta con el estudio complementario en {nombre} y tiene certificado?"
                    else:
                        pregunta = f"¿Cuenta con el estudio complementario en {nombre}?"
                    pregunta_key = ("estudio_complementario", pregunta)
                    if pregunta_key not in preguntas_set:
                        preguntas.append({
                            "bloque": 4,
                            "tipo_pregunta": "estudio_complementario",
                            "pregunta": pregunta
                        })
                        preguntas_set.add(pregunta_key)

    return preguntas
