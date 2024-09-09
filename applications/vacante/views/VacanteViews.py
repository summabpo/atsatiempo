from django.shortcuts import render, redirect, get_object_or_404
from applications.cliente.models import Cli051Cliente
from applications.vacante.forms.VacanteForms import VacanteForm
from applications.vacante.models import Cli052Vacante, Cli055ProfesionEstudio, Cli053SoftSkill, Cli054HardSkill, Cli052VacanteHardSkillsId054, Cli052VacanteSoftSkillsId053
from applications.common.models import Cat001Estado, Cat004Ciudad
from django.contrib import messages
from django.http import JsonResponse
import json

def vacante_cliente_mostrar(request, pk=None):
    #datos clientes
    cliente = get_object_or_404(Cli051Cliente, pk=pk)
    #estado_general_vacante
    estado = Cat001Estado.objects.get(id=1)
    #listado vacantes activas
    vacantes = Cli052Vacante.objects.filter(cliente_id_051=cliente.id, estado_id_001=1).order_by('-id')

    print(vacantes)

    form_errors = False

    # Formulario Vacantes
    if request.method == 'POST': 
        form = VacanteForm(request.POST)
        
        if form.is_valid():
            #datos formulario

            titulo = form.cleaned_data['titulo']
            numero_posiciones = form.cleaned_data['numero_posiciones']
            profesion_estudio_id_055 = form.cleaned_data['profesion_estudio_id_055']
            experiencia_requerida = form.cleaned_data['experiencia_requerida']
            soft_skills_id_053 = form.cleaned_data['soft_skills_id_053']
            hard_skills_id_054 = form.cleaned_data['hard_skills_id_054']
            funciones_responsabilidades = form.cleaned_data['funciones_responsabilidades']
            salario = form.cleaned_data['salario']

            estado_id = Cat001Estado.objects.get(id=1)
            ciudad_id = Cat004Ciudad.objects.get(id=form.cleaned_data['ciudad'])

            print(profesion_estudio_id_055)

            # Intentar obtener el objeto profesion estudio
            profesion_estudio_dato, created = Cli055ProfesionEstudio.objects.get_or_create(
                nombre = profesion_estudio_id_055,
                defaults={'estado_id_001': estado}
            )

            print(profesion_estudio_dato)

            #crea la vacante
            vacante_creada = Cli052Vacante.objects.create(
                titulo = titulo,
                numero_posiciones = numero_posiciones,
                experiencia_requerida = experiencia_requerida,
                funciones_responsabilidades = funciones_responsabilidades,
                salario = salario,
                estado_vacante = 1,
                ciudad_id = ciudad_id.id,
                cliente_id_051_id = cliente.id,
                estado_id_001_id = estado_id.id,
                profesion_estudio_id_055_id = profesion_estudio_dato.id,
            )



            # Convertir el string JSON en un objeto Python (lista de diccionarios)
            skills = json.loads(soft_skills_id_053)
            
            # Ahora puedes iterar sobre la lista de diccionarios
            for skill in skills:
                print(skill['value'])  # Aquí puedes hacer lo que necesites con cada valor

                # Intentar obtener el objeto soft_skills
                soft_skills, created = Cli053SoftSkill.objects.get_or_create(
                    nombre = skill['value'],
                    defaults={'estado_id_001': estado}
                )

                Cli052VacanteSoftSkillsId053.objects.create(
                    cli052vacante=vacante_creada,
                    cli053softskill=soft_skills
                )


            # Convertir el string JSON en un objeto Python (lista de diccionarios)
            skills = json.loads(hard_skills_id_054)
            
            # Ahora puedes iterar sobre la lista de diccionarios
            for skill in skills:
                print(skill['value'])  # Aquí puedes hacer lo que necesites con cada valor

                # Intentar obtener el objeto hard_skills
                hard_skills, created = Cli054HardSkill.objects.get_or_create(
                    nombre = skill['value'],
                    defaults={'estado_id_001': estado}
                )

                Cli052VacanteHardSkillsId054.objects.create(
                    cli052vacante=vacante_creada,
                    cli054hardskill=hard_skills
                )

            messages.success(request, 'El registro de la vacante ha sido creado con éxito.')
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