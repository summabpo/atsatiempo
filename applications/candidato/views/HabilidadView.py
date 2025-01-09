from django.shortcuts import render, redirect, get_object_or_404
from applications.candidato.models import Can101Candidato, Can101CandidatoSkill, Can104Skill
from applications.common.models import Cat001Estado 
from applications.candidato.forms.HabilidadForms import HabilidadCandidatoForm
from django.views.generic import (TemplateView, ListView)
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from applications.usuarios.models import Permiso
from django.contrib.auth.decorators import login_required
from applications.usuarios.decorators  import validar_permisos
from django.http import JsonResponse

@login_required
@validar_permisos('acceso_admin', 'acceso_candidato')
def habilidad_obtener(request, pk=None):
    candidato = get_object_or_404(Can101Candidato, pk=pk)
    data = Cat001Estado.objects.get(id=1)
    habilidades = Can101CandidatoSkill.objects.filter(candidato_id_101=candidato.id).order_by('-id')
    candidato_porcentaje = candidato.calcular_porcentaje()
    if request.method == 'POST':
        form = HabilidadCandidatoForm(request.POST)

        if form.is_valid():
            level = form.cleaned_data['level']
            ability = form.cleaned_data['ability']
            
            # Convertir el nombre a minúsculas
            ability = ability.lower()
            
            # Intentar obtener el objeto
            skill, created = Can104Skill.objects.get_or_create(
                nombre=ability,
                defaults={'estado_id_004': data}
            )

            # Verificar si la habilidad ya está asociada al candidato
            if Can101CandidatoSkill.objects.filter(candidato_id_101=candidato, skill_id_104=skill).exists():
                messages.error(request, 'La habilidad ya está asociada al candidato')
            else:
                # Crear el registro de la habilidad del candidato
                Can101CandidatoSkill.objects.create(
                    candidato_id_101=candidato,
                    skill_id_104=skill,
                    nivel=level
                )
                messages.success(request, 'La habilidad se ha guardado correctamente')
                return redirect('candidatos:candidato_habilidad', pk=candidato.id)

            
        else:
            messages.error(request, form.errors)
    else: 
        form = HabilidadCandidatoForm()
        habilidades = Can101CandidatoSkill.objects.filter(candidato_id_101 = candidato.id)
    
    return render(request, 'candidato/form_habilidad.html',
        { 
            'form': form,
            'habilidades': habilidades,
            'candidato': candidato,
            'candidato_porcentaje': candidato_porcentaje,
        })
    
# eliminar habilidades seleccionadas
@csrf_exempt
@login_required
@validar_permisos('acceso_admin', 'acceso_candidato')
def habilidad_eliminar(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ids = data.get('ids', [])
        if not ids:
            return JsonResponse({'success': False, 'message': 'No se proporcionaron IDs.'})

        # Eliminar los registros
        Can101CandidatoSkill.objects.filter(id__in=ids).delete()
        return JsonResponse({'success': True, 'message': 'Registros eliminados correctamente.'})
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})

#eliminar habilidad por boton
@csrf_exempt
@login_required
@validar_permisos('acceso_admin', 'acceso_candidato')
def habilidad_eliminar_id(request, pk, candidato_id):
    habilidad = get_object_or_404(Can101CandidatoSkill, pk=pk)
    habilidad.delete()
    messages.success(request, 'La habilidad se ha eliminado correctamente')
    return redirect('candidatos:candidato_habilidad', pk=candidato_id)
    
    
##* utilidades 

@csrf_exempt
@login_required
#@validar_permisos(*Permiso.obtener_nombres())
def limpiar_lisskill(request):
    if request.method == 'POST':
        request.session.pop('listskill', None)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


