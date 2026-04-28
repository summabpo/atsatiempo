from collections import defaultdict
from os.path import basename
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.db.models import F, Count, Q, Value, Case, When, CharField, Max, Prefetch
from django.db import DatabaseError, transaction, IntegrityError
import copy

from django.views.decorators.http import require_POST, require_http_methods
from applications.cliente.models import (
    Cli051Cliente,
    Cli064AsignacionCliente,
    Cli078MotivadoresCandidato,
    Cli085AccionesDecisivas,
    Cli086AsignacionCargoAccionesDecisivas,
)
from applications.cliente.acciones_cargo_utils import acciones_decisivas_asignadas_cargo_activas

from applications.services.service_interview import query_interview_all, attach_ultima_entrevista_a_reclutados
from applications.services.service_recruited import query_recruited_vacancy_id
from applications.reclutado.forms.FormRecruited import ReclutadoCrearForm
from applications.vacante.models import Cli052Vacante, Cli055ProfesionEstudio, Cli053SoftSkill, Cli054HardSkill, Cli052VacanteHardSkillsId054, Cli052VacanteSoftSkillsId053, Cli072FuncionesResponsabilidades, Cli073PerfilVacante, Cli068Cargo, Cli074AsignacionFunciones, Cli075GrupoProfesion
from applications.reclutado.models import (
    Cli056AplicacionVacante,
    Cli063AplicacionVacanteHistorial,
    Cli087ReporteAccionDecisivaReclutado,
)
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
from django.utils import timezone
from django.db.models import OuterRef, Subquery
from datetime import timedelta

#forms
from applications.vacante.forms.VacanteForms import VacancyAssingForm, VacancyFormAllV2, VacancyFormEdit, VacanteForm, VacanteFormEdit, VacancyFormAll, VacancyAssignRecruiterForm

#views
from applications.services.service_vacanty import query_vacanty_all, query_vacanty_detail, get_vacanty_questions

#query
from applications.services.service_client import query_client_detail
from applications.services.service_recruited import (
    consultar_historial_aplicacion_vacante_candidate,
)
from applications.services.service_candidate import buscar_candidato
from applications.usuarios.templatetags.custom_tags import get_match_inicial_porcentaje
from applications.reclutado.views.admin_views import estructurar_resultado_entrevista_json
from applications.candidato.models import Can103Educacion
from applications.services.choices import ESTADO_APLICACION_COLOR_STATIC


from components.RegistrarHistorialVacante import (
    crear_historial_aplicacion,
    obtener_nombre_estado_aplicacion,
)

from components.RegistrarGestionVacante import validar_vacante_cancelar


def _vm2_vacante_ok_for_cliente_session(request, vacante):
    """Si hay cliente en sesión, la vacante debe pertenecer a ese cliente asignado."""
    cid = request.session.get("cliente_id")
    if not cid:
        return True
    asig = getattr(vacante, "asignacion_cliente_id_064", None)
    if not asig or not asig.id_cliente_asignado_id:
        return False
    return int(asig.id_cliente_asignado_id) == int(cid)


def _obtener_asignacion_cliente_existente_para_cliente_asignado(cliente_asignado_id: int):
    """
    Para clientes tipo '3' (Asignado), NO se debe crear CLI064.
    Se debe reutilizar la asignación existente donde el cliente en sesión es el id_cliente_asignado.
    """
    if not cliente_asignado_id:
        return None

    asignacion = (
        Cli064AsignacionCliente.objects.filter(
            id_cliente_asignado_id=cliente_asignado_id,
            estado_id=1,
            tipo_asignacion="2",
        )
        .order_by("-id")
        .first()
    )
    if asignacion:
        return asignacion

    return (
        Cli064AsignacionCliente.objects.filter(
            id_cliente_asignado_id=cliente_asignado_id,
            estado_id=1,
        )
        .order_by("-id")
        .first()
    )


def _calcular_fecha_cierre_planteada_por_cargo(cargo_obj) -> timezone.datetime:
    dias = getattr(cargo_obj, "cantidad_dias_envio_candidatos", None)
    try:
        dias = int(dias) if dias is not None else 0
    except (TypeError, ValueError):
        dias = 0
    if dias <= 0:
        dias = 15
    return timezone.now() + timedelta(days=dias)


@login_required
@validar_permisos('acceso_cliente')
@require_POST
def cancel_vacancy_from_dashboard(request):
    """
    Cancela una vacante (estado 4) desde el dashboard del cliente.
    Espera JSON: { "vacante_id": <int>, "descripcion": <str> }
    """
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)

    vacante_id = payload.get("vacante_id")
    descripcion = (payload.get("descripcion") or "").strip()

    if not vacante_id:
        return JsonResponse({"ok": False, "error": "Falta vacante_id"}, status=400)
    if not descripcion:
        return JsonResponse({"ok": False, "error": "La descripción de cancelación es obligatoria"}, status=400)

    cliente_id = request.session.get("cliente_id")
    if not cliente_id:
        return JsonResponse({"ok": False, "error": "Sesión de cliente no encontrada"}, status=403)

    vacante = (
        Cli052Vacante.objects.select_related("asignacion_cliente_id_064")
        .filter(id=vacante_id, estado_id_001_id=1)
        .filter(Q(asignacion_cliente_id_064__id_cliente_asignado_id=cliente_id) | Q(asignacion_cliente_id_064__id_cliente_maestro_id=cliente_id))
        .first()
    )
    if not vacante:
        return JsonResponse({"ok": False, "error": "Vacante no encontrada"}, status=404)

    if int(vacante.estado_vacante) not in (1, 2):
        return JsonResponse({"ok": False, "error": "La vacante no está en un estado cancelable"}, status=409)

    url_actual = f"{request.scheme}://{request.get_host()}"

    try:
        with transaction.atomic():
            # Cancela aplicaciones relacionadas (si aplica) y envía correo
            validar_vacante_cancelar(vacante, url_actual)

            vacante.estado_vacante = 4
            vacante.comentarios = descripcion
            vacante.save(update_fields=["estado_vacante", "comentarios"])
    except Exception as e:
        return JsonResponse({"ok": False, "error": "No fue posible cancelar la vacante"}, status=500)

    return JsonResponse({"ok": True, "vacante_id": vacante.id})


#crear todas las vacantes
@login_required
@validar_permisos('acceso_cliente')
def create_vacanty(request):

    # Verificar si el cliente_id está en la sesión
    cliente_id = request.session.get('cliente_id')

    # Data cliente a mostrar
    data = query_client_detail(cliente_id)

    vacantes = Cli052Vacante.objects.select_related(
        'asignacion_cliente_id_064__id_cliente_asignado'
    ).filter(
        asignacion_cliente_id_064__id_cliente_asignado=cliente_id,
        asignacion_cliente_id_064__tipo_asignacion='1'  # Aquí va el campo correcto
    )

    form = VacancyFormAll(cliente_id=cliente_id)

    if request.method == 'POST':
        form = VacancyFormAll(request.POST, cliente_id=cliente_id)

        if form.is_valid():

            #datos principales
            titulo = form.cleaned_data['titulo']                            #perfil de la vacante
            cargo = form.cleaned_data['cargo']                              #perfil de la vacante
            numero_posiciones = form.cleaned_data['numero_posiciones']      #perfil de la vacante
            cantidad_presentar = form.cleaned_data['cantidad_presentar']     #perfil de la vacante    
            fecha_presentacion = Cli052Vacante.fecha_presentacion_desde_date_formulario(
                form.cleaned_data['fecha_presentacion']
            )
            

            #detalles del trabajo
            termino_contrato = form.cleaned_data['termino_contrato']
            tiempo_experiencia = form.cleaned_data['tiempo_experiencia']
            modalidad = form.cleaned_data['modalidad']
            jornada = form.cleaned_data['jornada']
            
            #lugar del trabajo
            lugar_trabajo = form.cleaned_data['lugar_trabajo']
            barrio =  form.cleaned_data['barrio']
            direccion =  form.cleaned_data['direccion']
            url_mapa = form.cleaned_data['url_mapa']
            
            horario_inicio = form.cleaned_data['horario_inicio']
            horario_final = form.cleaned_data['horario_final']
            hora_inicio = form.cleaned_data['hora_inicio']
            hora_final = form.cleaned_data['hora_final']
            
            #requisitos y habilidades
            soft_skills = form.cleaned_data['soft_skills']
            hard_skills = form.cleaned_data['hard_skills']
            idioma = form.cleaned_data['idioma']
            nivel_idioma = form.cleaned_data['nivel_idioma']
            profesion_estudio = form.cleaned_data['profesion_estudio']
            nivel_estudio = form.cleaned_data['nivel_estudio']
            edad_inicial = form.cleaned_data['edad_inicial']
            edad_final = form.cleaned_data['edad_final']
            genero = form.cleaned_data['genero']
            

            #informacion salarial
            salario = form.cleaned_data['salario']
            
            tipo_salario = form.cleaned_data['tipo_salario']
            frecuencia_pago = form.cleaned_data['frecuencia_pago']
            salario_adicional = form.cleaned_data['salario_adicional']

            #responsabilidad del cargo
            funciones_responsabilidades = form.cleaned_data['funciones_responsabilidades']

            #descripcion de la vacante
            descripcion_vacante = form.cleaned_data['descripcion_vacante']

            #creacion del perfil de la vacante
            perfil_vacante, perfil_vacante_nuevo = Cli073PerfilVacante.objects.get_or_create(
                edad_inicial=edad_inicial,
                edad_final=edad_final,
                genero=genero,
                tiempo_experiencia=tiempo_experiencia,
                modalidad=modalidad,
                jornada=jornada,
                salario=salario,
                tipo_salario=tipo_salario,
                frecuencia_pago=frecuencia_pago,
                salario_adicional=salario_adicional,
                idioma=idioma,
                nivel_idioma=nivel_idioma,
                profesion_estudio=Cli055ProfesionEstudio.objects.get(id=profesion_estudio),
                nivel_estudio=nivel_estudio,
                estado_estudio=False,  # Assuming default value
                lugar_trabajo=Cat004Ciudad.objects.get(id=lugar_trabajo),
                termino_contrato=termino_contrato,
                estado=Cat001Estado.objects.get(id=1),
                horario_inicio=horario_inicio,  # Assuming default value
                horario_final=horario_final,  # Assuming default value
                hora_inicio=hora_inicio,  # Assuming default value
                hora_final=hora_final,  # Assuming default value
                barrio=barrio,  # Assuming default value
                direccion=direccion,  # Assuming default value
                url_mapa=url_mapa  # Assuming default value
            )

        
            #verificacion de asignación vacante
            cliente_tipo = (
                Cli051Cliente.objects.only("tipo_cliente").get(id=cliente_id).tipo_cliente
            )
            if str(cliente_tipo) == "3":
                asignacion_cliente = _obtener_asignacion_cliente_existente_para_cliente_asignado(
                    int(cliente_id)
                )
                if not asignacion_cliente:
                    messages.error(
                        request,
                        "No se encontró una asignación activa para este cliente asignado. "
                        "Contacte al administrador para validar la asignación (CLI064).",
                    )
                    return redirect("vacantes:vacantes_listado_cliente")
            else:
                asignacion_cliente, _ = Cli064AsignacionCliente.objects.get_or_create(
                    id_cliente_maestro=Cli051Cliente.objects.get(id=1000),
                    id_cliente_asignado=Cli051Cliente.objects.get(id=cliente_id),
                    defaults={
                        "tipo_asignacion": "1",
                        "estado": Cat001Estado.objects.get(id=1),
                    },
                )

            #creacion de la vacante
            cargo_obj = Cli068Cargo.objects.get(id=cargo)
            vacante = Cli052Vacante.objects.create(
                titulo=titulo,
                numero_posiciones=numero_posiciones,
                cantidad_presentar=cantidad_presentar,
                estado_vacante=1,
                estado_id_001=Cat001Estado.objects.get(id=1),
                fecha_presentacion=fecha_presentacion,
                # usuario_asignado=request.user,
                asignacion_cliente_id_064=asignacion_cliente,
                cargo=cargo_obj,
                perfil_vacante=perfil_vacante,
                descripcion_vacante=descripcion_vacante,
                fecha_cierra_planteada=_calcular_fecha_cierre_planteada_por_cargo(cargo_obj),
            )

            # Convertir el string JSON en un objeto Python (lista de diccionarios)
            skills = json.loads(soft_skills)
            
            # Ahora puedes iterar sobre la lista de diccionarios
            for skill in skills:
                # Intentar obtener el objeto soft_skills
                soft_skills, created = Cli053SoftSkill.objects.get_or_create(
                    nombre = skill['value'],
                    defaults={'estado_id_001': Cat001Estado.objects.get(id=1)}
                )

                Cli052VacanteSoftSkillsId053.objects.create(
                    cli052vacante=vacante,
                    cli053softskill=soft_skills
                )


            # Convertir el string JSON en un objeto Python (lista de diccionarios)
            skills = json.loads(hard_skills)
            
            # Ahora puedes iterar sobre la lista de diccionarios
            for skill in skills:
                # Intentar obtener el objeto hard_skills
                hard_skills, created = Cli054HardSkill.objects.get_or_create(
                    nombre = skill['value'],
                    defaults={'estado_id_001': Cat001Estado.objects.get(id=1)}
                )

                Cli052VacanteHardSkillsId054.objects.create(
                    cli052vacante=vacante,
                    cli054hardskill=hard_skills
                )

            # Iteraciones con las funciones y la vacante
            funciones_responsabilidades = json.loads(funciones_responsabilidades)
            for funcion in funciones_responsabilidades:
                funcion_responsabilidad, created = Cli072FuncionesResponsabilidades.objects.get_or_create(
                    nombre=funcion['value'],
                    defaults={'estado': Cat001Estado.objects.get(id=1)}
                )

                Cli074AsignacionFunciones.objects.create(
                    vacante=vacante,
                    funcion_responsabilidad=funcion_responsabilidad,
                    estado=Cat001Estado.objects.get(id=1)
                )

            # form.save()
            messages.success(request, 'Vacante creada correctamente')
            return redirect('vacantes:vacantes_listado_cliente')

        else:
            print(form.errors)
    else:
        form = VacancyFormAll(cliente_id=cliente_id)

    context = {
        'form': form,
        'vacantes': vacantes,
    }

    return render(request, 'admin/vacancy/client_user/vacancy_create.html', context)

@login_required
@validar_permisos('acceso_cliente')
def create_vacanty_v2(request):
    # Verificar si el cliente_id está en la sesión
    cliente_id = request.session.get('cliente_id')

    form = VacancyFormAllV2(cliente_id=cliente_id)

    if request.method == 'POST':
        form = VacancyFormAllV2(request.POST, cliente_id=cliente_id)

        if form.is_valid():
            # Asignación cliente:
            # - Si es cliente tipo 3 (Asignado): reutilizar CLI064 existente (NO crear).
            # - Para los demás: se mantiene la lógica actual.
            cliente_tipo = (
                Cli051Cliente.objects.only("tipo_cliente").get(id=cliente_id).tipo_cliente
            )
            if str(cliente_tipo) == "3":
                asignacion_cliente = _obtener_asignacion_cliente_existente_para_cliente_asignado(
                    int(cliente_id)
                )
                if not asignacion_cliente:
                    messages.error(
                        request,
                        "No se encontró una asignación activa para este cliente asignado. "
                        "Contacte al administrador para validar la asignación (CLI064).",
                    )
                    return redirect("vacantes:vacantes_listado_cliente")
            else:
                asignacion_cliente, _ = Cli064AsignacionCliente.objects.get_or_create(
                    id_cliente_maestro=Cli051Cliente.objects.get(id=1000),
                    id_cliente_asignado=Cli051Cliente.objects.get(id=cliente_id),
                    defaults={
                        "tipo_asignacion": "1",
                        "estado": Cat001Estado.objects.get(id=1),
                    },
                )
            # --- 1. Recolecta los datos de los campos JSON en listas de Python ---
            # Motivo de la vacante
            motivo_vacante_data = {
                "motivo": form.cleaned_data.get('motivo_vacante'),
                "otro_motivo": form.cleaned_data.get('otro_motivo')
            }

            # Horarios con estructura mejorada
            tipo_horario = form.cleaned_data.get('tipo_horario')
            horarios_data = {
                "tipo": tipo_horario,
                "bloques": []
            }
            
            for i in range(1, 4):
                horario_inicio = form.cleaned_data.get(f'horario_inicio_{i}')
                horario_final = form.cleaned_data.get(f'horario_final_{i}')
                hora_inicio = form.cleaned_data.get(f'hora_inicio_{i}')
                hora_final = form.cleaned_data.get(f'hora_final_{i}')
                
                if all([horario_inicio, horario_final, hora_inicio, hora_final]):
                    horarios_data["bloques"].append({
                        "dia_inicio": horario_inicio,
                        "dia_final": horario_final,
                        "hora_inicio": str(hora_inicio),
                        "hora_final": str(hora_final),
                        "bloque": i
                    })
            
            # Funciones y responsabilidades
            funciones_data = []
            for i in range(1,4):
                funcion = form.cleaned_data.get(f'funciones_responsabilidades_{i}')
                if funcion:
                    funciones_data.append({"bloque": i, "funcion": funcion})

            # Experiencia laboral
            experiencia_data = []
            for i in range(1,4):
                tiempo_experiencia = form.cleaned_data.get(f'tiempo_experiencia_{i}')
                experiencia_especifica = form.cleaned_data.get(f'experiencia_especifica_en_{i}')
                if tiempo_experiencia and experiencia_especifica:
                    experiencia_data.append({
                        "bloque": i,
                        "tiempo_experiencia" : tiempo_experiencia,
                        "experiencia_especifica" : experiencia_especifica,
                    })

            # Idiomas
            idiomas_data = []
            for i in range(1,3): # Asumiendo 2 bloques de idiomas
                idioma = form.cleaned_data.get(f'idioma_{i}')
                nivel_idioma = form.cleaned_data.get(f'nivel_idioma_{i}')
                if idioma and nivel_idioma:
                    idiomas_data.append({
                        "bloque": i,
                        "idioma" : idioma,
                        "nivel" : nivel_idioma,
                    })
            
            # Estudios complementarios
            estudios_data = []
            for i in range(1,4):
                estudio = form.cleaned_data.get(f'estudios_complementarios_{i}')
                certificado = form.cleaned_data.get(f'estudios_complementarios_certificado_{i}')
                if estudio: # Certificado puede ser False
                    estudios_data.append({
                        "bloque": i,
                        "estudio" : estudio,
                        "certificado" : certificado,
                    })

            # --- 2. Crea el Perfil de la Vacante pasando los objetos Python ---
            # Handle grupo_profesion field properly
            grupo_profesion_value = form.cleaned_data['grupo_profesion']
            grupo_profesion_obj = None
            if grupo_profesion_value and grupo_profesion_value != '':
                try:
                    grupo_profesion_obj = Cli075GrupoProfesion.objects.get(id=grupo_profesion_value)
                except Cli075GrupoProfesion.DoesNotExist:
                    grupo_profesion_obj = None
            
            # Handle profesion_estudio field properly
            profesion_estudio_value = form.cleaned_data['profesion_estudio']
            profesion_estudio_obj = None
            if profesion_estudio_value and profesion_estudio_value != '':
                try:
                    profesion_estudio_obj = Cli055ProfesionEstudio.objects.get(id=profesion_estudio_value)
                except Cli055ProfesionEstudio.DoesNotExist:
                    profesion_estudio_obj = None

            estudios_complentarios_all = []
            for i in range(1,4):
                estudios_complementarios = form.cleaned_data.get(f'estudios_complementarios_{i}')
                estudios_complementarios_certificado = form.cleaned_data.get(f'estudios_complementarios_certificado_{i}')

                if all([estudios_complementarios, estudios_complementarios_certificado]):
                    estudios_complentarios_all.append({
                        "estudio" : estudios_complementarios,
                        "certificado_estudios_complementarios" : estudios_complementarios_certificado,
                    })
            json_estudios_complementarios = json.dumps(estudios_complentarios_all, ensure_ascii=False)

            # Competencias
            relacionales = form.cleaned_data.get('skill_relacionales', [])
            personales = form.cleaned_data.get('skill_personales', [])
            cognitivas = form.cleaned_data.get('skill_cognitivas', [])
            digitales = form.cleaned_data.get('skill_digitales', [])
            liderazgo = form.cleaned_data.get('skill_liderazgo', [])
            
            all_selected_skills = (
                list(relacionales) +
                list(personales) +
                list(cognitivas) +
                list(digitales) +
                list(liderazgo)
            )

            
            #fitcultural 
            # Fit Cultural (Los campos son ModelChoiceField, no ModelMultipleChoiceField)
            fit_cultural_objects = []
            
            # Agregar cada selección individual si existe
            if form.cleaned_data.get('grupo_fit_1'):
                fit_cultural_objects.append(form.cleaned_data['grupo_fit_1'])
            if form.cleaned_data.get('grupo_fit_2'):
                fit_cultural_objects.append(form.cleaned_data['grupo_fit_2'])
            if form.cleaned_data.get('grupo_fit_3'):
                fit_cultural_objects.append(form.cleaned_data['grupo_fit_3'])
            if form.cleaned_data.get('grupo_fit_4'):
                fit_cultural_objects.append(form.cleaned_data['grupo_fit_4'])
            if form.cleaned_data.get('grupo_fit_5'):
                fit_cultural_objects.append(form.cleaned_data['grupo_fit_5'])

            #motivadores
            motivadores_candidato = form.cleaned_data.get('motivadores_candidato')

            #Comentarios 
            comentarios= form.cleaned_data.get('comentarios')
            descripcion_vacante = form.cleaned_data.get('descripcion_vacante')

            #creacion perfil de la vacante
            cargo_obj = Cli068Cargo.objects.get(id=form.cleaned_data['cargo'])

            perfil_vacante = Cli073PerfilVacante.objects.create(
                edad_inicial=form.cleaned_data['edad_inicial'],
                edad_final=form.cleaned_data['edad_final'],
                genero=form.cleaned_data['genero'],
                tiempo_experiencia=1,
                modalidad=form.cleaned_data['modalidad'],
                salario=form.cleaned_data['salario'].replace('.', ''),
                tipo_salario=form.cleaned_data['tipo_salario'],
                frecuencia_pago=form.cleaned_data['frecuencia_pago'],
                salario_adicional=form.cleaned_data['salario_adicional'],
                profesion_estudio=profesion_estudio_obj,
                nivel_estudio=form.cleaned_data['nivel_estudio'],
                estado_estudio=form.cleaned_data['estado_estudio'],
                lugar_trabajo_id=form.cleaned_data['lugar_trabajo'],
                barrio=form.cleaned_data['barrio'],
                direccion=form.cleaned_data['direccion'],
                termino_contrato=form.cleaned_data['termino_contrato'],
                tipo_horario=tipo_horario,
                # Pasa las listas de Python directamente
                motivo_vacante=motivo_vacante_data,
                horario=horarios_data,
                experiencia_laboral=experiencia_data,
                idiomas=idiomas_data,
                estudio_complementario=estudios_data,
                funciones_responsabilidades=funciones_data,
                tipo_profesion=form.cleaned_data['tipo_profesion'],
                profesion_estudio_listado=form.cleaned_data['profesion_estudio_listado'],
                grupo_profesion=grupo_profesion_obj,
            )

            # --- 3. Crea la Vacante ---
            
            vacante = Cli052Vacante.objects.create(
                cargo=cargo_obj,
                numero_posiciones=form.cleaned_data['numero_posiciones'],
                cantidad_presentar=form.cleaned_data['cantidad_presentar'],
                titulo=f'Vacante para el cargo: {cargo_obj.nombre_cargo}',
                fecha_presentacion=Cli052Vacante.fecha_presentacion_desde_date_formulario(
                    form.cleaned_data['fecha_presentacion']
                ),
                asignacion_cliente_id_064=asignacion_cliente,
                perfil_vacante=perfil_vacante,
                descripcion_vacante=form.cleaned_data.get('descripcion_vacante'),
                comentarios=form.cleaned_data.get('comentarios'),
                requerimientos_especiales=form.cleaned_data.get('requerimientos_especiales'),
                fecha_cierra_planteada=_calcular_fecha_cierre_planteada_por_cargo(cargo_obj),
            )
            
            # Asignar motivadores múltiples
            motivadores_ids = form.cleaned_data.get('motivadores_candidato', [])
            if motivadores_ids:
                motivadores_objects = Cli078MotivadoresCandidato.objects.filter(id__in=motivadores_ids)
                vacante.motivadores.set(motivadores_objects)
            
            # 1. Combina todos los objetos skill del formulario en una sola lista
            skills_seleccionadas = (
                list(form.cleaned_data.get('skill_relacionales', [])) +
                list(form.cleaned_data.get('skill_personales', [])) +
                list(form.cleaned_data.get('skill_cognitivas', [])) +
                list(form.cleaned_data.get('skill_digitales', [])) +
                list(form.cleaned_data.get('skill_liderazgo', []))
            )

            # 2. Usa .set() en tu nuevo campo 'habilidades'. Django hace todo el trabajo.
            if skills_seleccionadas:
                vacante.habilidades.set(skills_seleccionadas)

            # Fit Cultural (Los campos son ModelChoiceField, no ModelMultipleChoiceField)
            if fit_cultural_objects:
                # .set() espera una lista de objetos o de IDs. Ambas funcionan.
                vacante.fit_cultural.set(fit_cultural_objects)
            
            messages.success(request, 'Vacante creada correctamente')
            return redirect('vacantes:vacantes_listado_cliente')
        else:
            error_messages = []
            for field, errors in form.errors.items():
                if field == '__all__':
                    for error in errors:
                        error_messages.append(str(error))
                else:
                    field_obj = form.fields.get(field)
                    field_label = field_obj.label if (field_obj and field_obj.label) else field.replace('_', ' ').title()
                    error_messages.append(f"{field_label}: {', '.join(str(e) for e in errors)}")
            msg = 'Por favor revise el formulario. ' + ' | '.join(error_messages) if error_messages else 'Por favor revise el formulario.'
            messages.error(request, msg)
            
    else:
        form = VacancyFormAllV2(cliente_id=cliente_id)

    cargos_refs_map = {
        str(c.id): (c.referencias_laborales or 0)
        for c in Cli068Cargo.objects.filter(cliente_id=cliente_id)
    }
    context = {
        'form': form,
        'cargos_refs_map': cargos_refs_map,
    }

    return render(request, 'admin/vacancy/client_user/vacancy_create_v2.html', context)

#listar todas las vacantes del cliente
@login_required
@validar_permisos('acceso_cliente')
def list_vacanty_all(request):

    # Verificar si el cliente_id está en la sesión
    cliente_id = request.session.get('cliente_id')
    
    # Obtener el cliente correspondiente al ID
    cliente = get_object_or_404(Cli051Cliente, id=cliente_id)

    vacantes = query_vacanty_all()
    vacantes = vacantes.filter(
        estado_id_001=1,  # Asumiendo que ese es el campo correcto para el estado
        asignacion_cliente_id_064__id_cliente_asignado=cliente
    ).order_by('-fecha_creacion')  # Más recientes primero, luego las más antiguas

    context ={ 
        'vacantes': vacantes,
        'vacantes_filtro': 'todas',
    }

    return render(request, 'admin/vacancy/client_user/vacancy_list.html', context)


@login_required
@validar_permisos('acceso_cliente')
def list_vacanty_pendientes(request):
    """Listado de vacantes activas o en proceso (pendientes)."""
    cliente_id = request.session.get('cliente_id')
    cliente = get_object_or_404(Cli051Cliente, id=cliente_id)

    vacantes = (
        query_vacanty_all()
        .filter(estado_id_001=1, asignacion_cliente_id_064__id_cliente_asignado=cliente)
        .filter(estado_vacante__in=(1, 2))
        .order_by('-fecha_creacion')
    )
    return render(
        request,
        'admin/vacancy/client_user/vacancy_list.html',
        {'vacantes': vacantes, 'vacantes_filtro': 'pendientes'},
    )


@login_required
@validar_permisos('acceso_cliente')
def pending_vacancies_summary(request):
    """
    Resumen de vacantes pendientes (Activa / En proceso) en un solo tablero:
    - selector de vacante
    - "talento enviado" (candidatos asociados + match inicial si existe)
    - panorama (talento por enviar / validación de confianza / viaje de contratación)
    - línea de tiempo (historial de la aplicación más reciente)
    """
    cliente_id = request.session.get('cliente_id')
    cliente = get_object_or_404(Cli051Cliente, id=cliente_id)

    vacantes = (
        query_vacanty_all()
        .filter(estado_id_001=1, asignacion_cliente_id_064__id_cliente_asignado=cliente)
        .filter(estado_vacante__in=(1, 2))
        .select_related("cargo")
        .order_by('-fecha_creacion')
    )

    vacante_id = request.GET.get("vacante_id")
    vacante_seleccionada = None
    if vacante_id:
        vacante_seleccionada = vacantes.filter(id=vacante_id).first()
    if not vacante_seleccionada:
        vacante_seleccionada = vacantes.first()

    aplicaciones = []
    aplicaciones_enviadas = []
    envios_al_cliente_cronologico = []
    dias_gestion_vacante = None
    timeline_items = []
    panorama = {"talento_por_enviar": 0, "validacion_confianza": 0, "viaje_contratacion": 0}

    if vacante_seleccionada:
        aplicaciones_qs = (
            Cli056AplicacionVacante.objects.select_related("candidato_101")
            .filter(vacante_id_052_id=vacante_seleccionada.id)
            .order_by("-fecha_actualizacion", "-fecha_aplicacion", "-id")
        )
        aplicaciones = list(aplicaciones_qs[:200])

        # "Enviados al cliente": desde Entrevista Programada (3) en adelante
        aplicaciones_enviadas = list(aplicaciones_qs.filter(estado_aplicacion__gte=3)[:50])
        envios_al_cliente_cronologico = list(
            aplicaciones_qs.filter(estado_aplicacion__gte=3).order_by("fecha_actualizacion", "id")[:40]
        )

        creacion = vacante_seleccionada.fecha_creacion
        if creacion:
            if timezone.is_aware(creacion):
                d0 = timezone.localtime(creacion).date()
            else:
                d0 = creacion.date()
            dias_gestion_vacante = max(0, (timezone.localdate() - d0).days)

        panorama["talento_por_enviar"] = 1 if aplicaciones_qs.filter(estado_aplicacion__gte=3).count() == 0 else 0
        panorama["validacion_confianza"] = aplicaciones_qs.filter(estado_aplicacion=5).count()
        panorama["viaje_contratacion"] = aplicaciones_qs.filter(estado_aplicacion=13).count()

        aplicacion_timeline = aplicaciones_qs.first()
        if aplicacion_timeline:
            timeline_items = list(
                Cli063AplicacionVacanteHistorial.objects.filter(aplicacion_vacante_056_id=aplicacion_timeline.id)
                .order_by("-fecha")[:12]
            )

    context = {
        "vacantes": vacantes,
        "vacante": vacante_seleccionada,
        "aplicaciones": aplicaciones,
        "aplicaciones_enviadas": aplicaciones_enviadas,
        "envios_al_cliente_cronologico": envios_al_cliente_cronologico,
        "dias_gestion_vacante": dias_gestion_vacante,
        "panorama": panorama,
        "timeline_items": timeline_items,
        "now": timezone.now(),
    }
    return render(request, "admin/vacancy/client_user/vacancy_pendientes_summary.html", context)


@login_required
@validar_permisos('acceso_cliente')
def list_vacanty_finalizadas(request):
    """Listado de vacantes finalizadas/cerradas."""
    cliente_id = request.session.get('cliente_id')
    cliente = get_object_or_404(Cli051Cliente, id=cliente_id)

    vacantes = (
        query_vacanty_all()
        .filter(estado_id_001=1, asignacion_cliente_id_064__id_cliente_asignado=cliente)
        .filter(estado_vacante=3)
        .order_by('-fecha_creacion')
    )
    return render(
        request,
        'admin/vacancy/client_user/vacancy_list.html',
        {'vacantes': vacantes, 'vacantes_filtro': 'finalizadas'},
    )


@login_required
@validar_permisos('acceso_cliente')
def list_vacanty_vencidas(request):
    """Listado de vacantes vencidas (fecha_cierra_planteada < hoy y sigue activa/en proceso)."""
    cliente_id = request.session.get('cliente_id')
    cliente = get_object_or_404(Cli051Cliente, id=cliente_id)

    vacantes = (
        query_vacanty_all()
        .filter(estado_id_001=1, asignacion_cliente_id_064__id_cliente_asignado=cliente)
        .filter(estado_vacante__in=(1, 2))
        .filter(fecha_cierra_planteada__isnull=False)
        .filter(fecha_cierra_planteada__lt=timezone.now())
        .order_by('-fecha_creacion')
    )
    return render(
        request,
        'admin/vacancy/client_user/vacancy_list.html',
        {'vacantes': vacantes, 'vacantes_filtro': 'vencidas'},
    )


@login_required
@validar_permisos('acceso_cliente')
def vacancy_management_summary(request, pk, vacante_id):
    """
    Resumen de gestión de una vacante finalizada:
    - métricas (aplicados/en proceso/seleccionados/contratados)
    - candidato contratado (seleccionable si hay varios)
    - línea de tiempo basada en historial de la aplicación
    """
    cliente_id = request.session.get('cliente_id')
    cliente = get_object_or_404(Cli051Cliente, id=cliente_id)

    vacante = get_object_or_404(
        Cli052Vacante.objects.select_related(
            'cargo',
            'asignacion_cliente_id_064',
            'asignacion_cliente_id_064__id_cliente_asignado',
        ),
        id=vacante_id,
        estado_id_001=1,
        asignacion_cliente_id_064__id_cliente_asignado=cliente,
    )

    metricas = Cli056AplicacionVacante.calcular_cantidades_y_porcentajes(vacante.id)

    contratados_qs = (
        Cli056AplicacionVacante.objects.select_related('candidato_101')
        .filter(vacante_id_052_id=vacante.id, estado_aplicacion=15)
        .order_by('fecha_actualizacion', 'fecha_aplicacion', 'id')
    )

    aplicacion_id = request.GET.get('aplicacion')
    aplicacion_seleccionada = None
    if aplicacion_id and str(aplicacion_id).isdigit():
        aplicacion_seleccionada = contratados_qs.filter(id=int(aplicacion_id)).first()
    if not aplicacion_seleccionada:
        aplicacion_seleccionada = contratados_qs.first()

    timeline = []
    if aplicacion_seleccionada:
        timeline = list(
            Cli063AplicacionVacanteHistorial.objects.filter(
                aplicacion_vacante_056_id=aplicacion_seleccionada.id
            )
            .select_related('usuario_id_genero')
            .order_by('-fecha')
        )

    timeline_rows = []
    icon_by_estado = {
        1: "assignment",
        2: "event",
        3: "check_circle",
        4: "cancel",
        5: "task",
        6: "verified",
        7: "dangerous",
        8: "person_check",
        9: "flag",
        10: "block",
        11: "logout",
        12: "do_not_disturb_on",
        13: "hourglass_top",
        14: "cancel",
        15: "check_circle",
    }
    for h in timeline:
        estado_code = getattr(h, "estado", None)
        estado_nombre, color = ESTADO_APLICACION_COLOR_STATIC.get(
            estado_code, (obtener_nombre_estado_aplicacion(estado_code), "secondary")
        )
        badge_bg = f"bg-{color} bg-opacity-10 text-{color}"
        timeline_rows.append(
            {
                'fecha': h.fecha,
                'estado': estado_code,
                'estado_nombre': estado_nombre,
                'badge_bg': badge_bg,
                'icon': icon_by_estado.get(estado_code, "timeline"),
                'descripcion': getattr(h, 'descripcion', None),
                'usuario': getattr(h, 'usuario_id_genero', None),
            }
        )

    # Gráfica por candidato (según aplicación seleccionada): usa promedios/calificaciones del reporte final.
    reporte_chart = None
    reporte_compacto_html = ''
    if aplicacion_seleccionada:
        entrevista = (
            Cli057AsignacionEntrevista.objects.filter(
                asignacion_vacante=aplicacion_seleccionada,
                resultado_entrevista__isnull=False,
            )
            .exclude(resultado_entrevista={})
            .order_by('-fecha_entrevista', '-hora_entrevista')
            .first()
        )

        json_match_inicial_raw = aplicacion_seleccionada.json_match_inicial
        json_match_inicial = {}
        if json_match_inicial_raw:
            try:
                json_match_inicial = (
                    json.loads(json_match_inicial_raw)
                    if isinstance(json_match_inicial_raw, str)
                    else json_match_inicial_raw
                )
            except (json.JSONDecodeError, TypeError):
                json_match_inicial = {}

        resultado_part = estructurar_resultado_entrevista_json(
            entrevista.resultado_entrevista if entrevista else None,
            json_match_inicial,
        )
        promedios = resultado_part.get('promedios') or {}
        pruebas_list = resultado_part.get('pruebas') or []
        conf = resultado_part.get('confiabilidad_riesgo') or {}

        def _to_float(v):
            try:
                return float(v)
            except (TypeError, ValueError):
                return 0.0

        labels = [
            'Hard Skills',
            'Habilidades',
            'Fit cultural',
            'Motivadores',
            'Pruebas',
            'Confiabilidad / riesgo',
        ]
        keys = ['hard_skills', 'habilidades', 'fit_cultural', 'motivadores', 'pruebas', 'confiabilidad_riesgo']
        values = [
            _to_float(promedios.get('hard_skills')),
            _to_float(promedios.get('habilidades')),
            _to_float(promedios.get('fit_cultural')),
            _to_float(promedios.get('motivadores')),
            _to_float(pruebas_list[0].get('calificacion')) if isinstance(pruebas_list, list) and pruebas_list else 0.0,
            _to_float(conf.get('calificacion')) if isinstance(conf, dict) else 0.0,
        ]
        promedio_total = _to_float(resultado_part.get('promedio_total'))
        pct = int(max(0, min(100, round(promedio_total * 10)))) if promedio_total else 0

        # Bandas de color como vm2 (según % global).
        if pct >= 80:
            color = '#198754'
        elif pct >= 60:
            color = '#f59e0b'
        elif pct >= 40:
            color = '#0ea5e9'
        elif pct > 0:
            color = '#6c757d'
        else:
            color = '#B10022'

        def _vm2_resumen_score_badge(val):
            try:
                v = float(val)
            except (TypeError, ValueError):
                v = 0.0
            if v >= 8:
                return 'text-success bg-success bg-opacity-10 border-success'
            if v >= 6:
                return 'text-warning bg-warning bg-opacity-10 border-warning'
            if v >= 4:
                return 'text-warning bg-warning bg-opacity-10 border-warning'
            if v > 0:
                return 'text-danger bg-danger bg-opacity-10 border-danger'
            return 'text-secondary bg-secondary bg-opacity-10 border-secondary'

        rounded_vals = [round(max(0.0, min(10.0, v)), 2) for v in values]
        stat_cards = []
        for i, k in enumerate(keys):
            val = rounded_vals[i] if i < len(rounded_vals) else 0.0
            score_txt = f'{val:.1f}' if val > 0 else '—'
            stat_cards.append(
                {
                    'key': k,
                    'label': labels[i],
                    'score': score_txt,
                    'badge': _vm2_resumen_score_badge(val),
                }
            )

        reporte_chart = {
            'labels': labels,
            'keys': keys,
            'values': rounded_vals,
            'pct': pct,
            'color': color,
            'stat_cards': stat_cards,
        }
        reporte_compacto_html = render_to_string(
            'admin/vacancy/partials/modal_entrevista_resultado_reporte_compacto.html',
            {'datos_reporte_final': resultado_part},
        )

    banner_ctx = {
        'nombre': '—',
        'estudio': '—',
        'ciudad': '—',
        'imagen': None,
    }
    respuesta_cliente = ''
    if aplicacion_seleccionada:
        reg = aplicacion_seleccionada.registro_reclutamiento
        if isinstance(reg, dict):
            respuesta_cliente = (reg.get('descripcion_respuesta_cliente') or '').strip()
        cand = aplicacion_seleccionada.candidato_101
        if cand:
            det = buscar_candidato(cand.id)
            estudio = '—'
            eds = det.get('educacion') or []
            if eds:
                e0 = eds[0]
                estudio = (
                    e0.get('titulo')
                    or e0.get('carrera')
                    or e0.get('tipo_estudio')
                    or '—'
                )
            banner_ctx = {
                'nombre': (det.get('nombre_completo') or cand.nombre_completo()),
                'estudio': estudio,
                'ciudad': (det.get('ciudad') or '—'),
                'imagen': det.get('imagen_perfil'),
            }

    duracion_cierre = None
    if vacante.fecha_creacion and vacante.fecha_cierre:
        duracion_cierre = vacante.fecha_cierre - vacante.fecha_creacion

    total_postulaciones = Cli056AplicacionVacante.objects.filter(vacante_id_052_id=vacante.id).count()
    no_aptos_cnt = (metricas.get('no_aptas') or {}).get('cantidad', 0) if isinstance(metricas, dict) else 0
    contratados_cnt = contratados_qs.count()
    resumen_cifras = {
        'total_aplicaron': total_postulaciones,
        'no_aptos': no_aptos_cnt,
        'contratados': contratados_cnt,
    }

    context = {
        'vacante': vacante,
        'metricas': metricas,
        'resumen_cifras': resumen_cifras,
        'contratados': contratados_qs,
        'aplicacion_seleccionada': aplicacion_seleccionada,
        'timeline': timeline_rows,
        'duracion_cierre': duracion_cierre,
        'reporte_chart': reporte_chart,
        'reporte_compacto_html': reporte_compacto_html,
        'banner_ctx': banner_ctx,
        'respuesta_cliente': respuesta_cliente,
    }
    return render(request, 'admin/vacancy/client_user/vacancy_management_summary.html', context)


#gestionar la vacante
@login_required
@validar_permisos('acceso_cliente')
def vacancy_management_from_client(request, pk, vacante_id):
    # Verificar si el cliente_id está en la sesión
    cliente_id = request.session.get('cliente_id')
    grupo_id = request.session.get('grupo_id')
    form_errors = False
    print(grupo_id)
    
    # Data cliente a mostrar
    data = query_client_detail(pk)
    vacante = get_object_or_404(Cli052Vacante.objects.prefetch_related('habilidades'), id=vacante_id)
    

    # Obtener información de las entrevistas por vacante
    entrevistas = query_interview_all()
    entrevistas = entrevistas.filter(asignacion_vacante__vacante_id_052=vacante.id)

    # Obtener preguntas de la vacante
    preguntas = get_vacanty_questions(vacante.id)

    # Obtener los reclutados asociados a la vacante con estado_aplicacion = 3,5
    reclutados = query_recruited_vacancy_id(vacante.id).filter(estado_aplicacion__in=[3,5])
    
    # Para este template solo mostramos finalistas (estado_aplicacion = 8)
    # Ordenar por fecha de aplicación ascendente
    from django.utils import timezone
    reclutados_finalizalista = sorted(list(reclutados), key=lambda x: (x.fecha_aplicacion or timezone.now(), x.id))
    attach_ultima_entrevista_a_reclutados(reclutados_finalizalista)

    # Mantener las otras listas vacías para compatibilidad con el template
    reclutados_recibido = []
    reclutados_seleccionado = []
    reclutados_descartado = []
    

    # Formularios para reclutar candidato y asignar analista a la vacante
    form_reclutados = ReclutadoCrearForm()
    form = VacancyAssingForm(cliente_id=cliente_id)
    form_reclutador = VacancyAssignRecruiterForm(cliente_id=cliente_id)
    analista_asignado = UsuarioBase.objects.filter(id=vacante.usuario_asignado_id).first()
    reclutador_asignado = UsuarioBase.objects.filter(id=vacante.asignacion_reclutador_id).first()

    context = {
        'data': data,
        'vacante': vacante,
        'reclutados': reclutados,
        'reclutados_recibido': reclutados_recibido,
        'reclutados_seleccionado': reclutados_seleccionado,
        'reclutados_finalizalista': reclutados_finalizalista,
        'reclutados_descartado': reclutados_descartado,
        'entrevistas': entrevistas,
        'form_reclutados' : form_reclutados,
        'preguntas': preguntas,
        'form': form,
        'form_reclutador': form_reclutador,
        'analista_asignado': analista_asignado,
        'reclutador_asignado': reclutador_asignado,
        'form_errors': form_errors,
    }
    return render(request, 'admin/vacancy/client_user/vacancy_management.html', context)


#detalle de la vacante
@login_required
@validar_permisos('acceso_admin', 'acceso_cliente', 'acceso_analista_seleccion_ats', 'acceso_analista_seleccion')
def detail_vacancy(request, pk):
    # Verificar si el cliente_id está en la sesión
    # cliente_id = request.session.get('cliente_id')
    vacante = get_object_or_404(
        Cli052Vacante.objects.select_related(
            "cargo",
            "perfil_vacante",
            "perfil_vacante__lugar_trabajo",
            "perfil_vacante__profesion_estudio",
            "perfil_vacante__grupo_profesion",
            "asignacion_cliente_id_064__id_cliente_asignado",
            "asignacion_cliente_id_064__id_cliente_asignado__ciudad_id_004",
            "usuario_asignado",
            "usuario_asignado__group",
            "asignacion_reclutador",
            "asignacion_reclutador__group",
        ).prefetch_related(
            "habilidades",
            "motivadores",
            "fit_cultural",
        ),
        id=pk,
    )
    cliente_id = vacante.asignacion_cliente_id_064.id_cliente_asignado.id
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

    # Función para extraer IDs de profesion_estudio_listado (JSON) para MultipleChoiceField
    def parse_profesion_listado_ids(listado_json):
        """Convierte JSON de profesiones a lista de IDs para el campo Select2 múltiple."""
        if not listado_json:
            return []
        try:
            data = json.loads(listado_json) if isinstance(listado_json, str) else listado_json
            if isinstance(data, list):
                return [str(item.get('id')) for item in data if isinstance(item, dict) and item.get('id')]
        except (json.JSONDecodeError, TypeError):
            pass
        return []

    # Construir initial data para el formulario
    initial = {
        'titulo': vacante.titulo,
        'cargo': vacante.cargo_id if vacante.cargo else None,
        'termino_contrato': perfil_vacante.termino_contrato if perfil_vacante else None,
        'modalidad': perfil_vacante.modalidad if perfil_vacante else None,
        'cantidad_presentar': vacante.cantidad_presentar,
        'numero_posiciones': vacante.numero_posiciones,
        'fecha_presentacion': vacante.fecha_presentacion_para_input_date(),
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
        'estado_estudio': perfil_vacante.estado_estudio if perfil_vacante else None,
        'cantidad_semestres': perfil_vacante.cantidad_semestres if perfil_vacante else None,
        'motivadores_candidato': [str(x) for x in vacante.motivadores.values_list('id', flat=True)] if vacante.motivadores.exists() else [],
        'comentarios': vacante.comentarios,
        'descripcion_vacante': vacante.descripcion_vacante,
        'tipo_profesion': perfil_vacante.tipo_profesion if perfil_vacante else None,
        'grupo_profesion': perfil_vacante.grupo_profesion_id if perfil_vacante and perfil_vacante.grupo_profesion else None,
        'profesion_estudio_listado': parse_profesion_listado_ids(perfil_vacante.profesion_estudio_listado) if perfil_vacante else [],
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

        # Referencias laborales solicitadas (según cargo al crear/editar)
        ref_sol = getattr(perfil_vacante, "referencias_laborales_solicitud", None)
        if ref_sol:
            for item in ref_sol:
                if isinstance(item, dict):
                    try:
                        o = int(item.get("orden", 0))
                    except (TypeError, ValueError):
                        continue
                    if 1 <= o <= 10:
                        initial[f"ref_laboral_{o}"] = (item.get("descripcion") or "").strip()

    # Requerimientos especiales (en vacante, no en perfil)
    if vacante.requerimientos_especiales:
        req_list = vacante.requerimientos_especiales
        if isinstance(req_list, list):
            for i, req in enumerate(req_list[:5], start=1):
                initial[f'requerimientos_especiales_{i}'] = str(req) if req else ''

    # Fit cultural
    initial['grupo_fit_1'] = list(vacante.fit_cultural.filter(id__in=FIT_GRUPO_1_IDS).values_list('id', flat=True))
    initial['grupo_fit_2'] = list(vacante.fit_cultural.filter(id__in=FIT_GRUPO_2_IDS).values_list('id', flat=True))
    initial['grupo_fit_3'] = list(vacante.fit_cultural.filter(id__in=FIT_GRUPO_3_IDS).values_list('id', flat=True))
    initial['grupo_fit_4'] = list(vacante.fit_cultural.filter(id__in=FIT_GRUPO_4_IDS).values_list('id', flat=True))
    initial['grupo_fit_5'] = list(vacante.fit_cultural.filter(id__in=FIT_GRUPO_5_IDS).values_list('id', flat=True))

    if request.method == 'POST':
        form = VacancyFormAllV2(
            request.POST, initial=initial, cliente_id=cliente_id, es_edicion=True
        )
        if form.is_valid():

            # Update existing data
            vacante.titulo = form.cleaned_data['titulo']
            vacante.cargo = Cli068Cargo.objects.get(id=form.cleaned_data['cargo'])
            vacante.numero_posiciones = form.cleaned_data['numero_posiciones']
            vacante.cantidad_presentar = form.cleaned_data['cantidad_presentar']
            # fecha_presentacion no se altera al editar (campo deshabilitado en el formulario)
            vacante.descripcion_vacante = form.cleaned_data['descripcion_vacante']
            vacante.comentarios = form.cleaned_data['comentarios']
            vacante.requerimientos_especiales = form.cleaned_data.get('requerimientos_especiales')
            # Actualizar motivadores múltiples
            motivadores_ids = form.cleaned_data.get('motivadores_candidato', [])
            if motivadores_ids:
                motivadores_objects = Cli078MotivadoresCandidato.objects.filter(id__in=motivadores_ids)
                vacante.motivadores.set(motivadores_objects)
            else:
                vacante.motivadores.clear()

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
            perfil_vacante.estado_estudio = form.cleaned_data['estado_estudio']
            perfil_vacante.cantidad_semestres = form.cleaned_data['cantidad_semestres']
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

            # Referencias laborales: sección removida del formulario (ya no se persiste aquí).

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
            
            # Fit Cultural (Los campos son ModelChoiceField, no ModelMultipleChoiceField)
            vacante.fit_cultural.clear()
            fit_cultural_objects = []
            
            # Agregar cada selección individual si existe
            if form.cleaned_data.get('grupo_fit_1'):
                fit_cultural_objects.append(form.cleaned_data['grupo_fit_1'])
            if form.cleaned_data.get('grupo_fit_2'):
                fit_cultural_objects.append(form.cleaned_data['grupo_fit_2'])
            if form.cleaned_data.get('grupo_fit_3'):
                fit_cultural_objects.append(form.cleaned_data['grupo_fit_3'])
            if form.cleaned_data.get('grupo_fit_4'):
                fit_cultural_objects.append(form.cleaned_data['grupo_fit_4'])
            if form.cleaned_data.get('grupo_fit_5'):
                fit_cultural_objects.append(form.cleaned_data['grupo_fit_5'])
            
            if fit_cultural_objects:
                vacante.fit_cultural.add(*fit_cultural_objects)
            
            messages.success(request, 'Vacante editada correctamente')
            return redirect('vacantes:vacantes_propias', pk=pk)
        else:
            error_messages = []
            for field, errors in form.errors.items():
                if field == '__all__':
                    for error in errors:
                        error_messages.append(str(error))
                else:
                    field_obj = form.fields.get(field)
                    field_label = field_obj.label if (field_obj and field_obj.label) else field.replace('_', ' ').title()
                    error_messages.append(f"{field_label}: {', '.join(str(e) for e in errors)}")
            msg = 'Por favor revise el formulario. ' + ' | '.join(error_messages) if error_messages else 'Por favor revise el formulario.'
            messages.error(request, msg)

    else:
        form = VacancyFormAllV2(initial=initial, cliente_id=cliente_id, es_edicion=True)

    cliente_asignado = None
    if vacante.asignacion_cliente_id_064:
        cliente_asignado = vacante.asignacion_cliente_id_064.id_cliente_asignado

    # Listado de candidatos (tabla en vacancy_detail.html) + secciones por estado de reclutamiento
    aplicaciones_tabla = (
        Cli056AplicacionVacante.objects.select_related(
            "candidato_101",
            "candidato_101__ciudad_id_004",
        )
        .filter(vacante_id_052=vacante)
        .order_by("estado_reclutamiento", "-fecha_actualizacion", "-id")
    )

    from applications.services.choices import ESTADO_RECLUTADO_CHOICES_STATIC, ESTADO_RECLUTADO_COLOR_STATIC

    apps_list = list(aplicaciones_tabla)
    attach_ultima_entrevista_a_reclutados(apps_list)
    by_estado_reclutamiento = defaultdict(list)
    for app in apps_list:
        by_estado_reclutamiento[app.estado_reclutamiento].append(app)

    choices_reclutamiento = {k: v for k, v in ESTADO_RECLUTADO_CHOICES_STATIC if k != ""}
    reclutamiento_secciones = []
    for code in (1, 2, 3, 4):
        label = choices_reclutamiento.get(code, "Desconocido")
        _nombre, color_key = ESTADO_RECLUTADO_COLOR_STATIC.get(code, (label, "secondary"))
        reclutamiento_secciones.append(
            {
                "code": code,
                "title": label,
                "color": color_key,
                "items": by_estado_reclutamiento.get(code, []),
            }
        )

    aplicaciones_todas = sorted(
        apps_list,
        key=lambda a: (a.fecha_aplicacion or timezone.now(), a.id),
        reverse=True,
    )

    # Panel lateral: Seleccionado (8) o Seleccionado por Cliente (13)
    aplicaciones_seleccion_cliente = sorted(
        [a for a in apps_list if a.estado_aplicacion in (8, 13)],
        key=lambda a: (a.fecha_actualizacion or a.fecha_aplicacion or timezone.now(), a.id),
        reverse=True,
    )

    # Métricas por estado de aplicación (misma lógica que listado de vacantes: en_proceso = 2,3,5,6)
    qs_metric = Cli056AplicacionVacante.objects.filter(vacante_id_052=vacante)
    vacante_metric_aplicados = qs_metric.filter(estado_aplicacion=1).count()
    vacante_metric_entrevista = qs_metric.filter(estado_aplicacion__in=[2, 3, 5, 6]).count()
    vacante_metric_no_aprobados = qs_metric.filter(estado_aplicacion__in=[4, 7, 12]).count()
    vacante_metric_seleccionados = qs_metric.filter(estado_aplicacion__in=[8, 13]).count()
    _tot_m = len(apps_list)

    def _pct_vac(n):
        return round(100.0 * n / _tot_m) if _tot_m else 0

    # Fecha del candidato N (N = cantidad_presentar): orden cronológico por fecha_actualizacion
    # entre aplicaciones en decisión del cliente (8, 12, 13). Si hay menos de N, se usa el último disponible.
    _qs_cliente = qs_metric.filter(estado_aplicacion__in=[8, 12, 13]).order_by(
        "fecha_actualizacion", "id"
    )
    _lista_cliente = list(_qs_cliente)
    _limite_presentar = vacante.cantidad_presentar
    if _limite_presentar is not None and _limite_presentar > 0 and _lista_cliente:
        _hasta = min(int(_limite_presentar), len(_lista_cliente))
        fecha_ultimo_candidato_enviado = _lista_cliente[_hasta - 1].fecha_actualizacion
    elif _lista_cliente:
        fecha_ultimo_candidato_enviado = _lista_cliente[-1].fecha_actualizacion
    else:
        fecha_ultimo_candidato_enviado = None

    # Candidatos con al menos una entrevista calificada (resultado registrado) y estado «Apto» (2)
    filtro_apto_entrevista_completa = (
        Q(asignaciones_entrevista__resultado_entrevista__isnull=False)
        & ~Q(asignaciones_entrevista__resultado_entrevista={})
        & Q(asignaciones_entrevista__estado_asignacion=2)
    )
    vacante_metric_aptos_entrevista_completa = (
        qs_metric.filter(filtro_apto_entrevista_completa).distinct().count()
    )
    # Presentados al cliente (8, 12, 13) con entrevista calificada y estado «Apto»
    vacante_metric_presentados_apto_entrevista = (
        qs_metric.filter(estado_aplicacion__in=[8, 12, 13])
        .filter(filtro_apto_entrevista_completa)
        .distinct()
        .count()
    )

    def _normalizar_dt_para_diff(dt):
        if dt is None:
            return None
        if timezone.is_naive(dt):
            return timezone.make_aware(dt, timezone.get_current_timezone())
        return dt

    diferencia_fechas_presentacion_envio = None
    fp = _normalizar_dt_para_diff(vacante.fecha_presentacion)
    ul = _normalizar_dt_para_diff(fecha_ultimo_candidato_enviado)
    if fp and ul:
        delta = ul - fp
        total_seconds = abs(int(delta.total_seconds()))
        dias = total_seconds // 86400
        horas = (total_seconds % 86400) // 3600
        minutos = (total_seconds % 3600) // 60
        partes = []
        if dias:
            partes.append(f"{dias} día{'s' if dias != 1 else ''}")
        if horas:
            partes.append(f"{horas} h")
        if not partes and minutos:
            partes.append(f"{minutos} min")
        if not partes:
            partes.append("0 min")
        texto_diff = " · ".join(partes)
        if delta.total_seconds() == 0:
            nota = "Ambas fechas coinciden."
        elif delta.total_seconds() > 0:
            nota = "El último envío al cliente es posterior a la fecha de presentación."
        else:
            nota = "El último envío al cliente es anterior a la fecha de presentación."
        diferencia_fechas_presentacion_envio = {"texto": texto_diff, "nota": nota}

    cargos_refs_map = {
        str(c.id): (c.referencias_laborales or 0)
        for c in Cli068Cargo.objects.filter(cliente_id=cliente_id)
    }

    context = {
        "vacante": vacante,
        "form": form,
        "cargos_refs_map": cargos_refs_map,
        "data": {"cliente": cliente_asignado},
        "is_candidato": False,
        "aplicaciones_tabla": aplicaciones_tabla,
        "aplicaciones_total": len(apps_list),
        "aplicaciones_todas": aplicaciones_todas,
        "aplicaciones_seleccion_cliente": aplicaciones_seleccion_cliente,
        "reclutamiento_secciones": reclutamiento_secciones,
        "vacante_metric_aplicados": vacante_metric_aplicados,
        "vacante_metric_entrevista": vacante_metric_entrevista,
        "vacante_metric_no_aprobados": vacante_metric_no_aprobados,
        "vacante_metric_seleccionados": vacante_metric_seleccionados,
        "vacante_metric_pct_aplicados": _pct_vac(vacante_metric_aplicados),
        "vacante_metric_pct_entrevista": _pct_vac(vacante_metric_entrevista),
        "vacante_metric_pct_no_aprobados": _pct_vac(vacante_metric_no_aprobados),
        "vacante_metric_pct_seleccionados": _pct_vac(vacante_metric_seleccionados),
        "fecha_ultimo_candidato_enviado": fecha_ultimo_candidato_enviado,
        "vacante_metric_aptos_entrevista_completa": vacante_metric_aptos_entrevista_completa,
        "vacante_metric_presentados_apto_entrevista": vacante_metric_presentados_apto_entrevista,
        "diferencia_fechas_presentacion_envio": diferencia_fechas_presentacion_envio,
    }

    return render(request, "admin/vacancy/client_user/vacancy_detail.html", context)


@login_required
@validar_permisos(
    "acceso_admin",
    "acceso_cliente",
    "acceso_analista_seleccion_ats",
    "acceso_analista_seleccion",
)
def vacancy_aplicacion_modal_cuerpo(request, vacante_pk, aplicacion_pk):
    """
    Fragmento HTML para el modal de candidato en detalle de vacante (pestañas:
    entrevista/resultado, perfil, historial de aplicación, respuesta del cliente).
    """
    aplicacion = get_object_or_404(
        Cli056AplicacionVacante.objects.select_related(
            "candidato_101",
            "candidato_101__ciudad_id_004",
            "vacante_id_052",
        ),
        pk=aplicacion_pk,
        vacante_id_052_id=vacante_pk,
    )
    entrevistas = (
        Cli057AsignacionEntrevista.objects.filter(asignacion_vacante=aplicacion)
        .select_related("usuario_asignado", "usuario_asigno")
        .order_by("-fecha_entrevista", "-hora_entrevista", "-id")
    )
    historial = consultar_historial_aplicacion_vacante_candidate(aplicacion.id)
    info_detalle_candidato = buscar_candidato(aplicacion.candidato_101_id)
    match_inicial_pct = get_match_inicial_porcentaje(aplicacion.json_match_inicial)
    if match_inicial_pct is None:
        match_inicial_display = "—"
    else:
        match_inicial_display = f"{match_inicial_pct}%"

    json_match_inicial = {}
    raw_jm = aplicacion.json_match_inicial
    if raw_jm:
        try:
            if isinstance(raw_jm, str):
                json_match_inicial = json.loads(raw_jm)
            else:
                json_match_inicial = raw_jm
        except (json.JSONDecodeError, TypeError):
            json_match_inicial = {}

    entrevistas_modal = []
    for e in entrevistas:
        entrevistas_modal.append(
            {
                "entrevista": e,
                "datos_reporte_final": estructurar_resultado_entrevista_json(
                    e.resultado_entrevista, json_match_inicial
                ),
            }
        )

    _rr = aplicacion.registro_reclutamiento
    if isinstance(_rr, dict):
        _txt_cliente = (_rr.get("descripcion_respuesta_cliente") or "").strip()
    else:
        _txt_cliente = ""
    estado_respuesta_cliente_relevante = aplicacion.estado_aplicacion in (8, 12, 13)
    es_respuesta_cliente_apto = aplicacion.estado_aplicacion in (8, 13)

    context = {
        "aplicacion": aplicacion,
        "reclutado": aplicacion,
        "candidato": aplicacion.candidato_101,
        "vacante": aplicacion.vacante_id_052,
        "entrevistas": entrevistas,
        "entrevistas_modal": entrevistas_modal,
        "historial": historial,
        "info_detalle_candidato": info_detalle_candidato,
        "match_inicial_pct": match_inicial_pct,
        "match_inicial_display": match_inicial_display,
        "respuesta_cliente_texto": _txt_cliente,
        "estado_respuesta_cliente_relevante": estado_respuesta_cliente_relevante,
        "es_respuesta_cliente_apto": es_respuesta_cliente_apto,
    }
    return render(
        request,
        "admin/vacancy/partials/modal_candidato_aplicacion_tabs.html",
        context,
    )


@login_required
@validar_permisos(
    "acceso_admin",
    "acceso_cliente",
    "acceso_analista_seleccion_ats",
    "acceso_analista_seleccion",
)
def vacancy_aplicacion_panel_reporte_final(request, vacante_pk, aplicacion_pk):
    """
    Fragmento HTML para el panel (vacancy_management2):
    muestra el resultado compacto del reporte final (última entrevista).
    """
    aplicacion = get_object_or_404(
        Cli056AplicacionVacante.objects.select_related("vacante_id_052"),
        pk=aplicacion_pk,
        vacante_id_052_id=vacante_pk,
    )

    entrevistas = (
        Cli057AsignacionEntrevista.objects.filter(asignacion_vacante=aplicacion)
        .order_by("-fecha_entrevista", "-hora_entrevista", "-id")
    )
    entrevista = entrevistas.first()

    json_match_inicial = {}
    raw_jm = aplicacion.json_match_inicial
    if raw_jm:
        try:
            if isinstance(raw_jm, str):
                json_match_inicial = json.loads(raw_jm)
            else:
                json_match_inicial = raw_jm
        except (json.JSONDecodeError, TypeError):
            json_match_inicial = {}

    datos_reporte_final = None
    if entrevista and entrevista.resultado_entrevista:
        datos_reporte_final = estructurar_resultado_entrevista_json(
            entrevista.resultado_entrevista, json_match_inicial
        )

    return render(
        request,
        "admin/vacancy/partials/panel_reporte_final_compacto.html",
        {"datos_reporte_final": datos_reporte_final},
    )


@login_required
@validar_permisos(
    "acceso_admin",
    "acceso_cliente",
    "acceso_analista_seleccion_ats",
    "acceso_analista_seleccion",
)
def vacancy_aplicacion_historial_filas(request, vacante_pk, aplicacion_pk):
    """
    Filas HTML del historial (cli_063) para una sola aplicación a vacante.
    Usado en vacancy_management2 al seleccionar candidato.
    """
    get_object_or_404(
        Cli056AplicacionVacante.objects.select_related("vacante_id_052"),
        pk=aplicacion_pk,
        vacante_id_052_id=vacante_pk,
    )
    historial = consultar_historial_aplicacion_vacante_candidate(aplicacion_pk)
    return render(
        request,
        "admin/vacancy/partials/vm2_historial_aplicacion_filas.html",
        {"historial": historial},
    )


@login_required
@validar_permisos(
    "acceso_admin",
    "acceso_cliente",
    "acceso_analista_seleccion_ats",
    "acceso_analista_seleccion",
)
def vacancy_aplicacion_vm2_info_candidato(request, vacante_pk, aplicacion_pk):
    """HTML para el modal «Información del candidato» en vacancy_management2."""
    aplicacion = get_object_or_404(
        Cli056AplicacionVacante.objects.select_related(
            "candidato_101",
            "candidato_101__ciudad_id_004",
        ),
        pk=aplicacion_pk,
        vacante_id_052_id=vacante_pk,
    )
    candidato = aplicacion.candidato_101
    info_detalle_candidato = buscar_candidato(candidato.id)
    idiomas_vm2 = _vm2_idiomas_candidato(candidato)
    return render(
        request,
        "admin/vacancy/partials/vm2_modal_info_candidato.html",
        {
            "aplicacion": aplicacion,
            "candidato": candidato,
            "info_detalle_candidato": info_detalle_candidato,
            "idiomas_vm2": idiomas_vm2,
        },
    )


@login_required
@require_POST
@validar_permisos(
    "acceso_admin",
    "acceso_cliente",
    "acceso_analista_seleccion_ats",
    "acceso_analista_seleccion",
)
def vacancy_aplicacion_vm2_gestion_accion(request, vacante_pk, aplicacion_pk):
    """
    Desde gestión de vacante (vm2): pasar a viaje de contratación (estado 13)
    o registrar decisiones definitivas (estado 5 + filas cli_087).
    Requiere aplicación en estado 3 (Entrevista aprobada).
    """
    try:
        body = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)

    accion = (body.get("accion") or "").strip()
    descripcion_respuesta_cliente = (body.get("descripcion_respuesta_cliente") or "").strip()
    aplicacion = get_object_or_404(
        Cli056AplicacionVacante.objects.select_related(
            "vacante_id_052",
            "vacante_id_052__asignacion_cliente_id_064",
        ),
        pk=aplicacion_pk,
        vacante_id_052_id=vacante_pk,
    )
    vacante = aplicacion.vacante_id_052
    if not _vm2_vacante_ok_for_cliente_session(request, vacante):
        return JsonResponse({"ok": False, "error": "No autorizado."}, status=403)

    if aplicacion.estado_aplicacion != 3:
        return JsonResponse(
            {
                "ok": False,
                "error": "La aplicación debe estar en estado Entrevista aprobada para esta acción.",
            },
            status=400,
        )

    uid = request.session.get("_auth_user_id") or getattr(request.user, "id", None)
    if not uid:
        return JsonResponse({"ok": False, "error": "Usuario no identificado."}, status=403)
    usuario = get_object_or_404(UsuarioBase, pk=uid)

    if not descripcion_respuesta_cliente:
        return JsonResponse(
            {
                "ok": False,
                "error": "La descripción / respuesta del cliente es obligatoria.",
            },
            status=400,
        )

    estado_activo = Cat001Estado.objects.filter(nombre__iexact="Activo").first()
    if not estado_activo:
        estado_activo = Cat001Estado.objects.filter(pk=1).first()
    if not estado_activo:
        return JsonResponse({"ok": False, "error": "No hay estado catálogo Activo."}, status=500)

    if accion == "ir_contratacion":
        with transaction.atomic():
            rr = aplicacion.registro_reclutamiento or {}
            if not isinstance(rr, dict):
                rr = {}
            rr["descripcion_respuesta_cliente"] = descripcion_respuesta_cliente
            aplicacion.registro_reclutamiento = rr
            aplicacion.save(update_fields=["registro_reclutamiento"])
            crear_historial_aplicacion(
                aplicacion,
                13,
                uid,
                "Pase a viaje de contratación (en espera por respuesta de contratación). "
                f"Respuesta cliente: {descripcion_respuesta_cliente}",
            )
        messages.success(request, "Candidato enviado a viaje de contratación.")
        return JsonResponse(
            {
                "ok": True,
                "estado_aplicacion": 13,
                "message": "Candidato enviado a viaje de contratación.",
            }
        )

    if accion == "marcar_no_apto":
        with transaction.atomic():
            rr = aplicacion.registro_reclutamiento or {}
            if not isinstance(rr, dict):
                rr = {}
            rr["descripcion_respuesta_cliente"] = descripcion_respuesta_cliente
            aplicacion.registro_reclutamiento = rr
            aplicacion.save(update_fields=["registro_reclutamiento"])
            crear_historial_aplicacion(
                aplicacion,
                12,
                uid,
                f"No Apto. Respuesta cliente: {descripcion_respuesta_cliente}",
            )
        messages.success(request, "Candidato marcado como No Apto.")
        return JsonResponse(
            {
                "ok": True,
                "estado_aplicacion": 12,
                "message": "Candidato marcado como No Apto.",
            }
        )

    if accion == "registrar_decisiones":
        cargo = vacante.cargo
        if not cargo:
            return JsonResponse(
                {"ok": False, "error": "La vacante no tiene cargo asociado."},
                status=400,
            )

        ids_cargo = set(
            Cli086AsignacionCargoAccionesDecisivas.objects.filter(cargo=cargo).values_list(
                "accion_decisiva_id", flat=True
            )
        )
        if not ids_cargo:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "No hay acciones decisivas configuradas para el cargo.",
                },
                status=400,
            )

        reportes_in = {}
        for r in body.get("reportes") or []:
            aid = r.get("accion_decisiva_id")
            if aid is None:
                continue
            try:
                aid = int(aid)
            except (TypeError, ValueError):
                continue
            if aid not in ids_cargo:
                return JsonResponse(
                    {"ok": False, "error": "Acción decisiva no asignada al cargo."},
                    status=400,
                )
            reportes_in[aid] = r.get("respuestas") if isinstance(r.get("respuestas"), dict) else {}

        if not reportes_in:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "Seleccione al menos una acción decisiva para registrar.",
                },
                status=400,
            )

        acciones_map = Cli085AccionesDecisivas.objects.in_bulk(reportes_in.keys())
        if len(acciones_map) != len(reportes_in):
            return JsonResponse(
                {"ok": False, "error": "Una o más acciones decisivas no existen."},
                status=400,
            )

        with transaction.atomic():
            rr = aplicacion.registro_reclutamiento or {}
            if not isinstance(rr, dict):
                rr = {}
            rr["descripcion_respuesta_cliente"] = descripcion_respuesta_cliente
            aplicacion.registro_reclutamiento = rr
            aplicacion.save(update_fields=["registro_reclutamiento"])

            # 1) Crear filas cli_087 por acción seleccionada
            for aid, resp in reportes_in.items():
                Cli087ReporteAccionDecisivaReclutado.objects.create(
                    aplicacion_vacante_056=aplicacion,
                    accion_decisiva_id=aid,
                    usuario_cargado=usuario,
                    usuario_actualizado=usuario,
                    estado=estado_activo,
                    json_data=resp,
                )

            # 2) Un solo cambio de estado 3 → 5 en historial (y en la aplicación)
            crear_historial_aplicacion(
                aplicacion,
                5,
                uid,
                "Registro de decisiones definitivas. "
                f"Respuesta cliente: {descripcion_respuesta_cliente}",
            )

            # 3) Entradas adicionales de historial, una por acción, conservando estado 5
            #    (sin volver a forzar “Cambio de estado ... a ...” por cada acción).
            for aid in sorted(reportes_in.keys()):
                acc = acciones_map.get(aid)
                nombre_acc = (getattr(acc, "nombre", "") or "").strip() or f"ID {aid}"
                Cli063AplicacionVacanteHistorial.objects.create(
                    aplicacion_vacante_056=aplicacion,
                    usuario_id_genero=usuario,
                    estado=5,
                    descripcion=f"Acción decisiva asignada: {nombre_acc}",
                )

        messages.success(request, "Decisiones definitivas registradas correctamente.")
        return JsonResponse(
            {
                "ok": True,
                "estado_aplicacion": 5,
                "message": "Decisiones definitivas registradas correctamente.",
            }
        )

    return JsonResponse({"ok": False, "error": "Acción no válida."}, status=400)


@login_required
@require_POST
@validar_permisos(
    "acceso_admin",
    "acceso_cliente",
    "acceso_analista_seleccion_ats",
    "acceso_analista_seleccion",
)
def vacancy_aplicacion_vm2_gestion_estado_13(request, vacante_pk, aplicacion_pk):
    """
    Desde gestión de vacante (vm2): cierre de estado 13 (En espera por respuesta de contratación)
    hacia 15 (Contratado) o 14 (No contratado), registrando observación en historial.
    """
    try:
        body = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)

    decision = (body.get("decision") or "").strip().lower()
    observacion = (body.get("observacion") or "").strip()

    if decision not in ("contratado", "no_contratado"):
        return JsonResponse({"ok": False, "error": "Decisión inválida."}, status=400)
    if not observacion:
        return JsonResponse({"ok": False, "error": "La observación es obligatoria."}, status=400)

    aplicacion = get_object_or_404(
        Cli056AplicacionVacante.objects.select_related(
            "vacante_id_052",
            "vacante_id_052__asignacion_cliente_id_064",
        ),
        pk=aplicacion_pk,
        vacante_id_052_id=vacante_pk,
    )
    vacante = aplicacion.vacante_id_052
    if not _vm2_vacante_ok_for_cliente_session(request, vacante):
        return JsonResponse({"ok": False, "error": "No autorizado."}, status=403)

    if aplicacion.estado_aplicacion != 13:
        return JsonResponse(
            {"ok": False, "error": "La aplicación debe estar en estado 13 para gestionar esta acción."},
            status=400,
        )

    uid = request.session.get("_auth_user_id") or getattr(request.user, "id", None)
    if not uid:
        return JsonResponse({"ok": False, "error": "Usuario no identificado."}, status=403)

    nuevo_estado = 15 if decision == "contratado" else 14
    titulo = "Contratado" if nuevo_estado == 15 else "No contratado"
    with transaction.atomic():
        # Bloquear la vacante para evitar carreras al completar cupos.
        vacante = (
            Cli052Vacante.objects.select_for_update()
            .only("id", "numero_posiciones", "estado_vacante", "fecha_cierre")
            .get(pk=vacante.pk)
        )
        crear_historial_aplicacion(
            aplicacion,
            nuevo_estado,
            uid,
            f"{titulo}. Observación: {observacion}",
        )

        # Si fue contratado, verificar si ya se completó el número de posiciones.
        if nuevo_estado == 15:
            contratados = Cli056AplicacionVacante.objects.filter(
                vacante_id_052_id=vacante.id,
                estado_aplicacion=15,
            ).count()
            if vacante.numero_posiciones and contratados >= int(vacante.numero_posiciones):
                # 3 = Finalizada (según ESTADO_VACANTE_CHOICHES_STATIC)
                if vacante.estado_vacante != 3:
                    vacante.estado_vacante = 3
                if not vacante.fecha_cierre:
                    vacante.fecha_cierre = timezone.now()
                vacante.save(update_fields=["estado_vacante", "fecha_cierre"])

    return JsonResponse(
        {
            "ok": True,
            "estado_aplicacion": nuevo_estado,
            "message": f"Estado actualizado a {titulo}.",
        }
    )


def _vm2_is_schema_field_dict(d):
    """Nodo hoja: metadatos de campo (type, label, …) definidos en Cli085.json_data."""
    if not isinstance(d, dict) or not d:
        return False
    return "type" in d and "label" in d


def _vm2_schema_default_val(schema):
    t = str(schema.get("type") or "string").lower()
    if t == "boolean":
        return False
    if t == "number":
        return None
    if t == "file":
        return ""
    return ""


def _vm2_nombre_usuario_cli087(u):
    if not u:
        return ""
    parts = [
        getattr(u, "primer_nombre", None) or "",
        getattr(u, "segundo_nombre", None) or "",
        getattr(u, "primer_apellido", None) or "",
        getattr(u, "segundo_apellido", None) or "",
    ]
    s = " ".join(p for p in parts if p).strip()
    return s or (getattr(u, "username", None) or "").strip() or str(getattr(u, "pk", "") or "")


def _vm2_merge_json_valores_sobre_plantilla(plantilla, valores):
    """Superpone valores guardados (Cli087) sobre la plantilla (Cli085.json_data)."""
    if plantilla is None:
        return valores
    if isinstance(plantilla, dict) and _vm2_is_schema_field_dict(plantilla):
        if valores is None:
            return _vm2_schema_default_val(plantilla)
        if isinstance(valores, str) and valores.strip().startswith("{"):
            try:
                parsed = json.loads(valores)
                if isinstance(parsed, dict) and _vm2_is_schema_field_dict(parsed):
                    return _vm2_schema_default_val(plantilla)
            except json.JSONDecodeError:
                pass
        if isinstance(valores, dict) and _vm2_is_schema_field_dict(valores):
            # No usar una copia de la plantilla como valor (provoca "[object Object]" / JSON vacío en UI).
            if "value" in valores:
                inner = valores.get("value")
                return copy.deepcopy(inner) if inner is not None else _vm2_schema_default_val(plantilla)
            return _vm2_schema_default_val(plantilla)
        return valores
    if isinstance(plantilla, dict):
        if not isinstance(valores, dict):
            return copy.deepcopy(plantilla)
        out = {}
        for k, pv in plantilla.items():
            if k in valores:
                out[k] = _vm2_merge_json_valores_sobre_plantilla(pv, valores[k])
            else:
                out[k] = copy.deepcopy(pv)
        return out
    if isinstance(plantilla, list) and plantilla:
        item_tpl = plantilla[0]
        if not valores or not isinstance(valores, list):
            return copy.deepcopy(plantilla)
        res = []
        for item in valores:
            if isinstance(item_tpl, dict) and isinstance(item, dict):
                res.append(_vm2_merge_json_valores_sobre_plantilla(item_tpl, item))
            else:
                res.append(item)
        return res if res else copy.deepcopy(plantilla)
    return valores if valores is not None else plantilla


def _vm2_normalizar_json_respuesta_plantilla(plantilla, posted):
    """Alinea el JSON enviado a la forma de la plantilla (solo claves definidas en Cli085)."""
    if plantilla is None:
        return posted
    if isinstance(plantilla, dict) and _vm2_is_schema_field_dict(plantilla):
        return posted
    if isinstance(plantilla, dict):
        if not isinstance(posted, dict):
            return copy.deepcopy(plantilla)
        out = {}
        for k, tv in plantilla.items():
            if k in posted:
                out[k] = _vm2_normalizar_json_respuesta_plantilla(tv, posted[k])
            else:
                out[k] = copy.deepcopy(tv)
        return out
    if isinstance(plantilla, list) and plantilla:
        item_tpl = plantilla[0]
        if not isinstance(posted, list):
            return copy.deepcopy(plantilla)
        out = []
        for p in posted:
            if isinstance(item_tpl, dict) and isinstance(p, dict):
                out.append(_vm2_normalizar_json_respuesta_plantilla(item_tpl, p))
        return out if out else copy.deepcopy(plantilla)
    return posted


@login_required
@require_http_methods(["GET", "POST"])
@validar_permisos(
    "acceso_admin",
    "acceso_cliente",
    "acceso_analista_seleccion_ats",
    "acceso_analista_seleccion",
)
def vacancy_aplicacion_vm2_cli087(request, vacante_pk, aplicacion_pk, cli087_pk):
    """
    GET: plantilla json_data (Cli085) + valores fusionados (Cli087).
    POST: guarda respuestas anidadas en Cli087.json_data según la forma de la plantilla.
    """
    aplicacion = get_object_or_404(
        Cli056AplicacionVacante.objects.select_related("vacante_id_052__asignacion_cliente_id_064"),
        pk=aplicacion_pk,
        vacante_id_052_id=vacante_pk,
    )
    vacante = aplicacion.vacante_id_052
    if not _vm2_vacante_ok_for_cliente_session(request, vacante):
        return JsonResponse({"ok": False, "error": "No autorizado."}, status=403)

    try:
        cli087 = get_object_or_404(
            Cli087ReporteAccionDecisivaReclutado.objects.select_related(
                "accion_decisiva",
                "usuario_cargado",
                "usuario_actualizado",
            ),
            pk=cli087_pk,
            aplicacion_vacante_056_id=aplicacion_pk,
        )
    except DatabaseError:
        return JsonResponse(
            {
                "ok": False,
                "error": (
                    "No se pudo cargar el reporte: revise que la base de datos tenga las columnas del modelo "
                    "Cli087 (migraciones de la app reclutado, p. ej. fecha_actualizacion / usuario_actualizado)."
                ),
            },
            status=500,
        )

    acc = cli087.accion_decisiva
    plantilla = acc.json_data

    if request.method == "GET":
        guardado = cli087.json_data
        if not isinstance(guardado, dict) and not isinstance(guardado, list):
            guardado = {}
        merged = _vm2_merge_json_valores_sobre_plantilla(plantilla, guardado)
        fech_txt = ""
        if cli087.fecha_cargado:
            fech_txt = timezone.localtime(cli087.fecha_cargado).strftime("%d/%m/%Y %H:%M")
        fech_act_txt = ""
        fa = getattr(cli087, "fecha_actualizacion", None)
        if fa:
            fech_act_txt = timezone.localtime(fa).strftime("%d/%m/%Y %H:%M")
        elif cli087.fecha_cargado:
            fech_act_txt = fech_txt
        archivo_url = ""
        archivo_nom = ""
        try:
            if cli087.archivo_reporte:
                archivo_url = cli087.archivo_reporte.url
                archivo_nom = basename(cli087.archivo_reporte.name) or ""
        except (ValueError, AttributeError):
            pass
        # Para estado 5: el dictamen es obligatorio y final: aprobada | no_aprobada.
        # Se deja "pendiente" solo como estado informativo, no seleccionable.
        choices_ad = [
            {"value": k, "label": str(v)}
            for k, v in Cli087ReporteAccionDecisivaReclutado.ACCION_DECISIVA_ESTADO_CHOICES
            if k in ("aprobada", "no_aprobada")
        ]
        cod_ad = (getattr(cli087, "estado_accion_decisiva", None) or "pendiente").strip()
        if cod_ad not in {"aprobada", "pendiente", "no_aprobada"}:
            cod_ad = "pendiente"
        return JsonResponse(
            {
                "ok": True,
                "cli087_id": cli087.id,
                "accion_id": acc.id,
                "accion_nombre": acc.nombre or "",
                "plantilla": plantilla,
                "valores": merged,
                "tiene_plantilla": plantilla is not None,
                "archivo_reporte_url": archivo_url,
                "archivo_reporte_name": archivo_nom,
                "fecha_cargado": fech_txt,
                "fecha_actualizacion": fech_act_txt,
                "usuario_cargado_nombre": _vm2_nombre_usuario_cli087(cli087.usuario_cargado),
                "usuario_actualizado_nombre": _vm2_nombre_usuario_cli087(
                    getattr(cli087, "usuario_actualizado", None) or cli087.usuario_cargado
                ),
                "estado_accion_decisiva": cod_ad,
                "estado_accion_decisiva_label": cli087.get_estado_accion_decisiva_display(),
                "estado_accion_decisiva_choices": choices_ad,
            }
        )

    respuestas = None
    estado_ad = ""

    content_type = (request.content_type or "").lower()
    if "multipart/form-data" in content_type:
        raw_resp = request.POST.get("respuestas") or ""
        try:
            respuestas = json.loads(raw_resp) if raw_resp.strip() else None
        except json.JSONDecodeError:
            return JsonResponse({"ok": False, "error": "Campo respuestas no es JSON válido."}, status=400)
        estado_ad = (request.POST.get("estado_accion_decisiva") or "").strip()
        archivo = request.FILES.get("archivo_reporte")
    else:
        try:
            body = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)
        respuestas = body.get("respuestas")
        estado_ad = (body.get("estado_accion_decisiva") or "").strip()
        archivo = None

    # Solo lectura / evitar doble registro: una vez decidida (aprobada/no_aprobada) no se permite editar.
    estado_actual_ad = (getattr(cli087, "estado_accion_decisiva", None) or "pendiente").strip().lower()
    if estado_actual_ad in ("aprobada", "no_aprobada"):
        return JsonResponse(
            {
                "ok": False,
                "error": "Esta acción decisiva ya fue gestionada y está en modo solo lectura.",
            },
            status=400,
        )

    # Dictamen obligatorio: aprobada | no_aprobada (no se admite 'pendiente' al guardar).
    estado_ad = (estado_ad or "").strip().lower()
    if estado_ad not in ("aprobada", "no_aprobada"):
        return JsonResponse(
            {"ok": False, "error": "El estado de la acción decisiva es obligatorio (aprobada / no_aprobada)."},
            status=400,
        )

    # respuestas (json_data) es opcional en este flujo; si no viene, se conserva lo existente.
    if respuestas is None:
        respuestas = cli087.json_data if isinstance(cli087.json_data, (dict, list)) else {}
    if not isinstance(respuestas, (dict, list)):
        respuestas = {}

    normalizado = _vm2_normalizar_json_respuesta_plantilla(plantilla, respuestas)
    uid = request.session.get("_auth_user_id") or getattr(request.user, "id", None)
    usuario = get_object_or_404(UsuarioBase, pk=uid)

    cli087.json_data = normalizado
    update_fields = ["json_data"]
    cli087.estado_accion_decisiva = estado_ad
    update_fields.append("estado_accion_decisiva")
    if archivo:
        cli087.archivo_reporte = archivo
        update_fields.append("archivo_reporte")
    cli087.usuario_actualizado = usuario
    update_fields.append("usuario_actualizado")
    update_fields.append("fecha_actualizacion")
    try:
        with transaction.atomic():
            cli087.save(update_fields=update_fields)

            # 1) Historial por acción (estado 3) con el resultado.
            acc_nombre = (getattr(acc, "nombre", None) or "").strip() or f"ID {getattr(acc, 'pk', '') or ''}"
            etiqueta = "Aprobada" if estado_ad == "aprobada" else "No aprobada"
            Cli063AplicacionVacanteHistorial.objects.create(
                aplicacion_vacante_056=aplicacion,
                usuario_id_genero=usuario,
                estado=3,
                descripcion=f"Acción decisiva: {acc_nombre}. Resultado: {etiqueta}.",
            )

            # 2) Reglas de actualización del estado de la aplicación (transiciones 6→13 o 7→12).
            #    Solo aplican cuando la aplicación está en estado 5 (Acciones decisivas programadas).
            if aplicacion.estado_aplicacion == 5:
                if estado_ad == "no_aprobada":
                    crear_historial_aplicacion(
                        aplicacion,
                        7,
                        uid,
                        f"Acciones decisivas no aprobadas. Acción no aprobada: {acc_nombre}.",
                    )
                    crear_historial_aplicacion(
                        aplicacion,
                        12,
                        uid,
                        "No Apto por acciones decisivas no aprobadas.",
                    )
                else:
                    # Si todas las acciones decisivas de la aplicación están aprobadas → 6 y luego 13.
                    total = Cli087ReporteAccionDecisivaReclutado.objects.filter(
                        aplicacion_vacante_056_id=aplicacion_pk
                    ).count()
                    aprobadas = Cli087ReporteAccionDecisivaReclutado.objects.filter(
                        aplicacion_vacante_056_id=aplicacion_pk,
                        estado_accion_decisiva="aprobada",
                    ).count()
                    if total > 0 and aprobadas == total:
                        crear_historial_aplicacion(
                            aplicacion,
                            6,
                            uid,
                            "Acciones decisivas aprobadas (todas las acciones quedaron aprobadas).",
                        )
                        crear_historial_aplicacion(
                            aplicacion,
                            13,
                            uid,
                            "En espera por respuesta de contratación (post aprobación de acciones decisivas).",
                        )
    except DatabaseError:
        return JsonResponse(
            {
                "ok": False,
                "error": (
                    "No se pudo guardar el reporte. Aplique las migraciones pendientes de la app reclutado "
                    "sobre cli_087_reporte_accion_decisiva_reclutado."
                ),
            },
            status=500,
        )

    return JsonResponse(
        {
            "ok": True,
            "message": "Datos guardados correctamente.",
            "valores": normalizado,
            "estado_accion_decisiva": cli087.estado_accion_decisiva,
            "estado_accion_decisiva_label": cli087.get_estado_accion_decisiva_display(),
            "archivo_reporte_url": (cli087.archivo_reporte.url if cli087.archivo_reporte else ""),
            "archivo_reporte_name": (basename(cli087.archivo_reporte.name) if cli087.archivo_reporte else ""),
            "fecha_actualizacion": timezone.localtime(cli087.fecha_actualizacion).strftime(
                "%d/%m/%Y %H:%M"
            )
            if getattr(cli087, "fecha_actualizacion", None)
            else "",
            "usuario_actualizado_nombre": _vm2_nombre_usuario_cli087(cli087.usuario_actualizado),
            "estado_aplicacion": aplicacion.estado_aplicacion,
        }
    )


#detalle de la vacante
@login_required
@validar_permisos('acceso_admin', 'acceso_cliente', 'acceso_analista_seleccion_ats')
def detail_vacancy_interview(request, pk):
    # Verificar si el cliente_id está en la sesión
    cliente_id = request.session.get('cliente_id')
    
    # Obtener información de la vacante
    vacante = query_vacanty_detail().get(id=pk)

    # Obtener información de las entrevistas por vacante
    entrevistas = query_interview_all()
    entrevistas = entrevistas.filter(asignacion_vacante__vacante_id_052=pk)
    

    context ={
        'vacante': vacante,
        'entrevistas': entrevistas,
    }

    return render(request, 'admin/vacancy/client_user/vacancy_detail_interview.html', context)

#detalle de la vacante
@login_required
@validar_permisos('acceso_admin', 'acceso_cliente')
def detail_vacancy_assign(request, pk):
    # Verificar si el cliente_id está en la sesión
    cliente_id = request.session.get('cliente_id')
    
    # Obtener información de la vacante
    vacante = query_vacanty_detail().get(id=pk)
    print(vacante.usuario_asignado_id)
    analista_asignado = UsuarioBase.objects.filter(id=vacante.usuario_asignado_id).first()

    form = VacancyAssingForm(cliente_id=cliente_id)

    if request.method == 'POST':
        form = VacancyAssingForm(request.POST, cliente_id=cliente_id)
        if form.is_valid():
            analista_asignado = form.cleaned_data['analista_asignado']

            vacante.usuario_asignado = get_object_or_404(UsuarioBase, id=analista_asignado)
            vacante.save()
            
            messages.success(request, 'Analista asignado correctamente')
            return redirect('vacantes:vacantes_asignar_analista_cliente', pk=pk)
        else:
            print(form.errors)
    else:
        form = VacancyAssingForm(cliente_id=cliente_id)

    context ={
        'vacante': vacante,
        'form': form,
        'analista_asignado': analista_asignado,
    }

    return render(request, 'admin/vacancy/client_user/vacancy_detail_assign.html', context)

#@login_required
#@validar_permisos('acceso_cliente')
def vacancy_client_assigned(request):
    # Verificar si el cliente_id está en la sesión
    cliente_id = request.session.get('cliente_id')
    
    vacantes = query_vacanty_all()
    vacantes = vacantes.filter(
        asignacion_cliente_id_064__id_cliente_maestro=cliente_id,
        asignacion_cliente_id_064__tipo_asignacion='2'
    )

    context ={
        'vacantes': vacantes,
    }

    return render(request, 'admin/vacancy/client_user/headhunter/vacancy_client_assigned.html', context)


def _json_match_inicial_dict(aplicacion):
    raw = aplicacion.json_match_inicial
    if not raw:
        return {}
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {}


def _vm2_idiomas_candidato(candidato):
    """Lista de dicts {nombre, nivel_label, line} desde el JSON de idiomas del candidato."""
    from applications.services.choices import NIVEL_IDIOMA_CHOICES_STATIC

    niv_map = dict(NIVEL_IDIOMA_CHOICES_STATIC)
    raw = getattr(candidato, "idiomas", None)
    if not raw:
        return []
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return []
    if not isinstance(raw, list):
        return []
    out = []
    for it in raw:
        if not isinstance(it, dict):
            continue
        nombre = (it.get("nombre") or "").strip() or "—"
        ncode = it.get("nivel")
        if ncode in (None, ""):
            nlabel = "—"
        else:
            nlabel = niv_map.get(ncode)
            if nlabel is None:
                nlabel = str(ncode)
        line = f"{nombre} — {nlabel}"
        out.append({"nombre": nombre, "nivel_label": nlabel, "line": line})
    return out


def _vm2_cli087_por_aplicacion_map(reclutados):
    """
    Filas Cli087ReporteAccionDecisivaReclutado por id de aplicación, para el panel VM2 (estado 5).
    """
    ids = [a.id for a in reclutados]
    if not ids:
        return {}
    out = defaultdict(list)
    qs = (
        Cli087ReporteAccionDecisivaReclutado.objects.filter(aplicacion_vacante_056_id__in=ids)
        .select_related("accion_decisiva", "estado")
        .order_by("aplicacion_vacante_056_id", "fecha_cargado", "id")
    )
    _labels_estado_ad = dict(Cli087ReporteAccionDecisivaReclutado.ACCION_DECISIVA_ESTADO_CHOICES)

    for r in qs:
        aid = str(r.aplicacion_vacante_056_id)
        estado_nom = ""
        if r.estado_id:
            estado_nom = (getattr(r.estado, "nombre", None) or "").strip()
        es_pendiente = estado_nom.lower() == "activo"
        cod_ad = getattr(r, "estado_accion_decisiva", None) or "pendiente"
        if cod_ad not in _labels_estado_ad:
            cod_ad = "pendiente"
        out[aid].append(
            {
                "id": r.id,
                "accion_nombre": (getattr(r.accion_decisiva, "nombre", None) or "").strip(),
                "estado_nombre": estado_nom,
                "es_pendiente": es_pendiente,
                "estado_accion_decisiva": cod_ad,
                "estado_accion_decisiva_label": _labels_estado_ad.get(cod_ad, cod_ad),
            }
        )
    return dict(out)


def _enrich_reclutados_reporte_final_listado(aplicaciones):
    """
    Añade vm2_reporte_final_promedio (0..10 o None) y vm2_reporte_final_pct (0..100 o None)
    por aplicación, usando la última entrevista con resultado (misma lógica que el panel).
    """
    for aplicacion in aplicaciones:
        ent = None
        for e in aplicacion.asignaciones_entrevista.all()[:1]:
            ent = e
            break
        prom = None
        pct = None
        if ent and ent.resultado_entrevista:
            datos = estructurar_resultado_entrevista_json(
                ent.resultado_entrevista, _json_match_inicial_dict(aplicacion)
            )
            if datos and datos.get("promedio_total") is not None:
                try:
                    prom = float(datos["promedio_total"])
                    pct = max(0, min(100, round(prom * 10)))
                except (TypeError, ValueError):
                    prom = None
                    pct = None
        aplicacion.vm2_reporte_final_promedio = prom
        aplicacion.vm2_reporte_final_pct = pct


# gestionar la vacante2
@login_required
@validar_permisos('acceso_cliente')
def vacancy_management_from_client_2(request, pk, vacante_id):
    data = query_client_detail(pk)
    vacante = get_object_or_404(
        Cli052Vacante.objects.select_related(
            "cargo",
            "perfil_vacante",
            "perfil_vacante__lugar_trabajo",
            "perfil_vacante__profesion_estudio",
            "perfil_vacante__grupo_profesion",
            "asignacion_cliente_id_064__id_cliente_asignado",
        ).prefetch_related("habilidades"),
        id=vacante_id,
    )

    ultimo_estudio_graduado = (
        Can103Educacion.objects.filter(
            candidato_id_101=OuterRef("candidato_101_id"),
            estado_id_001=1,
            estado_estudios="G",
        )
        .order_by("-fecha_final", "-id")
    )

    prefetch_entrevistas = Prefetch(
        "asignaciones_entrevista",
        queryset=Cli057AsignacionEntrevista.objects.order_by(
            "-fecha_entrevista", "-hora_entrevista", "-id"
        ),
    )

    reclutados_qs = (
        query_recruited_vacancy_id(vacante.id)
        .filter(estado_aplicacion__in=[3, 5, 6, 7, 12, 13, 14, 15])
        .select_related("candidato_101__ciudad_id_004")
        .prefetch_related(prefetch_entrevistas)
        .annotate(
            ultimo_titulo_graduado=Subquery(ultimo_estudio_graduado.values("titulo")[:1]),
            ultima_carrera_graduada=Subquery(ultimo_estudio_graduado.values("carrera")[:1]),
            ultima_profesion_graduada=Subquery(
                ultimo_estudio_graduado.values("profesion_estudio__nombre")[:1]
            ),
        )
    )

    reclutados = list(reclutados_qs)
    _enrich_reclutados_reporte_final_listado(reclutados)

    # Tarjetas resumen: feedback (3), decisivas (5), aprob./seguimiento (6,13), no aprobados (7,12,14), contratados (15)
    vm2_por_feedback = [a for a in reclutados if a.estado_aplicacion == 3]
    vm2_decisiones_decisivas = [a for a in reclutados if a.estado_aplicacion == 5]
    orden_seguimiento = {6: 0, 13: 1}
    vm2_tras_decision = sorted(
        [a for a in reclutados if a.estado_aplicacion in (6, 13)],
        key=lambda x: (orden_seguimiento.get(x.estado_aplicacion, 99), (x.candidato_nombre or "").strip().lower()),
    )
    vm2_no_aprobados = sorted(
        [a for a in reclutados if a.estado_aplicacion in (7, 12, 14)],
        key=lambda x: (x.estado_aplicacion, (x.candidato_nombre or "").strip().lower()),
    )
    vm2_contratados = [a for a in reclutados if a.estado_aplicacion == 15]

    vm2_candidato_perfil_video = {}
    for a in reclutados:
        cand = a.candidato_101
        vid_url = ""
        if cand.video_perfil:
            vid_url = cand.video_perfil.url
        idiomas_rows = _vm2_idiomas_candidato(cand)
        vm2_candidato_perfil_video[str(a.id)] = {
            "video_url": vid_url,
            "perfil": (cand.perfil or "").strip(),
            "idiomas_display": [row["line"] for row in idiomas_rows],
        }

    vm2_acciones_cargo_decisivas = acciones_decisivas_asignadas_cargo_activas(vacante.cargo)

    vm2_cli087_por_aplicacion = _vm2_cli087_por_aplicacion_map(reclutados)

    context = {
        'data': data,
        'vacante': vacante,
        'reclutados': reclutados,
        'vm2_por_feedback': vm2_por_feedback,
        'vm2_decisiones_decisivas': vm2_decisiones_decisivas,
        'vm2_tras_decision': vm2_tras_decision,
        'vm2_no_aprobados': vm2_no_aprobados,
        'vm2_contratados': vm2_contratados,
        'vm2_candidato_perfil_video': vm2_candidato_perfil_video,
        'vm2_acciones_cargo_decisivas': vm2_acciones_cargo_decisivas,
        'vm2_cli087_por_aplicacion': vm2_cli087_por_aplicacion,
    }
    return render(request, 'admin/vacancy/client_user/vacancy_management2.html', context)