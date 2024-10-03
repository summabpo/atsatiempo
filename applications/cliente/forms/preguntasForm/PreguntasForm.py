import re, os
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field , Div

#modelos
from applications.cliente.models import Cli058Pregunta

class PreguntasForm(forms.Form):
    pregunta_cliente = forms.CharField(label='Ingrese Pregunta',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',  # Clases CSS del campo  
            }
        ), required=True)