from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset, Div, HTML
from applications.reclutado.models import Cli056AplicacionVacante
from applications.usuarios.models import UsuarioBase
from django.utils import timezone
from datetime import datetime, time

class ReclutadoCrearForm(forms.Form):
    numero_documento = forms.CharField(
        label="Número de Documento",
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el número de documento'})
    )

    def __init__(self, *args, **kwargs):
        # grupo_id = kwargs.pop('grupo_id', None)
        # cliente_id = kwargs.pop('cliente_id', None)
        super().__init__(*args, **kwargs)

        # Configuración de Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_crear_entrevista'
        self.helper.form_class = 'w-200'

        self.helper.layout = Layout(
            # 🏗️ DATOS GENERALES
            Div(
            Div(
                HTML("<h4 class='mb-3 text-primary'>Datos Principales</h4>"),
                Div('numero_documento', css_class='col-12'),  # Número de Documento
                css_class='row'
            ),
            css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),
        )

    def clean(self):
        cleaned_data = super().clean()
        numero_documento = cleaned_data.get('numero_documento')

        return cleaned_data   