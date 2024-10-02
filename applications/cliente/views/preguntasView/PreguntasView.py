from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from applications.usuarios.decorators  import validar_permisos

#modelos
from applications.usuarios.models import Permiso
from applications.cliente.models import Cli058Pregunta, Cli059Cuestionario, Cli060CuestionarioPregunta

@login_required
@validar_permisos(*Permiso.obtener_nombres())
def ver_preguntas_cliente(request):
    #obtenemos el cliente actual
    cliente_id = request.session.get('cliente_id')

    preguntas = Cli058Pregunta.objects.filter(cliente = cliente_id, estado = 1)

    contexto = {
        'preguntas' : preguntas,
    }

    return render(request, 'cliente/cuestionarios/ver_preguntas.html', contexto)