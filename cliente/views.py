from django.shortcuts import render, redirect

from .forms.ClienteForms import ClienteForm

# Create your views here.
def cliente_crear(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cliente/index.html')  # Cambia a la vista deseada después de guardar
    else:
        form = ClienteForm()
    
    return render(request, 'cliente/index.html', {'form': form})