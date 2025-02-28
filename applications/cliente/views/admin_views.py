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
from ..models import Cli051Cliente, Cli064AsignacionCliente

#form
from applications.vacante.forms.VacanteForms import VacanteForm
from ..forms.ClienteForms import ClienteForm


#views
@login_required
# @validar_permisos(*Permiso.obtener_nombres())
def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES)
        if form.is_valid():
            ClienteForm.logo = form.cleaned_data['logo']
            form.save()
            messages.success(request, 'Cliente Creado!')
            return redirect('clientes:cliente_ver')  # Cambia a la vista deseada después de guardar
        else:
            messages.error(request, "Errores en el formulario:", form.errors)
            print("Errores en el formulario:", form.errors) 
    else:
        form = ClienteForm()
    
    context = {
        'form': form
    }
    return render(request, 'admin/client/client_create.html', context)


# Mostrar todos los clientes todos
@login_required
# @validar_permisos(*Permiso.obtener_nombres())
def ver_cliente(request):
    clientes = Cli051Cliente.objects.filter(estado_id_001=1).order_by('-id')
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
    
    return render(request, 'admin/client/client_list.html', context)

# Mostrar todos los clientes todos
@login_required
# @validar_permisos(*Permiso.obtener_nombres())
def detalle_cliente(request, pk):
    cliente = Cli051Cliente.objects.filter(id=pk).prefetch_related(
        "actividad_economica",
        "ciudad_id_004",
        "estado_id_001"
    ).first()

    if not cliente:
        return None  # Cliente no encontrado

    # Obtener asignaciones del cliente (como maestro o asignado)
    asignaciones = Cli064AsignacionCliente.objects.filter(
        id_cliente_maestro=cliente
    ).select_related("id_cliente_asignado")

    data = {
        "cliente": {
            "id": cliente.id,
            "nit": cliente.nit,
            "razon_social": cliente.razon_social,
            "email": cliente.email,
            "contacto": cliente.contacto,
            "telefono": cliente.telefono,
            "perfil_empresarial": cliente.perfil_empresarial,
            "tipo_cliente": cliente.get_tipo_cliente_display(),
            "actividad_economica": cliente.actividad_economica.descripcion if cliente.actividad_economica else "No definida",
            "ciudad": cliente.ciudad_id_004.nombre,
            "estado": cliente.estado_id_001.nombre,
            "logo": cliente.logo.url if cliente.logo else None,
            "cargo": cliente.contacto_cargo,
            "direccion": cliente.direccion_cargo,
            "referencias_laborales": cliente.referencias_laborales,
            "cantidad_colaboradores": cliente.cantidad_colaboradores,
        },
        "asignaciones": [
            {
                "id": a.id,
                "cliente_asignado": a.id_cliente_asignado.razon_social,
                "tipo_asignacion": a.get_tipo_asignacion_display(),
                "fecha_asignacion": a.fecha_asignacion
            }
            for a in asignaciones
        ]
    }

    print(data)

    contexto = {
        'data' : data,
    }
    return render(request, 'admin/client/client_detail.html', contexto)