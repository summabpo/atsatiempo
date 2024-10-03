import re, os
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field , Div, HTML

#modelos
from applications.cliente.models import Cli058Pregunta

class PreguntasFormCliente(forms.Form):
    
    pregunta_cliente = forms.CharField(label='INGRESE PREGUNTA',
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Ej: ¿Su empresa fomenta la innovación?',
                'rows': 5,  
                'cols': 40,  
                'class': 'fixed-size-textarea form-control-solid'  # Clases CSS del campo  
            }
        ), required=True)
    
    respuesta = forms.ChoiceField(label='INGRESE RESPUESTA PREGUNTA',
        choices=[(str(i), str(i)) for i in range(1, 6)],  # 1 to 5
        widget=forms.RadioSelect(attrs={'class': 'rating-input d-inline-flex'}),  # Clases para alinear horizontalmente
        required=True
    )

    pregunta_correlacion = forms.CharField(label='INGRESE PREGUNTA CORRELACIONADA',
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Ej: ¿Ustes esta de acuerdo que la empresa fomente la innovación.?',
                'rows': 5,  
                'cols': 40,  
                'class': 'fixed-size-textarea form-control-solid'  # Clases CSS del campo  
            }
        ), required=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Configuración de Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_crear_pregunta'
        self.helper.form_class = 'w-200'
    
        self.helper.layout = Layout(
            Row(
                Column('pregunta_cliente', css_class='form-group mb-0'),
                css_class='form-group mb-0'
            ),
            Row(
                Column('respuesta', css_class='form-group mb-0'),  # Incluye el campo rating
                css_class='form-group mb-0'
            ),
            Row(
                Column('pregunta_correlacion', css_class='form-group mb-0'),
                css_class='form-group mb-0'
            ),
        )

    def clean(self):
        cleaned_data =  super().clean()

        # Validate titulo
        pregunta_cliente = cleaned_data.get('pregunta_cliente')
        respuesta = cleaned_data.get('respuesta')
        pregunta_correlacion = cleaned_data.get('pregunta_correlacion')

        return cleaned_data