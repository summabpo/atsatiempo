from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from applications.usuarios.decorators  import validar_permisos
from django.contrib import messages

#modelos
from applications.usuarios.models import Permiso
from applications.cliente.models import Cli058Pregunta, Cli059Cuestionario, Cli060CuestionarioPregunta, Cli051Cliente
from applications.common.models import Cat001Estado

#forms
from applications.cliente.forms.preguntasForm.PreguntasForm import PreguntasFormCliente

@login_required
@validar_permisos(*Permiso.obtener_nombres())
def ver_preguntas_cliente(request):
    #obtenemos el cliente actual
    cliente_id = request.session.get('cliente_id')

    preguntas = Cli058Pregunta.objects.filter(cliente = cliente_id, estado = 1)

    if request.method == 'POST':
        form = PreguntasFormCliente(request.POST)
        if form.is_valid():
            pregunta_cliente = form.cleaned_data['pregunta_cliente']
            respuesta = form.cleaned_data['respuesta']
            pregunta_correlacion = form.cleaned_data['pregunta_correlacion']

            cliente = Cli051Cliente.objects.get(id=cliente_id)  

            pregunta = Cli058Pregunta.objects.create(
                cliente=cliente,
                pregunta=pregunta_cliente,
                respuesta=respuesta,
                pregunta_correlacion=pregunta_correlacion,
            )


            messages.success(request, f'Se ha creado la pregunta: {pregunta.pregunta}')
            return redirect('clientes:ver_preguntas_cliente')  

        else:
            messages.error(request, 'Error al crear  la pregunta')

    else:
        form = PreguntasFormCliente()
    contexto = {
        'preguntas' : preguntas,
        'form' : form,
    }

    return render(request, 'cliente/cuestionarios/ver_preguntas.html', contexto)