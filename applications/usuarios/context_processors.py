"""Context processors para templates."""


def nivel_educativo_candidato(request):
    """Añade nivel_educativo_maximo al contexto cuando el usuario es candidato."""
    nivel_educativo_maximo = ''
    candidato_id = request.session.get('candidato_id')
    if candidato_id:
        try:
            from applications.candidato.models import Can101Candidato, Can103Educacion
            candidato_obj = Can101Candidato.objects.get(id=candidato_id)
            estudio_mas_alto = (
                Can103Educacion.objects
                .filter(candidato_id_101=candidato_obj, tipo_estudio__isnull=False)
                .exclude(tipo_estudio='')
                .order_by('-tipo_estudio')
                .first()
            )
            nivel_educativo_maximo = estudio_mas_alto.mostrar_tipo_estudio() if estudio_mas_alto else 'Sin estudios registrados'
        except Exception:
            nivel_educativo_maximo = ''
    return {'nivel_educativo_maximo': nivel_educativo_maximo}
