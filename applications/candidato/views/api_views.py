from django.http import JsonResponse
from applications.candidato.models import Can101Candidato, Can102Experiencia, Can103Educacion

# def api_candidate_info(request):
#     if request.method != 'POST':
#         return JsonResponse({'error': 'Método no permitido'}, status=405)
    
#     numero_documento = request.POST.get('numero_documento')
    
#     if not numero_documento:
#         return JsonResponse({'error': 'Número de documento no proporcionado'}, status=400)
    
#     try:
#         # Trae información del candidato
#         candidato = Can101Candidato.objects.get(numero_documento=numero_documento)
        
#         # Trae información de la experiencia y educación del candidato
#         experiencias = Can102Experiencia.objects.filter(candidato=candidato).values()
#         educaciones = Can103Educacion.objects.filter(candidato=candidato).values()
        
#         return JsonResponse({
#             'status': 'success',
#             'primer_nombre': candidato.primer_nombre,
#             'segundo_nombre': candidato.segundo_nombre,
#             'primer_apellido': candidato.primer_apellido,
#             'segundo_apellido': candidato.segundo_apellido,
#             'email': candidato.email,
#             'telefono': candidato.telefono,
#             'experiencias': list(experiencias),
#             'educaciones': list(educaciones),
#         })
#     except Can101Candidato.DoesNotExist:
#         return JsonResponse({'error': 'Candidato no encontrado'}, status=404)