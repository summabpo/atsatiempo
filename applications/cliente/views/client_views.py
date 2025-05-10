from datetime import timezone
from django.shortcuts import render, redirect # type: ignore
import json
from django.contrib import messages # type: ignore
from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.http import JsonResponse # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from applications.usuarios.decorators  import validar_permisos

#model
from applications.vacante.models import Cli052Vacante, Cli055ProfesionEstudio, Cli053SoftSkill, Cli052VacanteSoftSkillsId053, Cli054HardSkill, Cli052VacanteHardSkillsId054
from applications.reclutado.models import Cli056AplicacionVacante
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.usuarios.models import Permiso
from applications.cliente.models import Cli051Cliente, Cli064AsignacionCliente, Cli065ActividadEconomica,  Cli051ClientePoliticas, Cli067PoliticasInternas, Cli051ClientePruebas, Cli066PruebasPsicologicas, Cli068Cargo, Cli069Requisito, Cli070AsignacionRequisito, Cli071AsignacionPrueba

#form
from applications.vacante.forms.VacanteForms import VacanteForm
from ..forms.ClienteForms import ClienteForm, ClienteFormAsignacionPrueba, ClienteFormEdit, ClienteFormPoliticas, ClienteFormPruebas, ClienteFormCargos, ClienteFormRequisitos, ClienteFormAsignacionRequisito

#query
from applications.services.service_client import query_client_all, query_client_detail


#mostrar información del cliente a editar
@login_required
@validar_permisos('acceso_cliente')
def client_detail_info(request):

    cliente_id = request.session.get('cliente_id')

    # Data cliente a mostrar
    data = query_client_detail(cliente_id)

    cliente = Cli051Cliente.objects.get(id=cliente_id)
    # Define los datos iniciales que quieres pasar al formulario
    initial_data = {
        'estado_id_001': cliente.estado_id_001.id if cliente.estado_id_001 else '',
        'nit': cliente.nit,
        'razon_social': cliente.razon_social,
        'ciudad_id_004': cliente.ciudad_id_004.id if cliente.ciudad_id_004 else '',
        'email': cliente.email,
        'contacto': cliente.contacto,
        'telefono': cliente.telefono,
        'perfil_empresarial': cliente.perfil_empresarial,
        'logo': cliente.logo.url if cliente.logo else '',
        'tipo_cliente': cliente.tipo_cliente,
        'actividad_economica': cliente.actividad_economica.id if cliente.actividad_economica else '',
        'periodicidad_pago': cliente.periodicidad_pago,
        'referencias_laborales': cliente.referencias_laborales,
        'cantidad_colaboradores': cliente.cantidad_colaboradores,
        'contacto_cargo': cliente.contacto_cargo,
        'direccion_cargo': cliente.direccion_cargo,
    }

    form_cliente = ClienteFormEdit(initial=initial_data)

    #logica para mostrar el form
    if request.method == 'POST':
        form_cliente = ClienteFormEdit(request.POST, request.FILES)
        if form_cliente.is_valid():
            cliente.razon_social = form_cliente.cleaned_data['razon_social']
            cliente.nit = form_cliente.cleaned_data['nit']
            cliente.email = form_cliente.cleaned_data['email']
            cliente.contacto = form_cliente.cleaned_data['contacto']
            cliente.telefono = form_cliente.cleaned_data['telefono']
            cliente.perfil_empresarial = form_cliente.cleaned_data['perfil_empresarial']
            cliente.ciudad_id_004 = Cat004Ciudad.objects.get(id=form_cliente.cleaned_data['ciudad_id_004'])
            cliente.tipo_cliente = form_cliente.cleaned_data['tipo_cliente']
            cliente.actividad_economica = Cli065ActividadEconomica.objects.get(id=form_cliente.cleaned_data['actividad_economica'])
            cliente.periodicidad_pago = form_cliente.cleaned_data['periodicidad_pago']
            cliente.referencias_laborales = form_cliente.cleaned_data['referencias_laborales']
            cliente.cantidad_colaboradores = form_cliente.cleaned_data['cantidad_colaboradores']
            cliente.contacto_cargo = form_cliente.cleaned_data['contacto_cargo']
            cliente.direccion_cargo = form_cliente.cleaned_data['direccion_cargo']

            # Manejo del campo logo (imagen)
            if form_cliente.cleaned_data.get('logo'):
                cliente.logo = form_cliente.cleaned_data['logo']

            cliente.save()

            messages.success(request, 'El cliente ha sido actualizado con éxito.')
            return redirect('clientes:info_principal_cliente')

        else:
            messages.error(request, form_cliente.errors)  
    else:
        form_cliente = ClienteFormEdit(initial=initial_data)
    
    contexto = {
        'data' : data,
        'form_cliente': form_cliente,
    }
    return render(request, 'admin/client/client_user/client_info.html', contexto)

#mostrar información del cliente de sus pruebas
@login_required
@validar_permisos('acceso_cliente')
def client_position(request):

    cliente_id = request.session.get('cliente_id')

    # Data cliente a mostrar
    data = query_client_detail(cliente_id)

    # Obtener los cargos del cliente
    position_client = Cli068Cargo.objects.filter(cliente_id=cliente_id)

    if request.method == 'POST':
        form = ClienteFormCargos(request.POST, cliente_id=cliente_id)
        if form.is_valid():
            cargo = form.cleaned_data['cargo']
            cargo_cliente = Cli068Cargo(
                cliente=Cli051Cliente.objects.get(id=cliente_id),
                nombre_cargo=cargo.upper(),
                estado=Cat001Estado.objects.get(id=1)
            )
            cargo_cliente.save()

            messages.success(request, 'Los cargos han sido asignados con éxito.')
            return redirect('clientes:cargos_cliente')

        else:
            messages.error(request, form.errors)
            print("Errores en el formulario:", form.errors)
    else:
        form = ClienteFormCargos(cliente_id=cliente_id)

    contexto = {
        'data': data,
        'position_client': position_client,
        'form': form,     
    }

    return render(request, 'admin/client/client_user/client_position.html', contexto)

#mostrar información del cliente de sus pruebas
@login_required
@validar_permisos('acceso_cliente')
def client_test(request):

    cliente_id = request.session.get('cliente_id')

    # Data cliente a mostrar
    data = query_client_detail(cliente_id)

    # Obtener las pruebas del cliente
    pruebas_cliente = Cli051ClientePruebas.objects.filter(cliente_id=cliente_id)
    form = ClienteFormPruebas()

    if request.method == 'POST':
        form = ClienteFormPruebas(request.POST, cliente_id=cliente_id)
        if form.is_valid():
            prueba = form.cleaned_data['pruebas']
            prueba_cliente = Cli051ClientePruebas(
                cliente=Cli051Cliente.objects.get(id=cliente_id),
                prueba_psicologica=Cli066PruebasPsicologicas.objects.get(id=prueba),
                estado=Cat001Estado.objects.get(id=1)
            )
            prueba_cliente.save()

            messages.success(request, 'Las pruebas han sido creadas con éxito.')
            return redirect('clientes:pruebas_cliente')

        else:
            messages.error(request, form.errors)
            print("Errores en el formulario:", form.errors)
    else:
        form = ClienteFormPruebas(cliente_id=cliente_id)

    contexto = {
        'data': data,
        'pruebas_cliente': pruebas_cliente,
        'form': form,
    }

    return render(request, 'admin/client/client_user/client_test.html', contexto)

#mostrar información del cliente de sus politicas
@login_required
@validar_permisos('acceso_cliente')
def client_politics(request):

    cliente_id = request.session.get('cliente_id')

    # Data cliente a mostrar
    data = query_client_detail(cliente_id)

    # Obtener las políticas del cliente
    politicas_cliente = Cli051ClientePoliticas.objects.filter(cliente_id=cliente_id)
    form = ClienteFormPoliticas()

    if request.method == 'POST':
        form = ClienteFormPoliticas(request.POST, cliente_id=cliente_id)
        if form.is_valid():
            politica = form.cleaned_data['politicas']
            politica_cliente = Cli051ClientePoliticas(
                cliente=Cli051Cliente.objects.get(id=cliente_id),
                politica_interna=Cli067PoliticasInternas.objects.get(id=politica),
                estado = Cat001Estado.objects.get(id=1)
            )
            politica_cliente.save()

            messages.success(request, 'Las políticas han sido asignadas con éxito.')
            return redirect('clientes:politicas_cliente')

        else:
            messages.error(request, form.errors)
            print("Errores en el formulario:", form.errors)
    else:
        form = ClienteFormPoliticas(cliente_id=cliente_id)
        

    contexto = {
        'data': data,
        'politicas_cliente': politicas_cliente,
        'form': form,
    }

    return render(request, 'admin/client/client_user/client_politics.html', contexto)

#mostrar información de los requisitos del clinete
@login_required
@validar_permisos('acceso_cliente')
def client_required(request):

    cliente_id = request.session.get('cliente_id')

    # Data cliente a mostrar
    data = query_client_detail(cliente_id)

    # Obtener los requisitos del cliente
    requisitos_cliente = Cli069Requisito.objects.filter(cliente=cliente_id)

    form = ClienteFormRequisitos()

    if request.method == 'POST':
        form = ClienteFormRequisitos(request.POST, cliente_id=cliente_id)
        if form.is_valid():
            requisito = form.cleaned_data['requisitos']
            descripcion = form.cleaned_data['descripcion']
            requisito_cliente = Cli069Requisito(
                cliente=Cli051Cliente.objects.get(id=cliente_id),
                descripcion=descripcion,
                estado=Cat001Estado.objects.get(id=1),
                nombre=requisito.upper()
            )
            requisito_cliente.save()

            messages.success(request, 'Los requisitos han sido asignados con éxito.')
            return redirect('clientes:requisitos_cliente')

        else:
            messages.error(request, form.errors)
            print("Errores en el formulario:", form.errors)
    else:
        form = ClienteFormRequisitos(cliente_id=cliente_id)

    contexto = {
        'data': data,
        'requisitos_cliente': requisitos_cliente,
        'form': form,
    }

    return render(request, 'admin/client/client_user/client_required.html', contexto)

#mostrar información del cliente de sus pruebas y requisitos
@login_required
@validar_permisos('acceso_cliente')
def client_position_config(request, cargo_id):

    cliente_id = request.session.get('cliente_id')

    # Data cliente a mostrar
    data = query_client_detail(cliente_id)

    # Obtener el cargo específico del cliente
    cargo_cliente = get_object_or_404(Cli068Cargo, id=cargo_id)

    # Obtener las asignaciones de requisitos y pruebas del cargo
    asignaciones_requisitos = Cli070AsignacionRequisito.objects.filter(cargo=cargo_id, cargo__cliente_id=cliente_id)
    asignaciones_pruebas = Cli071AsignacionPrueba.objects.filter(
        cargo_id=cargo_id, 
        cliente_prueba__cliente__id=cliente_id
    )

    form = ClienteFormAsignacionRequisito(cliente_id=cliente_id, cargo_id=cargo_id)
    form1 = ClienteFormAsignacionPrueba(cliente_id=cliente_id, cargo_id=cargo_id)

    if request.method == 'POST':
        form = ClienteFormAsignacionRequisito(request.POST, cliente_id=cliente_id, cargo_id=cargo_id)
        form1 = ClienteFormAsignacionPrueba(request.POST, cliente_id=cliente_id, cargo_id=cargo_id)
        
        if form.is_valid():
            requisito = form.cleaned_data['requisito']
            Cli070AsignacionRequisito.objects.create(
                cargo=Cli068Cargo.objects.get(id=cargo_id), 
                requisito=Cli069Requisito.objects.get(id=requisito),
                estado=Cat001Estado.objects.get(id=1)
            )
            messages.success(request, 'El requisito ha sido asignado con éxito.')
        
        if form1.is_valid():
            prueba = form1.cleaned_data['prueba']
            asignacion_prueba = Cli051ClientePruebas.objects.get(prueba_psicologica=prueba, cliente=cliente_id)
            Cli071AsignacionPrueba.objects.create(
                cargo=Cli068Cargo.objects.get(id=cargo_id),
                cliente_prueba=Cli051ClientePruebas.objects.get(id=asignacion_prueba.id),
                estado=Cat001Estado.objects.get(id=1)
            )
            messages.success(request, 'La prueba ha sido asignada con éxito.')
        
        if form.is_valid() or form1.is_valid():
            return redirect('clientes:cargos_cliente_detalle', cargo_id=cargo_id)
        else:
            messages.error(request, form.errors)
            print("Errores en el formulario:", form.errors)
    else:
        form = ClienteFormAsignacionRequisito(cliente_id=cliente_id, cargo_id=cargo_id)
        form1 = ClienteFormAsignacionPrueba(cliente_id=cliente_id, cargo_id=cargo_id)

    contexto = {
        'data': data,
        'cargo_cliente': cargo_cliente,
        'asignaciones_requisitos': asignaciones_requisitos,
        'asignaciones_pruebas': asignaciones_pruebas,
        'form': form,
        'form1': form1,
    }

    return render(request, 'admin/client/client_user/client_position_config.html', contexto)

