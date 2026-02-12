from django.shortcuts import render
from applications.common.views.EnvioCorreo import enviar_correo
from applications.services.service_candidate import personal_information_calculation
from applications.services.service_recruited import consultar_historial_aplicacion_vacante, query_recruited_vacancy_id, consultar_historial_aplicacion_vacante_candidate
from applications.vacante.forms.BuscarVacanteForm import VacanteFiltro
from applications.vacante.models import Cli052Vacante, Cli055ProfesionEstudio, Cli053SoftSkill, Cli054HardSkill, Cli052VacanteHardSkillsId054, Cli052VacanteSoftSkillsId053, Cli072FuncionesResponsabilidades, Cli073PerfilVacante, Cli068Cargo, Cli074AsignacionFunciones
from applications.reclutado.models import Cli056AplicacionVacante
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
    except Cli056AplicacionVacante.DoesNotExist:
        messages.error(request, "La aplicación de vacante no existe o no pertenece al candidato.")
        return redirect('vacantes:vacante_candidato_aplicadas')
        

    context = {
        'vacancy': vacancy,
        'vacante': vacante,
        'historial': historico_vacante,
        'is_candidato': True,  # Indicar que es candidato para restringir información
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