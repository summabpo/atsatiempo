from django.shortcuts import render, redirect, get_object_or_404
from applications.candidato.models import Can101Candidato, Can102Experiencia, Can103Educacion, Can101CandidatoSkill, Can104Skill
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.candidato.forms.CandidatoForms import CandidatoForm
from applications.candidato.forms.ExperienciaForms import ExperienciaCandidatoForm
from applications.candidato.forms.HabilidadForms import HabilidadCandidatoForm
from applications.candidato.forms.EstudioForms import EstudioCandidatoForm
from django.views.generic import (TemplateView, ListView)
from django.contrib import messages
from django.http import JsonResponse
import json

def candidato_mostrar(request, pk=None):
    # Valida si se pasa un parametro pk o ID del candidato
    if pk:
        candidato = get_object_or_404(Can101Candidato, pk=pk)
        accion = 'Editar'
    
    else:
        candidato = None
        accion = 'Crear'

   

    if request.method == 'POST':

        if 'submit_candidato' in request.POST:
            form = CandidatoForm(request.POST, instance=candidato)
            
            if form.is_valid():
                form.save()
                messages.success(request, 'Información Personal Actualizada')
                return redirect('candidatos:candidato_editar', pk=candidato.id)
            else:
                errores = ''
                for field, errors in form.errors.items():
                    errores += f'{field}: {", ".join(errors)}'
                messages.error(request, f'El formulario tiene los siguientes errores: {errores}')
        else:
            form = CandidatoForm(instance=candidato) 

    else:
        form = CandidatoForm(instance=candidato)
        

    return render(request, 'candidato/form_candidato.html', {
        'form': form,
        'candidato': candidato,
        'accion': accion, 
         })

global_dato = None 

def obtener_estudio_view(request):
    global global_dato

    if request.method == 'GET':
        dato              = request.GET.get('dato')
        solicitud_estudio = get_object_or_404(Can103Educacion, pk=dato)
        global_dato = dato
        

        estado_id    = Cat001Estado.objects.get(nombre=solicitud_estudio.estado_id_001)
        candidato_id = Can101Candidato.objects.get(email=solicitud_estudio.candidato_id_101)
        ciudad_id    = Cat004Ciudad.objects.get(nombre=solicitud_estudio.ciudad_id_004)

        print(solicitud_estudio.grado_en)
        
        response_data = {
            'data': {
                'id': solicitud_estudio.id,
                'estado_id_001': estado_id.id,
                'institucion': solicitud_estudio.institucion,
                'fecha_inicial': solicitud_estudio.fecha_inicial,
                'fecha_final': solicitud_estudio.fecha_final,
                'grado_en':  True if solicitud_estudio.grado_en  == "True" else False  ,
                'titulo': solicitud_estudio.titulo,
                'carrera': solicitud_estudio.carrera,
                'fortaleza_adquiridas': solicitud_estudio.fortaleza_adquiridas,
                'candidato_id_101': candidato_id.id,
                'ciudad_id_004': ciudad_id.id,
            }
        }
        
        return JsonResponse(response_data)
    
    if request.method == 'POST':
        institucion = None
        fecha_inicial = None
        fecha_final = None
        titulo = None
        carrera = None
        fortaleza_adquiridas = None
        candidato_id_101 = None
        ciudad_id_004 = None
        grado_en = None

        institucion = request.POST.get('institucion')
        fecha_inicial = request.POST.get('fecha_inicial')
        fecha_final = request.POST.get('fecha_final')
        titulo = request.POST.get('titulo')
        carrera = request.POST.get('carrera')
        fortaleza_adquiridas = request.POST.get('fortaleza_adquiridas')
        candidato_id_101 = request.POST.get('id_candidato')
        ciudad_id_004 = request.POST.get('ciudad_id_004')
        grado_en = request.POST.get('grado_en')
        
        ghost = global_dato

        
        
        solicitud_estudio_modificar = get_object_or_404(Can103Educacion, pk=ghost)
        # Obtener la instancia del modelo Can101Candidato
        candidato = get_object_or_404(Can101Candidato, pk=candidato_id_101)

        # Obtener la instancia del modelo Cat004Ciudad
        ciudad = get_object_or_404(Cat004Ciudad, pk=ciudad_id_004)

        solicitud_estudio_modificar.estado_id_001 = Cat001Estado.objects.get(id=1)
        solicitud_estudio_modificar.institucion = institucion
        solicitud_estudio_modificar.fecha_inicial = fecha_inicial
        solicitud_estudio_modificar.fecha_final = fecha_final
        solicitud_estudio_modificar.titulo = titulo
        solicitud_estudio_modificar.carrera = carrera
        solicitud_estudio_modificar.fortaleza_adquiridas = fortaleza_adquiridas
        solicitud_estudio_modificar.ciudad_id_004 = ciudad
        solicitud_estudio_modificar.grado_en = grado_en

        solicitud_estudio_modificar.save()

        messages.success(request, 'Se ha realizado la actualización del registro éxito.')
        return redirect('candidatos:candidato_editar', pk=candidato.id)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

# 
global_id_laboral = None
def obtener_laboral_view(request):
    global global_id_laboral

    if request.method == 'GET':
        dato              = request.GET.get('dato')
        solicitud_laboral = get_object_or_404(Can102Experiencia, pk=dato)
        global_id_laboral = dato

        estado_id    = Cat001Estado.objects.get(nombre=solicitud_laboral.estado_id_001)
        candidato_id = Can101Candidato.objects.get(email=solicitud_laboral.candidato_id_101)

        
        response_data = {
            'data': {
                'id': solicitud_laboral.id,
                'estado_id_001': estado_id.id,
                'entidad': solicitud_laboral.entidad,
                'sector': solicitud_laboral.sector,
                'fecha_inicial': solicitud_laboral.fecha_inicial,
                'fecha_final': solicitud_laboral.fecha_final,
                'activo':  True if solicitud_laboral.activo  == "SI" else False ,
                'logro': solicitud_laboral.logro,
                'candidato_id_101': candidato_id.id,
                'cargo': solicitud_laboral.cargo,
            }
        }
        
        return JsonResponse(response_data)
    
    if request.method == 'POST':
        entidad = None
        sector = None
        activo = None
        fecha_inicial = None
        fecha_final = None
        cargo = None

        entidad = request.POST.get('entidad')
        sector = request.POST.get('sector')
        activo = request.POST.get('activo')
        fecha_inicial = request.POST.get('fecha_inicial')
        fecha_final = request.POST.get('fecha_final')
        cargo = request.POST.get('cargo')
        candidato_id_101 = request.POST.get('id_candidato')

        id_experiencia = global_id_laboral

        solicitud_laboral_modificar = get_object_or_404(Can102Experiencia, pk=id_experiencia)

        # Obtener la instancia del modelo Can101Candidato
        candidato = get_object_or_404(Can101Candidato, pk=candidato_id_101)

        solicitud_laboral_modificar.estado_id_001 = Cat001Estado.objects.get(id=1)
        solicitud_laboral_modificar.entidad = entidad
        solicitud_laboral_modificar.sector = sector
        solicitud_laboral_modificar.activo = activo
        solicitud_laboral_modificar.fecha_inicial = fecha_inicial
        solicitud_laboral_modificar.fecha_final = fecha_final
        solicitud_laboral_modificar.cargo = cargo

        solicitud_laboral_modificar.save()
    
        messages.success(request, 'Se ha realizado la actualización del registro éxito.')
        return redirect('candidatos:candidato_editar', pk=candidato.id)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


#Crear Habilidades opcional
def habilidades_crear(request):

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(data)
            for item in data:
                # Intentar obtener el objeto existente
                habilidad, creada = Can104Skill.objects.get_or_create(
                    nombre=item['palabra'],
                    estado_id_004= Cat001Estado.objects.get(id=1) 
                )

                if creada:
                    print(f'La habilidad {habilidad.nombre} se ha creado con éxito')
                else:
                    print(f'La habilidad {habilidad.nombre} ya existe')

                Can101CandidatoSkill.objects.get_or_create(
                    candidato_id_101=Can101Candidato.objects.get(id=item['empleado_id']), 
                    skill_id_104=habilidad,
                    nivel=item['estado']
                )

            messages.success(request, 'Se ha ingresado las habilidades.')
            return redirect('candidatos:candidato_editar', pk=item['empleado_id'])

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)