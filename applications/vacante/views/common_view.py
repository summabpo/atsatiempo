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
        "ponderacion_sugerida": 25
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
                print('--------------------------------')
                print(pregunta_vacante['tipo_pregunta'])
                print(pregunta_vacante['pregunta'])
                print(respuesta_candidato)
                print('--------------------------------')
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
        "ponderacion_sugerida": 30
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
        "ponderacion_sugerida": 15
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
        "ponderacion_sugerida": 10
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
        "ponderacion_sugerida": 5
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
        "ponderacion_sugerida": 5
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
        "ponderacion_sugerida": 5
    }

    # Obtener motivadores requeridos por la vacante
    motivadores_vacante = []
    if vacante.motivadores:
        # La vacante tiene un solo motivador (ForeignKey)
        motivadores_vacante = [vacante.motivadores.id]
        motivador_vacante_nombre = vacante.motivadores.nombre
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
        "ponderacion_sugerida": 5
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
    json_match['ubicacion_y_salarial'] = {
        "criterio_id": "4",
        "categoria": "Ubicación y Expectativas Salariales",
        "criterio_especifico": "Ubicación y Rango Salarial",
        "descripcion": "Coincidencia de la ubicación del candidato con el lugar de trabajo de la vacante y verificación de que el salario total (base + adicional) de la vacante sea igual o mayor a la aspiración salarial del candidato.",
        "fuentes_informacion": ["Perfil del candidato", "perfil de la vacante"],
        "ponderacion_sugerida": 10
    }

    # --- Coincidencia de Ubicación ---
    # El candidato tiene ciudad_id_004 y la vacante tiene perfil_vacante.lugar_trabajo
    ciudad_candidato = getattr(candidato, 'ciudad_id_004', None)
    perfil_vacante = getattr(vacante, 'perfil_vacante', None)
    lugar_trabajo_vacante = getattr(perfil_vacante, 'lugar_trabajo', None) if perfil_vacante else None
    
    nombre_ciudad_candidato = str(ciudad_candidato) if ciudad_candidato else "No especificada"
    nombre_ciudad_vacante = str(lugar_trabajo_vacante) if lugar_trabajo_vacante else "No especificada"
    ubicacion_match = False

    if ciudad_candidato and lugar_trabajo_vacante:
        ubicacion_match = ciudad_candidato.id == lugar_trabajo_vacante.id
    else:
        # Si alguna de las dos no está especificada, no hay match
        ubicacion_match = False

    # --- Coincidencia de Rango Salarial ---
    # La vacante tiene salario base + salario adicional en perfil_vacante
    # El candidato tiene aspiracion_salarial
    aspiracion_candidato = getattr(candidato, 'aspiracion_salarial', None)
    
        # Obtener salario base y adicional de la vacante
    salario_base = getattr(perfil_vacante, 'salario', 0) if perfil_vacante else 0
    salario_adicional = getattr(perfil_vacante, 'salario_adicional', 0) if perfil_vacante else 0
    
    # Convertir Decimal a float para serialización JSON
    salario_base_float = float(salario_base) if salario_base else 0.0
    salario_adicional_float = float(salario_adicional) if salario_adicional else 0.0
    
    # Calcular salario total de la vacante
    salario_total_vacante = salario_base_float + salario_adicional_float
    
    rango_salarial_vacante = {
        "salario_base": salario_base_float,
        "salario_adicional": salario_adicional_float,
        "salario_total": salario_total_vacante
    }
    
        # Verificar si el salario total de la vacante es igual o mayor a la aspiración del candidato
    rango_salarial_match = False
    if aspiracion_candidato is not None and salario_total_vacante > 0:
        try:
            aspiracion_candidato_val = float(aspiracion_candidato)
            # El salario total ya está en float, no necesita conversión
            salario_total_val = salario_total_vacante
            # El salario de la vacante debe ser igual o mayor a la aspiración del candidato
            rango_salarial_match = salario_total_val >= aspiracion_candidato_val
        except Exception:
            rango_salarial_match = False
    else:
        rango_salarial_match = False

    # --- Resultado global: filtro crítico ---
    # Si alguna de las dos (ubicación o salario) no hace match, el resultado es False
    resultado_ubicacion_y_salarial = ubicacion_match and rango_salarial_match

    # --- Cálculo de ponderación y puntaje ---
    ponderacion_ubicacion_salarial = 10  # Ponderación sugerida para este criterio
    puntaje_ubicacion_salarial = 0
    
    if resultado_ubicacion_y_salarial:
        # Si hay match en ambos criterios, calcular puntaje basado en la calidad del match
        puntaje_base = ponderacion_ubicacion_salarial
        
        # Bonus por ubicación exacta
        if ubicacion_match:
            puntaje_ubicacion_salarial += puntaje_base * 0.5  # 50% del puntaje por ubicación
        
        # Bonus por salario adecuado
        if rango_salarial_match:
            puntaje_ubicacion_salarial += puntaje_base * 0.5  # 50% del puntaje por salario
        
        puntaje_ubicacion_salarial = round(puntaje_ubicacion_salarial, 2)
    else:
        # Si no hay match en alguno de los criterios, puntaje 0
        puntaje_ubicacion_salarial = 0

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

    print(json.dumps(json_match, indent=4, ensure_ascii=False))


    
    
    

    context = {
        'candidato': candidato,
        'vacante': vacante,
        'json_match': json_match,
    }

    return render(request, 'admin/vacancy/match.html', context)
