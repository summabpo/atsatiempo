from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from applications.usuarios.decorators  import validar_permisos
from django.contrib import messages
from applications.common.views.EnvioCorreo import enviar_correo, generate_token
from django.db.models import F

#formularios
from applications.vacante.forms.EntrevistaForm import EntrevistaCrearForm

#modelos
from applications.vacante.models import Cli057AsignacionEntrevista, Cli056AplicacionVacante, Cli052Vacante
from applications.cliente.models import Cli051Cliente
from applications.usuarios.models import Permiso
from applications.usuarios.models import UsuarioBase
from applications.common.models import Cat001Estado
from applications.candidato.models import Can101Candidato

#consultas
from applications.vacante.views.consultas.VacanteConsultaView import consulta_vacantes_disponibles

# Ver entrevistas generadas por cliente
@login_required
@validar_permisos(*Permiso.obtener_nombres())
def ver_vacante_disponibles(request):
    candidato_id = request.session.get('candidato_id')
    vacantes = consulta_vacantes_disponibles(candidato_id)

    contexto = {
        'vacantes' : vacantes
    }
    
    return render(request, 'vacante/ver_vacantes_disponibles.html', contexto)