import re
import os
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML, Div
from applications.usuarios.models import UsuarioBase, Grupo
from applications.cliente.models import Cli051Cliente

class UsuarioModalForm(forms.Form):
    """
    Formulario para crear y editar usuarios a través de modales.
    Incluye todos los campos del modelo UsuarioBase.
    """
    
    # Campos del usuario
    primer_nombre = forms.CharField(
        label='Primer Nombre', 
        max_length=60,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Primer Nombre',
            'required': 'required'
        })
    )

    segundo_nombre = forms.CharField(
        label='Segundo Nombre', 
        max_length=60,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Segundo Nombre (opcional)'
        })
    )

    primer_apellido = forms.CharField(
        label='Primer Apellido', 
        max_length=60,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Primer Apellido',
            'required': 'required'
        })
    )

    segundo_apellido = forms.CharField(
        label='Segundo Apellido', 
        max_length=60,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Segundo Apellido (opcional)'
        })
    )

    email = forms.EmailField(
        label='Correo Electrónico', 
        max_length=150,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com',
            'required': 'required'
        })
    )

    telefono = forms.CharField(
        label='Teléfono', 
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Teléfono (opcional)'
        })
    )

    group = forms.ModelChoiceField(
        label='Grupo/Rol',
        queryset=Grupo.objects.filter(activate=True),
        required=True,
        empty_label='Seleccione un grupo',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': 'required'
        })
    )

    imagen_perfil = forms.ImageField(
        label='Imagen de Perfil', 
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None)
        self.cliente_id = kwargs.pop('cliente_id', None)
        super().__init__(*args, **kwargs)

        # Configuración de Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_usuario_modal'
        self.helper.enctype = 'multipart/form-data'
        self.helper.form_class = 'needs-validation'
        self.helper.form_show_labels = True

        # Layout optimizado para modales
        self.helper.layout = Layout(
            Row(
                Column('primer_nombre', css_class='col-md-6 mb-3'),
                Column('segundo_nombre', css_class='col-md-6 mb-3'),
                css_class='row'
            ),
            Row(
                Column('primer_apellido', css_class='col-md-6 mb-3'),
                Column('segundo_apellido', css_class='col-md-6 mb-3'),
                css_class='row'
            ),
            Row(
                Column('email', css_class='col-md-6 mb-3'),
                Column('telefono', css_class='col-md-6 mb-3'),
                css_class='row'
            ),
            Row(
                Column('group', css_class='col-md-6 mb-3'),
                Column('imagen_perfil', css_class='col-md-6 mb-3'),
                css_class='row'
            ),
        )

    def clean(self):
        cleaned_data = super().clean()

        primer_nombre = cleaned_data.get('primer_nombre')
        segundo_nombre = cleaned_data.get('segundo_nombre')
        primer_apellido = cleaned_data.get('primer_apellido')
        segundo_apellido = cleaned_data.get('segundo_apellido')
        email = cleaned_data.get('email')
        telefono = cleaned_data.get('telefono')
        group = cleaned_data.get('group')

        # Función auxiliar para validar que un campo contenga solo letras
        def validar_solo_letras(valor, campo):
            if valor and not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', valor):
                self.add_error(campo, f"El campo {campo} solo puede contener letras.")

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
        if not email:
            self.add_error('email', 'El correo electrónico es obligatorio.')
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            self.add_error('email', 'Por favor, introduce una dirección de correo electrónico válida.')
        else:
            # Verificar si el correo ya existe en la base de datos
            qs = UsuarioBase.objects.filter(username=email)
            if self.usuario:
                qs = qs.exclude(pk=self.usuario.pk)
            if qs.exists():
                self.add_error('email', 'Este correo electrónico ya está registrado.')

        # Validar teléfono (opcional)
        if telefono:
            # Validar que solo contenga números, espacios, guiones y paréntesis
            if not re.match(r'^[\d\s\-\(\)\+]+$', telefono):
                self.add_error('telefono', 'El teléfono solo puede contener números, espacios, guiones, paréntesis y el símbolo +.')

        # Validar grupo (obligatorio)
        if not group:
            self.add_error('group', 'El grupo del usuario es obligatorio.')

        # Validar imagen de perfil
        imagen_perfil = cleaned_data.get('imagen_perfil')
        if imagen_perfil:
            # Verificar la extensión del archivo
            extension = os.path.splitext(imagen_perfil.name)[1].lower()
            if extension not in ['.jpg', '.jpeg', '.png']:
                self.add_error('imagen_perfil', 'Formato de imagen no válido. Solo se permiten JPG, JPEG y PNG.')
            # Verificar el tamaño del archivo (5 MB máximo)
            if imagen_perfil.size > 5 * 1024 * 1024:
                self.add_error('imagen_perfil', 'El tamaño de la imagen no debe exceder los 5 MB.')

        return cleaned_data

    def save(self, commit=True):
        """
        Método para guardar el usuario.
        Este método será llamado desde la vista.
        """
        if not self.is_valid():
            raise ValueError("El formulario no es válido")
        
        # Los datos se procesarán en la vista
        return self.cleaned_data
