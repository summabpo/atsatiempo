from django.shortcuts import render, redirect, get_object_or_404
from applications.candidato.forms.pruebasforms import PruebasForm
from applications.candidato.models import Can101Candidato, Can104Skill, Can101CandidatoSkill
from applications.common.models import Cat001Estado 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def pruebas(request, candidato_id, pk=None):
    candidato = get_object_or_404(Can101Candidato, pk=candidato_id)
    data = Cat001Estado.objects.get(id=1)

    # Recuperar listskill de la sesión si existe
    listskill = request.session.get('listskill', [])
    habi = None
    
    if request.method == 'POST':
        form = PruebasForm(request.POST)
        if form.is_valid():
            level = form.cleaned_data['level']
            ability = form.cleaned_data['ability']
            
            post_data = request.POST.dict()  # Para datos de formulario (application/x-www-form-urlencoded)
            print('Datos POST recibidos:', post_data)

            skill = Can104Skill.objects.filter(id=ability)
            if skill.exists():
                candidato_skill = Can101CandidatoSkill.objects.create(
                    candidato_id_101=candidato, 
                    skill_id_104=skill.first(), 
                    nivel=level,
                )
            else:
                skill = Can104Skill.objects.create(
                    estado_id_004=data,
                    nombre=ability,
                )
                candidato_skill = Can101CandidatoSkill.objects.create(
                    candidato_id_101=candidato, 
                    skill_id_104=skill, 
                    nivel=level,
                )
            
            #Guardar la instancia de Can101CandidatoSkill en la lista
            listskill.append({
                'id': candidato_skill.id,
                'ability': candidato_skill.skill_id_104.nombre,
                'level': candidato_skill.nivel,
            })

            #Guardar la lista en la sesión
            request.session['listskill'] = listskill

            #Limpiar el formulario
            form = PruebasForm()
            return redirect('candidatos:inicio', candidato_id=candidato.id)
    else: 
        
        form = PruebasForm()
        habi = Can101CandidatoSkill.objects.filter(candidato_id_101=candidato)
    
    return render(request, 'base_test/habilidades.html',
                  { 
                      'form': form,
                      'habi': habi,
                      'listskill': listskill,
                  })
    
    
##* utilidades 

@csrf_exempt
def limpiar_lisskill(request):
    if request.method == 'POST':
        print('llege yo ')
        request.session.pop('listskill', None)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)