# API para profesiones
from django.http import JsonResponse
from applications.vacante.models import Cli055ProfesionEstudio

def profesiones_whitelist(request):
    """API para obtener la lista de profesiones para Tagify"""
    try:
        profesiones = Cli055ProfesionEstudio.objects.filter(
            estado_id_001=1
        ).values('id', 'nombre').order_by('nombre')
        
        # Formato para Tagify
        whitelist = [
            {'value': p['nombre'], 'id': p['id']} 
            for p in profesiones
        ]
        
        return JsonResponse(whitelist, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)