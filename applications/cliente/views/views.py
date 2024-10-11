from django.shortcuts import render, redirect
from ..models import Cli051Cliente
from ..forms.ClienteForms import ClienteForm
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    TemplateView,
    UpdateView,
    DeleteView
)
# Create your views here.
def cliente_crear(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES)
        if form.is_valid():
            ClienteForm.logo = form.cleaned_data['logo']
            form.save()
            return redirect('clientes:cliente_listar')  # Cambia a la vista deseada después de guardar
    else:
        form = ClienteForm()
    
    return render(request, 'cliente/form_cliente.html', {'form': form})

class ListadoClientes(ListView):
    template_name = 'cliente/listado_clientes.html'
    model = Cli051Cliente
    context_object_name = 'clientes'