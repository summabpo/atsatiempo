from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from applications.usuarios.decorators  import validar_permisos
from django.contrib import messages
from applications.common.views.EnvioCorreo import enviar_correo, generate_token
from django.db.models import F
from django.http import JsonResponse

#formularios
from applications.vacante.forms.EntrevistaForm import EntrevistaCrearForm

#modelos
from applications.vacante.models import Cli057AsignacionEntrevista, Cli056AplicacionVacante, Cli052Vacante
from applications.cliente.models import Cli051Cliente
from applications.usuarios.models import Permiso
from applications.usuarios.models import UsuarioBase
from applications.common.models import Cat001Estado
from applications.candidato.models import Can101Candidato

from components.RegistrarHistorialVacante import crear_historial_aplicacion

#consultas
from applications.vacante.views.consultas.AsignacionEntrevistaConsultaView import consulta_asignacion_entrevista_entrevistador, consulta_asignacion_entrevista_candidato, consulta_asignacion_entrevista_cliente_todas


#CLIENTE

# Ver entrevistas generadas por cliente
@login_required
@validar_permisos(*Permiso.obtener_nombres())
def ver_entrevista_todos(request):    
    cliente_id = request.session.get('cliente_id')

    asignacion_entrevista = consulta_asignacion_entrevista_cliente_todas(cliente_id)
    contexto = {
        'asignacion_entrevista': asignacion_entrevista
    }

    return render(request, 'vacante/ver_entrevista_todos.html', contexto)

# Ver entrevistas generadas por candidato
@login_required
@validar_permisos('acceso_candidato')
def ver_entrevista_candidato(request): 
    candidato_id = request.session.get('candidato_id')

    asignaciones = Cli057AsignacionEntrevista.objects.select_related(
        'asignacion_vacante__vacante_id_052__cliente_id_051', 
        'asignacion_vacante__vacante_id_052', 
        'asignacion_vacante__candidato_101'
    ).filter(
        asignacion_vacante__candidato_101__id=candidato_id
    ).order_by('-fecha_entrevista').values(
        # Campos del modelo principal (Cli057AsignacionEntrevista)
        'id',
        'fecha_entrevista',
        'hora_entrevista',
        'lugar_enlace',
        # Resto de clientes pendientes
        razon_social=F('asignacion_vacante__vacante_id_052__cliente_id_051__razon_social'),
        titulo_vacante=F('asignacion_vacante__vacante_id_052__titulo'),
        primer_nombre=F('asignacion_vacante__candidato_101__primer_nombre'),
        segundo_nombre=F('asignacion_vacante__candidato_101__segundo_nombre'),
        primer_apellido=F('asignacion_vacante__candidato_101__primer_apellido'),
        segundo_apellido=F('asignacion_vacante__candidato_101__segundo_apellido'),
    )

    asignacion_entrevista = consulta_asignacion_entrevista_candidato(candidato_id)
    contexto = {
        'asignaciones': asignaciones,
        'asignacion_entrevista': asignacion_entrevista,
    }

    return render(request, 'vacante/ver_entrevista_candidato.html', contexto)

# Ver entrevistas generadas por entrevistador
@login_required
@validar_permisos(*Permiso.obtener_nombres())
def ver_entrevista_entrevistador(request):    
    usuario_id = request.session.get('_auth_user_id')

    usuario_id = int(usuario_id)

    asignaciones = Cli057AsignacionEntrevista.objects.select_related(
        'asignacion_vacante__vacante_id_052__cliente_id_051', 
        'asignacion_vacante__vacante_id_052', 
        'asignacion_vacante__candidato_101'
    ).filter(
        usuario_asignado__id = usuario_id
    ).order_by('-fecha_entrevista').values(
        # Campos del modelo principal (Cli057AsignacionEntrevista)
        'id',
        'fecha_entrevista',
        'hora_entrevista',
        'lugar_enlace',
        # Resto de clientes pendientes
        razon_social=F('asignacion_vacante__vacante_id_052__cliente_id_051__razon_social'),
        titulo_vacante=F('asignacion_vacante__vacante_id_052__titulo'),
        primer_nombre=F('asignacion_vacante__candidato_101__primer_nombre'),
        segundo_nombre=F('asignacion_vacante__candidato_101__segundo_nombre'),
        primer_apellido=F('asignacion_vacante__candidato_101__primer_apellido'),
        segundo_apellido=F('asignacion_vacante__candidato_101__segundo_apellido'),
    )

    asignacion_entrevista = consulta_asignacion_entrevista_entrevistador(usuario_id)
    print(asignacion_entrevista)
    contexto = {
        'asignaciones': asignaciones,
        'asignacion_entrevista': asignacion_entrevista,
    }

    return render(request, 'vacante/ver_entrevista_todos.html', contexto)

#Generar Entrevista
@login_required
@validar_permisos('acceso_admin', 'acceso_cliente')
def crear_entrevista(request, asignacion_id):
    url_actual = f"{request.scheme}://{request.get_host()}"
    validar_registro = False
    usuario_id = request.session.get('_auth_user_id')
    aplicacion_entrevista = get_object_or_404(Cli056AplicacionVacante, pk=asignacion_id)

    # Valida si esta valido la variable de sesion cliente
    cliente_id = request.session.get('cliente_id')
    if cliente_id:
        cliente = get_object_or_404(Cli051Cliente, id=cliente_id)
    else:
        cliente = get_object_or_404(Cli051Cliente, id=aplicacion_entrevista.vacante_id_052.cliente_id_051.id)

    grupo_id = request.session.get('grupo_id')

    vacante = get_object_or_404(Cli052Vacante, id=aplicacion_entrevista.vacante_id_052.id)
    
    usuario = get_object_or_404(UsuarioBase, id=usuario_id)
    
    asignacion_vacante = Cli056AplicacionVacante.objects.get(id=asignacion_id)
    info_candidato = Can101Candidato.objects.get(id= asignacion_vacante.candidato_101.id)

    entrevista_existente = Cli057AsignacionEntrevista.objects.filter(asignacion_vacante=asignacion_vacante)
    # if entrevista_existente:
    #     validar_registro = True
    #     entrevista = Cli057AsignacionEntrevista.objects.get(asignacion_vacante=asignacion_vacante)
    #     messages.success(request, 'Ya se ha asignado una entrevista')
    # else:
    #     entrevista = None    

    if request.method == 'POST':

        form = EntrevistaCrearForm(request.POST, grupo_id=4, cliente_id=cliente.id)
        if form.is_valid():
            
            fecha_entrevista = form.cleaned_data['fecha_entrevista']
            hora_entrevista = form.cleaned_data['hora_entrevista']
            entrevistador = form.cleaned_data['entrevistador']
            tipo_entrevista = form.cleaned_data['tipo_entrevista']
            lugar_enlace = form.cleaned_data['lugar_enlace']
            usuario_asignado = get_object_or_404(UsuarioBase, id=entrevistador)

            # Obtener instancias de los modelos relacionados
            usuario_asigno = request.user  # Asumiendo que el usuario actual es quien asigna la entrevista
            estado_default = Cat001Estado.objects.get(id=1)  # Asumiendo que 1 es el estado por defecto

            # Crear la nueva asignación de entrevista
            asignacion_entrevista = Cli057AsignacionEntrevista.objects.create(
                asignacion_vacante=asignacion_vacante,
                usuario_asigno=usuario_asigno,
                usuario_asignado=usuario_asignado,
                fecha_entrevista=fecha_entrevista,
                hora_entrevista=hora_entrevista,
                tipo_entrevista=tipo_entrevista,
                lugar_enlace=lugar_enlace,
                estado_asignacion=1,  # Pendiente por defecto
                estado=estado_default,
            )

            #funcion para crear registro en el historial y actualizar estado de la aplicacion de la vcatente
            crear_historial_aplicacion(asignacion_vacante, 2, request.session.get('_auth_user_id'), 'Entrevista Asignada')
            
            contexto_email_1 = {
                'entrevistador' : f'{usuario_asignado.primer_nombre} {usuario_asignado.segundo_nombre} {usuario_asignado.primer_apellido}',
                'nombre_candidato' : f'{info_candidato.primer_nombre} {info_candidato.segundo_nombre} {info_candidato.primer_apellido} {info_candidato.segundo_apellido}' ,
                'fecha_entrevista' : fecha_entrevista,
                'hora_entrevista' : hora_entrevista,
                'lugar_enlace' : lugar_enlace,
                'vacante' : vacante.titulo,
                'cliente' : cliente.razon_social,
                'url' : url_actual
            }

            lista_correos = [
                usuario_asignado.email,
                info_candidato.email
            ]

            # Envio de correo
            enviar_correo('asignacion_entrevista_entrevista', contexto_email_1, f'Asginación de Entrevista ID: {asignacion_entrevista.id}', lista_correos, correo_remitente=None)

            frase_aleatoria = 'Se ha asignado entrevista correctamente.'
            messages.success(request, frase_aleatoria)
            
            if cliente_id:
                return redirect('vacantes:gestion_vacante_reclutados', pk=vacante.id)
            else:
                return redirect('clientes:cliente_vacante_reclutado', pk=vacante.id)
        else:
            messages.error(request, 'Error al crear la asignación')
    else:
        form = EntrevistaCrearForm(grupo_id=4, cliente_id=cliente.id)

    contexto = {
        'form' : form,
        'aplicacion_entrevista': aplicacion_entrevista,
        'vacante': vacante,
        'validar_registro' : validar_registro,
        # 'entrevista' : entrevista,
    }

    return render(request, 'vacante/crear_entrevista.html', contexto)

def obtener_entrevistas(request):
    entrevistas = Cli057AsignacionEntrevista.objects.filter(estado=1)

    eventos_json = [
        {
            "title": f"Entrevista ID {evento.id}",
            "start": f"{evento.fecha_entrevista.isoformat()}T{evento.hora_entrevista}",
            "end": evento.fecha_entrevista.isoformat(),
            "description": f"Entrevista tipo: {evento.obtener_tipo_entrevista()} programada.",
            "color": evento.obtener_color(),  # Incluir el color
            "lugar_enlace": evento.lugar_enlace,  # Lugar Enlace
            "nombre_vacante": evento.asignacion_vacante.vacante_id_052.titulo,  # Nombre Vacante
            "nombre_cliente": evento.asignacion_vacante.vacante_id_052.cliente_id_051.razon_social,  # Nombre Vacante
            "estado_asignacion": evento.mostrar_estado_asignacion(),  # Nombre Vacante
        }
        for evento in entrevistas
    ]
    return JsonResponse(eventos_json, safe=False)