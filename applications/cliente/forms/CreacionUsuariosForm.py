import re, os
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML
from applications.common.models import Cat004Ciudad
from applications.usuarios.models import UsuarioBase
from django.db.models import Q

class CrearUsuarioInternoForm(forms.Form):
    # Campos del usuario
    primer_nombre = forms.CharField(
        label='Primer Nombre', 
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'placeholder': 'Primer Nombre',
        })
    )

    segundo_nombre = forms.CharField(
        label='Segundo Nombre', 
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'placeholder': 'Segundo Nombre',
        })
    )

    primer_apellido = forms.CharField(
        label='Primer Apellido', 
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'placeholder': 'Primer Apellido',
        })
    )

    segundo_apellido = forms.CharField(
        label='Segundo Apellido', 
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'placeholder': 'Segundo Apellido',
        })
    )

    correo = forms.EmailField(
        label='Correo Usuario', 
        max_length=150,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'placeholder': 'Ingrese el correo del usuario',
        })
    )

    rol = forms.ChoiceField(
        label='Rol del Usuario',
        choices=[
            ('', 'Seleccione un rol'),
            ('4', 'Entrevistador'),
            ('5', 'Analista de selección'),
            ('6', 'Analista de selección ATS (Interno)'),
        ],
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
            'data-placeholder': 'Seleccione un rol',
            'data-tags':'true',
            'data-dropdown-parent': '#modal_grupo_trabajo',
            'data-hide-search': 'true' ,
        })
    )

    # campo de ciudad
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Configuración de Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_crear_usuario'
        self.helper.form_class = 'w-200'

        self.helper.layout = Layout(
            Row(
                Column('primer_nombre', css_class='form-group mb-0'),
                Column('segundo_nombre', css_class='form-group mb-0'),
                Column('primer_apellido', css_class='form-group mb-0'),
                Column('segundo_apellido', css_class='form-group mb-0'),
                css_class='fw-semibold fs-6 mb-2'
            ),
            Row(
                Column('correo', css_class='form-group mb-0'),
                css_class='fw-semibold fs-6 mb-2'
            ),
            Row(
                Column('rol', css_class='form-group mb-0'),
                css_class='fw-semibold fs-6 mb-2'
            ),
        )

    def clean(self):
        cleaned_data = super().clean()

        primer_nombre    = cleaned_data.get('primer_nombre')
        segundo_nombre   = cleaned_data.get('segundo_nombre')
        primer_apellido  = cleaned_data.get('primer_apellido')
        segundo_apellido = cleaned_data.get('segundo_apellido')
        correo = cleaned_data.get('correo')

        # Función auxiliar para validar que un campo contenga solo letras
        def validar_solo_letras(valor, campo):
            if valor and not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', valor):
                self.add_error(campo, f"El campo {campo} solo puede contener letras.")
        
        #campo para validar
        # Validar primer nombre (obligatorio)
        if not primer_nombre:
            self.add_error('primer_nombre', 'El primer nombre es obligatorio.')
        else:
            validar_solo_letras(primer_nombre, 'primer_nombre')
        
        # Validar segundo nombre (opcional)
        if segundo_nombre:
            validar_solo_letras(segundo_nombre, 'segundo_nombre')
        
        # Validar primer apellido (obligatorio)
        if not primer_apellido:
            self.add_error('primer_apellido', 'El primer apellido es obligatorio.')
        else:
            validar_solo_letras(primer_apellido, 'primer_apellido')
        
        # Validar segundo apellido (opcional)
        if segundo_apellido:
            validar_solo_letras(segundo_apellido, 'segundo_apellido')
        
        # Validar correo electrónico
        if not correo:
            self.add_error('correo', 'El correo electrónico es obligatorio.')
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', correo):
            self.add_error('correo', 'Por favor, introduce una dirección de correo electrónico válida.')
        else:
            # Verificar si el correo ya existe en la base de datos
            if UsuarioBase.objects.filter(username=correo).exists():
                self.add_error('correo', 'Este correo electrónico ya está registrado.')
        
        return super().clean()
    
class CrearUsuarioInternoAtsForm(forms.Form):
    # Campos del usuario
    primer_nombre = forms.CharField(
        label='Primer Nombre', 
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'placeholder': 'Primer Nombre',
        })
    )

    segundo_nombre = forms.CharField(
        label='Segundo Nombre', 
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'placeholder': 'Segundo Nombre',
        })
    )

    primer_apellido = forms.CharField(
        label='Primer Apellido', 
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'placeholder': 'Primer Apellido',
        })
    )

    segundo_apellido = forms.CharField(
        label='Segundo Apellido', 
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'placeholder': 'Segundo Apellido',
        })
    )

    correo = forms.EmailField(
        label='Correo Usuario', 
        max_length=150,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'placeholder': 'Ingrese el correo del usuario',
        })
    )

    rol = forms.ChoiceField(
        label='Rol del Usuario',
        choices=[
            ('', 'Seleccione un rol'),
            ('6', 'Analista ATS'),
        ],
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
            'data-placeholder': 'Seleccione un rol',
            'data-tags':'true',
            'data-dropdown-parent': '#modal_grupo_trabajo',
            'data-hide-search': 'true' ,
        })
    )

    # campo de ciudad
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Configuración de Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_crear_usuario'
        self.helper.form_class = 'w-200'

        self.helper.layout = Layout(
            Row(
                Column('primer_nombre', css_class='form-group mb-0'),
                Column('segundo_nombre', css_class='form-group mb-0'),
                Column('primer_apellido', css_class='form-group mb-0'),
                Column('segundo_apellido', css_class='form-group mb-0'),
                css_class='fw-semibold fs-6 mb-2'
            ),
            Row(
                Column('correo', css_class='form-group mb-0'),
                css_class='fw-semibold fs-6 mb-2'
            ),
            Row(
                Column('rol', css_class='form-group mb-0'),
                css_class='fw-semibold fs-6 mb-2'
            ),
        )

    def clean(self):
        cleaned_data = super().clean()

        primer_nombre    = cleaned_data.get('primer_nombre')
        segundo_nombre   = cleaned_data.get('segundo_nombre')
        primer_apellido  = cleaned_data.get('primer_apellido')
        segundo_apellido = cleaned_data.get('segundo_apellido')
        correo = cleaned_data.get('correo')

        # Función auxiliar para validar que un campo contenga solo letras
        def validar_solo_letras(valor, campo):
            if valor and not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', valor):
                self.add_error(campo, f"El campo {campo} solo puede contener letras.")
        
        #campo para validar
        # Validar primer nombre (obligatorio)
        if not primer_nombre:
            self.add_error('primer_nombre', 'El primer nombre es obligatorio.')
        else:
            validar_solo_letras(primer_nombre, 'primer_nombre')
        
        # Validar segundo nombre (opcional)
        if segundo_nombre:
            validar_solo_letras(segundo_nombre, 'segundo_nombre')
        
        # Validar primer apellido (obligatorio)
        if not primer_apellido:
            self.add_error('primer_apellido', 'El primer apellido es obligatorio.')
        else:
            validar_solo_letras(primer_apellido, 'primer_apellido')
        
        # Validar segundo apellido (opcional)
        if segundo_apellido:
            validar_solo_letras(segundo_apellido, 'segundo_apellido')
        
        # Validar correo electrónico
        if not correo:
            self.add_error('correo', 'El correo electrónico es obligatorio.')
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', correo):
            self.add_error('correo', 'Por favor, introduce una dirección de correo electrónico válida.')
        else:
            # Verificar si el correo ya existe en la base de datos
            if UsuarioBase.objects.filter(username=correo).exists():
                self.add_error('correo', 'Este correo electrónico ya está registrado.')
        
        return super().clean()