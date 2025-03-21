from django.shortcuts import render, redirect
from applications.candidato.models import Can101Candidato, Can104Skill
from django.views import View
from django.http import JsonResponse
from django.db.models import Q
from applications.common.forms.PruebasForm import HabilidadForm

class ListadoSimpleListView(View):
    model = Can101Candidato
    template_name = "pruebas/grid_prueba_simple.html"

    def get(self, request, *args, **kwargs):
        # Obtener todos los objetos del modelo
        candidatos = self.model.objects.all()
        
        # Renderizar la plantilla con los datos
        return render(request, self.template_name, {'candidatos': candidatos})
    
class ListadoExportarListView(View):
    model = Can101Candidato
    template_name = "pruebas/grid_prueba_exportar.html"

    def get(self, request, *args, **kwargs):
        # Obtener todos los objetos del modelo
        candidatos = self.model.objects.all()
        
        # Renderizar la plantilla con los datos
        return render(request, self.template_name, {'candidatos': candidatos})
    
def PruebaTextoSugerido(request):
    
    if request.method == 'POST':
        form = HabilidadForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('nombre_de_tu_vista')  # Redirige después de guardar
    else:
        form = HabilidadForm()

    return render(request, 'pruebas/form_auto_completado.html', {'form': form})

def sugerir_habilidades(request):
    query = request.GET.get('query', '')
    habilidades = Can104Skill.objects.filter(nombre__icontains=query)[:5]
    sugerencias = [habilidad.nombre for habilidad in habilidades]
    return JsonResponse(sugerencias, safe=False)


def test_template(request):
    return render(request, 'admin/test_template.html')
