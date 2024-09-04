from django.shortcuts import render
from applications.candidato.models import Can101Candidato, Can104Skill
from django.views import View
from django.http import JsonResponse
from django.db.models import Q

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
    
class PruebaTextoSugerido(View):
    model = Can101Candidato
    template_name = "pruebas/form_auto_completado.html"

    def get(self, request, *args, **kwargs):
        # Obtener todos los objetos del modelo
        candidatos = self.model.objects.all()
        
        # Renderizar la plantilla con los datos
        return render(request, self.template_name, {'candidatos': candidatos})

def sugerir_habilidades(request):
    query = request.GET.get('query', '')
    habilidades = Can104Skill.objects.filter(nombre__icontains=query)[:5]
    sugerencias = [habilidad.nombre for habilidad in habilidades]
    return JsonResponse(sugerencias, safe=False)