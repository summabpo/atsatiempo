from django.shortcuts import render
from applications.candidato.models import Can101Candidato
from django.views import View

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