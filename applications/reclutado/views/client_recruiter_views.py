from django.contrib.auth.views import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, Count, Q, Value, Case, When, CharField
from applications.common.models import Cat001Estado
from applications.usuarios.decorators  import validar_permisos


@login_required
@validar_permisos('acceso_reclutador')
def vacancies_assigned_recruiter(request):
    

    return render(request, 'admin/recruiter/client_recruiter/vacancies_assigned_recruiter.html')