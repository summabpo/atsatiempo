from django.http import JsonResponse
from applications.candidato.models import Can101Candidato
from applications.reclutado.models import Cli056AplicacionVacante
from applications.services.service_candidate import buscar_candidato_por_documento

def api_candidate_document(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    numero_documento = request.POST.get('numero_documento')
    vacante = request.POST.get('vacante_id')
    
    if not numero_documento:
        return JsonResponse({'error': 'Número de documento no proporcionado'}, status=400)
    
    
        

    try:
        #trae información del candidato
        candidato = buscar_candidato_por_documento(numero_documento)
        
        if Cli056AplicacionVacante.objects.filter(candidato_101=candidato.id, vacante_id_052=vacante).exists():
            status = 'error'
            message = 'El candidato ya está registrado en esta vacante.'
        else:
            status = 'success'
            message = 'Candidato disponible para registro.'
        
        return JsonResponse({
            'message': message,
            'status': status,
            'primer_nombre': candidato.primer_nombre,
            'segundo_nombre': candidato.segundo_nombre,
            'primer_apellido': candidato.primer_apellido,
            'segundo_apellido': candidato.segundo_apellido,
            'email': candidato.email,
            'telefono': candidato.telefono,
        })
    except Can101Candidato.DoesNotExist:
        return JsonResponse({'error': 'Candidato no encontrado'}, status=404)