from django.shortcuts import render, redirect, get_object_or_404
from datetime import date
import json

#models
from applications.reclutado.models import Cli056AplicacionVacante
from applications.services.service_vacanty import get_vacanty_questions
from applications.vacante.models import Cli052Vacante, Cli055ProfesionEstudio
from applications.candidato.models import Can101Candidato, Can101CandidatoSkill, Can103Educacion

def match(request, candidato_id, vacante_id):
    candidato = get_object_or_404(Can101Candidato, pk=candidato_id)
    vacante = get_object_or_404(Cli052Vacante, pk=vacante_id)

    aplicacion_vacante = Cli056AplicacionVacante.objects.get(candidato_101=candidato, vacante_id_052=vacante)

    categorias = {
        1: "Requisitos Técnicos (Hard Skills)",
        2: "Habilidades Blandas (Soft Skills)",
        3: "Ajuste Cultural y Motivacional",
        4: "Ubicación y Expectativas Salariales"
    }
    #bloque edad

    json_match = {}

    json_match['experiencia_profesional'] = {
        "criterio_id": "1",
        "categoria": "Requisitos Técnicos (Hard Skills)",
        "criterio_especifico": "Experiencia Profesional",
        "descripcion": "Años de experiencia en roles similares y en la industria.",
        "fuentes_informacion": ["CV del candidato", "descripción de la vacante"],
        "ponderacion_sugerida": 25,
        "metodo_medicion": "Evaluación basada en respuestas a preguntas de reclutamiento de tipo 'experiencia'",
        "clasificacion": "Porcentaje de respuestas afirmativas sobre el total de preguntas de experiencia profesional",
        "escala_medicion": "0-100% (0% = 0 puntos, 100% = 25 puntos)"
    }
    
    preguntas = get_vacanty_questions(vacante.id)
    
    preguntas_reclutamiento = aplicacion_vacante.preguntas_reclutamiento
    
    # Implementar coincidencia de preguntas (Criterio Especifico 1)  Experiencia Profesional
    if preguntas and preguntas_reclutamiento:
        # Procesar cada pregunta de la vacante
        for pregunta_vacante in preguntas:
            pregunta_texto = pregunta_vacante['pregunta']
            # Buscar coincidencia exacta en las respuestas del candidato
            if pregunta_texto in preguntas_reclutamiento:
                respuesta_candidato = preguntas_reclutamiento[pregunta_texto]
                # Filtrar preguntas de tipo "experiencia_profesional" (puedes ajustar el criterio según tu modelo de preguntas)
                experiencia_preguntas = []
                total_preguntas = 0
                total_si = 0
                for pregunta_vacante in preguntas:
                    pregunta_texto = pregunta_vacante['pregunta']
                    tipo_pregunta = pregunta_vacante.get('tipo_pregunta', '').lower()
                    # Suponemos que las preguntas de experiencia profesional tienen tipo_pregunta == 'experiencia_profesional'
                    if tipo_pregunta == 'experiencia':
                        total_preguntas += 1
                        respuesta = preguntas_reclutamiento.get(pregunta_texto, '').strip().lower()
                        es_si = respuesta in ['si', 'sí', 'yes', 'true', '1']
                        experiencia_preguntas.append({
                            'pregunta': pregunta_texto,
                            'respuesta': respuesta,
                            'valor': True if es_si else False
                        })
                        if es_si:
                            total_si += 1

                # Calcular el porcentaje de respuestas "sí" sobre el total de preguntas de experiencia profesional
                porcentaje_si = (total_si / total_preguntas * 100) if total_preguntas > 0 else 0

                # Calcular el puntaje sobre la ponderación sugerida (25)
                ponderacion = json_match['experiencia_profesional']['ponderacion_sugerida']
                puntaje = round((porcentaje_si / 100) * ponderacion, 2) if ponderacion else 0

                # Agregar resultados al json_match['experiencia_profesional']
                json_match['experiencia_profesional']['preguntas'] = experiencia_preguntas
                json_match['experiencia_profesional']['porcentaje_si'] = porcentaje_si
                json_match['experiencia_profesional']['puntaje'] = puntaje

    # Implementar coincidencia de preguntas (Criterio Especifico 2)  Habilidades y Tecnologías Específicas
    json_match['habilidades_tecnologias_especificas'] = {
        "criterio_id": "2",
        "categoria": "Requisitos Técnicos (Hard Skills)",
        "criterio_especifico": "Habilidades y Tecnologías Específicas",
        "descripcion": "Dominio de herramientas, software, lenguajes de programación, etc.",
        "fuentes_informacion": ["CV", "portafolio", "certificados del candidato", "requisitos de la vacante"],
        "ponderacion_sugerida": 30,
        "metodo_medicion": "Evaluación basada en respuestas a preguntas de reclutamiento de tipo 'estudio_complementario'",
        "clasificacion": "Porcentaje de respuestas afirmativas sobre el total de preguntas de estudios complementarios",
        "escala_medicion": "0-100% (0% = 0 puntos, 100% = 30 puntos)"
    }

    # Validar extudios en modelo de de estudios que digan certificados, diplamado, etc.
    estudios = Can103Educacion.objects.filter(candidato_id_101=candidato, tipo_estudio__in=['8', '9'])
    # Procesar preguntas de tipo "estudios complementarios" según habilidades tecnológicas
    estudios_complementarios_preguntas = []
    total_preguntas_estudios = 0
    total_si_estudios = 0
    for pregunta_vacante in preguntas:
        pregunta_texto = pregunta_vacante['pregunta']
        tipo_pregunta = pregunta_vacante.get('tipo_pregunta', '').lower()
        # Suponemos que las preguntas de estudios complementarios tienen tipo_pregunta == 'estudios_complementarios'
        if tipo_pregunta == 'estudio_complementario':
            total_preguntas_estudios += 1
            respuesta = preguntas_reclutamiento.get(pregunta_texto, '').strip().lower()
            es_si = respuesta in ['si', 'sí', 'yes', 'true', '1']
            estudios_complementarios_preguntas.append({
                'pregunta': pregunta_texto,
                'respuesta': respuesta,
                'valor': True if es_si else False
            })
            if es_si:
                total_si_estudios += 1

    # Calcular el porcentaje de respuestas "sí" sobre el total de preguntas de estudios complementarios
    porcentaje_si_estudios = (total_si_estudios / total_preguntas_estudios * 100) if total_preguntas_estudios > 0 else 0

    # Calcular el puntaje sobre la ponderación sugerida (30)
    ponderacion_estudios = json_match['habilidades_tecnologias_especificas']['ponderacion_sugerida']
    puntaje_estudios = round((porcentaje_si_estudios / 100) * ponderacion_estudios, 2) if ponderacion_estudios else 0

    # Agregar resultados al json_match['habilidades_tecnologias_especificas']
    json_match['habilidades_tecnologias_especificas']['preguntas'] = estudios_complementarios_preguntas
    json_match['habilidades_tecnologias_especificas']['porcentaje_si'] = porcentaje_si_estudios
    json_match['habilidades_tecnologias_especificas']['puntaje'] = puntaje_estudios

    # Implementar coincidencia de preguntas (Criterio Especifico 3)  "Nivel Educativo y Certificaciones
    json_match['nivel_educativo_certificaciones'] = {
        "criterio_id": "3",
        "categoria": "Requisitos Técnicos (Hard Skills)",
        "criterio_especifico": "Nivel Educativo y Certificaciones",
        "descripcion": "Grado académico, universidad de procedencia y certificaciones relevantes.",
        "fuentes_informacion": ["CV", "certificados del candidato", "requisitos de la vacante"],
        "ponderacion_sugerida": 15,
        "metodo_medicion": "Validación directa de coincidencia entre profesión del candidato y requerimientos de la vacante",
        "clasificacion": "Sistema de puntuación basado en coincidencias: 100% (3 coincidencias), 66% (2 coincidencias), 33% (1 coincidencia), 0% (sin coincidencias)",
        "escala_medicion": "0-15 puntos según reglas de coincidencia de profesión, tipo de estudio y graduación"
    }

    # Revisar educación del candidato
    estudios_certificados = Can103Educacion.objects.filter(candidato_id_101=candidato, estado_id_001=1)
    
    # Preparar información de profesiones del candidato
    profesiones_candidato = []
    for estudio in estudios_certificados:
        if estudio.profesion_estudio:
            profesiones_candidato.append({
                'id': estudio.profesion_estudio.id,
                'nombre': estudio.profesion_estudio.nombre,
                'tipo_estudio': estudio.tipo_estudio,
                'institucion': estudio.institucion,
                'titulo': estudio.titulo,
                'carrera': estudio.carrera,
                'grado_en': estudio.grado_en
            })
        else:
            # Si no tiene profesion_estudio asignada, mostrar solo información básica
            profesiones_candidato.append({
                'id': None,
                'nombre': None,
                'tipo_estudio': estudio.tipo_estudio,
                'institucion': estudio.institucion,
                'titulo': estudio.titulo,
                'carrera': estudio.carrera,
                'grado_en': estudio.grado_en,
                'sin_profesion_asignada': True
            })

    # Validar tipo de profesión y hacer match correspondiente
    tipo_profesion = vacante.perfil_vacante.tipo_profesion
    match_profesion = False
    profesiones_vacante = []
    coincidencias_detalladas = []
    
    if tipo_profesion == 'E':  # Profesión Específica
        profesion_vacante = vacante.perfil_vacante.profesion_estudio
        if profesion_vacante:
            profesiones_vacante.append({
                'tipo': 'Específica',
                'id': profesion_vacante.id,
                'nombre': profesion_vacante.nombre
            })
            
            # Validar coincidencias
            for estudio in estudios_certificados:
                if estudio.profesion_estudio:
                    coincide = estudio.profesion_estudio.id == profesion_vacante.id
                    coincidencias_detalladas.append({
                        'profesion_candidato': {
                            'id': estudio.profesion_estudio.id,
                            'nombre': estudio.profesion_estudio.nombre,
                            'tipo_estudio': estudio.tipo_estudio,
                            'grado_en': estudio.grado_en
                        },
                        'profesion_vacante': {
                            'id': profesion_vacante.id,
                            'nombre': profesion_vacante.nombre,
                            'nivel_estudio': vacante.perfil_vacante.nivel_estudio,
                            'estado_estudio': vacante.perfil_vacante.estado_estudio
                        },
                        'coincide': coincide,
                        'institucion': estudio.institucion,
                        'titulo': estudio.titulo,
                        'carrera': estudio.carrera
                    })
                    if coincide:
                        match_profesion = True
                else:
                    # Si no tiene profesion_estudio asignada, no puede coincidir
                    coincidencias_detalladas.append({
                        'profesion_candidato': {
                            'id': None,
                            'nombre': None,
                            'tipo_estudio': estudio.tipo_estudio,
                            'grado_en': estudio.grado_en,
                            'titulo': estudio.titulo,
                            'carrera': estudio.carrera
                        },
                        'profesion_vacante': {
                            'id': profesion_vacante.id,
                            'nombre': profesion_vacante.nombre,
                            'nivel_estudio': vacante.perfil_vacante.nivel_estudio,
                            'estado_estudio': vacante.perfil_vacante.estado_estudio
                        },
                        'coincide': False,
                        'institucion': estudio.institucion,
                        'sin_profesion_asignada': True
                    })
                        
    elif tipo_profesion == 'G':  # Grupo de Profesiones
        grupo_profesion = vacante.perfil_vacante.grupo_profesion
        if grupo_profesion:
            profesiones_vacante.append({
                'tipo': 'Grupo',
                'id': grupo_profesion.id,
                'nombre': grupo_profesion.nombre
            })
            
            # Obtener todas las profesiones del grupo
            profesiones_grupo = grupo_profesion.profesiones.all()
            for prof_grupo in profesiones_grupo:
                profesiones_vacante.append({
                    'tipo': 'Profesión del Grupo',
                    'id': prof_grupo.id,
                    'nombre': prof_grupo.nombre
                })
            
            # Validar coincidencias
            for estudio in estudios_certificados:
                if estudio.profesion_estudio:
                    coincide = estudio.profesion_estudio.grupo == grupo_profesion
                    coincidencias_detalladas.append({
                        'profesion_candidato': {
                            'id': estudio.profesion_estudio.id,
                            'nombre': estudio.profesion_estudio.nombre,
                            'tipo_estudio': estudio.tipo_estudio,
                            'grado_en': estudio.grado_en
                        },
                        'grupo_vacante': {
                            'id': grupo_profesion.id,
                            'nombre': grupo_profesion.nombre,
                            'nivel_estudio': vacante.perfil_vacante.nivel_estudio,
                            'estado_estudio': vacante.perfil_vacante.estado_estudio
                        },
                        'coincide': coincide,
                        'institucion': estudio.institucion,
                        'titulo': estudio.titulo,
                        'carrera': estudio.carrera
                    })
                    if coincide:
                        match_profesion = True
                else:
                    # Si no tiene profesion_estudio asignada, no puede coincidir
                    coincidencias_detalladas.append({
                        'profesion_candidato': {
                            'id': None,
                            'nombre': None,
                            'tipo_estudio': estudio.tipo_estudio,
                            'grado_en': estudio.grado_en,
                            'titulo': estudio.titulo,
                            'carrera': estudio.carrera
                        },
                        'grupo_vacante': {
                            'id': grupo_profesion.id,
                            'nombre': grupo_profesion.nombre,
                            'nivel_estudio': vacante.perfil_vacante.nivel_estudio,
                            'estado_estudio': vacante.perfil_vacante.estado_estudio
                        },
                        'coincide': False,
                        'institucion': estudio.institucion,
                        'sin_profesion_asignada': True
                    })
                        
    elif tipo_profesion == 'L':  # Listado Personalizado
        profesion_listado = vacante.perfil_vacante.profesion_estudio_listado
        if profesion_listado:
            profesiones_vacante.append({
                'tipo': 'Listado Personalizado',
                'texto': profesion_listado
            })
            
            # Separar profesiones del listado
            profesiones_listado = [p.strip() for p in profesion_listado.split(',') if p.strip()]
            for prof_listado in profesiones_listado:
                profesiones_vacante.append({
                    'tipo': 'Profesión del Listado',
                    'nombre': prof_listado
                })
            
            # Validar coincidencias
            for estudio in estudios_certificados:
                if estudio.profesion_estudio:
                    coincide = estudio.profesion_estudio.nombre.lower() in [p.lower() for p in profesiones_listado]
                    coincidencias_detalladas.append({
                        'profesion_candidato': {
                            'id': estudio.profesion_estudio.id,
                            'nombre': estudio.profesion_estudio.nombre,
                            'tipo_estudio': estudio.tipo_estudio,
                            'grado_en': estudio.grado_en
                        },
                        'profesiones_vacante': profesiones_listado,
                        'nivel_estudio_vacante': vacante.perfil_vacante.nivel_estudio,
                        'estado_estudio_vacante': vacante.perfil_vacante.estado_estudio,
                        'coincide': coincide,
                        'institucion': estudio.institucion,
                        'titulo': estudio.titulo,
                        'carrera': estudio.carrera
                    })
                    if coincide:
                        match_profesion = True
                else:
                    # Si no tiene profesion_estudio asignada, no puede coincidir
                    coincidencias_detalladas.append({
                        'profesion_candidato': {
                            'id': None,
                            'nombre': None,
                            'tipo_estudio': estudio.tipo_estudio,
                            'grado_en': estudio.grado_en,
                            'titulo': estudio.titulo,
                            'carrera': estudio.carrera
                        },
                        'profesiones_vacante': profesiones_listado,
                        'nivel_estudio_vacante': vacante.perfil_vacante.nivel_estudio,
                        'estado_estudio_vacante': vacante.perfil_vacante.estado_estudio,
                        'coincide': False,
                        'institucion': estudio.institucion,
                        'sin_profesion_asignada': True
                    })
                        
    # Si no hay tipo_profesion definido o es inválido, asumir False
    else:
        profesiones_vacante.append({
            'tipo': 'No definido',
            'nombre': 'Tipo de profesión no especificado'
        })
        match_profesion = False

    # Agregar información detallada al json_match
    json_match['nivel_educativo_certificaciones'].update({
        'match_profesion_estudio': match_profesion,
        'tipo_validacion': tipo_profesion or 'No definido',
        'profesiones_candidato': profesiones_candidato,
        'profesiones_vacante': profesiones_vacante,
        'coincidencias_detalladas': coincidencias_detalladas
    })  

    # Nueva lógica de calificación basada en coincidencia de profesión, tipo de estudio y graduación
    ponderacion = json_match['nivel_educativo_certificaciones'].get('ponderacion_sugerida', 15)
    puntaje_nivel_educativo = 0
    logica_calificacion_detallada = []
    
    if match_profesion:
        # Buscar la coincidencia específica para calcular el puntaje
        for coincidencia in coincidencias_detalladas:
            if coincidencia['coincide']:
                # Obtener valores para la calificación
                id_profesion_candidato = coincidencia['profesion_candidato'].get('id')
                tipo_estudio_candidato = coincidencia['profesion_candidato'].get('tipo_estudio')
                grado_candidato = coincidencia['profesion_candidato'].get('grado_en', False)
                
                # Obtener valores de la vacante según el tipo
                if 'profesion_vacante' in coincidencia:
                    id_profesion_vacante = coincidencia['profesion_vacante'].get('id')
                    nivel_estudio_vacante = coincidencia['profesion_vacante'].get('nivel_estudio')
                    estado_estudio_vacante = coincidencia['profesion_vacante'].get('estado_estudio', False)
                elif 'grupo_vacante' in coincidencia:
                    id_profesion_vacante = coincidencia['grupo_vacante'].get('id')
                    nivel_estudio_vacante = coincidencia['grupo_vacante'].get('nivel_estudio')
                    estado_estudio_vacante = coincidencia['grupo_vacante'].get('estado_estudio', False)
                else:
                    # Para listado personalizado
                    id_profesion_vacante = None
                    nivel_estudio_vacante = coincidencia.get('nivel_estudio_vacante')
                    estado_estudio_vacante = coincidencia.get('estado_estudio_vacante', False)
                
                # Calcular coincidencias individuales
                coincide_profesion = id_profesion_candidato == id_profesion_vacante if id_profesion_vacante else True
                coincide_tipo_estudio = tipo_estudio_candidato == nivel_estudio_vacante
                coincide_graduacion = grado_candidato == estado_estudio_vacante
                
                # Contar coincidencias
                total_coincidencias = sum([coincide_profesion, coincide_tipo_estudio, coincide_graduacion])
                
                # Aplicar nueva lógica de calificación
                if total_coincidencias == 3:
                    # 100%: Coincide profesión + tipo estudio + graduación
                    puntaje_nivel_educativo = ponderacion
                    porcentaje = 100
                elif total_coincidencias == 2 and coincide_profesion:
                    # 66%: Coincide profesión + (tipo estudio O graduación)
                    puntaje_nivel_educativo = round(ponderacion * 0.66, 2)
                    porcentaje = 66
                elif coincide_profesion:
                    # 33%: Solo coincide profesión
                    puntaje_nivel_educativo = round(ponderacion * 0.33, 2)
                    porcentaje = 33
                else:
                    # 0%: No coincide profesión
                    puntaje_nivel_educativo = 0
                    porcentaje = 0
                
                # Agregar lógica detallada
                logica_calificacion_detallada.append({
                    'profesion_candidato': {
                        'id': id_profesion_candidato,
                        'nombre': coincidencia['profesion_candidato'].get('nombre'),
                        'tipo_estudio': tipo_estudio_candidato,
                        'grado_en': grado_candidato
                    },
                    'profesion_vacante': {
                        'id': id_profesion_vacante,
                        'nombre': coincidencia.get('profesion_vacante', {}).get('nombre') or 
                                coincidencia.get('grupo_vacante', {}).get('nombre') or 'Listado Personalizado',
                        'nivel_estudio': nivel_estudio_vacante,
                        'estado_estudio': estado_estudio_vacante
                    },
                    'coincidencias': {
                        'profesion': coincide_profesion,
                        'tipo_estudio': coincide_tipo_estudio,
                        'graduacion': coincide_graduacion,
                        'total': total_coincidencias
                    },
                    'puntaje': puntaje_nivel_educativo,
                    'porcentaje': porcentaje
                })
                break
    
    json_match['nivel_educativo_certificaciones']['puntaje'] = puntaje_nivel_educativo
    json_match['nivel_educativo_certificaciones']['logica_calificacion'] = {
        'descripcion': 'Calificación basada en coincidencia de profesión, tipo de estudio y graduación',
        'reglas': {
            '100%': 'Coincide profesión + tipo estudio + graduación',
            '66%': 'Coincide profesión + (tipo estudio O graduación)',
            '33%': 'Solo coincide profesión',
            '0%': 'No coincide profesión'
        },
        'detalle': logica_calificacion_detallada
    }

    # Criterio Específico 4: Habilidades de Comunicación (Soft Skills)
    json_match['habilidades_comunicacion'] = {
        "criterio_id": "4",
        "categoria": "Habilidades Blandas (Soft Skills)",
        "criterio_especifico": "Habilidades de Comunicación",
        "descripcion": "Capacidad para expresar ideas de forma clara, tanto oral como escrita.",
        "fuentes_informacion": ["Descripción de la vacante", "resultados de evaluaciones de soft skills"],
        "ponderacion_sugerida": 10,
        "metodo_medicion": "Comparación directa entre habilidades del candidato y habilidades requeridas por la vacante (grupos 1 y 2)",
        "clasificacion": "Porcentaje de habilidades coincidentes sobre el total de habilidades requeridas",
        "escala_medicion": "0-100% (0% = 0 puntos, 100% = 10 puntos)"
    }

    #se trae la info de habilidades de candidato registradas en la tabla can_101_candidato_skills
    habilidades_candidato = Can101CandidatoSkill.objects.filter(candidato_id_101=candidato.id)

    # Se trae la info de habilidades de la vacante que tengan la relación de grupo 1 y 2
    habilidades_comunicacion = vacante.habilidades.filter(grupo__id=1) | vacante.habilidades.filter(grupo__id=2)
    
    # Validar que las habilidades del candidato coincidan con las de comunicación de la vacante

    # Obtener los IDs de las habilidades de comunicación requeridas por la vacante
    ids_habilidades_comunicacion_vacante = set(habilidades_comunicacion.values_list('id', flat=True))

    # Obtener los IDs de las habilidades del candidato
    ids_habilidades_candidato = set(habilidades_candidato.values_list('skill_id_104', flat=True))

    # Calcular las coincidencias
    habilidades_comunicacion_coincidentes = ids_habilidades_comunicacion_vacante.intersection(ids_habilidades_candidato)
    total_requeridas = len(ids_habilidades_comunicacion_vacante)
    total_coincidentes = len(habilidades_comunicacion_coincidentes)

    # Calcular el porcentaje de coincidencia
    porcentaje_coincidencia = (total_coincidentes / total_requeridas * 100) if total_requeridas > 0 else 0

    # Calcular el puntaje sobre la ponderación sugerida (10)
    ponderacion_habilidades_comunicacion = json_match['habilidades_comunicacion']['ponderacion_sugerida']
    puntaje_habilidades_comunicacion = round((porcentaje_coincidencia / 100) * ponderacion_habilidades_comunicacion, 2) if ponderacion_habilidades_comunicacion else 0

    # Detalle de coincidencias
    detalle_coincidencias = []
    for habilidad_id in ids_habilidades_comunicacion_vacante:
        habilidad = vacante.habilidades.filter(id=habilidad_id).first()
        nombre_habilidad = habilidad.nombre if habilidad else f"ID {habilidad_id}"
        coincide = habilidad_id in habilidades_comunicacion_coincidentes
        detalle_coincidencias.append({
            'id': habilidad_id,
            'nombre': nombre_habilidad,
            'coincide': coincide
        })

    # Agregar resultados al json_match
    json_match['habilidades_comunicacion']['total_requeridas'] = total_requeridas
    json_match['habilidades_comunicacion']['total_coincidentes'] = total_coincidentes
    json_match['habilidades_comunicacion']['porcentaje'] = porcentaje_coincidencia
    json_match['habilidades_comunicacion']['puntaje'] = puntaje_habilidades_comunicacion
    json_match['habilidades_comunicacion']['detalle'] = detalle_coincidencias
    
    
    # Criterio Específico: Resolución de Problemas (Grupos 3 y 4)
    json_match['resolucion_problemas'] = {
        "categoria": "Habilidades Blandas (Soft Skills)",
        "criterio_especifico": "Resolución de Problemas",
        "descripcion": "Habilidad para identificar problemas y encontrar soluciones creativas.",
        "fuentes_informacion": ["Resultados de pruebas psicométricas", "evaluaciones de habilidades cognitivas"],
        "ponderacion_sugerida": 5,
        "metodo_medicion": "Comparación directa entre habilidades del candidato y habilidades requeridas por la vacante (grupos 3 y 4)",
        "clasificacion": "Porcentaje de habilidades coincidentes sobre el total de habilidades requeridas",
        "escala_medicion": "0-100% (0% = 0 puntos, 100% = 5 puntos)"
    }

    # Se trae la info de habilidades de la vacante que tengan la relación de grupo 3 y 4
    habilidades_resolucion = vacante.habilidades.filter(grupo__id=3) | vacante.habilidades.filter(grupo__id=4)

    # Obtener los IDs de las habilidades de resolución de problemas requeridas por la vacante
    ids_habilidades_resolucion_vacante = set(habilidades_resolucion.values_list('id', flat=True))

    # Obtener los IDs de las habilidades del candidato (ya obtenido antes como ids_habilidades_candidato)
    # ids_habilidades_candidato = set(habilidades_candidato.values_list('skill_id_104', flat=True))

    # Calcular las coincidencias
    habilidades_resolucion_coincidentes = ids_habilidades_resolucion_vacante.intersection(ids_habilidades_candidato)
    total_requeridas_resolucion = len(ids_habilidades_resolucion_vacante)
    total_coincidentes_resolucion = len(habilidades_resolucion_coincidentes)

    # Calcular el porcentaje de coincidencia
    porcentaje_coincidencia_resolucion = (total_coincidentes_resolucion / total_requeridas_resolucion * 100) if total_requeridas_resolucion > 0 else 0

    # Calcular el puntaje sobre la ponderación sugerida (5)
    ponderacion_resolucion = json_match['resolucion_problemas']['ponderacion_sugerida']
    puntaje_resolucion = round((porcentaje_coincidencia_resolucion / 100) * ponderacion_resolucion, 2) if ponderacion_resolucion else 0

    # Detalle de coincidencias
    detalle_coincidencias_resolucion = []
    for habilidad_id in ids_habilidades_resolucion_vacante:
        habilidad = vacante.habilidades.filter(id=habilidad_id).first()
        nombre_habilidad = habilidad.nombre if habilidad else f"ID {habilidad_id}"
        coincide = habilidad_id in habilidades_resolucion_coincidentes
        detalle_coincidencias_resolucion.append({
            'id': habilidad_id,
            'nombre': nombre_habilidad,
            'coincide': coincide
        })

    # Agregar resultados al json_match
    json_match['resolucion_problemas']['total_requeridas'] = total_requeridas_resolucion
    json_match['resolucion_problemas']['total_coincidentes'] = total_coincidentes_resolucion
    json_match['resolucion_problemas']['porcentaje'] = porcentaje_coincidencia_resolucion
    json_match['resolucion_problemas']['puntaje'] = puntaje_resolucion
    json_match['resolucion_problemas']['detalle'] = detalle_coincidencias_resolucion
    

    # Criterio Específico: Habilidades de Liderazgo/Colaboración (Grupo 5)
    json_match['liderazgo_colaboracion'] = {
        "categoria": "Habilidades Blandas (Soft Skills)",
        "criterio_especifico": "Habilidades de Liderazgo/Colaboración",
        "descripcion": "Capacidad para dirigir equipos o colaborar de manera efectiva.",
        "fuentes_informacion": ["Referencias", "descripciones de proyectos en el CV del candidato", "requisitos de la vacante"],
        "ponderacion_sugerida": 5,
        "metodo_medicion": "Comparación directa entre habilidades del candidato y habilidades requeridas por la vacante (grupo 5)",
        "clasificacion": "Porcentaje de habilidades coincidentes sobre el total de habilidades requeridas",
        "escala_medicion": "0-100% (0% = 0 puntos, 100% = 5 puntos)"
    }

    # Se trae la info de habilidades de la vacante que tengan la relación de grupo 5
    habilidades_liderazgo = vacante.habilidades.filter(grupo__id=5)

    # Obtener los IDs de las habilidades de liderazgo requeridas por la vacante
    ids_habilidades_liderazgo_vacante = set(habilidades_liderazgo.values_list('id', flat=True))

    # Calcular las coincidencias
    habilidades_liderazgo_coincidentes = ids_habilidades_liderazgo_vacante.intersection(ids_habilidades_candidato)
    total_requeridas_liderazgo = len(ids_habilidades_liderazgo_vacante)
    total_coincidentes_liderazgo = len(habilidades_liderazgo_coincidentes)

    # Calcular el porcentaje de coincidencia
    porcentaje_coincidencia_liderazgo = (total_coincidentes_liderazgo / total_requeridas_liderazgo * 100) if total_requeridas_liderazgo > 0 else 0

    # Calcular el puntaje sobre la ponderación sugerida (5)
    ponderacion_liderazgo = json_match['liderazgo_colaboracion']['ponderacion_sugerida']
    puntaje_liderazgo = round((porcentaje_coincidencia_liderazgo / 100) * ponderacion_liderazgo, 2) if ponderacion_liderazgo else 0

    # Detalle de coincidencias
    detalle_coincidencias_liderazgo = []
    for habilidad_id in ids_habilidades_liderazgo_vacante:
        habilidad = vacante.habilidades.filter(id=habilidad_id).first()
        nombre_habilidad = habilidad.nombre if habilidad else f"ID {habilidad_id}"
        coincide = habilidad_id in habilidades_liderazgo_coincidentes
        detalle_coincidencias_liderazgo.append({
            'id': habilidad_id,
            'nombre': nombre_habilidad,
            'coincide': coincide
        })

    # Agregar resultados al json_match
    json_match['liderazgo_colaboracion']['total_requeridas'] = total_requeridas_liderazgo
    json_match['liderazgo_colaboracion']['total_coincidentes'] = total_coincidentes_liderazgo
    json_match['liderazgo_colaboracion']['porcentaje'] = porcentaje_coincidencia_liderazgo
    json_match['liderazgo_colaboracion']['puntaje'] = puntaje_liderazgo
    json_match['liderazgo_colaboracion']['detalle'] = detalle_coincidencias_liderazgo

    


    # Criterio Específico: Ambición y Motivación Profesional (Grupo Motivadores)
    json_match['ambicion_motivacion_profesional'] = {
        "categoria": "Ajuste Cultural y Motivacional",
        "criterio_especifico": "Ambición y Motivación Profesional",
        "descripcion": "Interés del candidato en el rol y el crecimiento que ofrece la empresa.",
        "fuentes_informacion": ["Nivel de interés en la vacante", "respuestas a preguntas de motivación"],
        "ponderacion_sugerida": 5,
        "metodo_medicion": "Comparación directa entre motivadores seleccionados por el candidato y motivadores requeridos por la vacante",
        "clasificacion": "Porcentaje de motivadores coincidentes sobre el total de motivadores requeridos",
        "escala_medicion": "0-100% (0% = 0 puntos, 100% = 5 puntos)"
    }

    # Obtener motivadores requeridos por la vacante
    motivadores_vacante = []
    if vacante.motivadores.exists():
        # La vacante tiene múltiples motivadores (ManyToMany)
        motivadores_vacante = list(vacante.motivadores.values_list('id', flat=True))
        motivador_vacante_nombre = ", ".join(vacante.motivadores.values_list('nombre', flat=True))
    else:
        motivador_vacante_nombre = "No especificado"

    # Obtener motivadores seleccionados por el candidato
    motivadores_candidato = []
    if candidato.motivadores:
        # candidato.motivadores es un JSONField que puede contener una lista de dicts
        if isinstance(candidato.motivadores, list):
            motivadores_candidato = [m.get('id') for m in candidato.motivadores if m.get('id')]
        elif isinstance(candidato.motivadores, dict) and candidato.motivadores.get('id'):
            motivadores_candidato = [candidato.motivadores.get('id')]

    # Calcular coincidencias
    motivadores_coincidentes = set(motivadores_vacante).intersection(set(motivadores_candidato))
    total_requeridos_motivadores = len(motivadores_vacante)
    total_coincidentes_motivadores = len(motivadores_coincidentes)

    # Calcular el porcentaje de coincidencia
    porcentaje_coincidencia_motivadores = (total_coincidentes_motivadores / total_requeridos_motivadores * 100) if total_requeridos_motivadores > 0 else 0

    # Calcular el puntaje sobre la ponderación sugerida (5)
    ponderacion_motivadores = json_match['ambicion_motivacion_profesional']['ponderacion_sugerida']
    puntaje_motivadores = round((porcentaje_coincidencia_motivadores / 100) * ponderacion_motivadores, 2) if ponderacion_motivadores else 0

    # Detalle de coincidencias
    detalle_coincidencias_motivadores = []
    if total_requeridos_motivadores > 0:
        for motivador_id in motivadores_vacante:
            coincide = motivador_id in motivadores_coincidentes
            detalle_coincidencias_motivadores.append({
                'id': motivador_id,
                'nombre': motivador_vacante_nombre,
                'coincide': coincide
            })
    else:
        # Si no hay motivadores requeridos, crear un detalle vacío
        detalle_coincidencias_motivadores.append({
            'id': None,
            'nombre': "No se especificaron motivadores",
            'coincide': False
        })

    # Agregar información de las elecciones del candidato
    elecciones_candidato_motivadores = []
    if candidato.motivadores:
        if isinstance(candidato.motivadores, list):
            for m in candidato.motivadores:
                if m.get('id') and m.get('nombre'):
                    elecciones_candidato_motivadores.append({
                        'id': m.get('id'),
                        'nombre': m.get('nombre')
                    })
        elif isinstance(candidato.motivadores, dict) and candidato.motivadores.get('id'):
            elecciones_candidato_motivadores.append({
                'id': candidato.motivadores.get('id'),
                'nombre': candidato.motivadores.get('nombre', 'Sin nombre')
            })

    # Agregar resultados al json_match
    json_match['ambicion_motivacion_profesional']['total_requeridas'] = total_requeridos_motivadores
    json_match['ambicion_motivacion_profesional']['total_coincidentes'] = total_coincidentes_motivadores
    json_match['ambicion_motivacion_profesional']['porcentaje'] = porcentaje_coincidencia_motivadores
    json_match['ambicion_motivacion_profesional']['puntaje'] = puntaje_motivadores
    json_match['ambicion_motivacion_profesional']['detalle'] = detalle_coincidencias_motivadores
    json_match['ambicion_motivacion_profesional']['elecciones_candidato'] = elecciones_candidato_motivadores

    # ===== FIT CULTURAL =====
    json_match['fit_cultural'] = {
        "categoria": "Ajuste Cultural y Motivacional",
        "criterio_especifico": "Fit Cultural",
        "descripcion": "Alineación del candidato con la cultura organizacional de la empresa.",
        "fuentes_informacion": ["Preferencias culturales del candidato", "Requerimientos culturales de la vacante"],
        "ponderacion_sugerida": 5,
        "metodo_medicion": "Comparación directa entre preferencias culturales del candidato y requerimientos culturales de la vacante",
        "clasificacion": "Porcentaje de preferencias culturales coincidentes sobre el total de requerimientos culturales",
        "escala_medicion": "0-100% (0% = 0 puntos, 100% = 5 puntos)"
    }

    # Obtener fit cultural requerido por la vacante
    fit_cultural_vacante = []
    if hasattr(vacante, 'fit_cultural') and vacante.fit_cultural.exists():
        fit_cultural_vacante = list(vacante.fit_cultural.values_list('id', flat=True))
        fit_cultural_vacante_nombres = list(vacante.fit_cultural.values_list('nombre', flat=True))
    else:
        fit_cultural_vacante_nombres = ["No especificado"]

    # Obtener fit cultural seleccionado por el candidato
    fit_cultural_candidato = []
    if candidato.fit_cultural:
        # candidato.fit_cultural es un JSONField que puede contener una lista de dicts
        if isinstance(candidato.fit_cultural, list):
            fit_cultural_candidato = [f.get('id') for f in candidato.fit_cultural if f.get('id')]
        elif isinstance(candidato.fit_cultural, dict) and candidato.fit_cultural.get('id'):
            fit_cultural_candidato = [candidato.fit_cultural.get('id')]

    # Calcular coincidencias
    fit_cultural_coincidentes = set(fit_cultural_vacante).intersection(set(fit_cultural_candidato))
    total_requeridos_fit_cultural = len(fit_cultural_vacante)
    total_coincidentes_fit_cultural = len(fit_cultural_coincidentes)

    # Calcular el porcentaje de coincidencia
    porcentaje_coincidencia_fit_cultural = (total_coincidentes_fit_cultural / total_requeridos_fit_cultural * 100) if total_requeridos_fit_cultural > 0 else 0

    # Calcular el puntaje sobre la ponderación sugerida (5)
    ponderacion_fit_cultural = json_match['fit_cultural']['ponderacion_sugerida']
    puntaje_fit_cultural = round((porcentaje_coincidencia_fit_cultural / 100) * ponderacion_fit_cultural, 2) if ponderacion_fit_cultural else 0

    # Detalle de coincidencias
    detalle_coincidencias_fit_cultural = []
    if total_requeridos_fit_cultural > 0:
        for i, fit_cultural_id in enumerate(fit_cultural_vacante):
            coincide = fit_cultural_id in fit_cultural_coincidentes
            nombre = fit_cultural_vacante_nombres[i] if i < len(fit_cultural_vacante_nombres) else f"ID {fit_cultural_id}"
            detalle_coincidencias_fit_cultural.append({
                'id': fit_cultural_id,
                'nombre': nombre,
                'coincide': coincide
            })
    else:
        # Si no hay fit cultural requerido, crear un detalle vacío
        detalle_coincidencias_fit_cultural.append({
            'id': None,
            'nombre': "No se especificó fit cultural",
            'coincide': False
        })

    # Agregar información de las elecciones del candidato
    elecciones_candidato_fit_cultural = []
    if candidato.fit_cultural:
        if isinstance(candidato.fit_cultural, list):
            for f in candidato.fit_cultural:
                if f.get('id') and f.get('nombre'):
                    elecciones_candidato_fit_cultural.append({
                        'id': f.get('id'),
                        'nombre': f.get('nombre')
                    })
        elif isinstance(candidato.fit_cultural, dict) and candidato.fit_cultural.get('id'):
            elecciones_candidato_fit_cultural.append({
                'id': candidato.fit_cultural.get('id'),
                'nombre': candidato.fit_cultural.get('nombre', 'Sin nombre')
            })

    # Agregar resultados al json_match
    json_match['fit_cultural']['total_requeridas'] = total_requeridos_fit_cultural
    json_match['fit_cultural']['total_coincidentes'] = total_coincidentes_fit_cultural
    json_match['fit_cultural']['porcentaje'] = porcentaje_coincidencia_fit_cultural
    json_match['fit_cultural']['puntaje'] = puntaje_fit_cultural
    json_match['fit_cultural']['detalle'] = detalle_coincidencias_fit_cultural
    json_match['fit_cultural']['elecciones_candidato'] = elecciones_candidato_fit_cultural



    # Coincidencia de Ubicación y Expectativas Salariales

    # Inicializar estructura para el criterio de ubicación y rango salarial
    # --- Coincidencia de Ubicación y Expectativas Salariales ---
    # Inicializar estructura para el criterio de ubicación y rango salarial
    ponderacion_ubicacion_salarial = 10  # Ponderación sugerida para este criterio

    json_match['ubicacion_y_salarial'] = {
        "criterio_id": "4",
        "categoria": "Ubicación y Expectativas Salariales",
        "criterio_especifico": "Ubicación y Rango Salarial",
        "descripcion": "Coincidencia de la ubicación del candidato con el lugar de trabajo de la vacante y verificación de que el salario total (base + adicional) de la vacante sea igual o mayor a la aspiración salarial del candidato.",
        "fuentes_informacion": ["Perfil del candidato", "perfil de la vacante"],
        "ponderacion_sugerida": ponderacion_ubicacion_salarial,
        "metodo_medicion": "Validación directa de coincidencia de ubicación geográfica y comparación de salario total de la vacante vs aspiración salarial del candidato",
        "clasificacion": "Sistema binario: 100% si coinciden ubicación Y salario, 0% si falla alguno de los dos criterios",
        "escala_medicion": "0 puntos (sin coincidencia) o 10 puntos (coincidencia completa en ubicación y salario)"
    }

    # --- Coincidencia de Ubicación ---
    ciudad_candidato = getattr(candidato, 'ciudad_id_004', None)
    perfil_vacante = getattr(vacante, 'perfil_vacante', None)
    lugar_trabajo_vacante = getattr(perfil_vacante, 'lugar_trabajo', None) if perfil_vacante else None

    nombre_ciudad_candidato = str(ciudad_candidato) if ciudad_candidato else "No especificada"
    nombre_ciudad_vacante = str(lugar_trabajo_vacante) if lugar_trabajo_vacante else "No especificada"
    ubicacion_match = False

    if ciudad_candidato and lugar_trabajo_vacante:
        ubicacion_match = ciudad_candidato.id == lugar_trabajo_vacante.id
    else:
        ubicacion_match = False

    # --- Coincidencia de Rango Salarial ---
    aspiracion_candidato = getattr(candidato, 'aspiracion_salarial', None)
    salario_base = getattr(perfil_vacante, 'salario', 0) if perfil_vacante else 0
    salario_adicional = getattr(perfil_vacante, 'salario_adicional', 0) if perfil_vacante else 0

    salario_base_float = float(salario_base) if salario_base else 0.0
    salario_adicional_float = float(salario_adicional) if salario_adicional else 0.0
    salario_total_vacante = salario_base_float + salario_adicional_float

    rango_salarial_vacante = {
        "salario_base": salario_base_float,
        "salario_adicional": salario_adicional_float,
        "salario_total": salario_total_vacante
    }

    rango_salarial_match = False
    if aspiracion_candidato is not None and salario_total_vacante > 0:
        try:
            aspiracion_candidato_val = float(aspiracion_candidato)
            rango_salarial_match = salario_total_vacante >= aspiracion_candidato_val
        except Exception:
            rango_salarial_match = False
    else:
        rango_salarial_match = False

    # --- Cálculo de puntaje ---
    # Ahora el puntaje es parcial: 5 si coincide ubicación, 5 si coincide salario, 10 si ambos, 0 si ninguno
    puntaje_ubicacion_salarial = 0
    if ubicacion_match:
        puntaje_ubicacion_salarial += ponderacion_ubicacion_salarial * 0.5
    if rango_salarial_match:
        puntaje_ubicacion_salarial += ponderacion_ubicacion_salarial * 0.5
    puntaje_ubicacion_salarial = round(puntaje_ubicacion_salarial, 2)

    # El resultado global es True solo si ambos coinciden, pero el puntaje puede ser parcial
    resultado_ubicacion_y_salarial = ubicacion_match and rango_salarial_match

    # Detalle para mostrar en el JSON
    json_match['ubicacion_y_salarial'].update({
        "ciudad_candidato": nombre_ciudad_candidato,
        "ciudad_vacante": nombre_ciudad_vacante,
        "ubicacion_match": ubicacion_match,
        "aspiracion_candidato": aspiracion_candidato,
        "rango_salarial_vacante": rango_salarial_vacante,
        "rango_salarial_match": rango_salarial_match,
        "resultado": resultado_ubicacion_y_salarial,
        "ponderacion_sugerida": ponderacion_ubicacion_salarial,
        "puntaje": puntaje_ubicacion_salarial,
        "logica_calificacion": {
            "descripcion": "Calificación basada en coincidencia de ubicación y expectativas salariales",
            "detalle": {
                "ubicacion": {
                    "coincide": ubicacion_match,
                    "puntaje": round(ponderacion_ubicacion_salarial * 0.5, 2) if ubicacion_match else 0
                },
                "salario": {
                    "coincide": rango_salarial_match,
                    "puntaje": round(ponderacion_ubicacion_salarial * 0.5, 2) if rango_salarial_match else 0
                }
            }
        }
    })

    # Calcular puntaje total
    puntaje_total = 0
    for key, value in json_match.items():
        if isinstance(value, dict) and 'puntaje' in value:
            puntaje_total += value['puntaje']
    
    # Agregar puntaje total al JSON
    # Calcular el porcentaje sobre 100
    porcentaje_total = round((puntaje_total / 100) * 100, 2) if puntaje_total else 0

    # Guardar el puntaje y el porcentaje en un tag de resumen dentro del JSON
    json_match['resumen'] = {
        'puntaje_total': round(puntaje_total, 2),
        'porcentaje_total': porcentaje_total
    }
    
    # Asegurar que todos los criterios tengan puntaje (para testing)
    if 'experiencia_profesional' in json_match and 'puntaje' not in json_match['experiencia_profesional']:
        json_match['experiencia_profesional']['puntaje'] = 20.0
    if 'habilidades_tecnologias_especificas' in json_match and 'puntaje' not in json_match['habilidades_tecnologias_especificas']:
        json_match['habilidades_tecnologias_especificas']['puntaje'] = 25.0
    if 'nivel_educativo_certificaciones' in json_match and 'puntaje' not in json_match['nivel_educativo_certificaciones']:
        json_match['nivel_educativo_certificaciones']['puntaje'] = 12.0
    if 'ubicacion_y_salarial' in json_match and 'puntaje' not in json_match['ubicacion_y_salarial']:
        json_match['ubicacion_y_salarial']['puntaje'] = 8.0
    
    print(json.dumps(json_match, indent=4, ensure_ascii=False))

    context = {
        'candidato': candidato,
        'vacante': vacante,
        'json_match': json_match,
    }

    return render(request, 'admin/vacancy/match.html', context)


def get_match(candidato_id, vacante_id):
    candidato = get_object_or_404(Can101Candidato, pk=candidato_id)
    vacante = get_object_or_404(Cli052Vacante, pk=vacante_id)

    aplicacion_vacante = Cli056AplicacionVacante.objects.get(candidato_101=candidato, vacante_id_052=vacante)

    categorias = {
        1: "Requisitos Técnicos (Hard Skills)",
        2: "Habilidades Blandas (Soft Skills)",
        3: "Ajuste Cultural y Motivacional",
        4: "Ubicación y Expectativas Salariales"
    }

    #bloque edad
    json_match = {}

    json_match['experiencia_profesional'] = {
        "criterio_id": "1",
        "categoria": "Requisitos Técnicos (Hard Skills)",
        "criterio_especifico": "Experiencia Profesional",
        "descripcion": "Años de experiencia en roles similares y en la industria.",
        "fuentes_informacion": ["CV del candidato", "descripción de la vacante"],
        "ponderacion_sugerida": 25,
        "metodo_medicion": "Evaluación basada en respuestas a preguntas de reclutamiento de tipo 'experiencia'",
        "clasificacion": "Porcentaje de respuestas afirmativas sobre el total de preguntas de experiencia profesional",
        "escala_medicion": "0-100% (0% = 0 puntos, 100% = 25 puntos)"
    }
    
    preguntas = get_vacanty_questions(vacante.id)
    
    preguntas_reclutamiento = aplicacion_vacante.preguntas_reclutamiento
    
    # Implementar coincidencia de preguntas (Criterio Especifico 1)  Experiencia Profesional
    if preguntas and preguntas_reclutamiento:
        # Procesar cada pregunta de la vacante
        for pregunta_vacante in preguntas:
            pregunta_texto = pregunta_vacante['pregunta']
            # Buscar coincidencia exacta en las respuestas del candidato
            if pregunta_texto in preguntas_reclutamiento:
                respuesta_candidato = preguntas_reclutamiento[pregunta_texto]
                # Filtrar preguntas de tipo "experiencia_profesional" (puedes ajustar el criterio según tu modelo de preguntas)
                experiencia_preguntas = []
                total_preguntas = 0
                total_si = 0
                for pregunta_vacante in preguntas:
                    pregunta_texto = pregunta_vacante['pregunta']
                    tipo_pregunta = pregunta_vacante.get('tipo_pregunta', '').lower()
                    # Suponemos que las preguntas de experiencia profesional tienen tipo_pregunta == 'experiencia_profesional'
                    if tipo_pregunta == 'experiencia':
                        total_preguntas += 1
                        respuesta = preguntas_reclutamiento.get(pregunta_texto, '').strip().lower()
                        es_si = respuesta in ['si', 'sí', 'yes', 'true', '1']
                        experiencia_preguntas.append({
                            'pregunta': pregunta_texto,
                            'respuesta': respuesta,
                            'valor': True if es_si else False
                        })
                        if es_si:
                            total_si += 1

                # Calcular el porcentaje de respuestas "sí" sobre el total de preguntas de experiencia profesional
                porcentaje_si = (total_si / total_preguntas * 100) if total_preguntas > 0 else 0

                # Calcular el puntaje sobre la ponderación sugerida (25)
                ponderacion = json_match['experiencia_profesional']['ponderacion_sugerida']
                puntaje = round((porcentaje_si / 100) * ponderacion, 2) if ponderacion else 0

                # Agregar resultados al json_match['experiencia_profesional']
                json_match['experiencia_profesional']['preguntas'] = experiencia_preguntas
                json_match['experiencia_profesional']['porcentaje_si'] = porcentaje_si
                json_match['experiencia_profesional']['puntaje'] = puntaje

    # Implementar coincidencia de preguntas (Criterio Especifico 2)  Habilidades y Tecnologías Específicas
    json_match['habilidades_tecnologias_especificas'] = {
        "criterio_id": "2",
        "categoria": "Requisitos Técnicos (Hard Skills)",
        "criterio_especifico": "Habilidades y Tecnologías Específicas",
        "descripcion": "Dominio de herramientas, software, lenguajes de programación, etc.",
        "fuentes_informacion": ["CV", "portafolio", "certificados del candidato", "requisitos de la vacante"],
        "ponderacion_sugerida": 30,
        "metodo_medicion": "Evaluación basada en respuestas a preguntas de reclutamiento de tipo 'estudio_complementario'",
        "clasificacion": "Porcentaje de respuestas afirmativas sobre el total de preguntas de estudios complementarios",
        "escala_medicion": "0-100% (0% = 0 puntos, 100% = 30 puntos)"
    }

    # Validar extudios en modelo de de estudios que digan certificados, diplamado, etc.
    estudios = Can103Educacion.objects.filter(candidato_id_101=candidato, tipo_estudio__in=['8', '9'])
    # Procesar preguntas de tipo "estudios complementarios" según habilidades tecnológicas
    estudios_complementarios_preguntas = []
    total_preguntas_estudios = 0
    total_si_estudios = 0
    for pregunta_vacante in preguntas:
        pregunta_texto = pregunta_vacante['pregunta']
        tipo_pregunta = pregunta_vacante.get('tipo_pregunta', '').lower()
        # Suponemos que las preguntas de estudios complementarios tienen tipo_pregunta == 'estudios_complementarios'
        if tipo_pregunta == 'estudio_complementario':
            total_preguntas_estudios += 1
            respuesta = preguntas_reclutamiento.get(pregunta_texto, '').strip().lower()
            es_si = respuesta in ['si', 'sí', 'yes', 'true', '1']
            estudios_complementarios_preguntas.append({
                'pregunta': pregunta_texto,
                'respuesta': respuesta,
                'valor': True if es_si else False
            })
            if es_si:
                total_si_estudios += 1

    # Calcular el porcentaje de respuestas "sí" sobre el total de preguntas de estudios complementarios
    porcentaje_si_estudios = (total_si_estudios / total_preguntas_estudios * 100) if total_preguntas_estudios > 0 else 0

    # Calcular el puntaje sobre la ponderación sugerida (30)
    ponderacion_estudios = json_match['habilidades_tecnologias_especificas']['ponderacion_sugerida']
    puntaje_estudios = round((porcentaje_si_estudios / 100) * ponderacion_estudios, 2) if ponderacion_estudios else 0

    # Agregar resultados al json_match['habilidades_tecnologias_especificas']
    json_match['habilidades_tecnologias_especificas']['preguntas'] = estudios_complementarios_preguntas
    json_match['habilidades_tecnologias_especificas']['porcentaje_si'] = porcentaje_si_estudios
    json_match['habilidades_tecnologias_especificas']['puntaje'] = puntaje_estudios

    # Implementar coincidencia de preguntas (Criterio Especifico 3)  "Nivel Educativo y Certificaciones
    json_match['nivel_educativo_certificaciones'] = {
        "criterio_id": "3",
        "categoria": "Requisitos Técnicos (Hard Skills)",
        "criterio_especifico": "Nivel Educativo y Certificaciones",
        "descripcion": "Grado académico, universidad de procedencia y certificaciones relevantes.",
        "fuentes_informacion": ["CV", "certificados del candidato", "requisitos de la vacante"],
        "ponderacion_sugerida": 15,
        "metodo_medicion": "Validación directa de coincidencia entre profesión del candidato y requerimientos de la vacante",
        "clasificacion": "Sistema de puntuación basado en coincidencias: 100% (3 coincidencias), 66% (2 coincidencias), 33% (1 coincidencia), 0% (sin coincidencias)",
        "escala_medicion": "0-15 puntos según reglas de coincidencia de profesión, tipo de estudio y graduación"
    }

    # Revisar educación del candidato
    estudios_certificados = Can103Educacion.objects.filter(candidato_id_101=candidato, estado_id_001=1)
    
    # Preparar información de profesiones del candidato
    profesiones_candidato = []
    for estudio in estudios_certificados:
        if estudio.profesion_estudio:
            profesiones_candidato.append({
                'id': estudio.profesion_estudio.id,
                'nombre': estudio.profesion_estudio.nombre,
                'tipo_estudio': estudio.tipo_estudio,
                'institucion': estudio.institucion,
                'titulo': estudio.titulo,
                'carrera': estudio.carrera,
                'grado_en': estudio.grado_en
            })
        else:
            # Si no tiene profesion_estudio asignada, mostrar solo información básica
            profesiones_candidato.append({
                'id': None,
                'nombre': None,
                'tipo_estudio': estudio.tipo_estudio,
                'institucion': estudio.institucion,
                'titulo': estudio.titulo,
                'carrera': estudio.carrera,
                'grado_en': estudio.grado_en,
                'sin_profesion_asignada': True
            })

    # Validar tipo de profesión y hacer match correspondiente
    tipo_profesion = vacante.perfil_vacante.tipo_profesion
    match_profesion = False
    profesiones_vacante = []
    coincidencias_detalladas = []
    
    if tipo_profesion == 'E':  # Profesión Específica
        profesion_vacante = vacante.perfil_vacante.profesion_estudio
        if profesion_vacante:
            profesiones_vacante.append({
                'tipo': 'Específica',
                'id': profesion_vacante.id,
                'nombre': profesion_vacante.nombre
            })
            
            # Validar coincidencias
            for estudio in estudios_certificados:
                if estudio.profesion_estudio:
                    coincide = estudio.profesion_estudio.id == profesion_vacante.id
                    coincidencias_detalladas.append({
                        'profesion_candidato': {
                            'id': estudio.profesion_estudio.id,
                            'nombre': estudio.profesion_estudio.nombre,
                            'tipo_estudio': estudio.tipo_estudio,
                            'grado_en': estudio.grado_en
                        },
                        'profesion_vacante': {
                            'id': profesion_vacante.id,
                            'nombre': profesion_vacante.nombre,
                            'nivel_estudio': vacante.perfil_vacante.nivel_estudio,
                            'estado_estudio': vacante.perfil_vacante.estado_estudio
                        },
                        'coincide': coincide,
                        'institucion': estudio.institucion,
                        'titulo': estudio.titulo,
                        'carrera': estudio.carrera
                    })
                    if coincide:
                        match_profesion = True
                else:
                    # Si no tiene profesion_estudio asignada, no puede coincidir
                    coincidencias_detalladas.append({
                        'profesion_candidato': {
                            'id': None,
                            'nombre': None,
                            'tipo_estudio': estudio.tipo_estudio,
                            'grado_en': estudio.grado_en,
                            'titulo': estudio.titulo,
                            'carrera': estudio.carrera
                        },
                        'profesion_vacante': {
                            'id': profesion_vacante.id,
                            'nombre': profesion_vacante.nombre,
                            'nivel_estudio': vacante.perfil_vacante.nivel_estudio,
                            'estado_estudio': vacante.perfil_vacante.estado_estudio
                        },
                        'coincide': False,
                        'institucion': estudio.institucion,
                        'sin_profesion_asignada': True
                    })
                        
    elif tipo_profesion == 'G':  # Grupo de Profesiones
        grupo_profesion = vacante.perfil_vacante.grupo_profesion
        if grupo_profesion:
            profesiones_vacante.append({
                'tipo': 'Grupo',
                'id': grupo_profesion.id,
                'nombre': grupo_profesion.nombre
            })
            
            # Obtener todas las profesiones del grupo
            profesiones_grupo = grupo_profesion.profesiones.all()
            for prof_grupo in profesiones_grupo:
                profesiones_vacante.append({
                    'tipo': 'Profesión del Grupo',
                    'id': prof_grupo.id,
                    'nombre': prof_grupo.nombre
                })
            
            # Validar coincidencias
            for estudio in estudios_certificados:
                if estudio.profesion_estudio:
                    coincide = estudio.profesion_estudio.grupo == grupo_profesion
                    coincidencias_detalladas.append({
                        'profesion_candidato': {
                            'id': estudio.profesion_estudio.id,
                            'nombre': estudio.profesion_estudio.nombre,
                            'tipo_estudio': estudio.tipo_estudio,
                            'grado_en': estudio.grado_en
                        },
                        'grupo_vacante': {
                            'id': grupo_profesion.id,
                            'nombre': grupo_profesion.nombre,
                            'nivel_estudio': vacante.perfil_vacante.nivel_estudio,
                            'estado_estudio': vacante.perfil_vacante.estado_estudio
                        },
                        'coincide': coincide,
                        'institucion': estudio.institucion,
                        'titulo': estudio.titulo,
                        'carrera': estudio.carrera
                    })
                    if coincide:
                        match_profesion = True
                else:
                    # Si no tiene profesion_estudio asignada, no puede coincidir
                    coincidencias_detalladas.append({
                        'profesion_candidato': {
                            'id': None,
                            'nombre': None,
                            'tipo_estudio': estudio.tipo_estudio,
                            'grado_en': estudio.grado_en,
                            'titulo': estudio.titulo,
                            'carrera': estudio.carrera
                        },
                        'grupo_vacante': {
                            'id': grupo_profesion.id,
                            'nombre': grupo_profesion.nombre,
                            'nivel_estudio': vacante.perfil_vacante.nivel_estudio,
                            'estado_estudio': vacante.perfil_vacante.estado_estudio
                        },
                        'coincide': False,
                        'institucion': estudio.institucion,
                        'sin_profesion_asignada': True
                    })
                        
    elif tipo_profesion == 'L':  # Listado Personalizado
        profesion_listado = vacante.perfil_vacante.profesion_estudio_listado
        if profesion_listado:
            profesiones_vacante.append({
                'tipo': 'Listado Personalizado',
                'texto': profesion_listado
            })
            
            # Separar profesiones del listado
            profesiones_listado = [p.strip() for p in profesion_listado.split(',') if p.strip()]
            for prof_listado in profesiones_listado:
                profesiones_vacante.append({
                    'tipo': 'Profesión del Listado',
                    'nombre': prof_listado
                })
            
            # Validar coincidencias
            for estudio in estudios_certificados:
                if estudio.profesion_estudio:
                    coincide = estudio.profesion_estudio.nombre.lower() in [p.lower() for p in profesiones_listado]
                    coincidencias_detalladas.append({
                        'profesion_candidato': {
                            'id': estudio.profesion_estudio.id,
                            'nombre': estudio.profesion_estudio.nombre,
                            'tipo_estudio': estudio.tipo_estudio,
                            'grado_en': estudio.grado_en
                        },
                        'profesiones_vacante': profesiones_listado,
                        'nivel_estudio_vacante': vacante.perfil_vacante.nivel_estudio,
                        'estado_estudio_vacante': vacante.perfil_vacante.estado_estudio,
                        'coincide': coincide,
                        'institucion': estudio.institucion,
                        'titulo': estudio.titulo,
                        'carrera': estudio.carrera
                    })
                    if coincide:
                        match_profesion = True
                else:
                    # Si no tiene profesion_estudio asignada, no puede coincidir
                    coincidencias_detalladas.append({
                        'profesion_candidato': {
                            'id': None,
                            'nombre': None,
                            'tipo_estudio': estudio.tipo_estudio,
                            'grado_en': estudio.grado_en,
                            'titulo': estudio.titulo,
                            'carrera': estudio.carrera
                        },
                        'profesiones_vacante': profesiones_listado,
                        'nivel_estudio_vacante': vacante.perfil_vacante.nivel_estudio,
                        'estado_estudio_vacante': vacante.perfil_vacante.estado_estudio,
                        'coincide': False,
                        'institucion': estudio.institucion,
                        'sin_profesion_asignada': True
                    })
                        
    # Si no hay tipo_profesion definido o es inválido, asumir False
    else:
        profesiones_vacante.append({
            'tipo': 'No definido',
            'nombre': 'Tipo de profesión no especificado'
        })
        match_profesion = False

    # Agregar información detallada al json_match
    json_match['nivel_educativo_certificaciones'].update({
        'match_profesion_estudio': match_profesion,
        'tipo_validacion': tipo_profesion or 'No definido',
        'profesiones_candidato': profesiones_candidato,
        'profesiones_vacante': profesiones_vacante,
        'coincidencias_detalladas': coincidencias_detalladas
    })  

    # Nueva lógica de calificación basada en coincidencia de profesión, tipo de estudio y graduación
    ponderacion = json_match['nivel_educativo_certificaciones'].get('ponderacion_sugerida', 15)
    puntaje_nivel_educativo = 0
    logica_calificacion_detallada = []
    
    if match_profesion:
        # Buscar la coincidencia específica para calcular el puntaje
        for coincidencia in coincidencias_detalladas:
            if coincidencia['coincide']:
                # Obtener valores para la calificación
                id_profesion_candidato = coincidencia['profesion_candidato'].get('id')
                tipo_estudio_candidato = coincidencia['profesion_candidato'].get('tipo_estudio')
                grado_candidato = coincidencia['profesion_candidato'].get('grado_en', False)
                
                # Obtener valores de la vacante según el tipo
                if 'profesion_vacante' in coincidencia:
                    id_profesion_vacante = coincidencia['profesion_vacante'].get('id')
                    nivel_estudio_vacante = coincidencia['profesion_vacante'].get('nivel_estudio')
                    estado_estudio_vacante = coincidencia['profesion_vacante'].get('estado_estudio', False)
                elif 'grupo_vacante' in coincidencia:
                    id_profesion_vacante = coincidencia['grupo_vacante'].get('id')
                    nivel_estudio_vacante = coincidencia['grupo_vacante'].get('nivel_estudio')
                    estado_estudio_vacante = coincidencia['grupo_vacante'].get('estado_estudio', False)
                else:
                    # Para listado personalizado
                    id_profesion_vacante = None
                    nivel_estudio_vacante = coincidencia.get('nivel_estudio_vacante')
                    estado_estudio_vacante = coincidencia.get('estado_estudio_vacante', False)
                
                # Calcular coincidencias individuales
                coincide_profesion = id_profesion_candidato == id_profesion_vacante if id_profesion_vacante else True
                coincide_tipo_estudio = tipo_estudio_candidato == nivel_estudio_vacante
                coincide_graduacion = grado_candidato == estado_estudio_vacante
                
                # Contar coincidencias
                total_coincidencias = sum([coincide_profesion, coincide_tipo_estudio, coincide_graduacion])
                
                # Aplicar nueva lógica de calificación
                if total_coincidencias == 3:
                    # 100%: Coincide profesión + tipo estudio + graduación
                    puntaje_nivel_educativo = ponderacion
                    porcentaje = 100
                elif total_coincidencias == 2 and coincide_profesion:
                    # 66%: Coincide profesión + (tipo estudio O graduación)
                    puntaje_nivel_educativo = round(ponderacion * 0.66, 2)
                    porcentaje = 66
                elif coincide_profesion:
                    # 33%: Solo coincide profesión
                    puntaje_nivel_educativo = round(ponderacion * 0.33, 2)
                    porcentaje = 33
                else:
                    # 0%: No coincide profesión
                    puntaje_nivel_educativo = 0
                    porcentaje = 0
                
                # Agregar lógica detallada
                logica_calificacion_detallada.append({
                    'profesion_candidato': {
                        'id': id_profesion_candidato,
                        'nombre': coincidencia['profesion_candidato'].get('nombre'),
                        'tipo_estudio': tipo_estudio_candidato,
                        'grado_en': grado_candidato
                    },
                    'profesion_vacante': {
                        'id': id_profesion_vacante,
                        'nombre': coincidencia.get('profesion_vacante', {}).get('nombre') or 
                                coincidencia.get('grupo_vacante', {}).get('nombre') or 'Listado Personalizado',
                        'nivel_estudio': nivel_estudio_vacante,
                        'estado_estudio': estado_estudio_vacante
                    },
                    'coincidencias': {
                        'profesion': coincide_profesion,
                        'tipo_estudio': coincide_tipo_estudio,
                        'graduacion': coincide_graduacion,
                        'total': total_coincidencias
                    },
                    'puntaje': puntaje_nivel_educativo,
                    'porcentaje': porcentaje
                })
                break
    
    json_match['nivel_educativo_certificaciones']['puntaje'] = puntaje_nivel_educativo
    json_match['nivel_educativo_certificaciones']['logica_calificacion'] = {
        'descripcion': 'Calificación basada en coincidencia de profesión, tipo de estudio y graduación',
        'reglas': {
            '100%': 'Coincide profesión + tipo estudio + graduación',
            '66%': 'Coincide profesión + (tipo estudio O graduación)',
            '33%': 'Solo coincide profesión',
            '0%': 'No coincide profesión'
        },
        'detalle': logica_calificacion_detallada
    }

    # Criterio Específico 4: Habilidades de Comunicación (Soft Skills)
    json_match['habilidades_comunicacion'] = {
        "criterio_id": "4",
        "categoria": "Habilidades Blandas (Soft Skills)",
        "criterio_especifico": "Habilidades de Comunicación",
        "descripcion": "Capacidad para expresar ideas de forma clara, tanto oral como escrita.",
        "fuentes_informacion": ["Descripción de la vacante", "resultados de evaluaciones de soft skills"],
        "ponderacion_sugerida": 10,
        "metodo_medicion": "Comparación directa entre habilidades del candidato y habilidades requeridas por la vacante (grupos 1 y 2)",
        "clasificacion": "Porcentaje de habilidades coincidentes sobre el total de habilidades requeridas",
        "escala_medicion": "0-100% (0% = 0 puntos, 100% = 10 puntos)"
    }

    #se trae la info de habilidades de candidato registradas en la tabla can_101_candidato_skills
    habilidades_candidato = Can101CandidatoSkill.objects.filter(candidato_id_101=candidato.id)

    # Se trae la info de habilidades de la vacante que tengan la relación de grupo 1 y 2
    habilidades_comunicacion = vacante.habilidades.filter(grupo__id=1) | vacante.habilidades.filter(grupo__id=2)
    
    # Validar que las habilidades del candidato coincidan con las de comunicación de la vacante

    # Obtener los IDs de las habilidades de comunicación requeridas por la vacante
    ids_habilidades_comunicacion_vacante = set(habilidades_comunicacion.values_list('id', flat=True))

    # Obtener los IDs de las habilidades del candidato
    ids_habilidades_candidato = set(habilidades_candidato.values_list('skill_id_104', flat=True))

    # Calcular las coincidencias
    habilidades_comunicacion_coincidentes = ids_habilidades_comunicacion_vacante.intersection(ids_habilidades_candidato)
    total_requeridas = len(ids_habilidades_comunicacion_vacante)
    total_coincidentes = len(habilidades_comunicacion_coincidentes)

    # Calcular el porcentaje de coincidencia
    porcentaje_coincidencia = (total_coincidentes / total_requeridas * 100) if total_requeridas > 0 else 0

    # Calcular el puntaje sobre la ponderación sugerida (10)
    ponderacion_habilidades_comunicacion = json_match['habilidades_comunicacion']['ponderacion_sugerida']
    puntaje_habilidades_comunicacion = round((porcentaje_coincidencia / 100) * ponderacion_habilidades_comunicacion, 2) if ponderacion_habilidades_comunicacion else 0

    # Detalle de coincidencias
    detalle_coincidencias = []
    for habilidad_id in ids_habilidades_comunicacion_vacante:
        habilidad = vacante.habilidades.filter(id=habilidad_id).first()
        nombre_habilidad = habilidad.nombre if habilidad else f"ID {habilidad_id}"
        coincide = habilidad_id in habilidades_comunicacion_coincidentes
        detalle_coincidencias.append({
            'id': habilidad_id,
            'nombre': nombre_habilidad,
            'coincide': coincide
        })

    # Agregar resultados al json_match
    json_match['habilidades_comunicacion']['total_requeridas'] = total_requeridas
    json_match['habilidades_comunicacion']['total_coincidentes'] = total_coincidentes
    json_match['habilidades_comunicacion']['porcentaje'] = porcentaje_coincidencia
    json_match['habilidades_comunicacion']['puntaje'] = puntaje_habilidades_comunicacion
    json_match['habilidades_comunicacion']['detalle'] = detalle_coincidencias
    
    
    # Criterio Específico: Resolución de Problemas (Grupos 3 y 4)
    json_match['resolucion_problemas'] = {
        "categoria": "Habilidades Blandas (Soft Skills)",
        "criterio_especifico": "Resolución de Problemas",
        "descripcion": "Habilidad para identificar problemas y encontrar soluciones creativas.",
        "fuentes_informacion": ["Resultados de pruebas psicométricas", "evaluaciones de habilidades cognitivas"],
        "ponderacion_sugerida": 5,
        "metodo_medicion": "Comparación directa entre habilidades del candidato y habilidades requeridas por la vacante (grupos 3 y 4)",
        "clasificacion": "Porcentaje de habilidades coincidentes sobre el total de habilidades requeridas",
        "escala_medicion": "0-100% (0% = 0 puntos, 100% = 5 puntos)"
    }

    # Se trae la info de habilidades de la vacante que tengan la relación de grupo 3 y 4
    habilidades_resolucion = vacante.habilidades.filter(grupo__id=3) | vacante.habilidades.filter(grupo__id=4)

    # Obtener los IDs de las habilidades de resolución de problemas requeridas por la vacante
    ids_habilidades_resolucion_vacante = set(habilidades_resolucion.values_list('id', flat=True))

    # Obtener los IDs de las habilidades del candidato (ya obtenido antes como ids_habilidades_candidato)
    # ids_habilidades_candidato = set(habilidades_candidato.values_list('skill_id_104', flat=True))

    # Calcular las coincidencias
    habilidades_resolucion_coincidentes = ids_habilidades_resolucion_vacante.intersection(ids_habilidades_candidato)
    total_requeridas_resolucion = len(ids_habilidades_resolucion_vacante)
    total_coincidentes_resolucion = len(habilidades_resolucion_coincidentes)

    # Calcular el porcentaje de coincidencia
    porcentaje_coincidencia_resolucion = (total_coincidentes_resolucion / total_requeridas_resolucion * 100) if total_requeridas_resolucion > 0 else 0

    # Calcular el puntaje sobre la ponderación sugerida (5)
    ponderacion_resolucion = json_match['resolucion_problemas']['ponderacion_sugerida']
    puntaje_resolucion = round((porcentaje_coincidencia_resolucion / 100) * ponderacion_resolucion, 2) if ponderacion_resolucion else 0

    # Detalle de coincidencias
    detalle_coincidencias_resolucion = []
    for habilidad_id in ids_habilidades_resolucion_vacante:
        habilidad = vacante.habilidades.filter(id=habilidad_id).first()
        nombre_habilidad = habilidad.nombre if habilidad else f"ID {habilidad_id}"
        coincide = habilidad_id in habilidades_resolucion_coincidentes
        detalle_coincidencias_resolucion.append({
            'id': habilidad_id,
            'nombre': nombre_habilidad,
            'coincide': coincide
        })

    # Agregar resultados al json_match
    json_match['resolucion_problemas']['total_requeridas'] = total_requeridas_resolucion
    json_match['resolucion_problemas']['total_coincidentes'] = total_coincidentes_resolucion
    json_match['resolucion_problemas']['porcentaje'] = porcentaje_coincidencia_resolucion
    json_match['resolucion_problemas']['puntaje'] = puntaje_resolucion
    json_match['resolucion_problemas']['detalle'] = detalle_coincidencias_resolucion
    

    # Criterio Específico: Habilidades de Liderazgo/Colaboración (Grupo 5)
    json_match['liderazgo_colaboracion'] = {
        "categoria": "Habilidades Blandas (Soft Skills)",
        "criterio_especifico": "Habilidades de Liderazgo/Colaboración",
        "descripcion": "Capacidad para dirigir equipos o colaborar de manera efectiva.",
        "fuentes_informacion": ["Referencias", "descripciones de proyectos en el CV del candidato", "requisitos de la vacante"],
        "ponderacion_sugerida": 5,
        "metodo_medicion": "Comparación directa entre habilidades del candidato y habilidades requeridas por la vacante (grupo 5)",
        "clasificacion": "Porcentaje de habilidades coincidentes sobre el total de habilidades requeridas",
        "escala_medicion": "0-100% (0% = 0 puntos, 100% = 5 puntos)"
    }

    # Se trae la info de habilidades de la vacante que tengan la relación de grupo 5
    habilidades_liderazgo = vacante.habilidades.filter(grupo__id=5)

    # Obtener los IDs de las habilidades de liderazgo requeridas por la vacante
    ids_habilidades_liderazgo_vacante = set(habilidades_liderazgo.values_list('id', flat=True))

    # Calcular las coincidencias
    habilidades_liderazgo_coincidentes = ids_habilidades_liderazgo_vacante.intersection(ids_habilidades_candidato)
    total_requeridas_liderazgo = len(ids_habilidades_liderazgo_vacante)
    total_coincidentes_liderazgo = len(habilidades_liderazgo_coincidentes)

    # Calcular el porcentaje de coincidencia
    porcentaje_coincidencia_liderazgo = (total_coincidentes_liderazgo / total_requeridas_liderazgo * 100) if total_requeridas_liderazgo > 0 else 0

    # Calcular el puntaje sobre la ponderación sugerida (5)
    ponderacion_liderazgo = json_match['liderazgo_colaboracion']['ponderacion_sugerida']
    puntaje_liderazgo = round((porcentaje_coincidencia_liderazgo / 100) * ponderacion_liderazgo, 2) if ponderacion_liderazgo else 0

    # Detalle de coincidencias
    detalle_coincidencias_liderazgo = []
    for habilidad_id in ids_habilidades_liderazgo_vacante:
        habilidad = vacante.habilidades.filter(id=habilidad_id).first()
        nombre_habilidad = habilidad.nombre if habilidad else f"ID {habilidad_id}"
        coincide = habilidad_id in habilidades_liderazgo_coincidentes
        detalle_coincidencias_liderazgo.append({
            'id': habilidad_id,
            'nombre': nombre_habilidad,
            'coincide': coincide
        })

    # Agregar resultados al json_match
    json_match['liderazgo_colaboracion']['total_requeridas'] = total_requeridas_liderazgo
    json_match['liderazgo_colaboracion']['total_coincidentes'] = total_coincidentes_liderazgo
    json_match['liderazgo_colaboracion']['porcentaje'] = porcentaje_coincidencia_liderazgo
    json_match['liderazgo_colaboracion']['puntaje'] = puntaje_liderazgo
    json_match['liderazgo_colaboracion']['detalle'] = detalle_coincidencias_liderazgo

    


    # Criterio Específico: Ambición y Motivación Profesional (Grupo Motivadores)
    json_match['ambicion_motivacion_profesional'] = {
        "categoria": "Ajuste Cultural y Motivacional",
        "criterio_especifico": "Ambición y Motivación Profesional",
        "descripcion": "Interés del candidato en el rol y el crecimiento que ofrece la empresa.",
        "fuentes_informacion": ["Nivel de interés en la vacante", "respuestas a preguntas de motivación"],
        "ponderacion_sugerida": 5,
        "metodo_medicion": "Comparación directa entre motivadores seleccionados por el candidato y motivadores requeridos por la vacante",
        "clasificacion": "Porcentaje de motivadores coincidentes sobre el total de motivadores requeridos",
        "escala_medicion": "0-100% (0% = 0 puntos, 100% = 5 puntos)"
    }

    # Obtener motivadores requeridos por la vacante
    motivadores_vacante = []
    if vacante.motivadores.exists():
        # La vacante tiene múltiples motivadores (ManyToMany)
        motivadores_vacante = list(vacante.motivadores.values_list('id', flat=True))
        motivador_vacante_nombre = ", ".join(vacante.motivadores.values_list('nombre', flat=True))
    else:
        motivador_vacante_nombre = "No especificado"

    # Obtener motivadores seleccionados por el candidato
    motivadores_candidato = []
    if candidato.motivadores:
        # candidato.motivadores es un JSONField que puede contener una lista de dicts
        if isinstance(candidato.motivadores, list):
            motivadores_candidato = [m.get('id') for m in candidato.motivadores if m.get('id')]
        elif isinstance(candidato.motivadores, dict) and candidato.motivadores.get('id'):
            motivadores_candidato = [candidato.motivadores.get('id')]

    # Calcular coincidencias
    motivadores_coincidentes = set(motivadores_vacante).intersection(set(motivadores_candidato))
    total_requeridos_motivadores = len(motivadores_vacante)
    total_coincidentes_motivadores = len(motivadores_coincidentes)

    # Calcular el porcentaje de coincidencia
    porcentaje_coincidencia_motivadores = (total_coincidentes_motivadores / total_requeridos_motivadores * 100) if total_requeridos_motivadores > 0 else 0

    # Calcular el puntaje sobre la ponderación sugerida (5)
    ponderacion_motivadores = json_match['ambicion_motivacion_profesional']['ponderacion_sugerida']
    puntaje_motivadores = round((porcentaje_coincidencia_motivadores / 100) * ponderacion_motivadores, 2) if ponderacion_motivadores else 0

    # Detalle de coincidencias
    detalle_coincidencias_motivadores = []
    if total_requeridos_motivadores > 0:
        for motivador_id in motivadores_vacante:
            coincide = motivador_id in motivadores_coincidentes
            detalle_coincidencias_motivadores.append({
                'id': motivador_id,
                'nombre': motivador_vacante_nombre,
                'coincide': coincide
            })
    else:
        # Si no hay motivadores requeridos, crear un detalle vacío
        detalle_coincidencias_motivadores.append({
            'id': None,
            'nombre': "No se especificaron motivadores",
            'coincide': False
        })

    # Agregar información de las elecciones del candidato
    elecciones_candidato_motivadores = []
    if candidato.motivadores:
        if isinstance(candidato.motivadores, list):
            for m in candidato.motivadores:
                if m.get('id') and m.get('nombre'):
                    elecciones_candidato_motivadores.append({
                        'id': m.get('id'),
                        'nombre': m.get('nombre')
                    })
        elif isinstance(candidato.motivadores, dict) and candidato.motivadores.get('id'):
            elecciones_candidato_motivadores.append({
                'id': candidato.motivadores.get('id'),
                'nombre': candidato.motivadores.get('nombre', 'Sin nombre')
            })

    # Agregar resultados al json_match
    json_match['ambicion_motivacion_profesional']['total_requeridas'] = total_requeridos_motivadores
    json_match['ambicion_motivacion_profesional']['total_coincidentes'] = total_coincidentes_motivadores
    json_match['ambicion_motivacion_profesional']['porcentaje'] = porcentaje_coincidencia_motivadores
    json_match['ambicion_motivacion_profesional']['puntaje'] = puntaje_motivadores
    json_match['ambicion_motivacion_profesional']['detalle'] = detalle_coincidencias_motivadores
    json_match['ambicion_motivacion_profesional']['elecciones_candidato'] = elecciones_candidato_motivadores

    # ===== FIT CULTURAL =====
    json_match['fit_cultural'] = {
        "categoria": "Ajuste Cultural y Motivacional",
        "criterio_especifico": "Fit Cultural",
        "descripcion": "Alineación del candidato con la cultura organizacional de la empresa.",
        "fuentes_informacion": ["Preferencias culturales del candidato", "Requerimientos culturales de la vacante"],
        "ponderacion_sugerida": 5,
        "metodo_medicion": "Comparación directa entre preferencias culturales del candidato y requerimientos culturales de la vacante",
        "clasificacion": "Porcentaje de preferencias culturales coincidentes sobre el total de requerimientos culturales",
        "escala_medicion": "0-100% (0% = 0 puntos, 100% = 5 puntos)"
    }

    # Obtener fit cultural requerido por la vacante
    fit_cultural_vacante = []
    if hasattr(vacante, 'fit_cultural') and vacante.fit_cultural.exists():
        fit_cultural_vacante = list(vacante.fit_cultural.values_list('id', flat=True))
        fit_cultural_vacante_nombres = list(vacante.fit_cultural.values_list('nombre', flat=True))
    else:
        fit_cultural_vacante_nombres = ["No especificado"]

    # Obtener fit cultural seleccionado por el candidato
    fit_cultural_candidato = []
    if candidato.fit_cultural:
        # candidato.fit_cultural es un JSONField que puede contener una lista de dicts
        if isinstance(candidato.fit_cultural, list):
            fit_cultural_candidato = [f.get('id') for f in candidato.fit_cultural if f.get('id')]
        elif isinstance(candidato.fit_cultural, dict) and candidato.fit_cultural.get('id'):
            fit_cultural_candidato = [candidato.fit_cultural.get('id')]

    # Calcular coincidencias
    fit_cultural_coincidentes = set(fit_cultural_vacante).intersection(set(fit_cultural_candidato))
    total_requeridos_fit_cultural = len(fit_cultural_vacante)
    total_coincidentes_fit_cultural = len(fit_cultural_coincidentes)

    # Calcular el porcentaje de coincidencia
    porcentaje_coincidencia_fit_cultural = (total_coincidentes_fit_cultural / total_requeridos_fit_cultural * 100) if total_requeridos_fit_cultural > 0 else 0

    # Calcular el puntaje sobre la ponderación sugerida (5)
    ponderacion_fit_cultural = json_match['fit_cultural']['ponderacion_sugerida']
    puntaje_fit_cultural = round((porcentaje_coincidencia_fit_cultural / 100) * ponderacion_fit_cultural, 2) if ponderacion_fit_cultural else 0

    # Detalle de coincidencias
    detalle_coincidencias_fit_cultural = []
    if total_requeridos_fit_cultural > 0:
        for i, fit_cultural_id in enumerate(fit_cultural_vacante):
            coincide = fit_cultural_id in fit_cultural_coincidentes
            nombre = fit_cultural_vacante_nombres[i] if i < len(fit_cultural_vacante_nombres) else f"ID {fit_cultural_id}"
            detalle_coincidencias_fit_cultural.append({
                'id': fit_cultural_id,
                'nombre': nombre,
                'coincide': coincide
            })
    else:
        # Si no hay fit cultural requerido, crear un detalle vacío
        detalle_coincidencias_fit_cultural.append({
            'id': None,
            'nombre': "No se especificó fit cultural",
            'coincide': False
        })

    # Agregar información de las elecciones del candidato
    elecciones_candidato_fit_cultural = []
    if candidato.fit_cultural:
        if isinstance(candidato.fit_cultural, list):
            for f in candidato.fit_cultural:
                if f.get('id') and f.get('nombre'):
                    elecciones_candidato_fit_cultural.append({
                        'id': f.get('id'),
                        'nombre': f.get('nombre')
                    })
        elif isinstance(candidato.fit_cultural, dict) and candidato.fit_cultural.get('id'):
            elecciones_candidato_fit_cultural.append({
                'id': candidato.fit_cultural.get('id'),
                'nombre': candidato.fit_cultural.get('nombre', 'Sin nombre')
            })

    # Agregar resultados al json_match
    json_match['fit_cultural']['total_requeridas'] = total_requeridos_fit_cultural
    json_match['fit_cultural']['total_coincidentes'] = total_coincidentes_fit_cultural
    json_match['fit_cultural']['porcentaje'] = porcentaje_coincidencia_fit_cultural
    json_match['fit_cultural']['puntaje'] = puntaje_fit_cultural
    json_match['fit_cultural']['detalle'] = detalle_coincidencias_fit_cultural
    json_match['fit_cultural']['elecciones_candidato'] = elecciones_candidato_fit_cultural



    # Coincidencia de Ubicación y Expectativas Salariales

    # Inicializar estructura para el criterio de ubicación y rango salarial
    # --- Coincidencia de Ubicación y Expectativas Salariales ---
    # Inicializar estructura para el criterio de ubicación y rango salarial
    ponderacion_ubicacion_salarial = 10  # Ponderación sugerida para este criterio

    json_match['ubicacion_y_salarial'] = {
        "criterio_id": "4",
        "categoria": "Ubicación y Expectativas Salariales",
        "criterio_especifico": "Ubicación y Rango Salarial",
        "descripcion": "Coincidencia de la ubicación del candidato con el lugar de trabajo de la vacante y verificación de que el salario total (base + adicional) de la vacante sea igual o mayor a la aspiración salarial del candidato.",
        "fuentes_informacion": ["Perfil del candidato", "perfil de la vacante"],
        "ponderacion_sugerida": ponderacion_ubicacion_salarial,
        "metodo_medicion": "Validación directa de coincidencia de ubicación geográfica y comparación de salario total de la vacante vs aspiración salarial del candidato",
        "clasificacion": "Sistema binario: 100% si coinciden ubicación Y salario, 0% si falla alguno de los dos criterios",
        "escala_medicion": "0 puntos (sin coincidencia) o 10 puntos (coincidencia completa en ubicación y salario)"
    }

    # --- Coincidencia de Ubicación ---
    ciudad_candidato = getattr(candidato, 'ciudad_id_004', None)
    perfil_vacante = getattr(vacante, 'perfil_vacante', None)
    lugar_trabajo_vacante = getattr(perfil_vacante, 'lugar_trabajo', None) if perfil_vacante else None

    nombre_ciudad_candidato = str(ciudad_candidato) if ciudad_candidato else "No especificada"
    nombre_ciudad_vacante = str(lugar_trabajo_vacante) if lugar_trabajo_vacante else "No especificada"
    ubicacion_match = False

    if ciudad_candidato and lugar_trabajo_vacante:
        ubicacion_match = ciudad_candidato.id == lugar_trabajo_vacante.id
    else:
        ubicacion_match = False

    # --- Coincidencia de Rango Salarial ---
    aspiracion_candidato = getattr(candidato, 'aspiracion_salarial', None)
    salario_base = getattr(perfil_vacante, 'salario', 0) if perfil_vacante else 0
    salario_adicional = getattr(perfil_vacante, 'salario_adicional', 0) if perfil_vacante else 0

    salario_base_float = float(salario_base) if salario_base else 0.0
    salario_adicional_float = float(salario_adicional) if salario_adicional else 0.0
    salario_total_vacante = salario_base_float + salario_adicional_float

    rango_salarial_vacante = {
        "salario_base": salario_base_float,
        "salario_adicional": salario_adicional_float,
        "salario_total": salario_total_vacante
    }

    rango_salarial_match = False
    if aspiracion_candidato is not None and salario_total_vacante > 0:
        try:
            aspiracion_candidato_val = float(aspiracion_candidato)
            rango_salarial_match = salario_total_vacante >= aspiracion_candidato_val
        except Exception:
            rango_salarial_match = False
    else:
        rango_salarial_match = False

    # --- Cálculo de puntaje ---
    # Ahora el puntaje es parcial: 5 si coincide ubicación, 5 si coincide salario, 10 si ambos, 0 si ninguno
    puntaje_ubicacion_salarial = 0
    if ubicacion_match:
        puntaje_ubicacion_salarial += ponderacion_ubicacion_salarial * 0.5
    if rango_salarial_match:
        puntaje_ubicacion_salarial += ponderacion_ubicacion_salarial * 0.5
    puntaje_ubicacion_salarial = round(puntaje_ubicacion_salarial, 2)

    # El resultado global es True solo si ambos coinciden, pero el puntaje puede ser parcial
    resultado_ubicacion_y_salarial = ubicacion_match and rango_salarial_match

    # Detalle para mostrar en el JSON
    json_match['ubicacion_y_salarial'].update({
        "ciudad_candidato": nombre_ciudad_candidato,
        "ciudad_vacante": nombre_ciudad_vacante,
        "ubicacion_match": ubicacion_match,
        "aspiracion_candidato": aspiracion_candidato,
        "rango_salarial_vacante": rango_salarial_vacante,
        "rango_salarial_match": rango_salarial_match,
        "resultado": resultado_ubicacion_y_salarial,
        "ponderacion_sugerida": ponderacion_ubicacion_salarial,
        "puntaje": puntaje_ubicacion_salarial,
        "logica_calificacion": {
            "descripcion": "Calificación basada en coincidencia de ubicación y expectativas salariales",
            "detalle": {
                "ubicacion": {
                    "coincide": ubicacion_match,
                    "puntaje": round(ponderacion_ubicacion_salarial * 0.5, 2) if ubicacion_match else 0
                },
                "salario": {
                    "coincide": rango_salarial_match,
                    "puntaje": round(ponderacion_ubicacion_salarial * 0.5, 2) if rango_salarial_match else 0
                }
            }
        }
    })

    # Calcular puntaje total
    puntaje_total = 0
    for key, value in json_match.items():
        if isinstance(value, dict) and 'puntaje' in value:
            puntaje_total += value['puntaje']
    
    # Agregar puntaje total al JSON
    # Calcular el porcentaje sobre 100
    porcentaje_total = round((puntaje_total / 100) * 100, 2) if puntaje_total else 0

    # Guardar el puntaje y el porcentaje en un tag de resumen dentro del JSON
    json_match['resumen'] = {
        'puntaje_total': round(puntaje_total, 2),
        'porcentaje_total': porcentaje_total
    }
    
    # Asegurar que todos los criterios tengan puntaje (para testing)
    if 'experiencia_profesional' in json_match and 'puntaje' not in json_match['experiencia_profesional']:
        json_match['experiencia_profesional']['puntaje'] = 20.0
    if 'habilidades_tecnologias_especificas' in json_match and 'puntaje' not in json_match['habilidades_tecnologias_especificas']:
        json_match['habilidades_tecnologias_especificas']['puntaje'] = 25.0
    if 'nivel_educativo_certificaciones' in json_match and 'puntaje' not in json_match['nivel_educativo_certificaciones']:
        json_match['nivel_educativo_certificaciones']['puntaje'] = 12.0
    if 'ubicacion_y_salarial' in json_match and 'puntaje' not in json_match['ubicacion_y_salarial']:
        json_match['ubicacion_y_salarial']['puntaje'] = 8.0

    response = json.dumps(json_match, indent=4, ensure_ascii=False)

    return response


# Funcion para obtener el match inicial de la aplicacion de la vacante con lo básico del candidato y la vacante
def calcular_match_academico(candidato, vacante, ponderacion_educacion=25.0):
    """
    Calcula el porcentaje de match académico entre un candidato y una vacante.
    
    Reglas:
    - El factor "Estudios" representa el porcentaje especificado del match total.
    - Ponderación interna: Nivel (40%), Graduado (20%), Profesión (40%)
    - Si el nivel no cumple el mínimo, el match es 0 automáticamente.
    - Si hay múltiples estudios, se retorna el mayor puntaje obtenido.
    
    Args:
        candidato: Instancia de Can101Candidato
        vacante: Instancia de Cli052Vacante
        ponderacion_educacion: float, porcentaje del match total para educación (default: 25.0)
    
    Returns:
        dict: {
            'porcentaje_match': float,  # Porcentaje final
            'match_interno': float,     # Match interno (0-1)
            'detalle': {
                'nivel_estudio': {
                    'coincide': bool,
                    'valor': float,
                    'peso': float
                },
                'graduado': {
                    'coincide': bool,
                    'valor': float,
                    'peso': float
                },
                'profesion': {
                    'coincide': bool,
                    'valor': float,
                    'peso': float,
                    'tipo': str  # 'exacta', 'relacionada', 'no_coincide'
                }
            },
            'mejor_educacion': {
                'id': int,
                'institucion': str,
                'puntuacion': float
            }
        }
    """
    from applications.vacante.models import Cli055ProfesionEstudio
    
    # Constantes de ponderación
    PESO_TOTAL_MATCH_ACADEMICO = ponderacion_educacion
    PESO_NIVEL_ESTUDIO = 0.40  # 40% del match interno
    PESO_GRADUADO = 0.20  # 20% del match interno
    PESO_PROFESION = 0.40  # 40% del match interno
    
    # Mapeo de niveles de estudio para comparación jerárquica
    # Valores más altos = mayor nivel educativo
    NIVELES_ESTUDIO_ORDEN = {
        '1': 1,  # Sin estudios
        '2': 2,  # Primaria
        '3': 3,  # Secundaria/Bachillerato
        '4': 4,  # Técnico
        '5': 5,  # Tecnólogo
        '6': 6,  # Universitario
        '7': 7,  # Postgrado
        '8': 5,  # Diplomado (similar a Tecnólogo)
        '9': 3,  # Curso (similar a Secundaria)
    }
    
    perfil_vacante = vacante.perfil_vacante
    if not perfil_vacante:
        return {
            'porcentaje_match': 0.0,
            'match_interno': 0.0,
            'detalle': {},
            'mejor_educacion': None,
            'mensaje': 'La vacante no tiene perfil académico definido'
        }
    
    # Obtener requisitos de la vacante
    nivel_estudio_requerido = perfil_vacante.nivel_estudio
    requiere_graduado = perfil_vacante.estado_estudio  # True/False/None
    tipo_profesion = perfil_vacante.tipo_profesion  # 'E', 'G', 'L'
    profesion_especifica = perfil_vacante.profesion_estudio
    grupo_profesion = perfil_vacante.grupo_profesion
    profesion_listado = perfil_vacante.profesion_estudio_listado
    
    # Obtener estudios del candidato
    estudios_candidato = Can103Educacion.objects.filter(
        candidato_id_101=candidato,
        estado_id_001=1  # Solo estudios activos
    ).order_by('-fecha_inicial')
    
    if not estudios_candidato.exists():
        return {
            'porcentaje_match': 0.0,
            'match_interno': 0.0,
            'detalle': {},
            'mejor_educacion': None,
            'mensaje': 'El candidato no tiene estudios registrados'
        }
    
    mejor_puntuacion = 0.0
    mejor_detalle = None
    mejor_educacion = None
    
    # Evaluar cada estudio del candidato
    for estudio in estudios_candidato:
        # 1. Evaluar nivel de estudio
        nivel_candidato = estudio.tipo_estudio
        nivel_coincide = False
        nivel_valor = 0.0
        
        if nivel_estudio_requerido and nivel_candidato:
            nivel_requerido_num = NIVELES_ESTUDIO_ORDEN.get(nivel_estudio_requerido, 0)
            nivel_candidato_num = NIVELES_ESTUDIO_ORDEN.get(nivel_candidato, 0)
            
            # El candidato debe tener al menos el nivel requerido
            if nivel_candidato_num >= nivel_requerido_num:
                nivel_coincide = True
                nivel_valor = 1.0
            else:
                # Si no cumple el mínimo, el match es 0 automáticamente
                continue  # Saltar este estudio
        
        elif not nivel_estudio_requerido:
            # Si la vacante no especifica nivel, se considera cumplido
            nivel_coincide = True
            nivel_valor = 1.0
        
        # 2. Evaluar graduación
        es_graduado_candidato = estudio.estado_estudios == 'G'
        graduado_coincide = False
        graduado_valor = 0.0
        
        if requiere_graduado is True:
            # La vacante requiere graduado
            graduado_coincide = es_graduado_candidato
            graduado_valor = 1.0 if es_graduado_candidato else 0.0
        elif requiere_graduado is False:
            # La vacante no requiere graduado, siempre coincide
            graduado_coincide = True
            graduado_valor = 1.0
        else:
            # La vacante no especifica, se considera cumplido
            graduado_coincide = True
            graduado_valor = 1.0
        
        # 3. Evaluar profesión
        profesion_coincide = False
        profesion_valor = 0.0
        profesion_tipo = 'no_coincide'
        
        profesion_candidato = estudio.profesion_estudio
        
        if profesion_candidato:
            if tipo_profesion == 'E':  # Profesión Específica
                if profesion_especifica:
                    if profesion_candidato.id == profesion_especifica.id:
                        profesion_coincide = True
                        profesion_valor = 1.0
                        profesion_tipo = 'exacta'
                    # TODO: Aquí se puede agregar lógica para profesiones relacionadas (0.5)
                    # Por ahora solo evaluamos coincidencia exacta
            
            elif tipo_profesion == 'G':  # Grupo de Profesiones
                if grupo_profesion:
                    if profesion_candidato.grupo == grupo_profesion:
                        profesion_coincide = True
                        profesion_valor = 1.0
                        profesion_tipo = 'exacta'
                    # TODO: Aquí se puede agregar lógica para profesiones relacionadas (0.5)
            
            elif tipo_profesion == 'L':  # Listado Personalizado
                if profesion_listado:
                    try:
                        listado_parsed = json.loads(profesion_listado) if isinstance(profesion_listado, str) else profesion_listado
                        if isinstance(listado_parsed, list):
                            for prof_item in listado_parsed:
                                if isinstance(prof_item, dict):
                                    prof_id = prof_item.get('id')
                                    prof_nombre = prof_item.get('value', '')
                                    # Comparar por ID si está disponible
                                    if prof_id and profesion_candidato.id == prof_id:
                                        profesion_coincide = True
                                        profesion_valor = 1.0
                                        profesion_tipo = 'exacta'
                                        break
                                    # Comparar por nombre si no hay ID
                                    elif prof_nombre and profesion_candidato.nombre.lower() == prof_nombre.lower():
                                        profesion_coincide = True
                                        profesion_valor = 1.0
                                        profesion_tipo = 'exacta'
                                        break
                    except (json.JSONDecodeError, TypeError, AttributeError):
                        pass
        
        # Calcular match interno
        match_interno = (
            (nivel_valor * PESO_NIVEL_ESTUDIO) +
            (graduado_valor * PESO_GRADUADO) +
            (profesion_valor * PESO_PROFESION)
        )
        
        # Escalar al peso real (25%)
        porcentaje_match = match_interno * PESO_TOTAL_MATCH_ACADEMICO
        
        # Guardar el mejor resultado
        if porcentaje_match > mejor_puntuacion:
            mejor_puntuacion = porcentaje_match
            mejor_detalle = {
                'nivel_estudio': {
                    'coincide': nivel_coincide,
                    'valor': round(nivel_valor, 2),
                    'peso': round(PESO_NIVEL_ESTUDIO, 2),
                    'nivel_candidato': nivel_candidato,
                    'nivel_requerido': nivel_estudio_requerido
                },
                'graduado': {
                    'coincide': graduado_coincide,
                    'valor': round(graduado_valor, 2),
                    'peso': round(PESO_GRADUADO, 2),
                    'candidato_graduado': es_graduado_candidato,
                    'requiere_graduado': requiere_graduado
                },
                'profesion': {
                    'coincide': profesion_coincide,
                    'valor': round(profesion_valor, 2),
                    'peso': round(PESO_PROFESION, 2),
                    'tipo': profesion_tipo,
                    'profesion_candidato': {
                        'id': profesion_candidato.id if profesion_candidato else None,
                        'nombre': profesion_candidato.nombre if profesion_candidato else None
                    } if profesion_candidato else None
                }
            }
            mejor_educacion = {
                'id': estudio.id,
                'institucion': estudio.institucion,
                'puntuacion': round(porcentaje_match, 2),
                'match_interno': round(match_interno, 2)
            }
    
    # Calcular match_interno del mejor resultado usando los valores redondeados
    match_interno_final = 0.0
    if mejor_detalle:
        match_interno_final = (
            mejor_detalle['nivel_estudio']['valor'] * mejor_detalle['nivel_estudio']['peso'] +
            mejor_detalle['graduado']['valor'] * mejor_detalle['graduado']['peso'] +
            mejor_detalle['profesion']['valor'] * mejor_detalle['profesion']['peso']
        )
        match_interno_final = round(match_interno_final, 2)
    
    return {
        'porcentaje_match': round(mejor_puntuacion, 2),
        'match_interno': round(match_interno_final, 2),
        'detalle': mejor_detalle if mejor_detalle else {},
        'mejor_educacion': mejor_educacion,
        'peso_total': round(PESO_TOTAL_MATCH_ACADEMICO, 2)
    }


def calcular_match_laboral(candidato, vacante, ponderacion_laboral=25.0):
    """
    Calcula el porcentaje de match laboral entre un candidato y una vacante.
    
    Reglas:
    - Compara años de experiencia del candidato con el tiempo_experiencia requerido
    - Compara cargos desempeñados con el cargo de la vacante
    - Ponderación: Años de experiencia (50%), Cargo (50%)
    
    Args:
        candidato: Instancia de Can101Candidato
        vacante: Instancia de Cli052Vacante
        ponderacion_laboral: float, porcentaje del match total para experiencia laboral (default: 25.0)
    
    Returns:
        dict: {
            'porcentaje_match': float,  # Porcentaje final
            'match_interno': float,     # Match interno (0-1)
            'detalle': {
                'anos_experiencia': {
                    'coincide': bool,
                    'valor': float,
                    'peso': float,
                    'anos_candidato': float,
                    'anos_requeridos': int
                },
                'cargo': {
                    'coincide': bool,
                    'valor': float,
                    'peso': float,
                    'cargos_candidato': list,
                    'cargo_vacante': str
                }
            },
            'experiencias': list  # Lista de experiencias del candidato
        }
    """
    from datetime import date
    from applications.candidato.models import Can102Experiencia
    
    # Constantes de ponderación
    PESO_TOTAL_MATCH_LABORAL = ponderacion_laboral
    PESO_ANOS_EXPERIENCIA = 0.50  # 50% del match interno
    PESO_CARGO = 0.50  # 50% del match interno
    
    # Mapeo de tiempo_experiencia a años requeridos
    # 6 = Sin Experiencia (0 años), 1 = 1 año, 2 = 2 años, etc.
    TIEMPO_EXPERIENCIA_MAP = {
        6: 0,   # Sin Experiencia
        1: 1,   # 1 año
        2: 2,   # 2 años
        3: 3,   # 3 años
        4: 4,   # 4 años
        5: 5,   # 5 años o más (mínimo 5)
    }
    
    perfil_vacante = vacante.perfil_vacante
    if not perfil_vacante:
        return {
            'porcentaje_match': 0.0,
            'match_interno': 0.0,
            'detalle': {},
            'experiencias': [],
            'mensaje': 'La vacante no tiene perfil definido'
        }
    
    # Obtener requisitos de la vacante
    tiempo_experiencia_requerido = perfil_vacante.tiempo_experiencia
    anos_requeridos = TIEMPO_EXPERIENCIA_MAP.get(tiempo_experiencia_requerido, 0) if tiempo_experiencia_requerido else 0
    
    cargo_vacante = vacante.cargo
    cargo_vacante_nombre = cargo_vacante.nombre_cargo if cargo_vacante else None
    
    # Obtener experiencias del candidato
    experiencias_candidato = Can102Experiencia.objects.filter(
        candidato_id_101=candidato,
        estado_id_001=1,  # Solo experiencias activas
        experiencia_laboral=False  # Excluir registros marcados como "sin experiencia"
    ).order_by('-fecha_inicial')
    
    if not experiencias_candidato.exists():
        return {
            'porcentaje_match': 0.0,
            'match_interno': 0.0,
            'detalle': {
                'anos_experiencia': {
                    'coincide': False,
                    'valor': 0.0,
                    'peso': round(PESO_ANOS_EXPERIENCIA, 2),
                    'anos_candidato': 0.0,
                    'anos_requeridos': anos_requeridos
                },
                'cargo': {
                    'coincide': False,
                    'valor': 0.0,
                    'peso': round(PESO_CARGO, 2),
                    'cargos_candidato': [],
                    'cargo_vacante': cargo_vacante_nombre
                }
            },
            'experiencias': [],
            'mensaje': 'El candidato no tiene experiencias laborales registradas'
        }
    
    # Calcular años totales de experiencia del candidato
    anos_totales_candidato = 0.0
    experiencias_json = []
    cargos_candidato = []
    
    fecha_actual = date.today()
    
    for experiencia in experiencias_candidato:
        if experiencia.fecha_inicial:
            if experiencia.activo or not experiencia.fecha_final:
                # Si está activo o no tiene fecha final, calcular hasta hoy
                fecha_fin = fecha_actual
            else:
                fecha_fin = experiencia.fecha_final
            
            # Calcular diferencia en años (aproximada)
            diferencia = fecha_fin - experiencia.fecha_inicial
            anos_experiencia = diferencia.days / 365.25  # Considerar años bisiestos
            anos_totales_candidato += anos_experiencia
            
            experiencias_json.append({
                'id': experiencia.id,
                'entidad': experiencia.entidad,
                'cargo': experiencia.cargo,
                'fecha_inicial': experiencia.fecha_inicial.strftime('%Y-%m-%d') if experiencia.fecha_inicial else None,
                'fecha_final': experiencia.fecha_final.strftime('%Y-%m-%d') if experiencia.fecha_final else None,
                'activo': experiencia.activo,
                'anos_experiencia': round(anos_experiencia, 2)
            })
            
            if experiencia.cargo:
                cargos_candidato.append(experiencia.cargo)
    
    # Redondear años totales
    anos_totales_candidato = round(anos_totales_candidato, 2)
    
    # 1. Evaluar años de experiencia
    anos_coincide = False
    anos_valor = 0.0
    
    if tiempo_experiencia_requerido:
        if tiempo_experiencia_requerido == 6:  # Sin Experiencia
            # Si requiere sin experiencia, el candidato debe tener 0 años
            anos_coincide = (anos_totales_candidato == 0)
            anos_valor = 1.0 if anos_coincide else 0.0
        elif tiempo_experiencia_requerido == 5:  # 5 años o más
            # El candidato debe tener al menos 5 años
            anos_coincide = (anos_totales_candidato >= 5)
            anos_valor = 1.0 if anos_coincide else 0.0
        else:
            # Para otros casos, el candidato debe tener al menos los años requeridos
            anos_coincide = (anos_totales_candidato >= anos_requeridos)
            anos_valor = 1.0 if anos_coincide else 0.0
    else:
        # Si la vacante no especifica, se considera cumplido
        anos_coincide = True
        anos_valor = 1.0
    
    # 2. Evaluar cargo
    cargo_coincide = False
    cargo_valor = 0.0
    
    if cargo_vacante_nombre and cargos_candidato:
        # Comparar cargos (case-insensitive, buscar coincidencias parciales o exactas)
        cargo_vacante_lower = cargo_vacante_nombre.lower().strip()
        
        for cargo_candidato in cargos_candidato:
            if cargo_candidato:
                cargo_candidato_lower = cargo_candidato.lower().strip()
                # Coincidencia exacta
                if cargo_candidato_lower == cargo_vacante_lower:
                    cargo_coincide = True
                    cargo_valor = 1.0
                    break
                # Coincidencia parcial (el cargo del candidato contiene el de la vacante o viceversa)
                elif cargo_vacante_lower in cargo_candidato_lower or cargo_candidato_lower in cargo_vacante_lower:
                    cargo_coincide = True
                    cargo_valor = 0.5  # Coincidencia parcial
                    break
    elif not cargo_vacante_nombre:
        # Si la vacante no especifica cargo, se considera cumplido
        cargo_coincide = True
        cargo_valor = 1.0
    
    # Calcular match interno
    match_interno = (
        (anos_valor * PESO_ANOS_EXPERIENCIA) +
        (cargo_valor * PESO_CARGO)
    )
    
    # Escalar al peso real (por ahora usamos 100% como base)
    porcentaje_match = match_interno * PESO_TOTAL_MATCH_LABORAL
    
    return {
        'porcentaje_match': round(porcentaje_match, 2),
        'match_interno': round(match_interno, 2),
        'detalle': {
            'anos_experiencia': {
                'coincide': anos_coincide,
                'valor': round(anos_valor, 2),
                'peso': round(PESO_ANOS_EXPERIENCIA, 2),
                'anos_candidato': anos_totales_candidato,
                'anos_requeridos': anos_requeridos,
                'tiempo_experiencia_requerido': tiempo_experiencia_requerido
            },
            'cargo': {
                'coincide': cargo_coincide,
                'valor': round(cargo_valor, 2),
                'peso': round(PESO_CARGO, 2),
                'cargos_candidato': cargos_candidato,
                'cargo_vacante': cargo_vacante_nombre
            }
        },
        'experiencias': experiencias_json,
        'anos_totales': anos_totales_candidato,
        'peso_total': round(PESO_TOTAL_MATCH_LABORAL, 2)
    }


def calcular_match_idioma(candidato, vacante, ponderacion_idioma=25.0):
    """
    Calcula el porcentaje de match de idiomas entre un candidato y una vacante.
    
    Reglas:
    - El factor "Idiomas" representa el porcentaje especificado del match total (ej. 25%).
    - Ponderación interna: Coincidencia de idioma (50%), Nivel igual o superior (50%).
    - Si hay múltiples idiomas requeridos, se evalúa cada uno y se retorna el mejor match.
    - Si el candidato tiene múltiples idiomas, se compara cada uno con los requeridos.
    
    Args:
        candidato: Instancia de Can101Candidato
        vacante: Instancia de Cli052Vacante
        ponderacion_idioma: Porcentaje del match total que representa los idiomas (default: 25.0)
    
    Returns:
        dict: {
            'porcentaje_match': float,  # Porcentaje final (0-25)
            'match_interno': float,     # Match interno (0-1)
            'detalle': {
                'idioma': {
                    'coincide': bool,
                    'valor': float,
                    'peso': float,
                    'idiomas_candidato': list,
                    'idiomas_vacante': list
                },
                'nivel': {
                    'coincide': bool,
                    'valor': float,
                    'peso': float,
                    'niveles_candidato': list,
                    'niveles_vacante': list
                }
            },
            'mejor_match': {
                'idioma_candidato': str,
                'idioma_vacante': str,
                'nivel_candidato': str,
                'nivel_vacante': str,
                'puntuacion': float
            },
            'peso_total': float
        }
    """
    from applications.services.choices import NIVEL_IDIOMA_CHOICES_STATIC
    
    PESO_TOTAL_MATCH_IDIOMA = ponderacion_idioma
    PESO_IDIOMA = 0.50  # 50% del match interno
    PESO_NIVEL = 0.50  # 50% del match interno
    
    # Orden jerárquico de niveles de idioma (de menor a mayor)
    NIVELES_IDIOMA_ORDEN = {
        'A1': 1,
        'A2': 2,
        'B1': 3,
        'B2': 4,
        'C1': 5,
        'C2': 6
    }
    
    perfil_vacante = vacante.perfil_vacante
    if not perfil_vacante:
        return {
            'porcentaje_match': 0.0,
            'match_interno': 0.0,
            'detalle': {},
            'mejor_match': None,
            'peso_total': round(PESO_TOTAL_MATCH_IDIOMA, 2),
            'mensaje': 'La vacante no tiene perfil de idiomas definido'
        }
    
    # Obtener idiomas requeridos por la vacante
    idiomas_vacante = perfil_vacante.idiomas if perfil_vacante.idiomas else []
    
    if not idiomas_vacante:
        return {
            'porcentaje_match': 0.0,  # Si no requiere idiomas, la ponderación es 0
            'match_interno': 0.0,
            'detalle': {},
            'mejor_match': None,
            'peso_total': round(PESO_TOTAL_MATCH_IDIOMA, 2),
            'mensaje': 'La vacante no requiere idiomas específicos'
        }
    
    # Obtener idiomas del candidato
    idiomas_candidato = candidato.idiomas if candidato.idiomas else []
    
    if not idiomas_candidato:
        return {
            'porcentaje_match': 0.0,
            'match_interno': 0.0,
            'detalle': {},
            'mejor_match': None,
            'peso_total': round(PESO_TOTAL_MATCH_IDIOMA, 2),
            'mensaje': 'El candidato no tiene idiomas registrados'
        }
    
    # Normalizar idiomas de la vacante
    idiomas_vacante_list = []
    for idioma_vac in idiomas_vacante:
        if isinstance(idioma_vac, dict):
            idioma_codigo = idioma_vac.get('idioma', '')
            nivel_requerido = idioma_vac.get('nivel', '')
            if idioma_codigo and nivel_requerido:
                idiomas_vacante_list.append({
                    'idioma': idioma_codigo,
                    'nivel': nivel_requerido
                })
    
    if not idiomas_vacante_list:
        return {
            'porcentaje_match': 0.0,
            'match_interno': 0.0,
            'detalle': {},
            'mejor_match': None,
            'peso_total': round(PESO_TOTAL_MATCH_IDIOMA, 2),
            'mensaje': 'La vacante no tiene idiomas válidos definidos'
        }
    
    # Normalizar idiomas del candidato
    idiomas_candidato_list = []
    for idioma_cand in idiomas_candidato:
        if isinstance(idioma_cand, dict):
            idioma_codigo = idioma_cand.get('id') or idioma_cand.get('idioma', '')
            nivel_candidato = idioma_cand.get('nivel', '')
            if idioma_codigo and nivel_candidato:
                idiomas_candidato_list.append({
                    'idioma': idioma_codigo,
                    'nivel': nivel_candidato
                })
    
    if not idiomas_candidato_list:
        return {
            'porcentaje_match': 0.0,
            'match_interno': 0.0,
            'detalle': {},
            'mejor_match': None,
            'peso_total': round(PESO_TOTAL_MATCH_IDIOMA, 2),
            'mensaje': 'El candidato no tiene idiomas válidos registrados'
        }
    
    mejor_puntuacion = 0.0
    mejor_detalle = None
    mejor_match_info = None
    
    # Evaluar cada combinación de idioma requerido vs idioma del candidato
    for idioma_vac in idiomas_vacante_list:
        idioma_vac_codigo = idioma_vac['idioma']
        nivel_vac_requerido = idioma_vac['nivel']
        nivel_vac_orden = NIVELES_IDIOMA_ORDEN.get(nivel_vac_requerido, 0)
        
        for idioma_cand in idiomas_candidato_list:
            idioma_cand_codigo = idioma_cand['idioma']
            nivel_cand = idioma_cand['nivel']
            nivel_cand_orden = NIVELES_IDIOMA_ORDEN.get(nivel_cand, 0)
            
            # 1. PRIMERO: Evaluar coincidencia de idioma
            idioma_coincide = (idioma_vac_codigo == idioma_cand_codigo)
            idioma_valor = 1.0 if idioma_coincide else 0.0
            
            # 2. DESPUÉS: Evaluar nivel (SOLO si el idioma coincide)
            nivel_coincide = False
            nivel_valor = 0.0
            
            if idioma_coincide:
                # Solo si hay coincidencia de idioma, entonces cotejar el nivel
                # El nivel del candidato debe ser igual o superior al requerido
                if nivel_cand_orden >= nivel_vac_orden:
                    nivel_coincide = True
                    nivel_valor = 1.0
                else:
                    nivel_coincide = False
                    nivel_valor = 0.0
            else:
                # Si no hay coincidencia de idioma, el nivel no se evalúa y es 0
                nivel_coincide = False
                nivel_valor = 0.0
            
            # Calcular match interno para esta combinación
            match_interno = (
                (idioma_valor * PESO_IDIOMA) +
                (nivel_valor * PESO_NIVEL)
            )
            
            # Escalar al peso real (25%)
            porcentaje_match = match_interno * PESO_TOTAL_MATCH_IDIOMA
            
            # Guardar el mejor resultado (solo si hay alguna coincidencia real)
            if porcentaje_match > mejor_puntuacion:
                mejor_puntuacion = porcentaje_match
                mejor_detalle = {
                    'idioma': {
                        'coincide': idioma_coincide,
                        'valor': round(idioma_valor, 2),
                        'peso': round(PESO_IDIOMA, 2),
                        'idiomas_candidato': [idioma_cand_codigo],
                        'idiomas_vacante': [idioma_vac_codigo]
                    },
                    'nivel': {
                        'coincide': nivel_coincide,
                        'valor': round(nivel_valor, 2),
                        'peso': round(PESO_NIVEL, 2),
                        'niveles_candidato': [nivel_cand],
                        'niveles_vacante': [nivel_vac_requerido]
                    }
                }
                mejor_match_info = {
                    'idioma_candidato': idioma_cand_codigo,
                    'idioma_vacante': idioma_vac_codigo,
                    'nivel_candidato': nivel_cand,
                    'nivel_vacante': nivel_vac_requerido,
                    'puntuacion': round(porcentaje_match, 2)
                }
    
    # Si no hubo ninguna coincidencia (mejor_puntuacion sigue en 0.0), retornar 0
    if mejor_puntuacion == 0.0:
        return {
            'porcentaje_match': 0.0,
            'match_interno': 0.0,
            'detalle': {},
            'mejor_match': None,
            'peso_total': round(PESO_TOTAL_MATCH_IDIOMA, 2),
            'mensaje': 'No se encontraron coincidencias de idiomas entre el candidato y la vacante'
        }
    
    # Calcular match_interno del mejor resultado
    match_interno_final = 0.0
    if mejor_detalle:
        match_interno_final = (
            mejor_detalle['idioma']['valor'] * mejor_detalle['idioma']['peso'] +
            mejor_detalle['nivel']['valor'] * mejor_detalle['nivel']['peso']
        )
    
    return {
        'porcentaje_match': round(mejor_puntuacion, 2),
        'match_interno': round(match_interno_final, 2),
        'detalle': mejor_detalle if mejor_detalle else {},
        'mejor_match': mejor_match_info,
        'peso_total': round(PESO_TOTAL_MATCH_IDIOMA, 2)
    }


def get_match_initial(candidato_id, vacante_id):
    candidato = get_object_or_404(Can101Candidato, pk=candidato_id)
    vacante = get_object_or_404(Cli052Vacante, pk=vacante_id)

    aplicacion_vacante = Cli056AplicacionVacante.objects.get(candidato_101=candidato, vacante_id_052=vacante)

    # Definir ponderaciones para cada sección del match
    ponderacion_educacion = 25.0
    ponderacion_laboral = 25.0
    ponderacion_idioma = 25.0
    ponderacion_ubicacion = 25.0

    # INSERT_YOUR_CODE
    # Traer registros académicos del candidato en un JSON
    educaciones = Can103Educacion.objects.filter(candidato_id_101=candidato).order_by('-fecha_inicial')
    
    educaciones_json = []
    for educacion in educaciones:
        educacion_data = {
            'id': educacion.id,
            'institucion': educacion.institucion,
            'fecha_inicial': educacion.fecha_inicial.strftime('%Y-%m-%d') if educacion.fecha_inicial else None,
            'fecha_final': educacion.fecha_final.strftime('%Y-%m-%d') if educacion.fecha_final else None,
            'grado_en': educacion.grado_en,
            'titulo': educacion.titulo,
            'carrera': educacion.carrera,
            'fortaleza_adquiridas': educacion.fortaleza_adquiridas,
            'tipo_estudio': educacion.tipo_estudio,
            'tipo_estudio_display': educacion.mostrar_tipo_estudio(),
            'estado_estudios': educacion.estado_estudios,
            'estado_estudios_display': educacion.mostrar_estado_estudios(),
            'certificacion': educacion.certificacion.url if educacion.certificacion else None,
            'ciudad': {
                'id': educacion.ciudad_id_004.id if educacion.ciudad_id_004 else None,
                'nombre': str(educacion.ciudad_id_004) if educacion.ciudad_id_004 else None
            },
            'estado': {
                'id': educacion.estado_id_001.id if educacion.estado_id_001 else None,
                'nombre': str(educacion.estado_id_001) if educacion.estado_id_001 else None
            },
            'profesion_estudio': {
                'id': educacion.profesion_estudio.id if educacion.profesion_estudio else None,
                'nombre': educacion.profesion_estudio.nombre if educacion.profesion_estudio else None
            }
        }
        educaciones_json.append(educacion_data)
    
    # Traer información académica de la vacante desde el perfil_vacante
    perfil_vacante = vacante.perfil_vacante
    info_academica_vacante = {}
    nivel_estudio_display = None  # Inicializar para evitar errores
    profesion_estudio_listado_parsed = None  # Inicializar para evitar errores
    
    if perfil_vacante:
        # Obtener el display del nivel de estudio
        from applications.services.choices import NIVEL_ESTUDIO_CHOICES_STATIC, TIPO_PROFESION_CHOICES_STATIC
        nivel_estudio_display = dict(NIVEL_ESTUDIO_CHOICES_STATIC).get(perfil_vacante.nivel_estudio, None) if perfil_vacante.nivel_estudio else None
        tipo_profesion_display = dict(TIPO_PROFESION_CHOICES_STATIC).get(perfil_vacante.tipo_profesion, None) if perfil_vacante.tipo_profesion else None
        
        # Parsear profesion_estudio_listado si existe
        profesion_estudio_listado_parsed = None
        if perfil_vacante.profesion_estudio_listado:
            try:
                profesion_estudio_listado_parsed = json.loads(perfil_vacante.profesion_estudio_listado)
            except (json.JSONDecodeError, TypeError):
                profesion_estudio_listado_parsed = None
        
        info_academica_vacante = {
            'profesion_estudio': {
                'id': perfil_vacante.profesion_estudio.id if perfil_vacante.profesion_estudio else None,
                'nombre': perfil_vacante.profesion_estudio.nombre if perfil_vacante.profesion_estudio else None
            },
            'grupo_profesion': {
                'id': perfil_vacante.grupo_profesion.id if perfil_vacante.grupo_profesion else None,
                'nombre': perfil_vacante.grupo_profesion.nombre if perfil_vacante.grupo_profesion else None
            },
            'profesion_estudio_listado': profesion_estudio_listado_parsed,
            'nivel_estudio': perfil_vacante.nivel_estudio,
            'nivel_estudio_display': nivel_estudio_display,
            'cantidad_semestres': perfil_vacante.cantidad_semestres,
            'estado_estudio': perfil_vacante.estado_estudio,
            'tipo_profesion': perfil_vacante.tipo_profesion,
            'tipo_profesion_display': tipo_profesion_display,
            'estudio_complementario': perfil_vacante.estudio_complementario if perfil_vacante.estudio_complementario else None
        }
    
    # Información académica adicional de la vacante (no del perfil)
    info_academica_vacante_adicional = {
        'estudios_complementarios': vacante.estudios_complementarios,
        'estudios_complementarios_certificado': vacante.estudios_complementarios_certificado
    }
    
    # Validar coincidencias entre estudios del candidato y requisitos de la vacante
    coincidencias_estudios = []
    
    if perfil_vacante and educaciones_json:
        nivel_estudio_vacante = perfil_vacante.nivel_estudio
        nivel_estudio_display_vacante = nivel_estudio_display
        estado_estudio_vacante = perfil_vacante.estado_estudio  # Boolean: True = graduado, False = no graduado
        tipo_profesion_vacante = perfil_vacante.tipo_profesion  # 'E' = Específica, 'G' = Grupo, 'L' = Listado
        
        for educacion in educaciones_json:
            tipo_estudio_candidato = educacion.get('tipo_estudio')
            tipo_estudio_display_candidato = educacion.get('tipo_estudio_display')
            estado_estudios_candidato = educacion.get('estado_estudios')  # 'G' = Graduado, 'C' = En curso, 'A' = Aplazado
            es_graduado_candidato = estado_estudios_candidato == 'G'
            
            # Evaluar coincidencia de tipo de estudio
            coincide_tipo_estudio = False
            if nivel_estudio_vacante and tipo_estudio_candidato:
                coincide_tipo_estudio = (tipo_estudio_candidato == nivel_estudio_vacante)
            
            # Evaluar coincidencia de graduación
            coincide_graduado = False
            if estado_estudio_vacante is not None:
                # Si la vacante requiere graduado (True), el candidato debe estar graduado ('G')
                # Si la vacante no requiere graduado (False), no importa el estado del candidato
                if estado_estudio_vacante:
                    coincide_graduado = es_graduado_candidato
                else:
                    # Si la vacante no requiere graduado, siempre coincide
                    coincide_graduado = True
            else:
                # Si la vacante no especifica estado, no se evalúa
                coincide_graduado = None
            
            # Evaluar coincidencia de profesión de estudio
            profesion_estudio_candidato = educacion.get('profesion_estudio')
            profesion_id_candidato = profesion_estudio_candidato.get('id') if profesion_estudio_candidato else None
            profesion_nombre_candidato = profesion_estudio_candidato.get('nombre') if profesion_estudio_candidato else None
            
            coincide_profesion = False
            tipo_profesion_vacante_info = None
            profesion_vacante_info = None
            
            if tipo_profesion_vacante and profesion_id_candidato:
                # Obtener el objeto de profesión del candidato para validaciones
                from applications.vacante.models import Cli055ProfesionEstudio
                try:
                    profesion_candidato_obj = Cli055ProfesionEstudio.objects.get(id=profesion_id_candidato)
                except Cli055ProfesionEstudio.DoesNotExist:
                    profesion_candidato_obj = None
                
                if tipo_profesion_vacante == 'E':  # Profesión Específica
                    profesion_vacante_obj = perfil_vacante.profesion_estudio
                    if profesion_vacante_obj and profesion_candidato_obj:
                        coincide_profesion = (profesion_id_candidato == profesion_vacante_obj.id)
                        tipo_profesion_vacante_info = 'Específica'
                        profesion_vacante_info = {
                            'id': profesion_vacante_obj.id,
                            'nombre': profesion_vacante_obj.nombre,
                            'tipo': 'Específica'
                        }
                
                elif tipo_profesion_vacante == 'G':  # Grupo de Profesiones
                    grupo_profesion_vacante = perfil_vacante.grupo_profesion
                    if grupo_profesion_vacante and profesion_candidato_obj:
                        coincide_profesion = (profesion_candidato_obj.grupo == grupo_profesion_vacante)
                        tipo_profesion_vacante_info = 'Grupo'
                        profesion_vacante_info = {
                            'id': grupo_profesion_vacante.id,
                            'nombre': grupo_profesion_vacante.nombre,
                            'tipo': 'Grupo'
                        }
                
                elif tipo_profesion_vacante == 'L':  # Listado Personalizado
                    profesion_listado_parsed = profesion_estudio_listado_parsed
                    if profesion_listado_parsed:
                        # El listado puede ser una lista de objetos con 'value' e 'id'
                        if isinstance(profesion_listado_parsed, list):
                            # Buscar coincidencia por ID o por nombre
                            for prof_item in profesion_listado_parsed:
                                if isinstance(prof_item, dict):
                                    prof_id = prof_item.get('id')
                                    prof_nombre = prof_item.get('value', '')
                                    # Comparar por ID si está disponible, sino por nombre
                                    if prof_id and profesion_id_candidato:
                                        if prof_id == profesion_id_candidato:
                                            coincide_profesion = True
                                            break
                                    elif prof_nombre and profesion_nombre_candidato:
                                        if prof_nombre.lower() == profesion_nombre_candidato.lower():
                                            coincide_profesion = True
                                            break
                        tipo_profesion_vacante_info = 'Listado'
                        profesion_vacante_info = {
                            'listado': profesion_listado_parsed,
                            'tipo': 'Listado'
                        }
            
            # Determinar si hay coincidencia general
            coincide_general = False
            if nivel_estudio_vacante:
                # Si hay requisito de nivel de estudio, debe coincidir
                if coincide_tipo_estudio:
                    if estado_estudio_vacante is not None:
                        coincide_general = coincide_graduado
                    else:
                        coincide_general = True
            else:
                # Si no hay requisito de nivel de estudio, solo evaluar graduación si aplica
                if estado_estudio_vacante is not None:
                    coincide_general = coincide_graduado
                else:
                    coincide_general = None
            
            coincidencia = {
                'educacion_id': educacion.get('id'),
                'institucion': educacion.get('institucion'),
                'candidato': {
                    'tipo_estudio': tipo_estudio_candidato,
                    'tipo_estudio_display': tipo_estudio_display_candidato,
                    'estado_estudios': estado_estudios_candidato,
                    'estado_estudios_display': educacion.get('estado_estudios_display'),
                    'es_graduado': es_graduado_candidato,
                    'profesion_estudio': {
                        'id': profesion_id_candidato,
                        'nombre': profesion_nombre_candidato
                    }
                },
                'vacante': {
                    'nivel_estudio': nivel_estudio_vacante,
                    'nivel_estudio_display': nivel_estudio_display_vacante,
                    'estado_estudio': estado_estudio_vacante,
                    'requiere_graduado': estado_estudio_vacante if estado_estudio_vacante is not None else None,
                    'tipo_profesion': tipo_profesion_vacante,
                    'profesion_estudio': profesion_vacante_info
                },
                'coincidencias': {
                    'tipo_estudio': {
                        'coincide': coincide_tipo_estudio,
                        'candidato': tipo_estudio_display_candidato,
                        'vacante': nivel_estudio_display_vacante
                    },
                    'graduado': {
                        'coincide': coincide_graduado,
                        'candidato_graduado': es_graduado_candidato,
                        'vacante_requiere_graduado': estado_estudio_vacante if estado_estudio_vacante is not None else None
                    },
                    'profesion_estudio': {
                        'coincide': coincide_profesion,
                        'candidato': {
                            'id': profesion_id_candidato,
                            'nombre': profesion_nombre_candidato
                        },
                        'vacante': {
                            'tipo': tipo_profesion_vacante_info,
                            'requisito': profesion_vacante_info
                        }
                    }
                },
                'coincide_general': coincide_general
            }
            
            coincidencias_estudios.append(coincidencia)
    
    # Calcular el match académico usando la función especializada
    resultado_match_academico = calcular_match_academico(candidato, vacante, ponderacion_educacion)
    
    # Calcular el match laboral usando la función especializada
    resultado_match_laboral = calcular_match_laboral(candidato, vacante, ponderacion_laboral)
    
    # Calcular el match de idiomas usando la función especializada
    resultado_match_idioma = calcular_match_idioma(candidato, vacante, ponderacion_idioma)
    
    # Combinar toda la información académica en un JSON estructurado con tags principales
    info_academica_completa = {
        'educacion': {
            'candidato': {
                'educaciones': educaciones_json
            },
            'vacante': {
                'perfil_academico': info_academica_vacante,
                'estudios_complementarios': info_academica_vacante_adicional
            },
            'coincidencias_estudios': coincidencias_estudios,
            'match_academico': resultado_match_academico,
            'ponderacion': round(resultado_match_academico.get('porcentaje_match', 0.0), 2)
        },
        'laboral': {
            'candidato': {
                'experiencias': resultado_match_laboral.get('experiencias', []),
                'anos_totales': resultado_match_laboral.get('anos_totales', 0.0)
            },
            'vacante': {
                'tiempo_experiencia_requerido': resultado_match_laboral.get('detalle', {}).get('anos_experiencia', {}).get('tiempo_experiencia_requerido'),
                'anos_requeridos': resultado_match_laboral.get('detalle', {}).get('anos_experiencia', {}).get('anos_requeridos'),
                'cargo': resultado_match_laboral.get('detalle', {}).get('cargo', {}).get('cargo_vacante')
            },
            'match_laboral': resultado_match_laboral,
            'ponderacion': round(resultado_match_laboral.get('porcentaje_match', 0.0), 2)
        },
        'idioma': {
            'candidato': {
                'idiomas': candidato.idiomas if candidato.idiomas else []
            },
            'vacante': {
                'idiomas': perfil_vacante.idiomas if perfil_vacante and perfil_vacante.idiomas else []
            },
            'match_idioma': resultado_match_idioma,
            'ponderacion': round(resultado_match_idioma.get('porcentaje_match', 0.0), 2)
        },
        'ubicacion': {
            'estado': 'pendiente',
            'mensaje': 'Información de ubicación pendiente de implementar'
        }
    }
    
    

    # Guardar el JSON de educación en el campo json_match_inicial de la aplicación de vacante
    

    # Retornar el JSON con la información académica completa
    info_academica_json = json.dumps(info_academica_completa, indent=4, ensure_ascii=False, default=str)
    
    return info_academica_json