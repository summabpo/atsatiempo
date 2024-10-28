from django import forms
from .models import Psi201Pregunta, Psi202Respuesta

class Psi201PreguntaForm(forms.ModelForm):
    class Meta:
        model = Psi201Pregunta
        fields = ['texto', 'es_invertida', 'factor', 'subfactor']
        widgets = {
            'factor': forms.Select(choices=Psi201Pregunta.FACTOR_CHOICES),
            'subfactor': forms.Select(choices=Psi201Pregunta.SUBFACTOR_CHOICES),
        }

class Psi202RespuestaForm(forms.ModelForm):
    class Meta:
        model = Psi202Respuesta
        fields = ['id_pregunta', 'respuesta']
        widgets = {
            'id_pregunta': forms.Select(attrs={'class': 'form-control'}),
            'respuesta': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'form-control'}),
        }
        labels = {
            'id_pregunta': 'Pregunta',
            'respuesta': 'Respuesta (1-5)',
        }