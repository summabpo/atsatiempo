
import re
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from common.models import Cat004Ciudad, Cat001Estado
from ..models import Cli051Cliente


class ClienteForm(forms.Form):
    estado_id_001 = forms.ModelChoiceField(label='ESTADO'    , queryset=Cat001Estado.objects.all(), required=True)
    nit           = forms.CharField(label='NIT' , required=True  ,widget=forms.TextInput(attrs={'placeholder': 'Por favor ingrese NIT'}))
    razon_social  = forms.CharField(label='RAZON SOCIAL', required=True ,widget=forms.TextInput(attrs={'placeholder': 'Razón Social'}))
    ciudad_id_004 = forms.ModelChoiceField(label='CIUDAD', queryset=Cat004Ciudad.objects.all(), required=True)
    email         = forms.CharField(label='EMAIL'    , required=False ,widget=forms.TextInput(attrs={'placeholder': 'Sufijo costo'}))
    contacto      = forms.CharField(label='CONTACTO'    , required=False ,widget=forms.TextInput(attrs={'placeholder': 'Sufijo costo'}))
    telefono      = forms.CharField(label='TELEFONO'    , required=False ,widget=forms.TextInput(attrs={'placeholder': 'Sufijo costo'}))
    

    def __init__(self, *args, **kwargs):
        super(ClienteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('estado_id_001', css_class='js-select2'),
            Field('nit'),
            Field('razon_social'),
            Field('ciudad_id_004', css_class='js-select2'),
            Field('email'),
            Field('contacto'),
            Field('telefono'),
            Submit('submit', 'Guardar', css_class='btn-primary')
        )
    
    def clean(self):
        cleaned_data = super().clean()
        estado_id_001 = cleaned_data.get('estado_id_001')
        nit = cleaned_data.get('nit')
        razon_social = cleaned_data.get('razon_social')
        ciudad_id_004 = cleaned_data.get('ciudad_id_004')
        email = cleaned_data.get('email')
        contacto = cleaned_data.get('contacto')
        telefono = cleaned_data.get('telefono')

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', razon_social):
            self.add_error('razon_social', "El nombre solo puede contener letras.")
        else:
            self.cleaned_data['razon_social'] = razon_social.upper()

    def save(self):
        estado_id_001 = self.cleaned_data['estado_id_001']
        nit = self.cleaned_data['nit']
        razon_social = self.cleaned_data['razon_social']
        ciudad_id_004 = self.cleaned_data['ciudad_id_004']
        email = self.cleaned_data.get('email', '')
        contacto = self.cleaned_data.get('contacto', '')
        telefono = self.cleaned_data.get('telefono', '')
        

        # Lógica para guardar en tu modelo Cliente
        cliente = Cli051Cliente(
            estado_id_001 = estado_id_001,
            nit=nit,
            razon_social=razon_social,
            ciudad_id_004=ciudad_id_004,
            email=email,
            contacto=contacto,
            telefono=telefono,
            
        )
        cliente.save()