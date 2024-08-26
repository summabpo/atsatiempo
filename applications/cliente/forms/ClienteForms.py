
import re, os
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from applications.common.models import Cat004Ciudad, Cat001Estado
from ..models import Cli051Cliente


class ClienteForm(forms.Form):
    # estado_id_001 = forms.ModelChoiceField(label='ESTADO'    , queryset=Cat001Estado.objects.all(), required=True)
    nit           = forms.CharField(label='NIT' , required=True  ,widget=forms.TextInput(attrs={'placeholder': ' Nit'}))
    razon_social  = forms.CharField(label='RAZON SOCIAL', required=True ,widget=forms.TextInput(attrs={'placeholder': 'Razón Social'}))
    ciudad_id_004 = forms.ModelChoiceField(label='CIUDAD', queryset=Cat004Ciudad.objects.all(), required=True)
    email         = forms.CharField(label='EMAIL'    , required=True , widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    contacto      = forms.CharField(label='CONTACTO'    , required=True ,widget=forms.TextInput(attrs={'placeholder': 'Contacto'}))
    telefono      = forms.CharField(label='TELEFONO'    , required=True ,widget=forms.TextInput(attrs={'placeholder': 'Teléfono'}))
    perfil_empresarial = forms.CharField(label='PERFIL EMPRESARIAL', required=True, widget=forms.Textarea(attrs={'placeholder': 'Descripción de la Empresa'}))
    logo = forms.ImageField(label='LOGO', required=False)

    def __init__(self, *args, **kwargs):
        super(ClienteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.enctype = 'multipart/form-data'


        self.fields['nit'].widget.attrs.update({
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'data-placeholder': 'Ingrese Nombre'
        })

        self.fields['razon_social'].widget.attrs.update({
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'data-placeholder': 'Ingrese Razón Social'
        })

        self.fields['ciudad_id_004'].widget.attrs.update({
            'class': 'form-select form-select-sm form-select-solid',
            'data-control': 'select2',
            'data-placeholder': 'Select an option'
        })

        self.fields['email'].widget.attrs.update({
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'data-placeholder': 'Ingrese Razón Social'
        })

        self.fields['contacto'].widget.attrs.update({
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'data-placeholder': 'Ingrese Razón Social'
        })

        self.fields['telefono'].widget.attrs.update({
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'data-placeholder': 'Ingrese Razón Social'
        })

        self.fields['perfil_empresarial'].widget.attrs.update({
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'data-placeholder': 'Ingrese Razón Social'
        })

        self.fields['logo'].widget.attrs.update({
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'data-placeholder': 'Ingrese Razón Social'
        })

        self.helper.layout = Layout(
            # Field('estado_id_001', css_class='form-control, js-select2'),
            Field('nit'),
            Field('razon_social'),
            Field('ciudad_id_004'),
            Field('email'),
            Field('contacto'),
            Field('telefono'),
            Field('perfil_empresarial'),
            Field('logo'),
            Submit('submit', 'Guardar', css_class='btn-primary')
        )
    
    def clean(self):
        cleaned_data = super().clean()
        nit = cleaned_data.get('nit')
        razon_social = cleaned_data.get('razon_social')
        telefono = cleaned_data.get('telefono')
        contacto = cleaned_data.get('contacto')
        perfil_empresarial = cleaned_data.get('perfil_empresarial')
        email = cleaned_data.get('email')
        logo = cleaned_data.get('logo')

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', razon_social):
            self.add_error('razon_social', "El nombre solo puede contener letras.")
        else:
            self.cleaned_data['razon_social'] = razon_social.upper()
        
        if not re.match(r'^\d{9}$', nit):
            self.add_error('nit','El NIT debe contener solo números y tener  9 dígitos.')

        if not re.match(r'^\d{10}$', telefono):
            self.add_error('telefono','El teléfono debe contener solo números y tener 10 dígitos.')

        if len(perfil_empresarial.split()) < 10:
            self.add_error('perfil_empresarial','La descripción debe contener al menos 10 palabras')

        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            self.add_error('email','El email no es válido.')

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', contacto):
            self.add_error('contacto','El Nombre del Contacto solo puede contener letras.')
        else:
            self.cleaned_data['contacto'] = contacto.upper()

        # validacion imagen logo
        tamanio_maximo = 5 * 1024 * 1024  # 5 MB
        listado_extensiones = ['.jpg', '.jpeg', '.png']

        if logo:
            if logo.size > tamanio_maximo:
                self.add_error('logo','El tamaño del archivo supera el tamaño permitido.')

            extension = os.path.splitext(logo.name)[1].lower()
            if extension not in listado_extensiones:
                self.add_error('logo','El archivo no es válido.')

            if Cli051Cliente.objects.filter(logo=logo.name).exists():
                self.add_error('logo','Ya existe un archivo con este nombre. Por favor renombre el archivo y vuelva a intentarlo.')

        return super().clean()


    def save(self):
        # estado_id_001 = self.cleaned_data['estado_id_001']
        nit = self.cleaned_data['nit']
        razon_social = self.cleaned_data['razon_social']
        ciudad_id_004 = self.cleaned_data['ciudad_id_004']
        email = self.cleaned_data.get('email', '')
        contacto = self.cleaned_data.get('contacto', '')
        telefono = self.cleaned_data.get('telefono', '')
        perfil_empresarial = self.cleaned_data.get('perfil_empresarial', '')
        logo = self.cleaned_data.get('logo')
        

        # Lógica para guardar en tu modelo Cliente
        cliente = Cli051Cliente(
            estado_id_001 = Cat001Estado.objects.get(id=1),
            nit=nit,
            razon_social=razon_social,
            ciudad_id_004=ciudad_id_004,
            email=email,
            contacto=contacto,
            telefono=telefono,
            perfil_empresarial=perfil_empresarial,
            logo=logo,
            
        )
        cliente.save()