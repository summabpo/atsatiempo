from applications.candidato.models import Can101Candidato  

def buscar_candidato_por_documento(numero_documento):
    return Can101Candidato.objects.get(numero_documento=numero_documento)