import re, os
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field , Div
from applications.common.models import Cat004Ciudad, Cat001Estado
from ..models import Cli051Cliente, Cli065ActividadEconomica


class ClienteForm(forms.Form):
    # estado_id_001 = forms.ModelChoiceField(label='ESTADO'    , queryset=Cat001Estado.objects.all(), required=True)
    nit           = forms.CharField(label='NIT' , required=True  ,widget=forms.TextInput(attrs={'placeholder': ' Nit'}))
    razon_social  = forms.CharField(label='RAZON SOCIAL', required=True ,widget=forms.TextInput(attrs={'placeholder': 'Razón Social'}))
    # ciudad_id_004 = forms.ModelChoiceField(label='CIUDAD', queryset=Cat004Ciudad.objects.all(), required=True)
    email         = forms.CharField(label='EMAIL'    , required=True , widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    contacto      = forms.CharField(label='CONTACTO'    , required=True ,widget=forms.TextInput(attrs={'placeholder': 'Contacto'}))
    telefono      = forms.CharField(label='TELEFONO'    , required=True ,widget=forms.TextInput(attrs={'placeholder': 'Teléfono'}))
    perfil_empresarial = forms.CharField(
        label='PERFIL EMPRESARIAL',
        required=True,
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Descripción de la Empresa',
                'rows': 5,  
                'cols': 40,  
                'class': 'fixed-size-textarea'
            }
        )
    )
    logo = forms.ImageField(label='LOGO', required=False)
    
    TIPO_CLIENTE = [
        ('1', 'Empresa'),
        ('2', 'Headhunter'),
        ('3', 'Ciente Headhunter'),
    ]

    tipo_cliente = forms.ChoiceField(
        label='TIPO CLIENTE',
        choices=[('', 'Seleccione una opción')] + TIPO_CLIENTE,
        widget=forms.Select(
            attrs={
                'class': 'form-select form-control ps-5 h-55 select2',
                'id': 'id_tipo_cliente',
            }
        ), required=True)

    def __init__(self, *args, **kwargs):
        super(ClienteForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.enctype = 'multipart/form-data'
        self.helper.form_id = 'form_cliente'



        self.fields['nit'].widget.attrs.update({
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'data-placeholder': 'Ingrese Nit'
        })

        self.fields['razon_social'].widget.attrs.update({
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'data-placeholder': 'Ingrese Razón Social',
            
        })

        cities = Cat004Ciudad.objects.all().order_by('nombre')
        city_choices = [('', 'Seleccione una Ciudad')] + [(ciudad.id, f"{ciudad.nombre}") for ciudad in cities]

        self.fields['ciudad_id_004'] = forms.ChoiceField(
            label='CIUDAD',
            choices=city_choices,
            widget=forms.Select(
                attrs={
                    'class': 'form-select form-control ps-5 h-55 select2',
                    'id': 'id_ciudad_id_004',
                    }
        ), required=True)

        activities = Cli065ActividadEconomica.objects.all().order_by('descripcion')
        activity_choices = [('', 'Seleccione una Actividad Económica')] + [(actividad.id, f"{actividad.codigo} - {actividad.descripcion}") for actividad in activities]

        self.fields['actividad_economica'] = forms.ChoiceField(
            label='ACTIVIDAD ECONÓMICA',
            choices=activity_choices,
            widget=forms.Select(
                attrs={
                    'class': 'form-select form-control ps-5 h-55 select2',
                    'id': 'id_actividad_economica',
                }
            ), required=True)

        self.fields['email'].widget.attrs.update({
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'data-placeholder': 'Ingrese Razón Social'
        })

        self.fields['contacto'].widget.attrs.update({
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'data-placeholder': 'Contacto'
        })

        self.fields['telefono'].widget.attrs.update({
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'data-placeholder': 'Teléfono'
        })

        self.fields['perfil_empresarial'].widget.attrs.update({
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'data-placeholder': 'Perfil Empresarial'
        })

        self.fields['logo'].widget.attrs.update({
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'data-placeholder': 'Logo'
        })

        self.helper.layout = Layout(
            Div(
                Div(
                    Div('tipo_cliente', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('nit', css_class='col form-control-solid mb-3 mb-lg-0'),
                    Div('razon_social', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('ciudad_id_004', css_class='col'),
                    Div('email', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('contacto', css_class='col'),
                    Div('telefono', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('logo', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('perfil_empresarial', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('actividad_economica', css_class='col'),
                    css_class='row'
                ),
            )
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
        actividad_economica = cleaned_data.get('actividad_economica')
        tipo_cliente = cleaned_data.get('tipo_cliente')

        if not tipo_cliente:
            self.add_error('tipo_cliente', 'Debe seleccionar un tipo de cliente.')

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', razon_social):
            self.add_error('razon_social', "El nombre solo puede contener letras.")
        else:
            self.cleaned_data['razon_social'] = razon_social.upper()
        
        if not re.match(r'^\d{9}$', nit):
            self.add_error('nit','El NIT debe contener solo números y tener  9 dígitos.')

        if not re.match(r'^\d{10}$', telefono):
            self.add_error('telefono','El teléfono debe contener solo números y tener 10 dígitos.')

        # Verifica si el teléfono ya está registrado
        if telefono and Cli051Cliente.objects.filter(telefono=telefono).exists():
            self.add_error('telefono', 'El teléfono ya está registrado.')

        if len(perfil_empresarial.split()) < 10:
            self.add_error('perfil_empresarial','La descripción debe contener al menos 10 palabras')

        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            self.add_error('email','El email no es válido.')

        # Verifica si el email ya está registrado
        if email and Cli051Cliente.objects.filter(email=email).exists():
            self.add_error('email','El email ya está registrado.')

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

        if not actividad_economica:
            self.add_error('actividad_economica', 'Debe seleccionar una actividad económica.')

        return cleaned_data


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
        actividad_economica = self.cleaned_data['actividad_economica']
        tipo_cliente = self.cleaned_data['tipo_cliente']
        

        # Lógica para guardar en tu modelo Cliente
        cliente = Cli051Cliente(
            estado_id_001=Cat001Estado.objects.get(id=1),
            nit=nit,
            razon_social=razon_social,
            ciudad_id_004=Cat004Ciudad.objects.get(id=ciudad_id_004),
            email=email,
            contacto=contacto,
            telefono=telefono,
            perfil_empresarial=perfil_empresarial,
            logo=logo,
            actividad_economica=Cli065ActividadEconomica.objects.get(id=actividad_economica),
            tipo_cliente=tipo_cliente
        )
        cliente.save()

class ClienteFormEdit(forms.Form):
    nit = forms.CharField(label='NIT', required=True, widget=forms.TextInput(attrs={'placeholder': 'Nit'}))
    razon_social = forms.CharField(label='RAZON SOCIAL', required=True, widget=forms.TextInput(attrs={'placeholder': 'Razón Social'}))
    email = forms.CharField(label='EMAIL', required=True, widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    contacto = forms.CharField(label='CONTACTO', required=True, widget=forms.TextInput(attrs={'placeholder': 'Contacto'}))
    telefono = forms.CharField(label='TELEFONO', required=True, widget=forms.TextInput(attrs={'placeholder': 'Teléfono'}))
    perfil_empresarial = forms.CharField(
        label='PERFIL EMPRESARIAL',
        required=True,
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Descripción de la Empresa',
                'rows': 5,
                'cols': 40,
                'class': 'fixed-size-textarea'
            }
        )
    )
    logo = forms.ImageField(label='LOGO', required=False)

    TIPO_CLIENTE = [
        ('1', 'Empresa'),
        ('2', 'Headhunter'),
        ('3', 'Cliente Headhunter'),
    ]

    tipo_cliente = forms.ChoiceField(
        label='TIPO CLIENTE',
        choices=[('', 'Seleccione una opción')] + TIPO_CLIENTE,
        widget=forms.Select(
            attrs={
                'class': 'form-select form-control ps-5 h-55 select2',
                'id': 'id_tipo_cliente',
            }
        ), required=True)

    def __init__(self, *args, **kwargs):
        super(ClienteFormEdit, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.enctype = 'multipart/form-data'
        self.helper.form_id = 'form_cliente_edit'

        self.fields['nit'].widget.attrs.update({
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'data-placeholder': 'Ingrese Nit'
        })

        self.fields['razon_social'].widget.attrs.update({
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'data-placeholder': 'Ingrese Razón Social'
        })

        cities = Cat004Ciudad.objects.all().order_by('nombre')
        city_choices = [('', 'Seleccione una Ciudad')] + [(ciudad.id, f"{ciudad.nombre}") for ciudad in cities]

        self.fields['ciudad_id_004'] = forms.ChoiceField(
            label='CIUDAD',
            choices=city_choices,
            widget=forms.Select(
                attrs={
                    'class': 'form-select form-control ps-5 h-55 select2',
                    'id': 'id_ciudad_id_004',
                }
            ), required=True)

        activities = Cli065ActividadEconomica.objects.all().order_by('descripcion')
        activity_choices = [('', 'Seleccione una Actividad Económica')] + [(actividad.id, f"{actividad.codigo} - {actividad.descripcion}") for actividad in activities]

        self.fields['actividad_economica'] = forms.ChoiceField(
            label='ACTIVIDAD ECONÓMICA',
            choices=activity_choices,
            widget=forms.Select(
                attrs={
                    'class': 'form-select form-control ps-5 h-55 select2',
                    'id': 'id_actividad_economica',
                }
            ), required=True)

        self.fields['email'].widget.attrs.update({
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'data-placeholder': 'Ingrese Email'
        })

        self.fields['contacto'].widget.attrs.update({
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'data-placeholder': 'Contacto'
        })

        self.fields['telefono'].widget.attrs.update({
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'data-placeholder': 'Teléfono'
        })

        self.fields['perfil_empresarial'].widget.attrs.update({
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'data-placeholder': 'Perfil Empresarial'
        })

        self.fields['logo'].widget.attrs.update({
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'data-placeholder': 'Logo'
        })

        self.helper.layout = Layout(
            Div(
                Div(
                    Div('tipo_cliente', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('nit', css_class='col form-control-solid mb-3 mb-lg-0'),
                    Div('razon_social', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('ciudad_id_004', css_class='col'),
                    Div('email', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('contacto', css_class='col'),
                    Div('telefono', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('logo', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('perfil_empresarial', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('actividad_economica', css_class='col'),
                    css_class='row'
                ),
            )
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
        actividad_economica = cleaned_data.get('actividad_economica')
        tipo_cliente = cleaned_data.get('tipo_cliente')

        if not tipo_cliente:
            self.add_error('tipo_cliente', 'Debe seleccionar un tipo de cliente.')

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', razon_social):
            self.add_error('razon_social', "El nombre solo puede contener letras.")
        else:
            self.cleaned_data['razon_social'] = razon_social.upper()

        if not re.match(r'^\d{9}$', nit):
            self.add_error('nit', 'El NIT debe contener solo números y tener 9 dígitos.')

        if not re.match(r'^\d{10}$', telefono):
            self.add_error('telefono', 'El teléfono debe contener solo números y tener 10 dígitos.')

        if len(perfil_empresarial.split()) < 10:
            self.add_error('perfil_empresarial', 'La descripción debe contener al menos 10 palabras')

        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            self.add_error('email', 'El email no es válido.')

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', contacto):
            self.add_error('contacto', 'El Nombre del Contacto solo puede contener letras.')
        else:
            self.cleaned_data['contacto'] = contacto.upper()

        # validacion imagen logo
        tamanio_maximo = 5 * 1024 * 1024  # 5 MB
        listado_extensiones = ['.jpg', '.jpeg', '.png']

        if logo:
            if logo.size > tamanio_maximo:
                self.add_error('logo', 'El tamaño del archivo supera el tamaño permitido.')

            extension = os.path.splitext(logo.name)[1].lower()
            if extension not in listado_extensiones:
                self.add_error('logo', 'El archivo no es válido.')

            if Cli051Cliente.objects.filter(logo=logo.name).exists():
                self.add_error('logo', 'Ya existe un archivo con este nombre. Por favor renombre el archivo y vuelva a intentarlo.')

        if not actividad_economica:
            self.add_error('actividad_economica', 'Debe seleccionar una actividad económica.')

        return cleaned_data

    def save(self, cliente_id):
        cliente = Cli051Cliente.objects.get(id=cliente_id)
        cliente.nit = self.cleaned_data['nit']
        cliente.razon_social = self.cleaned_data['razon_social']
        cliente.ciudad_id_004 = self.cleaned_data['ciudad_id_004']
        cliente.email = self.cleaned_data.get('email', '')
        cliente.contacto = self.cleaned_data.get('contacto', '')
        cliente.telefono = self.cleaned_data.get('telefono', '')
        cliente.perfil_empresarial = self.cleaned_data.get('perfil_empresarial', '')
        cliente.logo = self.cleaned_data.get('logo')
        cliente.actividad_economica = Cli065ActividadEconomica.objects.get(id=self.cleaned_data['actividad_economica'])
        cliente.tipo_cliente = self.cleaned_data['tipo_cliente']
        cliente.save()