import re, os
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML

class SignupFormCandidato(forms.Form):

    # Campos del usuario
    primer_nombre = forms.CharField(
        label='Primer Nombre', 
        widget=forms.TextInput(attrs={'placeholder': 'Primer Nombre', 'required': 'True'}),
        max_length=150,
        required=True
    )
    
    segundo_nombre = forms.CharField(
        label='Segundo Nombre', 
        widget=forms.TextInput(attrs={'placeholder': 'Segundo Nombre'}),
        max_length=150,
        required=False
    )
    
    primer_apellido = forms.CharField(
        label='Primer Apellido', 
        widget=forms.TextInput(attrs={'placeholder': 'Primer Apellido', 'required': 'required'}),
        max_length=150,
        required=True
    )

    segundo_apellido = forms.CharField(
        label='Segundo Apellido', 
        widget=forms.TextInput(attrs={'placeholder': 'Segundo Apellido'}),
        max_length=150,
        required=False
    )
        
    email = forms.EmailField(
        label='Correo electrónico Usuario', 
        widget=forms.EmailInput(attrs={'placeholder': 'Correo electrónico', 'required': 'required'}),
        required=True
    )

    password1 = forms.CharField(
        label='Contraseña', 
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña', 'required': 'required'}),
        required=True
    )

    password2 = forms.CharField(
        label='Confirmar contraseña', 
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirmar contraseña', 'required': 'required'}),
        required=True
    )



    def clean(self):
        cleaned_data = super().clean()
        primer_nombre = cleaned_data.get('primer_nombre')
        segundo_nombre = cleaned_data.get('segundo_nombre')
        primer_apellido = cleaned_data.get('primer_apellido')
        segundo_apellido = cleaned_data.get('segundo_apellido')
        email = cleaned_data.get('email')

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', primer_nombre):
            self.add_error('primer_nombre', "Solo puede contener letras.")
        else:
            self.cleaned_data['primer_nombre'] = primer_nombre.upper()
        
        if segundo_nombre:
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', segundo_nombre):
                self.add_error('segundo_nombre', "Solo puede contener letras.")
            else:
                self.cleaned_data['segundo_nombre'] = segundo_nombre.upper()
        
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', primer_apellido):
            self.add_error('primer_apellido', "Solo puede contener letras.")
        else:
            self.cleaned_data['primer_apellido'] = primer_apellido.upper()
        
        if segundo_apellido:
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', segundo_apellido):
                self.add_error('segundo_apellido', "Solo puede contener letras.")
            else:
                self.cleaned_data['segundo_apellido'] = segundo_apellido.upper()

        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            self.add_error('email','El Correo no es válido.')

        return super().clean()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Configuración de Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_signup_candidato'
        self.helper.form_class = 'w-200'
        
        # Definimos el layout del formulario
        self.helper.layout = Layout(
            Row(
                Column('primer_nombre', css_class='form-group mb-0'),
                Column('segundo_nombre', css_class='form-group mb-0'),
                css_class='row'
            ),
            Row(
                Column('primer_apellido', css_class='form-group mb-0'),
                Column('segundo_apellido', css_class='form-group mb-0'),
                css_class='row'
            ),
            Row(
                Column('email', css_class='form-group mb-0'),
                css_class='row'
            ),
            Row(
                Column('password1', css_class='form-group mb-0'),
                Column('password2', css_class='form-group mb-0'),
                css_class='row'
            ),
            Submit('submit', 'Crear', css_class='btn btn-lg btn-primary w-100 mb-5'),
        )