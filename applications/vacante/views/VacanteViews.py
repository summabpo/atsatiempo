from django.shortcuts import render, redirect, get_object_or_404
from applications.cliente.models import Cli051Cliente
from applications.vacante.forms.VacanteForms import VacanteForm
from applications.vacante.models import Cli052Vacante, Cli055ProfesionEstudio, Cli053SoftSkill, Cli054HardSkill
from applications.common.models import Cat001Estado, Cat004Ciudad
from django.contrib import messages
from django.http import JsonResponse

def vacante_cliente_mostrar(request, pk=None):
    #datos clientes
    cliente = get_object_or_404(Cli051Cliente, pk=pk)
    #estado_general_vacante
    estado = Cat001Estado.objects.get(id=1)
    #listado vacantes activas
    vacantes = Cli052Vacante.objects.filter(cliente_id_051=cliente.id, estado_id_001=1).order_by('-id')

    form_errors = False

    # Formulario Vacantes
    if request.method == 'POST': 
        form = VacanteForm(request.POST)
        
        if form.is_valid():
            #datos formulario

            titulo = form.cleaned_data['titulo']
            numero_posiciones = form.cleaned_data['numero_posiciones']
            profesion_estudio_id_055 = form.cleaned_data['profesion_estudio_id_055']
            soft_skills_id_053 = form.cleaned_data['soft_skills_id_053']
            hard_skills_id_054 = form.cleaned_data['hard_skills_id_054']
            funciones_responsabilidades = form.cleaned_data['funciones_responsabilidades']
            ciudad = form.cleaned_data['ciudad']
            salario = form.cleaned_data['salario']

            print(f'Skillis: {soft_skills_id_053}')

            # Intentar obtener el objeto profesion estudio
            profesion_estudio_dato, created = Cli055ProfesionEstudio.objects.get_or_create(
                nombre = profesion_estudio_id_055,
                defaults={'estado_id_001': estado}
            )

            # Intentar obtener el objeto soft_skills
            soft_skills, created = Cli053SoftSkill.objects.get_or_create(
                nombre = soft_skills_id_053,
                defaults={'estado_id_001': estado}
            )

            # Intentar obtener el objeto hard_skills
            hard_skills, created = Cli054HardSkill.objects.get_or_create(
                nombre = hard_skills_id_054,
                defaults={'estado_id_001': estado}
            )

            #crea la vacante
            # vacante_creada = Cli052Vacante.objects.create(
            #     titulo = titulo,
            #     numero_posiciones = numero_posiciones,
            #     profesion_estudio_id_055 = profesion_estudio_dato
            #     experiencia_requerida = experiencia_requerida
            #     soft_skills_id_053 = soft_skills,
            #     hard_skills_id_054 = hard_skills,
            #     funciones_responsabilidades = funciones_responsabilidades,
            #     ciudad = ciudad,
            #     salario = salario
            #     estado_vacante
            #     estado_id_001 
            #     cliente_id_051
            #     fecha_creacion
            # )

            # form.save()
            messages.success(request, 'El registro de experiencia academica ha sido creado')
            return redirect('vacantes:vacantes_cliente', pk=cliente.id)
        else:
            form_errors = True
            messages.error(request, form.errors)
    else:
        form = VacanteForm()
        vacantes = Cli052Vacante.objects.filter(cliente_id_051=cliente.id, estado_id_001=1).order_by('-id')

    return render(request, 'vacante/listado_vacantes_cliente.html',
        { 
            'form': form,
            'vacantes': vacantes,
            'cliente': cliente,
            'form_errors': form_errors,
        })    