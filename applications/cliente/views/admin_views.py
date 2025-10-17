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
from applications.usuarios.models import Permiso, UsuarioBase
from applications.cliente.models import Cli051Cliente, Cli064AsignacionCliente, Cli065ActividadEconomica,  Cli051ClientePoliticas, Cli067PoliticasInternas, Cli051ClientePruebas, Cli066PruebasPsicologicas, Cli068Cargo, Cli069Requisito, Cli070AsignacionRequisito, Cli071AsignacionPrueba

#form
from applications.vacante.forms.VacanteForms import VacanteForm
from ..forms.ClienteForms import ClienteForm, ClienteFormAsignacionCliente, ClienteFormAsignacionPrueba, ClienteFormEdit, ClienteFormPoliticas, ClienteFormPruebas, ClienteFormCargos, ClienteFormRequisitos, ClienteFormAsignacionRequisito

#query
from applications.services.service_client import query_client_all, query_client_detail


#views
@login_required
@validar_permisos('acceso_admin')
def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES)
        if form.is_valid():
            ClienteForm.logo = form.cleaned_data['logo']
            form.save()
            messages.success(request, 'Cliente Creado!')
            return redirect('clientes:cliente_ver')  # Cambia a la vista deseada después de guardar
        else:
            errores = "\n".join([f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()])
            messages.error(request, f"Errores en el formulario:\n{errores}")
            print("Errores en el formulario:", errores) 
    else:
        form = ClienteForm()
    
    context = {
        'form': form
    }
    return render(request, 'admin/client/admin_user/client_create.html', context)

# Mostrar todos los clientes todos
@login_required
@validar_permisos('acceso_admin')
def ver_cliente(request):
    cliente = query_client_all()
    clientes = cliente.filter(estado_id_001=1).order_by('-id')
    form_errors = False

    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES)
        if form.is_valid():
            ClienteForm.logo = form.cleaned_data['logo']
            form.save()
            messages.success(request, 'Cliente Creado!')
            return redirect('clientes:cliente_listar')  # Cambia a la vista deseada después de guardar
        else:
            form_errors = True
            form = ClienteForm(request.POST, request.FILES)
    else:
        form = ClienteForm()

    context = {
        'clientes': clientes,
        'form': form,
        'form_errors': form_errors,
        }
    
    return render(request, 'admin/client/admin_user/client_list.html', context)

# Mostrar todos los clientes todos
@login_required
@validar_permisos('acceso_admin', 'acceso_cliente')
def client_detail(request, pk):
    
    data = query_client_detail(pk)

    contexto = {
        'data' : data,
    }
    return render(request, 'admin/client/admin_user/client_detail.html', contexto)

#mostrar clientes asignados al cliente headhunter
@login_required
@validar_permisos('acceso_admin')
def client_detail_assigned(request, pk):
    data = query_client_detail(pk)

    # Filtra las asignaciones activas donde el cliente maestro es pk
    # Mostrar todos los clientes que tienen la asignación por el id maestro (pk)
    asignaciones_activas = Cli064AsignacionCliente.objects.filter(id_cliente_maestro=pk, estado__id=1)
    clientes_asignados = Cli051Cliente.objects.filter(id__in=asignaciones_activas.values_list('id_cliente_asignado', flat=True))


    form = ClienteFormAsignacionCliente()
    if request.method == 'POST':
        form = ClienteFormAsignacionCliente(request.POST, request.FILES)
        if form.is_valid():
            # form.save()
            # guardar el cliente asignado
            nit = form.cleaned_data['nit']
            cliente_asignado, created = Cli051Cliente.objects.get_or_create(
                nit=nit,
                defaults={
                    
                    'razon_social': form.cleaned_data['razon_social'],
                    'ciudad_id_004': Cat004Ciudad.objects.get(id=form.cleaned_data['ciudad_id_004']),
                    'email': form.cleaned_data.get('email', ''),
                    'contacto': form.cleaned_data.get('contacto', ''),
                    'telefono': form.cleaned_data.get('telefono', ''),
                    'perfil_empresarial': form.cleaned_data.get('perfil_empresarial', ''),
                    'logo': form.cleaned_data.get('logo'),
                    'actividad_economica': Cli065ActividadEconomica.objects.get(id=form.cleaned_data['actividad_economica']),
                    'tipo_cliente': 1,
                    'periodicidad_pago': form.cleaned_data['periodicidad_pago'],
                    # 'referencias_laborales': form.cleaned_data['referencias_laborales'],
                    'cantidad_colaboradores': form.cleaned_data['cantidad_colaboradores'],
                    'contacto_cargo': form.cleaned_data['contacto_cargo'],
                    'direccion_cargo': form.cleaned_data['direccion_cargo'],
                    'estado_id_001': Cat001Estado.objects.get(id=1),
                }
            )

            cliente_asignado = Cli051Cliente.objects.get(nit=nit)

            # guardar la asignación
            cliente_maestro = Cli051Cliente.objects.get(id=pk)
            asignacion_cliente = Cli064AsignacionCliente(
                id_cliente_maestro=cliente_maestro,
                id_cliente_asignado=cliente_asignado,
                tipo_asignacion='2',
                estado=Cat001Estado.objects.get(id=1)
            )
            asignacion_cliente.save()

            messages.success(request, 'Cliente Asignado!')
            return redirect('clientes:client_detail_assigned', pk=pk)
        else:
            messages.error(request, form.errors)
            print("Errores en el formulario:", form.errors)
    else:
        form = ClienteFormAsignacionCliente()

    
    contexto = {
        'data' : data,
        'clientes_asignados': clientes_asignados,
        'form': form,
    }
    return render(request, 'admin/client/admin_user/client_detail_assigned.html', contexto)

#mostrar información del cliente a editar
@login_required
@validar_permisos('acceso_admin', 'acceso_cliente')
def client_detail_info(request, pk):
    # Data cliente a mostrar
    data = query_client_detail(pk)

    cliente = Cli051Cliente.objects.get(id=pk)
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
        # 'referencias_laborales': cliente.referencias_laborales,
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
            # cliente.referencias_laborales = form_cliente.cleaned_data['referencias_laborales']
            cliente.cantidad_colaboradores = form_cliente.cleaned_data['cantidad_colaboradores']
            cliente.contacto_cargo = form_cliente.cleaned_data['contacto_cargo']
            cliente.direccion_cargo = form_cliente.cleaned_data['direccion_cargo']

            # Manejo del campo logo (imagen)
            if form_cliente.cleaned_data.get('logo'):
                cliente.logo = form_cliente.cleaned_data['logo']

            cliente.save()

            messages.success(request, 'El cliente ha sido actualizado con éxito.')
            return redirect('clientes:cliente_info', pk=cliente.id)

        else:
            messages.error(request, form_cliente.errors)  
    else:
        form_cliente = ClienteFormEdit(initial=initial_data)
    
    contexto = {
        'data' : data,
        'form_cliente': form_cliente,
    }
    return render(request, 'admin/client/admin_user/client_detail_info.html', contexto)

#mostrar información del cliente de sus politicas
@login_required
@validar_permisos('acceso_admin', 'acceso_cliente')
def client_detail_politics(request, pk):

    # Data cliente a mostrar
    data = query_client_detail(pk)

    # Obtener las políticas del cliente
    politicas_cliente = Cli051ClientePoliticas.objects.filter(cliente_id=pk)
    form = ClienteFormPoliticas()

    if request.method == 'POST':
        form = ClienteFormPoliticas(request.POST, cliente_id=pk)
        if form.is_valid():
            politica = form.cleaned_data['politicas']
            politica_cliente = Cli051ClientePoliticas(
                cliente=Cli051Cliente.objects.get(id=pk),
                politica_interna=Cli067PoliticasInternas.objects.get(id=politica),
                estado = Cat001Estado.objects.get(id=1)
            )
            politica_cliente.save()

            messages.success(request, 'Las políticas han sido asignadas con éxito.')
            return redirect('clientes:cliente_politicas', pk=pk)

        else:
            messages.error(request, form.errors)
            print("Errores en el formulario:", form.errors)
    else:
        form = ClienteFormPoliticas(cliente_id=pk)
        

    contexto = {
        'data': data,
        'politicas_cliente': politicas_cliente,
        'form': form,
    }

    return render(request, 'admin/client/admin_user/client_detail_politics.html', contexto)

#mostrar información del cliente de sus pruebas
@login_required
@validar_permisos('acceso_admin', 'acceso_cliente')
def client_detail_test(request, pk):
    # Data cliente a mostrar
    data = query_client_detail(pk)

    # Obtener las pruebas del cliente
    pruebas_cliente = Cli051ClientePruebas.objects.filter(cliente_id=pk)
    form = ClienteFormPruebas()

    if request.method == 'POST':
        form = ClienteFormPruebas(request.POST, cliente_id=pk)
        if form.is_valid():
            prueba = form.cleaned_data['pruebas']
            prueba_cliente = Cli051ClientePruebas(
                cliente=Cli051Cliente.objects.get(id=pk),
                prueba_psicologica=Cli066PruebasPsicologicas.objects.get(id=prueba),
                estado=Cat001Estado.objects.get(id=1)
            )
            prueba_cliente.save()

            messages.success(request, 'Las pruebas han sido asignadas con éxito.')
            return redirect('clientes:cliente_pruebas', pk=pk)

        else:
            messages.error(request, form.errors)
            print("Errores en el formulario:", form.errors)
    else:
        form = ClienteFormPruebas(cliente_id=pk)

    contexto = {
        'data': data,
        'pruebas_cliente': pruebas_cliente,
        'form': form,
    }

    return render(request, 'admin/client/admin_user/client_detail_test.html', contexto)

#mostrar información del cliente de sus pruebas
@login_required
@validar_permisos('acceso_admin', 'acceso_cliente')
def client_detail_position(request, pk):
    # Data cliente a mostrar
    data = query_client_detail(pk)

    # Obtener los cargos del cliente
    position_client = Cli068Cargo.objects.filter(cliente_id=pk)

    if request.method == 'POST':
        form = ClienteFormCargos(request.POST, cliente_id=pk)
        if form.is_valid():
            try:
                cargo = form.cleaned_data['cargo'].upper()
                referencias_laborales = form.cleaned_data['referencias_laborales']
                
                cargo_cliente = Cli068Cargo.objects.create(
                    cliente=Cli051Cliente.objects.get(id=pk),
                    nombre_cargo=cargo,
                    referencias_laborales=referencias_laborales,
                    estado=Cat001Estado.objects.get(id=1)
                )

                messages.success(request, 'El cargo ha sido creado con éxito.')
                return redirect('clientes:cliente_cargos', pk=pk)
            except Exception as e:
                messages.error(request, f'Error al crear el cargo: {str(e)}')
        else:
            # Mostrar errores de validación específicos
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            print("Errores en el formulario:", form.errors)
    else:
        form = ClienteFormCargos(cliente_id=pk)

    contexto = {
        'data': data,
        'position_client': position_client,
        'form': form,     
    }

    return render(request, 'admin/client/admin_user/client_detail_position.html', contexto)

#mostrar información del cliente de sus pruebas y requisitos
@login_required
@validar_permisos('acceso_admin', 'acceso_cliente')
def client_detail_position_config(request, pk, cargo_id):
    # Data cliente a mostrar
    data = query_client_detail(pk)

    # Obtener el cargo específico del cliente
    cargo_cliente = get_object_or_404(Cli068Cargo, id=cargo_id)

    # Obtener las asignaciones de requisitos y pruebas del cargo
    asignaciones_requisitos = Cli070AsignacionRequisito.objects.filter(cargo=cargo_id, cargo__cliente_id=pk)
    asignaciones_pruebas = Cli071AsignacionPrueba.objects.filter(
        cargo_id=cargo_id, 
        cliente_prueba__cliente__id=pk
    )

    # Formularios para editar cargo, asignar requisitos y pruebas
    form_cargo = ClienteFormCargos(cliente_id=pk, cargo_id=cargo_id)
    form_requisitos = ClienteFormAsignacionRequisito(cliente_id=pk, cargo_id=cargo_id)
    form_pruebas = ClienteFormAsignacionPrueba(cliente_id=pk, cargo_id=cargo_id)
    
    if request.method == 'POST':
        # Determinar qué formulario se está enviando
        if 'edit_cargo' in request.POST:
            form_cargo = ClienteFormCargos(request.POST, cliente_id=pk, cargo_id=cargo_id)
            if form_cargo.is_valid():
                try:
                    cargo = form_cargo.cleaned_data['cargo'].upper()
                    referencias_laborales = form_cargo.cleaned_data['referencias_laborales']
                    
                    # Actualizar cargo existente
                    cargo_obj = Cli068Cargo.objects.get(id=cargo_id)
                    cargo_obj.nombre_cargo = cargo
                    cargo_obj.referencias_laborales = referencias_laborales
                    cargo_obj.save()
                    
                    messages.success(request, 'El cargo ha sido actualizado con éxito.')
                    return redirect('clientes:cliente_cargos_configuracion', pk=pk, cargo_id=cargo_id)
                except Exception as e:
                    messages.error(request, f'Error al actualizar el cargo: {str(e)}')
            else:
                # Mostrar errores de validación específicos
                for field, errors in form_cargo.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
                print("Errores en el formulario de cargo:", form_cargo.errors)
        
        elif 'assign_requisito' in request.POST:
            form_requisitos = ClienteFormAsignacionRequisito(request.POST, cliente_id=pk, cargo_id=cargo_id)
            if form_requisitos.is_valid():
                requisito = form_requisitos.cleaned_data['requisito']
                Cli070AsignacionRequisito.objects.create(
                    cargo=Cli068Cargo.objects.get(id=cargo_id), 
                    requisito=Cli069Requisito.objects.get(id=requisito),
                    estado=Cat001Estado.objects.get(id=1)
                )
                messages.success(request, 'El requisito ha sido asignado con éxito.')
                return redirect('clientes:cliente_cargos_configuracion', pk=pk, cargo_id=cargo_id)
        
        elif 'assign_prueba' in request.POST:
            form_pruebas = ClienteFormAsignacionPrueba(request.POST, cliente_id=pk, cargo_id=cargo_id)
            if form_pruebas.is_valid():
                prueba = form_pruebas.cleaned_data['prueba']
                asignacion_prueba = Cli051ClientePruebas.objects.get(prueba_psicologica=prueba, cliente=pk)
                Cli071AsignacionPrueba.objects.create(
                    cargo=Cli068Cargo.objects.get(id=cargo_id),
                    cliente_prueba=Cli051ClientePruebas.objects.get(id=asignacion_prueba.id),
                    estado=Cat001Estado.objects.get(id=1)
                )
                messages.success(request, 'La prueba ha sido asignada con éxito.')
                return redirect('clientes:cliente_cargos_configuracion', pk=pk, cargo_id=cargo_id)
    else:
        form_cargo = ClienteFormCargos(cliente_id=pk, cargo_id=cargo_id)
        form_requisitos = ClienteFormAsignacionRequisito(cliente_id=pk, cargo_id=cargo_id)
        form_pruebas = ClienteFormAsignacionPrueba(cliente_id=pk, cargo_id=cargo_id)

    contexto = {
        'data': data,
        'cargo_cliente': cargo_cliente,
        'asignaciones_requisitos': asignaciones_requisitos,
        'asignaciones_pruebas': asignaciones_pruebas,
        'form_cargo': form_cargo,
        'form_requisitos': form_requisitos,
        'form_pruebas': form_pruebas,
    }

    return render(request, 'admin/client/admin_user/client_detail_position_config.html', contexto)

@login_required
@validar_permisos('acceso_admin', 'acceso_cliente')
def client_detail_position_required_delete(request, pk, cargo_id):

    # Obtener la asignación de requisito individual por su id
    asignacion_requisito = Cli070AsignacionRequisito.objects.get(id=pk)
    cliente_id = asignacion_requisito.cargo.cliente.id
    
    # Eliminar la asignación específica
    asignacion_requisito.delete()

    messages.success(request, 'El requisito ha sido eliminado con éxito.')
    return redirect('clientes:cliente_cargos_configuracion', pk=cliente_id, cargo_id=cargo_id)

@login_required
@validar_permisos('acceso_admin', 'acceso_cliente')
def client_detail_position_test_delete(request, pk, cargo_id):
    
    # Obtener la asignación de prueba individual por su id
    asignacion_prueba = Cli071AsignacionPrueba.objects.get(id=pk)
    cliente_id = asignacion_prueba.cargo.cliente.id
    
    # Eliminar la asignación específica
    asignacion_prueba.delete()
    messages.success(request, 'La prueba ha sido eliminada con éxito.')
    return redirect('clientes:cliente_cargos_configuracion', pk=cliente_id, cargo_id=cargo_id)

#mostrar información de los requisitos del clinete
@login_required
@validar_permisos('acceso_admin', 'acceso_cliente')
def client_detail_required(request, pk):
    # Data cliente a mostrar
    data = query_client_detail(pk)

    # Obtener los requisitos del cliente
    requisitos_cliente = Cli069Requisito.objects.filter(cliente=pk)

    form = ClienteFormRequisitos()

    if request.method == 'POST':
        form = ClienteFormRequisitos(request.POST, cliente_id=pk)
        if form.is_valid():
            requisito = form.cleaned_data['requisitos']
            descripcion = form.cleaned_data['descripcion']
            requisito_cliente = Cli069Requisito(
                cliente=Cli051Cliente.objects.get(id=pk),
                descripcion=descripcion,
                estado=Cat001Estado.objects.get(id=1),
                nombre=requisito.upper()
            )
            requisito_cliente.save()

            messages.success(request, 'Los requisitos han sido asignados con éxito.')
            return redirect('clientes:cliente_requisitos', pk=pk)

        else:
            messages.error(request, form.errors)
            print("Errores en el formulario:", form.errors)
    else:
        form = ClienteFormRequisitos(cliente_id=pk)

    contexto = {
        'data': data,
        'requisitos_cliente': requisitos_cliente,
        'form': form,
    }

    return render(request, 'admin/client/admin_user/client_detail_required.html', contexto)


@login_required
@validar_permisos('acceso_admin', 'acceso_cliente')
def client_detail_group_work(request, pk):

    # Data cliente a mostrar
    data = query_client_detail(pk)
    cliente_id = request.session.get('cliente_id')
    # Obtener los usuarios internos del cliente
    users_list = UsuarioBase.objects.filter(cliente_id_051=pk, group_id__in=[3, 4])
    contexto = {
        'data': data,
        'users_list': users_list,
    }

    return render(request, 'admin/client/admin_user/client_detail_group_work.html', contexto)
