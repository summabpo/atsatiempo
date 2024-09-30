from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from applications.usuarios.decorators  import validar_permisos
from django.contrib import messages
from applications.common.views.EnvioCorreo import enviar_correo, generate_token

#formularios
from applications.vacante.forms.EntrevistaForm import EntrevistaCrearForm

#modelos
from applications.vacante.models import Cli057AsignacionEntrevista, Cli056AplicacionVacante, Cli052Vacante
from applications.cliente.models import Cli051Cliente
from applications.usuarios.models import Permiso
from applications.usuarios.models import UsuarioBase
from applications.common.models import Cat001Estado

# Create your views here.


#CLIENTE

# Ver entrevistas generadas
@login_required
@validar_permisos(*Permiso.obtener_nombres())
def ver_entrevista_todos(request):    
    asignaciones = Cli057AsignacionEntrevista.objects.filter(estado=1, asignacion_vacante__candidato_101__id=1 ).select_related(
        'asignacion_vacante__candidato_101',
        'asignacion_vacante__vacante_id_052',
        'usuario_asigno',
        'usuario_asignado'
    ).values('asignacion_vacante__id','asignacion_vacante__candidato_101__primer_nombre').order_by('fecha_asignacion')
    
    print(asignaciones)

    contexto = {
        'asignaciones': asignaciones
    }

#Generar Entrevista
@login_required
@validar_permisos(*Permiso.obtener_nombres())
def crear_entrevista(request, asignacion_id):

    usuario_id = request.session.get('_auth_user_id')
    cliente_id = request.session.get('cliente_id')
    grupo_id = request.session.get('grupo_id')
    print(asignacion_id)

    aplicacion_entrevista = get_object_or_404(Cli056AplicacionVacante, pk=asignacion_id)
    vacante = get_object_or_404(Cli052Vacante, id=aplicacion_entrevista.vacante_id_052.id)
    cliente = get_object_or_404(Cli051Cliente, id=cliente_id)
    usuario = get_object_or_404(UsuarioBase, id=usuario_id)
    print(grupo_id)
    print(cliente_id)
    if request.method == 'POST':
        form = EntrevistaCrearForm(request.POST, grupo_id=4, cliente_id=cliente_id)
        if form.is_valid():
            
            fecha_entrevista = form.cleaned_data['fecha_entrevista']
            hora_entrevista = form.cleaned_data['hora_entrevista']
            entrevistador = form.cleaned_data['entrevistador']
            tipo_entrevista = form.cleaned_data['tipo_entrevista']
            lugar_enlace = form.cleaned_data['lugar_enlace']
            usuario_asignado = get_object_or_404(UsuarioBase, id=entrevistador)

            # Obtener instancias de los modelos relacionados
            asignacion_vacante = Cli056AplicacionVacante.objects.get(id=asignacion_id)
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

            contexto_email_1 = {
                'name' : f'{usuario_asignado.primer_nombre} {usuario_asignado.segundo_nombre} {usuario_asignado.primer_apellido}',
                'nombre_candidato' : f'{usuario_asignado.primer_nombre} {usuario_asignado.segundo_nombre} {usuario_asignado.primer_apellido}',
                'fecha_entrevista' : fecha_entrevista,
                'hora_entrevista' : hora_entrevista,
                'lugar_enlace' : lugar_enlace,
                'vacante' : vacante.titulo,
                'cliente' : cliente.razon_social,
            }

            # Envio de correo
            enviar_correo('asignacion_entrevista_entrevistador', contexto_email_1, f'Asginación de Entrevista ID: {asignacion_entrevista.id}', [usuario_asignado.email], correo_remitente=None)

            frase_aleatoria = 'Se ha asignado entrevista correctamente.'
            messages.success(request, frase_aleatoria)
            print('Llegamos bien!')
            return redirect('vacantes:vacante_gestion', pk=vacante.id)
            
        else:
            messages.error(request, 'Error al crear la asignación')
    else:
        form = EntrevistaCrearForm(grupo_id=4, cliente_id=cliente_id)

    contexto = {
        'form' : form,
        'aplicacion_entrevista': aplicacion_entrevista,
        'vacante': vacante,
        'EntrevistaForm': EntrevistaCrearForm,
    }

    return render(request, 'vacante/crear_entrevista.html', contexto)