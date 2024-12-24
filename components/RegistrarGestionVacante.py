from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, Q, Case, When, Value, CharField

#utils
from django.utils.timezone import now
from applications.common.views.EnvioCorreo import enviar_correo

#modelos
from applications.vacante.models import Cli052Vacante
from applications.reclutado.models import Cli056AplicacionVacante

def validar_vacante_cierre(vacante_id):

    cantidad_vacantes = Cli056AplicacionVacante.objects.filter(vacante_id_052=vacante_id, estado_aplicacion=8).count()

    vacante = get_object_or_404(Cli052Vacante, id=vacante_id)

    if cantidad_vacantes == vacante.numero_posiciones:
        vacante.estado_vacante = 3
        vacante.fecha_cierre = now()
        vacante.save()

        respuesta = True
    else:
        respuesta = False
    
    return respuesta

def validar_vacante_cancelar(vacante, url_actual):
    # Se obtiene la vacante
    

    #validar personal recluado que no se encuentre seleccionado o No Apto
    cantidad_vacantes = Cli056AplicacionVacante.objects.filter(
        vacante_id_052=vacante.id  # Filtrar por el ID de la vacante
    ).exclude(
        estado_aplicacion__in=[8, 12]  # Excluir los estados 8 y 12
    )

    for aplicacion in cantidad_vacantes:
        aplicacion.estado_aplicacion = 10
        aplicacion.save()

        candidato = aplicacion.candidato_101
        email_candidato = candidato.email


        
        contexto_email_1 = {
            'nombre_candidato' : f'{candidato.primer_nombre} {candidato.segundo_nombre} {candidato.primer_apellido} {candidato.segundo_apellido}' ,
            'cliente' : vacante.cliente_id_051.razon_social,
            'id_vacante' : vacante.id,
            'vacante' : vacante.titulo,
            'url' : url_actual
        }
        print(email_candidato)
        lista_correos = [
            email_candidato,
        ]

        # Envio de correo
        enviar_correo('cancelacion_vacante_correo', contexto_email_1, f'Cancelación Vacante ID: {vacante.id}', lista_correos, correo_remitente=None)


