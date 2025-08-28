from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, Count, Q, Value, Case, When, CharField
from applications.cliente.models import Cli051Cliente, Cli064AsignacionCliente, Cli078MotivadoresCandidato

from applications.common.views.EnvioCorreo import enviar_correo
from applications.services.service_interview import query_interview_all
from applications.services.service_recruited import query_recruited_vacancy_id
from applications.vacante.forms.EntrevistaForm import EntrevistaCrearForm
from applications.vacante.models import Cli052Vacante, Cli055ProfesionEstudio, Cli053SoftSkill, Cli054HardSkill, Cli052VacanteHardSkillsId054, Cli052VacanteSoftSkillsId053, Cli072FuncionesResponsabilidades, Cli073PerfilVacante, Cli068Cargo, Cli074AsignacionFunciones, Cli075GrupoProfesion
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

#forms
from applications.vacante.forms.VacanteForms import VacancyAssingForm, VacancyFormAllV2, VacancyFormEdit, VacanteForm, VacanteFormEdit, VacancyFormAll

#views
from applications.services.service_vacanty import get_vacanty_questions, query_vacanty_all, query_vacanty_detail

#query
from applications.services.service_client import query_client_detail
from components.RegistrarHistorialVacante import crear_historial_aplicacion


@login_required
@validar_permisos('acceso_analista_seleccion_ats')
def list_assigned_vacancies(request):
    # Verificar si el cliente_id está en la sesión
    user_logged_in = request.session.get('user_login')

    vacantes = query_vacanty_all()
    vacantes = vacantes.filter(
        estado_id_001=1,  # Asumiendo que ese es el campo correcto para el estado
        usuario_asignado=user_logged_in.get('id'),  # Asumiendo que el ID del usuario asignado está en la sesión
    )

    context = {
        'vacantes': vacantes,
    }

    return render(request, 'admin/vacancy/client_analyst_internal_user/vacancy_list.html', context)

@login_required
@validar_permisos('acceso_analista_seleccion_ats')
def edit_vacancy(request, pk, vacante_id):

    vacante = get_object_or_404(Cli052Vacante.objects.prefetch_related('habilidades'), id=vacante_id)
    
    habilidades_guardadas = vacante.habilidades.all() 
    perfil_vacante = vacante.perfil_vacante

    # IDs de Skills extraídos de la tabla can_104_skill
    SKILLS_RELACIONALES_IDS = [1, 2, 3, 4, 5]
    SKILLS_PERSONALES_IDS = [6, 7, 8, 9, 10]
    SKILLS_COGNITIVAS_IDS = [11, 12, 13, 14, 15, 16]
    SKILLS_LIDERAZGO_IDS = [18, 19, 20, 21, 22]
    SKILLS_DIGITALES_IDS = [23, 24, 25, 26, 27]

    # IDs para FIT CULTURAL extraídos de la tabla cli_077_fit_cultural
    FIT_GRUPO_1_IDS = [1, 2, 3, 4]
    FIT_GRUPO_2_IDS = [5, 6, 7, 8]
    FIT_GRUPO_3_IDS = [9, 10, 11, 12, 13]
    FIT_GRUPO_4_IDS = [14, 15, 16]
    FIT_GRUPO_5_IDS = [17, 18, 19, 20]

    # Función para procesar profesion_estudio_listado
    def procesar_profesion_listado(listado_json):
        if not listado_json:
            return ""
        try:
            # Si es un string JSON, parsearlo y devolverlo como string JSON válido
            if isinstance(listado_json, str):
                # Verificar si ya es JSON válido
                try:
                    data = json.loads(listado_json)
                    # Si es una lista de objetos con 'value' e 'id', devolver el JSON original
                    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict) and 'value' in data[0]:
                        return listado_json
                    else:
                        # Si no tiene el formato esperado, convertirlo
                        return json.dumps([{"value": item, "id": i} for i, item in enumerate(data)])
                except json.JSONDecodeError:
                    # Si no es JSON válido, crear el formato correcto
                    return json.dumps([{"value": listado_json, "id": 0}])
            else:
                # Si ya es una lista o dict, convertirlo al formato correcto
                if isinstance(listado_json, list):
                    if len(listado_json) > 0 and isinstance(listado_json[0], dict) and 'value' in listado_json[0]:
                        return json.dumps(listado_json)
                    else:
                        return json.dumps([{"value": item, "id": i} for i, item in enumerate(listado_json)])
                else:
                    return json.dumps([{"value": str(listado_json), "id": 0}])
        except (json.JSONDecodeError, TypeError, AttributeError):
            # Si no es JSON válido, devolver como string simple
            return json.dumps([{"value": str(listado_json), "id": 0}]) if listado_json else ""

    # Construir initial data para el formulario
    initial = {
        'titulo': vacante.titulo,
        'cargo': vacante.cargo_id if vacante.cargo else None,
        'termino_contrato': perfil_vacante.termino_contrato if perfil_vacante else None,
        'modalidad': perfil_vacante.modalidad if perfil_vacante else None,
        'cantidad_presentar': vacante.cantidad_presentar,
        'numero_posiciones': vacante.numero_posiciones,
        'fecha_presentacion': vacante.fecha_presentacion.strftime('%Y-%m-%d') if vacante.fecha_presentacion else None,
        'barrio': perfil_vacante.barrio if perfil_vacante else None,
        'direccion': perfil_vacante.direccion if perfil_vacante else None,
        'salario': str(perfil_vacante.salario) if perfil_vacante and perfil_vacante.salario else None,
        'tipo_salario': perfil_vacante.tipo_salario if perfil_vacante else None,
        'frecuencia_pago': perfil_vacante.frecuencia_pago if perfil_vacante else None,
        'salario_adicional': perfil_vacante.salario_adicional if perfil_vacante else None,
        'edad_inicial': perfil_vacante.edad_inicial if perfil_vacante else None,
        'edad_final': perfil_vacante.edad_final if perfil_vacante else None,
        'genero': perfil_vacante.genero if perfil_vacante else None,
        'lugar_trabajo': perfil_vacante.lugar_trabajo_id if perfil_vacante and perfil_vacante.lugar_trabajo else None,
        'profesion_estudio': perfil_vacante.profesion_estudio_id if perfil_vacante and perfil_vacante.profesion_estudio else None,
        'nivel_estudio': perfil_vacante.nivel_estudio if perfil_vacante else None,
        'motivadores_candidato': vacante.motivadores_id if vacante.motivadores else None,
        'otro_motivador': vacante.otro_motivador,
        'comentarios': vacante.comentarios,
        'descripcion_vacante': vacante.descripcion_vacante,
        'tipo_profesion': perfil_vacante.tipo_profesion if perfil_vacante else None,
        'grupo_profesion': perfil_vacante.grupo_profesion_id if perfil_vacante and perfil_vacante.grupo_profesion else None,
        'profesion_estudio_listado': procesar_profesion_listado(perfil_vacante.profesion_estudio_listado) if perfil_vacante else None,
    }

    # Cargar skills correctamente por grupo
    initial['skill_relacionales'] = habilidades_guardadas.filter(id__in=SKILLS_RELACIONALES_IDS)
    initial['skill_personales'] = habilidades_guardadas.filter(id__in=SKILLS_PERSONALES_IDS)
    initial['skill_cognitivas'] = habilidades_guardadas.filter(id__in=SKILLS_COGNITIVAS_IDS)
    initial['skill_digitales'] = habilidades_guardadas.filter(id__in=SKILLS_DIGITALES_IDS)
    initial['skill_liderazgo'] = habilidades_guardadas.filter(id__in=SKILLS_LIDERAZGO_IDS)

    # Extraer datos de campos JSON del perfil_vacante
    if perfil_vacante:
        # Motivo de la vacante
        if perfil_vacante.motivo_vacante and isinstance(perfil_vacante.motivo_vacante, dict):
            initial['motivo_vacante'] = perfil_vacante.motivo_vacante.get('motivo', '')
            initial['otro_motivo'] = perfil_vacante.motivo_vacante.get('otro_motivo', '')

        # Horarios
        if perfil_vacante.horario:
            for horario in perfil_vacante.horario:
                if isinstance(horario, dict):  # <-- Verificación aplicada
                    bloque = horario.get('bloque', 1)
                    initial[f'horario_inicio_{bloque}'] = horario.get('dia_inicio', '')
                    initial[f'horario_final_{bloque}'] = horario.get('dia_final', '')
                    initial[f'hora_inicio_{bloque}'] = horario.get('hora_inicio', '')
                    initial[f'hora_final_{bloque}'] = horario.get('hora_final', '')

        # Experiencia laboral
        if perfil_vacante.experiencia_laboral:
            for exp in perfil_vacante.experiencia_laboral:
                if isinstance(exp, dict):  # <-- Verificación aplicada
                    bloque = exp.get('bloque', 1)
                    initial[f'tiempo_experiencia_{bloque}'] = exp.get('tiempo_experiencia', '')
                    initial[f'experiencia_especifica_en_{bloque}'] = exp.get('experiencia_especifica', '')

        # Idiomas
        if perfil_vacante.idiomas:
            for idioma in perfil_vacante.idiomas:
                if isinstance(idioma, dict):  # <-- Verificación aplicada
                    bloque = idioma.get('bloque', 1)
                    initial[f'idioma_{bloque}'] = idioma.get('idioma', '')
                    initial[f'nivel_idioma_{bloque}'] = idioma.get('nivel', '')

        # Estudios complementarios
        if perfil_vacante.estudio_complementario:
            for estudio in perfil_vacante.estudio_complementario:
                if isinstance(estudio, dict):  # <-- Verificación aplicada
                    bloque = estudio.get('bloque', 1)
                    initial[f'estudios_complementarios_{bloque}'] = estudio.get('estudio', '')
                    initial[f'estudios_complementarios_certificado_{bloque}'] = estudio.get('certificado', '')

        # Funciones y responsabilidades
        if perfil_vacante.funciones_responsabilidades:
            for funcion in perfil_vacante.funciones_responsabilidades:
                if isinstance(funcion, dict):  # <-- Verificación aplicada
                    bloque = funcion.get('bloque', 1)
                    initial[f'funciones_responsabilidades_{bloque}'] = funcion.get('funcion', '')

    # Fit cultural
    initial['grupo_fit_1'] = list(vacante.fit_cultural.filter(id__in=FIT_GRUPO_1_IDS).values_list('id', flat=True))
    initial['grupo_fit_2'] = list(vacante.fit_cultural.filter(id__in=FIT_GRUPO_2_IDS).values_list('id', flat=True))
    initial['grupo_fit_3'] = list(vacante.fit_cultural.filter(id__in=FIT_GRUPO_3_IDS).values_list('id', flat=True))
    initial['grupo_fit_4'] = list(vacante.fit_cultural.filter(id__in=FIT_GRUPO_4_IDS).values_list('id', flat=True))
    initial['grupo_fit_5'] = list(vacante.fit_cultural.filter(id__in=FIT_GRUPO_5_IDS).values_list('id', flat=True))

    if request.method == 'POST':
        form = VacancyFormAllV2(request.POST, cliente_id=pk)
        if form.is_valid():

            # Update existing data
            vacante.titulo = form.cleaned_data['titulo']
            vacante.cargo = Cli068Cargo.objects.get(id=form.cleaned_data['cargo'])
            vacante.numero_posiciones = form.cleaned_data['numero_posiciones']
            vacante.cantidad_presentar = form.cleaned_data['cantidad_presentar']
            vacante.fecha_presentacion = form.cleaned_data['fecha_presentacion']
            vacante.descripcion_vacante = form.cleaned_data['descripcion_vacante']
            vacante.comentarios = form.cleaned_data['comentarios']
            vacante.motivadores = Cli078MotivadoresCandidato.objects.get(id=form.cleaned_data['motivadores_candidato']) if form.cleaned_data['motivadores_candidato'] else None
            vacante.otro_motivador = form.cleaned_data['otro_motivador']

            vacante.save()

            # Update perfil_vacante
            perfil_vacante = vacante.perfil_vacante
            perfil_vacante.edad_inicial = form.cleaned_data['edad_inicial']
            perfil_vacante.edad_final = form.cleaned_data['edad_final']
            perfil_vacante.genero = form.cleaned_data['genero']
            perfil_vacante.modalidad = form.cleaned_data['modalidad']
            perfil_vacante.salario = form.cleaned_data['salario'].replace('.', '') if form.cleaned_data['salario'] else None
            perfil_vacante.tipo_salario = form.cleaned_data['tipo_salario']
            perfil_vacante.frecuencia_pago = form.cleaned_data['frecuencia_pago']
            perfil_vacante.salario_adicional = form.cleaned_data['salario_adicional']
            perfil_vacante.profesion_estudio = Cli055ProfesionEstudio.objects.get(id=form.cleaned_data['profesion_estudio']) if form.cleaned_data['profesion_estudio'] else None
            perfil_vacante.nivel_estudio = form.cleaned_data['nivel_estudio']
            perfil_vacante.lugar_trabajo = Cat004Ciudad.objects.get(id=form.cleaned_data['lugar_trabajo']) if form.cleaned_data['lugar_trabajo'] else None
            perfil_vacante.termino_contrato = form.cleaned_data['termino_contrato']
            perfil_vacante.barrio = form.cleaned_data['barrio']
            perfil_vacante.direccion = form.cleaned_data['direccion']
            perfil_vacante.tipo_profesion = form.cleaned_data['tipo_profesion']
            perfil_vacante.grupo_profesion = Cli075GrupoProfesion.objects.get(id=form.cleaned_data['grupo_profesion']) if form.cleaned_data['grupo_profesion'] else None
            perfil_vacante.profesion_estudio_listado = form.cleaned_data['profesion_estudio_listado']
            
            # Guardar datos JSON
            # Motivo de la vacante
            motivo_vacante_data = {
                'motivo': form.cleaned_data['motivo_vacante'],
                'otro_motivo': form.cleaned_data['otro_motivo'] if form.cleaned_data['motivo_vacante'] == 'Otro' else None
            }
            perfil_vacante.motivo_vacante = motivo_vacante_data
            
            # Horarios (múltiples bloques)
            horarios_data = []
            for i in range(1, 4):
                horario_inicio = form.cleaned_data.get(f'horario_inicio_{i}')
                horario_final = form.cleaned_data.get(f'horario_final_{i}')
                hora_inicio = form.cleaned_data.get(f'hora_inicio_{i}')
                hora_final = form.cleaned_data.get(f'hora_final_{i}')
                
                if all([horario_inicio, horario_final, hora_inicio, hora_final]):
                    horarios_data.append({
                        'bloque': i,
                        'dia_inicio': horario_inicio,
                        'dia_final': horario_final,
                        'hora_inicio': str(hora_inicio),
                        'hora_final': str(hora_final)
                    })
            perfil_vacante.horario = horarios_data
            
            # Experiencia laboral
            experiencia_data = []
            for i in range(1, 4):
                tiempo_experiencia = form.cleaned_data.get(f'tiempo_experiencia_{i}')
                experiencia_especifica = form.cleaned_data.get(f'experiencia_especifica_en_{i}')
                
                if tiempo_experiencia and experiencia_especifica:
                    experiencia_data.append({
                        'bloque': i,
                        'tiempo_experiencia': tiempo_experiencia,
                        'experiencia_especifica': experiencia_especifica
                    })
            perfil_vacante.experiencia_laboral = experiencia_data
            
            # Idiomas
            idiomas_data = []
            for i in range(1, 3):
                idioma = form.cleaned_data.get(f'idioma_{i}')
                nivel_idioma = form.cleaned_data.get(f'nivel_idioma_{i}')
                
                if idioma and nivel_idioma:
                    idiomas_data.append({
                        'bloque': i,
                        'idioma': idioma,
                        'nivel': nivel_idioma
                    })
            perfil_vacante.idiomas = idiomas_data
            
            # Estudios complementarios
            estudios_data = []
            for i in range(1, 4):
                estudio = form.cleaned_data.get(f'estudios_complementarios_{i}')
                certificado = form.cleaned_data.get(f'estudios_complementarios_certificado_{i}')
                
                if estudio and certificado is not None:
                    estudios_data.append({
                        'bloque': i,
                        'estudio': estudio,
                        'certificado': certificado
                    })
            perfil_vacante.estudio_complementario = estudios_data
            
            # Funciones y responsabilidades
            funciones_data = []
            for i in range(1, 4):
                funcion = form.cleaned_data.get(f'funciones_responsabilidades_{i}')
                if funcion:
                    funciones_data.append({
                        'bloque': i,
                        'funcion': funcion
                    })
            perfil_vacante.funciones_responsabilidades = funciones_data
            
            perfil_vacante.save()

            # Update skills (ManyToMany fields)
            # 1. Recolecta todos los objetos 'skill' del formulario en una sola lista
            skills_seleccionadas = (
                list(form.cleaned_data.get('skill_relacionales', [])) +
                list(form.cleaned_data.get('skill_personales', [])) +
                list(form.cleaned_data.get('skill_cognitivas', [])) +
                list(form.cleaned_data.get('skill_digitales', [])) +
                list(form.cleaned_data.get('skill_liderazgo', []))
            )

            # 2. ✅ Usa .set() para actualizar la relación.
            # Esto borra las habilidades viejas y agrega las nuevas automáticamente.
            vacante.habilidades.set(skills_seleccionadas)
            
            # Fit cultural
            vacante.fit_cultural.clear()
            grupo_fit_1 = form.cleaned_data.get('grupo_fit_1', [])
            grupo_fit_2 = form.cleaned_data.get('grupo_fit_2', [])
            grupo_fit_3 = form.cleaned_data.get('grupo_fit_3', [])
            grupo_fit_4 = form.cleaned_data.get('grupo_fit_4', [])
            grupo_fit_5 = form.cleaned_data.get('grupo_fit_5', [])
            
            # Solo debe haber un grupo fit seleccionado, pero por si acaso tomamos el primero que encuentre
            todos_fit = list(grupo_fit_1) + list(grupo_fit_2) + list(grupo_fit_3) + list(grupo_fit_4) + list(grupo_fit_5)
            if todos_fit:
                vacante.fit_cultural.add(*todos_fit)
            
            messages.success(request, 'Vacante editada correctamente')
            return redirect('vacantes:vacantes_asignadas_analista_interno')
        else:
            print(form.errors)
            messages.error(request, 'Por favor revise el formulario, errores encontrados.')

    else:
        form = VacancyFormAllV2(initial=initial, cliente_id=pk)
    context = { 
        'vacante': vacante,
        'form': form,
    }

    return render(request, 'admin/vacancy/client_analyst_internal_user/vacancy_edit.html', context)


#detalle de la vacante
@login_required
@validar_permisos('acceso_analista_seleccion_ats')
def detail_vacancy(request, pk):
    # vacante = query_vacanty_detail().get(id=pk)
    vacante = get_object_or_404(Cli052Vacante.objects.prefetch_related('habilidades'), id=pk)
    # Obtener información de las entrevistas por vacante
    entrevistas = query_interview_all()
    entrevistas = entrevistas.filter(asignacion_vacante__vacante_id_052=vacante.id)
    # Obtener preguntas de la vacante
    preguntas = get_vacanty_questions(vacante.id)
    # Obtener los reclutados asociados a la vacante
    reclutados = query_recruited_vacancy_id(vacante.id)

    cliente_id = Cli051Cliente.objects.get(id=vacante.asignacion_cliente_id_064.id_cliente_asignado.id)

    form = VacancyFormAll()

    context ={
        'vacante': vacante,
        'form': form,
        'entrevistas': entrevistas,
        'preguntas': preguntas,
        'reclutados': reclutados,
        'cliente_id': cliente_id,
    }

    return render(request, 'admin/vacancy/client_analyst_internal_user/vacancy_detail.html', context)