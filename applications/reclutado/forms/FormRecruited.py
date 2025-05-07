from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset, Div, HTML
from applications.reclutado.models import Cli056AplicacionVacante
from applications.candidato.models import Can101Candidato
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
    primer_nombre = forms.CharField(
        label="Primer Nombre",
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el primer nombre'})
    )
    segundo_nombre = forms.CharField(
        label="Segundo Nombre",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el segundo nombre'})
    )
    primer_apellido = forms.CharField(
        label="Primer Apellido",
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el primer apellido'})
    )
    segundo_apellido = forms.CharField(
        label="Segundo Apellido",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el segundo apellido'})
    )
    telefono = forms.CharField(
        label="Teléfono",
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el número de teléfono'})
    )
    email = forms.EmailField(
        label="Correo Electrónico",
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el correo electrónico'})
    )

    def __init__(self, *args, **kwargs):
        # grupo_id = kwargs.pop('grupo_id', None)
        # cliente_id = kwargs.pop('cliente_id', None)
        super().__init__(*args, **kwargs)

        # Configuración de Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_crear_reclutado'
        self.helper.form_class = 'w-200'

        self.helper.layout = Layout(
            # 🏗️ DATOS GENERALES
            Div(
            Div(
                HTML("<h4 class='mb-3 text-primary'>Datos Candidato</h4>"),
                Div('numero_documento', css_class='col-12'),  # Número de Documento 
                Div('primer_nombre', css_class='col-3'),  # Primer Nombre
                Div('segundo_nombre', css_class='col-3'),  # Segundo Nombre
                Div('primer_apellido', css_class='col-3'),  # Primer Apellido
                Div('segundo_apellido', css_class='col-3'),  # Segundo Apellido
                Div('email', css_class='col-6'),  # email 
                Div('telefono', css_class='col-6'),  # Teléfono 
                css_class='row'
            ),
            css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),
        )

    def clean(self):
        cleaned_data = super().clean()
        numero_documento = cleaned_data.get('numero_documento')
        primer_nombre = cleaned_data.get('primer_nombre')
        segundo_nombre = cleaned_data.get('segundo_nombre')
        primer_apellido = cleaned_data.get('primer_apellido')
        segundo_apellido = cleaned_data.get('segundo_apellido')
        telefono = cleaned_data.get('telefono')
        email = cleaned_data.get('email')

        # Validar si el número de documento ya existe en el modelo Cli056AplicacionVacante
        if Can101Candidato.objects.filter(numero_documento=numero_documento).exists():
            # Validar si el correo ya existe en el modelo Can101Candidato
            if Can101Candidato.objects.filter(email=email).exclude(numero_documento=numero_documento).exists():
                raise forms.ValidationError("El correo electrónico ya está registrado con otro candidato.")
            # Validar si el teléfono ya existe en el modelo Can101Candidato
            if Can101Candidato.objects.filter(telefono=telefono).exclude(numero_documento=numero_documento).exists():
                raise forms.ValidationError("El número de teléfono ya está registrado con otro candidato.")

        return cleaned_data   