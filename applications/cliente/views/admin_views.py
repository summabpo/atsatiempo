from django.shortcuts import render, redirect
import json
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from applications.usuarios.decorators  import validar_permisos

#model
from applications.vacante.models import Cli052Vacante, Cli055ProfesionEstudio, Cli053SoftSkill, Cli052VacanteSoftSkillsId053, Cli054HardSkill, Cli052VacanteHardSkillsId054
from applications.reclutado.models import Cli056AplicacionVacante
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.usuarios.models import Permiso
from ..models import Cli051Cliente

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
            return redirect('clientes:cliente_ver')  # Cambia a la vista deseada después de guardar
    else:
        form = ClienteForm()
    
    context = {
        'form': form
    }
    return render(request, 'admin/client/client_create.html', context)

# Portal interno
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
    
    return render(request, 'admin/client/standard_client_list.html', context)