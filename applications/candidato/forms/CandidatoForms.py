from datetime import date
import re, os
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Layout, Div, Submit, HTML, Row, Column, Fieldset
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.services.choices import GENERO_CHOICES_STATIC
from ..models import Can101Candidato

class CandidatoForm(forms.Form):
    # estado_id_001 = forms.ModelChoiceField(label='ESTADO', queryset=Cat001Estado.objects.all(), required=True)
    email = forms.CharField(label='EMAIL', required=True , widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    primer_nombre = forms.CharField(label='PRIMER NOMBRE', required=True, max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Primer Nombre'}))
    segundo_nombre = forms.CharField(label='SEGUNDO NOMBRE', required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Segundo Nombre'}))
    primer_apellido = forms.CharField(label='PRIMER APELLIDO', required=True, max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Primer Apellido'}))
    segundo_apellido = forms.CharField(label='SEGUNDO APELLIDO', required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Segundo Apellido'}))
    ciudad_id_004 = forms.ModelChoiceField(label='CIUDAD', queryset=Cat004Ciudad.objects.all(), required=True)
    sexo = forms.ChoiceField(label='GENERO', choices=[ ('', '---'), ('M', 'MASCULINO'), ('F', 'FEMENINO')], required=True)
    fecha_nacimiento = forms.DateField(label='FECHA DE NACIMIENTO', widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    telefono = forms.CharField(label='TELEFONO'    , required=True , widget=forms.TextInput(attrs={'placeholder': 'Teléfono'}))
    imagen_perfil = forms.ImageField(label='IMAGEN DE PERFIL', required=False)
    hoja_de_vida = forms.FileField(label='HOJA DE VIDA', required=False)
    

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super(CandidatoForm, self).__init__(*args, **kwargs)

        if self.instance:
            #self.fields['estado_id_001'].initial = self.instance.estado_id_001
            self.fields['email'].initial = self.instance.email
            self.fields['primer_nombre'].initial = self.instance.primer_nombre
            self.fields['segundo_nombre'].initial = self.instance.segundo_nombre
            self.fields['primer_apellido'].initial = self.instance.primer_apellido
            self.fields['segundo_apellido'].initial = self.instance.segundo_apellido
            self.fields['ciudad_id_004'].initial = self.instance.ciudad_id_004
            self.fields['sexo'].initial = self.instance.sexo
            self.fields['fecha_nacimiento'].initial = str(self.instance.fecha_nacimiento)
            self.fields['telefono'].initial = self.instance.telefono
            self.fields['imagen_perfil'].initial = self.instance.imagen_perfil
            self.fields['hoja_de_vida'].initial = self.instance.hoja_de_vida

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'container'
        self.helper.layout = Layout(
            Div(
                Div(
                    Div('primer_nombre', css_class='col form-control-solid mb-3 mb-lg-0'),
                    Div('segundo_nombre', css_class='col'),
                    Div('primer_apellido', css_class='col'),
                    Div('segundo_apellido', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('email', css_class='col'),
                    Div('telefono', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('fecha_nacimiento', css_class='col'),
                    Div('sexo', css_class='col'),
                    Div('ciudad_id_004', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('imagen_perfil', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('hoja_de_vida', css_class='col'),
                    css_class='row'
                ),
                # Div(
                #     Div('estado_id_001', css_class='col'),
                #     css_class='row'
                # ),

                Submit('submit_candidato', 'Guardar Empleado', css_class='btn btn-primary mt-3'),
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        primer_nombre = cleaned_data.get('primer_nombre')
        segundo_nombre = cleaned_data.get('segundo_nombre')
        primer_apellido = cleaned_data.get('primer_apellido')
        segundo_apellido = cleaned_data.get('segundo_apellido')
        email = cleaned_data.get('email')
        telefono = cleaned_data.get('telefono')
        imagen_perfil = cleaned_data.get('imagen_perfil') 
        hoja_de_vida = cleaned_data.get('hoja_de_vida') 

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', primer_nombre):
            self.add_error('primer_nombre', "El campo solo puede contener letras.")
        else:
            self.cleaned_data['primer_nombre'] = primer_nombre.upper()     

        if segundo_nombre:  # Verifica si el campo no está vacío
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', segundo_nombre):
                self.add_error('segundo_nombre', "El segundo nombre solo puede contener letras.")
            else:
                self.cleaned_data['segundo_nombre'] = segundo_nombre.upper()

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', primer_apellido):
            self.add_error('primer_apellido', "El campo solo puede contener letras.")
        else:
            self.cleaned_data['primer_apellido'] = primer_apellido.upper()   

        if segundo_apellido:  # Verifica si el campo no está vacío
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', segundo_apellido):
                # self.add_error("El campo solo puede contener letras.")
                self.add_error('segundo_apellido', "El segundo apellido solo puede contener letras.")
            else:
                self.cleaned_data['segundo_apellido'] = segundo_apellido.upper()  

        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            self.add_error('email','El email no es válido.')

        if not re.match(r'^\d{10}$', telefono):
            self.add_error('telefono','El teléfono debe contener solo números y tener 10 dígitos.')
        
        # validacion imagen perfil
        tamanio_maximo = 5 * 1024 * 1024  # 5 MB
        listado_extensiones = ['.jpg', '.jpeg', '.png']

        if imagen_perfil:
            if imagen_perfil.size > tamanio_maximo:
                self.add_error('imagen_perfil','El tamaño del archivo supera el tamaño permitido.')

            extension = os.path.splitext(imagen_perfil.name)[1].lower()
            if extension not in listado_extensiones:
                self.add_error('imagen_perfil','El archivo no es válido.')

            if self.instance:
                if Can101Candidato.objects.filter(imagen_perfil=imagen_perfil.name).exclude(id=self.instance.id).exists():
                    self.add_error('imagen_perfil','Ya existe un archivo con este nombre en otro registro. Por favor renombre el archivo y vuelva a intentarlo.')
            
        
        # validacion hoja de vida
        tamanio_maximo_hoja = 2 * 1024 * 1024  # 2 MB
        listado_extensiones_hoja = ['.pdf']

        if hoja_de_vida:
            if hoja_de_vida.size > tamanio_maximo_hoja:
                self.add_error('hoja_de_vida', 'El tamaño del archivo supera el tamaño permitido.')

            extension_hoja = os.path.splitext(hoja_de_vida.name)[1].lower()
            if extension_hoja not in listado_extensiones_hoja:
                self.add_error('hoja_de_vida', 'El archivo no es válido. Debe ser un archivo PDF.')

            if self.instance:
                if Can101Candidato.objects.filter(hoja_de_vida=hoja_de_vida.name).exclude(id=self.instance.id).exists():
                    self.add_error('hoja_de_vida', 'Ya existe un archivo con este nombre en otro registro. Por favor renombre el archivo y vuelva a intentarlo.')

        # return cleaned_data

    def save(self):
        if self.instance:
            candidato = self.instance
        else:
            candidato = Can101Candidato()
        
        candidato.estado_id_001 = Cat001Estado.objects.get(id=1)
        candidato.email = self.cleaned_data['email']
        candidato.primer_nombre = self.cleaned_data['primer_nombre']
        candidato.segundo_nombre = self.cleaned_data['segundo_nombre']
        candidato.primer_apellido = self.cleaned_data['primer_apellido']
        candidato.segundo_apellido = self.cleaned_data['segundo_apellido']
        candidato.telefono = self.cleaned_data['telefono']
        candidato.ciudad_id_004 = self.cleaned_data['ciudad_id_004']
        candidato.sexo = self.cleaned_data['sexo']
        candidato.fecha_nacimiento = self.cleaned_data['fecha_nacimiento']
        candidato.imagen_perfil = self.cleaned_data['imagen_perfil']
        candidato.hoja_de_vida = self.cleaned_data['hoja_de_vida']


        candidato.save()

class CandidatoFormAdmin(forms.Form):
    # campos para el formulario de administración de candidatos
    email = forms.CharField(label='EMAIL', required=True , widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    primer_nombre = forms.CharField(label='PRIMER NOMBRE', required=True, max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Primer Nombre'}))
    segundo_nombre = forms.CharField(label='SEGUNDO NOMBRE', required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Segundo Nombre'}))
    primer_apellido = forms.CharField(label='PRIMER APELLIDO', required=True, max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Primer Apellido'}))
    segundo_apellido = forms.CharField(label='SEGUNDO APELLIDO', required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Segundo Apellido'}))
    sexo = forms.ChoiceField(label='GENERO', choices=[ ('', '---'), ('M', 'MASCULINO'), ('F', 'FEMENINO')], required=True)
    fecha_nacimiento = forms.DateField(label='FECHA DE NACIMIENTO', widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    telefono = forms.CharField(label='TELEFONO'    , required=True , widget=forms.TextInput(attrs={'placeholder': 'Teléfono'}))
    imagen_perfil = forms.ImageField(label='IMAGEN DE PERFIL', required=False)
    hoja_de_vida = forms.FileField(label='HOJA DE VIDA', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_candidato'

        cities = Cat004Ciudad.objects.all().order_by('nombre')
        city_choices = [('', '----------')] + [(ciudad.id, f"{ciudad.nombre}") for ciudad in cities]

        self.fields['ciudad'] = forms.ChoiceField(
            label='CIUDAD',
            choices=city_choices,
            widget=forms.Select(
                attrs={
                    'class': 'form-select form-select-solid',  # Clases CSS del campo  
                    'data-control': 'select2',
                    'data-placeholder': 'Seleccion una opción',
                    'data-dropdown-parent': '#modal_candidato',
                    }
        ), required=True)

        self.helper.layout = Layout(
            Fieldset(
                'Nombre',
                Row(
                    Column('primer_nombre', css_class='form-group col-md-6 mb-0'),
                    Column('segundo_nombre', css_class='form-group col-md-6 mb-0'),
                    Column('primer_apellido', css_class='form-group col-md-6 mb-0'),
                    Column('segundo_apellido', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                )
            ),
            Fieldset(
                '',
                Row(
                    Column('email', css_class='form-group col-md-6 mb-0'),
                    Column('telefono', css_class='form-group col-md-6 mb-0'),
                )
            ),
            Fieldset(
                '',
                Row(
                    Column('fecha_nacimiento', css_class='form-group col-md-4 mb-0'),
                    Column('sexo', css_class='form-group col-md-4 mb-0'),
                    Column('ciudad', css_class='form-group col-md-4 mb-0'),
                )
            ),
            Fieldset(
                'Imagen Candidato',
                Row(
                    Column('imagen_perfil', css_class='form-group col-md-12 mb-0'),
                )
            ),
            Fieldset(
                'Hoja de Vida Candidato',
                Row(
                    Column('hojda_de_vida', css_class='form-group col-md-12 mb-0'),
                )
            ),
        )

    #metodo de validacion
    def validate_telefono(self, telefono):
        # Verificar que el teléfono sea único
        if Can101Candidato.objects.filter(telefono=telefono).exists():
            self.add_error('telefono', 'Este número de teléfono ya está registrado.')

        # Validar formato del teléfono
        if not re.match(r'^\d{10}$', telefono):
            self.add_error('telefono', 'El teléfono debe contener solo números y tener 10 dígitos.')

    def clean(self):
        cleaned_data =  super().clean() 
        
        primer_nombre = cleaned_data.get('primer_nombre')
        segundo_nombre = cleaned_data.get('segundo_nombre')
        primer_apellido = cleaned_data.get('primer_apellido')
        segundo_apellido = cleaned_data.get('segundo_apellido')
        email = cleaned_data.get('email')
        telefono = cleaned_data.get('telefono')
        imagen_perfil = cleaned_data.get('imagen_perfil')
        hoja_de_vida = cleaned_data.get('hoja_de_vida')
        

        # Validación primer nombre
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', primer_nombre):
            self.add_error('primer_nombre', "El campo solo puede contener letras.")
        else:
            self.cleaned_data['primer_nombre'] = primer_nombre.upper()     

        # Validación segundo nombre
        if segundo_nombre:  # Verifica si el campo no está vacío
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', segundo_nombre):
                self.add_error('segundo_nombre', "El segundo nombre solo puede contener letras.")
            else:
                self.cleaned_data['segundo_nombre'] = segundo_nombre.upper()

        # Validación primer apellido
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', primer_apellido):
            self.add_error('primer_apellido', "El campo solo puede contener letras.")
        else:
            self.cleaned_data['primer_apellido'] = primer_apellido.upper()   

        # Validación segundo apellido
        if segundo_apellido:  # Verifica si el campo no está vacío
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', segundo_apellido):
                # self.add_error("El campo solo puede contener letras.")
                self.add_error('segundo_apellido', "El segundo apellido solo puede contener letras.")
            else:
                self.cleaned_data['segundo_apellido'] = segundo_apellido.upper() 

        # Validación de Email
        if email:
            if Can101Candidato.objects.filter(email=email).exists():
                self.add_error('email', 'Este correo electrónico ya está registrado.')

        # Validación de Teléfono
        if telefono:
            self.validate_telefono(telefono)

        #validación Ciudad
        ciudad = self.cleaned_data.get('ciudad')
        if not ciudad:
            raise forms.ValidationError("Este campo es obligatorio.")
        
        # validacion imagen logo
        tamanio_maximo = 5 * 1024 * 1024  # 5 MB
        listado_extensiones = ['.jpg', '.jpeg', '.png']

        if imagen_perfil:
            if imagen_perfil.size > tamanio_maximo:
                self.add_error('imagen_perfil','El tamaño del archivo supera el tamaño permitido.')

            extension = os.path.splitext(imagen_perfil.name)[1].lower()
            if extension not in listado_extensiones:
                self.add_error('imagen_perfil','El archivo no es válido.')

            if Can101Candidato.objects.filter(imagen_perfil=imagen_perfil.name).exists():
                self.add_error('imagen_perfil','Ya existe un archivo con este nombre. Por favor renombre el archivo y vuelva a intentarlo.')

        # validacion hoja de vida
        tamanio_maximo_hoja = 2 * 1024 * 1024  # 2 MB
        listado_extensiones_hoja = ['.pdf']

        if hoja_de_vida:
            if hoja_de_vida.size > tamanio_maximo_hoja:
                self.add_error('hoja_de_vida', 'El tamaño del archivo supera el tamaño permitido.')

            extension_hoja = os.path.splitext(hoja_de_vida.name)[1].lower()
            if extension_hoja not in listado_extensiones_hoja:
                self.add_error('hoja_de_vida', 'El archivo no es válido. Debe ser un archivo PDF.')

            if Can101Candidato.objects.filter(hoja_de_vida=hoja_de_vida.name).exists():
                self.add_error('hoja_de_vida', 'Ya existe un archivo con este nombre. Por favor renombre el archivo y vuelva a intentarlo.')
        
        return cleaned_data
    
#formulario para el registro o edición de candidatos
class CandidateForm(forms.Form):
    email = forms.EmailField(
        label='EMAIL',
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email',
            'class': 'form-control form-control-solid'
        })
    )
    primer_nombre = forms.CharField(
        label='PRIMER NOMBRE',
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'Primer Nombre',
            'class': 'form-control form-control-solid'
        })
    )
    segundo_nombre = forms.CharField(
        label='SEGUNDO NOMBRE',
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'Segundo Nombre',
            'class': 'form-control form-control-solid'
        })
    )
    primer_apellido = forms.CharField(
        label='PRIMER APELLIDO',
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'Primer Apellido',
            'class': 'form-control form-control-solid'
        })
    )
    segundo_apellido = forms.CharField(
        label='SEGUNDO APELLIDO',
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'Segundo Apellido',
            'class': 'form-control form-control-solid'
        })
    )
    ciudad_id_004 = forms.ModelChoiceField(
        label='CIUDAD',
        queryset=Cat004Ciudad.objects.all(),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-solid'
        })
    )
    sexo = forms.ChoiceField(
        label='GENERO',
        choices= GENERO_CHOICES_STATIC,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-solid'
        })
    )
    fecha_nacimiento = forms.DateField(
        label='FECHA DE NACIMIENTO',
        required=True,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control form-control-solid'
        })
    )
    telefono = forms.CharField(
        label='TELEFONO',
        required=True,
        max_length=10,
        widget=forms.TextInput(attrs={
            'placeholder': 'Teléfono',
            'class': 'form-control form-control-solid'
        })
    )
    numero_documento = forms.CharField(
        label='NUMERO DE DOCUMENTO',
        required=True,
        max_length=20,
        widget=forms.TextInput(attrs={
            'placeholder': 'Número de Documento',
            'class': 'form-control form-control-solid'
        })
    )
    direccion = forms.CharField(
        label='DIRECCIÓN',
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Dirección',
            'class': 'form-control form-control-solid'
        })
    )
    imagen_perfil = forms.ImageField(
        label='IMAGEN DE PERFIL',
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control form-control-solid'
        })
    )
    hoja_de_vida = forms.FileField(
        label='HOJA DE VIDA',
        required=True,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control form-control-solid'
        })
    )

    def __init__(self, *args, instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.candidato = instance  # guardamos el candidato si se va a editar

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Datos Personales</h4>"),
                    Div('primer_nombre', css_class='col-3'),
                    Div('segundo_nombre', css_class='col-3'),
                    Div('primer_apellido', css_class='col-3'),
                    Div('segundo_apellido', css_class='col-3'),
                    Div('numero_documento', css_class='col-4'),
                    Div('fecha_nacimiento', css_class='col-4'),
                    Div('sexo', css_class='col-4'),
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Contacto</h4>"),
                    Div('email', css_class='col-6'),
                    Div('telefono', css_class='col-6'),
                    Div('ciudad_id_004', css_class='col-6'),
                    Div('direccion', css_class='col-6'),
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Documentos</h4>"),
                    
                    Div('imagen_perfil', css_class='col-6'),
                    Div('hoja_de_vida', css_class='col-6'),
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),
        )

    def clean(self):
        cleaned_data =  super().clean() 

        primer_nombre = cleaned_data.get('primer_nombre')
        segundo_nombre = cleaned_data.get('segundo_nombre')
        primer_apellido = cleaned_data.get('primer_apellido')
        segundo_apellido = cleaned_data.get('segundo_apellido')
        email = cleaned_data.get('email')
        telefono = cleaned_data.get('telefono')
        ciudad_id_004 = cleaned_data.get('ciudad_id_004')
        sexo = cleaned_data.get('sexo')
        fecha_nacimiento = cleaned_data.get('fecha_nacimiento')
        numero_documento = cleaned_data.get('numero_documento')
        direccion = cleaned_data.get('direccion')
        imagen_perfil = cleaned_data.get('imagen_perfil')
        hoja_de_vida = cleaned_data.get('hoja_de_vida')

        # Validación de Número de Documento
        if numero_documento:
            if not re.match(r'^\d+$', numero_documento):
                self.add_error('numero_documento', 'El número de documento debe contener solo números.')
            elif Can101Candidato.objects.filter(numero_documento=numero_documento).exclude(id=self.candidato.id if self.candidato else None).exists():
                self.add_error('numero_documento', 'Este número de documento ya está registrado en otro registro.')
                

        # Validación de Dirección
        if direccion:
            if len(direccion) > 255:
                self.add_error('direccion', 'La dirección no puede exceder los 255 caracteres.')

        # Validación de Sexo
        if sexo and sexo not in dict(GENERO_CHOICES_STATIC).keys():
            self.add_error('sexo', 'El género seleccionado no es válido.')

        # Validación de Fecha de Nacimiento
        if fecha_nacimiento:
            if fecha_nacimiento > date.today():
                self.add_error('fecha_nacimiento', 'La fecha de nacimiento no puede ser en el futuro.')

        # Validación primer nombre
        if primer_nombre and isinstance(primer_nombre, str):
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', primer_nombre):
                self.add_error('primer_nombre', "El campo solo puede contener letras.")
            else:
                self.cleaned_data['primer_nombre'] = primer_nombre.upper()  

        # Validación segundo nombre
        if segundo_nombre:  # Verifica si el campo no está vacío
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', segundo_nombre):
                self.add_error('segundo_nombre', "El segundo nombre solo puede contener letras.")
            else:
                self.cleaned_data['segundo_nombre'] = segundo_nombre.upper()

        # Validación primer apellido
        if primer_apellido and isinstance(primer_apellido, str):
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', primer_apellido):
                self.add_error('primer_apellido', "El campo solo puede contener letras.")
            else:
                self.cleaned_data['primer_apellido'] = primer_apellido.upper()  

        # Validación segundo apellido
        if segundo_apellido:  # Verifica si el campo no está vacío
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', segundo_apellido):
                # self.add_error("El campo solo puede contener letras.")
                self.add_error('segundo_apellido', "El segundo apellido solo puede contener letras.")
            else:
                self.cleaned_data['segundo_apellido'] = segundo_apellido.upper() 

        # Validación de Email
        if email:
            if Can101Candidato.objects.filter(email=email).exclude(id=self.candidato.id if self.candidato else None).exists():
                self.add_error('email', 'Este correo electrónico ya está registrado.')

        # Validación de Teléfono
        if telefono:
            # Validar formato del teléfono
            if not re.match(r'^\d{10}$', telefono):
                self.add_error('telefono', 'El teléfono debe contener solo números y tener 10 dígitos.')

            # Verificar que el teléfono sea único
            if Can101Candidato.objects.filter(telefono=telefono).exclude(id=self.candidato.id if self.candidato else None).exists():
                self.add_error('telefono', 'Este número de teléfono ya está registrado.')

        #validación Ciudad
        
        if not ciudad_id_004:
            self.add_error('ciudad_id_004', "Este campo es obligatorio.")
        
        # validacion imagen logo
        tamanio_maximo = 5 * 1024 * 1024  # 5 MB
        listado_extensiones = ['.jpg', '.jpeg', '.png']

        if imagen_perfil:
            if imagen_perfil.size > tamanio_maximo:
                self.add_error('imagen_perfil','El tamaño del archivo supera el tamaño permitido.')

            extension = os.path.splitext(imagen_perfil.name)[1].lower()
            if extension not in listado_extensiones:
                self.add_error('imagen_perfil','El archivo no es válido.')

            if Can101Candidato.objects.filter(imagen_perfil=imagen_perfil.name).exists():
                self.add_error('imagen_perfil','Ya existe un archivo con este nombre. Por favor renombre el archivo y vuelva a intentarlo.')

        # validacion hoja de vida
        tamanio_maximo_hoja = 2 * 1024 * 1024  # 2 MB
        listado_extensiones_hoja = ['.pdf']

        if hoja_de_vida:
            if hoja_de_vida.size > tamanio_maximo_hoja:
                self.add_error('hoja_de_vida', 'El tamaño del archivo supera el tamaño permitido.')

            extension_hoja = os.path.splitext(hoja_de_vida.name)[1].lower()
            if extension_hoja not in listado_extensiones_hoja:
                self.add_error('hoja_de_vida', 'El archivo no es válido. Debe ser un archivo PDF.')

            if Can101Candidato.objects.filter(hoja_de_vida=hoja_de_vida.name).exists():
                self.add_error('hoja_de_vida', 'Ya existe un archivo con este nombre. Por favor renombre el archivo y vuelva a intentarlo.')
        
        return cleaned_data

