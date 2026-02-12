from datetime import date
import re, os
from django import forms
from django.utils.html import format_html, escape
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Layout, Div, Submit, HTML, Row, Column, Fieldset
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.services.choices import GENERO_CHOICES_STATIC, IDIOMA_CHOICES_STATIC, NIVEL_IDIOMA_CHOICES_STATIC
from ..models import Can101Candidato
from applications.cliente.models import Cli078MotivadoresCandidato, Cli077FitCultural
import json


class RadioSelectWithDescription(forms.RadioSelect):
    """Widget personalizado que muestra la descripción de cada opción de fit cultural en un tooltip"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cache para las descripciones
        self._descriptions_cache = {}
    
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        
        # Obtener el objeto del modelo para acceder a la descripción
        fit_cultural = None
        
        # El valor puede ser el objeto del modelo directamente o el ID como string/int
        if value and value != '':
            if isinstance(value, Cli077FitCultural):
                # Si ya es el objeto del modelo
                fit_cultural = value
            else:
                # Si es el ID, obtener el objeto
                try:
                    # Convertir a int si es string
                    fit_id = int(value) if isinstance(value, str) else value
                    # Usar cache si está disponible
                    if fit_id in self._descriptions_cache:
                        fit_cultural = self._descriptions_cache[fit_id]
                    else:
                        fit_cultural = Cli077FitCultural.objects.get(id=fit_id)
                        self._descriptions_cache[fit_id] = fit_cultural
                except (Cli077FitCultural.DoesNotExist, ValueError, TypeError):
                    pass
        
        # Si encontramos el objeto y tiene descripción, agregar atributo data-descripcion al input
        if fit_cultural and fit_cultural.descripcion:
            # Agregar un icono visual al label para indicar que hay información adicional
            original_label = option['label']
            option['label'] = format_html(
                '{} <i class="ri-information-line text-primary ms-1" style="cursor: help; font-size: 0.9rem;"></i>',
                original_label
            )
            # Agregar la descripción como atributo data-* en el input
            # Asegurarse de que attrs existe y es un diccionario
            if 'attrs' not in option or option['attrs'] is None:
                option['attrs'] = {}
            # Agregar el atributo data-descripcion
            option['attrs']['data-descripcion'] = fit_cultural.descripcion
            # También agregar el ID para referencia
            option['attrs']['data-fit-id'] = str(fit_cultural.id)
        
        return option
    
    def render(self, name, value, attrs=None, renderer=None):
        # Limpiar cache antes de renderizar
        self._descriptions_cache = {}
        return super().render(name, value, attrs, renderer)

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
    hoja_de_vida = forms.FileField(
        label='HOJA DE VIDA', 
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'accept': '.pdf,.doc,.docx'  # Acepta PDF y Word
        })
    )
    

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

        # Agregar campos dinámicos de idiomas (similar a la vacante)
        for i in range(1, 3):  # Crearemos hasta 2 pares de campos
            idioma_field = f'idioma_{i}'
            nivel_field = f'nivel_idioma_{i}'
            
            # Crear y añadir el campo 'idioma'
            self.fields[idioma_field] = forms.ChoiceField(
                label=f'Idioma {i}',
                choices=IDIOMA_CHOICES_STATIC,
                widget=forms.Select(attrs={'class': 'form-select'}),
                required=False
            )
            # Crear y añadir el campo 'nivel_idioma'
            self.fields[nivel_field] = forms.ChoiceField(
                label='Nivel',
                choices=NIVEL_IDIOMA_CHOICES_STATIC,
                widget=forms.Select(attrs={'class': 'form-select'}),
                required=False
            )
            
            # Inicializar desde el JSON de idiomas si existe
            if self.instance and self.instance.idiomas:
                try:
                    idiomas_data = self.instance.idiomas if isinstance(self.instance.idiomas, list) else json.loads(self.instance.idiomas)
                    if isinstance(idiomas_data, list) and len(idiomas_data) >= i:
                        idioma_item = idiomas_data[i-1]
                        if isinstance(idioma_item, dict):
                            # Buscar por bloque o por índice
                            idioma_val = None
                            nivel_val = None
                            
                            # Si tiene campo 'bloque', buscar por bloque
                            if 'bloque' in idioma_item:
                                for item in idiomas_data:
                                    if item.get('bloque') == i:
                                        idioma_val = item.get('idioma') or item.get('id') or item.get('nombre')
                                        nivel_val = item.get('nivel') or item.get('nivel_idioma')
                                        break
                            else:
                                # Si no tiene bloque, usar el índice
                                idioma_val = idioma_item.get('idioma') or idioma_item.get('id') or idioma_item.get('nombre')
                                nivel_val = idioma_item.get('nivel') or idioma_item.get('nivel_idioma')
                            
                            if idioma_val:
                                self.fields[idioma_field].initial = idioma_val
                            if nivel_val:
                                self.fields[nivel_field].initial = nivel_val
                except (json.JSONDecodeError, TypeError, AttributeError, IndexError):
                    pass

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'container'
        self.helper.layout = Layout(
            Fieldset(
                'Información Básica',
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
                    # Sección de Idiomas
                    HTML('<div class="d-flex align-items-center my-4"><h6 class="mb-0 pe-3 text-primary fw-bold">Idiomas</h6><hr class="flex-grow-1 m-0 border-top border-1 border-secondary opacity-20"></div>'),
                    # Bloque 1 de idiomas - siempre visible
                    HTML('<div class="row" id="idiomas_bloque_1"><div class="d-flex align-items-center my-4"><div class="w-100 d-flex align-items-center" style="position: relative;"><hr class="flex-grow-1 m-0 border-top border-1 border-secondary opacity-20"><p class="position-absolute start-50 translate-middle-x mb-0 px-3 bg-white text-primary" style="z-index:1;">Idioma 1</p><hr class="flex-grow-1 m-0 border-top border-1 border-secondary opacity-20"></div></div>'),
                    Div(
                        Div('idioma_1', css_class='col-md-4'),
                        Div('nivel_idioma_1', css_class='col-md-8'),
                        css_class='row'
                    ),
                    HTML('</div>'),
                    # Bloque 2 de idiomas - oculto por defecto
                    HTML('<div class="row d-none" id="idiomas_bloque_2"><div class="d-flex align-items-center my-4"><div class="w-100 d-flex align-items-center" style="position: relative;"><hr class="flex-grow-1 m-0 border-top border-1 border-secondary opacity-20"><p class="position-absolute start-50 translate-middle-x mb-0 px-3 bg-white text-primary" style="z-index:1;">Idioma 2</p><hr class="flex-grow-1 m-0 border-top border-1 border-secondary opacity-20"></div></div>'),
                    Div(
                        Div('idioma_2', css_class='col-md-4'),
                        Div('nivel_idioma_2', css_class='col-md-8'),
                        css_class='row'
                    ),
                    HTML('</div>'),
                    # Botón para agregar Idioma 2
                    HTML('<div class="row" id="boton_idiomas_2"><div class="col-md-12 text-center"><button type="button" class="btn btn-outline-primary" id="agregar_idiomas_2"><i class="fas fa-plus me-2"></i>Agregar Idioma 2 (Opcional)</button></div></div>'),
                    # Div(
                    #     Div('estado_id_001', css_class='col'),
                    #     css_class='row'
                    # ),

                    Submit('submit_candidato', 'Guardar Empleado', css_class='btn btn-primary mt-3'),
                )
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
        tamanio_maximo_hoja = 5 * 1024 * 1024  # 5 MB (aumentado para Word)
        listado_extensiones_hoja = ['.pdf', '.doc', '.docx']

        if hoja_de_vida:
            if hoja_de_vida.size > tamanio_maximo_hoja:
                self.add_error('hoja_de_vida', 'El tamaño del archivo supera el tamaño permitido (máximo 5MB).')

            extension_hoja = os.path.splitext(hoja_de_vida.name)[1].lower()
            if extension_hoja not in listado_extensiones_hoja:
                self.add_error('hoja_de_vida', 'El archivo no es válido. Debe ser un archivo PDF o Word (.doc, .docx).')

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
        
        # Guardar idiomas en formato JSON
        idiomas_data = []
        for i in range(1, 3):  # Hasta 2 bloques de idiomas
            idioma = self.cleaned_data.get(f'idioma_{i}')
            nivel_idioma = self.cleaned_data.get(f'nivel_idioma_{i}')
            
            if idioma and nivel_idioma:
                # Obtener el nombre del idioma desde las opciones
                idioma_nombre = dict(IDIOMA_CHOICES_STATIC).get(idioma, idioma)
                nivel_nombre = dict(NIVEL_IDIOMA_CHOICES_STATIC).get(nivel_idioma, nivel_idioma)
                
                idiomas_data.append({
                    'id': idioma,  # ID del idioma (valor del choice)
                    'nombre': idioma_nombre,  # Nombre del idioma (texto)
                    'nivel': nivel_idioma  # Nivel del idioma
                })
        
        candidato.idiomas = idiomas_data if idiomas_data else None

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
    hoja_de_vida = forms.FileField(
        label='HOJA DE VIDA', 
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'accept': '.pdf,.doc,.docx'  # Acepta PDF y Word
        })
    )

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
        tamanio_maximo_hoja = 5 * 1024 * 1024  # 5 MB (aumentado para Word)
        listado_extensiones_hoja = ['.pdf', '.doc', '.docx']

        if hoja_de_vida:
            if hoja_de_vida.size > tamanio_maximo_hoja:
                self.add_error('hoja_de_vida', 'El tamaño del archivo supera el tamaño permitido (máximo 5MB).')

            extension_hoja = os.path.splitext(hoja_de_vida.name)[1].lower()
            if extension_hoja not in listado_extensiones_hoja:
                self.add_error('hoja_de_vida', 'El archivo no es válido. Debe ser un archivo PDF o Word (.doc, .docx).')

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

    
    
    def clean_imagen_perfil(self):
        imagen_perfil = self.cleaned_data.get('imagen_perfil')
        
        # Si el archivo ya se guardó exitosamente en la vista, no validar nada
        if self.files_saved_in_request.get('imagen_perfil', False):
            # El archivo ya se guardó en la vista, no procesarlo de nuevo
            # Retornar None para que Django no intente procesar el archivo nuevamente
            return None
        
        # Si no hay archivo nuevo, retornar None (no es requerido)
        if not imagen_perfil:
            return None
        
        # Validar solo si hay un nuevo archivo que no fue guardado previamente
        # Validar extensión (JPG, PNG)
        import os
        ext = os.path.splitext(imagen_perfil.name)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png']:
            raise forms.ValidationError('El archivo debe ser una imagen en formato JPG o PNG.')
        
        # Validar tamaño (máximo 10 MB)
        if imagen_perfil.size > 10 * 1024 * 1024:  # 10 MB en bytes
            raise forms.ValidationError('El archivo no puede superar los 10 MB.')
        
        # Django ImageField ya valida automáticamente que sea una imagen válida
        # No necesitamos validar con PIL aquí para evitar problemas con el archivo cerrado
        # Si la imagen es inválida, Django lanzará un error automáticamente
        
        return imagen_perfil
    hoja_de_vida = forms.FileField(
        label='HOJA DE VIDA',
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control form-control-solid'
        })
    )
    
    def clean_hoja_de_vida(self):
        hoja_de_vida = self.cleaned_data.get('hoja_de_vida')
        
        # Si el archivo ya se guardó exitosamente en la vista, no validar nada
        if self.files_saved_in_request.get('hoja_de_vida', False):
            # El archivo ya se guardó en la vista, no procesarlo de nuevo
            if self.candidato and self.candidato.hoja_de_vida:
                return self.candidato.hoja_de_vida
            return None
        
        # Validar solo si hay un nuevo archivo
        if hoja_de_vida:
            # Validar extensión (PDF, DOC, DOCX)
            import os
            ext = os.path.splitext(hoja_de_vida.name)[1].lower()
            if ext not in ['.pdf', '.doc', '.docx']:
                raise forms.ValidationError('El archivo debe ser un documento en formato PDF o Word (.doc, .docx).')
            
            # Validar tamaño (máximo 10 MB)
            if hoja_de_vida.size > 10 * 1024 * 1024:  # 10 MB en bytes
                raise forms.ValidationError('El archivo no puede superar los 10 MB.')
        
        return hoja_de_vida
    
    video_perfil = forms.FileField(
        label='VIDEO DE PERFIL',
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control form-control-solid'
        })
    )
    
    def clean_video_perfil(self):
        video_perfil = self.cleaned_data.get('video_perfil')
        
        # Si el archivo ya se guardó exitosamente en la vista, no validar nada
        if self.files_saved_in_request.get('video_perfil', False):
            # El archivo ya se guardó en la vista, no procesarlo de nuevo
            if self.candidato and self.candidato.video_perfil:
                return self.candidato.video_perfil
            return None
        
        # Validar solo si hay un nuevo archivo
        if video_perfil:
            # Validar extensión (MP4)
            import os
            ext = os.path.splitext(video_perfil.name)[1].lower()
            if ext not in ['.mp4']:
                raise forms.ValidationError('El archivo debe ser un video en formato MP4.')
            
            # Validar tamaño (máximo 150 MB)
            if video_perfil.size > 150 * 1024 * 1024:  # 150 MB en bytes
                raise forms.ValidationError('El archivo no puede superar los 150 MB.')
        
        return video_perfil

    perfil = forms.CharField(
        label='Mi perfil',
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Por favor escriba su perfil del candidato aquí.',
            'class': 'form-control form-control-solid',
            'rows': 4
        })
    )

    aspiracion_salarial = forms.IntegerField(
        label='ASPIRACIÓN SALARIAL',
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Aspiración Salarial',
            'class': 'form-control form-control-solid'
        })
    )

    

    motivadores = forms.ModelMultipleChoiceField(
        label='MOTIVADORES',
        required=False,
        queryset=Cli078MotivadoresCandidato.objects.filter(estado_id=1),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input d-flex flex-wrap', # Clase para el input del checkbox
        }),
    )

    

    grupo_fit_1 = forms.ModelChoiceField(
            queryset=Cli077FitCultural.objects.filter(estado=1, grupo=1).order_by('id'),
            label='Estilo trabajo predominante en el área:',
            to_field_name='id',
            widget=RadioSelectWithDescription(attrs={
                'class': 'form-check-input', # Clase para el input del radio
            }),
            required=False # Si quieres que la selección sea opcional
        )
    
    grupo_fit_2 = forms.ModelChoiceField(
            queryset=Cli077FitCultural.objects.filter(estado=1, grupo=2).order_by('id'),
            label='Tipo de liderazgo presente:',
            to_field_name='id',
            widget=RadioSelectWithDescription(attrs={
                'class': 'form-check-input', # Clase para el input del radio
            }),
            required=False # Si quieres que la selección sea opcional
        )
    
    grupo_fit_3 = forms.ModelChoiceField(
            queryset=Cli077FitCultural.objects.filter(estado=1, grupo=3).order_by('id'),
            label='Comunicación organizacional:',
            to_field_name='id',
            widget=RadioSelectWithDescription(attrs={
                'class': 'form-check-input', # Clase para el input del radio
            }),
            required=False # Si quieres que la selección sea opcional
        )

    grupo_fit_4 = forms.ModelChoiceField(
            queryset=Cli077FitCultural.objects.filter(estado=1, grupo=4).order_by('id'),
            label='Ritmo de trabajo:',
            to_field_name='id',
            widget=RadioSelectWithDescription(attrs={
                'class': 'form-check-input', # Clase para el input del radio
            }),
            required=False # Si quieres que la selección sea opcional
        )
    
    grupo_fit_5 = forms.ModelChoiceField(
            queryset=Cli077FitCultural.objects.filter(estado=1, grupo=5).order_by('id'),
            label='Estilo toma de decisiones:',
            to_field_name='id',
            widget=RadioSelectWithDescription(attrs={
                'class': 'form-check-input', # Clase para el input del radio
            }),
            required=False # Si quieres que la selección sea opcional
        )
    


    def __init__(self, *args, instance=None, files_saved_in_request=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.candidato = instance  # guardamos el candidato si se va a editar
        self.files_saved_in_request = files_saved_in_request or {}  # archivos ya guardados exitosamente

        # Agregar campos dinámicos de idiomas (similar a la vacante)
        for i in range(1, 3):  # Crearemos hasta 2 pares de campos
            idioma_field = f'idioma_{i}'
            nivel_field = f'nivel_idioma_{i}'
            
            # Crear y añadir el campo 'idioma'
            self.fields[idioma_field] = forms.ChoiceField(
                label=f'Idioma {i}',
                choices=IDIOMA_CHOICES_STATIC,
                widget=forms.Select(attrs={'class': 'form-select form-select-solid'}),
                required=False
            )
            # Crear y añadir el campo 'nivel_idioma'
            self.fields[nivel_field] = forms.ChoiceField(
                label='Nivel',
                choices=NIVEL_IDIOMA_CHOICES_STATIC,
                widget=forms.Select(attrs={'class': 'form-select form-select-solid'}),
                required=False
            )
            
            # Inicializar desde el JSON de idiomas si existe
            if self.candidato and self.candidato.idiomas:
                try:
                    idiomas_data = self.candidato.idiomas if isinstance(self.candidato.idiomas, list) else json.loads(self.candidato.idiomas)
                    if isinstance(idiomas_data, list) and len(idiomas_data) >= i:
                        idioma_item = idiomas_data[i-1]
                        if isinstance(idioma_item, dict):
                            # Buscar por bloque o por índice
                            idioma_val = None
                            nivel_val = None
                            
                            # Si tiene campo 'bloque', buscar por bloque
                            if 'bloque' in idioma_item:
                                for item in idiomas_data:
                                    if item.get('bloque') == i:
                                        idioma_val = item.get('idioma') or item.get('id')
                                        nivel_val = item.get('nivel') or item.get('nivel_idioma')
                                        break
                            else:
                                # Si no tiene bloque, usar el índice
                                idioma_val = idioma_item.get('idioma') or idioma_item.get('id')
                                nivel_val = idioma_item.get('nivel') or idioma_item.get('nivel_idioma')
                            
                            if idioma_val:
                                self.fields[idioma_field].initial = idioma_val
                            if nivel_val:
                                self.fields[nivel_field].initial = nivel_val
                except (json.JSONDecodeError, TypeError, AttributeError, IndexError):
                    pass

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        # self.helper.layout = Layout(
        #     Div(
        #         Div(
        #             HTML("<h4 class='mb-3 text-primary'>Datos Personales</h4>"),
        #             Div('primer_nombre', css_class='col-md-3'),
        #             Div('segundo_nombre', css_class='col-md-3'),
        #             Div('primer_apellido', css_class='col-md-3'),
        #             Div('segundo_apellido', css_class='col-md-3'),
        #             Div('numero_documento', css_class='col-md-3'),
        #             Div('fecha_nacimiento', css_class='col-md-3'),
        #             Div('sexo', css_class='col-md-3'),
        #             Div('aspiracion_salarial', css_class='col-md-3'),
        #             css_class='row'
        #         ),
        #         css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
        #     ),
        #     Div(
        #         Div(
        #             HTML("<h4 class='mb-3 text-primary'>Contacto</h4>"),
        #             Div('email', css_class='col-md-6'),
        #             Div('telefono', css_class='col-md-6'),
        #             Div('ciudad_id_004', css_class='col-md-6'),
        #             Div('direccion', css_class='col-md-6'),
        #             css_class='row'
        #         ),
        #         css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
        #     ),
        #     Div(
        #         Div(
        #             HTML("<h4 class='mb-3 text-primary'>Perfil</h4>"),
        #             Div('perfil', css_class='col-md-12'),
        #             css_class='row'
        #         ),
        #         css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
        #     ),
        #     Div(
        #         Div(
        #             HTML("<h4 class='mb-3 text-primary'>Documentos</h4>"),
                    
        #             Div('imagen_perfil', css_class='col-md-4'),
        #             Div('hoja_de_vida', css_class='col-md-4'),
        #             Div('video_perfil', css_class='col-md-4'),
        #             css_class='row'
        #         ),
        #         css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
        #     ),
        #     Div(
        #         HTML("<h4 class='mb-3 text-primary'>Fit Cultural</h4>"),
        #         HTML("<p class='text-muted mb-3'>Selecciona una opción por cada categoría. Marca lo que más se ajusta a tu realidad.</p>"),
        #         Div(
        #             Div('grupo_fit_1', css_class='col-md-6 mb-3'),
        #             Div('grupo_fit_2', css_class='col-md-6 mb-3'),
        #             Div('grupo_fit_3', css_class='col-md-6 mb-3'),
        #             Div('grupo_fit_4', css_class='col-md-6 mb-3'),
        #             Div('grupo_fit_5', css_class='col-md-6 mb-3'),
        #             css_class='row'
        #         ),
        #         css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
        #     ),
        #     Div(
        #         HTML("<h4 class='mb-3 text-primary'>Motivadores</h4>"),
        #         HTML("<p class='text-muted mb-3'>Selecciona máximo 2 motivadores que sean más importantes para ti en tu vida laboral.</p>"),
        #         Div(
        #             Div('motivadores', css_class='col-md-12 motivadores'),
        #             css_class='row'
        #         ),
        #         css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
        #     ),
        # )

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
        video_perfil = cleaned_data.get('video_perfil')
        perfil = cleaned_data.get('perfil')
        motivadores = cleaned_data.get('motivadores')
        
        # Combinar todos los campos de fit cultural de los diferentes grupos para validación
        fit_cultural_combined = []
        for i in range(1, 6):  # grupo_fit_1 a grupo_fit_5
            grupo_field = f'grupo_fit_{i}'
            if grupo_field in cleaned_data and cleaned_data[grupo_field]:
                # Ahora cada campo es una selección única, no una lista
                fit_cultural_combined.append(cleaned_data[grupo_field])

        # Validación de Perfil del Candidato
        if perfil:
            palabras = perfil.strip().split()
            if len(palabras) < 10:
                self.add_error('perfil', 'El perfil del candidato debe contener al menos 10 palabras.')

        # Validación de Número de Documento
        if numero_documento:
            if not re.match(r'^\d+$', numero_documento):
                self.add_error('numero_documento', 'El número de documento debe contener solo números.')
            elif Can101Candidato.objects.filter(numero_documento=numero_documento).exclude(id=self.candidato.id if self.candidato else None).exists():
                self.add_error('numero_documento', 'Este número de documento ya está registrado en otro registro.')
        else:
            self.add_error('numero_documento', 'El número de documento es obligatorio.')

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
        
        # Sin validaciones de archivos - se permiten todos los archivos sin restricciones


        # validación motivadores
        # motivadores puede venir como QuerySet, lista de objetos, o lista de dicts (cuando se inicializa desde JSON)
        print(motivadores)
        motivadores_count = 0
        if motivadores:
            # Si es QuerySet o lista de objetos
            try:
                motivadores_count = len(motivadores)
            except TypeError:
                # Si es un solo objeto, lo convertimos a 1
                motivadores_count = 1
            # Si es lista de dicts (por ejemplo, [{'id': 1, 'nombre': 'X'}])
            if isinstance(motivadores, dict):
                motivadores_count = 1
            elif isinstance(motivadores, list) and motivadores and isinstance(motivadores[0], dict):
                motivadores_count = len(motivadores)
        else:
            self.add_error('motivadores', 'Debe seleccionar al menos una opción de motivadores.')
            
        if motivadores_count > 2:
            self.add_error('motivadores', 'Solo puede seleccionar máximo dos opciones de motivadores.')
        
        # Validación fit cultural - asegurar que se seleccione al menos una opción por cada grupo
        grupos_labels = {
            1: 'Estilo trabajo predominante en el área',
            2: 'Tipo de liderazgo presente',
            3: 'Comunicación organizacional',
            4: 'Ritmo de trabajo',
            5: 'Estilo toma de decisiones'
        }
        
        for i in range(1, 6):
            grupo_field = f'grupo_fit_{i}'
            value = cleaned_data.get(grupo_field)
            
            # Validar que se haya seleccionado al menos una opción por grupo
            if not value:
                self.add_error(grupo_field, f'Debe seleccionar al menos una opción para: {grupos_labels[i]}')
            elif isinstance(value, list):
                # Si por alguna razón viene como lista, validar y convertir
                if len(value) > 1:
                    self.add_error(grupo_field, 'Solo puede seleccionar una opción por grupo.')
                elif len(value) == 1:
                    # Si viene como lista de un solo elemento, lo convertimos al objeto
                    cleaned_data[grupo_field] = value[0]
        

        return cleaned_data

