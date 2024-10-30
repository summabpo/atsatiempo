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
class CalificarPreguntaForm(forms.Form):
    pregunta = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    calificacion = forms.IntegerField(
        widget=forms.NumberInput(attrs={'type': 'range', 'min': 1, 'max': 5, 'step': 1}),
        label="Calificación"
    )

    def __init__(self, *args, **kwargs):
        pregunta_obj = kwargs.pop('pregunta_obj', None)
        super().__init__(*args, **kwargs)
        if pregunta_obj:
            self.fields['pregunta'].initial = pregunta_obj.texto
            self.fields['pregunta'].label = f"Pregunta: {pregunta_obj.texto}"