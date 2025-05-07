from django.shortcuts import get_object_or_404
from applications.candidato.models import Can101Candidato, Can101CandidatoSkill, Can102Experiencia, Can103Educacion 

def buscar_candidato_por_documento(numero_documento):
    return Can101Candidato.objects.get(numero_documento=numero_documento)

def buscar_candidato(candidato_id):
    candidato_obj = get_object_or_404(Can101Candidato, pk=candidato_id)

    educaciones = list(Can103Educacion.objects.filter(candidato_id_101=candidato_obj))
    experiencias = list(Can102Experiencia.objects.filter(candidato_id_101=candidato_obj))
    habilidades = list(Can101CandidatoSkill.objects.filter(candidato_id_101=candidato_obj).select_related('skill_id_104'))

    return {
        'id': candidato_obj.id,
        'nombre_completo': candidato_obj.nombre_completo(),
        'email': candidato_obj.email,
        'telefono': candidato_obj.telefono,
        'sexo': candidato_obj.get_sexo_display(),
        'fecha_nacimiento': candidato_obj.fecha_nacimiento,
        'estado': str(candidato_obj.estado_id_001),
        'ciudad': str(candidato_obj.ciudad_id_004),
        'imagen_perfil': candidato_obj.imagen_perfil.url if candidato_obj.imagen_perfil else None,
        'hoja_de_vida': candidato_obj.hoja_de_vida.url if candidato_obj.hoja_de_vida else None,
        'numero_documento': candidato_obj.numero_documento,
        'porcentaje': candidato_obj.calcular_porcentaje(),
        'puede_aplicar': candidato_obj.puede_aplicar(),
        'educacion': [
            {
                'institucion': e.institucion,
                'titulo': e.titulo,
                'tipo_estudio': e.get_tipo_estudio_display(),
                'fecha_inicial': e.fecha_inicial,
                'fecha_final': e.fecha_final,
                'grado_en': e.grado_en,
                'carrera': e.carrera,
                'fortalezas': e.fortaleza_adquiridas,
                'ciudad': str(e.ciudad_id_004),
                'estado': str(e.estado_id_001),
            } for e in educaciones
        ],
        'experiencia': [
            {
                'entidad': ex.entidad,
                'sector': ex.sector,
                'cargo': ex.cargo,
                'fecha_inicial': ex.fecha_inicial,
                'fecha_final': ex.fecha_final,
                'activo': ex.activo,
                'logro': ex.logro,
                'estado': str(ex.estado_id_001),
            } for ex in experiencias
        ],
        'skills': [
            {
                'nombre': s.skill_id_104.nombre,
                'nivel': s.get_nivel_display(),
            } for s in habilidades
        ]
    }