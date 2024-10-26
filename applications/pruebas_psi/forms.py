from django import forms
from .models import Psi201Pregunta

class Psi201PreguntaForm(forms.ModelForm):
    class Meta:
        model = Psi201Pregunta
        fields = ['texto', 'es_invertida', 'factor', 'subfactor']
        widgets = {
            'factor': forms.Select(choices=Psi201Pregunta.FACTOR_CHOICES),
            'subfactor': forms.Select(choices=Psi201Pregunta.SUBFACTOR_CHOICES),
        }