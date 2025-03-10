import re, os
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field , Div, HTML
from applications.common.models import Cat004Ciudad, Cat001Estado
from ..models import Cli051Cliente, Cli065ActividadEconomica, Cli067PoliticasInternas, Cli066PruebasPsicologicas, Cli068Cargo, Cli069Requisito


class ClienteForm(forms.Form):
    nit           = forms.CharField(label='NIT' , required=True  ,widget=forms.TextInput(attrs={'placeholder': ' Nit'}))
    razon_social  = forms.CharField(label='RAZON SOCIAL', required=True ,widget=forms.TextInput(attrs={'placeholder': 'Razón Social'}))
    email         = forms.CharField(label='EMAIL'    , required=True , widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    contacto      = forms.CharField(label='NOMBRE CONTACTO'    , required=True ,widget=forms.TextInput(attrs={'placeholder': 'Nombre Contacto'}))
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
        ('1', 'Cliente Standard'),
        ('2', 'Cliente Headhunter'),
        ('3', 'Cliente Asignado Headhunter'),
    ]
    tipo_cliente = forms.ChoiceField(
        label='TIPO CLIENTE',
        choices=[('', 'Seleccione una opción')] + TIPO_CLIENTE,
        widget=forms.Select(
            attrs={
                'class': 'form-select form-control',
                'id': 'id_tipo_cliente',
            }
        ), required=True)
    
    PAGO_NOMINA = [
        ('1', 'Semanal'),
        ('2', 'Quincenal'),
        ('3', 'Mensual'),
    ]
    periodicidad_pago = forms.ChoiceField(
        label='PERIODICIDAD DE PAGO',
        choices=[('', 'Seleccione una opción')] + PAGO_NOMINA,
        widget=forms.Select(
            attrs={
                'class': 'form-select form-control ps-5 h-55 select2',
                'id': 'id_periodicidad_pago',
            }
        ), required=False)

    referencias_laborales = forms.IntegerField(
        label='REFERENCIAS LABORALES',
        required=False,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control form-control-solid mb-3 mb-lg-0',
                'placeholder': 'Referencias Laborales'
            }
        ))

    cantidad_colaboradores = forms.IntegerField(
        label='CANTIDAD DE COLABORADORES',
        required=False,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control form-control-solid mb-3 mb-lg-0',
                'placeholder': 'Cantidad de Colaboradores'
            }
        ))
    
    contacto_cargo = forms.CharField(
        label='CARGO DEL CONTACTO',
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid mb-3 mb-lg-0',
                'placeholder': 'Cargo del Contacto'
            }
        )
    )

    direccion_cargo = forms.CharField(
        label='DIRECCIÓN DEL CONTACTO',
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid mb-3 mb-lg-0',
                'placeholder': 'Dirección del Contacto'
            }
        )
    )

    

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
                    'class': 'form-select form-control select2',
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
                    'class': 'form-select form-control select2',
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
                    Div(
                        HTML("<h4 class='mb-3 text-primary'>Información Principal</h4>"),  
                        Div('tipo_cliente', css_class='col-4'),
                        Div('nit', css_class='col-4'),
                        Div('razon_social', css_class='col-4'),
                        Div('ciudad_id_004', css_class='col-6'),
                        Div('logo', css_class='col-6'),
                        Div('perfil_empresarial', css_class='col-12'),
                        Div('actividad_economica', css_class='col-12'),
                        css_class='row'
                    ),
                    css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"  # 
                ),
                Div(
                    Div(
                        HTML("<h4 class='mb-3 text-primary'>Información Contacto</h4>"),  #  Agregar título con color y margen
                        Div('contacto', css_class='col-12'),
                        Div('contacto_cargo', css_class='col-12'),
                        Div('direccion_cargo', css_class='col-4'),
                        Div('email', css_class='col-4'),
                        Div('telefono', css_class='col-4'),
                        css_class='row'
                    ),
                    css_class="mb-4 p-3 border rounded"  #  Opcional: Agregar estilo de borde y fondo
                ),
                Div(
                    Div(
                        HTML("<h4 class='mb-3 text-primary'>Información Adicional</h4>"),  #  Agregar título con color y margen
                        Div('periodicidad_pago', css_class='col'),
                        Div('referencias_laborales', css_class='col'),
                        Div('cantidad_colaboradores', css_class='col'),
                        css_class='row'
                    ),
                    css_class="mb-4 p-3 border rounded "  #  Opcional: Agregar estilo de borde y fondo
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
        periodicidad_pago = cleaned_data.get('periodicidad_pago')
        referencias_laborales = cleaned_data.get('referencias_laborales')
        cantidad_colaboradores = cleaned_data.get('cantidad_colaboradores')
        contacto_cargo = cleaned_data.get('contacto_cargo')
        direccion_cargo = cleaned_data.get('direccion_cargo')

        if not contacto_cargo:
            self.add_error('contacto_cargo', 'El Cargo del Contacto no puede estar vacío.')
        else:
            self.cleaned_data['contacto_cargo'] = contacto_cargo.upper()

        if not direccion_cargo:
            self.add_error('direccion_cargo', 'La Dirección del Contacto no puede estar vacía.')
        else:
            self.cleaned_data['direccion_cargo'] = direccion_cargo.upper()

        if not tipo_cliente:
            self.errors['tipo_cliente'] = self.error_class(['Debe seleccionar un tipo de cliente.'])

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

        if not periodicidad_pago:
            self.add_error('periodicidad_pago', 'Debe seleccionar una periodicidad de pago.')

        if referencias_laborales is None:
            self.add_error('referencias_laborales', 'Debe ingresar el número de referencias laborales.')

        if cantidad_colaboradores is None:
            self.add_error('cantidad_colaboradores', 'Debe ingresar la cantidad de colaboradores.')

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
        periodicidad_pago = self.cleaned_data['periodicidad_pago']
        referencias_laborales = self.cleaned_data['referencias_laborales']
        cantidad_colaboradores = self.cleaned_data['cantidad_colaboradores']
        contacto_cargo = self.cleaned_data['contacto_cargo']
        direccion_cargo = self.cleaned_data['direccion_cargo']
        

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
            tipo_cliente=tipo_cliente,
            periodicidad_pago=periodicidad_pago,
            referencias_laborales=referencias_laborales,
            cantidad_colaboradores=cantidad_colaboradores,
            contacto_cargo=contacto_cargo,
            direccion_cargo=direccion_cargo
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
        ('1', 'Cliente Standard'),
        ('2', 'Cliente Headhunter'),
        ('3', 'Cliente Asignado Headhunter'),
    ]

    tipo_cliente = forms.ChoiceField(
        label='TIPO CLIENTE',
        choices=[('', 'Seleccione una opción')] + TIPO_CLIENTE,
        widget=forms.Select(
            attrs={
                'class': 'form-select form-control',
                'id': 'id_tipo_cliente',
            }
        ), required=True)

    PAGO_NOMINA = [
        ('1', 'Semanal'),
        ('2', 'Quincenal'),
        ('3', 'Mensual'),
    ]
    periodicidad_pago = forms.ChoiceField(
        label='PERIODICIDAD DE PAGO',
        choices=[('', 'Seleccione una opción')] + PAGO_NOMINA,
        widget=forms.Select(
            attrs={
                'class': 'form-select form-control ps-5 h-55 select2',
                'id': 'id_periodicidad_pago',
            }
        ), required=False)

    referencias_laborales = forms.IntegerField(
        label='REFERENCIAS LABORALES',
        required=False,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control form-control-solid mb-3 mb-lg-0',
                'placeholder': 'Referencias Laborales'
            }
        ))

    cantidad_colaboradores = forms.IntegerField(
        label='CANTIDAD DE COLABORADORES',
        required=False,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control form-control-solid mb-3 mb-lg-0',
                'placeholder': 'Cantidad de Colaboradores'
            }
        ))

    contacto_cargo = forms.CharField(
        label='CARGO DEL CONTACTO',
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid mb-3 mb-lg-0',
                'placeholder': 'Cargo del Contacto'
            }
        )
    )

    direccion_cargo = forms.CharField(
        label='DIRECCIÓN DEL CONTACTO',
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid mb-3 mb-lg-0',
                'placeholder': 'Dirección del Contacto'
            }
        )
    )

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
                    'class': 'form-select form-control select2',
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
                    'class': 'form-select form-control select2',
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
                    Div(
                        HTML("<h4 class='mb-3 text-primary'>Información Principal</h4>"),  
                        Div('tipo_cliente', css_class='col-4'),
                        Div('nit', css_class='col-4'),
                        Div('razon_social', css_class='col-4'),
                        Div('ciudad_id_004', css_class='col-6'),
                        Div('logo', css_class='col-6'),
                        Div('perfil_empresarial', css_class='col-12'),
                        Div('actividad_economica', css_class='col-12'),
                        css_class='row'
                    ),
                    css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"  
                ),
                Div(
                    Div(
                        HTML("<h4 class='mb-3 text-primary'>Información Contacto</h4>"),  
                        Div('contacto', css_class='col-12'),
                        Div('contacto_cargo', css_class='col-12'),
                        Div('direccion_cargo', css_class='col-4'),
                        Div('email', css_class='col-4'),
                        Div('telefono', css_class='col-4'),
                        css_class='row'
                    ),
                    css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"  
                ),
                Div(
                    Div(
                        HTML("<h4 class='mb-3 text-primary'>Información Adicional</h4>"),  
                        Div('periodicidad_pago', css_class='col'),
                        Div('referencias_laborales', css_class='col'),
                        Div('cantidad_colaboradores', css_class='col'),
                        css_class='row'
                    ),
                    css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"  
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
        periodicidad_pago = cleaned_data.get('periodicidad_pago')
        referencias_laborales = cleaned_data.get('referencias_laborales')
        cantidad_colaboradores = cleaned_data.get('cantidad_colaboradores')
        contacto_cargo = cleaned_data.get('contacto_cargo')
        direccion_cargo = cleaned_data.get('direccion_cargo')

        if not contacto_cargo:
            self.add_error('contacto_cargo', 'El Cargo del Contacto no puede estar vacío.')
        else:
            self.cleaned_data['contacto_cargo'] = contacto_cargo.upper()

        if not direccion_cargo:
            self.add_error('direccion_cargo', 'La Dirección del Contacto no puede estar vacía.')
        else:
            self.cleaned_data['direccion_cargo'] = direccion_cargo.upper()

        if not tipo_cliente:
            self.errors['tipo_cliente'] = self.error_class(['Debe seleccionar un tipo de cliente.'])

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

        if not actividad_economica:
            self.add_error('actividad_economica', 'Debe seleccionar una actividad económica.')

        if not periodicidad_pago:
            self.add_error('periodicidad_pago', 'Debe seleccionar una periodicidad de pago.')

        if referencias_laborales is None:
            self.add_error('referencias_laborales', 'Debe ingresar el número de referencias laborales.')

        if cantidad_colaboradores is None:
            self.add_error('cantidad_colaboradores', 'Debe ingresar la cantidad de colaboradores.')

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
        cliente.periodicidad_pago = self.cleaned_data['periodicidad_pago']
        cliente.referencias_laborales = self.cleaned_data['referencias_laborales']
        cliente.cantidad_colaboradores = self.cleaned_data['cantidad_colaboradores']
        cliente.contacto_cargo = self.cleaned_data['contacto_cargo']
        cliente.direccion_cargo = self.cleaned_data['direccion_cargo']
        cliente.save()

class ClienteFormPoliticas(forms.Form):

    def __init__(self, *args, **kwargs):
        super(ClienteFormPoliticas, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_cliente_politicas'

        politicas = Cli067PoliticasInternas.objects.filter(estado=1).order_by('descripcion')
        politicas_choices = [('', 'Seleccione una politica')] + [(politica.id, f"{politica.descripcion}") for politica in politicas]

        self.fields['politicas'] = forms.ChoiceField(
            label='POLITICAS',
            choices=politicas_choices,
            widget=forms.Select(
                attrs={
                    'class': 'form-select form-control select2',
                    'id': 'id_politicas',
                }
            ), required=True)

        self.helper.layout = Layout(
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Políticas internas</h4>"),
                    Div('politicas', css_class='col-12'),
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        politicas = cleaned_data.get('politicas')

        if not politicas:
            self.add_error('politicas', 'Debe seleccionar una política.')

        return cleaned_data

class ClienteFormPruebas(forms.Form):

    def __init__(self, *args, **kwargs):
        super(ClienteFormPruebas, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_cliente_pruebas'

        pruebas = Cli066PruebasPsicologicas.objects.filter(estado=1).order_by('descripcion')
        pruebas_choices = [('', 'Seleccione una prueba')] + [(prueba.id, f"{prueba.nombre}") for prueba in pruebas]

        self.fields['pruebas'] = forms.ChoiceField(
            label='PRUEBAS',
            choices=pruebas_choices,
            widget=forms.Select(
                attrs={
                    'class': 'form-select form-control select2',
                    'id': 'id_pruebas',
                }
            ), required=True)

        self.helper.layout = Layout(
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Pruebas</h4>"),
                    Div('pruebas', css_class='col-12'),
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        pruebas = cleaned_data.get('pruebas')

        if not pruebas:
            self.add_error('pruebas', 'Debe seleccionar una política.')

        return cleaned_data
    
class ClienteFormCargos(forms.Form):
    
    def __init__(self, *args, cliente_id=None, **kwargs):
        super(ClienteFormCargos, self).__init__(*args, **kwargs)
        self.cliente_id = cliente_id

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_cliente_cargos'

        self.fields['cargo'] = forms.CharField(
            label='CARGOS',
            required=True,
            widget=forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid mb-3 mb-lg-0',
                    'placeholder': 'Cargos'
                }
            )
        )

        self.helper.layout = Layout(
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Cargos</h4>"),
                    Div('cargo', css_class='col-12'),
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        cargo = cleaned_data.get('cargo')
        
        if not cargo:
            self.add_error('cargo', 'Debe ingresar un cargo.')
        else:
            # Verifica si el cargo ya está registrado para el mismo cliente
            cargo = cargo.upper()
            if Cli068Cargo.objects.filter(nombre_cargo=cargo, cliente_id=self.cliente_id).exists():
                self.add_error('cargo', 'El cargo ya está registrado para este cliente.')

        return cleaned_data
    
class ClienteFormRequisitos(forms.Form):

    def __init__(self, *args, cliente_id=None, **kwargs):
        super(ClienteFormRequisitos, self).__init__(*args, **kwargs)
        self.cliente_id = cliente_id

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_cliente_requisitos'

        self.fields['requisitos'] = forms.CharField(
            label='NOMBRE',
            required=True,
            widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid mb-3 mb-lg-0',
                'placeholder': 'Nombre'
            }
            )
        )

        self.fields['descripcion'] = forms.CharField(
            label='DESCRIPCIÓN',
            required=True,
            widget=forms.Textarea(
            attrs={
                'class': 'form-control form-control-solid mb-3 mb-lg-0',
                'placeholder': 'Descripción',
                'rows': 5,
                'cols': 40,
            }
            )
        )

        self.helper.layout = Layout(
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Requisitos</h4>"),
                    Div('requisitos', css_class='col-12'),
                    Div('descripcion', css_class='col-12'),
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        requisitos = cleaned_data.get('requisitos')
        descripcion = cleaned_data.get('descripcion')

        if not requisitos:
            self.add_error('requisitos', 'Debe ingresar un requisito.')
        else:
            requisitos = requisitos.upper()
            # Verifica si el requisito ya está registrado para el mismo cliente
            if Cli069Requisito.objects.filter(nombre=requisitos, cliente_id=self.cliente_id).exists():
                self.add_error('requisitos', 'El requisito ya está registrado para este cliente.')

        if not descripcion:
            self.add_error('descripcion', 'Debe ingresar una descripción.')
        elif len(descripcion.split()) < 10:
            self.add_error('descripcion', 'La descripción debe contener al menos 10 palabras.')

        return cleaned_data