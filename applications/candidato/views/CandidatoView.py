from django.shortcuts import render, redirect, get_object_or_404
from applications.candidato.models import Can101Candidato, Can102Experiencia, Can103Educacion, Can101CandidatoSkill
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.candidato.forms.CandidatoForms import CandidatoForm
from applications.candidato.forms.ExperienciaForms import ExperienciaCandidatoForm
from applications.candidato.forms.HabilidadForms import HabilidadCandidatoForm
from applications.candidato.forms.EstudioForms import EstudioCandidatoForm
from django.views.generic import (TemplateView, ListView)
from django.contrib import messages
from django.http import JsonResponse

def candidato_mostrar(request, pk=None):
    # Valida si se pasa un parametro pk o ID del candidato
    if pk:
        candidato = get_object_or_404(Can101Candidato, pk=pk)
        experiencias = Can102Experiencia.objects.filter(candidato_id_101=candidato.id, estado_id_001=1).order_by('-id')
        estudios = Can103Educacion.objects.filter(candidato_id_101=candidato.id, estado_id_001=1).order_by('-id')
        habilidades = Can101CandidatoSkill.objects.filter(candidato_id_101=candidato.id).order_by('-id')

        accion = 'Editar'

    else:
        candidato = None
        experiencias = None
        estudios = None
        habilidades = None
        
        accion = 'Crear'

    if request.method == 'POST':

        if 'submit_candidato' in request.POST:
            form = CandidatoForm(request.POST, instance=candidato)
            
            if form.is_valid():
                form.save()
                messages.success(request, 'Experiencia Creada')
                return redirect('candidatos:candidato_editar', pk=candidato.id)
            else:
                errores = ''
                for field, errors in form.errors.items():
                    errores += f'{field}: {", ".join(errors)}'
                messages.error(request, f'El formulario tiene los siguientes errores: {errores}')
        else:
            form = CandidatoForm(instance=candidato) 

        if 'submit_experiencia' in request.POST:
            form_experiencia = ExperienciaCandidatoForm(request.POST)
            if form_experiencia.is_valid():
                form_experiencia.save(candidato_id=candidato.id)
                messages.success(request, 'Experiencia Creada')
                return redirect('candidatos:candidato_editar', pk=candidato.id)
            else:
                errores = ''
                for field, errors in form_experiencia.errors.items():
                    errores += f'{field}: {", ".join(errors)}'
                messages.error(request, f'El formulario tiene los siguientes errores : {errores}')
        else:
            form_experiencia = ExperienciaCandidatoForm(candidato_id=candidato.id)

        if 'submit_estudio' in request.POST:
            form_estudio = EstudioCandidatoForm(request.POST)
            if form_estudio.is_valid():
                form_estudio.save(candidato_id=candidato.id)
                messages.success(request, 'Estudio Creado')
                return redirect('candidatos:candidato_editar', pk=candidato.id)
            else:
                errores = ''
                for field, errors in form_estudio.errors.items():
                    errores += f'{field}: {", ".join(errors)}'
                messages.error(request, f'El formulario tiene los siguientes errores aca : {errores}')
        else:
            form_estudio = EstudioCandidatoForm(candidato_id=candidato.id)
            

        if 'submit_habilidad' in request.POST:
            form_habilidad = HabilidadCandidatoForm(request.POST)
            if form_habilidad.is_valid():
                form_habilidad.save(candidato_id=candidato.id)
                messages.success(request, 'Habilidad Creada')
                return redirect('candidatos:candidato_editar', pk=candidato.id)
            else:
                errores = ''
                for field, errors in form_habilidad.errors.items():
                    errores += f'{field}: {", ".join(errors)}'
                messages.error(request, f'El formulario tiene los siguientes errores aca : {errores}')
        else:
            form_habilidad = HabilidadCandidatoForm(candidato_id=candidato.id)
            
    else:
        form = CandidatoForm(instance=candidato)
        form_experiencia = ExperienciaCandidatoForm(candidato_id=candidato.id)
        form_estudio = EstudioCandidatoForm(candidato_id=candidato.id)
        form_habilidad = HabilidadCandidatoForm(candidato_id=candidato.id)

    return render(request, 'candidato/form_candidato.html', {
        'form': form,
        'form_experiencia' : form_experiencia,
        'form_estudio' : form_estudio,
        'form_habilidad' : form_habilidad,
        'candidato': candidato,
        'experiencias': experiencias, 
        'habilidades':habilidades,
        'accion': accion, 
        'estudios': estudios
        })

def obtener_estudio_view(request):
    global global_dato

    if request.method == 'GET':
        dato              = request.GET.get('dato')
        solicitud_estudio = get_object_or_404(Can103Educacion, pk=dato)
        global_dato = dato

        estado_id = Cat001Estado.objects.get(nombre=solicitud_estudio.estado_id_001)
        candidato_id = Can101Candidato.objects.get(email=solicitud_estudio.candidato_id_101)
        ciudad_id = Cat004Ciudad.objects.get(nombre=solicitud_estudio.ciudad_id_004)
    
        response_data = {
            'data': {
                'id': solicitud_estudio.id,
                'estado_id_001': estado_id.id,
                'institucion': solicitud_estudio.institucion,
                'fecha_inicial': solicitud_estudio.fecha_inicial,
                'fecha_final': solicitud_estudio.fecha_final,
                'grado_en': solicitud_estudio.grado_en,
                'titulo': solicitud_estudio.titulo,
                'carrera': solicitud_estudio.carrera,
                'fortaleza_adquiridas': solicitud_estudio.fortaleza_adquiridas,
                'candidato_id_101': candidato_id.id,
                'ciudad_id_004': ciudad_id.id,
            }
        }
        
        return JsonResponse(response_data)
    
    if request.method == 'POST':
        estado_id_001 = None
        institucion = None
        fecha_inicial = None
        fecha_final = None
        titulo = None
        carrera = None
        fortaleza_adquiridas = None
        candidato_id_101 = None
        ciudad_id_004 = None

        estado_id_001 = request.POST.get('estado_id_001')
        institucion = request.POST.get('institucion')
        fecha_inicial = request.POST.get('fecha_inicial')
        fecha_final = request.POST.get('fecha_final')
        titulo = request.POST.get('titulo')
        carrera = request.POST.get('carrera')
        fortaleza_adquiridas = request.POST.get('fortaleza_adquiridas')
        candidato_id_101 = request.POST.get('candidato_id_101')
        ciudad_id_004 = request.POST.get('ciudad_id_004')

        ghost = global_dato
        
        solicitud_estudio_modificar = get_object_or_404(Can103Educacion, pk=ghost)

        solicitud_estudio_modificar.estado_id_001 = estado_id_001
        solicitud_estudio_modificar.institucion = institucion
        solicitud_estudio_modificar.fecha_inicial = fecha_inicial
        solicitud_estudio_modificar.fecha_final = fecha_final
        solicitud_estudio_modificar.titulo = titulo
        solicitud_estudio_modificar.carrera = carrera
        solicitud_estudio_modificar.fortaleza_adquiridas = fortaleza_adquiridas
        solicitud_estudio_modificar.candidato_id_101 = candidato_id_101
        solicitud_estudio_modificar.ciudad_id_004 = ciudad_id_004
        
        solicitud_estudio_modificar.save()
        print(estado_id)
        messages.success(request, 'La solicitud de Vacaciones/Licencias ha sido actualizada correctamente.')
        return redirect('candidatos:candidato_editar', pk=solicitud_estudio_modificar.id)

    return JsonResponse({'error': 'Método no permitido'}, status=405)