from django.shortcuts import render, redirect, get_object_or_404
from applications.candidato.models import Can101Candidato, Can102Experiencia, Can103Educacion
from applications.candidato.forms.CandidatoForms import CandidatoForm
from applications.candidato.forms.ExperienciaForms import ExperienciaCandidatoForm
from applications.candidato.forms.EstudioForms import EstudioCandidatoForm
from django.views.generic import (TemplateView, ListView)
from django.http import JsonResponse
from applications.common.models import Cat001Estado, Cat004Ciudad
from django.contrib import messages
from datetime import datetime
from applications.usuarios.models import Permiso
from django.contrib.auth.decorators import login_required
from applications.usuarios.decorators  import validar_permisos

global_id = None 

@login_required
@validar_permisos('acceso_admin', 'acceso_candidato')
def laboral_mostrar(request, pk=None):
    form_errors = False
    candidato = get_object_or_404(Can101Candidato, pk=pk)
    experiencias = Can102Experiencia.objects.filter(candidato_id_101=candidato.id, estado_id_001=1).order_by('-id')
    candidato_porcentaje = candidato.calcular_porcentaje()
    if request.method == 'POST': 
        form = ExperienciaCandidatoForm(request.POST)
        if form.is_valid():
            form.save(candidato_id=candidato.id)
            messages.success(request, 'El registro de experiencia laboral ha sido creado')
            return redirect('candidatos:candidato_laboral', pk=candidato.id)
        else:
            form_errors = True
            messages.error(request, form.errors)
    else:
        form = ExperienciaCandidatoForm(candidato_id=candidato.id)
    
    #Listado de objetos a enviar al template
    context = {
        'form': form,
        'candidato': candidato,
        'experiencias': experiencias,
        'form_errors': form_errors,
        'candidato_porcentaje': candidato_porcentaje,
    }

    return render(request, 'candidato/form_experiencia.html', context)



@login_required
@validar_permisos(*Permiso.obtener_nombres())
def laboral_api(request):
    global global_id

    if request.method == 'GET':
        id_educa = request.GET.get('dato')
        solicitud_candidato_labor= get_object_or_404(Can102Experiencia , pk=id_educa)

        global_id = solicitud_candidato_labor.id

        estado_id = Cat001Estado.objects.get(nombre=solicitud_candidato_labor.estado_id_001)

        response_data = {
            'data': {
                'id': solicitud_candidato_labor.id ,
                'estado_id_001': estado_id.id,
                'entidad': solicitud_candidato_labor.entidad,
                'sector': solicitud_candidato_labor.sector,
                'fecha_inicial': solicitud_candidato_labor.fecha_inicial,
                'fecha_final': solicitud_candidato_labor.fecha_final,
                'activo': solicitud_candidato_labor.activo,
                'logro': solicitud_candidato_labor.logro,
                'cargo': solicitud_candidato_labor.cargo,
            }
        }       
        return JsonResponse(response_data)

    if request.method == 'POST':
        
        entidad = request.POST.get('entidad')
        sector = request.POST.get('sector')
        fecha_inicial = request.POST.get('fecha_inicial')
        fecha_final = request.POST.get('fecha_final')
        cargo = request.POST.get('cargo')
        logro = request.POST.get('logro')
        activo = request.POST.get('activo') == 'on'
        
        

        expe_modificar = get_object_or_404(Can102Experiencia, pk= global_id )
        
        # Obtener la instancia del modelo Cat004Ciudad

        expe_modificar.entidad = entidad
        expe_modificar.activo = activo
        expe_modificar.sector = sector
        expe_modificar.cargo = cargo
        expe_modificar.logro = logro
        
        if fecha_inicial:
            expe_modificar.fecha_inicial = datetime.strptime(fecha_inicial, '%Y-%m-%d').date()
        if fecha_final:
            expe_modificar.fecha_final = datetime.strptime(fecha_final, '%Y-%m-%d').date()

        expe_modificar.save()
        
        messages.success(request, 'Se ha realizado la actualización del registro éxito.')
        return redirect('candidatos:candidato_laboral' , pk = expe_modificar.candidato_id_101.id)
        
    return JsonResponse({'error': 'Método no permitido'}, status=405)