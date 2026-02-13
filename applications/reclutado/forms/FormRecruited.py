from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset, Div, HTML
from applications.reclutado.models import Cli056AplicacionVacante
from applications.candidato.models import Can101Candidato
from applications.usuarios.models import UsuarioBase
from applications.services.choices import NIVEL_ESTUDIO_CHOICES_STATIC
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
            print("El número de documento ya existe en el modelo Cli056AplicacionVacante")
            # Validar si el correo ya existe en el modelo Can101Candidato
            if Can101Candidato.objects.filter(email=email).exclude(numero_documento=numero_documento).exists():
                self.add_error('email', 'El correo electrónico ya está registrado con otro candidato.')
                print("El correo electrónico ya está registrado con otro candidato.")
            # Validar si el teléfono ya existe en el modelo Can101Candidato
            if Can101Candidato.objects.filter(telefono=telefono).exclude(numero_documento=numero_documento).exists():
                print("El número de teléfono ya está registrado con otro candidato.")
                self.add_error('telefono', 'El número de teléfono ya está registrado con otro candidato.')


        return cleaned_data

class ActualizarEstadoReclutadoForm(forms.Form):
    estado_reclutamiento = forms.ChoiceField(
        label="Nuevo Estado",
        choices=[('', 'Seleccione una opción...')] + [
            (1, 'Recibido'),
            (2, 'Seleccionado'),
            (3, 'Finalista'),
            (4, 'Descartado'),
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select select2'})
    )
    comentario = forms.CharField(
        label="Comentario",
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Ingrese un comentario sobre el cambio de estado...'
        })
    )

    def __init__(self, *args, **kwargs):
        estado_actual = kwargs.pop('estado_actual', None)
        super().__init__(*args, **kwargs)
        
        # Configuración de Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_actualizar_estado'
        self.helper.form_class = 'w-100'
        
        self.helper.layout = Layout(
            Div(
                HTML("<h5 class='mb-3 text-primary'>Cambiar Estado del Candidato</h5>"),
                Div('estado_reclutamiento', css_class='col-12 mb-3'),
                Div('comentario', css_class='col-12 mb-3'),
                Div(
                    Submit('submit', 'Actualizar Estado', css_class='btn bg-primary bg-opacity-10 fw-medium text-primary py-2 px-4 w-100'),
                    css_class='col-12'
                ),
                css_class='row'
            ),
        )
        
        # Si hay un estado actual, excluirlo de las opciones (opcional)
        if estado_actual:
            choices = self.fields['estado_reclutamiento'].choices
            self.fields['estado_reclutamiento'].choices = [
                choice for choice in choices if choice[0] != estado_actual
            ]

class BusquedaRecibidosForm(forms.Form):
    nombre_candidato = forms.CharField(
        label="Nombre del Candidato",
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-solid',
            'placeholder': 'Buscar por nombre...'
        })
    )
    fecha_inicio = forms.DateField(
        label="Fecha Inicio",
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control form-control-solid',
            'type': 'date'
        })
    )
    fecha_fin = forms.DateField(
        label="Fecha Fin",
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control form-control-solid',
            'type': 'date'
        })
    )
    edad_minima = forms.IntegerField(
        label="Edad Mínima",
        required=False,
        min_value=0,
        max_value=120,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-solid',
            'placeholder': 'Edad mínima'
        })
    )
    edad_maxima = forms.IntegerField(
        label="Edad Máxima",
        required=False,
        min_value=0,
        max_value=120,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-solid',
            'placeholder': 'Edad máxima'
        })
    )
    nivel_estudio = forms.ChoiceField(
        label="Nivel de Estudio",
        choices=NIVEL_ESTUDIO_CHOICES_STATIC,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
            'data-placeholder': 'Seleccione nivel de estudio'
        })
    )
    puntaje_match_minimo = forms.FloatField(
        label="Puntaje Match Mínimo",
        required=False,
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-solid',
            'placeholder': 'Puntaje mínimo (0-100)',
            'step': '0.1'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configuración de Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_id = 'form_busqueda_recibidos'
        self.helper.form_class = 'w-100'
        
        self.helper.layout = Layout(
            # FILTROS DE BÚSQUEDA
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Filtros de Búsqueda</h4>"),
                    Div('nombre_candidato', css_class='col-12 mb-3'),
                    Div('fecha_inicio', css_class='col-6 mb-3'),
                    Div('fecha_fin', css_class='col-6 mb-3'),
                    Div('edad_minima', css_class='col-6 mb-3'),
                    Div('edad_maxima', css_class='col-6 mb-3'),
                    Div('nivel_estudio', css_class='col-12 mb-3'),
                    Div('puntaje_match_minimo', css_class='col-12 mb-3'),
                    Div(
                        Submit('submit', 'Buscar', css_class='btn btn-primary me-2'),
                        HTML('<a href="." class="btn btn-secondary">Limpiar</a>'),
                        css_class='col-12 d-flex justify-content-end'
                    ),
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),
        )

class RespuestaClienteForm(forms.Form):
    estado_respuesta = forms.ChoiceField(
        label="Respuesta",
        choices=[
            ('', 'Seleccione una opción...'),
            ('13', 'Apto'),
            ('12', 'No Apto'),
        ],
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
            'data-placeholder': 'Seleccione una opción'
        })
    )
    descripcion = forms.CharField(
        label="Descripción",
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control form-control-solid',
            'rows': 4,
            'placeholder': 'Ingrese la descripción de la respuesta...'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configuración de Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_respuesta_cliente'
        self.helper.form_class = 'w-100'
        
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Respuesta del Cliente</h4>"),
                    Div('estado_respuesta', css_class='col-12 mb-3'),
                    Div('descripcion', css_class='col-12 mb-3'),
                    Div(
                        Submit('submit', 'Guardar Respuesta', css_class='btn btn-primary w-100'),
                        css_class='col-12'
                    ),
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),
        )