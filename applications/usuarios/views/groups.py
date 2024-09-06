from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse

from applications.usuarios.forms.groupsform import groupsForm
from applications.usuarios.models import Grupo



def groups_views(request):
    form = groupsForm()
    groups = Grupo.objects.all()
    
    if request.method == 'POST':
        form = groupsForm(request.POST)
        if form.is_valid():
            new_group = Grupo (
                        name = form.cleaned_data['name'], 
                        description = form.cleaned_data['descripcion'] , 
                    )
            new_group.save()
            
            
    return render(request, './admin/groups.html',{
        'form':form,
        'groups':groups,
        })