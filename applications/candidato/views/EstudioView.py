from django.shortcuts import render, redirect, get_object_or_404
from applications.candidato.models import Can101Candidato, Can103Educacion
from applications.candidato.forms.CandidatoForms import CandidatoForm
from applications.candidato.forms.ExperienciaForms import ExperienciaCandidatoForm
from applications.candidato.forms.EstudioForms import EstudioCandidatoForm 
from django.views.generic import (TemplateView, ListView)
from django.contrib import messages
from django.http import JsonResponse
from applications.common.models import Cat001Estado, Cat004Ciudad
from datetime import datetime

global_id = None 


def estudio_mostrar(request, pk=None):
    form_errors = False
    candidato = get_object_or_404(Can101Candidato, pk=pk)
    estudios = Can103Educacion.objects.filter(candidato_id_101=candidato.id, estado_id_001=1).order_by('-id')

    # Formulario Estudios
    if request.method == 'POST': 
        form = EstudioCandidatoForm(request.POST)
        if form.is_valid():
            form.save(candidato_id=candidato.id)
            messages.success(request, 'El registro de experiencia academica ha sido creado')
            return redirect('candidatos:candidato_academica', pk=candidato.id)
        else:
            form_errors = True
            messages.error(request, form.errors)
    else:
        form = EstudioCandidatoForm(candidato_id=candidato.id)

    #Listado de objetos a enviar al template
    context = {
        'form': form,
        'candidato': candidato,
        'estudios': estudios,
        'form_errors': form_errors,
        
    }

    return render(request, 'candidato/form_estudio.html', context)




def estudio_api(request):
    global global_id

    if request.method == 'GET':
        id_educa = request.GET.get('dato')
        solicitud_candidato_academia= get_object_or_404(Can103Educacion , pk=id_educa)

        global_id = solicitud_candidato_academia.id

        estado_id = Cat001Estado.objects.get(nombre=solicitud_candidato_academia.estado_id_001)
        ciudad_id = Cat004Ciudad.objects.get(nombre=solicitud_candidato_academia.ciudad_id_004)

        response_data = {
            'data': {
                'id': solicitud_candidato_academia.id ,
                'estado_id_001': estado_id.id,
                'institucion': solicitud_candidato_academia.institucion,
                'fecha_inicial': solicitud_candidato_academia.fecha_inicial,
                'fecha_final': solicitud_candidato_academia.fecha_final,
                'grado_en': solicitud_candidato_academia.grado_en,
                'titulo': solicitud_candidato_academia.titulo,
                'carrera': solicitud_candidato_academia.carrera,
                'fortaleza_adquiridas': solicitud_candidato_academia.fortaleza_adquiridas,
                'ciudad_id_004': ciudad_id.id,
            }
        }       
        return JsonResponse(response_data)

    if request.method == 'POST':

        institucion = request.POST.get('institucion')
        fecha_inicial = request.POST.get('fecha_inicial')
        fecha_final = request.POST.get('fecha_final')
        grado_en = request.POST.get('grado_en') == 'on'
        titulo = request.POST.get('titulo')
        carrera = request.POST.get('carrera')
        fortaleza_adquiridas = request.POST.get('fortaleza_adquiridas')
        ciudad_id_004 = request.POST.get('ciudad_id_004')

        academia_modificar = get_object_or_404(Can103Educacion, pk= global_id )
        
        # Obtener la instancia del modelo Cat004Ciudad
        ciudad = get_object_or_404(Cat004Ciudad, pk=ciudad_id_004)

        academia_modificar.institucion = institucion
        academia_modificar.grado_en = grado_en
        academia_modificar.titulo = titulo
        academia_modificar.carrera = carrera
        academia_modificar.fortaleza_adquiridas = fortaleza_adquiridas
        academia_modificar.ciudad_id_004 = ciudad

        
        if fecha_inicial:
            academia_modificar.fecha_inicial = datetime.strptime(fecha_inicial, '%Y-%m-%d').date()
        if fecha_final:
            academia_modificar.fecha_final = datetime.strptime(fecha_final, '%Y-%m-%d').date()
            
        academia_modificar.save()
        
        messages.success(request, 'Se ha realizado la actualización del registro éxito.')
        return redirect('candidatos:candidato_academica' , pk = academia_modificar.candidato_id_101.id)
        
    return JsonResponse({'error': 'Método no permitido'}, status=405)